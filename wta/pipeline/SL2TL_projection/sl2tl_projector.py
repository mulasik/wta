from wta.pipeline.names import TSLabels, TUState
from wta.pipeline.SL2TL_projection.scope_classifier import SScopeClassifier
from wta.pipeline.SL2TL_projection.segment import Segment
from wta.pipeline.SL2TL_projection.textunit import TextunitBuilder
from wta.pipeline.SL2TL_projection.textunit_factory import TextunitFactory
from wta.pipeline.SL2TL_projection.tssegmenter import (
    DelTSSegmenter,
    ReplTSSegmenter,
    TSSegmenter,
)
from wta.pipeline.transformation_layer.tpsf import Tpsf
from wta.pipeline.transformation_layer.ts import TSBuilder
from wta.settings import Settings


class SL2TLProjector:
    """
    The class for projecting Sentence Layer on Transformation Layer.
    """

    def __init__(
            self,
            tpsf_id: int,
            tpsf_text: str,
            tsb: TSBuilder,
            prev_tpsf: Tpsf|None,
            removed_text: str,
            ts_text: str,
            settings: Settings
        ) -> None:

        self.tpsf_id = tpsf_id
        self.tpsf_text = tpsf_text
        self.tsb = tsb
        self.prev_tpsf = prev_tpsf


        # extract current, previous, and deleted text units
        self.tubs_current, prev_tubs, self.deleted_tubs = TextunitFactory().run(tpsf_id, tpsf_text, tsb, prev_tpsf, removed_text, ts_text, settings)

        # calculate scope of TS with regards to sentences
        self.sscope = SScopeClassifier().run(ts_text, tsb.label, self.tubs_current, self.deleted_tubs)

        # retrieve segments of sentences impacted by the transformation
        prev_tpsf_text = prev_tpsf.text if prev_tpsf else ""
        self.tssegments, self.replaced_segments = self._generate_segments(prev_tpsf_text, prev_tubs)

    def _generate_segments(
            self,
            prev_tpsf_text: str,
            prev_tubs: list[TextunitBuilder],
        ) -> tuple[list[Segment], list[Segment]]:
        impacted_tus_prev = [ptu for ptu in prev_tubs if ptu.state not in [TUState.UNC_PRE, TUState.UNC_POST]]
        segments: list[Segment] = []
        replaced_segments: list[Segment] = []
        if self.tsb.label in [TSLabels.DEL, TSLabels.MID]:
            del_segmenter = DelTSSegmenter(self.tpsf_id, self.tpsf_text, self.tsb, self.sscope, self.tubs_current, impacted_tus_prev, prev_tpsf_text)
            segments = del_segmenter.run()
        elif self.tsb.label == TSLabels.REPL:
            repl_segmenter = ReplTSSegmenter(self.tpsf_id, self.tpsf_text, self.tsb, self.sscope, self.tubs_current, impacted_tus_prev, prev_tpsf_text)
            segments = repl_segmenter.run()
            replaced_segments = repl_segmenter.segment_replaced_text()
        else:
            segmenter = TSSegmenter(self.tpsf_id, self.tpsf_text, self.tsb, self.sscope, self.tubs_current, impacted_tus_prev, prev_tpsf_text)
            segments = segmenter.run()
        return segments, replaced_segments
