import json
from abc import ABC
from typing import TypedDict

from typing_extensions import Self

from wta.pipeline.text_history.ts import TransformingSequence


class TextUnitDict(TypedDict):
    text: str
    pos_in_text: int | None
    tpsf_id: int | None
    ts_text: str | None
    ts_label: str | None


class TextUnit(ABC):  # noqa: B024
    """
    TextUnits are elements that the text is composed of.
    There are two types of TextUnits:
    - Sentence
    - SentenceInterspace (the space between the sentences such as a whitespace or a newline)
    """

    def __init__(self, text: str) -> None:
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

    def copy_with_text(self, new_text: str) -> Self:
        return self.__class__(new_text)

    def copy_with_appended_text(self, to_add: str) -> Self:
        return self.copy_with_text(self.text + to_add)


class Sin(TextUnit):
    pass


class Sec(TextUnit):
    pass


class Sen(TextUnit):
    pass
