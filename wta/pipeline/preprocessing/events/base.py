from typing import Optional

from ..action import Action


class BaseEvent:
    def __init__(self, content: str, startpos: int, endpos: int | None) -> None:
        self.content = content
        # text[startpos] returns the first character of the _content_
        self.startpos = startpos
        # text[endpos] returns the last character of the _content_
        self.endpos = endpos
        self.prev_evnt: "BaseEvent" | None = None
        self.next_evnt: "BaseEvent" | None = None

    def set_prev_evnt(self, prev_evnt: Optional["BaseEvent"]) -> None:
        self.prev_evnt = prev_evnt

    def set_next_evnt(self, next_evnt: Optional["BaseEvent"]) -> None:
        self.next_evnt = next_evnt

    def set_preceding_pause(self) -> None:
        pass

    # def set_endpos(self) -> None:
    #     pass

    def to_action(self) -> Action | None:
        return None
