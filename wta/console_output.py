import json
from wta.storage import BaseStorage


def output_tpsfs_to_console(tpsfs):
    """

    :param tpsfs:
    :return:
    """
    tpsf_list = []
    for tpsf in tpsfs:
        tpsf_list.append(BaseStorage.tpsf_to_dict(tpsf))
    print(json.dumps(tpsf_list, indent=5))


def output_sentence_history_to_console(sen_hist):
    sentence_history = BaseStorage.sentence_histories_to_dict(sen_hist)
    print(json.dumps(sentence_history, indent=5))


def output_revisions_number(tpsf_list: list, mode: str, filtered: bool):
    filtered = 'filtered' if filtered is True else 'all'
    print(f'{mode}: {len(tpsf_list)} text revisions ({filtered}).')



