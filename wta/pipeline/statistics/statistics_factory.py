from .statistics import (
    BasicStatistics,
    EventStatistics,
    PauseStatistics,
    TSStatistics,
    SentenceStatistics,
)


class StatsFactory:
    @classmethod
    def run(
        cls,
        idfx: str,
        texthis: dict,
        texthis_filtered: dict,
        texthis_pcm: dict,
        senhis: dict,
    ):
        b_stats = BasicStatistics(texthis, texthis_filtered, texthis_pcm)
        e_stats = EventStatistics(idfx)
        p_stats = PauseStatistics(texthis)
        ts_stats = TSStatistics(texthis)
        sen_stats = SentenceStatistics(texthis, senhis)
        return b_stats, e_stats, p_stats, ts_stats, sen_stats
