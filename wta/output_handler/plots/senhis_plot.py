import matplotlib.pyplot as plt

from wta.output_handler.plots.colors import Colors


class SenhisPlot:

    def __init__(self, texthis, senhis):
        self.texthis = [tpsf for tpsf in texthis if (
                len(tpsf.new_sentences) > 0
                or len(tpsf.modified_sentences) > 0
                or len(tpsf.deleted_sentences) > 0)]
        self.senhis = senhis
        self.plot_ = None
        self.title_ax1 = 'Sentence Histories'
        self.xlabel_ = 'Number of characters'
        self.sen_colors = Colors.assign_colors_to_sens(senhis)

    def plot_data(self):
        tpsf_sentences = self.preprocess_data()
        return self.plot(tpsf_sentences)

    def preprocess_data(self):
        """
        Collects sentence versions for each tpsf (its text and length)
        and retrieves sentence id from sentence history for each sentence version
        in order to assign the corresponding color to the sentence.
        Returns:
            A dict containing a list of tuples (sen len, sen color, sen text) for each tpsf
        """
        tpsf_sentences = {}
        for tpsf in self.texthis:
            tpsf_sens = []
            for id, sen in enumerate(tpsf.sentence_list):
                for sen_id, sen_list in self.senhis.items():
                    if sen.text.strip() in [s.text for s in sen_list] and sen.text.strip() not in [s[2] for s in tpsf_sens]:
                        tpsf_sens.append((len(sen.text), self.sen_colors[sen_id], sen.text))
                if sen.text.strip() not in [s[2] for s in tpsf_sens]:
                    tpsf_sens.append((len(sen.text), 'beige', sen.text))
            tpsf_sentences.update({tpsf.revision_id: tpsf_sens})
        return tpsf_sentences

    def plot(self, tpsf_sentences):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 20))
        ax1.set_ylim(len(tpsf_sentences) + 1, -1)
        ax1.tick_params(axis='both', which='major', labelsize=7)
        ax1.set_title(self.title_ax1, pad=5)
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
        ax1.set_xlabel(self.xlabel_)
        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.4, wspace=0.01)
        plt.tight_layout()
        return plt

