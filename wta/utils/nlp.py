from wta.models import SpacyModel
import nltk
import re
import difflib


def tag_words(text: str) -> list:
    doc = SpacyModel.nlp(text)
    tags = []
    for token in doc:
        tags.append({
            'text': token.text,
            'pos': token.pos_,
            'pos_details': token.tag_,
            'dep': token.dep_,
            'lemma': token.lemma_,
            'oov': token.is_oov,
            'is_punct': token.is_punct,
            'is_space': token.is_space
        })
    return tags


def segment_sentences(text: str) -> list:
    doc = SpacyModel.nlp(text)
    sentences = []
    for sent in doc.sents:
        sent_text = sent.text.strip()
        sentences.append(sent_text)
    return sentences


def segment_sentences_with_nltk(text):
    sent_detector = nltk.data.load('tokenizers/punkt/german.pickle')
    sentences = list(sent_detector.tokenize(text.strip()))
    return sentences


def contains_end_punctuation_internally(seq):
    return True if re.search(r'([\w\s,;:\-]*)([?!.])([\w\s,:;\-]*)', seq) is not None else False


def retrieve_end_punctuation(seq):
    end_punctuation = re.search(r'([\w\s,;:\-]+)([?!\n])([\w\s,:;\-]+)', seq)
    if end_punctuation:
        return end_punctuation.group(2)
    else:
        return None


def contains_end_punctuation_at_the_end(seq):
    end_punctuation_at_end = re.search(r'([\w\s,;:\-]+)[.?!]$', seq)
    if end_punctuation_at_end:
        return True
    else:
        return False


def is_short_sequence(seq, length):
    return len(seq) < length


def starts_with_lowercase_letter(seq):
    lowercase_at_beginning = re.search(r'^[a-zäöü]', seq)
    if lowercase_at_beginning is not None:
        return True
    else:
        return False


def calculate_sequence_similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def retrieve_match_range(seq1: str, seq2: str) -> tuple:
    seq_match = difflib.SequenceMatcher(None, seq1.strip(), seq2.strip())
    match_ranges = seq_match.get_matching_blocks()
    return match_ranges


def retrieve_mismatch_ranges(seq1: str, seq2: str) -> tuple:
    seq_match = difflib.SequenceMatcher(None, seq1, seq2)
    mismatch_ranges = seq_match.get_opcodes()
    return mismatch_ranges


def check_overlap_with_seq_beginning(s1, s2):
    # s1 is modifying seq and s2 is sen
    index = 1
    s1_beginning = s1[:index]
    if s1_beginning in s2:
        while s1_beginning in s2 and len(s1_beginning) < len(s1):
            index += 1
            s1_beginning = s1[:index]
        return True, s1_beginning, index
    else:
        return False, '', None


def check_overlap_with_seq_end(s1, s2):
    # s1 is modifying seq and s2 is sen
    index = len(s1)
    s1_end = s1[index:]
    if s1_end in s2:
        while s1_end in s2 and len(s1_end) < len(s1):
            index -= 1
            s1_end = s1[index:]
        return True, s1_end, index
    else:
        return False, '', None