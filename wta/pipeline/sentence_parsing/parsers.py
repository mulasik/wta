from abc import ABC, abstractmethod
from typing import TypedDict, cast

import diaparser
from diaparser.parsers import Parser

from .models import Grammars, ModelMapping, Parsers


class TokenProp(TypedDict):
    id: str  # noqa: A003
    word: str
    pos: str
    head: str
    dep_rel: str


class BaseParserAdapter(ABC):
    @abstractmethod
    def load_pipeline(self) -> Parser:
        pass

    @abstractmethod
    def predict(
        self, senhis_sentexts: dict[int, list[str]]
    ) -> dict[int, list[list[TokenProp] | None]]:
        raise NotImplementedError

class Supar(BaseParserAdapter):
    """
    SuPar predict function returns supar.utils.data.Dataset
    Iterating over the dataset returns supar.utils.transform.CoNLLSentence
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
    ...

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

    def load_pipeline(self) -> Parser:
        model = ModelMapping.mapping[self.grammar][Parsers.DIAPARSER][self.lang]
        return Parser.load(model)

    def predict(
        self, senhis_sentexts: dict[int, list[str]]
    ) -> dict[int, list[list[TokenProp] | None]]:
        pipeline = self.load_pipeline()
        senhis_parses: dict[int, list[list[TokenProp] | None]] = {}
        for sen_id, sgl_senhis_sentexts in senhis_sentexts.items():
            print(f"Processing the sentence {sen_id}...")
            senhis_parses[sen_id] = []
            for sentext in sgl_senhis_sentexts:
                result = pipeline.predict(
                    sentext, text=self.lang
                )
                senhis_parses[sen_id].append(self.postprocess(result))
                # TODO: visualise constituency trees:
                # t = Tree.fromstring(str(s_tree))
                # t.pretty_print()
                # output_file = os.path.join(self.const_trees_output_path, 'supar', f'{i}.ps')
                # ensure_path(os.path.join(self.const_trees_output_path, 'supar'))
                # TreeView(t)._cframe.print_to_file(output_file)
        return senhis_parses

    def postprocess(self, parsed_sen: diaparser.utils.transform.CoNLLSentence) -> list[TokenProp] | None:
        if self.grammar == Grammars.DEP:
            tok_lst: list[TokenProp] = []
            _tok_lst = [str(tok).split("\n") for tok in parsed_sen][0]
            for _tok in _tok_lst:
                _tok_props = _tok.split("\t")
                if len(_tok_props) > 1:
                    tok_lst.append(
                        {
                            "id": _tok_props[0],
                            "word": _tok_props[1],
                            "pos": _tok_props[3],
                            "head": _tok_props[6],
                            "dep_rel": _tok_props[7],
                        }
                    )
            return tok_lst
        if self.grammar == Grammars.CONST:
            return cast(list[TokenProp], list(parsed_sen)[0])
        return None

