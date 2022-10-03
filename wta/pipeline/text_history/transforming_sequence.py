import settings

from wta.utils.nlp import contains_end_punctuation_in_the_middle


class TransformingSequence:

    def __init__(self, text, label, startpos, endpos):
        self.text = text
        self.label = label
        self.startpos = startpos
        self.endpos = endpos
        self.tagged_tokens = None if text is None else settings.nlp_model.tag_words(self.text)
        self.contains_punctuation = True if 'PUNCT' in [tok['pos'] for tok in self.tagged_tokens] else False
        self.contains_end_punctuation_in_the_middle = contains_end_punctuation_in_the_middle(self.text)
        self.ts_relevance = None

    def set_text(self, text):
        self.text = text

    def set_ts_relevance(self, relevance):
        self.ts_relevance = relevance

    def __str__(self):
        return '' if self.text is None else f'{self.label} ({self.startpos}-{self.endpos}): "{self.text}"'

