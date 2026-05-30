from abc import ABC, abstractmethod
from typing import TypedDict

import spacy
from spacy.language import Language
from spacy.tokens import Doc
from tqdm import tqdm

from .models import MODEL_MAPPING, Grammars, Parsers


class TokenProp(TypedDict):
    id: int
    word: str
    pos: str
    head: int
    dep_rel: str


class BaseParserAdapter(ABC):

    @abstractmethod
    def predict(
        self, senhis_sentexts: dict[int, list[str]]
    ) -> dict[int, list[list[TokenProp]]]:
        raise NotImplementedError


class Spacy(BaseParserAdapter):

    """
    Spacy predict function returns a Doc object which contains a list of spacy.tokens.Token.
    Each token has a.o. the following properties:
        - token.i → index of token in the Doc
        - token.text → original string of the token
        - token.pos_ → coarse POS tag (e.g. "NOUN", "VERB")
        - token.head → head token in dependency tree
        - token.dep_ → dependency label
    """

    def __init__(self, lang: str, grammar: str) -> None:
        self.lang = lang
        self.grammar = grammar

    def load_pipeline(self) -> Language:
        model = MODEL_MAPPING[self.grammar][Parsers.SPACY][self.lang]
        print(f"Loading the model {model} for Spacy...")
        return spacy.load(model)

    def predict(
        self, senhis_sentexts: dict[int, list[str]]
    ) -> dict[int, list[list[TokenProp]]]:
        pipeline = self.load_pipeline()
        senhis_parses: dict[int, list[list[TokenProp]]] = {}
        prev_sentext = ""
        for sen_id, sgl_senhis_sentexts in tqdm(senhis_sentexts.items(), "Parsing SPSFs in sentence histories..."):
            senhis_parses[sen_id] = []
            for sentext in sgl_senhis_sentexts:
                if sentext != prev_sentext:
                    doc = pipeline(sentext)
                    tokens = self.postprocess(doc)
                    senhis_parses[sen_id].append(tokens)
                prev_sentext = sentext
        return senhis_parses


    def postprocess(self, parsed_sen: Doc) -> list[TokenProp]:
        if self.grammar == Grammars.DEP:
            tok_lst: list[TokenProp] = [{
                            "id": tok.i,
                            "word": tok.text,
                            "pos": tok.pos_,
                            "head": tok.head.i,
                            "dep_rel": tok.dep_,
                        } for tok in parsed_sen]
            return tok_lst
        print(f"The spaCy model integrated in THEtool doesn't support {self.grammar} parsing at the moment.")
        return []


class Benepar(BaseParserAdapter):
    """
    https://pypi.org/project/benepar/
    """

    def __init__(self, lang: str, grammar: str) -> None:
        self.lang = lang
        self.grammar = grammar


class Supar(BaseParserAdapter):
    """
    https://parser.yzhang.site
    SuPar predict function returns supar.utils.Dataset.
    dataset.sentences is a list of dataset.sentences.
    Iterating over the dataset returns supar.utils.transform.CoNLLSentence:
    1 She      ... 2 nsubj
    2 enjoys   ... 0 root
    3 playing  ... 2 xcomp
    4 tennis   ... 3 dobj
    5 .        ... 2 punct
    dataset.rels -> dependency relations:
    [['nsubj', 'root', 'xcomp', 'dobj', 'punct']]
    dataset.arcs -> head indices for each token:
    [[2, 0, 2, 3, 2]]
    """

    def __init__(self, lang: str, grammar: str) -> None:
        self.lang = lang
        self.grammar = grammar


class DiaParser(BaseParserAdapter):
    """
    https://github.com/Unipisa/diaparser
    DiaParser predict function returns diaparser.utils.data.Dataset
    Iterating over the dataset returns diaparser.utils.transform.CoNLLSentence
    CoNLLSentence has the CoNLL-X format. It is a string with tokens separated by newline:
        - ID (index in sentence, starting at 1)
        - FORM (word form itself)
        - LEMMA (word's lemma or stem)
        - CPOSTAG
        - POSTAG
        - FEAT (list of morphological features separated by |)
        - HEAD (index of syntactic parent, 0 for ROOT)
        - DEPREL (syntactic relationship between HEAD and this word)
        - PHEAD
        - PDEPREL
    E.g.
    1   The	_	_	_	_	2	det	_	_
    2	tortoise	_	_	_	_	3	nsubj	_	_
    """

    def __init__(self, lang: str, grammar: str) -> None:
        self.lang = lang
        self.grammar = grammar
