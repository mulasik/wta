from .utils.nlp import (contains_end_punctuation_at_the_end,
                        retrieve_end_punctuation,
                        is_short_sequence,
                        starts_with_lowercase_letter)
import json

class SentenceCandidate:

    def __init__(self, text, prev_sen):
        self.text = text
        self.prev_sen = prev_sen

        # check if the sentence contains ? or ! inside the sentence
        delimiter = retrieve_end_punctuation(self.text)
        self.contains_end_punctuation = True if delimiter else False
        self.split_sens = self.split_sen(delimiter) if self.contains_end_punctuation else None

        if self.prev_sen:
            # check if the sentence is very short and start with a lowercase letter
            # and the previous sentence ends with ?, ! or .
            self.is_merge_candidate = self.check_if_merge_candidate()
            self.merged_sens = self.prev_sen + ' ' + self.text if self.is_merge_candidate is True else None
        else:
            self.is_merge_candidate = False

    def split_sen(self, delimiter):
        split_sens = self.text.split(delimiter)
        split_sens[0] = split_sens[0] + delimiter
        return split_sens

    def check_if_merge_candidate(self):
        short_seq_len = 4
        return is_short_sequence(self.text, short_seq_len) and starts_with_lowercase_letter(self.text) and not contains_end_punctuation_at_the_end(self.prev_sen)


class Sentence:

    def __init__(self, text, start, end, revision_id, pos, transforming_sequence):
        self.text = text
        self.start_index = start
        self.end_index = end
        self.revision_id = revision_id
        self.pos_in_text = pos
        self.label = None
        self.transforming_sequence = transforming_sequence

        self.revision_relevance = None  # TODO

        self.previous_sentence = None

    def set_label(self, label):
        self.label = label

    def set_previous_text_version(self, sentence):
        self.previous_sentence = sentence

    def set_label(self, label):
        self.label = label

    def set_revision_relevance(self, revision_relevance):
        self.revision_relevance = revision_relevance

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

