from typing import TypedDict

from wta.pipeline.BL2TL_projection.burst import Burst, BurstDict
from wta.settings import Settings


class SegmentDict(TypedDict):
    text: str
    segment_type: str
    startpos: int | None
    endpos: int | None
    relative_startpos: int | None
    relative_endpos: int | None
    preceding_pause: float | None
    following_pause: float | None
    starttime: float | None
    endtime: float | None
    bursts: list[BurstDict]

class Segment:

    def __init__(
            self,
            text: str,
            segment_type: str,
            startpos: int | None,
            endpos: int | None,
            relative_startpos: int | None,
            relative_endpos: int | None,
            preceding_pause: float | None,
            following_pause: float | None,
            starttime: float | None,
            endtime: float | None

        ) -> None:
        self.text = text
        self.segment_type = segment_type
        self.startpos = startpos
        self.endpos = endpos
        self.relative_startpos = relative_startpos
        self.relative_endpos = relative_endpos
        self.preceding_pause = preceding_pause
        self.following_pause = following_pause
        self.starttime = starttime
        self.endtime = endtime
        self.bursts: list[Burst] | None = None

    def set_following_pause(self, following_pause: float|None) -> None:
        self.following_pause = following_pause

    def set_preceding_pause(self, preceding_pause: float|None) -> None:
        self.preceding_pause = preceding_pause

    def set_bursts(self, bursts: list[Burst]) -> None:
        self.bursts = bursts

    def to_dict(self) -> SegmentDict:
        return {
            "text": self.text,
            "segment_type": self.segment_type,
            "startpos": self.startpos,
            "endpos": self.endpos,
            "relative_startpos": self.relative_startpos,
            "relative_endpos": self.relative_endpos,
            "preceding_pause": self.preceding_pause,
            "following_pause": self.following_pause,
            "starttime": self.starttime,
            "endtime": self.endtime,
            "bursts": [b.to_dict() for b in self.bursts] if self.bursts is not None else []
        }

    def __str__(self) -> str:
        return f"""|{self.text}|
{self.segment_type.upper()} ({self.startpos}-{self.endpos} / {self.relative_startpos}-{self.relative_endpos})
Preceding and following pause: {self.preceding_pause} - {self.following_pause}
{len(self.bursts) if self.bursts is not None else '0'} burst(s): {[str(b) for b in self.bursts] if self.bursts is not None else 'None'}
"""

    # TODO: implement relevance determination, add collecting preceding transforming sequences of irrelevant tus
    def _determine_segment_relevance(self, settings: Settings) -> bool:
        return True
