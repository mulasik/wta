from wta.pipeline.names import SenLabels, TextTransScope, TSLabels
from wta.pipeline.transformation_layer.text_transformation import (
    TextDelTransformation,
    TextProdTransformation,
    TextReplTransformation,
    TextTransformation,
)
from wta.pipeline.transformation_layer.text_unit import TextUnit
from wta.pipeline.transformation_layer.tpsf import TpsfECM
from wta.pipeline.transformation_layer.ts import TransformingSequence


class TextTransformationClassifier:

    def run(
            self,
            tpsf_id: int,
            tpsf_text: str,
            ts: TransformingSequence,
            textunits: list[TextUnit],
            deleted_tus: list[TextUnit],
            impacted_tus_from_prev_tpsf: list[TextUnit],
            sequence_removed_by_repl: str | None,
            prev_tpst_text: str
        ) -> TextTransformation:
        print("=====")
        print(f"TS: |{ts.text}| ({ts.label})")
        modified_spsfs = [tu for tu in textunits if tu.state == SenLabels.MOD and tu.text_unit_type in [2, 3]]
        modified_spsfs_prev = [tu for tu in impacted_tus_from_prev_tpsf if tu.text_unit_type in [2, 3] and tu not in modified_spsfs]
        deleted_spsfs = [tu for tu in deleted_tus if tu.text_unit_type in [2, 3]]
        print(f"Modified TUs: {[s.text for s in modified_spsfs]}")
        print(f"Modified TUs prev: {[s.text for s in modified_spsfs_prev]}")
        if ts.label in [TSLabels.DEL, TSLabels.MID]:
            print(f"Deleted spsfs in deletion: {[s.text for s in deleted_spsfs]}")
            impacted_spsfs = [*modified_spsfs, *deleted_spsfs]
            scope = self._calculate_scope(impacted_spsfs, ts)
            return TextDelTransformation(tpsf_id, tpsf_text, scope, modified_spsfs, ts, prev_tpst_text, deleted_spsfs, modified_spsfs_prev)
        if ts.label == TSLabels.REPL:
            print(f"Deleted spsfs in replacement: {[s.text for s in deleted_spsfs]}")
            impacted_spsfs = [*modified_spsfs, *deleted_spsfs]
            scope = self._calculate_scope(impacted_spsfs, ts)
            return TextReplTransformation(tpsf_id, tpsf_text, scope, modified_spsfs, ts, prev_tpst_text, deleted_spsfs, modified_spsfs_prev, sequence_removed_by_repl)
        impacted_spsfs = [tu for tu in textunits if tu.state in [SenLabels.MOD, SenLabels.NEW] and tu.text_unit_type in [2, 3]]
        scope = self._calculate_scope(impacted_spsfs, ts)
        return TextProdTransformation(tpsf_id, tpsf_text, scope, impacted_spsfs, ts, prev_tpst_text)

    def _calculate_scope(self, impacted_spsfs: list[TextUnit], ts: TransformingSequence) -> str:
        if len(impacted_spsfs) == 1:
            return TextTransScope.SEN if impacted_spsfs[0].text == ts.text and impacted_spsfs[0].text_unit_type == 3 else TextTransScope.IN_SEN
        if len(impacted_spsfs) == 2:
            return TextTransScope.CROSS_SEN
        if len(impacted_spsfs) > 2:
            return TextTransScope.MULTI_SEN
        return TextTransScope.NO_SEN
