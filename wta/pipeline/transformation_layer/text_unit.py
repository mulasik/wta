import copy
import dataclasses
import enum
import json
from typing import TypedDict

from typing_extensions import Self

from wta.pipeline.transformation_layer.ts import TransformingSequence


class TextUnitDict(TypedDict):
    text_unit_type: "TextUnitType"
    text: str
    state: str
    tpsf_id: int


class TextUnitType(enum.IntEnum):
    SIN = enum.auto()
    SEC = enum.auto()
    SEN = enum.auto()
    PIN = enum.auto()


@dataclasses.dataclass(frozen=True)
class TextUnit:
    """
    TextUnits are elements that the text is composed of.
    There are three types of TextUnits:
    - Sentence (SEN)
    - Sentence Interspace (SIN) (the space between the sentences such as a whitespace or a newline)
    - Sentence Candidate (SEC) (an incomplete sentence)
    - Paragraph Interspace (PIN) (one or multiple whitespace characters occurring at any position in text: tab, newline, return, vertical tab)
    """

    text_unit_type: TextUnitType
    text: str
    state: str
    tpsf_id: int

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_dict(self) -> TextUnitDict:
        # TODO: extend with more tu properties
        return {
            "text_unit_type": self.text_unit_type,
            "text": self.text,
            "state": self.state,
            "tpsf_id": self.tpsf_id,
        }

    def to_text(self) -> str:
        # TODO: extend with more tu properties
        s = self.to_dict()
        return f"""
TPSF {s["tpsf_id"]}, type {s["text_unit_type"].name}, state {s["state"]}:
    |{s["text"]}|
"""

    def copy_to_builder(self) -> "TextUnitBuilder":
        builder = TextUnitBuilder(self.text_unit_type, copy.copy(self.text))
        builder.set_state(copy.copy(self.state))
        builder.set_tpsf_id(self.tpsf_id)
        return builder


class TextUnitBuilder:
    """
    TextUnits are elements that the text is composed of.
    There are three types of TextUnits:
    - Sentence (SEN)
    - Sentence Interspace (SIN) (the space between the sentences such as a whitespace or a newline)
    - Sentence Candidate (SEC) (an incomplete sentence)
    - Paragraph Interspace (PIN) (one or multiple whitespace characters occurring at any position in text: tab, newline, return, vertical tab)
    """

    def __init__(self, text_unit_type: TextUnitType, text: str) -> None:
        self.text_unit_type: TextUnitType = text_unit_type
        self.text: str = text
        self.state: str | None = None
        self.tpsf_id: int | None = None
        # TODO:
        #  - detect tu relevance,
        #  - collect preceding transforming sequences of irrelevant tus

    def set_state(self, state: str) -> None:
        self.state = state

    def set_tpsf_id(self, tpsf_id: int) -> None:
        self.tpsf_id = tpsf_id

    def __str__(self) -> str:
        return f"{self.text}"

    def copy_with_text(self, new_text: str) -> Self:
        return self.__class__(self.text_unit_type, new_text)

    def copy_with_appended_text(self, to_add: str) -> Self:
        return self.copy_with_text(self.text + to_add)

    def to_text_unit(self) -> TextUnit:
        if self.state is None or self.tpsf_id is None:
            msg = f"The text unit builder is not yet complete {vars(self)}"
            raise RuntimeError(msg)
        return TextUnit(
            text_unit_type=self.text_unit_type,
            text=self.text,
            state=self.state,
            tpsf_id=self.tpsf_id,
        )


class SPSFBuilder:
    def __init__(self, tu: TextUnit) -> None:
        self.sen_id: int | None = None
        self.text_unit_type: TextUnitType = tu.text_unit_type
        self.text: str = tu.text
        self.state: str = tu.state
        self.tpsf_id: int = tu.tpsf_id
        self.pos_in_text: int | None = None
        self.ts: TransformingSequence | None = None
        self.operation: str | None = None
        self.sentence_segment: str | None = None

    def set_pos_in_text(self, pos_in_text: int) -> None:
        self.pos_in_text = pos_in_text

    def set_id(self, sen_id: int) -> None:
        self.sen_id = sen_id

    def set_ts(self, ts: TransformingSequence) -> None:
        self.ts = ts

    def set_operation(self, operation: str) -> None:
        self.operation = operation

    def set_sentence_segment(self, sentence_segment: str) -> None:
        self.sentence_segment = sentence_segment

    def to_sentence_version(self) -> "SPSF":
        if self.sen_id is None or self.pos_in_text is None or self.ts is None:
            msg = f"The sentence version builder is not yet complete {vars(self)}"
            raise RuntimeError(msg)
        return SPSF(
            sen_id=self.sen_id,
            text_unit_type=self.text_unit_type,
            text=self.text,
            state=self.state,
            tpsf_id=self.tpsf_id,
            pos_in_text=self.pos_in_text,
            ts=self.ts,
            operation=self.operation,
            sentence_segment=self.sentence_segment
        )

class SPSFDict(TypedDict):
    sen_id: int
    text_unit_type: "TextUnitType"
    text: str
    state: str
    tpsf_id: int
    pos_in_text: int
    ts_label: str
    ts_text: str
    operation: str
    sentence_segment: str


@dataclasses.dataclass(frozen=True)
class SPSF:
    sen_id: int
    text_unit_type: TextUnitType
    text: str
    state: str
    tpsf_id: int
    pos_in_text: int
    ts: TransformingSequence
    operation: str
    sentence_segment: str

    def to_dict(self) -> SPSFDict:
        return {
            "sen_id": self.sen_id,
            "text_unit_type": self.text_unit_type,
            "text": self.text,
            "state": self.state,
            "tpsf_id": self.tpsf_id,
            "pos_in_text": self.pos_in_text,
            "ts_label": self.ts.label,
            "ts_text": self.ts.text,
            "operation": self.operation,
            "sentence_segment": self.sentence_segment
        }

    def to_text(self) -> str:
        s = self.to_dict()
        return f"""
TPSF {s["tpsf_id"]}, position {s["pos_in_text"]}:
    {s["text"]}
{s["ts_label"].upper()}:
    |{s["ts_text"]}|
Operation: {s["operation"]}
Sentence segment: {s["sentence_segment"]}
                """