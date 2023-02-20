import matplotlib.pyplot as plt

import settings
from ..plots.colors import Colors
from .base import BasePlot
from ...pipeline.names import SenLabels


class TexthisPlot(BasePlot):

    def __init__(self, texthis):
        self.texthis = texthis
        self.sen_lengths = self.preprocess_data()
        self.filtered = ''

    def preprocess_data(self):
        sentences_lengths = {}
        for tpsf in self.texthis:
            sentences_lens = []
            for tu, tu_state in zip(tpsf.textunits, tpsf.tus_states):
                if tu_state == SenLabels.MOD:
                    label = f'modified through {tpsf.ts.label}'
                else:
                    label = tu_state
                sentences_lens.append((label, len(tu.text)))
            sentences_lengths.update({tpsf.revision_id: sentences_lens})
        return sentences_lengths

    def create_figure(self):
        min_fig_heigth = 15
        tpsf_labels = []
        for key in self.sen_lengths.keys():
            text = f'TPSF {key}'
            tpsf_labels.append(text)
        fig_height = len(self.texthis) * 0.80 if len(self.texthis) > 15 else min_fig_heigth
        fig_width = fig_height * 0.8
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(fig_width, fig_height),
                                       gridspec_kw={'width_ratios': [4, 1]})
        plt.yticks(ticks=list(range(0, len(tpsf_labels))), labels=tpsf_labels)
        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.4, wspace=0.02)

        ax1.set_title('Text History', pad=5)
        ax1.set_ylim(len(self.sen_lengths) + 1, -1)
        ax1.tick_params(axis='both', which='major', labelsize=7)
        ax1.label_outer()
        ax1.set_xlabel('Number of characters')

        ax2.set_title('Transforming sequence', pad=5)
        ax2.set_ylim(len(self.sen_lengths) + 1, -1)
        ax2.tick_params(axis='both', which='major', labelsize=7)
        ax2.label_outer()
        ax2.set_xlabel('Number of characters')

        return ax1, ax2

    def plot_data(self, ax1, ax2):
        for id, sens in self.sen_lengths.items():
            starts = 0
            for s in sens:
                lbl = f'{s[0]} text units' if s[0] in ['new', 'deleted', 'unchanged_pre', 'unchanged_post'] else f'text units {s[0]}'
                ax1.barh(str(id), s[1], left=starts, height=1, color=Colors.SEN_COLORS[s[0]], edgecolor='white', label=lbl)
                starts += s[1]
        for tpsf in self.texthis:
            lbl = tpsf.ts.label
            ts_text_len = len(tpsf.ts.text)  # tpsf.ts.rplcmt_textlen if tpsf.ts.label == 'replacement'
            ax2.barh(str(tpsf.revision_id), ts_text_len, left=0, height=1, label=lbl, color=Colors.TS_COLORS[lbl], edgecolor='white')

    def set_legend(self, ax1, ax2):
        hand, labl = ax1.get_legend_handles_labels()
        handout = []
        lablout = []
        for h, l in zip(hand, labl):
            if l not in lablout:
                lablout.append(l)
                handout.append(h)
        ax1.legend(handout, lablout, loc="upper right")

        hand2, labl2 = ax2.get_legend_handles_labels()
        handout2 = []
        lablout2 = []
        for h2, l2 in zip(hand2, labl2):
            if l2 not in lablout2:
                lablout2.append(l2)
                handout2.append(h2)
        ax2.legend(handout2, lablout2, loc="upper right")

    def run(self):
        ax1, ax2 = self.create_figure()
        self.plot_data(ax1, ax2)
        self.set_legend(ax1, ax2)
        return plt


class FilteredTexthisPlot(TexthisPlot):

    def __init__(self, texthis):
        super().__init__(texthis)
        self.filtered = '_filtered'

    def create_figure(self):
        min_fig_heigth = 15
        tpsf_labels = []
        for key in self.sen_lengths.keys():
            text = f'TPSF {key}'
            tpsf_labels.append(text)
        fig_height = len(self.texthis) * 0.8 if len(self.texthis) > 15 else min_fig_heigth
        fig_width = fig_height * 0.8
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(fig_width, fig_height),
                                       gridspec_kw={'width_ratios': [5, 3]})
        plt.yticks(ticks=list(range(0, len(tpsf_labels))), labels=tpsf_labels)
        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.4, wspace=0.02)

        ax1.set_title('Filtered Text History', pad=5)
        ax1.set_ylim(len(self.sen_lengths) + 1, -1)
        ax1.tick_params(axis='both', which='major', labelsize=7)
        ax1.label_outer()
        ax1.set_xlabel('Number of characters')

        ax2.set_title('Preceding\n Edit Operation Types', pad=5)
        ax2.set_ylim(len(self.sen_lengths) + 1, -1)
        ax2.tick_params(axis='y', which='major', labelsize=7)
        ax2.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        ax2.label_outer()
        # ax2.set_xlabel('Edit operations sequence')

        return ax1, ax2

    def plot_data(self, ax1, ax2):
        for id, sens in self.sen_lengths.items():
            starts = 0
            for s in sens:
                lbl = f'{s[0]} sentences' if s[0] in ['new', 'deleted', 'unchanged'] else f'sentences {s[0]}'
                ax1.barh(str(id), s[1], left=starts, height=1, color=Colors.SEN_COLORS[s[0]], edgecolor='white',
                         label=lbl)
                starts += s[1]
        ypos = 0
        for tpsf in self.texthis:
            preceding_tss = tpsf.irrelevant_tss_aggregated if tpsf.irrelevant_tss_aggregated is not None else []
            preceding_tss = [*preceding_tss, tpsf.ts]
            starts = 0
            for ts in preceding_tss:
                lbl = ts.label
                if lbl == 'insertion':
                    bar_lbl = 'ins'
                elif lbl == 'append':
                    bar_lbl = 'app'
                elif lbl == 'deletion':
                    bar_lbl = 'del'
                elif lbl == 'midletion':
                    bar_lbl = 'mid'
                elif lbl == 'replacement':
                    bar_lbl = 'rep'
                elif lbl == 'pasting':
                    bar_lbl = 'pas'
                else:
                    print(
                        f'ATTENTION: Label undefined for the following transforming sequence: {ts.sen_text}. The transforming sequence will not be visible in the visualisation.')
                ts_len = 2
                ax2.barh(str(tpsf.revision_id), ts_len, left=starts, height=1,
                         color=Colors.TS_COLORS[lbl], edgecolor='white', label=lbl)  # label=lbl,
                ax2.sen_text(s=bar_lbl, x=1 + starts, y=ypos, color="w", verticalalignment="center",
                             horizontalalignment="center", size=10)
                starts += ts_len
            ypos += 1

