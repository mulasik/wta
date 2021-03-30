from wta.models import SpacyModel
import config
import nltk
import re
import difflib
import itertools

model = SpacyModel(config.VIDEO['language'])


def tag_words(text: str) -> list:
    doc = model.nlp(text)
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
    doc = model.nlp(text)
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
        return False, '', None


def retrieve_token_indices(prev_sen: str, cur_sen: str) -> tuple:
    prev_toks_with_indices = [(match.group(0), match.start(), match.end()-1) for match in re.finditer(r'\S+', prev_sen)]
    cur_toks_with_indices = [(match.group(0), match.start(), match.end()-1) for match in re.finditer(r'\S+', cur_sen)]
    return prev_toks_with_indices, cur_toks_with_indices


def retrieve_affected_tokens(sentence: dict) -> list:
    affected_tokens = []
    cur_sen = sentence.text
    prev_sen = '' if sentence.previous_sentence is None else sentence.previous_sentence.text
    prev_toks_with_indices, cur_toks_with_indices = retrieve_token_indices(prev_sen, cur_sen)
    _, mismatch_range, _ = retrieve_mismatch_range_for_sentence_pair(prev_sen, cur_sen)
    if mismatch_range:
        # as there is only one edit per TPSF (one sequence gets changed), there can always be only one mismatch range
        # if more than one mismatch range exists, merge all consequtive mismatch ranges together
        # multiple mismatch ranges occur if the inserted or deleted sequence is very short
        # and can be found at another position in the sentence which hasn't been edited
        mismatch_range = range(mismatch_range[0][0], mismatch_range[-1][-1]+1)
        for (pt, ct) in itertools.zip_longest(prev_toks_with_indices, cur_toks_with_indices):
            if pt is not None and ct is not None:
                if mismatch_range[0] <= pt[2] and pt[1] <= mismatch_range[-1] or mismatch_range[0] <= ct[2] and ct[1] <= mismatch_range[-1]:  # TODO to test
                    affected_token_pair = {
                        'prev_tok': pt,
                        'cur_tok': ct
                    }
                    affected_tokens.append(affected_token_pair)
            elif pt is None:
                pt = ('', None, None)
                if mismatch_range[0] <= ct[2] and ct[1] <= mismatch_range[-1]:
                    affected_token_pair = {
                        'prev_tok': pt,
                        'cur_tok': ct
                    }
                    affected_tokens.append(affected_token_pair)
            elif ct is None:
                ct = ('', None, None)
                if mismatch_range[0] <= pt[2] and pt[1] <= mismatch_range[-1]:
                    affected_token_pair = {
                        'prev_tok': pt,
                        'cur_tok': ct
                    }
                    affected_tokens.append(affected_token_pair)
    else:
        for ct in cur_toks_with_indices:
            pt = ('', None, None)
            affected_token_pair = {
                'prev_tok': pt,
                'cur_tok': ct
            }
            affected_tokens.append(affected_token_pair)
    return affected_tokens


def filter_out_irrelevant_tokens(tokens: list) -> list:
    relevant_tokens = []
    for tok in tokens:
        if tokens['prev_tok'][1] is not None and tokens['cur_tok'][1] is not None:
            relevant_tokens.append(tok)
    return relevant_tokens


def check_edit_distance(tokens: list) -> int:
    ed = nltk.edit_distance(tokens['prev_tok'][0], tokens['cur_tok'][0])
    return ed


def check_if_any_oov(tokens: list) -> bool:
    for t in tokens:
        pt = t['prev_tok']
        ct = t['cur_tok']
        if pt[0] != '':
            pt = pt[0]
            pt = model.nlp(pt)
            pt = pt[0]
            pt_oov = pt.is_oov
        else:
            pt_oov = None
        if ct[0] != '':
            ct = ct[0]
            ct = model.nlp(ct)
            ct = ct[0]
            ct_oov = ct.is_oov
        else:
            ct_oov = None
        if pt_oov is True or ct_oov is True:
            return True
    return False


def collect_additional_tokens_tags(text: str) -> tuple:
    doc = model.nlp(text)
    for token in doc:
        return token.text, token.shape_, token.is_alpha, token.is_stop, token.has_vector, token.vector_norm


def check_if_same_words(editted_word: str, result_word: str) -> bool:
    if editted_word and result_word:
        editted_word = model.nlp(editted_word)
        result_word = model.nlp(result_word)
        if editted_word.pos_ != result_word.pos_ or editted_word.lemma_ != result_word.lemma_ or editted_word.dep_ != result_word.dep_:
            return False
        else:
            return True


def retrieve_mismatch_range_for_sentence_pair(prev_sen: str, cur_sen: str) -> tuple:
    seq_match = difflib.SequenceMatcher(None, prev_sen, cur_sen)
    prev_cur_match = seq_match.get_opcodes()
    mismatch_range = []
    edit = None
    relevant = ''
    # there is always one mismatch range, as TPSF capturing happens upon each edit,
    # two separate edits on the same TPSF are not possible
    # TODO make it more generic
    for m in prev_cur_match:
        if m[0] == 'delete':
            edit = m[0]
            mismatch_range.append(range(m[1], m[2 ] +1))
            relevant = 'prev'
        elif m[0] == 'insert':
            edit = m[0]
            mismatch_range.append(range(m[3], m[4 ] +1))
            relevant = 'cur'
        elif m[0] == 'replace':
            edit = m[0]
            mismatch_range.append(range(max(m[1], m[3]), max(m[2 ] +1, m[4 ] +1)))
            if mismatch_range[0] == m[1] and mismatch_range[-1] == m[2]:
                relevant = 'prev'
            else:
                relevant = 'cur'
    return edit, mismatch_range, relevant


def analyse_affected_tokens(affected_tokens: list, predef_edit_distance: int):
    is_any_tok_oov = check_if_any_oov(affected_tokens)
    if is_any_tok_oov is True:
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
            # if more than 1 token is affected and none of them is OOV, the TPSF is relevant
            morphosyntactic_relevance = True
            edit_distance = None
    return edit_distance, is_any_tok_oov, morphosyntactic_relevance

