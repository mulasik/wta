from .transforming_sequence import TransformingSequence
from .sentence_tokenizer import SentenceTokenizer
from .sentence_classifier import SentenceClassifier


class TpsfEcm:

    # Edit operation types:
    DEL = 'deletion'
    REPL = 'replacement'
    INS_PAST = 'insertion by pasting'
    INS_ENT = 'insertion by entering'
    NO_EDIT = 'non-edit operation'

    def __init__(self, revision_id, output_chars, edit, pause, event_desc, prev_tpsf):

        self.revision_id = revision_id
        self.event_description = event_desc
        self.preceeding_pause = pause
        self.prev_text_version = '' if not prev_tpsf else prev_tpsf.result_text
        self.result_text = ''.join(output_chars)

        removed_sequence_text = ''.join(edit[1]) if len(edit[1]) > 0 else None
        inserted_sequence_text = edit[2] if len(edit[2]) > 0 else None
        appended_sequence_text = self.result_text[len(self.prev_text_version):]
        appended_sequence_text = appended_sequence_text if appended_sequence_text not in ['', inserted_sequence_text] else None

        # conclude edit operation from the transforming sequence content
        if removed_sequence_text is not None and inserted_sequence_text is None:
            self.edit_op = self.DEL
        elif removed_sequence_text is not None and inserted_sequence_text is not None:
            self.edit_op = self.REPL
        elif removed_sequence_text is None and inserted_sequence_text is not None:
            self.edit_op = self.INS_PAST if self.event_description == 'after insertion' else self.INS_ENT
        else:
            self.edit_op = self.NO_EDIT

        if removed_sequence_text is not None:
            self.transforming_sequence = TransformingSequence(removed_sequence_text, 'deletion')
        elif inserted_sequence_text is not None:
            self.transforming_sequence = TransformingSequence(inserted_sequence_text, 'insertion')
        elif appended_sequence_text is not None:
            self.transforming_sequence = TransformingSequence(appended_sequence_text, 'append')
        else:
            self.transforming_sequence = None

        self.edit_start_position = edit[0]
        if self.transforming_sequence is not None:
            self.verify_edit_start_position()

        # perform sentence segmentation
        sentence_tokenizer_prev = SentenceTokenizer(self.prev_text_version, self.revision_id, self.transforming_sequence)
        self.previous_sentence_list = sentence_tokenizer_prev.sentences
        sentence_tokenizer = SentenceTokenizer(self.result_text, self.revision_id, self.transforming_sequence)
        self.sentence_list = sentence_tokenizer.sentences

        sentence_classifier = SentenceClassifier(self.previous_sentence_list, self.sentence_list, self.transforming_sequence)
        self.new_sentences = sentence_classifier.new_sentences
        self.modified_sentences = sentence_classifier.modified_sentences
        self.deleted_sentences = sentence_classifier.deleted_sentences
        self.unchanged_sentences = sentence_classifier.unchanged_sentences
        self.delta_current_previous = sentence_classifier.delta_current_previous
        self.delta_previous_current = sentence_classifier.delta_previous_current

        self.morphosyntactic_relevance = True  # TODO

        # print(self)

    def verify_edit_start_position(self):
        pos = self.edit_start_position
        # update edit start position if the edit type is an "insertion by entering"
        # the inserted sequence length must be subtracted from the start position
        if self.edit_op == self.INS_ENT:
            pos = pos - len(self.transforming_sequence.text)
        # update edit_start_position if there is an appended_sequence
        # the position stored before is the edit end position (appended_sequence end index)
        # to get the edit_start_position the length of appended_sequence must be subtracted
        if self.transforming_sequence.label == 'append':
            pos = pos - len(self.transforming_sequence.text.strip())
        error_range = 2
        start = pos - error_range
        end = pos + error_range
        if self.transforming_sequence is not None:
            if self.transforming_sequence.label in ['insertion', 'append']:
                self.edit_start_position = self.result_text.find(self.transforming_sequence.text, start, end)
                # as long as the sequence can't be found,
                # extend the searched segment by one index on both ends and search again
                # TODO check the index issue
                while self.edit_start_position == -1:
                    start -= 1
                    end += 1
                    self.edit_start_position = self.result_text.find(self.transforming_sequence.text, start, end)
            else:
                self.edit_start_position = pos
        else:
            self.edit_start_position = None

    def __str__(self):
        return f'''

=== TPSF ===

PREVIOUS TEXT:  
{self.prev_text_version}

RESULT TEXT:            
{self.result_text}

TRANSFORMING SEQUENCE:  {self.transforming_sequence}

SENTENCES:
Previous sentences:     {[s.text for s in self.previous_sentence_list] if self.previous_sentence_list is not None else []}
Sentences:              {[s.text for s in self.sentence_list] if self.sentence_list is not None else []}

SENTENCE CLASSIfiCATION:
New sentences:          {[(s.label, s.text) for s in self.new_sentences]}
Modified sentences:     {[(s.label, s.text) for s in self.modified_sentences]}
Deleted sentences:      {[(s.label, s.text) for s in self.deleted_sentences]}
Unchanged sentences:    {[(s.label, s.text) for s in self.unchanged_sentences]}

        '''


class TpsfPcm:

    def __init__(self, output_chars, pause, final):
        if final is True:
            self.result_text = ''.join(output_chars)
        else:
            self.result_text = ''.join(output_chars[:-1])
        self.preceeding_pause = pause

    def __str__(self):
        return f'''
{self.result_text}
        '''

    def tpsfs_dict(self):
        tpsf_dict = {
            "preceeding_pause": self.preceeding_pause,
            "result_text": self.result_text,
        }
        return tpsf_dict

