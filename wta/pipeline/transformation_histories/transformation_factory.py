import re

import tqdm

from ..sentence_parsing.parsers import TokenProp
from .transformation import (
    ConstituencyTransformation,
    DependencyTransformation,
    Transformation,
)


class TransformationFactory:
    def __init__(
        self, senhis_parses: dict[int, list[list[TokenProp]]], grammar: str
    ) -> None:
        self.senhis_parses = senhis_parses
        self.grammar = grammar
        self.transhis: dict[int, list[Transformation]] = {}
        self.identify_transformations()

    def identify_transformations(self) -> None:
        pass


class DependencyTransformationFactory(TransformationFactory):
    def __init__(self, parsed_senhis: dict[int, list[list[TokenProp]]]) -> None:
        super().__init__(parsed_senhis, "dependency")

    def identify_transformations(self) -> None:
        sen_dependency_transformations: list[Transformation] = []
        progress = tqdm.tqdm(
            self.senhis_parses.items(), "Generating dependency transformation histories"
        )
        for sen_id, sgl_senhis_parses in progress:
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                if senver_id > 0:
                    prev_senver_id = senver_id - 1
                    prev_parsed_sen = sgl_senhis_parses[prev_senver_id]
                    for i, word in enumerate(parsed_sen):
                        try:
                            # the dependency relation has changed
                            prev_word = sgl_senhis_parses[senver_id - 1][i]
                            prev_word_deps = (
                                prev_word["id"],
                                prev_word["head"],
                                prev_word["dep_rel"],
                            )
                            word_deps = (word["id"], word["head"], word["dep_rel"])
                            if word_deps != prev_word_deps:
                                dep_impacted = True
                            else:
                                dep_impacted = False
                                word_modified = word["word"] != prev_word["word"]
                        # the tree has been extended
                        except IndexError:
                            dep_impacted = True
                    if dep_impacted or word_modified:
                        trans = DependencyTransformation(
                            senver_id,
                            str(parsed_sen),
                            prev_senver_id,
                            str(prev_parsed_sen),
                            dep_impacted,
                            word_modified,
                        )
                        sen_dependency_transformations.append(trans)
            if sen_dependency_transformations:
                self.transhis[sen_id] = sen_dependency_transformations


_WO_TOKENS_RE = re.compile(r"\(_ [A-ZÜÖÄa-züöä]+\)")


class ConsituencyTransformationFactory(TransformationFactory):
    def __init__(self, parsed_senhis: dict[int, list[list[TokenProp]]]) -> None:
        super().__init__(parsed_senhis, "constituency")

    def identify_transformations(self) -> None:
        progress = tqdm.tqdm(
            self.senhis_parses.items(),
            "Generating constituency transformation histories",
        )
        constituency_transformations: list[Transformation] = []
        for sen_id, sgl_senhis_parses in progress:
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                parse_wo_tokens = _WO_TOKENS_RE.sub("()", str(parsed_sen))
                if senver_id > 0:
                    prev_senver_id = senver_id - 1
                    prev_parsed_sen = sgl_senhis_parses[prev_senver_id]
                    prev_parse_wo_tokens = _WO_TOKENS_RE.sub("()", str(prev_parsed_sen))
                    try:
                        # the constituents have changed
                        const_impacted = parse_wo_tokens != prev_parse_wo_tokens
                    # the tree has been extended
                    except IndexError:
                        const_impacted = True
                    if const_impacted:
                        const = ConstituencyTransformation(
                            senver_id,
                            str(parsed_sen),
                            senver_id - 1,
                            str(prev_parsed_sen),
                            const_impacted,
                        )
                        constituency_transformations.append(const)
            if constituency_transformations:
                self.transhis[sen_id] = constituency_transformations
