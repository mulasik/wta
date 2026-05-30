from typing import TypedDict

from wta.pipeline.names import BurstTypes


class BurstDict(TypedDict):
    tpsf_id: int|None
    ts_label: str
    preceding_pause: float|None
    content: str
    following_pause: float|None

class Burst:

    def __init__(
            self,
            preceding_pause: float|None,
            following_pause: float|None,
            content:str,
            tpsf_id: int|None,
            ts_label: str
            ) -> None:
        self.preceding_pause = preceding_pause
        self.following_pause = following_pause
        self.content = content
        self.tpsf_id = tpsf_id
        self.ts_label = ts_label
        self.type = self.set_burst_type()

    def set_tpsf_id(self, tpsf_id: int) -> None:
        self.tpsf_id = tpsf_id

    def set_burst_type(self) -> str:
        if self.following_pause and self.preceding_pause:
            if self.preceding_pause > 2 and self.following_pause > 2:
                return BurstTypes.PP_BURST
            if self.preceding_pause > 2 and self.following_pause <= 2:
                return BurstTypes.PR_BURST
            if self.preceding_pause <= 2 and self.following_pause > 2:
                return BurstTypes.RP_BURST
            return BurstTypes.RR_BURST
        return BurstTypes.UNK


    def to_dict(self) -> BurstDict:
        return {
            "tpsf_id": self.tpsf_id,
            "ts_label": self.ts_label,
            "preceding_pause": self.preceding_pause,
            "content": self.content,
            "following_pause": self.following_pause,
        }

    def __str__(self) -> str:
        return f"{self.preceding_pause} ({self.type}): |{self.content}| {self.following_pause}"
