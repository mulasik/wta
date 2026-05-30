import dataclasses
from typing import TypedDict

from wta.pipeline.SL2TL_projection.segment import Segment, SegmentDict
from wta.pipeline.SL2TL_projection.textunit import Textunit


class SpsfBuilder:
    def __init__(self, tu: Textunit) -> None:
        self.sen_id: int | None = None
        self.tu_type: str = tu.type
        self.text: str = tu.text
        self.state: str = tu.state
        self.tpsf_id: int = tu.tpsf_id
        self.pos_in_text: int | None = None
        self.startpos: int = tu.startpos
        self.endpos: int = tu.endpos
        self.operation: str | None = None
        self.ts: Segment | None = tu.segment
        self.production_time: float | None = None
        self.previously_revised_spsf_pos: int | None = None

    def set_pos_in_text(self, pos_in_text: int) -> None:
        self.pos_in_text = pos_in_text

    def set_id(self, sen_id: int) -> None:
        self.sen_id = sen_id

    def set_state(self, state: str) -> None:
        self.state = state

    def set_operation(self, operation: str) -> None:
        self.operation = operation

    def set_ts(self, sen_ts: Segment|None) -> None:
        self.ts = sen_ts

    def set_production_time(self, production_time: float | None) -> None:
        self.production_time = production_time

    def set_previously_revised_spsf_pos(self, previously_revised_spsf_pos: int | None) -> None:
        self.previously_revised_spsf_pos = previously_revised_spsf_pos

    def set_text(self, text: str) -> None:
        self.text = text

    def set_tpsf_id(self, tpsf_id: int) -> None:
        self.tpsf_id = tpsf_id

    def __str__(self) -> str:
        return f"""
------
TPSF {self.tpsf_id}, {self.state} {self.tu_type} at pos {self.pos_in_text}:
|{self.text}|

Sentence TS: {self.ts}
Operation: {self.operation}
Production Time: {self.production_time}
Position of previously revised SPSF: {self.previously_revised_spsf_pos}
------
"""

    def to_spsf(self) -> "Spsf":
        if self.sen_id is None or self.pos_in_text is None:
            msg = f"The sentence version builder is not yet complete {vars(self)}"
            raise RuntimeError(msg)
        return Spsf(
            sen_id=self.sen_id,
            tu_type=self.tu_type,
            text=self.text,
            state=self.state,
            tpsf_id=self.tpsf_id,
            pos_in_text=self.pos_in_text,
            startpos=self.startpos,
            endpos=self.endpos,
            operation=self.operation,
            ts=self.ts,
            production_time=self.production_time,
            previously_revised_spsf_pos=self.previously_revised_spsf_pos
        )

class SpsfDict(TypedDict):
    sen_id: int
    tu_type: str
    text: str
    state: str
    tpsf_id: int
    pos_in_text: int
    operation: str|None
    ts: SegmentDict|None
    production_time: float|None
    previously_revised_spsf_pos: int|None


@dataclasses.dataclass(frozen=True)
class Spsf:
    sen_id: int
    tu_type: str
    text: str
    state: str
    tpsf_id: int
    pos_in_text: int
    startpos: int
    endpos: int
    operation: str|None
    ts: Segment|None
    production_time: float|None
    previously_revised_spsf_pos: int|None

    def to_dict(self) -> SpsfDict:
        return {
            "sen_id": self.sen_id,
            "tu_type": self.tu_type,
            "text": self.text,
            "state": self.state,
            "tpsf_id": self.tpsf_id,
            "pos_in_text": self.pos_in_text,
            "operation": None if self.operation is None else self.operation,
            "ts": None if self.ts is None else self.ts.to_dict(),
            "production_time": self.production_time,
            "previously_revised_spsf_pos": self.previously_revised_spsf_pos
        }

    def __str__(self) -> str:
        return f"""
TPSF {self.tpsf_id}, {self.state} {self.tu_type} at pos {self.pos_in_text}:
|{self.text}|
Sentence TS: {self.ts}
Operation: {self.operation}
Production Time: {self.production_time}
Position of previously revised SPSF: {self.previously_revised_spsf_pos}
"""
