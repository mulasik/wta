from pathlib import Path

from ..sentence_histories.text_unit import TextUnit
from ..text_history.tpsf import TpsfECM
from .statistics import (
    BasicStatistics,
    EventStatistics,
    SentenceStatistics,
    TSStatistics,
)


class StatsFactory:
    @staticmethod
    def run(
        idfx: Path,
        texthis: list[TpsfECM],
        texthis_filtered: list[TpsfECM],
        senhis: dict[int, list[TextUnit]],
    ) -> tuple[
        BasicStatistics,
        EventStatistics,
        # PauseStatistics,
        TSStatistics,
        SentenceStatistics,
    ]:
        b_stats = BasicStatistics(texthis, texthis_filtered)
        e_stats = EventStatistics(idfx)
        # p_stats = PauseStatistics(texthis)
        ts_stats = TSStatistics(texthis)
        sen_stats = SentenceStatistics(texthis, senhis)
        return b_stats, e_stats, ts_stats, sen_stats
