from .utils.nlp import contains_end_punctuation_in_the_middle


class TransformingSequence:

    def __init__(self, text, label, nlp_model):
        self.text = text
        self.label = label
        self.tagged_tokens = None if text is None else nlp_model.tag_words(self.text)
        self.contains_end_punctuation_in_the_middle = contains_end_punctuation_in_the_middle(self.text)

    def __str__(self):
        printed_text = '' if self.text is None else f'{self.label}: {self.text}'
        return printed_text

