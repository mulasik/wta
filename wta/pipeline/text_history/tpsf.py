from ..sentence_histories.sentence_factory import SentenceFactory
from ..sentence_histories.sentence_classifier import SentenceClassifier
from wta.pipeline.relevance_evaluator import RelevanceEvaluator


class TpsfECM:

    def __init__(self, revision_id, content, ts, prev_tpsf, final=False):
        self.revision_id = revision_id
        self.text = content
        self.ts = ts
        self.prev_tpsf = prev_tpsf
        self.final = final
        self.sentences = self.retrieve_sentences()
        self.new_sentences = None
        self.modified_sentences = None
        self.deleted_sentences = None
        self.unchanged_sentences = None
        self.delta_current_previous = None
        self.delta_previous_current = None
        self.classify_sentences()
        self.contains_typos = None
        self.check_tpsf_spelling()
        self.relevance, self.relevance_eval_results = self.evaluate_relevance()
        self.irrelevant_ts_aggregated = None

    def retrieve_sentences(self):
        sentence_tokenizer = SentenceFactory(self.text, self.revision_id, self.ts)
        return sentence_tokenizer.sentences

    def classify_sentences(self):
        previous_tpsf_sentences = [] if not self.prev_tpsf else self.prev_tpsf.sentence_list
        sentence_classifier = SentenceClassifier(previous_tpsf_sentences, self.sentences, self.ts)
        self.new_sentences = sentence_classifier.new_sentences
        self.modified_sentences = sentence_classifier.modified_sentences
        self.deleted_sentences = sentence_classifier.deleted_sentences
        self.unchanged_sentences = sentence_classifier.unchanged_sentences
        self.delta_current_previous = sentence_classifier.delta_current_previous
        self.delta_previous_current = sentence_classifier.delta_previous_current

    def check_tpsf_spelling(self):
        # check if tpsf contains typos
        sentence_spellcheck_results = []
        sens_to_check = self.new_sentences + self.modified_sentences
        for s in sens_to_check:
            s.check_sentence_spelling()
            sentence_spellcheck_results.append(s.typos_detected)
        tpsf_contains_typos = True if True in sentence_spellcheck_results else False
        self.contains_typos = tpsf_contains_typos

    def evaluate_relevance(self):
        relevance_evaluator = RelevanceEvaluator(self)
        if not self.final:
            return relevance_evaluator.relevance, relevance_evaluator.relevance_eval_results
        else:
            return True, []

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

SENTENCE CLASSIFICATION:
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


class TpsfPcm:

    # TODO

    def __init__(self, output_chars, pause, final):
        if final is True:
            self.text = ''.join(output_chars)
        else:
            self.text = ''.join(output_chars[:-1])
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


