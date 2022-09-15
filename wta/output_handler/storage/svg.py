import os

import paths
import settings
from wta.output_handler.names import Names
from .base import BaseStorage
from ..plots.texthis_plot import TexthisPlot, FilteredTexthisPlot
from ..plots.senhis_plot import SenhisPlot
from ..plots.transhis_plot import DepTranshisPlot, ConstTranshisPlot, SynBarTranshisPlot, SynPieTranshisPlot
from ..plots.stats_plot import SenEditPlot, TsLabelsPlot, TsTokensPlot, DeletionsPlot, InsertionsPlot


class Svg(BaseStorage):

    def preprocess_data(self):
        pass

    def to_file(self):
        self.plot.savefig(self.filepath, bbox_inches='tight')
        self.plot.close()


class TexthisSvg(Svg):

    def __init__(self, texthis):
        self.plot = self.preprocess_data(texthis)
        self.filepath = os.path.join(paths.texthis_visual_dir, f'{settings.filename}_{Names.TEXTHIS}_{Names.VISUAL}.svg')

    def preprocess_data(self, texthis):
        return TexthisPlot(texthis).run()


class FilteredTexthisSvg(Svg):

    def __init__(self, texthis_fltr):
        self.plot = self.preprocess_data(texthis_fltr)
        self.filepath = os.path.join(paths.texthis_visual_dir, f'{settings.filename}_{Names.TEXTHIS}_{Names.VISUAL}_filtered.svg')

    def preprocess_data(self, texthis_fltr):
        return FilteredTexthisPlot(texthis_fltr).run()


class SenhisSvg(Svg):

    def __init__(self, texthis, senhis, filtered=False):
        self.plot = self.preprocess_data(texthis, senhis)
        filtered_lbl = '_filtered' if filtered else ''
        self.filepath = os.path.join(paths.senhis_visual_dir, f'{settings.filename}_{Names.SENHIS}_{Names.VISUAL}{filtered_lbl}.svg')

    def preprocess_data(self, texthis, senhis):
        return SenhisPlot(texthis, senhis).run()


class DepTranshisSvg(Svg):

    def __init__(self, dep_transhis):
        self.plot = self.preprocess_data(dep_transhis)
        self.filepath = os.path.join(paths.dependency_transhis_dir, f'{settings.filename}_{Names.TRANSHIS}_{Names.DEP}_{Names.VISUAL}.svg')

    def preprocess_data(self, dep_transhis):
        return DepTranshisPlot(dep_transhis).run()


class ConstTranshisSvg(Svg):

    def __init__(self, const_transhis):
        self.plot = self.preprocess_data(const_transhis)
        self.filepath = os.path.join(paths.constituency_transhis_dir, f'{settings.filename}_{Names.TRANSHIS}_{Names.CONST}_{Names.VISUAL}.svg')

    def preprocess_data(self, const_transhis):
        return ConstTranshisPlot(const_transhis).run()


class SynBarTranshisSvg(Svg):

    def __init__(self, dep_transhis, const_transhis):
        self.plot = self.preprocess_data(dep_transhis, const_transhis)
        self.filepath = os.path.join(paths.transhis_dir, f'{settings.filename}_syntactic_impact_{Names.VISUAL}_bar.svg')

    def preprocess_data(self, dep_transhis, const_transhis):
        return SynBarTranshisPlot(dep_transhis, const_transhis).run()


class SynPieTranshisSvg(Svg):

    def __init__(self, dep_transhis, const_transhis):
        self.plot = self.preprocess_data(dep_transhis, const_transhis)
        self.filepath = os.path.join(paths.transhis_dir, f'{settings.filename}_syntactic_impact_{Names.VISUAL}_pie.svg')

    def preprocess_data(self, dep_transhis, const_transhis):
        return SynPieTranshisPlot(dep_transhis, const_transhis).run()


class SenEditSvg(Svg):

    def __init__(self, texthis, senhis):
        self.plot = self.preprocess_data(texthis, senhis)
        self.filepath = os.path.join(paths.stats_dir, f'{settings.filename}_sentence_edits_stats.svg')

    def preprocess_data(self, texthis, senhis):
        return SenEditPlot(texthis, senhis).run()


class TsLabelsSvg(Svg):

    def __init__(self, texthis, senhis):
        self.plot = self.preprocess_data(texthis, senhis)
        self.filepath = os.path.join(paths.stats_dir, f'{settings.filename}_ts_labels_stats.svg')

    def preprocess_data(self, texthis, senhis):
        return TsLabelsPlot(texthis, senhis).run()


class TsTokensSvg(Svg):

    def __init__(self, texthis, senhis):
        self.plot = self.preprocess_data(texthis, senhis)
        self.filepath = os.path.join(paths.stats_dir, f'{settings.filename}_ts_tokens_stats.svg')

    def preprocess_data(self, texthis, senhis):
        return TsTokensPlot(texthis, senhis).run()


class DeletionsSvg(Svg):

    def __init__(self, texthis, senhis):
        self.plot = self.preprocess_data(texthis, senhis)
        self.filepath = os.path.join(paths.stats_dir, f'{settings.filename}_deletions_stats.svg')

    def preprocess_data(self, texthis, senhis):
        return DeletionsPlot(texthis, senhis).run()


class InsertionsSvg(Svg):

    def __init__(self, texthis, senhis):
        self.plot = self.preprocess_data(texthis, senhis)
        self.filepath = os.path.join(paths.stats_dir, f'{settings.filename}_insertions_stats.svg')

    def preprocess_data(self, texthis, senhis):
        return InsertionsPlot(texthis, senhis).run()

