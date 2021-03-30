import json
from wta.export import export_ecm_tpsf_to_dict, export_sentence_history_to_dict


def output_tpsfs_to_console(tpsfs):
    tpsf_list = []
    for tpsf in tpsfs:
        tpsf_list.append(export_ecm_tpsf_to_dict(tpsf))
    print(json.dumps(tpsf_list, indent=5))


def output_sentence_history_to_console(sen_hist):
    sentence_history = export_sentence_history_to_dict(sen_hist)
    print(json.dumps(sentence_history, indent=5))


def output_revisions_number(tpsf_list: list, mode: str, filtered: bool):
    filtered = 'filtered' if filtered is True else 'all'
    print(f'{mode}: {len(tpsf_list)} text revisions ({filtered}).')



