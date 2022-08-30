import os

DATA_DIR = "example_data"
VIDEO_DATA_DIR = os.path.join(DATA_DIR, "video")


DEFAULT_PAUSE_DURATION = 2
DEFAULT_MIN_EDIT_DISTANCE = 3
DEFAULT_TS_MIN_TOKENS_NUMBER = 2
EDIT_DIST_COMBINED_WITH_TOK_NUMBER_DEFAULT = False
SPELLCHECKING_ENABLED_DEFAULT = False
PUNCTUATION_INCLUDED_DEFAULT = False
DEFAULT_LANGUAGE = "German"

VIDEO = {
    "xml": [
        os.path.join(VIDEO_DATA_DIR, f)
        for f in os.listdir(VIDEO_DATA_DIR)
        if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith("idfx") and f.startswith("N")
    ],
    "output": os.path.join("output_data", "video", "conf0"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "combine_edit_distance_with_tok_number": EDIT_DIST_COMBINED_WITH_TOK_NUMBER_DEFAULT,
    "enable_spellchecking": SPELLCHECKING_ENABLED_DEFAULT,
    "include_punctuation_edits": PUNCTUATION_INCLUDED_DEFAULT,
    "language": DEFAULT_LANGUAGE,
}

VIDEO_CONF1 = {
    "xml": [
        os.path.join(VIDEO_DATA_DIR, f)
        for f in os.listdir(VIDEO_DATA_DIR)
        if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "video"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "combine_edit_distance_with_tok_number": EDIT_DIST_COMBINED_WITH_TOK_NUMBER_DEFAULT,
    "enable_spellchecking": SPELLCHECKING_ENABLED_DEFAULT,
    "include_punctuation_edits": True,
    "language": DEFAULT_LANGUAGE,
}

VIDEO_CONF2 = {
    "xml": [
        os.path.join(VIDEO_DATA_DIR, f)
        for f in os.listdir(VIDEO_DATA_DIR)
        if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "video"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "edit_dist_combined_with_tok_number": True,
    "spellchecking": SPELLCHECKING_ENABLED_DEFAULT,
    "punctuation": PUNCTUATION_INCLUDED_DEFAULT,
    "language": DEFAULT_LANGUAGE,
}

VIDEO_CONF3 = {
    "xml": [
        os.path.join(VIDEO_DATA_DIR, f)
        for f in os.listdir(VIDEO_DATA_DIR)
        if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith("idfx") and f.startswith("R")
    ],
    "output": os.path.join("output_data", "video"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "edit_dist_combined_with_tok_number": True,
    "spellchecking": SPELLCHECKING_ENABLED_DEFAULT,
    "punctuation": False,
    "language": DEFAULT_LANGUAGE,
}

