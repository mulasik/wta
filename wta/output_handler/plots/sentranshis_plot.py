from typing import Generic, TypeVar

import matplotlib.pyplot as plt
import numpy as np

from wta.output_handler.plots.base import BasePlot
from wta.pipeline.names import SenTransformationTypes
from wta.pipeline.sentence_layer.sentence_histories.sentence_transformation import SentenceTransformation
from wta.settings import Settings

from .colors import Colors

_T = TypeVar("_T")

class SentransHisPlot(BasePlot, Generic[_T]):
    def __init__(
        self, sentranshis: dict[int, list[SentenceTransformation]], settings: Settings
    ) -> None:
        self.sentranshis = sentranshis
        self.settings = settings
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
        # self.create_figure()
        self.plot_data()
        # self.set_legend()

class SentransDraftPlot(SentransHisPlot[dict[int, list[SentenceTransformation]]]):
    def preprocess_data(self) -> tuple[str, dict[str, list[int]]]:
        sen_ids = []
        i = 0
        number_senversions = {
            "initial_draft": [],
            "revision_draft": []
        }
        for senvers in self.sentranshis.values():
            sen_ids.append(str(i))
            initial_draft_versions = [
                sv for sv in senvers if sv.operation in [
                    SenTransformationTypes.PROD, SenTransformationTypes.PRECON_DEL, SenTransformationTypes.PRECON_INS, SenTransformationTypes.PRECON_REV
                    ]
                ]
            revision_draft_versions = [
                sv for sv in senvers if sv.operation in [
                    SenTransformationTypes.CON_DEL, SenTransformationTypes.CON_INS, SenTransformationTypes.CON_REV
                    ]
                ]
            no_in_ver = len(initial_draft_versions)
            no_rev_ver = len(revision_draft_versions)
            number_senversions["initial_draft"].append(no_in_ver)
            number_senversions["revision_draft"].append(no_rev_ver)
            i += 1
        return sen_ids, number_senversions

    def create_figure(self) -> None:
        ...


    def plot_data(self) -> None:
        sen_ids = self.data[0]
        plt.rcParams.update({"font.size": 10})
        fig, ax = plt.subplots(figsize=(20,8))
        ticks_loc = np.arange(0, 30, step=2)
        # ax.set_ylim([0, 30])  # to set the same limit for all charts
        ax.set_yticks(ticks_loc)
        # plt.tick_params(axis='x', which='major', labelsize=10)
        # plt.yticks(range(1, max(number_versions)+1))
        ax.bar(sen_ids, self.data[1]["initial_draft"], color = Colors.DRAFT_COLORS["initial_draft"], label="initial draft")
        ax.bar(sen_ids, self.data[1]["revision_draft"], bottom = self.data[1]["initial_draft"], color = Colors.DRAFT_COLORS["revision_draft"], label="revision draft")
        ax.legend(loc="upper right")
        # plt.title('Number operations in sentence initial and revision draft')
        plt.xlabel('Sentence history ID')
        plt.ylabel('Number operations')

