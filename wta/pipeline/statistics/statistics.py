from abc import ABC, abstractmethod
from pathlib import Path
from typing import cast

import numpy as np
from bs4 import BeautifulSoup

from ..sentence_histories.text_unit import TextUnit
from ..text_history.tpsf import TpsfECM


class Statistics(ABC):
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

    @abstractmethod
    def retrieve_stats(self) -> dict[str, int | float | str]:
        pass


class BasicStatistics(Statistics):
    def __init__(
        self,
        texthis: list[TpsfECM],
        texthis_filtered: list[TpsfECM],
        texthis_pcm: list[TpsfECM],
    ) -> None:
        self.texthis = texthis
        self.texthis_filtered = texthis_filtered
        self.texthis_pcm = texthis_pcm
        self.data = self.retrieve_stats()

    def retrieve_stats(self) -> dict[str, int | float | str]:
        return {
            "num_tpsfs": len(self.texthis),
            "num_tpsfs_filtered": len(self.texthis_filtered),
            "num_tpsfs_pcm": len(self.texthis_pcm),
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
    def __init__(self, texthis: list[TpsfECM]) -> None:
        self.texthis = texthis
        self.data = self.retrieve_stats()

    def retrieve_stats(self) -> dict[str, int | float | str]:
        pauses = []
        total_pauses_duration = 0
        for tpsf in self.texthis:
            if tpsf.preceeding_pause:
                pauses.append(tpsf.preceeding_pause)
                total_pauses_duration += tpsf.preceeding_pause
        avg_pause_duration = round(total_pauses_duration / len(pauses))
        return {
            "avg_duration": avg_pause_duration,
            "max_duration": max(pauses),
            "min_duration": min(pauses),
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
            if len(tpsf.ts.content) > 0:
                num_nonempty_ts += 1
                transforming_sequences_texts.append(tpsf.ts.content)
            if tpsf.ts.label == "insertion":
                num_ins += 1
                num_ins_chars += len(tpsf.ts.content)
            if tpsf.ts.label == "deletion":
                number_dels += 1
                num_del_chars += len(tpsf.ts.content)
            if tpsf.ts.label == "append":
                num_apps += 1
                num_app_chars += len(tpsf.ts.content)
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
    def __init__(
        self, texthis: list[TpsfECM], senhis: dict[int, list[TextUnit]]
    ) -> None:
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
                sen_with_most_versions = sh[-1].content
            num_sen_versions.append(len(sh))
        mean_num_sentence_versions = cast(float, round(np.mean(num_sen_versions), 2))
        final_num_sentences = len(self.texthis[-1].sentence_list)
        return {
            "detected_sens": detected_sens,
            "final_num_sentences": final_num_sentences,
            "num_potentially_erroneous_sens": num_potentially_erroneous_sens,
            "max_num_sen_versions": max_num_sen_versions,
            "sen_with_most_versions": sen_with_most_versions,
            "mean_num_sentence_versions": mean_num_sentence_versions,
            "num_unchanged_sens": num_unchanged_sens,
        }
