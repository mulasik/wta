import uuid

from tqdm import tqdm

from wta.pipeline.text_history.ts import TransformingSequence
from wta.pipeline.text_history.ts_factory import retrieve_sen_ts
from wta.settings import Settings

from ..names import SenLabels
from ..text_history.tpsf import TpsfECM
from .text_unit import TextUnit, TextUnitType


class SentenceHistoryGenerator:
    def run(
        self, tpsfs: list[TpsfECM], settings: Settings
    ) -> dict[int, list[TextUnit]]:
        sentence_history = {}
        global_new_sens = []
        progress = tqdm(tpsfs, "Generating sentence histories")
        for i, tpsf in enumerate(progress):
            # print(f"****{tpsf.revision_id}****")
            current_tus = [
                tu
                for tu in tpsf.textunits
                if tu.text_unit_type in (TextUnitType.SEN, TextUnitType.SEC)
            ]
            for ind, tu in enumerate(current_tus):
                tu.set_pos_in_text(ind + 1)
            # print([(tu.state, tu.text, tu.pos_in_text) for tu in current_tus])
            prev_tus = [
                tu
                for tu in tpsfs[i - 1].textunits
                if tu.text_unit_type in (TextUnitType.SEN, TextUnitType.SEC)
            ]

            number_new = 0
            if i == 0:
                for tu in current_tus:
                    uid = uuid.uuid1().int
                    sentence_history[uid] = [tu]
                    tu.set_id(uid)
            elif i > 0 and len(current_tus) == len(prev_tus):
                # print(f"Number of sentences ({len(current_tus)}) has not changed.")
                for ctu, ptu in zip(current_tus, prev_tus):
                    ctu.set_id(ptu.tu_id)
                    sentence_history[ptu.tu_id].append(ctu)
            elif i > 0 and len(current_tus) < len(prev_tus):
                # print(
                #     f"Sentence deletion detected: from {len(prev_tus)} to {len(current_tus)}"
                # )
                number_deleted = abs(len(current_tus) - len(prev_tus))
                for i, ctu in enumerate(current_tus):
                    if ctu.state == SenLabels.UNC_PRE:
                        ctu.set_id(prev_tus[i].tu_id)
                        sentence_history[prev_tus[i].tu_id].append(ctu)
                    elif ctu.state in [SenLabels.MOD, SenLabels.UNC_POST]:
                        ctu.set_id(prev_tus[i - number_new].tu_id)
                        sentence_history[prev_tus[i + number_deleted].tu_id].append(ctu)
            elif i > 0 and len(current_tus) > len(prev_tus):
                # print(
                #     f"Sentence creation detected: from {len(prev_tus)} to {len(current_tus)}"
                # )
                for i, ctu in enumerate(current_tus):
                    if ctu.state == SenLabels.UNC_PRE:
                        ctu.set_id(prev_tus[i].tu_id)
                        sentence_history[prev_tus[i].tu_id].append(ctu)
                    elif ctu.state in [SenLabels.NEW, SenLabels.SPLIT]:
                        number_new += 1
                        if ctu.text in global_new_sens:
                            for key, sens in sentence_history.items():
                                texts = [s.text for s in sens]
                                if ctu.text in texts:
                                    sentence_history[key].append(ctu)
                                    ctu.set_id(key)
                        else:
                            uid = uuid.uuid1().int
                            sentence_history[uid] = [ctu]
                            ctu.set_id(uid)
                        global_new_sens.append(ctu.text)
                    elif ctu.state in [SenLabels.MOD, SenLabels.UNC_POST]:
                        try:
                            prev_tu_id = prev_tus[i - number_new].tu_id
                            ctu.set_id(prev_tu_id)
                            sentence_history[prev_tu_id].append(ctu)
                        except IndexError:
                            print(
                                "ATTENTION: Detected error when counting textunits."
                                "Probably a textunit segementation error."
                                "Cannot assign the textunit to any sentence history."
                                "Creating a new sentence history"
                            )
                            uid = uuid.uuid1().int
                            sentence_history[uid] = [ctu]
                            ctu.set_id(uid)
        sentence_history = self.eliminate_duplicates(sentence_history)
        for sen_versions in sentence_history.values():
            for i, sen in enumerate(sen_versions):
                if i == 0:
                    ts_label = [
                        tpsf.ts.label
                        for tpsf in tpsfs
                        if tpsf.revision_id == sen.tpsf_id
                    ][0]
                    sen_ts = TransformingSequence(
                        sen.text,
                        ts_label,
                        0,
                        len(sen.text),
                        None,
                        None,
                        None,
                        None,
                        None,
                        settings,
                    )
                else:
                    sen_ts = retrieve_sen_ts(sen_versions[i - 1], sen, settings)
                sen.set_ts(sen_ts)
        return sentence_history

    def eliminate_duplicates(
        self, sentence_history: dict[int, list[TextUnit]]
    ) -> dict[int, list[TextUnit]]:
        sentence_history_duplicates_eliminated = {}
        for key, sens in sentence_history.items():
            sens_duplicates_eliminated: list[TextUnit] = []
            for s in sens:
                if s.text not in [sde.text for sde in sens_duplicates_eliminated]:
                    sens_duplicates_eliminated.append(s)
                else:
                    continue
            sentence_history_duplicates_eliminated[key] = sens_duplicates_eliminated
        return sentence_history_duplicates_eliminated

    def filter_senhis(
        self, senhis: dict[int, list[TextUnit]]
    ) -> dict[int, list[TextUnit]]:
        filtered_senhis = {}
        for sen_id, sen_versions in senhis.items():
            filtered_sen_versions = [s for s in sen_versions if s.ts.relevance is True]
            filtered_senhis[sen_id] = filtered_sen_versions
        return filtered_senhis
