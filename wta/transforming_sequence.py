from .utils.nlp import tag_words, contains_end_punctuation_internally


class TransformingSequence:

    def __init__(self, text, label):
        self.text = text
        self.label = label
        self.tagged_tokens = None if text is None else tag_words(self.text)
        self.contains_end_punctuation_internally = contains_end_punctuation_internally(self.text)

    def __str__(self):
        printed_text = '' if self.text is None else f'{self.label}: {self.text}'
        return printed_text

