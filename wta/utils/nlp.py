import difflib
import re
from typing import Literal, TypedDict

import nltk


def segment_sentences_with_nltk(text: str) -> list[str]:
    sent_detector = nltk.data.load("tokenizers/punkt/german.pickle")
    return list(sent_detector.tokenize(text.strip()))


_PUNCTUATION_IN_MIDDLE_RE = re.compile("([\\w\\s,;:\\-]*)([?!.])([\\w\\s,:;\\-]*)")
_END_PUNCTIONATION_FROM_MIDDLE_RE = re.compile(r"([\w\s,;:\-]+)([?!]+)([\w\s,:;\-]+)")
_END_PUNCTIONATION_RE = re.compile(r'([\w\s,;:"\-()]+)[.?!]+(»|\"|\')*$')
_UPPERCASE_START_RE = re.compile(r"^(«|\"|\')*[A-ZÄÖÜ]")
_LOWERCASE_START_RE = re.compile(r"^[a-zäöü]")
_NON_WHITESPACE_RE = re.compile(r"\S+")


def contains_end_punctuation_in_the_middle(seq: str) -> bool:
    return _PUNCTUATION_IN_MIDDLE_RE.search(seq) is not None


def retrieve_end_punctuation_from_the_middle(seq: str) -> str | None:
    end_punctuation = _END_PUNCTIONATION_FROM_MIDDLE_RE.search(seq)
    if end_punctuation:
        return end_punctuation.group(2)
    return None


def ends_with_end_punctuation(seq: str) -> bool:
    return _END_PUNCTIONATION_RE.search(seq) is not None


def is_short_sequence(seq: str, length: int) -> bool:
    return len(seq) < length


def starts_with_uppercase_letter(seq: str) -> bool:
    uppercase_at_beginning = _UPPERCASE_START_RE.search(seq)
    return uppercase_at_beginning is not None


def starts_with_lowercase_letter(seq: str) -> bool:
    lowercase_at_beginning = _LOWERCASE_START_RE.search(seq)
    return lowercase_at_beginning is not None


def calculate_sequence_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def retrieve_match_range(seq1: str, seq2: str) -> list[difflib.Match]:
    seq_match = difflib.SequenceMatcher(None, seq1.strip(), seq2.strip())
    return seq_match.get_matching_blocks()


def retrieve_mismatch_ranges(
    seq1: str, seq2: str
) -> list[tuple[str, int, int, int, int]]:
    seq_match = difflib.SequenceMatcher(None, seq1, seq2)
    return seq_match.get_opcodes()


def check_overlap_with_seq_beginning(
    s1: str, s2: str
) -> tuple[Literal[True], str, int] | tuple[Literal[False], str, None]:
    # s1 is modifying seq and s2 is sen
    index = 1
    s1_beginning = s1[:index]
    if s1_beginning not in s2:
        return False, "", None

    while s1_beginning in s2 and len(s1_beginning) < len(s1):
        index += 1
        s1_beginning = s1[:index]
    return True, s1_beginning, index


def check_overlap_with_seq_end(
    s1: str, s2: str
) -> tuple[Literal[True], str, int] | tuple[Literal[False], str, None]:
    # s1 is modifying seq and s2 is sen
    index = len(s1)
    s1_end = s1[index:]
    if s1_end not in s2:
        return False, "", None

    while s1_end in s2 and len(s1_end) < len(s1):
        index -= 1
        s1_end = s1[index:]
    return True, s1_end, index


def retrieve_token_indices(
    prev_sen: str, cur_sen: str
) -> tuple[list[tuple[str, int, int]], list[tuple[str, int, int]]]:
    prev_toks_with_indices = [
        (match.group(0), match.start(), match.end() - 1)
        for match in _NON_WHITESPACE_RE.finditer(prev_sen)
    ]
    cur_toks_with_indices = [
        (match.group(0), match.start(), match.end() - 1)
        for match in _NON_WHITESPACE_RE.finditer(cur_sen)
    ]
    return prev_toks_with_indices, cur_toks_with_indices


