from pathlib import Path

from wta.config_data import ConfigData
from wta.pipeline.sentence_parsing.models import Languages

usr_home = Path.home()
_VIDEO_DATA_DIR = Path(usr_home, "thetool", "input_data", "video")
_VIDEO_OUTPUT_DATA_DIR = Path(usr_home, "thetool", "output_data", "video")

DEFAULT_PAUSE_DURATION = 2
DEFAULT_MIN_EDIT_DISTANCE = 3
DEFAULT_TS_MIN_TOKENS_NUMBER = 2
EDIT_DIST_COMBINED_WITH_TOK_NUMBER_DEFAULT = False
SPELLCHECKING_ENABLED_DEFAULT = False
PUNCTUATION_INCLUDED_DEFAULT = False
DEFAULT_LANGUAGE = Languages.DE

_VIDEO_IDFX_FILES = tuple(
    f for f in _VIDEO_DATA_DIR.iterdir() if f.is_file() and f.suffix == ".idfx"
)


VIDEO: ConfigData = {
    "xml": _VIDEO_IDFX_FILES,
    "output_dir": _VIDEO_OUTPUT_DATA_DIR / "conf0",
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "combine_edit_distance_with_tok_number": EDIT_DIST_COMBINED_WITH_TOK_NUMBER_DEFAULT,
    "enable_spellchecking": SPELLCHECKING_ENABLED_DEFAULT,
    "include_punctuation_edits": PUNCTUATION_INCLUDED_DEFAULT,
    "language": DEFAULT_LANGUAGE,
}

VIDEO_CONF1: ConfigData = {
    "xml": _VIDEO_IDFX_FILES,
    "output_dir": _VIDEO_OUTPUT_DATA_DIR,
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "combine_edit_distance_with_tok_number": EDIT_DIST_COMBINED_WITH_TOK_NUMBER_DEFAULT,
    "enable_spellchecking": SPELLCHECKING_ENABLED_DEFAULT,
    "include_punctuation_edits": True,
    "language": DEFAULT_LANGUAGE,
}

VIDEO_CONF2: ConfigData = {
    "xml": _VIDEO_IDFX_FILES,
    "output_dir": _VIDEO_OUTPUT_DATA_DIR,
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "edit_dist_combined_with_tok_number": True,
    "spellchecking": SPELLCHECKING_ENABLED_DEFAULT,
    "punctuation": PUNCTUATION_INCLUDED_DEFAULT,
    "language": DEFAULT_LANGUAGE,
}

VIDEO_CONF3: ConfigData = {
    "xml": tuple(f for f in _VIDEO_IDFX_FILES if f.name.startswith("R")),
    "output_dir": _VIDEO_OUTPUT_DATA_DIR,
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "min_edit_distance": DEFAULT_MIN_EDIT_DISTANCE,
    "ts_min_tokens_number": DEFAULT_TS_MIN_TOKENS_NUMBER,
    "edit_dist_combined_with_tok_number": True,
    "spellchecking": SPELLCHECKING_ENABLED_DEFAULT,
    "punctuation": False,
    "language": DEFAULT_LANGUAGE,
}
