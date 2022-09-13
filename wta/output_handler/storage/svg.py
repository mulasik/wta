import os

import paths
from wta.output_handler.storage.names import Names


class Svg:

    def __init__(self, plot, filename):
        self.plot = plot
        self.filename = filename

    def process_senhis(self, filtered=False):
        filtered = '' if not filtered else '_filtered'
        fig_file = os.path.join(paths.senhis_visual_dir, f'{self.filename}_{Names.SENHIS}_{Names.VISUAL}{filtered}.svg')
        self.plot.savefig(fig_file, bbox_inches='tight')
        self.plot.close()

