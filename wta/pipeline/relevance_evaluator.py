from ..settings import Settings
from .sentence_histories.sentence_classifier import SentenceClassifier
from .text_history.tpsf import TpsfECM
from .text_history.ts import TransformingSequence


class RelevanceEvaluator:
    def __init__(self, tpsf: TpsfECM, settings: Settings) -> None:
        self.tpsf = tpsf
        self.min_edit_distance = settings.config["min_edit_distance"]
        self.spellchecking = settings.config["enable_spellchecking"]
        self.ts_min_tokens_number = settings.config["ts_min_tokens_number"]
        self.edit_dist_combined_with_tok_number = settings.config[
            "combine_edit_distance_with_tok_number"
        ]
        self.punctuation_rel = settings.config["include_punctuation_edits"]
        self.nlp_model = settings.nlp_model
        self.sens_to_evaluate = self.tpsf.modified_sentences + self.tpsf.new_sentences
        self.relevance = None
        self.relevance_eval_results = {}
        self.determine_tpsf_relevance()
        for s in self.sens_to_evaluate:
            self.determine_sentence_relevance(s)

    def determine_tpsf_relevance(self) -> None:
        if self.tpsf.ts is not None:
            self.tpsf.check_tpsf_spelling()
            # check if ts meets the criteria defined in the tool config
            self.determine_ts_relevance(self.tpsf.ts)
            self.relevance = self.tpsf.ts.ts_relevance
            if (
                self.spellchecking is True
                and self.relevance is True
                and self.tpsf.contains_typos is True
            ):
                # overwrite relevance value if any typos discovered
                self.relevance = False
            self.capture_relevance_eval_results(
                len(self.tpsf.ts.text),
                len(self.tpsf.ts.tagged_tokens),
                self.tpsf.contains_typos,
            )

    def determine_ts_relevance(self, ts: TransformingSequence) -> None:
        ts_length = len(ts.text)
        ts_tokens_number = len(ts.tagged_tokens)
        ts_longer_than_min = ts_length >= self.min_edit_distance
        more_toks_than_min = ts_tokens_number >= self.ts_min_tokens_number
        if self.punctuation_rel is True and ts.contains_punctuation:
            ts.set_ts_relevance(True)
        elif self.edit_dist_combined_with_tok_number is True:
            if ts_longer_than_min and more_toks_than_min:
                ts.set_ts_relevance(True)
            else:
                ts.set_ts_relevance(False)
        elif self.edit_dist_combined_with_tok_number is False:
            if ts_longer_than_min or more_toks_than_min:
                ts.set_ts_relevance(True)
            else:
                ts.set_ts_relevance(False)

    def capture_relevance_eval_results(
        self, edit_distance: int, ts_tokens_number: int, tpsf_contains_typos: bool
    ) -> None:
        self.relevance_eval_results = {
            "edit_distance": edit_distance,
            "number_tokens_in_transformin_seq": ts_tokens_number,
            "tpsf_contains_typos": tpsf_contains_typos,
        }

    def determine_sentence_relevance(self, sen: SentenceClassifier) -> None:
        sen_transforming_sequence = sen.retrieve_tu_transforming_sequence()
        sen.set_tu_transforming_sequence(sen_transforming_sequence)
        self.determine_ts_relevance(sen.tu_transforming_sequence)
        sen.set_tu_relevance(sen.tu_transforming_sequence.ts_relevance)
