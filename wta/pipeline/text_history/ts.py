from ...language_models.spacy import TaggedWord
from ...utils.nlp import contains_end_punctuation_in_the_middle


class TransformingSequence:
    """
    A class to represent transforming sequence:
    the sequence which transforms one text version into another one.
    The transforming sequence can have one of the following labels:
    - append
    - insertion
    - deletion
    - midletion
    - replacement
    - pasting
    """

    def __init__(
        self,
        text: str,
        label: str,
        startpos: int,
        endpos: int | None,
        starttime: int | None,
        endtime: int | None,
        duration: int | None,
        preceding_pause: int | None,
        rplcmt_textlen: int | None,
    ) -> None:
        """
        Initializes an object of type TransformingSequence (TS).
        Args:
            text: content of the TS
            label: type of edit operation performed with the TS
            startpos: position of the first character of the TS
            endpos: position of the last character of the TS
            starttime: time when first event in the action group started
            endtime: time when last event in the action group ended
            duration: difference between endtime and starttime
            preceding_pause: time between endtime of the previous action group and starttime of the current action group
        """
        self.text = text
        self.label = label
        self.startpos = startpos
        self.endpos = endpos
        self.starttime = starttime
        self.endtime = endtime
        self.duration = duration
        self.preceding_pause = preceding_pause
        self.tagged_tokens: list[
            TaggedWord
        ] = (
            []
        )  # if text is None or text == '' else settings.nlp_model.tag_words(self.text)
        self.contains_punctuation = "PUNCT" in [
            tok["pos"] for tok in self.tagged_tokens
        ]
        self.contains_end_punctuation_in_the_middle = (
            contains_end_punctuation_in_the_middle(self.text)
        )
        self.ts_relevance: bool | None = None
        self.rplcmt_textlen = rplcmt_textlen

    def set_text(self, text: str) -> None:
        self.text = text

    def set_ts_relevance(self, relevance: bool) -> None:
        self.ts_relevance = relevance

    def __str__(self) -> str:
        return (
            ""
            if self.text is None
            else f'{self.label} ({self.startpos}-{self.endpos}): "{self.text}"'
        )


class SenTs:
    def __init__(self) -> None:
        ...


class TsGroup:
    def __init__(self) -> None:
        ...
