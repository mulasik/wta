from wta.pipeline.names import SenSegmentTypes, SenTransformationTypes, TSLabels
from wta.pipeline.transformation_layer.text_unit import SPSF, SPSFBuilder


class SenTransformationClassifier:

    def run(self, pre_completion: bool, sen_version: SPSFBuilder) -> tuple[bool, str, str]:
        if pre_completion is True:
                if sen_version.ts.label == TSLabels.APP:
                        operation = SenTransformationTypes.PROD
                elif sen_version.ts.label == TSLabels.PAST and sen_version.ts.endpos < len(sen_version.text):
                        operation = SenTransformationTypes.PRECON_INS
                elif sen_version.ts.label == TSLabels.PAST and sen_version.ts.endpos == len(sen_version.text):
                        operation = SenTransformationTypes.PROD
                elif sen_version.ts.label in [TSLabels.DEL, TSLabels.MID]:
                        operation = SenTransformationTypes.PRECON_DEL
                elif sen_version.ts.label == TSLabels.INS:
                        operation = SenTransformationTypes.PRECON_INS
                elif sen_version.ts.label == TSLabels.REPL:
                        operation = SenTransformationTypes.PRECON_REV
        elif pre_completion is False:
                if sen_version.ts.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST]:
                        operation = SenTransformationTypes.CON_INS
                elif sen_version.ts.label in [TSLabels.DEL, TSLabels.MID]:
                        operation = SenTransformationTypes.CON_DEL
                elif sen_version.ts.label == TSLabels.REPL:
                        operation = SenTransformationTypes.CON_REV
        sen_segment = self._retreive_sen_segment_info(sen_version)
        if sen_version.text_unit_type == 3:
            pre_completion = False
        return pre_completion, operation, sen_segment

    def _retreive_sen_segment_info(self, sv: SPSF) -> str:
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


