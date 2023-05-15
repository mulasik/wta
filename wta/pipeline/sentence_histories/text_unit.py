import copy
import dataclasses
import enum
import json
from typing import TypedDict

from typing_extensions import Self

from wta.pipeline.text_history.ts import TransformingSequence


class TextUnitDict(TypedDict):
    text: str
    pos_in_text: int
    tpsf_id: int
    ts_text: str
    ts_label: str


class TextUnitType(enum.Enum):
    SIN = enum.auto()
    SEC = enum.auto()
    SEN = enum.auto()


@dataclasses.dataclass(frozen=True)
class TextUnit:
    """
    TextUnits are elements that the text is composed of.
    There are two types of TextUnits:
    - Sentence
    - SentenceInterspace (the space between the sentences such as a whitespace or a newline)
    """

    text_unit_type: TextUnitType
    text: str
    tu_id: int
    state: str
    pos_in_text: int
    tpsf_id: int
    ts: TransformingSequence

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_dict(self) -> TextUnitDict:
        # TODO: extend with more tu properties
        return {
            "text": self.text,
            "pos_in_text": self.pos_in_text,
            "tpsf_id": self.tpsf_id,
            "ts_text": None if self.ts is None else self.ts.text,
            "ts_label": None if self.ts is None else self.ts.label,
        }

    def to_text(self) -> str:
        # TODO: extend with more tu properties
        s = self.to_dict()
        return f"""
TPSF {s["tpsf_id"]}, position {s["pos_in_text"]}:
    {s["text"]}
{s["ts_label"].upper()}:
    |{s["ts_text"]}|
                """

    def copy_to_builder(self) -> "TextUnitBuilder":
        builder = TextUnitBuilder(self.text_unit_type, copy.copy(self.text))
        builder.set_id(self.tu_id)
        builder.set_state(copy.copy(self.state))
        builder.set_pos_in_text(self.pos_in_text)
        builder.set_tpsf_id(self.tpsf_id)
        builder.set_ts(self.ts)
        return builder


class TextUnitBuilder:
    """
    TextUnits are elements that the text is composed of.
    There are two types of TextUnits:
    - Sentence
    - SentenceInterspace (the space between the sentences such as a whitespace or a newline)
    """

    def __init__(self, text_unit_type: TextUnitType, text: str) -> None:
        self.text_unit_type = text_unit_type
        self.text: str = text

        self.tu_id: int | None = None
        self.state: str | None = None
        self.pos_in_text: int | None = None
        self.tpsf_id: int | None = None
        self.ts: TransformingSequence | None = None
        # TODO:
        #  - detect tu relevance,
        #  - collect preceding transforming sequences of irrelevant tus

    def set_id(self, tu_id: int) -> None:
        self.tu_id = tu_id

    def set_state(self, state: str) -> None:
        self.state = state

    def set_pos_in_text(self, pos_in_text: int) -> None:
        self.pos_in_text = pos_in_text

    def set_tpsf_id(self, tpsf_id: int) -> None:
        self.tpsf_id = tpsf_id

    def set_ts(self, ts: TransformingSequence) -> None:
        self.ts = ts

    def __str__(self) -> str:
        return f"{self.text}"

    def copy_with_text(self, new_text: str) -> Self:
        return self.__class__(self.text_unit_type, new_text)

    def copy_with_appended_text(self, to_add: str) -> Self:
        return self.copy_with_text(self.text + to_add)

    def to_text_unit(self) -> TextUnit:
        if (
            self.tu_id is None
            or self.state is None
            or self.pos_in_text is None
            or self.tpsf_id is None
            or self.ts is None
        ):
            msg = f"The text unit builder is not yet complete {self}"
            raise RuntimeError(msg)
        return TextUnit(
            text_unit_type=self.text_unit_type,
            text=self.text,
            tu_id=self.tu_id,
            state=self.state,
            pos_in_text=self.pos_in_text,
            tpsf_id=self.tpsf_id,
            ts=self.ts,
        )
