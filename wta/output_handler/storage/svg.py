import os

import paths
import settings
from wta.output_handler.names import Names


class Svg:

    def __init__(self, plot, filepath):
        self.plot = plot
        self.filepath = filepath

    def to_svg(self):
        self.plot.savefig(self.filepath, bbox_inches='tight')
        self.plot.close()


class TexthisSvg(Svg):

    def __init__(self, plot, filtered=False):
        filtered = '' if not filtered else '_filtered'
        filepath = os.path.join(paths.texthis_visual_dir, f'{settings.filename}_{Names.TEXTHIS}_{Names.VISUAL}{filtered}.svg')
        super().__init__(plot, filepath)


class SenhisSvg(Svg):

    def __init__(self, plot, filtered=False):
        filtered = '' if not filtered else '_filtered'
        filepath = os.path.join(paths.senhis_visual_dir, f'{settings.filename}_{Names.SENHIS}_{Names.VISUAL}{filtered}.svg')
        super().__init__(plot, filepath)

