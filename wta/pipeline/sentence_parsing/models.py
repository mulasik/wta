class Languages:
    EN = "en"
    DE = "de"
    NL = "nl"
    NO = "no"
    FR = "fr"
    GR = "gr"


class Grammars:
    DEP = "dependency"
    CONST = "constituency"


class Parsers:
    SUPAR = "supar"
    DIAPARSER = "diaparser"


class Models:
    # DEPENDENCY

    # Trained on merged 12 selected treebanks from Universal Dependencies v2.3 dataset
    # by finetuning xlm-roberta-large
    # Selected languages: de, en, nl, no, fr
    # https://pypi.org/project/supar/
    SUPAR_MULTILINGUAL_DEP_MODEL = "biaffine-dep-xlmr"
    DIAPARSER_DE_DEP_MODEL = "de_htd.dbmdz-bert-base"
    DIAPARSER_FR_DEP_MODEL = "fr_sequoia.camembert"
    DIAPARSER_EN_DEP_MODEL = "en_ptb.electra"

    # CONSTITUENCY

    # Trained on SPMRL dataset by finetuning xlm-roberta-large
    # Selected languages: de, fr
    # https://pypi.org/project/supar/
    SUPAR_MULTILINGUAL_CONST_MODEL = "crf-con-xlmr"
    SUPAR_EN_CONST_MODEL = "crf-con-en"


class ModelMapping:
    mapping = {
        Grammars.DEP: {
            Parsers.SUPAR: {
                Languages.EN: Models.SUPAR_MULTILINGUAL_DEP_MODEL,
                Languages.DE: Models.SUPAR_MULTILINGUAL_DEP_MODEL,
                Languages.NL: Models.SUPAR_MULTILINGUAL_DEP_MODEL,
                Languages.NO: Models.SUPAR_MULTILINGUAL_DEP_MODEL,
                Languages.FR: Models.SUPAR_MULTILINGUAL_DEP_MODEL,
            },
            Parsers.DIAPARSER: {
                Languages.EN: Models.DIAPARSER_EN_DEP_MODEL,
                Languages.DE: Models.DIAPARSER_DE_DEP_MODEL,
                Languages.FR: Models.DIAPARSER_FR_DEP_MODEL,
            }
        },
        Grammars.CONST: {
            Parsers.SUPAR: {
                Languages.EN: Models.SUPAR_EN_CONST_MODEL,
                Languages.DE: Models.SUPAR_MULTILINGUAL_CONST_MODEL,
                Languages.FR: Models.SUPAR_MULTILINGUAL_CONST_MODEL,
            }
        },
    }
