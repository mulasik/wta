import json
from abc import ABC


class TextUnit(ABC):
    """
    TextUnits are elements that the text is composed of.
    There are two types of TextUnits:
    - Sentence
    - SentenceInterspace (the space between the sentences such as a whitespace or a newline)
    """

    def __init__(self, text):
        self.text: str = text
        self.tu_id: int = None
        self.state: str = None
        # TODO:
        #  - retrieve tu transforming sequence,
        #  - detect tu relevance,
        #  - collect preceding transforming sequences of irrelevant tus

    def set_id(self, tu_id):
        self.tu_id = tu_id

    def set_state(self, state):
        self.state = state

    def __str__(self):
        return f"{self.text}"

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_dict(self):
        # TODO: extend with more tu properties
        tu_dict = {"text": self.text}
        return tu_dict

    def to_text(self):
        # TODO: extend with more tu properties
        s = self.to_dict()
        return f"""
                {s["text"]}
                """


class Sin(TextUnit):
    text: str

    def __init__(self, text):
        super().__init__(text)


class Sec(TextUnit):
    text: str

    def __init__(self, text):
        super().__init__(text)


class Sen(TextUnit):
    text: str

    def __init__(self, text):
        super().__init__(text)
