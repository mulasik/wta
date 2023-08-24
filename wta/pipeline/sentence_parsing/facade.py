from ..sentence_histories.text_unit import SPSF, TextUnit
from .models import Parsers
from .parsers import BaseParserAdapter, DiaParser, TokenProp


class ParsingFacade:
    def __init__(
        self,
        senhis: dict[int, list[SPSF]],
        parser_name: str,
        lang: str,
        grammar: str,
    ) -> None:
        self.parser_lst = {
            Parsers.DIAPARSER: DiaParser,
        }
        self.senhis = senhis
        self.grammar = grammar
        self.parser = self._create_parser(parser_name, lang)
        self.senhis_parses: dict[int, list[list[TokenProp] | None]] | None = None

    def _create_parser(self, parser_name: str, lang: str) -> BaseParserAdapter:
        return self.parser_lst[parser_name](lang, self.grammar)

    def run(self) -> None:
        print(f"Running {self.grammar} parsing on {len(self.senhis)} sentences...")
        senhis_sentexts = self._extract_sentexts()
        self.senhis_parses = self.parser.predict(senhis_sentexts)

    def _extract_sentexts(self) -> dict[int, list[str]]:
        senhist_sentexts = {}
        for sen_id, single_senhis in self.senhis.items():
            senhist_sentexts[sen_id] = [sen.text for sen in single_senhis if sen.text]
        return senhist_sentexts
