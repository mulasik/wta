from tqdm import tqdm

from wta.pipeline.names import TSLabels, TUState
from wta.pipeline.sentence_layer.textunits.textunit import Textunit, TextUnitType
from wta.pipeline.transformation_layer.tpsf import Tpsf


def check_sen_states_correctness(
        tpsfs: list[Tpsf]
) -> tuple[list[bool], list[bool], list[bool]]:
    impacted_spsfs_checks: list[bool] = []
    new_spsfs_checks: list[bool] = []
    deleted_spsfs_checks: list[bool] = []
    # sen_segments_checks = []
    print()
    for i, tpsf in enumerate(tqdm(tpsfs, "Checking the quality of SPSFs and sentence TS extraction...")):
        # retrieve SPSFs
        no_sen_segments = len(tpsf.ts.segments)
        current_tus = tpsf.tus
        prev_tus = tpsfs[i-1].tus
        deleted_tus = tpsf.deleted_tus
        no_current_tus = len(current_tus)
        no_prev_tus = len(prev_tus) if i>0 else 0
        no_modified_current_spsfs = len([tu for tu in current_tus if tu.state == TUState.MOD])
        no_new_current_tus = len([tu for tu in current_tus if tu.state == TUState.NEW])
        no_split_current_tus = len([tu for tu in current_tus if tu.state == TUState.SPLIT])
        no_impacted_current_tus = no_modified_current_spsfs + no_new_current_tus + no_split_current_tus
        no_deleted_tus = len(deleted_tus)
        if tpsf.ts.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST, TSLabels.REPL]:
            if no_sen_segments != no_impacted_current_tus:
                print(f"\nERROR in TPSF {tpsf.id}: The number of impacted TUs DOES NOT correspond to the number of segments in TS.")
                print(f"{no_sen_segments} segments versus {no_impacted_current_tus} impacted SPSFs")
                print(f"Scope: {tpsf.transformation_scope}")
                print(f"TS ({tpsf.ts.label}: {tpsf.ts.startpos}-{tpsf.ts.endpos}): |{tpsf.ts.text}|")
                print(f"Segments: {[ss.text for ss in tpsf.ts.segments]}")
                print(f"Impacted TUs: {[(tu.startpos, tu.endpos, tu.state, tu.text) for tu in current_tus if tu.state in [TUState.MOD, TUState.NEW, TUState.SPLIT]]}")
                impacted_spsfs_checks.append(False)
            else:
                impacted_spsfs_checks.append(True)
            if no_prev_tus > 0 and no_split_current_tus > 1 and no_current_tus != no_prev_tus + no_new_current_tus + (no_split_current_tus-1):
                print(f"\nERROR in TPSF {tpsf.id}: The number of identifed new or split TUs is INCORRECT.")
                print(f"SPSFs new: {no_new_current_tus}, split {no_split_current_tus}, prev: {no_prev_tus}, current: {no_current_tus}")
                print(f"Scope: {tpsf.transformation_scope}")
                print(f"TS ({tpsf.ts.label}: {tpsf.ts.startpos}-{tpsf.ts.endpos}): |{tpsf.ts.text}|")
                print(f"Segments: {[ss.text for ss in tpsf.ts.segments]}")
                print(f"Impacted TUs: {[(tu.startpos, tu.endpos, tu.state, tu.text) for tu in current_tus if tu.state in [TUState.MOD, TUState.NEW, TUState.SPLIT]]}")
                new_spsfs_checks.append(False)
            else:
                new_spsfs_checks.append(True)
        if tpsf.ts.label in [TSLabels.DEL, TSLabels.MID]:
            any_merged_spsfs = any(spsf.state == TUState.MER for spsf in current_tus)
            if not any_merged_spsfs and no_deleted_tus != no_prev_tus-no_current_tus:
                print(f"\nERROR in TPSF {tpsf.id}: The number of identified deleted TUs is INCORRECT.")
                print(f"SPSFs deleted: {no_deleted_tus}, prev: {no_prev_tus}, current: {no_current_tus}")
                print(f"Scope: {tpsf.transformation_scope}")
                print(f"TS ({tpsf.ts.label}: {tpsf.ts.startpos}-{tpsf.ts.endpos}): |{tpsf.ts.text}|")
                print(f"Segments: {[ss.text for ss in tpsf.ts.segments]}")
                print(f"Deleted TUs: {[(tu.startpos, tu.endpos, tu.state, tu.text) for tu in prev_tus if tu.state in [TSLabels.DEL, TSLabels.MID]]}")
                print(f"Impacted TUs: {[(tu.startpos, tu.endpos, tu.state, tu.text) for tu in current_tus if tu.state == TUState.MOD]}")
                print(f"Current TUs: {[(tu.state, tu.text) for tu in current_tus]}")
                print(f"Previous TUs: {[(tu.state, tu.text) for tu in prev_tus]}")
                deleted_spsfs_checks.append(False)
            else:
                deleted_spsfs_checks.append(True)
        # for prev, cur in zip(prev_spsfs, current_spsfs):
        #     print(f"Prev: {prev.text}")
        #     print(f"Cur: {cur.text}")
        # print("Checking if sentence segments in TS correspond to impacted and deleted SPSFs...")
    return impacted_spsfs_checks, new_spsfs_checks, deleted_spsfs_checks
