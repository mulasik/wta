class RelevanceEvaluator:

    def __init__(self, tpsf, min_edit_distance, ts_min_tokens_number, spellchecking, punctuation_rel, nlp_model):
        self.tpsf = tpsf
        self.min_edit_distance = min_edit_distance
        self.spellchecking = spellchecking
        self.ts_min_tokens_number = ts_min_tokens_number
        self.punctuation_rel = punctuation_rel
        self.nlp_model = nlp_model
        self.sens_to_evaluate = self.tpsf.modified_sentences + self.tpsf.new_sentences
        self.relevance = None
        self.relevance_eval_results = {}
        self.determine_tpsf_relevance()
        for s in self.sens_to_evaluate:
            self.determine_sentence_relevance(s)

    def determine_ts_relevance(self, ts):
        ts_length = len(ts.text)
        ts_tokens_number = len(ts.tagged_tokens)
        ts_longer_than_min = ts_length >= self.min_edit_distance
        more_toks_than_min = ts_tokens_number >= self.ts_min_tokens_number
        if self.punctuation_rel is True and ts.contains_punctuation:
            ts.set_ts_relevance(True)
        elif ts_longer_than_min and more_toks_than_min:
            ts.set_ts_relevance(True)
        else:
            ts.set_ts_relevance(False)

    def determine_sentence_relevance(self, sen):
        sen_transforming_sequence = sen.retrieve_sen_transforming_sequence()
        sen.set_sentence_transforming_sequence(sen_transforming_sequence)
        self.determine_ts_relevance(sen.sen_transforming_sequence)
        sen.set_sentence_relevance(sen.sen_transforming_sequence.ts_relevance)

    def determine_tpsf_relevance(self):
        if self.tpsf.transforming_sequence is not None:
            self.tpsf.check_tpsf_spelling()
            # check if ts meets the criteria defined in the tool config
            self.determine_ts_relevance(self.tpsf.transforming_sequence)
            self.relevance = self.tpsf.transforming_sequence.ts_relevance
            if self.spellchecking is True:
                # overwrite relevance value if any typos discovered
                if self.relevance is True and self.tpsf.contains_typos is True:
                    self.relevance = False
            self.capture_relevance_eval_results(len(self.tpsf.transforming_sequence.text), len(self.tpsf.transforming_sequence.tagged_tokens), self.tpsf.contains_typos)

    def capture_relevance_eval_results(self, edit_distance, ts_tokens_number, tpsf_contains_typos):
        self.relevance_eval_results = {
                'edit_distance': edit_distance,
                'number_tokens_in_transformin_seq': ts_tokens_number,
                'tpsf_contains_typos': tpsf_contains_typos,
        }

