import copy
import re
import uuid
from typing import TypeAlias

from tqdm import tqdm

from wta.pipeline.BL2TL_projection.burst_factory import BurstFactory
from wta.pipeline.names import OperationTypes, TUState, TUTypes
from wta.pipeline.sentence_layer.sentence_histories.sentence_history import SentenceHistory
from wta.pipeline.sentence_layer.sentence_histories.spsf import SpsfBuilder
from wta.pipeline.SL2TL_projection.segment import Segment
from wta.pipeline.TL2SL_projection.operation_classifier import (
    OperationClassifier,
)
from wta.pipeline.transformation_layer.tpsf import Tpsf
from wta.pipeline.transformation_layer.ts import TransformingSequence

SentenceHistoryBuilders: TypeAlias = dict[int, list[SpsfBuilder]]


class SentenceHistoryGenerator:
    def run(self, tpsfs: list[Tpsf]) -> list[SentenceHistory]:
        sentence_history_builder: SentenceHistoryBuilders = {}
        prev_spsf_builders: list[SpsfBuilder] = []

        for i, tpsf in enumerate(tqdm(tpsfs, "Generating sentence histories")):
            # print(f"***** TPSF ID: {tpsf.id} *****")
            # print(f"TPSF TS:{tpsf.ts.label}\n{tpsf.ts.text}\n")
            result: list[SentenceHistory] = []
            # Extract current SPSFs and bursts within the TS of the given SPSF
            current_spsf_builders = self._extract_spsfs(tpsf)
            self._set_positions_of_spsfs(current_spsf_builders)
            self._project_bursts_on_spsfs(tpsf.ts, current_spsf_builders, i)

            for cur in current_spsf_builders:
                # print(f"Current SPSF builder:\n{str(cur)}\n")
                if cur.state in [TUState.UNC_PRE, TUState.UNC_POST]:
                    matching_sen_ids = [prev.sen_id for prev in prev_spsf_builders if prev.text == cur.text]
                    matching_sen_id = matching_sen_ids[0] if matching_sen_ids else None
                    if matching_sen_id is not None:
                        # print(f"Found matching previous SPSF with sen_id {matching_sen_id} and text:\n{[prev.text for prev in prev_spsf_builders if prev.sen_id == matching_sen_id][0]}\n")
                        sentence_history_builder[matching_sen_id].append(cur)
                        cur.set_id(matching_sen_id)

            if i == 0:
                # print("""Case 1: First TPSF version → all sentences are new.""")
                """
                Case 1: First TPSF version → all sentences are new.
                Assign new IDs to all SPSFs and initiate new histories for each of them.
                """
                for spsf in current_spsf_builders:
                    self._assign_new_id(spsf, sentence_history_builder)
            elif len(current_spsf_builders) == len(prev_spsf_builders):
                # print("""Case 2: Same number of sentences → only modifications.""")
                # self._handle_equal_sentence_count(current_spsf_builders, prev_spsf_builders, sentence_history_builder)
                """Case 2: Same number of sentences → only modifications."""
                for cur, prv in zip(current_spsf_builders, prev_spsf_builders):
                    if prv.sen_id and cur.state == TUState.MOD:
                        cur.set_id(prv.sen_id)
                        sentence_history_builder[prv.sen_id].append(cur)
            elif len(current_spsf_builders) < len(prev_spsf_builders):
                self._handle_deletions(current_spsf_builders, prev_spsf_builders, sentence_history_builder, tpsf)
            else:  # len(current) > len(prev)
                self._handle_insertions(current_spsf_builders, prev_spsf_builders, sentence_history_builder)

            prev_spsf_builders = current_spsf_builders

        for sen_id, builders in sentence_history_builder.items():
            versions = []
            pre_completion = True
            for builder in builders:
                if builder.state in [TUState.UNC_PRE, TUState.UNC_POST]:
                    builder.set_operation(OperationTypes.NON)
                    builder.set_ts(None)
                    builder.set_production_time(None)
                    versions.append(builder.to_spsf())
                else:
                    ts = tpsfs[builder.tpsf_id].ts
                    pre_completion, op = OperationClassifier().run(pre_completion, builder, ts)
                    builder.set_operation(op)
                    production_time = None if not builder.ts or builder.ts.endtime is None or builder.ts.starttime is None else builder.ts.endtime - builder.ts.starttime
                    builder.set_production_time(production_time)
                    # print(str(builder))
                    versions.append(builder.to_spsf())
            result.append(SentenceHistory(sen_id, versions))

        return result

    def _extract_spsfs(self, tpsf: Tpsf) -> list[SpsfBuilder]:
        return [SpsfBuilder(tu) for tu in tpsf.tus if tu.type in (TUTypes.SEN, TUTypes.SEC)]

    def _set_positions_of_spsfs(self, spsfs: list[SpsfBuilder]) -> None:
        for idx, spsf in enumerate(spsfs, 1):
            spsf.set_pos_in_text(idx)

    def _project_bursts_on_spsfs(self, ts: TransformingSequence, spsfs: list[SpsfBuilder], tpsf_id: int) -> None:
        for spsf in spsfs:
            if spsf.ts is not None:
                if len(ts.pauses) > 0 and spsf.ts.relative_endpos is not None:
                    relevant_pauses = ts.pauses[spsf.ts.relative_startpos:spsf.ts.relative_endpos+1]
                    preceding_pause = None if len(relevant_pauses) == 0 else relevant_pauses[0]
                    following_pause = ts.pauses[spsf.ts.relative_endpos+1:spsf.ts.relative_endpos+2][0] if len(ts.pauses) > spsf.ts.relative_endpos+1 else spsf.ts.following_pause
                    segment_bursts = BurstFactory().run(spsf.ts.text, relevant_pauses, following_pause, tpsf_id, ts.label)
                else:
                    relevant_pauses, preceding_pause, following_pause, segment_bursts = None, None, None, []
                    BurstFactory().run(spsf.ts.text, relevant_pauses, following_pause, tpsf_id, ts.label)
                spsf.ts.set_following_pause(following_pause)
                spsf.ts.set_preceding_pause(preceding_pause)
                spsf.ts.set_bursts(segment_bursts)


    def _assign_new_id(self, spsf: SpsfBuilder, history: SentenceHistoryBuilders) -> None:
        uid = uuid.uuid1().int
        spsf.set_id(uid)
        history[uid] = [spsf]

    def _handle_deletions(
        self,
        current: list[SpsfBuilder],
        prev: list[SpsfBuilder],
        history: SentenceHistoryBuilders,
        tpsf: Tpsf
    ) -> None:
        """Case 3: Fewer sentences → some deletions/merges."""
        candidates = []
        prev_modified = None
        for cur in current:
            if cur.state == TUState.MOD:
                candidates = [psv for psv in prev if re.search(re.escape(cur.text), psv.text)]
                prev_modified = candidates[0] if len(candidates) > 0 else None
                # print("Candidates:", [str(c) for c in candidates])
                if len(candidates) == 1 and candidates[0].sen_id:
                    cur.set_id(candidates[0].sen_id)
                    history[candidates[0].sen_id].append(cur)
                else:
                    print(
                        f"Could not match deleted SPSF:\n|{cur.text}|\nProbably due to a merge. Creating new history."
                    )
                    self._assign_new_id(cur, history)
        if prev_modified is None:
            for prv in prev:
                if prv.text not in [cur.text for cur in current]:
                    del_ts = Segment(prv.text, prv.tu_type, prv.startpos, prv.endpos, prv.startpos, prv.endpos, None, None, None, None)
                    del_spsf = copy.deepcopy(prv)
                    del_spsf.set_text("")
                    del_spsf.set_state(TUState.DEL)
                    del_spsf.set_tpsf_id(tpsf.id)
                    operation = OperationTypes.PRECON_DEL if del_spsf.tu_type == TUTypes.SEC else OperationTypes.CON_DEL
                    del_spsf.set_operation(operation)
                    del_spsf.set_ts(del_ts)
                    del_spsf.set_production_time(0.0)
                    if prv.sen_id:
                        history[prv.sen_id].append(del_spsf)

    def _handle_insertions(
        self,
        current: list[SpsfBuilder],
        prev: list[SpsfBuilder],
        history: SentenceHistoryBuilders,
    ) -> None:
        """Case 4: More sentences → some new insertions."""
        number_new = 0
        for idx, cur in enumerate(current):
            if cur.state == TUState.NEW:
                number_new += 1
                self._assign_new_id(cur, history)
            elif cur.state == TUState.MOD:
                try:
                    prev_sen_id = prev[idx - number_new].sen_id
                    if prev_sen_id:
                        cur.set_id(prev_sen_id)
                        history[prev_sen_id].append(cur)
                except IndexError:
                    print(
                        f"Indexing error while handling insertions. SPSF:\n|{cur.text}|\n"
                        "Probably a segmentation error. Creating new history."
                    )
                    self._assign_new_id(cur, history)


    # Add aggreation of irrelevant TSs into the sentence histories
    # analgue to tpsf_factory.py

    # Implement filtering based on TS relevance
    # def filter_senhis(self, senhis: dict[int, list[Spsf]]) -> dict[int, list[Spsf]]:
    #     filtered_senhis: dict[int, list[Spsf]] = {}
    #     for sen_id, sen_versions in senhis.items():
    #         filtered_sen_versions = [s for s in sen_versions if s.ts.relevance is True]
    #         filtered_senhis[sen_id] = filtered_sen_versions
    #     return filtered_senhis
