from pathlib import Path

from ..sentence_histories.text_unit import SPSF
from ..text_history.action import Action
from ..text_history.tpsf import TpsfECM, TpsfPCM
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
        texthis: list[TpsfECM],
        texthis_filtered: list[TpsfECM],
        texthis_pcm: list[TpsfPCM],
        actions: list[Action],
        senhis: dict[int, list[SPSF]],
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
