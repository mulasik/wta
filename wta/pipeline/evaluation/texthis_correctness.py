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
    print(f"\nThe final text in text history:\n{last_tpsf.text.strip()}")
    print(f"\nThe original text:\n{text.strip()}")
    print("\nATTENTION: The differences between the original and the retrieved text:\n")
    empty_diffs = []
    for diff in diffs:
        if diff[0] == "insert":
            print("INSERTED TEXT:")
            inserted_text = last_tpsf.text.strip()[diff[3]:diff[4]]
            print(f"|{inserted_text}|")
            if re.search(r"^\s+$", inserted_text):
                empty_diffs.append(True)
            else:
                empty_diffs.append(False)
        elif diff[0] == "delete":
            print("DELETED TEXT:")
            deleted_text = text.strip()[diff[1]:diff[2]]
            print(f"|{deleted_text}|")
            if re.search(r"^\s+$", deleted_text):
                empty_diffs.append(True)
            else:
                empty_diffs.append(False)
        elif diff[0] == "replace":
            print("REPLACED TEXT:")
            replaced_text = text.strip()[diff[1]:diff[2]]
            print(f"|{replaced_text}|")
            if re.search(r"^\s+$", replaced_text):
                empty_diffs.append(True)
            else:
                empty_diffs.append(False)
            print("REPLACED THROUGH:")
            replacing_text = last_tpsf.text.strip()[diff[1]:diff[2]]
            print(f"|{replacing_text}|")
            if re.search(r"^\s+$", replacing_text):
                empty_diffs.append(True)
            else:
                empty_diffs.append(False)
    if False not in empty_diffs:
        print("INFO: Successfully generated a text history. The difference to original contains only whitespaces.")
        return True
    return False
