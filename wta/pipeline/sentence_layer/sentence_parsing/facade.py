
from wta.pipeline.sentence_layer.sentence_histories.sentence_history import SentenceHistory

from .models import Parsers
from .parsers import BaseParserAdapter, Spacy, TokenProp

PARSER_LST = {
    Parsers.SPACY: Spacy
}

class ParsingFacade:

    def _create_parser(self, parser_name: str, lang: str, grammar: str) -> BaseParserAdapter:
        print(f"Creating parser {PARSER_LST[parser_name]}")
        return PARSER_LST[parser_name](lang, grammar)

    def run(
            self,
            senhis: list[SentenceHistory],
            parser_name: str,
            lang: str,
            grammar: str) -> dict[int, list[list[TokenProp]]]:
        parser = self._create_parser(parser_name, lang, grammar)
        print(f"Running {grammar} parsing on {len(senhis)} sentences...")
        senhis_sentexts = self._extract_sentexts(senhis)
        return parser.predict(senhis_sentexts)

    def _extract_sentexts(self, senhis: list[SentenceHistory]) -> dict[int, list[str]]:
        senhist_sentexts = {}
        for sh in senhis:
            senhist_sentexts[sh.sen_id] = [sen.text for sen in sh.senversions if sen.text]
        return senhist_sentexts
