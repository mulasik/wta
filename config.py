import os

DATA_DIR = "example_data"
VIDEO_DATA_DIR = os.path.join(DATA_DIR, "video")

DEFAULT_PAUSE_DURATION = 2
DEFAULT_MIN_EDIT_DISTANCE = 3
DEFAULT_FILTERING_BY_TS = True
DEFAULT_TS_MIN_TOKENS_NUMBER = 1
DEFAULT_FILTERING_BY_PRODUCT = True
DEFAULT_SPELLING_CHECK = True
DEFAULT_LANGUAGE = "German"

VIDEO = {
    "xml": [
        os.path.join(VIDEO_DATA_DIR, f)
        for f in os.listdir(VIDEO_DATA_DIR)
        if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "video"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "filtering_by_ts": DEFAULT_FILTERING_BY_TS,
    "ts_min_length": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "filtering_by_product": DEFAULT_FILTERING_BY_PRODUCT,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "spelling_check": DEFAULT_SPELLING_CHECK,
    "language": DEFAULT_LANGUAGE,
}

