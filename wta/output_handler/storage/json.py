import json
from pathlib import Path
from typing import Any, Generic, TypeAlias, TypeVar

import paths
import settings
from wta.pipeline.sentence_histories.text_unit import TextUnit, TextUnitDict
from wta.pipeline.transformation_histories.transformation import Transformation

from ...pipeline.text_history.tpsf import TpsfECM, TpsfECMDict
from ..names import Names
from .base import BaseStorage

_AnyDict: TypeAlias = dict[str, Any]  # type: ignore[misc]

_T = TypeVar("_T")


class Json(BaseStorage, Generic[_T]):
    def __init__(self, filepath: Path, data: _T) -> None:
        self.filepath = filepath
        self.data = data

    def to_file(self) -> None:
        with self.filepath.open("w") as f:
            json.dump(self.data, f)


class TexthisJson(Json[list[TpsfECMDict]]):
    def __init__(
        self, data: list[TpsfECM], mode: str = "ecm", filtered: bool = False
    ) -> None:
        self.mode = mode
        filter_label = "" if not filtered else "_filtered"
        json_file = (
            f"{settings.filename}_{Names.TEXTHIS}_{self.mode}{filter_label}.json"
        )
        super().__init__(paths.texthis_json_dir / json_file, self.preprocess_data(data))

    def preprocess_data(self, texthis: list[TpsfECM]) -> list[TpsfECMDict]:
        return [tpsf.to_dict() for tpsf in texthis]


class SenhisJson(Json[dict[int, list[TextUnitDict]]]):
    def __init__(
        self,
        data: dict[int, list[TextUnit]],
        view_mode: str = "normal",
        filtered: bool = False,
    ) -> None:
        self.view_mode = "" if view_mode == "normal" else f"_{view_mode}"
        self.data = self.preprocess_data(data)
        filter_label = "" if not filtered else "_filtered"
        json_file = (
            f"{settings.filename}_{Names.SENHIS}{self.view_mode}{filter_label}.json"
        )
        self.filepath = paths.senhis_json_dir / json_file

    def preprocess_data(
        self, senhis: dict[int, list[TextUnit]]
    ) -> dict[int, list[TextUnitDict]]:
        _senhis = {}
        for id, sens in senhis.items():
            _senhis[id] = [s.to_dict(self.view_mode) for s in sens]
        return _senhis


class TranshisJson(Json[dict[int, list[_AnyDict]]]):
    def __init__(self, data: dict[int, list[Transformation]], grammar: str) -> None:
        self.data = self.preprocess_data(data)
        self.grammar = grammar
        json_file = f"{settings.filename}_{Names.TRANSHIS}_{grammar}.json"
        output_dir = (
            paths.dependency_transhis_dir
            if grammar == "dependency"
            else paths.constituency_transhis_dir
        )
        self.filepath = output_dir / json_file

    def preprocess_data(
        self, transhis: dict[int, list[Transformation]]
    ) -> dict[int, list[_AnyDict]]:
        _transhis = {}
        for sen_id, th in transhis.items():
            _transhis[sen_id] = [t.__dict__ for t in th]
        return _transhis
