import operator

import matplotlib.pyplot as plt

from wta.output_handler.plots.colors import Colors

from .base import BasePlot


class StatsPlot(BasePlot):
    def __init__(self, texthis, senhis):
        self.texthis = texthis
        self.senhis = senhis
        self.data = self.preprocess_data()

    def preprocess_data(self):
        pass

    def create_figure(self):
        pass

    def plot_data(self):
        pass

    def set_legend(self):
        pass

    def run(self):
        plt = self.create_figure()
        self.plot_data()
        self.set_legend()
        return plt


class SenEditPlot(StatsPlot):
    def __init__(self, texthis, senhis):
        super().__init__(texthis, senhis)

    def preprocess_data(self):
        sen_ids = []
        i = 0
        number_versions = []
        for sens in self.senhis.values():
            sen_ids.append(str(i))
            number_versions.append(len(sens))
            i += 1
        return sen_ids, number_versions

    def create_figure(self):
        plt.rcParams.update({"font.size": 12})
        plt.figure(figsize=(15, 7))
        # plt.title('Number edit operations per sentence')
        # plt.xlabel('Sentence ID')
        # plt.ylabel('Number edit operations')
        plt.yticks(range(1, 31))  # for SIG
        # plt.yticks(range(1, max(number_versions)+1))
        return plt

    def plot_data(self):
        plt.bar(
            self.data[0],
            self.data[1],
            color=Colors.assign_color_to_number_versions(self.data[1]),
        )


class TsLabelsPlot(StatsPlot):
    def __init__(self, texthis, senhis):
        super().__init__(texthis, senhis)

    def preprocess_data(self):
        appended_tokens, inserted_tokens, deleted_tokens = 0, 0, 0
        for tpsf in self.texthis:
            if tpsf.ts.label == "append":
                appended_tokens += len(tpsf.ts.tagged_tokens)
            if tpsf.ts.label == "insertion":
                inserted_tokens += len(tpsf.ts.tagged_tokens)
            if tpsf.ts.label == "deletion":
                deleted_tokens += len(tpsf.ts.tagged_tokens)
        return [appended_tokens, inserted_tokens, deleted_tokens]

    def create_figure(self):
        plt.rcParams.update({"font.size": 35})
        plt.figure(figsize=(20, 15))
        plt.title("Edit operations types")
        return plt

    def plot_data(self):
        plt.pie(
            self.data,
            labels=["appends", "insertions", "deletions"],
            colors=["teal", "lightcoral", "cadetblue"],
        )


class TsTokensPlot(StatsPlot):
    def __init__(self, texthis, senhis):
        super().__init__(texthis, senhis)

    def preprocess_data(self):
        tpsf_ids, ts_tokens = [], []
        for tpsf in self.texthis:
            if tpsf.ts.tagged_tokens != "":
                tpsf_ids.append(tpsf.revision_id)
                no_edited_tokens = len(tpsf.ts.tagged_tokens)
                if tpsf.ts.label == "deletion":
                    no_edited_tokens = no_edited_tokens * -1
                ts_tokens.append(no_edited_tokens)
        return tpsf_ids, ts_tokens

    def create_figure(self):
        plt.rcParams.update({"font.size": 12})
        plt.figure(figsize=(20, 15))
        plt.ylim(-15, 60)  # for SIG
        plt.xlabel("Text version ID")
        plt.ylabel("Number added and removed tokens")
        return plt

    def plot_data(self):
        colors = ["cadetblue" if e >= 0 else "lightcoral" for e in self.data[1]]
        plt.bar(self.data[0], self.data[1], color=colors)


class DeletionsPlot(StatsPlot):
    def __init__(self, texthis, senhis):
        super().__init__(texthis, senhis)

    def preprocess_data(self):
        ts_content = {}
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

    def create_figure(self):
        plt.rcParams.update({"font.size": 35})
        plt.figure(figsize=(20, 15))
        # plt.title('Number edit operations per part of speech')
        return plt

    def plot_data(self):
        lbls = [t[0] for t in self.data]
        vals = [t[1] for t in self.data]
        plt.pie(vals, labels=lbls, colors=Colors.assign_color_to_pos(lbls))


class InsertionsPlot(StatsPlot):
    def __init__(self, texthis, senhis):
        super().__init__(texthis, senhis)

    def preprocess_data(self):
        ts_content = {}
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

    def create_figure(self):
        plt.rcParams.update({"font.size": 35})
        plt.figure(figsize=(20, 15))
        # plt.title('Number edit operations per part of speech')
        return plt

    def plot_data(self):
        lbls = [t[0] for t in self.data]
        vals = [t[1] for t in self.data]
        plt.pie(
            vals, labels=lbls, colors=Colors.assign_color_to_pos(lbls), normalize=False
        )  # TODO check the normalization impact
