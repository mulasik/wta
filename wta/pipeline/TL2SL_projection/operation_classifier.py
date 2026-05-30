from wta.pipeline.names import OperationTypes, TSLabels, TUTypes
from wta.pipeline.sentence_layer.sentence_histories.spsf import SpsfBuilder
from wta.pipeline.transformation_layer.ts import TransformingSequence


class OperationClassifier:

    def run(self, pre_completion: bool, spsf: SpsfBuilder, ts: TransformingSequence) -> tuple[bool, str]:
        # print(f"Classifying operation for TPSF {spsf.tpsf_id} and sentence at pos {spsf.pos_in_text} with TS label {ts.label} and pre_completion {pre_completion}")
        if pre_completion is True:
                if ts.label == TSLabels.APP:
                        operation = OperationTypes.PROD
                elif ts.label == TSLabels.PAST and ts.endpos < len(spsf.text):
                        operation = OperationTypes.PRECON_INS
                elif ts.label == TSLabels.PAST and ts.endpos == len(spsf.text):
                        operation = OperationTypes.PROD
                elif ts.label in [TSLabels.DEL, TSLabels.MID]:
                        operation = OperationTypes.PRECON_DEL
                elif ts.label == TSLabels.INS:
                        operation = OperationTypes.PRECON_INS
                elif ts.label == TSLabels.REPL:
                        operation = OperationTypes.PRECON_REPL
        elif pre_completion is False:
                if ts.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST]:
                        operation = OperationTypes.CON_INS
                elif ts.label in [TSLabels.DEL, TSLabels.MID]:
                        operation = OperationTypes.CON_DEL
                elif ts.label == TSLabels.REPL:
                        operation = OperationTypes.PRECON_REPL
        # print(f"Classified operation: {operation}")
        if spsf.tu_type == TUTypes.SEN:
            pre_completion = False
        return pre_completion, operation


