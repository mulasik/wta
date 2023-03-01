from pathlib import Path

import paths
import settings
from wta.pipeline.sentence_histories.text_unit import TextUnit
from wta.pipeline.sentence_parsing.parsers import TokenProp
from wta.pipeline.statistics.statistics import (
    BasicStatistics,
    EventStatistics,
    PauseStatistics,
    SentenceStatistics,
    TSStatistics,
)
from wta.pipeline.text_history.events.base import BaseEvent
from wta.pipeline.transformation_histories.transformation import Transformation

from ..pipeline.text_history.action import Action
from ..pipeline.text_history.tpsf import TpsfECM
from ..pipeline.text_history.ts import TransformingSequence
from ..utils.other import ensure_path
from .names import Names
from .storage.json import SenhisJson, TexthisJson, TranshisJson
from .storage.svg import (
    ConstTranshisSvg,
    DeletionsSvg,
    DepTranshisSvg,
    FilteredTexthisSvg,
    InsertionsSvg,
    SenEditSvg,
    SenhisSvg,
    SynBarTranshisSvg,
    SynPieTranshisSvg,
    TexthisSvg,
    TsLabelsSvg,
    TsTokensSvg,
)
from .storage.txt import (
    ActionGroupsTxt,
    ActionsTxt,
    ConstParsesTxt,
    DepParsesTxt,
    EventsTxt,
    SenhisTxt,
    StatsTxt,
    TexthisTxt,
    TpsfsTxt,
    TssTxt,
)


class StorageSettings:
    @classmethod
    def set_paths(cls) -> None:
        paths.events_dir = (
            settings.config["output_dir"] / Names.PREPROCESSING / Names.EVENTS
        )
        paths.actions_dir = (
            settings.config["output_dir"] / Names.PREPROCESSING / Names.ACTIONS
        )
        paths.tss_dir = settings.config["output_dir"] / Names.PREPROCESSING / Names.TSS
        paths.tpsfs_dir = (
            settings.config["output_dir"] / Names.PREPROCESSING / Names.TPSFS
        )
        paths.texthis_dir = settings.config["output_dir"] / Names.TEXTHIS
        paths.texthis_json_dir = paths.texthis_dir / Names.JSON
        paths.texthis_txt_dir = paths.texthis_dir / Names.TXT
        paths.texthis_visual_dir = paths.texthis_dir / Names.VISUAL
        paths.stats_dir = settings.config["output_dir"] / Names.STATS
        paths.senhis_dir = settings.config["output_dir"] / Names.SENHIS
        paths.senhis_json_dir = paths.senhis_dir / Names.JSON
        paths.senhis_txt_dir = paths.senhis_dir / Names.TXT
        paths.senhis_visual_dir = paths.senhis_dir / Names.VISUAL
        paths.senhis_parses_dir = paths.senhis_dir / Names.SENPAR
        paths.dependency_senhis_parses_dir = paths.senhis_parses_dir / Names.DEP

        paths.constituency_senhis_parses_dir = paths.senhis_parses_dir / Names.CONST

        paths.transhis_dir = settings.config["output_dir"] / Names.TRANSHIS
        paths.dependency_transhis_dir = paths.transhis_dir / Names.DEP
        paths.constituency_transhis_dir = paths.transhis_dir / Names.CONST
        paths_to_ensure = [d for d in dir(paths) if d.endswith("_dir")]
        for p in paths_to_ensure:
            ensure_path(getattr(paths, p))


class EventsOutputFactory:
    @classmethod
    def run(cls, events: list[BaseEvent]) -> None:
        StorageSettings.set_paths()
        EventsTxt(events).to_file()


class ActionsOutputFactory:
    @classmethod
    def run(cls, actions: list[Action]) -> None:
        StorageSettings.set_paths()
        ActionsTxt(actions).to_file()


class ActionGroupsOutputFactory:
    @classmethod
    def run(cls, action_groups: dict[str, list[Action]]) -> None:
        StorageSettings.set_paths()
        ActionGroupsTxt(action_groups).to_file()


