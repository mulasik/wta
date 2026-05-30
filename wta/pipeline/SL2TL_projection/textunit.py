import copy
import dataclasses
import json
from typing import TypedDict

from typing_extensions import Self

from wta.pipeline.SL2TL_projection.segment import Segment, SegmentDict


class TextunitDict(TypedDict):
    type: str
    text: str
    state: str
    startpos: int
    endpos: int
    tpsf_id: int
    segment: SegmentDict|None


class TextunitsDict(TypedDict):
    previous_textunits: list[TextunitDict]
    current_textunits: list[TextunitDict]


@dataclasses.dataclass(frozen=True)
class Textunit:
    """
    TextUnits are elements that the text is composed of.
    There are four types of TextUnits:
    - Sentence (SEN)
    - Sentence Interspace (SIN) (the space between the sentences such as a whitespace or a newline)
    - Sentence Candidate (SEC) (an incomplete sentence)
    - Paragraph Interspace (PIN) (one or multiple whitespace characters occurring at any position in text: tab, newline, return, vertical tab)
    """

    type: str
    text: str
    state: str
    startpos: int
    endpos: int
    tpsf_id: int
    segment: Segment|None

    def __str__(self) -> str:
        return f"{self.state} {self.type} ({self.startpos}-{self.endpos}): |{self.text}| ({self.segment})"

    def to_dict(self) -> TextunitDict:
        return {
            "type": self.type,
            "text": self.text,
            "state": self.state,
            "startpos": self.startpos,
            "endpos": self.endpos,
            "tpsf_id": self.tpsf_id,
            "segment": None if self.segment is None else self.segment.to_dict()
        }

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)

    def copy_to_builder(self) -> "TextunitBuilder":
        builder = TextunitBuilder(self.type, copy.copy(self.text))
        builder.set_state(copy.copy(self.state))
        builder.set_startpos(self.startpos)
        builder.set_endpos(self.endpos)
        builder.set_tpsf_id(self.tpsf_id)
        builder.assign_segment(copy.copy(self.segment))
        return builder


class TextunitBuilder:
    """
    TextUnits are elements that the text is composed of.
    There are three types of TextUnits:
    - Sentence (SEN)
    - Sentence Interspace (SIN) (the space between the sentences such as a whitespace or a newline)
    - Sentence Candidate (SEC) (an incomplete sentence)
    - Paragraph Interspace (PIN) (one or multiple whitespace characters occurring at any position in text: tab, newline, return, vertical tab)
    """

    def __init__(self, tu_type: str, text: str) -> None:
        self.type: str = tu_type
        self.text: str = text
        self.state: str | None = None
        self.startpos: int | None = None
        self.endpos: int | None = None
        self.tpsf_id: int | None = None
        self.segment: Segment | None = None

    def set_state(self, state: str) -> None:
        self.state = state

    def set_tpsf_id(self, tpsf_id: int) -> None:
        self.tpsf_id = tpsf_id

    def set_startpos(self, startpos: int) -> None:
        self.startpos = startpos

    def set_endpos(self, endpos: int) -> None:
        self.endpos = endpos

    def assign_segment(self, segment: Segment|None) -> None:
        self.segment = segment

    def __str__(self) -> str:
        return f"{self.state} {self.type} ({self.startpos}-{self.endpos}): ||{self.text}||"

    def copy_with_text(self, new_text: str) -> Self:
        return self.__class__(self.type, new_text)

    def copy_with_appended_text(self, to_add: str) -> Self:
        return self.copy_with_text(self.text + to_add)

    def to_text_unit(self) -> Textunit:
        if self.state is None or self.tpsf_id is None or self.startpos is None or self.endpos is None:
            msg = f"The text unit builder is not yet complete {vars(self)}"
            raise RuntimeError(msg)
        return Textunit(
            type=self.type,
            text=self.text,
            state=self.state,
            startpos=self.startpos,
            endpos=self.endpos,
            tpsf_id=self.tpsf_id,
            segment=self.segment
        )
