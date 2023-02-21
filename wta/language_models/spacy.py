import language_tool_python

from wta.pipeline.sentence_parsing.models import Languages
from wta.utils.nlp import check_edit_distance


class SpacyModel:
    def __init__(self, lang):
        import spacy

        if lang == Languages.DE:
            from spacy.lang.de import German

            self.nlp = German()
            print("Loading Spacy model for German...")
            self.nlp = spacy.load("de_core_news_md")
            self.tool = language_tool_python.LanguageTool("de-DE")
        elif lang == Languages.EN:
            from spacy.lang.en import English

            self.nlp = English()
            print("Loading Spacy model for English...")
            self.nlp = spacy.load("en_core_web_md")
            self.tool = language_tool_python.LanguageTool("en-US")
        elif lang == Languages.GR:
            from spacy.lang.el import Greek

            self.nlp = Greek()
            print("Loading Spacy model for Greek...")
            self.nlp = spacy.load("el_core_news_md")
            self.tool = language_tool_python.LanguageTool("el-GR")
        else:
            print("FAILURE: Could not recognize the language.")

    def tag_words(self, text: str) -> list:
        doc = self.nlp(text)
        tags = []
        for token in doc:
            is_typo = (
                True
                if self.tool.check(token.text)
                and self.tool.check(token.text)[0].ruleId == "GERMAN_SPELLER_RULE"
                else False
            )
            is_single_char = True if len(token) == 1 else False
            tags.append(
                {
                    "text": token.text,
                    "pos": token.pos_,
                    "pos_details": token.tag_,
                    "dep": token.dep_,
                    "lemma": token.lemma_,
                    "oov": token.is_oov,
                    "is_typo": is_typo,
                    "is_single_char": is_single_char,
                    "is_punct": token.is_punct,
                    "is_space": token.is_space,
                }
            )
        return tags

    def segment_text(self, text: str) -> list:
        doc = self.nlp(text)
        sentences = []
        # Attention:
        # Spacy handles single whitespaces at the beginning and at the end differently
        # then sequences of multiple whitespaces at the beginning and at the end
        # A single whitespace:
        # ' Hello everybody! ' after segmentation will return a sentence [' Hello everybody!']
        # >>> only the initial single whitespace is part of the sentence, the trailing whitespace is cut off
        # A sequence of multiple whitespaces:
        # '  Hello everybody!  I missed you a lot  ' will return ['  Hello everybody!  ', 'I missed you a lot  ']
        # >>> the multiple whitespaces between the sentences or at the end are attached to the preceding sentence.
        # If there is no preceding sentence the multiple whitespaces are attached to the first sentence.
        # Missing whitespace between sentences:
        # ' Hello everybody!I missed you a lot ' will return [' Hello everybody!I missed you a lot ']
        # >>> If the whitespace is missing, the sequence is interpreted as one sentence!
        # whitespace_ returns the trailing space character if present.
        # is_sent_start	Does the token start a sentence? bool or None if unknown. Defaults to True for the first token in the Doc.
        # is_sent_end	Does the token end a sentence? bool or None if unknown.
        for sent in doc.sents:
            sentences.append(sent.text_with_ws)
        return sentences

    def collect_additional_tokens_tags(self, text: str) -> tuple:
        doc = self.nlp(text)
        for token in doc:
            return (
                token.content,
                token.shape_,
                token.is_alpha,
                token.is_stop,
                token.has_vector,
                token.vector_norm,
            )

    def check_if_same_words(self, editted_word: str, result_word: str) -> bool:
        if editted_word and result_word:
            editted_word = self.nlp(editted_word)
            result_word = self.nlp(result_word)
            if (
                editted_word.pos_ != result_word.pos_
                or editted_word.lemma_ != result_word.lemma_
                or editted_word.dep_ != result_word.dep_
            ):
                return False
            else:
                return True

    def check_if_any_oov(self, tokens: list) -> bool:
        for t in tokens:
            pt = t["prev"]
            ct = t["cur"]
            if pt is not None and pt["text"] != "":
                pt = pt["text"]
                pt = self.nlp(pt)
                pt = pt[0]
                pt_oov = pt.is_oov
            else:
                pt_oov = None
            if ct is not None and ct["text"] != "":
                ct = ct["text"]
                ct = self.nlp(ct)
                ct = ct[0]
                ct_oov = ct.is_oov
            else:
                ct_oov = None
            if pt_oov is True or ct_oov is True:
                return True
        return False

    def check_if_token_a_typo(self, token: str) -> bool:
        return (
            True
            if self.tool.check(token)
            and self.tool.check(token)[0].ruleId == "GERMAN_SPELLER_RULE"
            else False
        )

    def check_if_any_typos(self, tokens: list) -> bool:
        typos = []
        for t in tokens:
            pt = t["prev"]
            ct = t["cur"]
            if pt is not None and pt["text"] != "":
                pt = pt["text"].strip(",.:")
                pt_is_typo = (
                    True
                    if self.tool.check(pt)
                    and self.tool.check(pt)[0].ruleId == "GERMAN_SPELLER_RULE"
                    else False
                )
            else:
                pt_is_typo = None
            typos.append(pt_is_typo)
            if ct is not None and ct["text"] != "":
                ct = ct["text"].strip(",.:")
                ct_is_typo = (
                    True
                    if self.tool.check(ct)
                    and self.tool.check(ct)[0].ruleId == "GERMAN_SPELLER_RULE"
                    else False
                )
            else:
                ct_is_typo = None
            typos.append(ct_is_typo)
        return True in typos

    def analyse_affected_tokens(self, affected_tokens: list, predef_edit_distance: int):
        is_any_tok_oov = self.check_if_any_oov(affected_tokens)
        is_any_tok_typo = self.check_if_any_typos(affected_tokens)
        if is_any_tok_typo is True:
            # if any of the tokens is OOV the TPSF is not relevant
            morphosyntactic_relevance = False
            edit_distance = None
        else:
            if len(affected_tokens) == 1:
                # if the edit was performed within one token, check the edit distance
                affected_token = affected_tokens[0]
                edit_distance = check_edit_distance(affected_token)
                # if the edit distance is less than the pre-defined edit distance, the TPSF is not relevant
                morphosyntactic_relevance = edit_distance > predef_edit_distance
            else:
                contains_one_char_token = (
                    True
                    if 1
                    in [
                        len(t["cur"]["text"])
                        for t in affected_tokens
                        if t["cur"] is not None
                    ]
                    else False
                )
                if contains_one_char_token:
                    morphosyntactic_relevance = False
                    edit_distance = None
                else:
                    # if more than 1 token is affected and none of them is a typo
                    # and non of them consists only of one character, the TPSF is relevant
                    morphosyntactic_relevance = True
                    edit_distance = None
        return edit_distance, is_any_tok_oov, is_any_tok_typo, morphosyntactic_relevance
