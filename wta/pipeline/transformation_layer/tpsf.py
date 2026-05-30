import dataclasses
from typing import Optional, TypedDict

from wta.pipeline.SL2TL_projection.textunit import Textunit, TextunitDict

from .ts import TransformingSequence, TSDict


class TpsfDict(TypedDict):
    id: int
    text: str
    prev_tpsf_text: str | None
    ts: TSDict
    tus: list[TextunitDict]
    deleted_tus: list[TextunitDict]
    prev_tpsf_tus: list[TextunitDict]
    relevance: bool

@dataclasses.dataclass(frozen=True)
class Tpsf:
    id: int
    text: str
    ts: TransformingSequence
    prev_tpsf: Optional["Tpsf"]
    tus: list[Textunit]
    deleted_tus: list[Textunit]
    relevance: bool
    irrelevant_tss_aggregated: tuple[TransformingSequence, ...]
    final: bool = False

    def __str__(self) -> str:
        return f"""

=== TPSF {self.id} ===

PREVIOUS TEXT:
{None if not self.prev_tpsf else self.prev_tpsf.text}

RESULT TEXT:
{self.text}

TRANSFORMING SEQUENCE:
{self.ts.label.upper()} *{self.ts.text}*

TEXT UNITS:
{[(tu.state, tu.text) for tu in self.tus]}

            """

    def to_dict(self) -> TpsfDict:
        return {
            "id": self.id,
            "text": self.text,
            "prev_tpsf_text": None if not self.prev_tpsf else self.prev_tpsf.text,
            "ts": self.ts.to_dict(),
            "tus": [tu.to_dict() for tu in self.tus],
            "deleted_tus": [tu.to_dict() for tu in self.deleted_tus],
            "prev_tpsf_tus": [] if self.prev_tpsf is None else [tu.to_dict() for tu in self.prev_tpsf.tus],
            "relevance": self.relevance
        }


@dataclasses.dataclass(frozen=True)
class TpsfPCM:
    revision_id: int
    content: str
    pause: float | None
