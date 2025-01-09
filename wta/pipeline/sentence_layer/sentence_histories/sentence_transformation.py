from typing import TypedDict

from wta.pipeline.transformation_layer.text_unit import SPSF, TextUnitType


class SentenceTransformationDict(TypedDict):
    tpsf_id: int
    sen_id: int
    sen_text: str
    sen_tu_type: TextUnitType
    sen_ts: str
    ts_startpos: int
    ts_endpos: int | None
    sen_len: int
    operation: str
    sentence_segment: str

class SentenceTransformation:

    def __init__(self, spsf: SPSF, operation: str, sentence_segment: str) -> None:
        self.spsf = spsf
        self.operation = operation
        self.sentence_segment = sentence_segment

    def to_dict(self) -> SentenceTransformationDict:
        return {
            "tpsf_id": self.spsf.tpsf_id,
            "sen_id": self.spsf.sen_id,
            "sen_text": self.spsf.text,
            "sen_tu_type": self.spsf.text_unit_type,
            "sen_ts": self.spsf.ts.text,
            "ts_startpos": self.spsf.ts.startpos,
            "ts_endpos": self.spsf.ts.endpos,
            "sen_len": len(self.spsf.text),
            "operation": self.operation,
            "sentence_segment": self.sentence_segment
        }