class TssOutputFactory:
    @classmethod
    def run(cls, tss: list[TransformingSequence]) -> None:
        StorageSettings.set_paths()
        TssTxt(tss).to_file()


class TpsfsOutputFactory:
    @classmethod
    def run(cls, tpsfs: list[TpsfECM]) -> None:
        StorageSettings.set_paths()
        TpsfsTxt(tpsfs).to_file()


class TexthisOutputFactory:
    @classmethod
    def run(cls, texthis: list[TpsfECM]) -> None:  # + texthis_pcm
        StorageSettings.set_paths()
        TexthisJson(texthis).to_file()
        # TODO: TexthisJson(texthis_pcm, mode='pcm').to_file()
        TexthisTxt(texthis).to_file()
        TexthisSvg(texthis).to_file()


class TexthisFltrOutputFactory:
    @classmethod
    def run(cls, texthis_fltr: list[TpsfECM]) -> None:  # + texthis_pcm
        StorageSettings.set_paths()
        TexthisJson(texthis_fltr, filtered=True).to_file()
        TexthisTxt(texthis_fltr, filtered=True).to_file()
        FilteredTexthisSvg(texthis_fltr).to_file()


class SenhisOutputFactory:
    @classmethod
    def run(
        cls,
        texthis: list[TpsfECM],
        texthis_fltr: list[TpsfECM],
        senhis: dict[int, list[TextUnit]],
        senhis_fltr: dict[int, list[TextUnit]],
    ) -> None:
        StorageSettings.set_paths()
        SenhisJson(senhis).to_file()
        SenhisJson(senhis, "simplified").to_file()
        SenhisJson(senhis_fltr, filtered=True).to_file()
        SenhisJson(senhis_fltr, "simplified", filtered=True).to_file()
        SenhisTxt(senhis).to_file()
        SenhisTxt(senhis_fltr, filtered=True).to_file()
        SenhisTxt(senhis, view_mode="extended").to_file()
        SenhisTxt(senhis, view_mode="extended", filtered=True).to_file()
        SenhisSvg(texthis, senhis).to_file()
        SenhisSvg(texthis_fltr, senhis_fltr, filtered=True).to_file()


class ParseOutputFactory:
    @classmethod
    def run(
        cls,
        dep_senhis_parses: dict[int, list[list[TokenProp]]],
        const_senhis_parses: dict[int, list[list[TokenProp]]],
    ) -> None:
        DepParsesTxt(dep_senhis_parses).to_file()
        ConstParsesTxt(const_senhis_parses).to_file()


class TranshisOutputFactory:
    @classmethod
    def run(
        cls,
        dep_transhis: dict[int, list[Transformation]],
        const_transhis: dict[int, list[Transformation]],
    ) -> None:
        TranshisJson(dep_transhis, "dependency").to_file()
        TranshisJson(const_transhis, "constituency").to_file()
        DepTranshisSvg(dep_transhis).to_file()
        ConstTranshisSvg(const_transhis).to_file()
        SynBarTranshisSvg(dep_transhis, const_transhis).to_file()
        SynPieTranshisSvg(dep_transhis, const_transhis).to_file()


class StatsOutputFactory:
    @classmethod
    def run(
        cls,
        b_stats: BasicStatistics,
        e_stats: EventStatistics,
        p_stats: PauseStatistics,
        ts_stats: TSStatistics,
        sen_stats: SentenceStatistics,
        idfx: Path,
        texthis: list[TpsfECM],
        senhis: dict[int, list[TextUnit]],
    ) -> None:
        StorageSettings.set_paths()
        StatsTxt(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx).to_file()
        SenEditSvg(texthis, senhis).to_file()
        TsTokensSvg(texthis, senhis).to_file()
        TsLabelsSvg(texthis, senhis).to_file()
        DeletionsSvg(texthis, senhis).to_file()
        InsertionsSvg(texthis, senhis).to_file()
