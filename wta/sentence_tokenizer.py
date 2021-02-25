from .utils.nlp import segment_sentences
from .sentence import SentenceCandidate, Sentence


class SentenceTokenizer:

    def __init__(self, text, revision_id, transforming_sequence):

        self.revision_id = revision_id
        self.transforming_sequence = transforming_sequence

        self.sentences = [] if text == '' else self.transform_into_sentence_list(text)

    def verify_sentence_segmentation(self, sentence_list):
        sentence_texts = []
        prev_sentence = None
        # verify sentence segmentation
        for sen in sentence_list:
            sentence_candidate = SentenceCandidate(sen.strip(), prev_sentence)
            if sentence_candidate.contains_end_punctuation:
                for ss in sentence_candidate.split_sens:
                    sentence_texts.append(ss)
            elif sentence_candidate.is_merge_candidate and sentence_candidate.merged_sens not in [s for s in sentence_texts]:
                sentence_texts.append(sentence_candidate.merged_sens)
            else:
                sentence_texts.append(sen)
            prev_sentence = sen
        return sentence_texts

    def transform_into_sentence_list(self, text):
        sentence_list = segment_sentences(text)
        verified_sentence_list = self.verify_sentence_segmentation(sentence_list)
        sentences = []
        pos = 0
        prev_sent_end_index = 0
        for sen in verified_sentence_list:
            sent_start_index = text.find(sen, prev_sent_end_index)
            sent_end_index = sent_start_index + len(sen.strip()) - 1
            sentence = Sentence(sen, sent_start_index, sent_end_index, self.revision_id, pos, self.transforming_sequence)
            sentences.append(sentence)
            prev_sent_end_index = sent_end_index
            pos += 1
        return sentences