# def identify_affected_tokens(
#     prev_sen_toks: list, cur_sen_toks: list, edit_type: str
# ) -> list:
#     affected_tokens = []
#     if prev_sen_toks and cur_sen_toks:
#         for pt, ct in itertools.zip_longest(prev_sen_toks, cur_sen_toks):
#             print(ct)
#             if pt["text"] != ct["text"]:
#                 if edit_type == "insertion":
#                     affected_tokens.append({"prev": None, "cur": ct})
#                 elif edit_type == "deletion":
#                     affected_tokens.append({"prev": pt, "cur": None})
#     elif not prev_sen_toks and cur_sen_toks:
#         for ct in cur_sen_toks:
#             affected_tokens.append({"prev": None, "cur": ct})
#     elif prev_sen_toks and not cur_sen_toks:
#         for pt in prev_sen_toks:
#             affected_tokens.append({"prev": pt, "cur": None})
#     print("AFFECTED TOKENS:")
#     print(affected_tokens)
#     return affected_tokens


# def retrieve_affected_tokens(prev_sen, cur_sen) -> list:
#     # affected_tokens is a list of tuples: previous word, current word with their indices
#     affected_tokens = []
#     prev_toks_with_indices, cur_toks_with_indices = retrieve_token_indices(
#         prev_sen, cur_sen
#     )
#     _, mismatch_range, _ = retrieve_mismatch_range_for_sentence_pair(prev_sen, cur_sen)
#     if mismatch_range:
#         # as there is only one edit per TPSF (one sequence gets changed), there can always be only one mismatch range
#         # if more than one mismatch range exists, merge all consecutive mismatch ranges together
#         # multiple mismatch ranges occur if the inserted or deleted sequence is very short
#         # and can be found at another position in the sentence which hasn't been edited
#         mismatch_range = range(mismatch_range[0][0], mismatch_range[-1][-1] + 1)
#         for pt, ct in itertools.zip_longest(
#             prev_toks_with_indices, cur_toks_with_indices
#         ):
#             if pt is not None and ct is not None:
#                 if (
#                     mismatch_range[0] <= pt[2]
#                     and pt[1] <= mismatch_range[-1]
#                     or mismatch_range[0] <= ct[2]
#                     and ct[1] <= mismatch_range[-1]
#                 ):  # TODO to test
#                     affected_token_pair = {"prev_tok": pt, "cur_tok": ct}
#                     affected_tokens.append(affected_token_pair)
#             elif pt is None:
#                 pt = ("", None, None)
#                 if mismatch_range[0] <= ct[2] and ct[1] <= mismatch_range[-1]:
#                     affected_token_pair = {"prev_tok": pt, "cur_tok": ct}
#                     affected_tokens.append(affected_token_pair)
#             elif ct is None:
#                 ct = ("", None, None)
#                 if mismatch_range[0] <= pt[2] and pt[1] <= mismatch_range[-1]:
#                     affected_token_pair = {"prev_tok": pt, "cur_tok": ct}
#                     affected_tokens.append(affected_token_pair)
#     else:
#         for ct in cur_toks_with_indices:
#             pt = ("", None, None)
#             affected_token_pair = {"prev_tok": pt, "cur_tok": ct}
#             affected_tokens.append(affected_token_pair)
#     return affected_tokens


# def filter_out_irrelevant_tokens(tokens: list) -> list:
#     relevant_tokens = []
#     for tok in tokens:
#         if tokens['prev'][1] is not None and tokens['cur'][1] is not None:
#             relevant_tokens.append(tok)
#     return relevant_tokens


class TokenDict(TypedDict):
    text: str


class TokensDict(TypedDict):
    prev: TokenDict | None
    cur: TokenDict | None


def check_edit_distance(tokens: TokensDict) -> int:
    prev_tok = "" if tokens["prev"] is None else tokens["prev"]["text"]
    cur_tok = "" if tokens["cur"] is None else tokens["cur"]["text"]
    return nltk.edit_distance(prev_tok, cur_tok)


def retrieve_mismatch_range_for_sentence_pair(
    prev_sen: str, cur_sen: str
) -> tuple[str | None, list[range], str]:
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
                if m[1] in mismatch_range[0] and m[2] in mismatch_range[-1]
                else "cur"
            )
    return edit, mismatch_range, relevant
