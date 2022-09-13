from bs4 import BeautifulSoup
from tqdm import tqdm

from wta.pipeline.text_history.tpsf import TpsfEcm, TpsfPcm

import settings


class IdfxParser:

    # Keystroke types:
    ARROW_KEYS = ['VK_LEFT', 'VK_RIGHT', 'VK_UP', 'VK_DOWN']
    BACKSPACE = 'VK_BACK'
    DELETE = 'VK_DELETE'
    END = 'VK_END'
    NON_PRODUCTION_KEYS = [BACKSPACE, DELETE, END] + ARROW_KEYS

    # Event types which trigger TPSF creation:
    PRE_DEL = 'before deletion'
    POST_DEL = 'after deletion'
    PRE_INS = 'before insertion'
    POST_INS = 'after insertion'
    PRE_REPL = 'before replacement'
    POST_REPL = 'after replacement'
    END = 'navigating to end'
    NAV = 'navigating without editing'
    FINAL = 'final text revision'

    def __init__(self, idfx):
        self.idfx = idfx
        self.pause_duration = settings.config['pause_duration']
        self.config = settings.config
        self.nlp_model = settings.nlp_model
        self.all_tpsfs_ecm = []  # accumulates the revisions of TPSF based on edit operations
        self.all_tpsfs_pcm = []  # accumulates the revisions of TPSF based on pause duration
        self.filtered_tpsfs_ecm = []
        self.number_events = 0

    def set_number_events(self, events):
        self.number_events = len(events)

    def run(self):
        soup = BeautifulSoup(open(self.idfx), features="lxml")
        events = soup.find_all('event')
        self.set_number_events(events)
        # retreive the initial creation timestamp for pause calculation
        entries = soup.find_all('entry')
        prev_endtime = int([e.value.get_text() for e in entries if e.key.get_text() == '__LogRelativeCreationDate'][0])

        # initialize all accumulator variables used while parsing the XML
        output_chars = []  # accumulates the chars of the text
        backspace_count = 0
        delete_count = 0
        removed_sequence = ''
        inserted_sequence = ''
        prev_key = ''
        prev_pos = 0

        # iterate over the XML to track writer's actions and collect all TPFSs
        # there are three types of events 'keyboard', 'insert' and 'replacement', they have different structure

        progress = tqdm(events, 'Processing keylogs')
        for i, event in enumerate(progress):
            parts = event.find_all('part')

            # for 'keyboard' event type, each keystroke is tracked to derive the TPSF
            if event['type'] == 'keyboard' and len(parts) == 2:
                wordlog = parts[0]
                winlog = parts[1]
                pos = int(wordlog.position.get_text())
                str_insertion_value = winlog.value.get_text()
                key_name = winlog.key.get_text()
                starttime = int(winlog.starttime.get_text())
                endtime = int(winlog.endtime.get_text())
                # calculate the pause since last keystroke
                try:
                    pause = (starttime - prev_endtime) / 1000
                except TypeError:
                    pause = None

                # save tpsf every time the writer moves backwards without editing the text
                if (pos < prev_pos and prev_key not in [self.BACKSPACE, self.DELETE]) or (pos == prev_pos and inserted_sequence != '' and prev_key not in [self.BACKSPACE, self.DELETE]):
                    event_desc = ""  # self.NAV TODO define the event description
                    edit = (prev_pos, removed_sequence, inserted_sequence)  # TODO test extensively
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)
                    self.all_tpsfs_ecm.append(tpsf)
                    removed_sequence = ''
                    inserted_sequence = ''

                # save tpsf every time the writer moves forwards by more than one position at a time
                if abs(pos - prev_pos) > 1:  # TODO: test extensively
                    if prev_key == self.BACKSPACE:
                        removed_sequence = removed_sequence[::-1]
                    event_desc = ""  # self.NAV TODO define the event description
                    edit = (pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                    self.all_tpsfs_ecm.append(tpsf)
                    removed_sequence = ''
                    inserted_sequence = ''

                # EDIT CAPTURING MODE

                if key_name in self.ARROW_KEYS and prev_key == self.BACKSPACE:
                    removed_sequence = removed_sequence[::-1]
                    event_desc = self.POST_DEL
                    edit = (pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                    self.all_tpsfs_ecm.append(tpsf)
                    removed_sequence = ''
                    inserted_sequence = ''

                if key_name in self.ARROW_KEYS and prev_key == self.DELETE:
                    event_desc = self.POST_DEL
                    edit = (pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                    self.all_tpsfs_ecm.append(tpsf)
                    removed_sequence = ''
                    inserted_sequence = ''

                if key_name == 'VK_RIGHT' and prev_key not in self.NON_PRODUCTION_KEYS:
                    # removed_sequence = removed_sequence[::-1]
                    event_desc = self.POST_INS
                    edit = (pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                    self.all_tpsfs_ecm.append(tpsf)
                    inserted_sequence = ''

                # CHAR PRODUCTION: appending or inserting chars
                if key_name not in self.NON_PRODUCTION_KEYS:
                    # capture the revision after deleting completed
                    if prev_key == self.BACKSPACE:
                        removed_sequence = removed_sequence[::-1]
                        event_desc = self.POST_DEL
                        edit = (pos, removed_sequence, inserted_sequence)
                        prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                        tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                        self.all_tpsfs_ecm.append(tpsf)
                        inserted_sequence = ''  # CHECK
                    if prev_key == self.DELETE:
                        event_desc = self.POST_DEL
                        edit = (pos, removed_sequence, inserted_sequence)
                        prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                        tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                        self.all_tpsfs_ecm.append(tpsf)
                        inserted_sequence = ''  # CHECK
                    # if cursor at the end of the text, append the char
                    if pos == len(output_chars):
                        # capture insertion by pasting with CTRL+V
                        if key_name == 'VK_V' and len(str_insertion_value) > 1:
                            event_desc = self.POST_INS
                            inserted_sequence = str_insertion_value
                            n_insertion_position = pos
                            for strChar in list(inserted_sequence):
                                output_chars.insert(n_insertion_position, strChar)
                                n_insertion_position += 1
                            edit = (pos, removed_sequence, inserted_sequence)
                            prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                            tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                            self.all_tpsfs_ecm.append(tpsf)
                            inserted_sequence = ''
                        else:
                            output_chars.extend(list(str_insertion_value))
                            inserted_sequence = ''
                    # if cursor in the middle of the text, insert the char
                    elif pos < len(output_chars):
                        if prev_key in self.ARROW_KEYS:
                            event_desc = self.PRE_INS
                            edit = (pos, removed_sequence, inserted_sequence)
                            prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                            tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                            self.all_tpsfs_ecm.append(tpsf)
                            inserted_sequence = ''
                        # capture insertion by pasting with CTRL+V
                        if key_name == 'VK_V' and len(str_insertion_value) > 1:
                            event_desc = self.POST_INS
                            inserted_sequence = str_insertion_value
                            n_insertion_position = pos
                            for strChar in list(str_insertion_value):
                                output_chars.insert(n_insertion_position, strChar)
                                n_insertion_position += 1
                            edit = (pos, removed_sequence, inserted_sequence)
                            prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                            tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                            self.all_tpsfs_ecm.append(tpsf)
                            inserted_sequence = ''
                        else:
                            n_insertion_position = pos
                            for strChar in list(str_insertion_value):
                                output_chars.insert(n_insertion_position, strChar)
                                n_insertion_position += 1
                            inserted_sequence += str_insertion_value

                        # if a char insertion is directly followed by a replacement,
                        # the same char occurs in two subsequent events: keyboard and replacement
                        # one of the double chars needs to be removed from output_handler chars and from inserted sequence
                        try:
                            next_event = events[i + 1]['type']
                        except IndexError:
                            next_event = None
                        # if next_event and next_event == 'replacement':
                            # del output_chars[pos]
                            # print(f'Inserted sequence before: *{inserted_sequence}*')
                            # inserted_sequence = inserted_sequence[:-1]  # TO REMOVE?
                            # print(f'Inserted sequence shortened: *{inserted_sequence}*')  # TO REMOVE
                    removed_sequence = ''
                    backspace_count = 0
                    delete_count = 0

                # CHAR DELETION: removing chars with backspace
                if key_name == self.BACKSPACE:
                    if pos > 0:
                        # if this is the first edit action on the current text,
                        # capture the current TPSF, before any edits are made
                        if backspace_count == 0:
                            event_desc = self.PRE_DEL
                            edit = (prev_pos, removed_sequence, inserted_sequence)
                            prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                            tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                            self.all_tpsfs_ecm.append(tpsf)
                            inserted_sequence = ''
                        if prev_key != self.BACKSPACE or pos != prev_pos - 1:
                            removed_sequence = ''
                        try:
                            removed_sequence += output_chars[pos - 1]
                        except IndexError:
                            print('Apparently the number of output_handler characters detected so far does not correspond to the position of the cursor.')
                        del output_chars[pos - 1]
                        backspace_count += 1

                # CHAR DELETION: removing chars with delete
                if key_name == self.DELETE:
                    # if this is the first edit action on the current text,
                    # capture the current TPSF, before any edits are made
                    if delete_count == 0:
                        event_desc = self.PRE_DEL
                        edit = (prev_pos, removed_sequence, inserted_sequence)
                        prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                        tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                        self.all_tpsfs_ecm.append(tpsf)
                    removed_sequence += output_chars[pos]
                    del output_chars[pos]
                    delete_count += 1
                    inserted_sequence = ''

                if key_name == 'VK_END':
                    event_desc = self.END
                    edit = (prev_pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                    self.all_tpsfs_ecm.append(tpsf)
                    inserted_sequence = ''

            # SEQUENCE REPLACEMENT: a sequence is marked and replaced with a char or empty string
            elif event['type'] == 'replacement':
                key_name = 'REPL'
                # capture the text before replacement takes place
                event_desc = self.PRE_REPL
                edit = (pos, removed_sequence, inserted_sequence)
                #  if the key just before replacement was backspace, revert the last deletion
                #  as it is the backspace used in the replacement operation not for deleting a previous char
                if prev_key == self.BACKSPACE:  # TODO
                    output_chars.insert(pos - 1, removed_sequence)  # TODO

                #  if the key just before replacement was delete, revert the last deletion
                #  as it is the delete used in the replacement operation not for deleting a char under cursor
                if prev_key == self.DELETE:
                    output_chars.insert(pos, removed_sequence)

                prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                self.all_tpsfs_ecm.append(tpsf)
                inserted_sequence = ''

                # the replacement starts at startpos and ends at endpos
                endtime = None
                pause = None  # TODO check if pause can be defined
                startpos = int(event.part.start.get_text())
                endpos = int(event.part.end.get_text())
                # the character to replace the marked sequence
                str_insertion_value = event.part.newtext.get_text()
                removed_sequence = output_chars[startpos:endpos]
                del output_chars[startpos:endpos]

                # replace the char in the output_chars list if not an empty string and delete the remaining sequence
                n_insertion_position = startpos
                for strChar in list(str_insertion_value):
                    output_chars.insert(n_insertion_position, strChar)
                    n_insertion_position += 1

                pos = startpos
                event_desc = self.POST_REPL
                edit = (startpos, removed_sequence, inserted_sequence)
                prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                self.all_tpsfs_ecm.append(tpsf)
                removed_sequence = ''
                inserted_sequence = ''  # CHECK

            # SEQUENCE INSERTION
            elif event['type'] == 'insert':
                key_name = 'INS'
                inserted_sequence = event.part.before.get_text()
                n_insertion_position = int(event.part.position.get_text())
                startpos = int(event.part.position.get_text()) - len(inserted_sequence)
                endtime = None
                pause = None  # TODO check if pause can be defined
                for strChar in list(inserted_sequence):
                    output_chars.insert(n_insertion_position, strChar)
                    n_insertion_position += 1
                pos = n_insertion_position
                event_desc = self.POST_INS
                edit = (startpos, removed_sequence, inserted_sequence)
                prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model)

                self.all_tpsfs_ecm.append(tpsf)
                inserted_sequence = ''
                
            # we are not interested in other stuff (e.g. "focus", "mouse")
            else:
                continue

            prev_endtime = endtime
            prev_pos = pos
            prev_key = key_name

            # PAUSE CAPTURING MODE

            if pause and pause > self.pause_duration:
                tpsf_paused = TpsfPcm(output_chars, pause, False)
                self.all_tpsfs_pcm.append(tpsf_paused)

        # EDIT CAPTURING MODE: append final text to tpsf list
        event_desc = self.FINAL
        edit = (pos, removed_sequence, inserted_sequence)
        prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
        tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.config, self.nlp_model, final=True)

        self.all_tpsfs_ecm.append(tpsf)
        # PAUSE CAPTURING MODE: append final text to tpsf list
        tpsf_paused = TpsfPcm(output_chars, pause, True)
        self.all_tpsfs_pcm.append(tpsf_paused)

    def filter_tpsfs_ecm(self):
        progress = tqdm(self.all_tpsfs_ecm, 'Filtering text history')
        irrelevant_ts_aggregated = []
        for tpsf in progress:
            if tpsf.relevance is True:
                tpsf.set_irrelevant_ts_aggregated(irrelevant_ts_aggregated)
                self.filtered_tpsfs_ecm.append(tpsf)
                irrelevant_ts_aggregated = []
            else:
                if tpsf.transforming_sequence is not None:
                    irrelevant_ts_aggregated.append((tpsf.transforming_sequence.text, tpsf.transforming_sequence.label))

