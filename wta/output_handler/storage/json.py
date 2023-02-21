import json
import os

import paths
import settings
from wta.output_handler.names import Names
from .base import BaseStorage


class Json(BaseStorage):
    def preprocess_data(self):
        pass

    def to_file(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f)


class TexthisJson(Json):
    def __init__(self, data, mode="ecm", filtered=False):
        self.data = self.preprocess_data(data)
        self.mode = mode
        filter_label = "" if not filtered else "_filtered"
        json_file = (
            f"{settings.filename}_{Names.TEXTHIS}_{self.mode}{filter_label}.json"
        )
        self.filepath = os.path.join(paths.texthis_json_dir, json_file)

    def preprocess_data(self, texthis):
        return [tpsf.to_dict() for tpsf in texthis]


class SenhisJson(Json):
    def __init__(self, data, view_mode="normal", filtered=False):
        self.view_mode = "" if view_mode == "normal" else f"_{view_mode}"
        self.data = self.preprocess_data(data)
        filter_label = "" if not filtered else "_filtered"
        json_file = (
            f"{settings.filename}_{Names.SENHIS}{self.view_mode}{filter_label}.json"
        )
        self.filepath = os.path.join(paths.senhis_json_dir, json_file)

    def preprocess_data(self, senhis):
        _senhis = {}
        for id, sens in senhis.items():
            _senhis[id] = [s.to_dict(self.view_mode) for s in sens]
        return _senhis


class TranshisJson(Json):
    def __init__(self, data, grammar):
        self.data = self.preprocess_data(data)
        self.grammar = grammar
        json_file = f"{settings.filename}_{Names.TRANSHIS}_{grammar}.json"
        output_dir = (
            paths.dependency_transhis_dir
            if grammar == "dependency"
            else paths.constituency_transhis_dir
        )
        self.filepath = os.path.join(output_dir, json_file)

    def preprocess_data(self, transhis):
        _transhis = {}
        for sen_id, th in transhis.items():
            _transhis[sen_id] = [t.__dict__ for t in th]
        return _transhis
