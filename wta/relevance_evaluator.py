from .utils.nlp import retrieve_affected_tokens


class RelevanceEvaluator:

    def __init__(self, tpsf, edit_distance_margin, filtering, nlp_model):
        self.tpsf = tpsf
        self.edit_distance_margin = edit_distance_margin
        self.filtering = filtering
        self.nlp_model = nlp_model
        self.morphosyntactic_relevance = None
        self.morphosyntactic_relevance_eval_results = []
        self.set_morphosyntactic_relevance()

    def evaluate_sen_morphosyntactic_relevance(self, sen):
        # affected_tokens is a list of tuples: previous word, current word with their indices
        affected_tokens = retrieve_affected_tokens(sen)
        # edited_tokens = filter_out_irrelevant_tokens(affected_tokens)  # TODO consider tokens filtering
        if len(affected_tokens) > 0:
            edit_distance, is_any_tok_oov, sentence_morphosyntactic_relevance = self.nlp_model.analyse_affected_tokens(affected_tokens, self.edit_distance_margin)
        else:
            # if no tokens are affected the TPSF is not relevant
            edit_distance, is_any_tok_oov, sentence_morphosyntactic_relevance = None, None, False
        return affected_tokens, edit_distance, is_any_tok_oov, sentence_morphosyntactic_relevance

    def capture_relevance_eval_results(self, sen, affected_tokens, is_any_tok_oov, edit_distance):
        self.morphosyntactic_relevance_eval_results.append({
            sen.pos_in_text: {
                'number_affected_tokens': len(affected_tokens),
                'affected_tokens': affected_tokens,
                'is_any_tok_oov': is_any_tok_oov,
                'edit_distance': edit_distance,
                'sentence_morphosyntactic_relevance': sen.sentence_morphosyntactic_relevance
            }
        })

    def determine_morphosyntactic_relevance(self):
        sentence_relevance_results = []
        # if any sentence in the TPSF has been edited, evaluate the relevance of the edits
        sens_to_evaluate = self.tpsf.modified_sentences + self.tpsf.new_sentences + self.tpsf.deleted_sentences
        for sen in sens_to_evaluate:
            affected_tokens, edit_distance, is_any_tok_oov, sen_morphosyntactic_relevance = self.evaluate_sen_morphosyntactic_relevance(sen)
            sen.set_sentence_morphosyntactic_relevance(sen_morphosyntactic_relevance)
            self.capture_relevance_eval_results(sen, affected_tokens, edit_distance, is_any_tok_oov)
            sentence_relevance_results.append(sen_morphosyntactic_relevance)
        self.morphosyntactic_relevance = True if True in sentence_relevance_results else False

    def set_morphosyntactic_relevance(self):
        if self.filtering is True:
            self.determine_morphosyntactic_relevance()

