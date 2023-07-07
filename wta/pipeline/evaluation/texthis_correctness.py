from pathlib import Path
import re

from wta.pipeline.text_history.tpsf import TpsfECM
from wta.settings import Settings
from wta.utils.nlp import retrieve_mismatch_ranges


def check_texthis_correctness(last_tpsf: TpsfECM, filename: str, settings: Settings) -> bool:
    if settings.config["ksl_source_format"] == "inputlog_idfx":
        txt_file = Path(settings.config["final_txt"], f"{filename.replace('_0', '_ori')}.txt")
    elif settings.config["ksl_source_format"] == "protext_csv":
        txt_file = Path(settings.config["final_txt"], f"{filename}.txt")
    with txt_file.open() as f:
        text = f.read()
    text = re.sub(r"\n+", "\n", text)
    if text.strip() == last_tpsf.text.strip():
        print("INFO: Successfully generated a text history. Last text version is the same as the text produced.")
        return True
    diffs = retrieve_mismatch_ranges(text.strip(), last_tpsf.text.strip())
    print("INFO: Failure when generating text history. Last text version is not the same as the text produced.")
    print(f"\n\nThe final text in text history:\n{last_tpsf.text.strip()}")
    print(f"\n\nThe original text:\n{text.strip()}")
    print("\n\nThe differences:\n")
    for diff in diffs:
        if diff[0] == "insert":
            print("INSERT")
            print(last_tpsf.text.strip()[diff[3]:diff[4]])
        elif diff[0] == "delete":
            print("DELETE")
            print(text.strip()[diff[1]:diff[2]])
        elif diff[0] == "replace":
            print("REPLACE")
            print(text.strip()[diff[1]:diff[2]])
            print("though:")
            print(last_tpsf.text.strip()[diff[1]:diff[2]])
    return False
