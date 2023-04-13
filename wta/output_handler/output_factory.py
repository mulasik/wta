from pathlib import Path

from ..pipeline.sentence_histories.text_unit import TextUnit
from ..pipeline.sentence_parsing.parsers import TokenProp
from ..pipeline.statistics.statistics import (
    BasicStatistics,
    EventStatistics,
    SentenceStatistics,
    TSStatistics,
)
from ..pipeline.text_history.action import Action
from ..pipeline.text_history.events.base import BaseEvent
from ..pipeline.text_history.tpsf import TpsfECM
from ..pipeline.text_history.ts import TransformingSequence
from ..pipeline.transformation_histories.transformation import Transformation
from ..settings import Settings
from .storage.json import SenhisJson, TexthisJson, TranshisJson
from .storage.svg import (
    ConstTranshisSvg,
    DeletionsSvg,
    DepTranshisSvg,
    FilteredTexthisSvg,
    InsertionsSvg,
    SenEditSvg,
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


class EventsOutputFactory:
    @classmethod
    def run(cls, events: list[BaseEvent], settings: Settings) -> None:
        EventsTxt(events, settings).to_file()


class ActionsOutputFactory:
    @classmethod
    def run(cls, actions: list[Action], settings: Settings) -> None:
        ActionsTxt(actions, settings).to_file()


class ActionGroupsOutputFactory:
    @classmethod
    def run(cls, action_groups: dict[str, list[Action]], settings: Settings) -> None:
        ActionGroupsTxt(action_groups, settings).to_file()


class TssOutputFactory:
    @classmethod
    def run(cls, tss: list[TransformingSequence], settings: Settings) -> None:
        TssTxt(tss, settings).to_file()


class TpsfsOutputFactory:
    @classmethod
    def run(cls, tpsfs: list[TpsfECM], settings: Settings) -> None:
        TpsfsTxt(tpsfs, settings).to_file()


class TexthisOutputFactory:
    @classmethod
    def run(cls, texthis: list[TpsfECM], settings: Settings) -> None:  # + texthis_pcm
        TexthisJson(texthis, settings).to_file()
        # TODO: TexthisJson(texthis_pcm, settings, mode='pcm').to_file()
        TexthisTxt(texthis, settings).to_file()
        TexthisSvg(texthis, settings).to_file()


class TexthisFltrOutputFactory:
    @classmethod
    def run(
        cls, texthis_fltr: list[TpsfECM], settings: Settings
    ) -> None:  # + texthis_pcm
        TexthisJson(texthis_fltr, settings, filtered=True).to_file()
        TexthisTxt(texthis_fltr, settings, filtered=True).to_file()
        FilteredTexthisSvg(texthis_fltr, settings).to_file()


class SenhisOutputFactory:
    @classmethod
    def run(
        cls,
        # texthis: list[TpsfECM],
        # texthis_fltr: list[TpsfECM],
        senhis: dict[int, list[TextUnit]],
        senhis_fltr: dict[int, list[TextUnit]],
        settings: Settings,
    ) -> None:
        SenhisJson(senhis, settings).to_file()
        # SenhisJson(senhis, settings, "simplified").to_file()
        SenhisJson(senhis_fltr, settings, filtered=True).to_file()
        # SenhisJson(senhis_fltr, settings, "simplified", filtered=True).to_file()
        SenhisTxt(senhis, settings).to_file()
        SenhisTxt(senhis_fltr, settings, filtered=True).to_file()
        # SenhisTxt(senhis, settings, view_mode="extended").to_file()
        # SenhisTxt(senhis, settings, view_mode="extended", filtered=True).to_file()
        # SenhisSvg(texthis, senhis, settings).to_file()
        # SenhisSvg(texthis_fltr, senhis_fltr, settings, filtered=True).to_file()


class ParseOutputFactory:
    @classmethod
    def run(
        cls,
        dep_senhis_parses: dict[int, list[list[TokenProp]]],
        const_senhis_parses: dict[int, list[list[TokenProp]]],
        settings: Settings,
    ) -> None:
        DepParsesTxt(dep_senhis_parses, settings).to_file()
        ConstParsesTxt(const_senhis_parses, settings).to_file()


class TranshisOutputFactory:
    @classmethod
    def run(
        cls,
        dep_transhis: dict[int, list[Transformation]],
        const_transhis: dict[int, list[Transformation]],
        settings: Settings,
    ) -> None:
        TranshisJson(dep_transhis, settings, "dependency").to_file()
        TranshisJson(const_transhis, settings, "constituency").to_file()
        DepTranshisSvg(dep_transhis, settings).to_file()
        ConstTranshisSvg(const_transhis, settings).to_file()
        SynBarTranshisSvg(dep_transhis, const_transhis, settings).to_file()
        SynPieTranshisSvg(dep_transhis, const_transhis, settings).to_file()


class StatsOutputFactory:
    @classmethod
    def run(
        cls,
        b_stats: BasicStatistics,
        e_stats: EventStatistics,
        # p_stats: PauseStatistics,
        ts_stats: TSStatistics,
        sen_stats: SentenceStatistics,
        idfx: Path,
        texthis: list[TpsfECM],
        senhis: dict[int, list[TextUnit]],
        settings: Settings,
    ) -> None:
        StatsTxt(b_stats, e_stats, ts_stats, sen_stats, idfx, settings).to_file()
        SenEditSvg(texthis, senhis, settings).to_file()
        TsTokensSvg(texthis, senhis, settings).to_file()
        TsLabelsSvg(texthis, senhis, settings).to_file()
        DeletionsSvg(texthis, senhis, settings).to_file()
        InsertionsSvg(texthis, senhis, settings).to_file()
