from wta.pipeline.text_history.transforming_sequence import TransformingSequence
from wta.pipeline.sentence_histories.sentence_tokenizer import SentenceTokenizer
from wta.pipeline.sentence_histories.sentence_classifier import SentenceClassifier
from wta.relevance_evaluator import RelevanceEvaluator


class Tpsf:

    def to_dict(self):
        pass


class TpsfEcm(Tpsf):

    # Edit operation types:
    DEL = 'deletion'
    REPL = 'replacement'
    INS_PAST = 'insertion by pasting'
    INS_ENT = 'insertion by entering'
    NO_EDIT = 'non-edit operation'

    def __init__(self, revision_id, output_chars, edit, pause, event_desc, prev_tpsf, config, nlp_model, final=False):

        self.revision_id = revision_id
        self.event_description = event_desc
        self.preceeding_pause = pause
        self.prev_text_version = '' if not prev_tpsf else prev_tpsf.result_text
        self.prev_tpsf = prev_tpsf
        self.result_text = ''.join(output_chars)
        self.previous_sentence_list = [] if not prev_tpsf else prev_tpsf.sentence_list
        self.contains_typos = None

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
            self.transforming_sequence = TransformingSequence(removed_sequence_text, 'deletion', nlp_model)
        elif inserted_sequence_text is not None:
            self.transforming_sequence = TransformingSequence(inserted_sequence_text, 'insertion', nlp_model)
        elif appended_sequence_text is not None:
            self.transforming_sequence = TransformingSequence(appended_sequence_text, 'append', nlp_model)
        else:
            self.transforming_sequence = None

        self.edit_start_position = edit[0]
        if self.transforming_sequence is not None:
            self.verify_edit_start_position()

        # perform sentence segmentation
        sentence_tokenizer = SentenceTokenizer(self.result_text, self.revision_id, self.transforming_sequence, nlp_model)
        self.sentence_list = sentence_tokenizer.sentences

        sentence_classifier = SentenceClassifier(self.previous_sentence_list, self.sentence_list, self.transforming_sequence, nlp_model)
        self.new_sentences = sentence_classifier.new_sentences
        self.modified_sentences = sentence_classifier.modified_sentences
        self.deleted_sentences = sentence_classifier.deleted_sentences
        self.unchanged_sentences = sentence_classifier.unchanged_sentences
        self.delta_current_previous = sentence_classifier.delta_current_previous
        self.delta_previous_current = sentence_classifier.delta_previous_current

        relevance_evaluator = RelevanceEvaluator(self, config['min_edit_distance'], config['ts_min_tokens_number'], config['enable_spellchecking'], config['include_punctuation_edits'], config['combine_edit_distance_with_tok_number'], nlp_model)
        if not final:
            self.relevance = relevance_evaluator.relevance
            self.relevance_eval_results = relevance_evaluator.relevance_eval_results
        else:
            self.relevance = True
            self.relevance_eval_results = []

        self.irrelevant_ts_aggregated = []

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

    def check_tpsf_spelling(self):
        # check if tpsf contains typos
        sentence_spellcheck_results = []
        sens_to_check = self.new_sentences + self.modified_sentences
        for s in sens_to_check:
            s.check_sentence_spelling()
            sentence_spellcheck_results.append(s.typos_detected)
        tpsf_contains_typos = True if True in sentence_spellcheck_results else False
        self.contains_typos = tpsf_contains_typos

    def set_irrelevant_ts_aggregated(self, irrelevant_ts_aggregated):
        self.irrelevant_ts_aggregated = irrelevant_ts_aggregated

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

    def to_dict(self):
        tpsf_dict = {
            "revision_id": self.revision_id,
            "event_description": self.event_description,
            "prev_text_version": self.prev_text_version,
            "preceeding_pause": self.preceeding_pause,
            "result_text": self.result_text,
            "edit": {
                "edit_start_position": self.edit_start_position,
                "transforming_sequence": {
                    "label": '' if self.transforming_sequence is None else self.transforming_sequence.label,
                    "text": '' if self.transforming_sequence is None else self.transforming_sequence.text,
                    "tokens": '' if self.transforming_sequence is None else self.transforming_sequence.tagged_tokens
                },
                "irrelevant_ts_aggregated": self.irrelevant_ts_aggregated
            },
            "sentences": {
                "previous_sentence_list": [s.to_dict() for s in self.previous_sentence_list],
                "current_sentence_list": [s.to_dict() for s in self.sentence_list],
                "delta_current_previous": [s.to_dict() for s in self.delta_current_previous],
                "delta_previous_current": [s.to_dict() for s in self.delta_previous_current],
                "new_sentences": [s.to_dict() for s in self.new_sentences],
                "modified_sentences": [s.to_dict() for s in self.modified_sentences],
                "deleted_sentences": [s.to_dict() for s in self.deleted_sentences],
                "unchanged_sentences": [s.to_dict() for s in self.unchanged_sentences],
            },
            "relevance_evaluation": self.relevance_eval_results,
            "relevance": self.relevance
        }
        return tpsf_dict

    def to_text(self):
        preceeding_edits = self.irrelevant_ts_aggregated
        preceeding_edits.append((self.transforming_sequence.text, self.transforming_sequence.label))
        return f"""
TPSF version {self.revision_id}:
{self.result_text}
Preceeding edits: {preceeding_edits}
"""


class TpsfPcm(Tpsf):

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

    def to_dict(self):
        tpsf_dict = {
            "preceeding_pause": self.preceeding_pause,
            "result_text": self.result_text,
        }
        return tpsf_dict

    def to_text(self):
        return f"""
Preceding pause: {self.preceeding_pause}
{self.result_text}
"""
