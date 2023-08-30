import dataclasses
from typing import TypedDict

from wta.language_models.spacy import SpacyModel
from wta.pipeline.sentence_histories.text_unit import SPSF, TextUnitType
from wta.settings import Settings

_GRAMMAR = {
    "de": ["GRAMMAR"],
    "fr": ["CAT_GRAMMAIRE", "AGREEMENT", "CAT_HOMONYMES_PARONYMES"],
}
_MECHANICS = {
    "de": ["TYPOS", "CASING", "HILFESTELLUNG_KOMMASETZUNG"],
    "fr": [
        "TYPOS",
        "CAT_TYPOGRAPHIE",
        "CAT_ELISION",
        "CASING",
        "CAT_MAJUSCULES",
        "PUNCTUATION",
    ],
}


class SenhoodDict(TypedDict):
    text: str
    mech_completeness: bool
    con_completeness: bool
    syn_completeness: bool
    mech_correctness: bool
    gram_correctness: bool


@dataclasses.dataclass(frozen=True)
class Sentencehood:
    """
    Sentencehood comprises five attributes of a text unit:
    - mechanical completeness
    - conceptual completeness
    - syntactic completeness
    - mechanical correctness
    - grammatical correctness
    """

    text: str
    mech_completeness: bool
    con_completeness: bool
    syn_completeness: bool
    mech_correctness: bool
    gram_correctness: bool

    def to_dict(self) -> SenhoodDict:
        return {
            "text": self.text,
            "mech_completeness": self.mech_completeness,
            "con_completeness": self.con_completeness,
            "syn_completeness": self.syn_completeness,
            "mech_correctness": self.mech_correctness,
            "gram_correctness": self.gram_correctness,
        }


class SentencehoodEvaluator:
    def run(
        self,
        sentence_history: dict[int, list[SPSF]],
        nlp_model: SpacyModel,
        settings: Settings,
    ) -> tuple[dict[int, list[Sentencehood]], dict[str, set[str]]]:
        sentencehood_history: dict[int, list[Sentencehood]] = {}
        error_details: dict[str, set[str]] = {}
        for sen_id, spsf_list in sentence_history.items():
            spsf_sentencehood_list = []
            for i, spsf in enumerate(spsf_list):
                mech_completeness = spsf.text_unit_type == TextUnitType.SEN
                con_completeness = (
                    True
                    if i == len(spsf_list) - 1
                    else spsf_list[i + 1].tpsf_id > spsf.tpsf_id + 1
                )
                tagged_spsf = nlp_model.nlp(spsf.text)
                syn_data: list[tuple[str, str]] = []
                syn_data = [(token.pos_, token.dep_) for token in tagged_spsf]
                syn_completeness = bool(
                    (("VERB", "ROOT") in syn_data or ("AUX", "ROOT") in syn_data)
                    and (("NOUN", "sb") in syn_data or ("PRON", "sb") in syn_data)
                )
                errors = nlp_model.tool.check(spsf.text)
                error_types = {e.category for e in errors}
                for e in errors:
                    if e.category not in error_details.keys():
                        error_details[e.category] = set(
                            spsf.text[e.offset : e.offset + e.errorLength]
                        )
                    else:
                        error_details[e.category].add(
                            spsf.text[e.offset : e.offset + e.errorLength]
                        )
                grammatical_errors = [
                    err
                    for err in _GRAMMAR[settings.config["language"]]
                    if err in error_types
                ]
                gramm_correctness = bool(grammatical_errors == [])
                mechanical_errors = [
                    err
                    for err in _MECHANICS[settings.config["language"]]
                    if err in error_types
                ]
                mech_correctness = bool(mech_completeness and mechanical_errors == [])
                sentencehood = Sentencehood(
                    text=spsf.text,
                    mech_completeness=mech_completeness,
                    con_completeness=con_completeness,
                    syn_completeness=syn_completeness,
                    mech_correctness=mech_correctness,
                    gram_correctness=gramm_correctness,
                )
                spsf_sentencehood_list.append(sentencehood)
            sentencehood_history[sen_id] = spsf_sentencehood_list
        return sentencehood_history, error_details
