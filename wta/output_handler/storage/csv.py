import csv
from pathlib import Path
from typing import Generic, TypeVar

from wta.output_handler import names
from wta.output_handler.storage.base import BaseStorage
from wta.pipeline.BL2TL_projection.burst import Burst
from wta.pipeline.sentence_layer.sentence_histories.sentence_history import SentenceHistory
from wta.pipeline.sentence_layer.sentence_histories.spsf import Spsf
from wta.pipeline.transformation_layer.tpsf import Tpsf
from wta.settings import Settings

_T = TypeVar("_T")


class Csv(BaseStorage, Generic[_T]):
    def __init__(self, filepath: Path, data: _T) -> None:
        self.filepath = filepath
        self.data = data

    def to_file(self) -> None:
        print(f"Will save as {self.filepath}")
        with self.filepath.open("w") as f:
            write = csv.writer(f)
            write.writerow(self.data[0])
            write.writerows(self.data[1:])


class TexthisCsv(Csv[list[Tpsf]]):
    def __init__(
        self,
        data: list[Tpsf],
        settings: Settings,
        mode: str = "ecm",
        filtered: bool = False,
    ) -> None:

        self.mode = mode
        filter_label = "" if not filtered else "_filtered"
        csv_file = (
            f"{settings.filename}_{names.TEXTHIS}_{self.mode}{filter_label}.csv"
        )
        super().__init__(
            settings.paths.texthis_csv_dir / csv_file, self.preprocess_data(data)
        )

    def preprocess_data(self, data: list[Tpsf]) -> list[str]:
        print("Preprocessing the data...")
        fields = [
            "tpsf_id",
            "tpsf_text",
            "ts_text",
            "ts_label",
            # "duration",
            # "length",
            # "point_of_insc",
            # "writing_speed_per_min",
            # "avg_pause_duration",
            # "preceding_pause",
            "bursts",
            "sentence_segments"
            ]
        rows = [fields]
        for tpsf in data:
            tpsf_id = tpsf.id
            tpsf_text = tpsf.text
            ts_text = tpsf.ts.text
            ts_label = tpsf.ts.label
            # duration = tt.duration
            # length = tt.length
            # point_of_insc = tt.point_of_insc
            # preceding_pause = tt.ts.preceding_pause
            bursts = [ss.to_dict() for ss in tpsf.ts.bursts]
            first = True
            tt_data = [
                    tpsf_id if first else "",
                    tpsf_text if first else "",
                    ts_text if first else "",
                    ts_label if first else "",
                    # duration,
                    # length,
                    # point_of_insc,
                    # preceding_pause,
                    bursts,
                    [seg.segment_type for seg in tpsf.ts.segments]
            ]
            rows.append(tt_data)
        return rows


class BurstlistCsv(Csv[list[Burst]]):
    def __init__(
        self,
        data: list[Burst],
        settings: Settings,
    ) -> None:
        csv_file = (
            f"{settings.filename}_{names.BURSTLIST}.csv"
        )
        super().__init__(
            settings.paths.burstlist_csv_dir / csv_file, self.preprocess_data(data)
        )

    def preprocess_data(self, data: list[Burst]) -> list[str]:
        print("Preprocessing the data...")
        fields = [
            "tpsf_id",
            "ts_label",
            "preceding_pause",
            "content",
            "following_pause"
            ]
        rows = [fields]
        for burst in data:
            tpsf_id = burst.tpsf_id
            ts_label = burst.ts_label
            preceding_pause = burst.preceding_pause
            content = f"|{burst.content}|"
            following_pause = burst.following_pause
            tt_data = [
                tpsf_id,
                ts_label,
                preceding_pause,
                content,
                following_pause
            ]
            rows.append(tt_data)
            if following_pause is not None and following_pause > 2.0:
                pause_burst_marker = [
                    "------",
                    "------",
                    "------",
                    "------",
                    "------"
                ]
                rows.append(pause_burst_marker)
        return rows


class SenhisCsv(Csv[dict[int, list[Spsf]]]):

    def __init__(
        self,
        data: list[SentenceHistory],
        settings: Settings,
        view_mode: str = "normal",
        filtered: bool = False,
    ) -> None:

        self.view_mode = "" if view_mode == "normal" else f"_{view_mode}"
        filter_label = "" if not filtered else "_filtered"
        csv_file = (
            f"{settings.filename}_{names.SENHIS}{self.view_mode}{filter_label}.csv"
        )
        super().__init__(
            settings.paths.senhis_csv_dir / csv_file, self.preprocess_data(data)
        )

    def preprocess_data(self, data: list[SentenceHistory]) -> list[str]:
        print("Preprocessing the data...")
        fields = [
            "tpsf_id",
            "sen_id",
            "pos_in_text",
            "state",
            "sen_text",
            "sen_tu_type",
            "sen_ts",
            "ts_startpos",
            "ts_endpos",
            "sen_len",
            "segment_type",
            "operation",
            "ts_preceding_pause",
            "ts_following_pause",
            "no_pauses_within_sen_ts",
            "sen_ts_bursts"
            ]
        rows = [fields]
        for senhis in data:
            for sv in senhis.senversions:
                sentrans_data = [
                    sv.tpsf_id,
                    senhis.sen_id,
                    sv.pos_in_text,
                    sv.state,
                    sv.text,
                    sv.tu_type,
                    sv.ts.text if sv.ts else None,
                    sv.ts.startpos if sv.ts else None,
                    sv.ts.endpos if sv.ts else None,
                    len(sv.text),
                    sv.ts.segment_type if sv.ts and sv.ts.segment_type else None,
                    sv.operation,
                    sv.ts.preceding_pause if sv.ts else None,
                    sv.ts.following_pause if sv.ts else None,
                    0 if sv.ts is None or sv.ts.bursts is None else len(sv.ts.bursts)-1,
                    [] if sv.ts is None or sv.ts.bursts is None else [ss.to_dict() for ss in sv.ts.bursts]
                ]
                rows.append(sentrans_data)
        return rows

