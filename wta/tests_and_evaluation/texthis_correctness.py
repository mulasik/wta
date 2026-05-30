import re
from pathlib import Path

from wta.pipeline.transformation_layer.tpsf import Tpsf
from wta.settings import Settings
from wta.utils.nlp import retrieve_mismatch_ranges


def check_texthis_correctness(
    last_tpsf: Tpsf, filename: str, settings: Settings
) -> bool:
    if settings.config["ksl_source_format"] in ["inputlog_idfx", "scriptlog_idfx"]:
        txt_file = Path(
            settings.config["final_txt"],
            f"{filename.replace('_0', '_ori').replace('il', 'ft')}.txt",
        )
    elif settings.config["ksl_source_format"] == "protext_csv":
        txt_file = Path(settings.config["final_txt"], f"{filename}.txt")
    with txt_file.open() as f:
        text = f.read()
    text = re.sub(r"\n+", "\n", text)
    if text.strip() == last_tpsf.text.strip():
        print(
            f"INFO: Successfully generated a text history for {filename}. Last text version is the same as the text produced."
        )
        return True
    diffs = retrieve_mismatch_ranges(text.strip(), last_tpsf.text.strip())
    print(
        f"WARNING: Potential failure when generating text history for {filename}: last text version is not the same as the text produced. Checking the differences..."
    )
    print(f"\nThe final text in text history:\n{last_tpsf.text.strip()}")
    print(f"\nThe original text:\n{text.strip()}")
    print("\nThe differences between the original and the retrieved text:\n")
    empty_diffs = []
    for diff in diffs:
        if diff[0] == "insert":
            print(f"INSERTED TEXT {diff[3]}:")
            inserted_text = last_tpsf.text.strip()[diff[3] : diff[4]]
            print(f"|{inserted_text}|")
            if re.search(r"^\s+$", inserted_text):
                empty_diffs.append(True)
            else:
                empty_diffs.append(False)
        elif diff[0] == "delete":
            print(f"DELETED TEXT {diff[1]}:")
            deleted_text = text.strip()[diff[1] : diff[2]]
            print(f"|{deleted_text}|")
            if re.search(r"^\s+$", deleted_text):
                empty_diffs.append(True)
            else:
                empty_diffs.append(False)
        elif diff[0] == "replace":
            print(f"REPLACED TEXT {diff[1]}:")
            replaced_text = text.strip()[diff[1] : diff[2]]
            print(f"|{replaced_text}|")
            if re.search(r"^\s+$", replaced_text):
                empty_diffs.append(True)
            else:
                empty_diffs.append(False)
            print("REPLACED THROUGH:")
            replacing_text = last_tpsf.text.strip()[diff[1] : diff[2]]
            print(f"|{replacing_text}|")
            if re.search(r"^\s+$", replacing_text):
                empty_diffs.append(True)
            else:
                empty_diffs.append(False)
    if False not in empty_diffs:
        print(
            f"SUCCESS: Successfully generated a text history for {filename}. The difference to original contains only whitespaces."
        )
        return True
    print(
        f"FAILURE: Text history for {filename} was generated incorrectly. There are differences between the original text and the final text version in the text history."
    )
    return False
