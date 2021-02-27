import json
import os


def export_sentences_to_list(sens):
    sentence_list = []
    for s in sens:
        sen = {
            'text': s.text,
            'start_index': s.start_index,
            'end_index': s.end_index,
            'pos_in_text': s.pos_in_text,
            'label': s.label,
            'transforming_sequence': {
                'text': None if s.transforming_sequence is None else s.transforming_sequence.text,
                'label': None if s.transforming_sequence is None else s.transforming_sequence.label,
                'tagged_tokens': None if s.transforming_sequence is None else s.transforming_sequence.tagged_tokens
            },
            'previous_sentence': {
                'text': None if s.previous_sentence is None else s.previous_sentence.text,
            }
        }
        sentence_list.append(sen)
    return sentence_list


def export_pcm_tpsf_to_dict(tpsf):
    tpsf_dict = {
        "preceeding_pause": tpsf.preceeding_pause,
        "result_text": tpsf.result_text,
    }
    return tpsf_dict


def export_ecm_tpsf_to_dict(tpsf):
    previous_sentence_list = export_sentences_to_list(tpsf.previous_sentence_list)
    sentence_list = export_sentences_to_list(tpsf.sentence_list)
    new_sentences = export_sentences_to_list(tpsf.new_sentences)
    modified_sentences = export_sentences_to_list(tpsf.modified_sentences)
    deleted_sentences = export_sentences_to_list(tpsf.deleted_sentences)
    unchanged_sentences = export_sentences_to_list(tpsf.unchanged_sentences)
    delta_current_previous = export_sentences_to_list(tpsf.delta_current_previous)
    delta_previous_current = export_sentences_to_list(tpsf.delta_previous_current)

    tpsf_dict = {
        "revision_id": tpsf.revision_id,
        "event_description": tpsf.event_description,
        "prev_text_version": tpsf.prev_text_version,
        "preceeding_pause": tpsf.preceeding_pause,
        "result_text": tpsf.result_text,
        "edit": {
            "edit_start_position": tpsf.edit_start_position,
            "transforming_sequence": {
                "label": '' if tpsf.transforming_sequence is None else tpsf.transforming_sequence.label,
                "text": '' if tpsf.transforming_sequence is None else tpsf.transforming_sequence.text,
                "tags": '' if tpsf.transforming_sequence is None else tpsf.transforming_sequence.tagged_tokens
            },
        },
        "sentences": {
            "previous_sentence_list": previous_sentence_list,
            "current_sentence_list": sentence_list,
            "delta_current_previous": delta_current_previous,
            "delta_previous_current": delta_previous_current,
            "new_sentences": new_sentences,
            "modified_sentences": modified_sentences,
            "deleted_sentences": deleted_sentences,
            "unchanged_sentences": unchanged_sentences,
        },
        "morphosyn_relevance_evaluation": tpsf.morphosyntactic_relevance_eval_results,
        "morphosyntactic_relevance": tpsf.morphosyntactic_relevance
    }
    return tpsf_dict


def output_tpsfs_to_console(tpsfs):
    tpsf_list = []
    for tpsf in tpsfs:
        tpsf_list.append(export_ecm_tpsf_to_dict(tpsf))
    print(json.dumps(tpsf_list, indent=5))


def export_tpsfs_to_json(tpsfs: list, mode: str, output_path: str, file_name: str, filtered=''):
    if mode == 'Edit Capturing Mode':
        tpsf_list = []
        for tpsf in tpsfs:
            tpsf_list.append(export_ecm_tpsf_to_dict(tpsf))
        json_file = f'{file_name}_output_ecm{filtered}.json'
        json_file_path = os.path.join(output_path, json_file)
    elif mode == 'Pause Capturing Mode':
        tpsf_list = []
        for tpsf in tpsfs:
            tpsf_list.append(export_pcm_tpsf_to_dict(tpsf))
        json_file = f'{file_name}_output_pcm.json'
        json_file_path = os.path.join(output_path, json_file)
    with open(json_file_path, 'w') as f:
        json.dump(tpsf_list, f)


def export_tpsfs_to_txt(tpsfs: list, output_path: str, file_name: str, filtered=''):
    tpsf_list = []
    for tpsf in tpsfs:
        tpsf_list.append(export_ecm_tpsf_to_dict(tpsf))
    txt_file = f'{file_name}_output_ecm{filtered}.txt'
    txt_file_path = os.path.join(output_path, txt_file)
    with open(txt_file_path, 'w') as f:
        for tpsf in tpsf_list:
            result_text = tpsf['result_text']
            id = tpsf['revision_id']
            f.write(f"""
TPSF version {id}:
{result_text}

""")


def export_sentence_history_to_dict(sentence_history):
    sen_hist = {}
    for id, sens in sentence_history.items():
        sentences = export_sentences_to_list(sens)
        sen_hist.update({id: sentences})
    return sen_hist


def output_sentence_history_to_console(sen_hist):
    sentence_history = export_sentence_history_to_dict(sen_hist)
    print(json.dumps(sentence_history, indent=5))


def export_sentence_history_to_json(sen_hist: dict, output_path: str, file_name: str):
    sentence_history = export_sentence_history_to_dict(sen_hist)
    json_file = f'{file_name}_sentence_history.json'
    json_file_path = os.path.join(output_path, json_file)
    with open(json_file_path, 'w') as f:
        json.dump(sentence_history, f)


def export_sentence_history_to_txt(sen_hist: dict, output_path: str, file_name: str, filtered=''):
    sentence_history = export_sentence_history_to_dict(sen_hist)
    txt_file = f'{file_name}_sentence_history{filtered}.txt'
    txt_file_path = os.path.join(output_path, txt_file)
    with open(txt_file_path, 'w') as f:
        for id, sens in sentence_history.items():
            f.write(f'''
******* {id} *******
''')
            for s in sens:
                f.write(f'''
{s['text']}
({s['label']} * position {s['pos_in_text']})
''')


def output_revisions_number(tpsf_list: list, mode: str, filtered: bool):
    filtered = 'filtered' if filtered is True else 'all'
    print(f'{mode}: {len(tpsf_list)} text revisions ({filtered}).')


