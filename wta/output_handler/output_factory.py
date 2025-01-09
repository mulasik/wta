from pathlib import Path

from wta.output_handler.storage.csv import SenTranshisCsv, SenTranshisSegmentsCsv, TextTranshisCsv
from wta.pipeline.sentence_layer.sentence_histories.sentence_transformation import SentenceTransformation
from wta.pipeline.sentence_layer.sentence_histories.sentencehood_evaluator import Sentencehood
from wta.pipeline.transformation_layer.text_transformation import TextTransformation

from ..pipeline.sentence_layer.sentence_parsing.parsers import TokenProp
from ..pipeline.sentence_layer.sentence_syntactic_transformation_histories.transformation import Transformation
from ..pipeline.statistics.statistics import (
    BasicStatistics,
    EventStatistics,
    PauseStatistics,
    SentenceStatistics,
    TSStatistics,
)
from ..pipeline.transformation_layer.action import Action
from ..pipeline.transformation_layer.events.base import BaseEvent
from ..pipeline.transformation_layer.text_unit import SPSF
from ..pipeline.transformation_layer.tpsf import TpsfECM, TpsfPCM
from ..pipeline.transformation_layer.ts import TransformingSequence
from ..settings import Settings
from .storage.json import SenhisJson, SenhoodJson, TexthisJson, TextTranshisJson, TranshisJson
from .storage.svg import (
    ConstTranshisSvg,
    DeletionsSvg,
    DepTranshisSvg,
    FilteredTexthisSvg,
    InsertionsSvg,
    SenEditSvg,
    SenhisSvg,
    SentranshisInitRevSvg,
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
    SenhoodhisTxt,
    StatsTxt,
    TexthisTxt,
    TextTranshisTxt,
    TpsfsPCMTxt,
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


class TpsfsPCMOutputFactory:
    @classmethod
    def run(cls, tpsfs: list[TpsfPCM], settings: Settings) -> None:
        TpsfsPCMTxt(tpsfs, settings).to_file()


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


class TextTranshisOutputFactory:
    @classmethod
    def run(cls, text_transformation_history: list[TextTransformation], settings: Settings) -> None:
        print("Generating JSON for text transformation history")
        TextTranshisJson(text_transformation_history, settings).to_file()
        TextTranshisTxt(text_transformation_history, settings).to_file()
        TextTranshisCsv(text_transformation_history, settings).to_file()


class SenhisOutputFactory:
    @classmethod
    def run(
        cls,
        texthis: list[TpsfECM],
        texthis_fltr: list[TpsfECM],
        senhis: dict[int, list[SPSF]],
        senhis_fltr: dict[int, list[SPSF]],
        settings: Settings,
    ) -> None:
        SenhisJson(senhis, settings).to_file()
        SenhisJson(senhis_fltr, settings, filtered=True).to_file()
        SenhisTxt(senhis, settings).to_file()
        SenhisTxt(senhis_fltr, settings, filtered=True).to_file()
        SenhisSvg(texthis, senhis, settings).to_file()
        SenhisSvg(texthis_fltr, senhis_fltr, settings, filtered=True).to_file()


class SenTranshisOutputFactory:
    @classmethod
    def run(cls, sentranshis: list[SentenceTransformation], settings: Settings) -> None:
        print("Generating JSON for text transformation history")
        SenTranshisCsv(sentranshis, settings).to_file()
        SenTranshisSegmentsCsv(sentranshis, settings).to_file()
        SentranshisInitRevSvg(sentranshis, settings).to_file()

class SenhoodhisOutputFactory:
    @classmethod
    def run(
        cls,
        senhoodhis: dict[int, list[Sentencehood]],
        settings: Settings,
    ) -> None:
        SenhoodhisTxt(senhoodhis, settings).to_file()
        SenhoodJson(senhoodhis, settings).to_file()


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
        p_stats: PauseStatistics,
        ts_stats: TSStatistics,
        sen_stats: SentenceStatistics,
        idfx: Path,
        texthis: list[TpsfECM],
        senhis: dict[int, list[SPSF]],
        settings: Settings,
    ) -> None:
        StatsTxt(
            b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx, settings
        ).to_file()
        SenEditSvg(texthis, senhis, settings).to_file()
        TsTokensSvg(texthis, senhis, settings).to_file()
        TsLabelsSvg(texthis, senhis, settings).to_file()
        DeletionsSvg(texthis, senhis, settings).to_file()
        InsertionsSvg(texthis, senhis, settings).to_file()
