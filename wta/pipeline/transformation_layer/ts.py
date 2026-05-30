import dataclasses
from typing import TypedDict

from wta.pipeline.BL2TL_projection.bl2tl_projector import BL2TLProjector
from wta.pipeline.BL2TL_projection.burst import Burst, BurstDict
from wta.pipeline.preprocessing.action import Action
from wta.pipeline.SL2TL_projection.segment import Segment, SegmentDict

from ...settings import Settings


class TSDict(TypedDict):
    text: str
    replaced_text: str
    label: str
    startpos: int
    endpos: int
    starttime: float
    endtime: float
    pauses: list[float]
    following_pause: float
    bursts: list[BurstDict]
    bscope: str
    segments: list[SegmentDict]
    replaced_segments: list[SegmentDict]
    sscope: str
    relevance: bool
    actions: list[Action]

@dataclasses.dataclass(frozen=True)
class TransformingSequence:
    """
    A class to represent transforming sequence:
    the sequence which reflects the difference between
    two adjacent text versions.

    Fields:
    text: content of the TS
    label: type of edit operation performed with the TS
    startpos: position of the first character of the TS
    endpos: position of the last character of the TS
    starttime: time when first event in the action group started
    endtime: time when last event in the action group ended
    duration: difference between endtime and starttime
    preceding_pause: time between endtime of the previous action group and starttime of the current action group
    """
    tpsf_id: int | None
    text: str
    replaced_text: str
    label: str
    startpos: int
    endpos: int
    starttime: float
    endtime: float
    pauses: list[float]
    following_pause: float
    bursts: list[Burst]
    bscope: str
    segments: list[Segment]
    replaced_segments: list[Segment]
    sscope: str
    relevance: bool
    actions: list[Action]

    def __str__(self) -> str:
        preceding_pause = self.pauses[0] if len(self.pauses) > 0 else None
        return (
            ""
            if self.text is None
            else f"""{self.label.upper()} * {self.sscope.upper()} * {self.bscope.upper()} * {self.startpos}-{self.endpos}:
|{self.text}|
Time: {round(self.starttime/1000, 4) if self.starttime else None}-{round(self.endtime/1000, 4) if self.endtime else None}
Preceding and following pause: {preceding_pause} and {self.following_pause}
{len(self.text)} characters
{len(self.pauses)} pauses: {self.pauses}
{len(self.bursts)} bursts: {[str(b) for b in self.bursts]}
{len(self.segments)} segments:
{[str(s) for s in self.segments]}
{len(self.replaced_segments)} rpl segments:
{[str(s) for s in self.replaced_segments]}
"""
        )

    def to_dict(self) -> TSDict:
        return {
            "text": self.text,
            "label": self.label,
            "startpos": self.startpos,
            "endpos": self.endpos,
            "starttime": self.starttime,
            "endtime": self.endtime,
            "pauses": self.pauses,
            "following_pause": self.following_pause,
            "bursts": [b.to_dict() for b in self.bursts],
            "bscope": self.bscope,
            "sscope": self.sscope,
            "segments": [s.to_dict() for s in self.segments],
            "replaced_text": self.replaced_text,
            "replaced_segments": [s.to_dict() for s in self.replaced_segments],
            "relevance": self.relevance,
            "actions": [a.to_dict() for a in self.actions],
        }


class TSBuilderDict(TypedDict):
    tpsf_id: int | None
    text: str
    label: str
    startpos: int
    endpos: int | None
    starttime: float | None
    endtime: float | None
    pauses: list[float]
    following_pause: float | None


@dataclasses.dataclass(frozen=True)
class TSBuilder:
    """
    A class to represent TSBuilder (TransformingSequenceBuilder).
    It stores basic data on the transformation retrieved
    directly from a keystroke log file required
    for generating objects of type TransformingSequence.
    """
    tpsf_id: int | None
    text: str
    label: str
    startpos: int
    endpos: int | None
    starttime: float | None
    endtime: float | None
    pauses: list[float]
    following_pause: float | None
    rplcmt_textlen: int | None
    actions: list[Action]

    def __str__(self) -> str:
        preceding_pause = self.pauses[0] if len(self.pauses) > 0 else None
        return (
            ""
            if self.text is None
            else f"""{self.label.upper()} * {self.startpos}-{self.endpos}:
|{self.text}|
Time: {self.starttime}-{self.endtime}
Preceding and following pause: {preceding_pause} and {self.following_pause}
{len(self.text)} characters
{len(self.pauses)} pauses: {self.pauses}
"""
        )

    def to_dict(self) -> TSBuilderDict:
        return {
            "tpsf_id": self.tpsf_id,
            "text": self.text,
            "label": self.label,
            "startpos": self.startpos,
            "endpos": self.endpos,
            "starttime": self.starttime,
            "endtime": self.endtime,
            "pauses": self.pauses,
            "following_pause": self.following_pause
        }

    def to_transforming_sequence(
            self,
            text: str,
            replaced_text: str,
            sscope: str,
            segments: list[Segment],
            replaced_segments: list[Segment],
            settings: Settings
        ) -> TransformingSequence:
        burst_trans_prjctr = BL2TLProjector(text, self.pauses, self.following_pause, self.tpsf_id, self.label)
        relevance = self._determine_ts_relevance(settings)
#         print(f"""
# >> FINAL TRANSFORMING SEQUENCE DETAILS <<
# TS: {self.label.upper()} ({self.startpos}-{self.endpos})
# Text: |{text}|
# Replaced text: |{replaced_text}|
# TS sentence scope: {sscope.upper()}
# TS sentence segments: {[s.__str__() for s in segments]}
# TS preceding pause: {self.pauses[0] if len(self.pauses)>0 else None}
# TS following pause: {self.following_pause}
# TS pauses: {self.pauses}
# TS burst scope: {burst_trans_prjctr.bscope.upper()}
# TS bursts: {[str(b) for b in burst_trans_prjctr.bursts]}
# """)
        return TransformingSequence(
            self.tpsf_id,
            text,
            replaced_text,
            self.label,
            self.startpos,
            self.endpos if self.endpos is not None else -1,
            self.starttime if self.starttime is not None else -1,
            self.endtime if self.endtime is not None else -1,
            self.pauses,
            self.following_pause if self.following_pause is not None else -1,
            burst_trans_prjctr.bursts,
            burst_trans_prjctr.bscope,
            segments,
            replaced_segments,
            sscope,
            relevance,
            actions=self.actions
        )

    def _determine_ts_relevance(self, settings: Settings) -> bool:
        if self.text is None or self.text == "":
            return False
        min_edit_distance = settings.config["min_edit_distance"]
        ts_min_tokens_number = settings.config["ts_min_tokens_number"]
        edit_dist_combined_with_tok_number = settings.config[
            "combine_edit_distance_with_tok_number"
        ]
        punctuation_rel = settings.config["include_punctuation_edits"]
        ts_longer_than_min = len(self.text) >= min_edit_distance
        more_toks_than_min = len(self.text.split(" ")) >= ts_min_tokens_number
        if punctuation_rel is True:
            tagged_tokens = settings.nlp_model.tag_words(self.text)
            contains_punctuation = "PUNCT" in [tok["pos"] for tok in tagged_tokens]
            if contains_punctuation:
                return True
        if edit_dist_combined_with_tok_number is True:
            return ts_longer_than_min and more_toks_than_min
        return ts_longer_than_min or more_toks_than_min

