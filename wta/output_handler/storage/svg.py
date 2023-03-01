from pathlib import Path

import matplotlib.pyplot as plt

import paths
import settings

from ...pipeline.sentence_histories.text_unit import TextUnit
from ...pipeline.text_history.tpsf import TpsfECM
from ...pipeline.transformation_histories.transformation import Transformation
from ..names import Names
from ..plots.senhis_plot import SenhisPlot
from ..plots.stats_plot import (
    DeletionsPlot,
    InsertionsPlot,
    SenEditPlot,
    TsLabelsPlot,
    TsTokensPlot,
)
from ..plots.texthis_plot import FilteredTexthisPlot, TexthisPlot
from ..plots.transhis_plot import (
    ConstTranshisPlot,
    DepTranshisPlot,
    SynBarTranshisPlot,
    SynPieTranshisPlot,
)
from .base import BaseStorage


class Svg(BaseStorage):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def to_file(self) -> None:
        plt.savefig(str(self.filepath), bbox_inches="tight")
        plt.close()


class TexthisSvg(Svg):
    def __init__(self, texthis: list[TpsfECM]) -> None:
        self.preprocess_data(texthis)
        super().__init__(
            paths.texthis_visual_dir
            / f"{settings.filename}_{Names.TEXTHIS}_{Names.VISUAL}.svg"
        )

    def preprocess_data(self, texthis: list[TpsfECM]) -> None:
        TexthisPlot(texthis).run()


class FilteredTexthisSvg(Svg):
    def __init__(self, texthis_fltr: list[TpsfECM]) -> None:
        self.preprocess_data(texthis_fltr)
        super().__init__(
            paths.texthis_visual_dir
            / f"{settings.filename}_{Names.TEXTHIS}_{Names.VISUAL}_filtered.svg"
        )

    def preprocess_data(self, texthis_fltr: list[TpsfECM]) -> None:
        FilteredTexthisPlot(texthis_fltr).run()


class SenhisSvg(Svg):
    def __init__(
        self,
        texthis: list[TpsfECM],
        senhis: dict[int, list[TextUnit]],
        filtered: bool = False,
    ) -> None:
        self.preprocess_data(texthis, senhis)
        filtered_lbl = "_filtered" if filtered else ""
        super().__init__(
            paths.senhis_visual_dir
            / f"{settings.filename}_{Names.SENHIS}_{Names.VISUAL}{filtered_lbl}.svg"
        )

    def preprocess_data(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        SenhisPlot(texthis, senhis).run()


class DepTranshisSvg(Svg):
    def __init__(self, dep_transhis: dict[int, list[Transformation]]) -> None:
        self.preprocess_data(dep_transhis)
        super().__init__(
            paths.dependency_transhis_dir
            / f"{settings.filename}_{Names.TRANSHIS}_{Names.DEP}_{Names.VISUAL}.svg"
        )

    def preprocess_data(self, dep_transhis: dict[int, list[Transformation]]) -> None:
        DepTranshisPlot(dep_transhis).run()


class ConstTranshisSvg(Svg):
    def __init__(self, const_transhis: dict[int, list[Transformation]]) -> None:
        self.preprocess_data(const_transhis)
        super().__init__(
            paths.constituency_transhis_dir
            / f"{settings.filename}_{Names.TRANSHIS}_{Names.CONST}_{Names.VISUAL}.svg"
        )

    def preprocess_data(self, const_transhis: dict[int, list[Transformation]]) -> None:
        ConstTranshisPlot(const_transhis).run()


class SynBarTranshisSvg(Svg):
    def __init__(
        self,
        dep_transhis: dict[int, list[Transformation]],
        const_transhis: dict[int, list[Transformation]],
    ) -> None:
        self.preprocess_data(dep_transhis, const_transhis)
        super().__init__(
            paths.transhis_dir
            / f"{settings.filename}_syntactic_impact_{Names.VISUAL}_bar.svg"
        )

    def preprocess_data(
        self,
        dep_transhis: dict[int, list[Transformation]],
        const_transhis: dict[int, list[Transformation]],
    ) -> None:
        SynBarTranshisPlot(dep_transhis, const_transhis).run()


class SynPieTranshisSvg(Svg):
    def __init__(
        self,
        dep_transhis: dict[int, list[Transformation]],
        const_transhis: dict[int, list[Transformation]],
    ) -> None:
        self.preprocess_data(dep_transhis, const_transhis)
        super().__init__(
            paths.transhis_dir
            / f"{settings.filename}_syntactic_impact_{Names.VISUAL}_pie.svg"
        )

    def preprocess_data(
        self,
        dep_transhis: dict[int, list[Transformation]],
        const_transhis: dict[int, list[Transformation]],
    ) -> None:
        SynPieTranshisPlot(dep_transhis, const_transhis).run()


class SenEditSvg(Svg):
    def __init__(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        self.preprocess_data(texthis, senhis)
        super().__init__(
            paths.stats_dir / f"{settings.filename}_sentence_edits_stats.svg"
        )

    def preprocess_data(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        SenEditPlot(texthis, senhis).run()


class TsLabelsSvg(Svg):
    def __init__(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        self.preprocess_data(texthis, senhis)
        super().__init__(paths.stats_dir / f"{settings.filename}_ts_labels_stats.svg")

    def preprocess_data(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        TsLabelsPlot(texthis, senhis).run()


class TsTokensSvg(Svg):
    def __init__(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        self.preprocess_data(texthis, senhis)
        super().__init__(paths.stats_dir / f"{settings.filename}_ts_tokens_stats.svg")

    def preprocess_data(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        TsTokensPlot(texthis, senhis).run()


class DeletionsSvg(Svg):
    def __init__(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        self.preprocess_data(texthis, senhis)
        super().__init__(paths.stats_dir / f"{settings.filename}_deletions_stats.svg")

    def preprocess_data(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        DeletionsPlot(texthis, senhis).run()


class InsertionsSvg(Svg):
    def __init__(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        self.preprocess_data(texthis, senhis)
        super().__init__(paths.stats_dir / f"{settings.filename}_insertions_stats.svg")

    def preprocess_data(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        InsertionsPlot(texthis, senhis).run()
