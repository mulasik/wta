import os

DATA_DIR = "example_data"
VIDEO_DATA_DIR = os.path.join(DATA_DIR, "video")


DEFAULT_PAUSE_DURATION = 2
DEFAULT_MIN_EDIT_DISTANCE = 3
DEFAULT_TS_MIN_TOKENS_NUMBER = 2
DEFAULT_SPELLCHECKING = False
DEFAULT_PUNCTUATION_RELEVANCE = True
DEFAULT_LANGUAGE = "German"

VIDEO = {
    "xml": [
        os.path.join(VIDEO_DATA_DIR, f)
        for f in os.listdir(VIDEO_DATA_DIR)
        if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith("idfx") and f.startswith("C")
    ],
    "output": os.path.join("output_data", "video"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "spellchecking": DEFAULT_SPELLCHECKING,
    "punctuation": DEFAULT_PUNCTUATION_RELEVANCE,
    "language": DEFAULT_LANGUAGE,
}

