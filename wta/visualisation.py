import matplotlib.pyplot as plt
import matplotlib.colors as pltc
import os
import numpy as np
import json


class Visualisation:

    def __init__(self, output_directory, file_name, filtered=''):
        self.output_directory = output_directory
        self.file_name = file_name
        self.filtered = filtered
        self.sentence_colors = {
            'unchanged': 'mistyrose',
            'new': 'darkslategrey',
            'deleted': 'seashell',
            'modified through deletion': 'lightcoral',
            'modified through insertion': 'cadetblue',
            'modified through append': 'teal'
        }
        self.transforming_colors = {
            'deletion': 'lightcoral',
            'insertion': 'cadetblue',
            'append': 'teal',
            '': 'w'
        }
        self.unrecommended_colors = ['white', 'snow', 'whitesmoke', 'seashell', 'antiquewhite', 'oldlace', 'floralwhite',
                                'cornsilk',
                                'ivory', 'honeydew', 'aliceblue', 'mintcream', 'azure', 'ghostwhite', 'lavenderblush',
                                'beige', 'bisque', 'black']
        self.available_colors = [k for k, v in pltc.cnames.items() if k not in self.unrecommended_colors]

    def visualise_text_history(self, tpsfs_to_visualise):

        sentences_lengths = {}
        for tpsf in tpsfs_to_visualise:
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
                ax1.barh(str(id), s[1], left=starts, height=1, color=self.sentence_colors[s[0]], edgecolor='white', label=lbl)
                starts += s[1]

        for tpsf in tpsfs_to_visualise:
            # lbl = 'insertion' if tpsf.transforming_sequence.label == 'append' else tpsf.transforming_sequence.label
            lbl = tpsf.transforming_sequence.label
            transforming_seq_text = tpsf.transforming_sequence.text
            ax2.barh(str(tpsf.revision_id), len(transforming_seq_text), left=0, height=1, label=lbl, color=self.transforming_colors[lbl], edgecolor='white')

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
        fig_file = os.path.join(self.output_directory, f'{self.file_name}_text_history', f'{self.file_name}_text_history_visualisation{self.filtered}.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def visualise_sentence_history(self, tpsfs_to_visualise, sentence_history):
        sen_colors = {}
        for id, sen_id in enumerate(list(sentence_history.keys())):
            sen_colors.update({sen_id: self.available_colors[id]})

        tpsf_sentences = {}
        for tpsf in tpsfs_to_visualise:
            tpsf_sens = []
            for id, sen in enumerate(tpsf.sentence_list):
                for sen_id, sen_list in sentence_history.items():
                    if sen.text.strip() in [s.text for s in sen_list] and sen.text.strip() not in [s[2] for s in tpsf_sens]:
                        sen_color = self.available_colors[int(id)]
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
        fig_file = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_history_visualisation{self.filtered}.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def visualise_filtered_text_history(self, tpsfs_to_visualise):
        sentences_lengths = {}
        for tpsf in tpsfs_to_visualise:
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

        fig_height = len(tpsfs_to_visualise) * 0.8  # if len(tpsfs_to_visualise) > 15 else min_fig_heigth
        fig_width = fig_height * 0.8
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(fig_width, fig_height), gridspec_kw={'width_ratios': [5, 3]})

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
                ax1.barh(str(id), s[1], left=starts, height=1, color=self.sentence_colors[s[0]], edgecolor='white', label=lbl)
                starts += s[1]

        ypos = 0
        for tpsf in tpsfs_to_visualise:
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
                    print(f'Attention. Label undefined for the following transforming sequence: {ts}. The transforming sequence will not be visible in the visualisation.')
                transforming_seq_len = 2
                ax2.barh(str(tpsf.revision_id), transforming_seq_len, left=starts, height=1, color=self.transforming_colors[lbl], edgecolor='white', label=lbl)  # label=lbl,
                ax2.text(s=bar_lbl, x=1+starts, y=ypos, color="w", verticalalignment="center", horizontalalignment="center", size=10)
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
        fig_file = os.path.join(self.output_directory, f'{self.file_name}_text_history', f'{self.file_name}_text_history_visualisation{self.filtered}.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def visualise_dependency_relations_impact(self):
        json_file_path = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_parses', 'dependency', f'{self.file_name}_dependency_relations_impact.json')
        with open(json_file_path, 'r') as f:
            dependency_relations_comparison = json.load(f)

        non_impact_edits_lst = []
        impact_edits_lst = []
        for sen_versions in dependency_relations_comparison.values():
            no_non_impact_edits, no_impact_edits = 0, 0
            for ver in sen_versions.values():
                if ver['dependency_relations_impacted'] is False:
                    no_non_impact_edits += 1
                elif ver['dependency_relations_impacted'] is True:
                    no_impact_edits += 1
            non_impact_edits_lst.append(no_non_impact_edits)
            impact_edits_lst.append(no_impact_edits)

        labels = dependency_relations_comparison.keys()

        plt.rcParams.update({'font.size': 6})
        plt.figure(figsize=(50, 25))

        x = np.arange(len(labels))  # the label locations
        width = 0.3  # the width of the bars

        fig, ax = plt.subplots()
        ax.bar(x - width / 2, non_impact_edits_lst, width, label='Edits without impact', color='cadetblue')
        ax.bar(x + width / 2, impact_edits_lst, width, label='Edits with impact', color='lightcoral')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        plt.xticks(range(0, len(labels) + 1))
        plt.yticks(range(0, max([max(non_impact_edits_lst), max(impact_edits_lst)]) + 1))
        ax.set_ylabel('Number edits')
        ax.set_xlabel('Sentence ID')
        # ax.set_title('Edits with and without impact on dependency relations')
        # ax.legend()

        # ax.bar_label(rects1, padding=3)
        # ax.bar_label(rects2, padding=3)

        fig.tight_layout()

        fig_file = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_parses', 'dependency', f'{self.file_name}_dep_impact_visualisation.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def visualise_consituents_impact(self):
        json_file_path = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_parses', 'constituency', f'{self.file_name}_constituency_impact.json')
        with open(json_file_path, 'r') as f:
            constituents_comparison = json.load(f)

        non_impact_edits_lst = []
        impact_edits_lst = []
        for sen_versions in constituents_comparison.values():
            no_non_impact_edits, no_impact_edits = 0, 0
            for ver in sen_versions.values():
                if ver['constituents_impacted'] is False:
                    no_non_impact_edits += 1
                elif ver['constituents_impacted'] is True:
                    no_impact_edits += 1
            non_impact_edits_lst.append(no_non_impact_edits)
            impact_edits_lst.append(no_impact_edits)

        labels = constituents_comparison.keys()

        plt.rcParams.update({'font.size': 6})
        plt.figure(figsize=(50, 25))

        x = np.arange(len(labels))  # the label locations
        width = 0.3  # the width of the bars

        fig, ax = plt.subplots()
        ax.bar(x - width / 2, non_impact_edits_lst, width, label='Edits without impact', color='cadetblue')
        ax.bar(x + width / 2, impact_edits_lst, width, label='Edits with impact', color='lightcoral')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        plt.xticks(range(0, len(labels) + 1))
        plt.yticks(range(0, max([max(non_impact_edits_lst), max(impact_edits_lst)]) + 1))
        ax.set_ylabel('Number edits')
        ax.set_xlabel('Sentence ID')
        # ax.set_title('Edits with and without impact on dependency relations')
        # ax.legend()

        # ax.bar_label(rects1, padding=3)
        # ax.bar_label(rects2, padding=3)

        fig.tight_layout()

        fig_file = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_parses', 'constituency', f'{self.file_name}_const_impact_visualisation.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def visualise_syntactic_impact(self):
        # constituency
        json_file_path_c = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_parses', 'constituency', f'{self.file_name}_constituency_impact.json')
        with open(json_file_path_c, 'r') as f:
            c_comparison = json.load(f)
        c_sens_impact_values = {}
        i_c = 0
        c_no_edits_with_impact = 0
        c_no_edits_wo_impact = 0
        for sen_id, vals in c_comparison.items():
            sen_ver_impact_values = [v['constituents_impacted'] for v in vals.values() if v['constituents_impacted'] is not None]
            c_sens_impact_values[i_c] = sen_ver_impact_values
            i_c += 1
            for v in sen_ver_impact_values:
                if v is True:
                    c_no_edits_with_impact += 1
                elif v is False:
                    c_no_edits_wo_impact += 1
        # dependency
        json_file_path_d = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_parses', 'dependency',
                                      f'{self.file_name}_dependency_relations_impact.json')
        with open(json_file_path_d, 'r') as f:
            d_comparison = json.load(f)
        d_sens_impact_values = {}
        i_d = 0
        d_no_edits_with_impact = 0
        d_no_edits_wo_impact = 0
        for sen_id, vals in d_comparison.items():
            sen_ver_impact_values = [v['dependency_relations_impacted'] for v in vals.values() if v['dependency_relations_impacted'] is not None]
            d_sens_impact_values[i_d] = sen_ver_impact_values
            i_d += 1
            for v in sen_ver_impact_values:
                if v is True:
                    d_no_edits_with_impact += 1
                elif v is False:
                    d_no_edits_wo_impact += 1

        color_mapping = {
            True: 'indianred',
            False: 'teal'
        }

        labels = c_sens_impact_values.keys()

        plt.rcParams.update({'font.size': 30})
        # TODO plt.figure(figsize=(30, 25))

        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(40, 20),
                                       gridspec_kw={'width_ratios': [1, 1]})

        # TODO fig, ax = plt.subplots()

        for id, impact_values in c_sens_impact_values.items():
            starts = 0
            for iv in impact_values:
                lbl = f'Edit with syntactic impact' if iv is True else f'Edit without syntactic impact'
                ax1.barh(id, 1, left=starts, height=1, color=color_mapping[iv], edgecolor='white', label=lbl)
                starts += 1

        for id, impact_values in d_sens_impact_values.items():
            starts = 0
            for iv in impact_values:
                lbl = f'Edit with syntactic impact' if iv is True else f'Edit without syntactic impact'
                ax2.barh(id, 1, left=starts, height=1, color=color_mapping[iv], edgecolor='white', label=lbl)
                starts += 1

        # removed for SIG:
        # c_max_no_edits = max([len(vals) for vals in c_sens_impact_values.values()])
        # plt.xticks(range(0, c_max_no_edits + 1))^
        plt.yticks(range(0, len(labels) + 1))

        ax1.set_xticks(range(0, 30))  # for SIG
        ax1.set_ylim(len(labels) + 1, -1)
        ax1.set_xlabel('Number edits')
        ax1.set_ylabel('Sentence ID')
        # hand, labl = ax1.get_legend_handles_labels()
        # handout = []
        # lablout = []
        # for h, l in zip(hand, labl):
        #     if l not in lablout:
        #         lablout.append(l)
        #         handout.append(h)
        # ax1.legend(handout, lablout, loc="upper right")
        ax1.set_title('CONSTITUENCY')

        ax2.set_xticks(range(0, 30))  # for SIG
        ax2.set_xlabel('Number edits')
        # hand, labl = ax2.get_legend_handles_labels()
        # handout = []
        # lablout = []
        # for h, l in zip(hand, labl):
        #     if l not in lablout:
        #         lablout.append(l)
        #         handout.append(h)
        # ax2.legend(handout, lablout, loc="upper right")
        ax2.set_title('DEPENDENCY')

        fig.tight_layout()

        fig_file = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_parses', f'{self.file_name}_syntactic_impact_visualisation.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

        c_vals = [c_no_edits_with_impact, c_no_edits_wo_impact]
        d_vals = [d_no_edits_with_impact, d_no_edits_wo_impact]
        lbls = [f'syntactic impact', f'no syntactic impact']
        plt.rcParams.update({'font.size': 35})
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(40, 20),
                                       gridspec_kw={'width_ratios': [1, 1]})
        ax1.pie(c_vals, colors=['indianred', 'teal'], autopct='%1.1f%%')
        ax1.set_title('CONSTITUENCY')
        ax2.pie(d_vals, colors=['indianred', 'teal'], autopct='%1.1f%%')
        ax2.set_title('DEPENDENCY')

        fig_file = os.path.join(self.output_directory, f'{self.file_name}_sentence_histories', f'{self.file_name}_sentence_parses', f'{self.file_name}_syntactic_impact_visualisation_pie.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()



