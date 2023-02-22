from ..sentence_histories.text_unit import TextUnit
from ..text_history.tpsf import TpsfECM
from .statistics import (
    BasicStatistics,
    EventStatistics,
    PauseStatistics,
    SentenceStatistics,
    TSStatistics,
)


class StatsFactory:
    @classmethod
    def run(
        cls,
        idfx: str,
        texthis: list[TpsfECM],
        texthis_filtered: list[TpsfECM],
        texthis_pcm: list[TpsfECM],
        senhis: dict[int, list[TextUnit]],
    ) -> tuple[
        BasicStatistics,
        EventStatistics,
        PauseStatistics,
        TSStatistics,
        SentenceStatistics,
    ]:
        b_stats = BasicStatistics(texthis, texthis_filtered, texthis_pcm)
        e_stats = EventStatistics(idfx)
        p_stats = PauseStatistics(texthis)
        ts_stats = TSStatistics(texthis)
        sen_stats = SentenceStatistics(texthis, senhis)
        return b_stats, e_stats, p_stats, ts_stats, sen_stats
