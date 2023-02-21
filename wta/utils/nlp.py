import difflib
import itertools
import re

import nltk


def segment_sentences_with_nltk(text):
    sent_detector = nltk.data.load("tokenizers/punkt/german.pickle")
    sentences = list(sent_detector.tokenize(text.strip()))
    return sentences


def contains_end_punctuation_in_the_middle(seq):
    return re.search("([\\w\\s,;:\\-]*)([?!.])([\\w\\s,:;\\-]*)", seq) is not None


def retrieve_end_punctuation_from_the_middle(seq):
    end_punctuation = re.search(r"([\w\s,;:\-]+)([?!]+)([\w\s,:;\-]+)", seq)
    if end_punctuation:
        return end_punctuation.group(2)
    else:
        return None


def ends_with_end_punctuation(seq):
    end_punctuation_at_end = re.search(r'([\w\s,;:"\-()]+)[.?!]+(»|\"|\')*$', seq)
    if end_punctuation_at_end:
        return True
    else:
        return False


def is_short_sequence(seq, length):
    return len(seq) < length


def starts_with_uppercase_letter(seq):
    uppercase_at_beginning = re.search(r"^(«|\"|\')*[A-ZÄÖÜ]", seq)
    return uppercase_at_beginning is not None


def starts_with_lowercase_letter(seq):
    lowercase_at_beginning = re.search(r"^[a-zäöü]", seq)
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
        return False, "", None


def check_overlap_with_seq_end(s1: str, s2: str) -> tuple:
    # s1 is modifying seq and s2 is sen
    index = len(s1)
    s1_end = s1[index:]
    if s1_end in s2:
        while s1_end in s2 and len(s1_end) < len(s1):
            index -= 1
            s1_end = s1[index:]
        return True, s1_end, index
    else:
        return False, "", None


def retrieve_token_indices(prev_sen: str, cur_sen: str) -> tuple:
    prev_toks_with_indices = [
        (match.group(0), match.start(), match.end() - 1)
        for match in re.finditer(r"\S+", prev_sen)
    ]
    cur_toks_with_indices = [
        (match.group(0), match.start(), match.end() - 1)
        for match in re.finditer(r"\S+", cur_sen)
    ]
    return prev_toks_with_indices, cur_toks_with_indices


def identify_affected_tokens(
    prev_sen_toks: list, cur_sen_toks: list, edit_type: str
) -> list:
    affected_tokens = []
    if prev_sen_toks and cur_sen_toks:
        for pt, ct in itertools.zip_longest(prev_sen_toks, cur_sen_toks):
            print(ct)
            if pt["text"] != ct["text"]:
                if edit_type == "insertion":
                    affected_tokens.append({"prev": None, "cur": ct})
                elif edit_type == "deletion":
                    affected_tokens.append({"prev": pt, "cur": None})
    elif not prev_sen_toks and cur_sen_toks:
        for ct in cur_sen_toks:
            affected_tokens.append({"prev": None, "cur": ct})
    elif prev_sen_toks and not cur_sen_toks:
        for pt in prev_sen_toks:
            affected_tokens.append({"prev": pt, "cur": None})
    print("AFFECTED TOKENS:")
    print(affected_tokens)
    return affected_tokens


def retrieve_affected_tokens(prev_sen, cur_sen) -> list:
    # affected_tokens is a list of tuples: previous word, current word with their indices
    affected_tokens = []
    prev_toks_with_indices, cur_toks_with_indices = retrieve_token_indices(
        prev_sen, cur_sen
    )
    _, mismatch_range, _ = retrieve_mismatch_range_for_sentence_pair(prev_sen, cur_sen)
    if mismatch_range:
        # as there is only one edit per TPSF (one sequence gets changed), there can always be only one mismatch range
        # if more than one mismatch range exists, merge all consecutive mismatch ranges together
        # multiple mismatch ranges occur if the inserted or deleted sequence is very short
        # and can be found at another position in the sentence which hasn't been edited
        mismatch_range = range(mismatch_range[0][0], mismatch_range[-1][-1] + 1)
        for pt, ct in itertools.zip_longest(
            prev_toks_with_indices, cur_toks_with_indices
        ):
            if pt is not None and ct is not None:
                if (
                    mismatch_range[0] <= pt[2]
                    and pt[1] <= mismatch_range[-1]
                    or mismatch_range[0] <= ct[2]
                    and ct[1] <= mismatch_range[-1]
                ):  # TODO to test
                    affected_token_pair = {"prev_tok": pt, "cur_tok": ct}
                    affected_tokens.append(affected_token_pair)
            elif pt is None:
                pt = ("", None, None)
                if mismatch_range[0] <= ct[2] and ct[1] <= mismatch_range[-1]:
                    affected_token_pair = {"prev_tok": pt, "cur_tok": ct}
                    affected_tokens.append(affected_token_pair)
            elif ct is None:
                ct = ("", None, None)
                if mismatch_range[0] <= pt[2] and pt[1] <= mismatch_range[-1]:
                    affected_token_pair = {"prev_tok": pt, "cur_tok": ct}
                    affected_tokens.append(affected_token_pair)
    else:
        for ct in cur_toks_with_indices:
            pt = ("", None, None)
            affected_token_pair = {"prev_tok": pt, "cur_tok": ct}
            affected_tokens.append(affected_token_pair)
    return affected_tokens


# def filter_out_irrelevant_tokens(tokens: list) -> list:
#     relevant_tokens = []
#     for tok in tokens:
#         if tokens['prev'][1] is not None and tokens['cur'][1] is not None:
#             relevant_tokens.append(tok)
#     return relevant_tokens


def check_edit_distance(tokens: list) -> int:
    prev_tok = "" if tokens["prev"] is None else tokens["prev"]["text"]
    cur_tok = "" if tokens["cur"] is None else tokens["cur"]["text"]
    ed = nltk.edit_distance(prev_tok, cur_tok)
    return ed


def retrieve_mismatch_range_for_sentence_pair(prev_sen: str, cur_sen: str) -> tuple:
    seq_match = difflib.SequenceMatcher(None, prev_sen, cur_sen)
    prev_cur_match = seq_match.get_opcodes()
    mismatch_range = []
    edit = None
    relevant = ""
    # there is always one mismatch range, as TPSF capturing happens upon each edit,
    # two separate edits on the same TPSF are not possible
    # TODO make it more generic
    for m in prev_cur_match:
        if m[0] == "delete":
            edit = m[0]
            mismatch_range.append(range(m[1], m[2] + 1))
            relevant = "prev"
        elif m[0] == "insert":
            edit = m[0]
            mismatch_range.append(range(m[3], m[4] + 1))
            relevant = "cur"
        elif m[0] == "replace":
            edit = m[0]
            mismatch_range.append(range(max(m[1], m[3]), max(m[2] + 1, m[4] + 1)))
            relevant = (
                "prev"
                if mismatch_range[0] == m[1] and mismatch_range[-1] == m[2]
                else "cur"
            )
    return edit, mismatch_range, relevant
