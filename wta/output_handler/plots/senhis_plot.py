import matplotlib.pyplot as plt

from wta.output_handler.plots.colors import Colors
from .base import BasePlot


class SenhisPlot(BasePlot):
    def __init__(self, texthis, senhis):
        texthis = [
            tpsf
            for tpsf in texthis
            if (
                len(tpsf.new_sentences) > 0
                or len(tpsf.modified_sentences) > 0
                or len(tpsf.deleted_sentences) > 0
            )
        ]
        self.title_ax1 = "Sentence Histories"
        self.xlabel_ = "Number of characters"
        self.sen_colors = Colors.assign_colors_to_sens(senhis)
        self.data = self.preprocess_data(texthis, senhis)

    def preprocess_data(self, texthis, senhis):
        """
        Collects sentence versions for each tpsf (its text and length)
        and retrieves sentence id from sentence history for each sentence version
        in order to assign the corresponding color to the sentence.
        Returns:
            A dict containing a list of tuples (sen len, sen color, sen text) for each tpsf
        """
        tpsf_sentences = {}
        for tpsf in texthis:
            tpsf_sens = []
            for id, sen in enumerate(tpsf.sentence_list):
                for sen_id, sen_list in senhis.items():
                    if sen.content.strip() in [
                        s.content for s in sen_list
                    ] and sen.content.strip() not in [s[2] for s in tpsf_sens]:
                        tpsf_sens.append(
                            (len(sen.content), self.sen_colors[sen_id], sen.content)
                        )
                if sen.content.strip() not in [s[2] for s in tpsf_sens]:
                    tpsf_sens.append((len(sen.content), "beige", sen.content))
            tpsf_sentences.update({tpsf.revision_id: tpsf_sens})
        return tpsf_sentences

    def create_figure(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 20))
        ax1.set_ylim(len(self.data) + 1, -1)
        ax1.tick_params(axis="both", which="major", labelsize=7)
        ax1.set_title(self.title_ax1, pad=5)
        ax1.set_xlabel(self.xlabel_)
        plt.subplots_adjust(bottom=0.1, right=0.8, top=0.4, wspace=0.01)
        last_tpsf_id = list(self.data.keys())[-1]
        ax2.set_title(
            f"Last Sentence Versions (TPSF {last_tpsf_id}):",
            pad=5,
            horizontalalignment="left",
        )
        ax2.axis("off")
        plt.tight_layout()
        return ax1, ax2

    def plot_data(self, ax1, ax2):
        for id, sens in self.data.items():
            a1_starts = 0
            for s in sens:
                ax1.barh(
                    f"TPSF {id}",
                    s[0],
                    left=a1_starts,
                    height=1,
                    color=s[1],
                    edgecolor="white",
                    alpha=0.7,
                )
                a1_starts += s[0]
        last_tpsf_id = list(self.data.keys())[-1]
        last_sen_versions = self.data[last_tpsf_id]
        a2_starts = 0.95
        for s in last_sen_versions:
            a2_starts -= 0.01
            ax2.content(
                0,
                a2_starts,
                s[2].strip(),
                wrap=True,
                size=7,
                bbox={"facecolor": s[1], "alpha": 0.6, "pad": 2},
            )
            a2_starts -= 0.01
        return plt

    def set_legend(self):
        pass

    def run(self):
        ax1, ax2 = self.create_figure()
        self.plot_data(ax1, ax2)
        return plt
