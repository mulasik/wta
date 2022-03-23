from .utils.nlp import (contains_end_punctuation_at_the_end,
                        retrieve_end_punctuation,
                        is_short_sequence,
                        starts_with_lowercase_letter,
                        retrieve_mismatch_range_for_sentence_pair)
from wta.transforming_sequence import TransformingSequence
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

    def __init__(self, text, start, end, revision_id, pos, transforming_sequence, nlp_model):
        self.text = text
        self.start_index = start
        self.end_index = end
        self.revision_id = revision_id
        self.pos_in_text = pos
        self.is_any_tok_oov = False
        self.label = None
        self.transforming_sequence = transforming_sequence
        self.tagged_tokens = None # if self.text is None else nlp_model.tag_words(self.text)
        self.typos_detected = None

        self.nlp_model = nlp_model

        self.sentence_relevance = None
        self.revision_relevance = None
        self.irrelevant_ts_aggregated = []

        self.previous_sentence = None
        self.sen_transforming_sequence = None

    def set_label(self, label):
        self.label = label

    def set_previous_text_version(self, sentence):
        self.previous_sentence = sentence

    def set_label(self, label):
        self.label = label

    def set_tagged_tokens_and_typos(self, tagged_tokens):
        self.tagged_tokens = tagged_tokens
        self.typos_detected = self.check_sentence_spelling()

    def set_typos_detected(self, typos_detected):
        self.typos_detected = typos_detected

    def set_is_any_tok_oov(self, is_any_tok_oov):
        self.is_any_tok_oov = is_any_tok_oov

    def set_sentence_relevance(self, relevance):
        self.sentence_relevance = relevance

    def set_sentence_transforming_sequence(self, sen_transforming_sequence):
        self.sen_transforming_sequence = sen_transforming_sequence

    def set_revision_relevance(self, revision_relevance):
        self.revision_relevance = revision_relevance

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def retrieve_sen_transforming_sequence(self):
        prev_sen = '' if self.previous_sentence is None else self.previous_sentence.text
        edit, mismatch_range, relevant = retrieve_mismatch_range_for_sentence_pair(prev_sen, self.text)
        if relevant == 'cur':
            mismatch_text = self.text[mismatch_range[0][0]:mismatch_range[0][-1]]
        elif relevant == 'prev':
            mismatch_text = prev_sen[mismatch_range[0][0]:mismatch_range[0][-1]]
        else:
            mismatch_text = ''
            print(f'Warning. The mismatch text is empty. Apparently no mismatch detected. Mismatch range: {mismatch_range}. Relevant sentence: {relevant}.')
        if edit == 'insert':
            label = 'insertion'
        elif edit == 'delete':
            label = 'deletion'
        elif edit == 'replace':
            label = 'insertion' if relevant == 'cur' else 'deletion'
        else:
            print('Warning. Empty transforming sequence label.')
            label = ''
        sen_transforming_sequence = TransformingSequence(mismatch_text, label, self.nlp_model)
        return sen_transforming_sequence

    def check_sentence_spelling(self):
        toks_spellcheck_results = [t['is_typo'] for t in self.tagged_tokens]
        sen_contains_typos = True if True in toks_spellcheck_results else False
        return sen_contains_typos

    def set_irrelevant_ts_aggregated(self, irrelevant_ts_aggregated):
        self.irrelevant_ts_aggregated = irrelevant_ts_aggregated

    def __str__(self):
        return f'{self.text}'

