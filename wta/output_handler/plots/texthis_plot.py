import matplotlib.pyplot as plt

import settings
from wta.output_handler.plots.colors import Colors


class TexthisPlot:

    def __init__(self, texthis):
        self.output_directory = settings.config['output_dir']
        self.filename = settings.filename
        self.filtered = ''
        self.texthis_to_visualise = [tpsf for tpsf in texthis if (
                len(tpsf.new_sentences) > 0
                or len(tpsf.modified_sentences) > 0
                or len(tpsf.deleted_sentences) > 0)]

    def plot_data(self):

        sentences_lengths = {}
        for tpsf in self.texthis_to_visualise:
            sentences_lens = []
            # transformation = 'insertion' if tpsf.transforming_sequence.label == 'append' else tpsf.transforming_sequence.label
            for s in tpsf.sentence_list:
                if s.text in [sen.text for sen in tpsf.unchanged_sentences]:
                    label = 'unchanged'
                elif s.text in [sen.text for sen in tpsf.new_sentences]:
                    label = 'new'
                elif s.text in [sen.text for sen in tpsf.modified_sentences]:
                    label = f'modified through {tpsf.transforming_sequence.label}'
                elif s.text in [sen.text for sen in tpsf.deleted_sentences]:
                    label = 'deleted'
                sentences_lens.append((label, len(s.text)))
            sentences_lengths.update({tpsf.revision_id: sentences_lens})

        min_fig_heigth = 15

        tpsf_labels = []
        for key in sentences_lengths.keys():
            text = f'TPSF {key}'
            tpsf_labels.append(text)

        fig_height = len(self.texthis_to_visualise) * 0.80 if len(self.texthis_to_visualise) > 15 else min_fig_heigth
        fig_width = fig_height * 0.8
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(fig_width, fig_height), gridspec_kw={'width_ratios': [4, 1]})

        plt.yticks(ticks=list(sentences_lengths.keys()), labels=tpsf_labels)

        ax1.set_ylim(len(sentences_lengths) + 1, -1)
        ax1.tick_params(axis='both', which='major', labelsize=7)

        ax2.set_ylim(len(sentences_lengths) + 1, -1)
        ax2.tick_params(axis='both', which='major', labelsize=7)

        ax1.label_outer()
        ax2.label_outer()

        for id, sens in sentences_lengths.items():
            starts = 0
            for s in sens:
                lbl = f'{s[0]} sentences' if s[0] in ['new', 'deleted', 'unchanged'] else f'sentences {s[0]}'
                ax1.barh(str(id), s[1], left=starts, height=1, color=Colors.SEN_COLORS[s[0]], edgecolor='white', label=lbl)
                starts += s[1]

        for tpsf in self.texthis_to_visualise:
            # lbl = 'insertion' if tpsf.transforming_sequence.label == 'append' else tpsf.transforming_sequence.label
            lbl = tpsf.transforming_sequence.label
            transforming_seq_text = tpsf.transforming_sequence.text
            ax2.barh(str(tpsf.revision_id), len(transforming_seq_text), left=0, height=1, label=lbl, color=Colors.TS_COLORS[lbl], edgecolor='white')

        ax1.set_xlabel('Number of characters')
        ax2.set_xlabel('Number of characters')
        ax1.set_title('Text History', pad=5)
        ax2.set_title('Transforming sequence', pad=5)

        # legend:
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

        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.4, wspace=0.02)

        return plt


class FilteredTexthisPlot(TexthisPlot):

    def __init__(self, texthis):
        super().__init__(texthis)
        self.filtered = '_filtered'

    def plot_data(self):
        sentences_lengths = {}
        for tpsf in self.texthis_to_visualise:
            sentences_lens = []
            if not tpsf.sentence_list:
                label = 'deleted'
                sentences_lens.append((label, len(s.text)))
            else:
                for s in tpsf.sentence_list:
                    if s.text in [sen.text for sen in tpsf.unchanged_sentences]:
                        label = 'unchanged'
                    elif s.text in [sen.text for sen in tpsf.new_sentences]:
                        label = 'new'
                    elif s.text in [sen.text for sen in tpsf.modified_sentences]:
                        label = f'modified through {tpsf.transforming_sequence.label}'
                    elif s.text in [sen.text for sen in tpsf.deleted_sentences]:
                        label = 'deleted'
                    sentences_lens.append((label, len(s.text)))
            sentences_lengths.update({tpsf.revision_id: sentences_lens})

        min_fig_heigth = 15

        tpsf_labels = []
        for key in sentences_lengths.keys():
            text = f'TPSF {key}'
            tpsf_labels.append(text)

        fig_height = len(self.texthis_to_visualise) * 0.8 if len(self.texthis_to_visualise) > 15 else min_fig_heigth
        fig_width = fig_height * 0.8
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(fig_width, fig_height),
                                       gridspec_kw={'width_ratios': [5, 3]})

        plt.yticks(ticks=list(sentences_lengths.keys()), labels=tpsf_labels)

        ax1.set_ylim(len(sentences_lengths) + 1, -1)
        ax1.tick_params(axis='both', which='major', labelsize=7)

        ax2.set_ylim(len(sentences_lengths) + 1, -1)
        ax2.tick_params(axis='y', which='major', labelsize=7)
        ax2.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off

        ax1.label_outer()
        ax2.label_outer()

        for id, sens in sentences_lengths.items():
            starts = 0
            for s in sens:
                lbl = f'{s[0]} sentences' if s[0] in ['new', 'deleted', 'unchanged'] else f'sentences {s[0]}'
                ax1.barh(str(id), s[1], left=starts, height=1, color=Colors.SEN_COLORS[s[0]], edgecolor='white',
                         label=lbl)
                starts += s[1]

        ypos = 0
        for tpsf in self.texthis_to_visualise:
            transforming_sequences = tpsf.irrelevant_ts_aggregated
            starts = 0
            for ts in transforming_sequences:
                # lbl = 'insertion' if ts[1] == 'append' else ts[1]
                lbl = ts[1]
                if lbl == 'insertion':
                    bar_lbl = 'ins'
                elif lbl == 'append':
                    bar_lbl = 'app'
                elif lbl == 'deletion':
                    bar_lbl = 'del'
                else:
                    print(
                        f'Attention. Label undefined for the following transforming sequence: {ts}. The transforming sequence will not be visible in the visualisation.')
                transforming_seq_len = 2
                ax2.barh(str(tpsf.revision_id), transforming_seq_len, left=starts, height=1,
                         color=Colors.TS_COLORS[lbl], edgecolor='white', label=lbl)  # label=lbl,
                ax2.text(s=bar_lbl, x=1 + starts, y=ypos, color="w", verticalalignment="center",
                         horizontalalignment="center", size=10)
                starts += transforming_seq_len
            ypos += 1

        ax1.set_xlabel('Number of characters')
        # ax2.set_xlabel('Edit operations sequence')
        ax1.set_title('Filtered Text History', pad=5)
        ax2.set_title('Preceding\n Edit Operations\n Sequence', pad=5)

        # legend:
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

        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.4, wspace=0.02)
        return plt