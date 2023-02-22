from typing import TypedDict

from typing_extensions import NotRequired


class ConfigData(TypedDict):
    xml: list[str]
    output_dir: str
    pause_duration: int
    min_edit_distance: int
    ts_min_tokens_number: int
    combine_edit_distance_with_tok_number: NotRequired[bool]
    enable_spellchecking: NotRequired[bool]
    include_punctuation_edits: NotRequired[bool]
    language: str
    edit_dist_combined_with_tok_number: NotRequired[bool]
    spellchecking: NotRequired[bool]
    punctuation: NotRequired[bool]
