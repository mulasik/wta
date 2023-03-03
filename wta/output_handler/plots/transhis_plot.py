import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from ...pipeline.transformation_histories.transformation import Transformation
from ...settings import Settings
from .base import BasePlot
from .colors import Colors


class TranshisPlot(BasePlot):
    def __init__(self, dep_transhis: dict[int, list[Transformation]]) -> None:
        self.dep_transhis = dep_transhis
        self.data = self.preprocess_data(dep_transhis)
        self.labels = self.dep_transhis.keys()

    def preprocess_data(
        self, data: dict[int, list[Transformation]]
    ) -> tuple[list[int], list[int]]:
        non_impact_edits_lst = []
        impact_edits_lst = []
        for sen_versions in data.values():
            no_non_impact_edits, no_impact_edits = 0, 0
            for ver in sen_versions:
                if ver.syntactic_impact is False:
                    no_non_impact_edits += 1
                elif ver.syntactic_impact is True:
                    no_impact_edits += 1
            non_impact_edits_lst.append(no_non_impact_edits)
            impact_edits_lst.append(no_impact_edits)
        return non_impact_edits_lst, impact_edits_lst

    def create_figure(self) -> Axes:
        plt.rcParams.update({"font.size": 6})
        plt.figure(figsize=(50, 25))
        fig, ax = plt.subplots()
        plt.xticks(range(0, len(self.labels) + 1))
        plt.yticks(range(0, max([max(self.data[0]), max(self.data[1])]) + 1))
        ax.set_ylabel("Number edits")
        ax.set_xlabel("Sentence ID")
        ax.set_title("Edits with and without impact on dependency relations")
        fig.tight_layout()
        return ax

    def plot_data(self, ax: Axes) -> None:
        x = np.arange(len(self.labels))  # the label locations
        width = 0.3  # the width of the bars
        ax.bar(
            x - width / 2,
            self.data[0],
            width,
            label="Edits without impact",
            color="cadetblue",
        )
        ax.bar(
            x + width / 2,
            self.data[1],
            width,
            label="Edits with impact",
            color="lightcoral",
        )

    def set_legend(self, ax: Axes) -> None:
        ax.legend()

    def run(self) -> None:
        ax = self.create_figure()
        self.plot_data(ax)
        self.set_legend(ax)


class DepTranshisPlot(TranshisPlot):
    pass


class ConstTranshisPlot(TranshisPlot):
    pass


