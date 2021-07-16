import matplotlib.pyplot as plt
import matplotlib.colors as pltc
import os


class Visualisation:

    def __init__(self, output_directory, file_name, filtered=''):
        self.output_directory = output_directory
        self.file_name = file_name
        self.filtered = filtered

    def visualise_text_history(self, tpsfs_to_visualise):

        sentences_lengths = {}
        for tpsf in tpsfs_to_visualise:
            sentences_lens = []
            transformation = 'insertion' if tpsf.transforming_sequence.label == 'append' else tpsf.transforming_sequence.label
            for s in tpsf.sentence_list:
                if s.text in [sen.text for sen in tpsf.unchanged_sentences]:
                    label = 'unchanged'
                elif s.text in [sen.text for sen in tpsf.new_sentences]:
                    label = 'new'
                elif s.text in [sen.text for sen in tpsf.modified_sentences]:
                    label = f'modified through {transformation}'
                elif s.text in [sen.text for sen in tpsf.deleted_sentences]:
                    label = 'deleted'
                sentences_lens.append((label, len(s.text)))
            sentences_lengths.update({tpsf.revision_id: sentences_lens})

        sentence_colors = {
            'unchanged': 'mistyrose',
            'new': 'darkslategrey',
            'modified through insertion': 'cadetblue',
            'modified through deletion': 'lightcoral',
            'deleted': 'indianred'
        }

        transforming_colors = {
            'deletion': 'indianred',
            'insertion': 'darkslategrey',
        }

        min_fig_heigth = 15

        tpsf_labels = []
        for key in sentences_lengths.keys():
            text = f'TPSF {key}'
            tpsf_labels.append(text)

        fig_height = len(tpsfs_to_visualise) * 0.80 if len(tpsfs_to_visualise) > 15 else min_fig_heigth
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
                ax1.barh(str(id), s[1], left=starts, height=1, color=sentence_colors[s[0]], edgecolor='white', label=lbl)
                starts += s[1]

        for tpsf in tpsfs_to_visualise:
            lbl = 'insertion' if tpsf.transforming_sequence.label == 'append' else tpsf.transforming_sequence.label
            transforming_seq_text = tpsf.transforming_sequence.text
            ax2.barh(str(tpsf.revision_id), len(transforming_seq_text), left=0, height=1, label=lbl, color=transforming_colors[lbl], edgecolor='white')

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
        fig_file = os.path.join(self.output_directory, f'{self.file_name}_text_history_visualisation{self.filtered}.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def visualise_sentence_history(self, tpsfs_to_visualise, sentence_history):

        unrecommended_colors = ['white', 'snow', 'whitesmoke', 'seashell', 'antiquewhite', 'oldlace', 'floralwhite',
                                'cornsilk',
                                'ivory', 'honeydew', 'aliceblue', 'mintcream', 'azure', 'ghostwhite', 'lavenderblush',
                                'beige', 'bisque', 'black']
        available_colors = [k for k, v in pltc.cnames.items() if k not in unrecommended_colors]

        sen_colors = {}
        for id, sen_id in enumerate(list(sentence_history.keys())):
            sen_colors.update({sen_id: available_colors[id]})

        tpsf_sentences = {}
        for tpsf in tpsfs_to_visualise:
            tpsf_sens = []
            for id, sen in enumerate(tpsf.sentence_list):
                for sen_id, sen_list in sentence_history.items():
                    if sen.text.strip() in [s.text for s in sen_list] and sen.text.strip() not in [s[2] for s in tpsf_sens]:
                        sen_color = available_colors[int(id)]
                        tpsf_sens.append((len(sen.text), sen_color, sen.text))
                if sen.text.strip() not in [s[2] for s in tpsf_sens]:
                    tpsf_sens.append((len(sen.text), 'beige', sen.text))
            tpsf_sentences.update({tpsf.revision_id: tpsf_sens})

        tpsf_labels = []
        for key in tpsf_sentences.keys():
            text = f'TPSF {key}'
            tpsf_labels.append(text)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 20))
        ax1.set_ylim(len(tpsf_sentences) + 1, -1)
        ax1.tick_params(axis='both', which='major', labelsize=7)
        ax1.set_title('Sentence History', pad=5)

        for id, sens in tpsf_sentences.items():
            a1_starts = 0
            for s in sens:
                ax1.barh(f'TPSF {id}', s[0], left=a1_starts, height=1, color=s[1], edgecolor='white', alpha=0.7)
                a1_starts += s[0]

        last_tpsf_id = list(tpsf_sentences.keys())[-1]
        ax2.set_title(f'Last Sentence Versions (TPSF {last_tpsf_id}):', pad=5, horizontalalignment='left')
        ax2.axis('off')
        last_sen_versions = tpsf_sentences[last_tpsf_id]
        a2_starts = 0.95
        for s in last_sen_versions:
            a2_starts -= 0.01
            ax2.text(0, a2_starts, s[2].strip(), wrap=True, size=7, bbox={'facecolor': s[1], 'alpha': 0.6, 'pad': 2})
            a2_starts -= 0.01

        ax1.set_xlabel('Number of characters')

        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.4, wspace=0.01)
        plt.tight_layout()
        fig_file = os.path.join(self.output_directory, f'{self.file_name}_sentence_history_visualisation{self.filtered}.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

