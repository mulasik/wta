from wta.pipeline.sentence_parsing.parsers import Supar

from .models import Parsers


class ParsingFacade:
    def __init__(self, senhis: dict, parser_name: str, lang: str, grammar: str):
        self.parser_lst = {
            Parsers.SUPAR: Supar,
        }
        self.senhis = senhis
        self.grammar = grammar
        self.parser = self._create_parser(parser_name, lang)
        self.senhis_parses = None

    def _create_parser(self, parser_name: str, lang: str):
        return self.parser_lst[parser_name](lang, self.grammar)

    def run(self):
        print(f"Running {self.grammar} parsing on {len(self.senhis)} sentences...")
        senhis_sentexts = self._extract_sentexts()
        self.senhis_parses = self.parser.predict(senhis_sentexts)

    def _extract_sentexts(self):
        senhist_sentexts = {}
        for sen_id, single_senhis in self.senhis.items():
            senhist_sentexts[sen_id] = [
                sen.content for sen in single_senhis if sen.content
            ]
        return senhist_sentexts
