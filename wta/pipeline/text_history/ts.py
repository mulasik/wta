from ...settings import Settings


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
        settings: Settings,
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

        self.relevance = (
            False
            if text is None or text == ""
            else self._determine_ts_relevance(settings)
        )
        self.rplcmt_textlen = rplcmt_textlen

    def set_text(self, text: str) -> None:
        self.text = text

    def _determine_ts_relevance(self, settings: Settings) -> bool:
        min_edit_distance = settings.config["min_edit_distance"]
        ts_min_tokens_number = settings.config["ts_min_tokens_number"]
        edit_dist_combined_with_tok_number = settings.config[
            "combine_edit_distance_with_tok_number"
        ]
        punctuation_rel = settings.config["include_punctuation_edits"]

        ts_longer_than_min = len(self.text) >= min_edit_distance
        more_toks_than_min = len(self.text.split(" ")) >= ts_min_tokens_number

        if punctuation_rel is True:
            tagged_tokens = settings.nlp_model.tag_words(self.text)
            contains_punctuation = "PUNCT" in [tok["pos"] for tok in tagged_tokens]
            if contains_punctuation:
                return True
        if edit_dist_combined_with_tok_number is True:
            return ts_longer_than_min and more_toks_than_min
        return ts_longer_than_min or more_toks_than_min

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
