class BaseEvent:

    def __init__(self, content, startpos, endpos):
        self.content = content
        self.startpos = startpos  # text[startpos] returns the first character of the _content_
        self.endpos = endpos  # text[endpos] returns the last character of the _content_
        self.prev_evnt = None
        self.next_evnt = None

    def set_prev_evnt(self, prev_evnt):
        self.prev_evnt = prev_evnt

    def set_next_evnt(self, next_evnt):
        self.next_evnt = next_evnt

    def set_pause(self):
        pass

    def set_endpos(self):
        pass

    def to_action(self):
        pass

