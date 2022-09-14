import os

import paths
import settings
from wta.output_handler.names import Names
from .base import BaseStorage
from ..plots.texthis_plot import TexthisPlot, FilteredTexthisPlot
from ..plots.senhis_plot import SenhisPlot


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
        return SenhisPlot(texthis, senhis).plot_data()

