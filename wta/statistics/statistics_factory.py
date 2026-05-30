from pathlib import Path

from wta.pipeline.preprocessing.action import Action
from wta.pipeline.sentence_layer.sentence_histories.sentence_history import SentenceHistory
from wta.pipeline.sentence_layer.sentence_histories.spsf import Spsf
from wta.pipeline.transformation_layer.tpsf import Tpsf, TpsfPCM

from .statistics import (
    BasicStatistics,
    EventStatistics,
    PauseStatistics,
    SentenceStatistics,
    TSStatistics,
)


class StatsFactory:
    @staticmethod
    def run(
        idfx: Path,
        texthis: list[Tpsf],
        texthis_filtered: list[Tpsf],
        texthis_pcm: list[TpsfPCM],
        actions: list[Action],
        senhis: list[SentenceHistory],
    ) -> tuple[
        BasicStatistics,
        EventStatistics,
        PauseStatistics,
        TSStatistics,
        SentenceStatistics,
    ]:
        b_stats = BasicStatistics(texthis, texthis_filtered)
        e_stats = EventStatistics(idfx)
        p_stats = PauseStatistics(texthis_pcm, actions)
        ts_stats = TSStatistics(texthis)
        sen_stats = SentenceStatistics(texthis, senhis)
        return b_stats, e_stats, p_stats, ts_stats, sen_stats
