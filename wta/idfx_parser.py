from bs4 import BeautifulSoup

from .tpsf import TpsfEcm, TpsfPcm


class IdfxParser:

    # Keystroke types:
    ARROW_KEYS = ['VK_LEFT', 'VK_RIGHT', 'VK_UP', 'VK_DOWN']
    BACKSPACE = 'VK_BACK'
    END = 'VK_END'
    NON_PRODUCTION_KEYS = [BACKSPACE, END] + ARROW_KEYS

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

    def __init__(self, idfx, pause_duration, edit_distance, filtering):
        self.idfx = idfx
        self.pause_duration = pause_duration
        self.edit_distance = edit_distance
        self.filtering = filtering
        self.all_tpsfs_ecm = []  # accumulates the revisions of TPSF based on edit operations
        self.all_tpsfs_pcm = []  # accumulates the revisions of TPSF based on pause duration
        self.all_tpsfs_ecm_dict = []
        self.all_tpsfs_pcm_dict = []

    def run(self):
        soup = BeautifulSoup(open(self.idfx), features="lxml")
        events = soup.find_all('event')
        # retreive the initial creation timestamp for pause calculation
        entries = soup.find_all('entry')
        prev_endtime = int([e.value.get_text() for e in entries if e.key.get_text() == '__LogRelativeCreationDate'][0])

        # initialize all accumulator variables used while parsing the XML
        output_chars = []  # accumulates the chars of the text
        backspace_count = 0
        removed_sequence = ''
        inserted_sequence = ''
        prev_key = ''
        prev_pos = 0

        # iterate over the XML to track writer's actions and collect all TPFSs
        # there are three types of events 'keyboard', 'insert' and 'replacement', they have different structure

        for i, event in enumerate(events):
            parts = event.find_all('part')

            # for 'keyboard' event type, each keystroke is tracked to derive the TPSF
            if event['type'] == 'keyboard':
                wordlog = parts[0]
                winlog = parts[1]
                pos = int(wordlog.position.get_text())
                char = winlog.value.get_text()
                key_name = winlog.key.get_text()
                starttime = int(winlog.starttime.get_text())
                endtime = int(winlog.endtime.get_text())
                # calculate the pause since last keystroke
                try:
                    pause = (starttime - prev_endtime) / 1000
                except TypeError:
                    pause = None

                # save tpsf every time the writer moves backwards without editing the text
                if pos < prev_pos and prev_key != self.BACKSPACE:
                    event_desc = self.NAV
                    edit = (prev_pos, removed_sequence, inserted_sequence)  # TODO test extensively
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                    self.all_tpsfs_ecm.append(tpsf)
                    inserted_sequence = ''
                    prev_version = tpsf.result_text

                # save tpsf every time the writer moves forwards by more than one position at a time
                if abs(pos - prev_pos) > 1:  # TODO: test extensively
                    event_desc = self.NAV
                    edit = (pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                    self.all_tpsfs_ecm.append(tpsf)
                    inserted_sequence = ''
                    prev_version = tpsf.result_text

                # EDIT CAPTURING MODE

                if key_name in self.ARROW_KEYS and prev_key == self.BACKSPACE:
                    removed_sequence = removed_sequence[::-1]
                    event_desc = self.POST_DEL
                    edit = (pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                    self.all_tpsfs_ecm.append(tpsf)
                    prev_version = tpsf.result_text
                    removed_sequence = ''

                if key_name == 'VK_RIGHT' and prev_key not in self.NON_PRODUCTION_KEYS:
                    # removed_sequence = removed_sequence[::-1]
                    event_desc = self.POST_INS
                    edit = (pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                    self.all_tpsfs_ecm.append(tpsf)
                    prev_version = tpsf.result_text
                    inserted_sequence = ''

                # CHAR PRODUCTION: appending or inserting chars
                if key_name not in self.NON_PRODUCTION_KEYS:
                    # capture the revision after deleting completed
                    if prev_key == self.BACKSPACE:
                        removed_sequence = removed_sequence[::-1]
                        event_desc = self.POST_DEL
                        edit = (pos, removed_sequence, inserted_sequence)
                        prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                        tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                        self.all_tpsfs_ecm.append(tpsf)
                        prev_version = tpsf.result_text
                        inserted_sequence = ''  # CHECK
                    # if cursor at the end of the text, append the char
                    if pos == len(output_chars):
                        # capture insertion by pasting with CTRL+V
                        if key_name == 'VK_V' and len(char) > 1:
                            event_desc = self.POST_INS
                            inserted_sequence = char
                            ins_pos = pos
                            for char in list(inserted_sequence):
                                output_chars.insert(ins_pos, char)
                                ins_pos += 1
                            edit = (pos, removed_sequence, inserted_sequence)
                            prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                            tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                            self.all_tpsfs_ecm.append(tpsf)
                            prev_version = tpsf.result_text
                            inserted_sequence = ''
                        else:
                            output_chars.append(char)
                            inserted_sequence = ''
                    # if cursor in the middle of the text, insert the char
                    elif pos < len(output_chars):
                        if prev_key in self.ARROW_KEYS:
                            event_desc = self.PRE_INS
                            edit = (pos, removed_sequence, inserted_sequence)
                            prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                            tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                            self.all_tpsfs_ecm.append(tpsf)
                            prev_version = tpsf.result_text
                            inserted_sequence = ''
                        # capture insertion by pasting with CTRL+V
                        if key_name == 'VK_V' and len(char) > 1:
                            event_desc = self.POST_INS
                            inserted_sequence = char
                            ins_pos = pos
                            for char in list(inserted_sequence):
                                output_chars.insert(ins_pos, char)
                                ins_pos += 1
                            edit = (pos, removed_sequence, inserted_sequence)
                            prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                            tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                            self.all_tpsfs_ecm.append(tpsf)
                            prev_version = tpsf.result_text
                            inserted_sequence = ''
                        else:
                            output_chars.insert(pos, char)
                            inserted_sequence += char

                        # if a char insertion is directly followed by a replacement,
                        # the same char occurs in two subsequent events: keyboard and replacement
                        # one of the double chars needs to be removed from output chars and from inserted sequence
                        try:
                            next_event = events[i + 1]['type']
                        except IndexError:
                            next_event = None
                        if next_event and next_event == 'replacement':
                            del output_chars[pos]
                            inserted_sequence = inserted_sequence[:-1]
                    removed_sequence = ''
                    backspace_count = 0

                # CHAR DELETION: removing chars with backspace
                if key_name == self.BACKSPACE:
                    # if this is the first edit action on the current text,
                    # capture the current TPSF, before any edits are made
                    if backspace_count == 0:
                        event_desc = self.PRE_DEL
                        edit = (prev_pos, removed_sequence, inserted_sequence)
                        prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                        tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                        self.all_tpsfs_ecm.append(tpsf)
                        prev_version = ''.join(output_chars)
                        inserted_sequence = ''  # CHECK
                    # if prev_key != 'VK_LEFT':
                    removed_sequence += output_chars[pos - 1]
                    del output_chars[pos - 1]
                    backspace_count += 1
                    inserted_sequence = ''

                if key_name == 'VK_END':
                    event_desc = self.END
                    edit = (prev_pos, removed_sequence, inserted_sequence)
                    prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                    tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                    self.all_tpsfs_ecm.append(tpsf)
                    inserted_sequence = ''
                    prev_version = tpsf.result_text

            # SEQUENCE REPLACEMENT: a sequence is marked and replaced with a char or empty string
            elif event['type'] == 'replacement':
                key_name = 'REPL'
                # capture the text before replacement takes place
                event_desc = self.PRE_REPL
                edit = (pos, removed_sequence, inserted_sequence)
                #  if the key just before replacement was backspace, revert the last deletion
                #  as it is the backspace used in the replacement operation not for deleting a previous char
                if prev_key == self.BACKSPACE:
                    output_chars.insert(pos - 1, removed_sequence)
                prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                self.all_tpsfs_ecm.append(tpsf)
                prev_version = ''.join(output_chars)

                # the replacement starts at startpos and ends at endpos
                endtime = None
                pause = None  # TODO check if pause can be defined
                startpos = int(event.part.start.get_text())
                endpos = int(event.part.end.get_text())
                pos = startpos
                # the character to replace the marked sequence
                char = event.part.newtext.get_text()
                removed_sequence = output_chars[startpos:endpos]
                if char == '':
                    del output_chars[startpos:endpos]
                else:
                    # replace the char in the output_chars list if not an empty string and delete the remaining sequence
                    output_chars[startpos] = char
                    del output_chars[startpos + 1:endpos]
                event_desc = self.POST_REPL
                edit = (pos, removed_sequence, inserted_sequence)
                prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                self.all_tpsfs_ecm.append(tpsf)
                prev_version = tpsf.result_text
                removed_sequence = ''
                inserted_sequence = ''  # CHECK

            # SEQUENCE INSERTION
            elif event['type'] == 'insert':
                key_name = 'INS'
                inserted_sequence = event.part.before.get_text()
                pos = int(event.part.position.get_text())
                startpos = int(event.part.position.get_text()) - len(inserted_sequence)
                endtime = None
                pause = None  # TODO check if pause can be defined
                for char in list(inserted_sequence):
                    output_chars.insert(pos, char)
                    pos += 1
                event_desc = self.POST_INS
                edit = (startpos, removed_sequence, inserted_sequence)
                prev_tpsf = None if len(self.all_tpsfs_ecm) == 0 else self.all_tpsfs_ecm[-1]
                tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
                self.all_tpsfs_ecm.append(tpsf)
                prev_version = tpsf.result_text
                inserted_sequence = ''

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
        tpsf = TpsfEcm(len(self.all_tpsfs_ecm), output_chars, edit, pause, event_desc, prev_tpsf, self.edit_distance, self.filtering)
        self.all_tpsfs_ecm.append(tpsf)
        # PAUSE CAPTURING MODE: append final text to tpsf list
        tpsf_paused = TpsfPcm(output_chars, pause, True)
        self.all_tpsfs_pcm.append(tpsf_paused)

