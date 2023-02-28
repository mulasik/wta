import json
from abc import ABC
from typing import TypedDict

from typing_extensions import Self


class TextUnitDict(TypedDict):
    text: str


class TextUnit(ABC):
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
        # TODO:
        #  - retrieve tu transforming sequence,
        #  - detect tu relevance,
        #  - collect preceding transforming sequences of irrelevant tus

    def set_id(self, tu_id: int) -> None:
        self.tu_id = tu_id

    def set_state(self, state: str) -> None:
        self.state = state

    def __str__(self) -> str:
        return f"{self.text}"

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_dict(self) -> TextUnitDict:
        # TODO: extend with more tu properties
        return {"text": self.text}

    def to_text(self) -> str:
        # TODO: extend with more tu properties
        s = self.to_dict()
        return f"""
                {s["text"]}
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
