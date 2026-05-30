
from wta.pipeline.names import TUState
from wta.pipeline.transformation_layer.tpsf import Tpsf


def check_ts_length(tpsfs: list[Tpsf]) -> list[bool]:
    """
    Check if the length of the text in the transformation sequence matches the length of the TPSF text.
    """
    res = []
    for tpsf in tpsfs:
        for tu in tpsf.tus:
            if tu.state == TUState.NEW and tu.sen_ts and len(tu.sen_ts.text) != len(tu.text):
                print(f"WARNING for {tu.tpsf_id}: The length of the TS does not correspond the length of the new SPSF!")
                res.append(False)
            else:
                res.append(True)
            if tu.state == TUState.MOD and tu.sen_ts and len(tu.sen_ts.text) > len(tu.text):
                print(f"WARNING for {tu.tpsf_id}: The TS is longer than the modified SPSF!")
                res.append(False)
            else:
                res.append(True)
    return res


def check_sen_ts_correctness(tpsfs: list[Tpsf]) -> list[bool]:
    """
    Check if the sentence transformation sequences are contained in the TPSF tranforming sequence.
    """
    res = []
    for tpsf in tpsfs:
        for tu in tpsf.tus:
            if tu.sen_ts is not None:
                if tu.sen_ts.text.find(tpsf.ts.text) == -1:
                    print(f"WARNING for {tu.tpsf_id}: Could not find SPFS TS in the TPSF TS!")
                    res.append(False)
                else:
                    res.append(True)
            else:
                print(f"({tpsf.id}) WARNING: spsf.ts is None!")
    return res
