import matplotlib.pyplot as plt
import os
import operator

import settings
import paths
from wta.output_handler.plots.colors import Colors


class StatsPlot:

    def __init__(self):
        self.output_directory = settings.config['output_dir']
        self.filename = settings.filename

    def plot_data(self, texthis, senhis):
        self.plot_sen_edit_ops(senhis)
        self.plot_ts_tokens(texthis)
        self.plot_dels_content(texthis)
        self.plot_ins_content(texthis)
        self.plot_ts_labels(texthis)

    def plot_sen_edit_ops(self, sentence_data):
        sen_ids = []
        i = 0
        number_versions = []
        for sens in sentence_data.values():
            sen_ids.append(str(i))
            number_versions.append(len(sens))
            i += 1
        plt.rcParams.update({'font.size': 12})
        plt.figure(figsize=(15, 7))
        plt.bar(sen_ids, number_versions, color=Colors.assign_color_to_number_versions(number_versions))
        # plt.title('Number edit operations per sentence')
        # plt.xlabel('Sentence ID')
        # plt.ylabel('Number edit operations')
        plt.yticks(range(1, 31))  # for SIG
        # plt.yticks(range(1, max(number_versions)+1))
        fig_file = os.path.join(paths.stats_dir, f'{settings.filename}_sentence_stats.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def plot_ts_labels(self, data_ecm):
        appended_tokens, inserted_tokens, deleted_tokens = 0, 0, 0
        for tpsf in data_ecm:
            if tpsf.transforming_sequence.label == 'append':
                appended_tokens += len(tpsf.transforming_sequence.tagged_tokens)
            if tpsf.transforming_sequence.label == 'insertion':
                inserted_tokens += len(tpsf.transforming_sequence.tagged_tokens)
            if tpsf.transforming_sequence.label == 'deletion':
                deleted_tokens += len(tpsf.transforming_sequence.tagged_tokens)
        plt.rcParams.update({'font.size': 35})
        plt.figure(figsize=(20, 15))
        plt.pie([appended_tokens, inserted_tokens, deleted_tokens], labels=['appends', 'insertions', 'deletions'],
                colors=['teal', 'lightcoral', 'cadetblue'])
        # plt.title('Edit operations types')
        fig_file = os.path.join(paths.stats_dir, f'{settings.filename}_ts_labels_stats.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def plot_dels_content(self, data_ecm):
        ts_content = {}
        for tpsf in data_ecm:
            if tpsf.transforming_sequence.label in ['deletion']:
                for t in tpsf.transforming_sequence.tagged_tokens:
                    if t['pos'] not in ['X', 'SPACE', 'PUNCT'] and t['pos'] not in ts_content.keys():
                        ts_content.update({t['pos']: 1})
                    elif t['pos'] not in ['X', 'SPACE', 'PUNCT'] and t['pos'] in ts_content.keys():
                        ts_content[t['pos']] += 1
        sorted_ts_content = sorted(ts_content.items(), key=operator.itemgetter(0), reverse=True)
        lbls = [t[0] for t in sorted_ts_content]
        vals = [t[1] for t in sorted_ts_content]
        plt.rcParams.update({'font.size': 35})
        plt.figure(figsize=(20, 15))
        plt.pie(vals, labels=lbls, colors=Colors.assign_color_to_pos(lbls))
        # plt.title('Number edit operations per part of speech')
        fig_file = os.path.join(paths.stats_dir, f'{settings.filename}_ts_content_stats_del.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def plot_ins_content(self, data_ecm):
        ts_content = {}
        for tpsf in data_ecm:
            if tpsf.transforming_sequence.label in ['insertion']:
                for t in tpsf.transforming_sequence.tagged_tokens:
                    if t['pos'] not in ['X', 'SPACE', 'PUNCT'] and t['pos'] not in ts_content.keys():
                        ts_content.update({t['pos']: 1})
                    elif t['pos'] not in ['X', 'SPACE', 'PUNCT'] and t['pos'] in ts_content.keys():
                        ts_content[t['pos']] += 1
        sorted_ts_content = sorted(ts_content.items(), key=operator.itemgetter(0), reverse=True)
        lbls = [t[0] for t in sorted_ts_content]
        vals = [t[1] for t in sorted_ts_content]
        plt.rcParams.update({'font.size': 35})
        plt.figure(figsize=(20, 15))
        plt.pie(vals, labels=lbls, colors=Colors.assign_color_to_pos(lbls),
                normalize=False)  # TODO check the normalization impact
        # plt.title('Number edit operations per part of speech')
        fig_file = os.path.join(paths.stats_dir, f'{settings.filename}_ts_content_stats_ins.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

    def plot_ts_tokens(self, data_ecm):
        tpsf_ids, ts_tokens = [], []
        for tpsf in data_ecm:
            if tpsf.transforming_sequence.tagged_tokens != '':
                tpsf_ids.append(tpsf.revision_id)
                no_edited_tokens = len(tpsf.transforming_sequence.tagged_tokens)
                if tpsf.transforming_sequence.label == 'deletion':
                    no_edited_tokens = no_edited_tokens * -1
                ts_tokens.append(no_edited_tokens)
        colors = ['cadetblue' if e >= 0 else 'lightcoral' for e in ts_tokens]
        plt.rcParams.update({'font.size': 12})
        plt.figure(figsize=(20, 15))
        plt.ylim(-15, 60)  # for SIG
        plt.bar(tpsf_ids, ts_tokens, color=colors)
        # plt.title('Number added versus removed tokens per text version')
        plt.xlabel('Text version ID')
        plt.ylabel('Number added and removed tokens')
        fig_file = os.path.join(paths.stats_dir, f'{settings.filename}_ts_tokens_stats.svg')
        plt.savefig(fig_file, bbox_inches='tight')
        plt.close()

