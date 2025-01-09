from typing import TypedDict


class TSBurstDict(TypedDict):
    preceding_pause: float
    content: str

class TSBurst:

    def __init__(
            self,
            preceding_pause: float,
            content:str
            ) -> None:
        self.preceding_pause = preceding_pause
        self.content = content

    def to_dict(self) -> TSBurstDict:
        return {
            "preceding_pause": self.preceding_pause,
            "content": self.content
        }
