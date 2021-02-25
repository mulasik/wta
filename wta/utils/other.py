import difflib

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