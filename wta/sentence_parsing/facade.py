from wta.sentence_parsing.parsers import Supar
from wta.sentence_parsing.models import Parsers


class ParsingFacade:

    def __init__(self, senhis: dict, parser_name: str, lang: str, grammar: str):
        self.senhis = senhis
        self.grammar = grammar
        self.parser = self.create_parser(parser_name, lang)
        self.senhis_parses = None

    def create_parser(self, parser_name: str, lang: str):
        if parser_name == Parsers.SUPAR:
            return Supar(lang, self.grammar)

    def run(self):
        print(f'Running {self.grammar} parsing on {len(self.senhis)} sentences...')
        senhis_sentexts = self.extract_sentexts()
        self.senhis_parses = self.parser.predict(senhis_sentexts)

    def extract_sentexts(self):
        senhist_sentexts = {}
        for sen_id, single_senhis in self.senhis.items():
            senhist_sentexts[sen_id] = [sen.text for sen in single_senhis if sen.text]
        return senhist_sentexts

