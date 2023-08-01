import dataclasses
from wta.language_models.spacy import SpacyModel

from wta.pipeline.sentence_histories.text_unit import SentenceVersion, TextUnit, TextUnitType


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



class SentencehoodEvaluator:
    def run(self, sentence_history: dict[int, list[SentenceVersion]], nlp_model: SpacyModel) -> dict[int, list[Sentencehood]]:
        sentencehood_history: dict[int, list[Sentencehood]] = {}
        for sen_id, spsf_list in sentence_history.items():
            spsf_sentencehood_list = []
            for i, spsf in enumerate(spsf_list):
                mech_completeness = spsf.text_unit_type == TextUnitType.SEN
                con_completeness = True if i == len(spsf_list) - 1 else spsf_list[i + 1].tpsf_id > spsf.tpsf_id + 1
                tagged_spsf = nlp_model.nlp(spsf.text)
                syn_data: list[tuple[str, str]] = []
                syn_data = [(token.pos_, token.dep_) for token in tagged_spsf]
                syn_completeness = bool(
                    (("VERB", "ROOT") in syn_data or ("AUX", "ROOT") in syn_data)
                    and (("NOUN", "sb") in syn_data or ("PRON", "sb") in syn_data))
                errors = nlp_model.tool.check(spsf.text)
                error_types = {e.category for e in errors}
                gramm_correctness = bool("GRAMMAR" not in error_types)
                mech_correctness = bool(
                    mech_completeness
                    and "TYPOS" not in error_types
                    and "CASING" not in error_types
                    and "HILFESTELLUNG_KOMMASETZUNG" not in error_types)
                sentencehood = Sentencehood(
                    text=spsf.text,
                    mech_completeness=mech_completeness,
                    con_completeness=con_completeness,
                    syn_completeness=syn_completeness,
                    mech_correctness=mech_correctness,
                    gram_correctness=gramm_correctness
                    )
                spsf_sentencehood_list.append(sentencehood)
            sentencehood_history[sen_id] = spsf_sentencehood_list
        return sentencehood_history

