
from typing import TypedDict


class TextTransformationSegmentDict(TypedDict):
    text: str
    segment_type: str
    length: int

class SentenceSegment:

    def __init__(
            self,
            text: str,
            segment_type: str) -> None:
        self.text = text
        self.segment_type = segment_type
        self.length = len(text)

    def to_dict(self) -> TextTransformationSegmentDict:
        return {
            "text": self.text,
            "segment_type": self.segment_type,
            "length": self.length
        }

    def to_text(self) -> str:
        return f"""|{self.text}| ({self.segment_type})"""
