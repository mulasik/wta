import matplotlib.pyplot as plt
import os
import numpy as np
import json

import settings
import paths
from wta.output_handler.storage.names import Names


class TranshisPlot:

    def __init__(self):
        self.output_directory = settings.config['output_dir']
        self.filename = settings.filename

    def plot_data(self):
        self.visualise_dependency_relations_impact()
        self.visualise_consituents_impact()
        self.visualise_syntactic_impact()

    def visualise_dependency_relations_impact(self):
        json_file_path = os.path.join(paths.dependency_transhis_dir, f'{settings.filename}_{Names.TRANSHIS}_dependency.json')
        with open(json_file_path, 'r') as f:
            dependency_transformations = json.load(f)

        non_impact_edits_lst = []
        impact_edits_lst = []
        for sen_versions in dependency_transformations.values():
            no_non_impact_edits, no_impact_edits = 0, 0
            for ver in sen_versions:
                if ver['syntactic_impact'] is False:
                    no_non_impact_edits += 1
                elif ver['syntactic_impact'] is True:
                    no_impact_edits += 1
            non_impact_edits_lst.append(no_non_impact_edits)
            impact_edits_lst.append(no_impact_edits)

        labels = dependency_transformations.keys()

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

        fig_file = json_file_path.replace('.json', '_visualisation.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def visualise_consituents_impact(self):
        json_file_path = os.path.join(paths.constituency_transhis_dir, f'{settings.filename}_{Names.TRANSHIS}_constituency.json')
        with open(json_file_path, 'r') as f:
            constituents_comparison = json.load(f)

        non_impact_edits_lst = []
        impact_edits_lst = []
        for sen_versions in constituents_comparison.values():
            no_non_impact_edits, no_impact_edits = 0, 0
            for ver in sen_versions:
                if ver['syntactic_impact'] is False:
                    no_non_impact_edits += 1
                elif ver['syntactic_impact'] is True:
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

        fig_file = os.path.join(paths.constituency_transhis_dir, f'{self.filename}_{Names.TRANSHIS}_{Names.CONST}_{Names.VISUAL}.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def visualise_syntactic_impact(self):
        # constituency
        json_file_path_c = os.path.join(paths.constituency_transhis_dir, f'{self.filename}_{Names.TRANSHIS}_{Names.CONST}.json')
        with open(json_file_path_c, 'r') as f:
            c_comparison = json.load(f)
        c_sens_impact_values = {}
        i_c = 0
        c_no_edits_with_impact = 0
        c_no_edits_wo_impact = 0
        for sen_id, vals in c_comparison.items():
            sen_ver_impact_values = [v['syntactic_impact'] for v in vals if v['syntactic_impact'] is not None]
            c_sens_impact_values[i_c] = sen_ver_impact_values
            i_c += 1
            for v in sen_ver_impact_values:
                if v is True:
                    c_no_edits_with_impact += 1
                elif v is False:
                    c_no_edits_wo_impact += 1
        # dependency
        json_file_path_d = os.path.join(paths.dependency_transhis_dir, f'{self.filename}_{Names.TRANSHIS}_{Names.DEP}.json')
        with open(json_file_path_d, 'r') as f:
            d_comparison = json.load(f)
        d_sens_impact_values = {}
        i_d = 0
        d_no_edits_with_impact = 0
        d_no_edits_wo_impact = 0
        for sen_id, vals in d_comparison.items():
            sen_ver_impact_values = [v['syntactic_impact'] for v in vals if v['syntactic_impact'] is not None]
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

        fig_file = os.path.join(paths.transhis_dir, f'{self.filename}_syntactic_impact_{Names.VISUAL}.svg')
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

        fig_file = os.path.join(paths.transhis_dir, f'{self.filename}_syntactic_impact_{Names.VISUAL}_pie.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()