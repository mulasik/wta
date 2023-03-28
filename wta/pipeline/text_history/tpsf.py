from typing import Any, Optional, TypedDict

from ...settings import Settings
from ..sentence_histories.text_unit import TextUnitDict
from ..sentence_histories.text_unit_factory import TextUnitFactory
from .ts import TransformingSequence


class EditDict(TypedDict):
    transforming_sequence: dict[str, Any]


class TextUnitsDict(TypedDict):
    previous_textunits: list[TextUnitDict]
    current_textunits: list[TextUnitDict]


class TpsfECMDict(TypedDict):
    revision_id: int
    prev_text_version: str | None
    result_text: str
    edit: EditDict
    textunits: TextUnitsDict


class TpsfECM:
    def __init__(
        self,
        revision_id: int,
        content: str,
        ts: TransformingSequence,
        prev_tpsf: Optional["TpsfECM"],
        settings: Settings,
        final: bool = False,
    ) -> None:
        self.revision_id = revision_id
        self.text = content
        self.ts = ts
        self.prev_tpsf = prev_tpsf
        self.final = final
        self.textunits, self.tus_states = TextUnitFactory().run(
            self.text, self.revision_id, self.ts, self.prev_tpsf, settings
        )

    def __str__(self) -> str:
        return f"""

=== TPSF ===

PREVIOUS TEXT:
{None if not self.prev_tpsf else self.prev_tpsf.text}

RESULT TEXT:
{self.text}

TRANSFORMING SEQUENCE:
{self.ts.label.upper()} *{self.ts.text}*

            """

    def to_dict(self) -> TpsfECMDict:
        return {
            "revision_id": self.revision_id,
            "prev_text_version": None if not self.prev_tpsf else self.prev_tpsf.text,
            "result_text": self.text,
            "edit": {
                "transforming_sequence": self.ts.__dict__,
            },
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
            """
