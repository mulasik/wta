from .utils.nlp import retrieve_affected_tokens, analyse_affected_tokens


class RelevanceEvaluator:

    def __init__(self, tpsf, edit_distance, filtering):
        self.tpsf = tpsf
        self.edit_distance = edit_distance
        self.filtering = filtering
        self.morphosyntactic_relevance = None
        self.morphosyntactic_relevance_eval_results = []
        self.set_morphosyntactic_relevance()

    def evaluate_morphosyntactic_relevance(self):
        for sen in self.tpsf.modified_sentences:
            # affected_tokens is a list of tuples: previous word, current word with their indices
            affected_tokens = retrieve_affected_tokens(sen)
            # edited_tokens = filter_out_irrelevant_tokens(affected_tokens)  # TODO consider if it might be useful
            if len(affected_tokens) > 0:
                self.edit_distance, is_any_tok_oov, self.morphosyntactic_relevance = analyse_affected_tokens(affected_tokens, self.edit_distance)
            else:
                # if no tokens are affected the TPSF is not relevant
                self.morphosyntactic_relevance = False
                is_any_tok_oov = None
                self.edit_distance = None
            self.morphosyntactic_relevance_eval_results.append({
                sen.pos_in_text: {
                    'number_affected_tokens': len(affected_tokens),
                    'affected_tokens': affected_tokens,
                    'is_any_tok_oov': is_any_tok_oov,
                    'edit_distance': self.edit_distance,
                }
            })

    def determine_morphosyntactic_relevance(self):
        if len(self.tpsf.modified_sentences) > 0:
            # if any sentence in the TPSF has been edited, evaluate the relevance of the edits
            self.evaluate_morphosyntactic_relevance()
        else:
            # if no sentence modifications are detected, immediately mark the TPSF as irrelevant
            self.morphosyntactic_relevance_eval_results = None
            self.morphosyntactic_relevance = False

    def set_morphosyntactic_relevance(self):
        if self.filtering is True:
            self.determine_morphosyntactic_relevance()

