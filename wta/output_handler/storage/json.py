import json
import os

import paths
import settings
from wta.output_handler.storage.base import BaseStorage, TranshisStorage, Names


class Json(BaseStorage, TranshisStorage):

    def process_texthis(self, tpsfs: list, mode: str, filtered=False):
        tpsf_list = [tpsf.to_dict() for tpsf in tpsfs]
        filter_label = '' if not filtered else '_filtered'
        json_file = f'{settings.filename}_{Names.TEXTHIS}_{mode}{filter_label}.json'
        json_file_path = os.path.join(paths.texthis_json_dir, json_file)
        with open(json_file_path, 'w') as f:
            json.dump(tpsf_list, f)

    def process_senhis(self, senhis: dict, view_mode='normal', filtered=False):
        view_mode_name = '' if view_mode == 'normal' else f'_{view_mode}'
        filter_label = '' if not filtered else '_filtered'
        json_file = f'{settings.filename}_{Names.SENHIS}{view_mode_name}{filter_label}.json'
        json_file_path = os.path.join(paths.senhis_json_dir, json_file)
        _senhis = {}
        for id, sens in senhis.items():
            _senhis[id] = [s.to_dict(view_mode) for s in sens]
        with open(json_file_path, 'w') as f:
            json.dump(_senhis, f)

    def process_transhis(self, transhis: dict, grammar: str):
        json_file = f'{settings.filename}_{Names.TRANSHIS}_{grammar}.json'
        output_dir = paths.dependency_transhis_dir if grammar == 'dependency' else paths.constituency_transhis_dir
        json_file_path = os.path.join(output_dir, json_file)
        _transhis = {}
        for sen_id, th in transhis.items():
            _transhis[sen_id] = [t.__dict__ for t in th]
        with open(json_file_path, 'w') as f:
            json.dump(_transhis, f)