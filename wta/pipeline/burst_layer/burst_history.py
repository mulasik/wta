from typing import TypedDict

from wta.pipeline.BL2TL_projection.burst import Burst


class BurstHistoryDict(TypedDict):
    bursts: list[Burst]


class BurstHistory:

    def __init__(self, bursts: list[Burst]) -> None:
        self.bursts: list[Burst] = bursts