class SynBarTranshisPlot(BasePlot):
    def __init__(
        self,
        dep_transhis: dict[int, list[Transformation]],
        const_transhis: dict[int, list[Transformation]],
        settings: Settings,
    ) -> None:
        self.output_directory = settings.config["output_dir"]
        self.filename = settings.filename
        self.dep_transhis = dep_transhis
        self.const_transhis = const_transhis
        self.data = self.preprocess_data()

    def preprocess_data(
        self,
    ) -> tuple[dict[int, list[bool]], int, int, dict[int, list[bool]], int, int]:
        # dependency
        d_sens_impact_values = {}
        i_d = 0
        d_no_edits_with_impact = 0
        d_no_edits_wo_impact = 0
        for sen_id, vals in self.dep_transhis.items():
            sen_ver_impact_values = [
                v.syntactic_impact for v in vals if v.syntactic_impact is not None
            ]
            d_sens_impact_values[i_d] = sen_ver_impact_values
            i_d += 1
            for v in sen_ver_impact_values:
                if v is True:
                    d_no_edits_with_impact += 1
                elif v is False:
                    d_no_edits_wo_impact += 1
        # constituency
        c_sens_impact_values = {}
        i_c = 0
        c_no_edits_with_impact = 0
        c_no_edits_wo_impact = 0
        for sen_id, vals in self.const_transhis.items():
            sen_ver_impact_values = [
                v.syntactic_impact for v in vals if v.syntactic_impact is not None
            ]
            c_sens_impact_values[i_c] = sen_ver_impact_values
            i_c += 1
            for v in sen_ver_impact_values:
                if v is True:
                    c_no_edits_with_impact += 1
                elif v is False:
                    c_no_edits_wo_impact += 1
        return (
            d_sens_impact_values,
            d_no_edits_with_impact,
            d_no_edits_wo_impact,
            c_sens_impact_values,
            c_no_edits_with_impact,
            c_no_edits_wo_impact,
        )

    def create_figure(self) -> tuple[Axes, Axes]:
        labels = self.data[3].keys()

        plt.rcParams.update({"font.size": 30})
        # TODO plt.figure(figsize=(30, 25))

        fig, (ax1, ax2) = plt.subplots(
            1, 2, sharey=True, figsize=(40, 20), gridspec_kw={"width_ratios": [1, 1]}
        )

        # TODO fig, ax = plt.subplots()
        # removed for SIG:
        # c_max_no_edits = max([len(vals) for vals in c_sens_impact_values.values()])
        # plt.xticks(range(0, c_max_no_edits + 1))^
        plt.yticks(range(0, len(labels) + 1))

        ax1.set_title("CONSTITUENCY")
        ax1.set_xticks(range(0, 30))  # for SIG
        ax1.set_ylim(len(labels) + 1, -1)
        ax1.set_xlabel("Number transformations")
        ax1.set_ylabel("Sentence ID")

        ax2.set_title("DEPENDENCY")
        ax2.set_xticks(range(0, 30))  # for SIG
        ax2.set_xlabel("Number transformations")

        fig.tight_layout()
        return ax1, ax2

    def plot_data(self, ax1: Axes, ax2: Axes) -> None:
        for id, impact_values in self.data[3].items():
            starts = 0
            for iv in impact_values:
                lbl = (
                    "Edit with syntactic impact"
                    if iv is True
                    else "Edit without syntactic impact"
                )
                ax1.barh(
                    id,
                    1,
                    left=starts,
                    height=1,
                    color=Colors.BOOL_COLORS[iv],
                    edgecolor="white",
                    label=lbl,
                )
                starts += 1
        for id, impact_values in self.data[0].items():
            starts = 0
            for iv in impact_values:
                lbl = (
                    "Edit with syntactic impact"
                    if iv is True
                    else "Edit without syntactic impact"
                )
                ax2.barh(
                    id,
                    1,
                    left=starts,
                    height=1,
                    color=Colors.BOOL_COLORS[iv],
                    edgecolor="white",
                    label=lbl,
                )
                starts += 1

    def set_legend(self, ax1: Axes, ax2: Axes) -> None:
        hand, labl = ax1.get_legend_handles_labels()
        handout = []
        lablout = []
        for h, l in zip(hand, labl):
            if l not in lablout:
                lablout.append(l)
                handout.append(h)
        ax1.legend(handout, lablout, loc="upper right")
        hand, labl = ax2.get_legend_handles_labels()
        handout = []
        lablout = []
        for h, l in zip(hand, labl):
            if l not in lablout:
                lablout.append(l)
                handout.append(h)
        ax2.legend(handout, lablout, loc="upper right")

    def run(self) -> None:
        ax1, ax2 = self.create_figure()
        self.plot_data(ax1, ax2)
        self.set_legend(ax1, ax2)


class SynPieTranshisPlot(SynBarTranshisPlot):
    def create_figure(self) -> tuple[Axes, Axes]:
        lbls = ["syntactic impact", "no syntactic impact"]  # TODO add labels
        plt.rcParams.update({"font.size": 35})
        fig, (ax1, ax2) = plt.subplots(
            1, 2, sharey=True, figsize=(40, 20), gridspec_kw={"width_ratios": [1, 1]}
        )
        ax1.set_title("CONSTITUENCY")
        ax2.set_title("DEPENDENCY")
        return ax1, ax2

    def plot_data(self, ax1: Axes, ax2: Axes) -> None:
        d_vals = [self.data[1], self.data[2]]
        c_vals = [self.data[4], self.data[5]]
        ax1.pie(c_vals, colors=["indianred", "teal"], autopct="%1.1f%%")
        ax2.pie(d_vals, colors=["indianred", "teal"], autopct="%1.1f%%")
