from abc import ABC
from pathlib import Path
from typing import cast

import numpy as np
from bs4 import BeautifulSoup

from ..sentence_histories.text_unit import SPSF, TextUnitType
from ..text_history.action import (
    Action,
    Append,
    Deletion,
    Insertion,
    Midletion,
    Navigation,
)
from ..text_history.tpsf import TpsfECM, TpsfPCM


class Statistics(ABC):  # noqa: B024
    """
    Statistics contain:
        Basic statistics
        - Edit Capturing Mode: number text revisions (all)
        - Pause Capturing Mode: number text revisions (all)
        - Edit Capturing Mode: number text revisions (filtered)
        Events
        - Number events, number keystrokes, replacements and inserts
        Pauses
        - Pauses (avg, min, max)
        Transforming sequences
        - TS length (avg)
        - Insertions number
        - Number inserted characters
        - Deletions number
        - Number deleted characters
        Sentences
        - Number detected sentences
        - Number sentences in the final version
        - Mean number versions per sentence
        - Number unchanged sentences
        - Number changed sentences *
        - Number deleted sentences *
    """


class BasicStatistics(Statistics):
    def __init__(
        self,
        texthis: list[TpsfECM],
        texthis_filtered: list[TpsfECM],
    ) -> None:
        self.texthis = texthis
        self.texthis_filtered = texthis_filtered
        self.data = self.retrieve_stats()

    def retrieve_stats(self) -> dict[str, int | float | str]:
        return {
            "num_tpsfs": len(self.texthis),
            "num_tpsfs_filtered": len(self.texthis_filtered),
        }


class EventStatistics(Statistics):
    def __init__(self, idfx: Path) -> None:
        self.idfx = idfx
        self.data = self.retrieve_stats()

    def retrieve_stats(self) -> dict[str, int | float | str]:
        with self.idfx.open() as fp:
            soup = BeautifulSoup(fp, features="lxml")
            events = soup.find_all("event")
        num_events = len(events)
        num_keystrokes, num_replacements, num_insertions = 0, 0, 0
        for e in events:
            if e["type"] == "keyboard":
                num_keystrokes += 1
            if e["type"] == "replacement":
                num_replacements += 1
            if e["type"] == "insert":
                num_insertions += 1
        return {
            "num_events": num_events,
            "num_keystrokes": num_keystrokes,
            "num_replacements": num_replacements,
            "num_insertions": num_insertions,
        }


class PauseStatistics(Statistics):
    def __init__(self, texthis: list[TpsfPCM], actions: list[Action]) -> None:
        self.texthis = texthis
        self.data = self.retrieve_stats(actions)

    def retrieve_stats(self, actions: list[Action]) -> dict[str, int | float | str]:
        pauses: list[float] = []
        total_pauses_duration: float = 0
        actions_pause_unknown: int = 0
        for act in actions:
            if (
                isinstance(act, (Append, Insertion, Deletion, Midletion, Navigation))
                and act.pause is not None
            ):
                pauses.append(act.pause)
                total_pauses_duration += act.pause
            else:
                actions_pause_unknown += 1
        avg_pause_duration = round(total_pauses_duration / len(pauses), 2)
        return {
            "num_tpsfs": len(self.texthis),
            "avg_duration": avg_pause_duration,
            "max_duration": max(pauses),
            "min_duration": min(pauses),
            "events_wo_pause_info": actions_pause_unknown,
        }


class TSStatistics(Statistics):
    def __init__(self, texthis: list[TpsfECM]) -> None:
        self.texthis = texthis
        self.data = self.retrieve_stats()

    def retrieve_stats(self) -> dict[str, int | float | str]:
        transforming_sequences_texts = []
        num_nonempty_ts = 0
        num_ins, number_dels, num_apps = 0, 0, 0
        num_ins_chars, num_del_chars, num_app_chars = 0, 0, 0
        for tpsf in self.texthis:
            if len(tpsf.ts.text) > 0:
                num_nonempty_ts += 1
                transforming_sequences_texts.append(tpsf.ts.text)
            if tpsf.ts.label == "insertion":
                num_ins += 1
                num_ins_chars += len(tpsf.ts.text)
            if tpsf.ts.label == "deletion":
                number_dels += 1
                num_del_chars += len(tpsf.ts.text)
            if tpsf.ts.label == "append":
                num_apps += 1
                num_app_chars += len(tpsf.ts.text)
        total_ts_length = 0
        for tst in transforming_sequences_texts:
            total_ts_length += len(tst)
        avg_ts_len = round(total_ts_length / len(transforming_sequences_texts))
        return {
            "num_nonempty_ts": num_nonempty_ts,
            "avg_ts_len": avg_ts_len,
            "num_ins": num_ins,
            "num_dels": number_dels,
            "num_apps": num_apps,
            "num_ins_chars": num_ins_chars,
            "num_del_chars": num_del_chars,
            "num_app_chars": num_app_chars,
        }


class SentenceStatistics(Statistics):
    def __init__(self, texthis: list[TpsfECM], senhis: dict[int, list[SPSF]]) -> None:
        self.texthis = texthis
        self.senhis = senhis
        self.data = self.retrieve_stats()

    def retrieve_stats(self) -> dict[str, int | float | str]:
        detected_sens = len(self.senhis)
        num_unchanged_sens = 0
        num_sen_versions = []
        max_num_sen_versions = 0
        num_potentially_erroneous_sens = 0
        sen_with_most_versions = ""
        for sh in self.senhis.values():
            if len(sh) == 1:
                num_unchanged_sens += 1
            if len(sh) == 2:
                num_potentially_erroneous_sens += 1
            if len(sh) > max_num_sen_versions:
                max_num_sen_versions = len(sh)
                sen_with_most_versions = sh[-1].text
            num_sen_versions.append(len(sh))
        mean_num_sentence_versions = cast(float, round(np.mean(num_sen_versions), 2))
        final_num_sentences = len(
            [
                tu
                for tu in self.texthis[-1].textunits
                if tu.text_unit_type in (TextUnitType.SEN, TextUnitType.SEC)
            ]
        )
        return {
            "detected_sens": detected_sens,
            "final_num_sentences": final_num_sentences,
            "num_potentially_erroneous_sens": num_potentially_erroneous_sens,
            "max_num_sen_versions": max_num_sen_versions,
            "sen_with_most_versions": sen_with_most_versions,
            "mean_num_sentence_versions": mean_num_sentence_versions,
            "num_unchanged_sens": num_unchanged_sens,
        }
