from wta.pipeline.BL2TL_projection.bscope_classifier import BScopeClassifier
from wta.pipeline.BL2TL_projection.burst_factory import BurstFactory


class BL2TLProjector:
    """
    The class for projecting Burst Layer on Transformation Layer.
    """

    def __init__(
            self,
            text: str,
            pauses: list[float],
            following_pause: float|None,
            tpsf_id: int|None,
            ts_label: str
        ) -> None:

        self.bursts = BurstFactory().run(text, pauses, following_pause, tpsf_id, ts_label)
        self.bscope = BScopeClassifier().run(pauses, following_pause, self.bursts)
