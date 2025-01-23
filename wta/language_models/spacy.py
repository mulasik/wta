from typing import TypedDict

import language_tool_python
from spacy.language import Language

from ..pipeline.sentence_layer.sentence_parsing.models import Languages
from ..utils.nlp import TokensDict, check_edit_distance


class TaggedWord(TypedDict):
    text: str
    pos: str
    pos_details: str
    dep: str
    lemma: str
    oov: bool
    is_typo: bool
    is_single_char: bool
    is_punct: bool
    is_space: bool


class SpacyModel:
    nlp: Language

    def __init__(self, lang: str) -> None:
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
        elif lang == Languages.FR:
            from spacy.lang.fr import French

            self.nlp = French()
            print("Loading Spacy model for French...")
            self.nlp = spacy.load("fr_core_news_md")
            self.tool = language_tool_python.LanguageTool("fr-FR")
        else:
            print("FAILURE: Could not recognize the language.")

    def tag_words(self, text: str) -> list[TaggedWord]:
        doc = self.nlp(text)
        tags: list[TaggedWord] = []
        for token in doc:
            matches = self.tool.check(token.text)
            is_typo = bool(matches and matches[0].ruleId == "GERMAN_SPELLER_RULE")
            is_single_char = len(token) == 1
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

    def segment_text(self, text: str) -> list[str]:
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

    # def collect_additional_tokens_tags(
    #     self, text: str
    # ) -> tuple[str, str, bool, bool, bool, float] | None:
    #     doc = self.nlp(text)
    #     for token in doc:
    #         return (
    #             token.content,
    #             token.shape_,
    #             token.is_alpha,
    #             token.is_stop,
    #             token.has_vector,
    #             token.vector_norm,
    #         )
    #     return None

    # def check_if_same_words(self, editted_word: str, result_word: str) -> bool | None:
    #     if not editted_word or not result_word:
    #         return None
    #     editted_word_tokens = self.nlp(editted_word)
    #     result_word_tokens = self.nlp(result_word)
    #     return (
    #         editted_word_tokens.pos_ == result_word_tokens.pos_
    #         and editted_word_tokens.lemma_ == result_word_tokens.lemma_
    #         and editted_word_tokens.dep_ == result_word_tokens.dep_
    #     )

    def check_if_any_oov(self, tokens: list[TokensDict]) -> bool:
        for t in tokens:
            pt = t["prev"]
            ct = t["cur"]
            if pt is not None and pt["text"] != "":
                pt_text = pt["text"]
                pt_tokens = self.nlp(pt_text)
                pt_token = pt_tokens[0]
                pt_oov = pt_token.is_oov
            else:
                pt_oov = None
            if ct is not None and ct["text"] != "":
                ct_text = ct["text"]
                ct_tokens = self.nlp(ct_text)
                ct_token = ct_tokens[0]
                ct_oov = ct_token.is_oov
            else:
                ct_oov = None
            if pt_oov is True or ct_oov is True:
                return True
        return False

    def check_if_token_a_typo(self, token: str) -> bool:
        matches = self.tool.check(token)
        return bool(matches and matches[0].ruleId == "GERMAN_SPELLER_RULE")

    def check_if_any_typos(self, tokens: list[TokensDict]) -> bool:
        typos = []
        for t in tokens:
            pt = t["prev"]
            ct = t["cur"]
            if pt is not None and pt["text"] != "":
                pt_text = pt["text"].strip(",.:")
                matches = self.tool.check(pt_text)
                pt_is_typo = bool(
                    matches and matches[0].ruleId == "GERMAN_SPELLER_RULE"
                )
            else:
                pt_is_typo = None
            typos.append(pt_is_typo)
            if ct is not None and ct["text"] != "":
                ct_text = ct["text"].strip(",.:")
                matches = self.tool.check(ct_text)
                ct_is_typo = bool(
                    matches and matches[0].ruleId == "GERMAN_SPELLER_RULE"
                )
            else:
                ct_is_typo = None
            typos.append(ct_is_typo)
        return True in typos

    def analyse_affected_tokens(
        self, affected_tokens: list[TokensDict], predef_edit_distance: int
    ) -> tuple[int | None, bool, bool, bool]:
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
                contains_one_char_token = 1 in [
                    len(t["cur"]["text"])
                    for t in affected_tokens
                    if t["cur"] is not None
                ]
                if contains_one_char_token:
                    morphosyntactic_relevance = False
                    edit_distance = None
                else:
                    # if more than 1 token is affected and none of them is a typo
                    # and non of them consists only of one character, the TPSF is relevant
                    morphosyntactic_relevance = True
                    edit_distance = None
        return edit_distance, is_any_tok_oov, is_any_tok_typo, morphosyntactic_relevance
