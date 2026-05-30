from wta.pipeline.sentence_layer.textunits.textunit import Textunit


def check_tu_startendpos_correctness(tus: list[Textunit], tpsf_text: str, scope: str) -> list[bool]:

    res: list[bool] = []
    for tu in tus:
        if tu.text != tpsf_text[tu.startpos:tu.endpos+1]:
            print(f"""
WARNING for one of {scope} textunits:
Apparently the start and end position of the textunit have been extracted incorrectly: {tu.startpos}-{tu.endpos}.
The textunit:
|{tu.text}|
does not correspond to the text extracted from the TPSF text based on the start and endpos:
|{tpsf_text[tu.startpos:tu.endpos+1]}|
            """)
            res.append(False)
        else:
            res.append(True)

    return res


def check_startpos_endpos() -> None:
            print(f"============ TU START- AND ENDPOS EXTRACTION CHECK FOR TPSF {i} ============")
            res_current = check_tu_startendpos_correctness(list(tus_current), tpsf_text, "current")
            res_deleted: list[bool] = []
            res_impacted_prev: list[bool] = []
            if prev_tpsf is not None:
                res_deleted = check_tu_startendpos_correctness(list(deleted_tus), prev_tpsf.text, "deleted")
                res_impacted_prev = check_tu_startendpos_correctness(list(impacted_tus_prev), prev_tpsf.text, "previous impacted")
            all_res = [*res_current, *res_deleted, *res_impacted_prev]
            if False in all_res:
                print(f"ERROR: {all_res.count(False)} from {len(all_res)} textunits have incorrect start or end position!")
            else:
                print(f"STATUS: All {len(all_res)} textunits have correct start or end position.")

