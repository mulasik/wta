from wta.pipeline.names import ProductionStages, SenSegmentTypes, SenTransformationTypes, TSLabels
from wta.pipeline.sentence_layer.sentence_histories.sentence_transformation import SentenceTransformation
from wta.pipeline.transformation_layer.text_unit import SPSF


class SenTransHistoryGenerator:
    def run(self, senhis: dict[int, list[SPSF]]) -> dict[int, list[SentenceTransformation]]:
        sentrans_history: dict[int, list[SentenceTransformation]] = {}
        for sen_id, sen_vers in senhis.items():
            pre_completion = True
            sentrans_history[sen_id] = []
            for sv in sen_vers:
                if pre_completion is True:
                    if sv.ts.label == TSLabels.APP:
                        operation = SenTransformationTypes.PROD
                    elif sv.ts.label == TSLabels.PAST and sv.ts.endpos < len(sv.text):
                        operation = SenTransformationTypes.PRECON_INS
                    elif sv.ts.label == TSLabels.PAST and sv.ts.endpos == len(sv.text):
                        operation = SenTransformationTypes.PROD
                    elif sv.ts.label == TSLabels.DEL:
                        operation = SenTransformationTypes.PRECON_DEL
                    elif sv.ts.label == TSLabels.INS:
                        operation = SenTransformationTypes.PRECON_INS
                    elif sv.ts.label == TSLabels.REPL:
                        operation = SenTransformationTypes.PRECON_REV
                elif pre_completion is False:
                    if sv.ts.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST]:
                        operation = SenTransformationTypes.CON_INS
                    elif sv.ts.label in [TSLabels.DEL, TSLabels.MID]:
                        operation = SenTransformationTypes.CON_DEL
                    elif sv.ts.label == TSLabels.REPL:
                        operation = SenTransformationTypes.CON_REV
                sen_segment = self.retreive_sen_segment_info(sv)
                sentrans = SentenceTransformation(sv, operation, sen_segment)
                sentrans_history[sen_id].append(sentrans)
                if sv.text_unit_type == 3:
                    pre_completion = False
        return sentrans_history

    def retreive_sen_segment_info(self, sv: SPSF) -> str:
        sen_segment = SenSegmentTypes.UNK
        if sv.ts.startpos == 0 and sv.text_unit_type != 3:
            sen_segment = SenSegmentTypes.SEN_BEG
        elif sv.ts.startpos == 0 and sv.text_unit_type == 3:
            sen_segment = SenSegmentTypes.SEN
        elif sv.text_unit_type == 3:
            production_ts_at_sen_end = sv.ts.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST] and sv.ts.endpos >= len(sv.text)
            deletion_ts_at_sen_end = sv.ts.label in [TSLabels.DEL, TSLabels.MID, TSLabels.REPL] and sv.ts.startpos <= len(sv.text) and sv.ts.endpos >= len(sv.text)
            if production_ts_at_sen_end or deletion_ts_at_sen_end:
                sen_segment = SenSegmentTypes.SEN_END
            elif sv.ts.startpos != 0 and sv.ts.endpos < len(sv.text):
                sen_segment = SenSegmentTypes.SEN_MID
            else:
                print(f"ATTENTION: Cannot identify sentence segment for {sv.text_unit_type} ({len(sv.text)}).\nTS label: {sv.ts.label} ({sv.ts.startpos}-{sv.ts.endpos})")
        elif sv.text_unit_type == 2 and sv.ts.startpos != 0:
            sen_segment = SenSegmentTypes.SEN_MID
        else:
            sen_segment = SenSegmentTypes.UNK
            print(f"ATTENTION: Cannot identify sentence segment for {sv.text_unit_type}:\nTS label{sv.ts.label} ({sv.ts.startpos}-{sv.ts.endpos})")
        return sen_segment


