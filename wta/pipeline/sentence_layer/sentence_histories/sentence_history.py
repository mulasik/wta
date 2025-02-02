import re
import uuid

from tqdm import tqdm  # type: ignore

from wta.pipeline.names import SenLabels
from wta.pipeline.sentence_layer.sentence_histories.sentence_transformation_classifier import (
    SenTransformationClassifier,
)
from wta.pipeline.transformation_layer.text_unit import SPSF, SPSFBuilder, TextUnitType
from wta.pipeline.transformation_layer.tpsf import TpsfECM
from wta.pipeline.transformation_layer.ts import TransformingSequence
from wta.pipeline.transformation_layer.ts_factory import retrieve_sen_ts
from wta.settings import Settings


class SentenceHistoryGenerator:
    def run(self, tpsfs: list[TpsfECM], settings: Settings) -> dict[int, list[SPSF]]:
        sentence_history_builder: dict[int, list[SPSFBuilder]] = {}
        sentence_history = {}
        global_new_sens = []
        prev_spsf_builders: list[SPSFBuilder] = []
        progress = tqdm(tpsfs, "Generating sentence histories")
        for i, tpsf in enumerate(progress):
            # print(f"****{tpsf.revision_id}****")
            current_spsf_builders = [
                SPSFBuilder(tu)
                for tu in tpsf.textunits
                if tu.text_unit_type in (TextUnitType.SEN, TextUnitType.SEC)
            ]
            for index, csb in enumerate(current_spsf_builders):
                csb.set_pos_in_text(index + 1)

            number_new = 0
            if i == 0:
                for csv in current_spsf_builders:
                    uid = uuid.uuid1().int
                    sentence_history_builder[uid] = [csv]
                    csv.set_id(uid)
                    global_new_sens.append(csv.text)
            elif i > 0 and len(current_spsf_builders) == len(prev_spsf_builders):
                # print(f"Number of sentences ({len(current_senver_builders)}) has not changed.")
                for csv, psv in zip(current_spsf_builders, prev_spsf_builders):
                    if psv.sen_id is not None:
                        csv.set_id(psv.sen_id)
                        sentence_history_builder[psv.sen_id].append(csv)
            elif i > 0 and len(current_spsf_builders) < len(prev_spsf_builders):
                # print(
                #     f"Sentence deletion detected: from {len(prev_spsf_builders)} to {len(current_spsf_builders)}"
                # )
                for ci, csv in enumerate(current_spsf_builders):
                    if csv.state == SenLabels.UNC_PRE:
                        prev_sen_id = prev_spsf_builders[ci].sen_id
                        if prev_sen_id is not None:
                            csv.set_id(prev_sen_id)
                            sentence_history_builder[prev_sen_id].append(csv)
                    elif csv.state in [SenLabels.MOD, SenLabels.UNC_POST]:
                        prev_spsf_ids = [
                            spsf.sen_id
                            for spsf in prev_spsf_builders
                            if re.search(csv.text, spsf.text) is not None
                        ]
                        prev_spsf_id = (
                            None if len(prev_spsf_ids) == 0 else prev_spsf_ids[0]
                        )
                        if prev_spsf_id is not None:
                            csv.set_id(prev_spsf_id)
                            sentence_history_builder[prev_spsf_id].append(csv)
            elif i > 0 and len(current_spsf_builders) > len(prev_spsf_builders):
                # print(
                #     f"Sentence creation detected: from {len(prev_spsf_builders)} to {len(current_senver_builders)}"
                # )
                for ci, ctu in enumerate(current_spsf_builders):
                    if ctu.state == SenLabels.UNC_PRE:
                        prev_sen_id = prev_spsf_builders[ci].sen_id
                        if prev_sen_id is not None:
                            ctu.set_id(prev_sen_id)
                            sentence_history_builder[prev_sen_id].append(ctu)
                    elif ctu.state in [SenLabels.NEW, SenLabels.SPLIT]:
                        number_new += 1
                        # TODO: consider a better method for tracking re-inserted sentences
                        # if ctu.text in global_new_sens:
                        #     for key, sens in sentence_history_builder.items():
                        #         texts = [s.text for s in sens]
                        #         if ctu.text in texts:
                        #             sentence_history_builder[key].append(ctu)
                        #             ctu.set_id(key)
                        # else:
                        uid = uuid.uuid1().int
                        sentence_history_builder[uid] = [ctu]
                        ctu.set_id(uid)
                        global_new_sens.append(ctu.text)
                    elif ctu.state in [SenLabels.MOD, SenLabels.UNC_POST]:
                        try:
                            prev_sen_id = prev_spsf_builders[ci - number_new].sen_id
                            if prev_sen_id is not None:
                                ctu.set_id(prev_sen_id)
                                sentence_history_builder[prev_sen_id].append(ctu)
                        except IndexError:
                            print(
                                "ATTENTION: Detected error when counting textunits. "
                                "Probably a textunit segementation error. "
                                "Cannot assign the textunit to any sentence history. "
                                "Creating a new sentence history."
                            )
                            uid = uuid.uuid1().int
                            sentence_history_builder[uid] = [ctu]
                            ctu.set_id(uid)
            prev_spsf_builders = current_spsf_builders
        sentence_history_builder = self.eliminate_duplicates(sentence_history_builder)
        for sen_id, senver_builders in sentence_history_builder.items():
            sentence_versions = []
            pre_completion = True
            for i, svb in enumerate(senver_builders):
                if i == 0:
                    ts_label = next(
                        tpsf.ts.label
                        for tpsf in tpsfs
                        if tpsf.revision_id == svb.tpsf_id
                    )
                    sen_ts = TransformingSequence(
                        svb.text,
                        ts_label,
                        0,
                        len(svb.text),
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        settings,
                    )
                else:
                    sen_ts = retrieve_sen_ts(senver_builders[i - 1], svb, settings)
                svb.set_ts(sen_ts)
                pre_completion, operation, sen_segment = SenTransformationClassifier().run(pre_completion, svb)
                svb.set_operation(operation)
                svb.set_sentence_segment(sen_segment)
                sentence_versions.append(svb.to_sentence_version())
            sentence_history[sen_id] = sentence_versions
        return sentence_history

    def eliminate_duplicates(
        self, sentence_history: dict[int, list[SPSFBuilder]]
    ) -> dict[int, list[SPSFBuilder]]:
        sentence_history_duplicates_eliminated = {}
        for key, sens in sentence_history.items():
            sens_duplicates_eliminated: list[SPSFBuilder] = []
            prev_sen: str = ""
            for s in sens:
                if s.text != prev_sen:
                    sens_duplicates_eliminated.append(s)
                prev_sen = s.text
            sentence_history_duplicates_eliminated[key] = sens_duplicates_eliminated
        return sentence_history_duplicates_eliminated

    def filter_senhis(self, senhis: dict[int, list[SPSF]]) -> dict[int, list[SPSF]]:
        filtered_senhis = {}
        for sen_id, sen_versions in senhis.items():
            filtered_sen_versions = [s for s in sen_versions if s.ts.relevance is True]
            filtered_senhis[sen_id] = filtered_sen_versions
        return filtered_senhis
