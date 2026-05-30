from wta.pipeline.names import SScope, TSLabels, TUState, TUTypes
from wta.pipeline.SL2TL_projection.textunit import TextunitBuilder


class SScopeClassifier:

    @staticmethod
    def run(
            ts_text: str,
            ts_label: str,
            textunits: list[TextunitBuilder],
            deleted_tus: list[TextunitBuilder],
        ) -> str:
        modified_spsfs = [tu for tu in textunits if tu.state in [TUState.MOD, TUState.MER, TUState.SPLIT] and tu.type in [TUTypes.SEN, TUTypes.SEC]]
        deleted_spsfs = [tu for tu in deleted_tus if tu.type in [TUTypes.SEN, TUTypes.SEC]]
        new_spsfs = [tu for tu in textunits if tu.state == TUState.NEW and tu.type in [TUTypes.SEN, TUTypes.SEC]]
        if ts_label in [TSLabels.DEL, TSLabels.MID]:
            impacted_spsfs = [*modified_spsfs, *deleted_spsfs]
        else:
            impacted_spsfs = [*modified_spsfs, *new_spsfs]

        if len(impacted_spsfs) == 1:
            if impacted_spsfs[0].text.strip() == ts_text.strip():
                if impacted_spsfs[0].type == TUTypes.SEN:
                    return SScope.SEN
                return SScope.SEC
            if impacted_spsfs[0].text.strip() != ts_text.strip():
                return SScope.IN_SEN

        if len(impacted_spsfs) == 2:
            return SScope.CROSS_SEN

        if len(impacted_spsfs) > 2:
            return SScope.MULTI_SEN

        return SScope.NO_SEN
