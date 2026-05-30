class Languages:
    EN = "en"
    DE = "de"
    FR = "fr"
    GR = "gr"


class Grammars:
    DEP = "dependency"
    CONST = "constituency"


class Parsers:
    SPACY = "Spacy"
    SUPAR = "Supar"
    DIAPARSER = "DiaParser"
    Benepar = "Benepar"


class Models:
    # DEPENDENCY PARSING
    """A transformer-based English model.
    2026: the most accurate of spaCy's standard English pipelines."""
    SPACY_EN_TRF_MODEL = "en_core_web_trf"

    # CONSTITUENCY PARSING


MODEL_MAPPING = {
    Grammars.DEP: {
        Parsers.SPACY: {
            Languages.EN: Models.SPACY_EN_TRF_MODEL
            }
        }
    }
