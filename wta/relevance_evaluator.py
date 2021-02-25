class RelevanceEvaluator:

    def __init__(self):
        self.var = 0

    # # TODO move
    # def analyse_affected_tokens(affected_tokens: list, predef_edit_distance: int):
    #     is_any_tok_oov = check_if_any_oov(affected_tokens)
    #     if is_any_tok_oov is True:
    #         # if any of the tokens is OOV the TPSF is not relevant
    #         morphosyntactic_relevance = False
    #         edit_distance = None
    #     else:
    #         if len(affected_tokens) == 1:
    #             # if the edit was performed within one token, check the edit distance
    #             affected_token = affected_tokens[0]
    #             edit_distance = check_edit_distance(affected_token)
    #             if edit_distance <= predef_edit_distance:
    #                 # if the edit distance is less than the pre-defined edit distance, the TPSF is not relevant
    #                 morphosyntactic_relevance = False
    #             else:
    #                 morphosyntactic_relevance = True
    #         else:
    #             # if more than 1 token is affected and none of them is OOV, the TPSF is relevant
    #             morphosyntactic_relevance = True
    #             edit_distance = None
    #     return edit_distance, is_any_tok_oov, morphosyntactic_relevance
    #
    # def evaluate_morphosyntactic_relevance(edited_sentences: dict, predef_edit_distance: int) -> tuple:
    #     morphosyntactic_relevance_eval_results = []
    #     for sens in edited_sentences:
    #         # affected_tokens is a list of tuples: previous word, current word with their indices
    #         affected_tokens = retrieve_affected_tokens(sens)
    #         # edited_tokens = filter_out_irrelevant_tokens(affected_tokens)  # TODO consider if it might be useful
    #         if len(affected_tokens) > 0:
    #             edit_distance, is_any_tok_oov, morphosyntactic_relevance = analyse_affected_tokens(affected_tokens,
    #                                                                                                predef_edit_distance)
    #         else:
    #             # if no tokens are affected the TPSF is not relevant
    #             morphosyntactic_relevance = False
    #             is_any_tok_oov = None
    #             edit_distance = None
    #         morphosyntactic_relevance_eval_results.append({
    #             sens['current_sentence']['pos_in_text']: {
    #                 'number_affected_tokens': len(affected_tokens),
    #                 'affected_tokens': affected_tokens,
    #                 'is_any_tok_oov': is_any_tok_oov,
    #                 'edit_distance': edit_distance,
    #             }
    #         })
    #         return morphosyntactic_relevance_eval_results, morphosyntactic_relevance
    #
    # def determine_morphosyntactic_relevance(tpsf: dict, predef_edit_distance: int) -> tuple:
    #     edited_sentences = tpsf['sentences']['edited_sentences']
    #     if len(edited_sentences) > 0:
    #         # if any sentence in the TPSF has been edited, evaluate the relevance of the edits
    #         morphosyntactic_relevance_eval_results, morphosyntactic_relevance = evaluate_morphosyntactic_relevance(
    #             edited_sentences, predef_edit_distance)
    #     else:
    #         # if no sentence modifications are detected, immediately mark the TPSF as irrelevant
    #         morphosyntactic_relevance_eval_results = None
    #         morphosyntactic_relevance = False
    #     return morphosyntactic_relevance_eval_results, morphosyntactic_relevance
    #
    # def enrich_tpsf_with_morphosyntactic_relevance_details(tpsf: dict, filtering: bool, predef_edit_dist: int):
    #     if filtering is True:
    #         tpsf['morphosyn_relevance_evaluation'], tpsf[
    #             'morphosyntactic_relevance'] = determine_morphosyntactic_relevance(tpsf, predef_edit_dist)
    #     else:
    #         tpsf['morphosyn_relevance_evaluation'], tpsf['morphosyntactic_relevance'] = None, None