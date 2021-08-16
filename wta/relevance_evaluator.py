from .utils.nlp import retrieve_affected_tokens


class RelevanceEvaluator:

    def __init__(self, tpsf, edit_distance_margin, filtering, spelling_check, nlp_model):
        self.tpsf = tpsf
        self.edit_distance_margin = edit_distance_margin
        self.filtering = filtering
        self.spelling_check = spelling_check
        self.nlp_model = nlp_model
        self.morphosyntactic_relevance = None
        self.morphosyntactic_relevance_eval_results = []
        self.set_morphosyntactic_relevance()

    def evaluate_sen_morphosyntactic_relevance(self, sen):
        cur_sen = sen.text
        prev_sen = '' if sen.previous_sentence is None else sen.previous_sentence.text
        # affected_tokens is a list of tuples: previous word, current word with their indices
        affected_tokens = retrieve_affected_tokens(prev_sen, cur_sen)
        print(f'TS {self.tpsf.transforming_sequence.label}:')
        print(self.tpsf.transforming_sequence.text)
        print('SENTENCE IMPACTED:')
        print(sen.text, sen.previous_sentence)
        print('AFFECTED STRINGS:')
        cur_affected_string = ' '.join([t['cur_tok'][0] for t in affected_tokens])
        prev_affected_string = ' '.join([t['prev_tok'][0] for t in affected_tokens])
        print('prev:', prev_affected_string)
        print('cur:', cur_affected_string)
        # edited_tokens = filter_out_irrelevant_tokens(affected_tokens)  # TODO consider tokens filtering
        if len(affected_tokens) > 0:
            edit_distance, is_any_tok_oov, is_any_tok_typo, sentence_morphosyntactic_relevance = self.nlp_model.analyse_affected_tokens(affected_tokens, self.edit_distance_margin)
        else:
            # if no tokens are affected the TPSF is not relevant
            edit_distance, is_any_tok_oov, is_any_tok_typo, sentence_morphosyntactic_relevance = None, None, None, False
        return affected_tokens, edit_distance, is_any_tok_oov, is_any_tok_typo, sentence_morphosyntactic_relevance

    def capture_relevance_eval_results(self, sen, affected_tokens, is_any_tok_oov, is_any_tok_typo, edit_distance):
        self.morphosyntactic_relevance_eval_results.append({
            sen.pos_in_text: {
                'number_affected_tokens': len(affected_tokens),
                'affected_tokens': affected_tokens,
                'is_any_tok_oov': is_any_tok_oov,
                'is_any_tok_typo': is_any_tok_typo,
                'edit_distance': edit_distance,
                'sentence_morphosyntactic_relevance': sen.sentence_morphosyntactic_relevance
            }
        })

    def determine_morphosyntactic_relevance(self):
        sentence_relevance_results = []
        # if any sentence in the TPSF has been edited, evaluate the relevance of the edits
        sens_to_evaluate = self.tpsf.modified_sentences + self.tpsf.new_sentences + self.tpsf.deleted_sentences
        if len(sens_to_evaluate) > 0:
            print('TPSF')
            print(self.tpsf.result_text)
            print('Modified', self.tpsf.modified_sentences)
            print('New', self.tpsf.new_sentences)
            print('Deleted', self.tpsf.deleted_sentences)
            for sen in sens_to_evaluate:
                affected_tokens, edit_distance, is_any_tok_oov, is_any_tok_typo, sen_morphosyntactic_relevance = self.evaluate_sen_morphosyntactic_relevance(sen)
                sen.set_sentence_morphosyntactic_relevance(sen_morphosyntactic_relevance)
                self.capture_relevance_eval_results(sen, affected_tokens, is_any_tok_oov, is_any_tok_typo, edit_distance)
                sentence_relevance_results.append(sen_morphosyntactic_relevance)
            self.morphosyntactic_relevance = False if False in sentence_relevance_results else True
        else:
            self.morphosyntactic_relevance = False

    def set_morphosyntactic_relevance(self):
        if self.filtering is True:
            self.determine_morphosyntactic_relevance()

