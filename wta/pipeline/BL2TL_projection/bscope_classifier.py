from wta.pipeline.BL2TL_projection.burst import Burst
from wta.pipeline.names import BScope


class BScopeClassifier:

    @staticmethod
    def run(
            pauses: list[float],
            following_pause: float|None,
            bursts: list[Burst]
        ) -> str:

        preceding_pause = pauses[0] if len(pauses) > 0 else None
        if preceding_pause is None or following_pause is None:
            return BScope.UNK
        if len(bursts) == 1 and None not in [preceding_pause, following_pause]:
            if preceding_pause > 2 and following_pause > 2:
                return BScope.UNI_PBURST
            if preceding_pause > 2 or following_pause > 2:
                return BScope.IN_PBURST
        if len(bursts) == 2:
            return BScope.CROSS_PBURST
        if len(bursts) > 2:
            return BScope.MULTI_PBURST
        return BScope.NO_PBURST
