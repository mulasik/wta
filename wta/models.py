from .utils.nlp import check_edit_distance
import language_tool_python


class SpacyModel:

    def __init__(self, lang):
        import spacy
        if lang == 'German':
            from spacy.lang.de import German
            self.nlp = German()
            print('Loading Spacy model for German...')
            self.nlp = spacy.load("de_core_news_md")
            self.tool = language_tool_python.LanguageTool('de-DE')
        elif lang == 'English':
            from spacy.lang.en import English
            self.nlp = English()
            print('Loading Spacy model for English...')
            self.nlp = spacy.load("en_core_web_md")
            self.tool = language_tool_python.LanguageTool('en-US')
        elif lang == 'Greek':
            from spacy.lang.el import Greek
            self.nlp = Greek()
            print('Loading Spacy model for Greek...')
            self.nlp = spacy.load("el_core_news_md")
            self.tool = language_tool_python.LanguageTool('el-GR')

    def tag_words(self, text: str) -> list:
        doc = self.nlp(text)
        tags = []
        for token in doc:
            is_typo = True if self.tool.check(token.text) else False
            is_single_char = True if len(token) == 1 else False
            tags.append({
                'text': token.text,
                'pos': token.pos_,
                'pos_details': token.tag_,
                'dep': token.dep_,
                'lemma': token.lemma_,
                'oov': token.is_oov,
                'is_typo': is_typo,
                'is_single_char': is_single_char,
                'is_punct': token.is_punct,
                'is_space': token.is_space
            })
        return tags

    def segment_sentences(self, text: str) -> list:
        doc = self.nlp(text)
        sentences = []
        for sent in doc.sents:
            sent_text = sent.text.strip()
            sentences.append(sent_text)
        return sentences

    def collect_additional_tokens_tags(self, text: str) -> tuple:
        doc = self.nlp(text)
        for token in doc:
            return token.text, token.shape_, token.is_alpha, token.is_stop, token.has_vector, token.vector_norm

    def check_if_same_words(self, editted_word: str, result_word: str) -> bool:
        if editted_word and result_word:
            editted_word = self.nlp(editted_word)
            result_word = self.nlp(result_word)
            if editted_word.pos_ != result_word.pos_ or editted_word.lemma_ != result_word.lemma_ or editted_word.dep_ != result_word.dep_:
                return False
            else:
                return True

    def check_if_any_oov(self, tokens: list) -> bool:
        for t in tokens:
            pt = t['prev_tok']
            ct = t['cur_tok']
            if pt[0] != '':
                pt = pt[0]
                pt = self.nlp(pt)
                pt = pt[0]
                pt_oov = pt.is_oov
            else:
                pt_oov = None
            if ct[0] != '':
                ct = ct[0]
                ct = self.nlp(ct)
                ct = ct[0]
                ct_oov = ct.is_oov
            else:
                ct_oov = None
            if pt_oov is True or ct_oov is True:
                return True
        return False

    def check_if_any_typos(self, tokens: list) -> bool:
        typos = []
        for t in tokens:
            pt = t['prev_tok']
            ct = t['cur_tok']
            if pt[0] != '':
                pt = pt[0].strip(',.:')
                pt_is_typo = True if self.tool.check(pt) and self.tool.check(pt)[0].ruleId == 'GERMAN_SPELLER_RULE' else False
            else:
                pt_is_typo = None
            typos.append(pt_is_typo)
            if ct[0] != '':
                ct = ct[0].strip(',.:')
                ct_is_typo = True if self.tool.check(ct) and self.tool.check(ct)[0].ruleId == 'GERMAN_SPELLER_RULE' else False
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
                if edit_distance <= predef_edit_distance:
                    # if the edit distance is less than the pre-defined edit distance, the TPSF is not relevant
                    morphosyntactic_relevance = False
                else:
                    morphosyntactic_relevance = True
            else:
                contains_one_char_token = True if 1 in [len(t['cur_tok'][0]) for t in affected_tokens] else False
                if contains_one_char_token:
                    morphosyntactic_relevance = False
                    edit_distance = None
                else:
                    # if more than 1 token is affected and none of them is a typo
                    # and non of them consists only of one character, the TPSF is relevant
                    morphosyntactic_relevance = True
                    edit_distance = None
        return edit_distance, is_any_tok_oov, is_any_tok_typo, morphosyntactic_relevance

