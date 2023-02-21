from abc import ABC, abstractmethod

from .models import Parsers, Grammars, ModelMapping


class BaseParserAdapter(ABC):
    @abstractmethod
    def load_pipeline(self):
        pass

    @abstractmethod
    def predict(self, senhis_sentexts: dict):
        pass


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

    def __init__(self, lang: str, grammar: str):
        self.lang = lang
        self.grammar = grammar

    def load_pipeline(self):
        from supar import Parser

        model = ModelMapping.mapping[self.grammar][Parsers.SUPAR][self.lang]
        return Parser.load(model)

    def predict(self, senhis_sentexts: dict):
        pipeline = self.load_pipeline()
        senhis_parses = {}
        for sen_id, sgl_senhis_sentexts in senhis_sentexts.items():
            print(f"Processing the sentence {sen_id}...")
            senhis_parses[sen_id] = []
            for senver_id, sentext in enumerate(sgl_senhis_sentexts):
                result = pipeline.predict(
                    sentext, lang=self.lang, prob=True, verbose=False
                )
                result = self.postprocess(result)
                senhis_parses[sen_id].append(result)
                # TODO: visualise constituency trees:
                # t = Tree.fromstring(str(s_tree))
                # t.pretty_print()
                # output_file = os.path.join(self.const_trees_output_path, 'supar', f'{i}.ps')
                # ensure_path(os.path.join(self.const_trees_output_path, 'supar'))
                # TreeView(t)._cframe.print_to_file(output_file)
        return senhis_parses

    def postprocess(self, parsed_sen):
        if self.grammar == Grammars.DEP:
            tok_lst = []
            _tok_lst = [str(tok).split("\n") for tok in parsed_sen][0]
            for _tok in _tok_lst:
                _tok_props = _tok.split("\t")
                if len(_tok_props) > 1:
                    tok_props = {
                        "id": _tok_props[0],
                        "word": _tok_props[1],
                        "pos": _tok_props[3],
                        "head": _tok_props[6],
                        "dep_rel": _tok_props[7],
                    }
                    tok_lst.append(tok_props)
            return tok_lst
        if self.grammar == Grammars.CONST:
            return [s for s in parsed_sen][0]
