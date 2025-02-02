import dataclasses
from typing import Any, Optional, TypedDict

from wta.pipeline.transformation_layer.sentence_segment import SentenceSegment

from ...settings import Settings
from .text_unit import TextUnit, TextUnitDict
from .ts import TransformingSequence


class TextUnitsDict(TypedDict):
    previous_textunits: list[TextUnitDict]
    current_textunits: list[TextUnitDict]


class TpsfECMDict(TypedDict):
    revision_id: int
    prev_text_version: str | None
    result_text: str
    transforming_sequence: dict[str, Any]
    transformation_scope: str
    sentence_segments: list[SentenceSegment]
    textunits: TextUnitsDict


@dataclasses.dataclass(frozen=True)
class TpsfECM:
    revision_id: int
    text: str
    ts: TransformingSequence
    prev_tpsf: Optional["TpsfECM"]
    textunits: tuple[TextUnit, ...]
    relevance: bool
    irrelevant_tss_aggregated: tuple[TransformingSequence, ...]
    transformation_scope: str
    sentence_segments: list[SentenceSegment]
    final: bool = False

    def _determine_tpsf_relevance(self, settings: Settings) -> bool:
        impacted_tus = [tu for tu in self.textunits if tu.state in ["new", "modified"]]
        for itu in impacted_tus:
            tagged_tokens = (
                []
                if itu.text is None or itu.text == ""
                else settings.nlp_model.tag_words(itu.text)
            )
            if True in [t["is_typo"] for t in tagged_tokens]:
                return False
        return True

    def __str__(self) -> str:
        return f"""

=== TPSF ===

PREVIOUS TEXT:
{None if not self.prev_tpsf else self.prev_tpsf.text}

RESULT TEXT:
{self.text}

TRANSFORMING SEQUENCE:
{self.ts.label.upper()} *{self.ts.text}*

SCOPE:
{self.transformation_scope}

SENTENCE SEGMENTS:
{[ss.to_text() for ss in self.sentence_segments]}

TEXT UNITS:
{[(tu.state, tu.text) for tu in self.textunits]}

            """

    def to_dict(self) -> TpsfECMDict:
        return {
            "revision_id": self.revision_id,
            "prev_text_version": None if not self.prev_tpsf else self.prev_tpsf.text,
            "result_text": self.text,
            "transforming_sequence": self.ts.to_dict(),
            "transformation_scope": self.transformation_scope,
            "sentence_segments": [ss.to_dict() for ss in self.sentence_segments],
            "textunits": {
                "previous_textunits": []
                if not self.prev_tpsf
                else [tu.to_dict() for tu in self.prev_tpsf.textunits],
                "current_textunits": [tu.to_dict() for tu in self.textunits],
            },
        }

    def to_text(self) -> str:
        return f"""
TPSF version {self.revision_id}:
{self.text}
TS:
{(self.ts.text, self.ts.label.upper())}
SCOPE:
{self.transformation_scope}
SENTENCE SEGMENTS:
{[ss.to_text() for ss in self.sentence_segments]}
TEXT UNITS:
{[(tu.state, tu.text) for tu in self.textunits]}
            """


@dataclasses.dataclass(frozen=True)
class TpsfPCM:
    revision_id: int
    content: str
    pause: float | None
