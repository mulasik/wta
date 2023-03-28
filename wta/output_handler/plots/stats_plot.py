import operator
from typing import Generic, TypeVar

import matplotlib.pyplot as plt

from ...pipeline.sentence_histories.text_unit import TextUnit
from ...pipeline.text_history.tpsf import TpsfECM
from .base import BasePlot
from .colors import Colors

_T = TypeVar("_T")


class StatsPlot(BasePlot, Generic[_T]):
    def __init__(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
        self.texthis = texthis
        self.senhis = senhis
        self.data = self.preprocess_data()

    def preprocess_data(self) -> _T:
        raise NotImplementedError

    def create_figure(self) -> None:
        pass

    def plot_data(self) -> None:
        pass

    def set_legend(self) -> None:
        pass

    def run(self) -> None:
        self.create_figure()
        self.plot_data()
        self.set_legend()


class SenEditPlot(StatsPlot[tuple[list[str], list[int]]]):
    def preprocess_data(self) -> tuple[list[str], list[int]]:
        sen_ids = []
        i = 0
        number_versions = []
        for sens in self.senhis.values():
            sen_ids.append(str(i))
            number_versions.append(len(sens))
            i += 1
        return sen_ids, number_versions

    def create_figure(self) -> None:
        plt.rcParams.update({"font.size": 12})
        plt.figure(figsize=(15, 7))
        # plt.title('Number edit operations per sentence')
        # plt.xlabel('Sentence ID')
        # plt.ylabel('Number edit operations')
        plt.yticks(range(1, 31))  # for SIG
        # plt.yticks(range(1, max(number_versions)+1))

    def plot_data(self) -> None:
        plt.bar(
            self.data[0],
            self.data[1],
            color=Colors.assign_color_to_number_versions(self.data[1]),
        )


class TsLabelsPlot(StatsPlot[tuple[int, int, int]]):
    def preprocess_data(self) -> tuple[int, int, int]:
        appended_tokens, inserted_tokens, deleted_tokens = 0, 0, 0
        for tpsf in self.texthis:
            if tpsf.ts.label == "append":
                appended_tokens += len(tpsf.ts.tagged_tokens)
            if tpsf.ts.label == "insertion":
                inserted_tokens += len(tpsf.ts.tagged_tokens)
            if tpsf.ts.label == "deletion":
                deleted_tokens += len(tpsf.ts.tagged_tokens)
        return appended_tokens, inserted_tokens, deleted_tokens

    def create_figure(self) -> None:
        plt.rcParams.update({"font.size": 35})
        plt.figure(figsize=(20, 15))
        plt.title("Edit operations types")

    def plot_data(self) -> None:
        plt.pie(
            self.data,
            labels=["appends", "insertions", "deletions"],
            colors=["teal", "lightcoral", "cadetblue"],
        )


class TsTokensPlot(StatsPlot[tuple[list[int], list[int]]]):
    def preprocess_data(self) -> tuple[list[int], list[int]]:
        tpsf_ids, ts_tokens = [], []
        for tpsf in self.texthis:
            if tpsf.ts.tagged_tokens != "":
                tpsf_ids.append(tpsf.revision_id)
                no_edited_tokens = len(tpsf.ts.tagged_tokens)
                if tpsf.ts.label == "deletion":
                    no_edited_tokens = no_edited_tokens * -1
                ts_tokens.append(no_edited_tokens)
        return tpsf_ids, ts_tokens

    def create_figure(self) -> None:
        plt.rcParams.update({"font.size": 12})
        plt.figure(figsize=(20, 15))
        plt.ylim(-15, 60)  # for SIG
        plt.xlabel("Text version ID")
        plt.ylabel("Number added and removed tokens")

    def plot_data(self) -> None:
        colors = ["cadetblue" if e >= 0 else "lightcoral" for e in self.data[1]]
        plt.bar(self.data[0], self.data[1], color=colors)


class DeletionsPlot(StatsPlot[list[tuple[str, int]]]):
    def preprocess_data(self) -> list[tuple[str, int]]:
        ts_content: dict[str, int] = {}
        for tpsf in self.texthis:
            if tpsf.ts.label in ["deletion"]:
                for t in tpsf.ts.tagged_tokens:
                    if (
                        t["pos"] not in ["X", "SPACE", "PUNCT"]
                        and t["pos"] not in ts_content.keys()
                    ):
                        ts_content.update({t["pos"]: 1})
                    elif (
                        t["pos"] not in ["X", "SPACE", "PUNCT"]
                        and t["pos"] in ts_content
                    ):
                        ts_content[t["pos"]] += 1
        return sorted(ts_content.items(), key=operator.itemgetter(0), reverse=True)

    def create_figure(self) -> None:
        plt.rcParams.update({"font.size": 35})
        plt.figure(figsize=(20, 15))
        # plt.title('Number edit operations per part of speech')

    def plot_data(self) -> None:
        lbls = [t[0] for t in self.data]
        vals = [t[1] for t in self.data]
        plt.pie(vals, labels=lbls, colors=Colors.assign_color_to_pos(lbls))


class InsertionsPlot(StatsPlot[list[tuple[str, int]]]):
    def preprocess_data(self) -> list[tuple[str, int]]:
        ts_content: dict[str, int] = {}
        for tpsf in self.texthis:
            if tpsf.ts.label in ["insertion"]:
                for t in tpsf.ts.tagged_tokens:
                    if (
                        t["pos"] not in ["X", "SPACE", "PUNCT"]
                        and t["pos"] not in ts_content.keys()
                    ):
                        ts_content.update({t["pos"]: 1})
                    elif (
                        t["pos"] not in ["X", "SPACE", "PUNCT"]
                        and t["pos"] in ts_content
                    ):
                        ts_content[t["pos"]] += 1
        return sorted(ts_content.items(), key=operator.itemgetter(0), reverse=True)

    def create_figure(self) -> None:
        plt.rcParams.update({"font.size": 35})
        plt.figure(figsize=(20, 15))
        # plt.title('Number edit operations per part of speech')

    def plot_data(self) -> None:
        lbls = [t[0] for t in self.data]
        vals = [t[1] for t in self.data]
        plt.pie(
            vals, labels=lbls, colors=Colors.assign_color_to_pos(lbls), normalize=False
        )  # TODO check the normalization impact
