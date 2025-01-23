import csv
from pathlib import Path
from typing import Generic, TypeVar

from wta.output_handler import names
from wta.output_handler.storage.base import BaseStorage
from wta.pipeline.transformation_layer.text_unit import SPSF
from wta.pipeline.transformation_layer.tpsf import TpsfECM
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


class TexthisCsv(Csv[list[TpsfECM]]):
    def __init__(
        self,
        data: list[TpsfECM],
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

    def preprocess_data(self, data: list[TpsfECM]) -> list[str]:
        print("Preprocessing the data...")
        fields = [
            "tpsf_id",
            "tpsf_text",
            "ts_text",
            "scope",
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
            tpsf_id = tpsf.revision_id
            tpsf_text = tpsf.text
            ts_text = tpsf.ts.text
            scope = tpsf.transformation_scope
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
                    scope if first else "",
                    ts_label if first else "",
                    # duration,
                    # length,
                    # point_of_insc,
                    # preceding_pause,
                    bursts,
                    [seg.segment_type for seg in tpsf.sentence_segments]
            ]
            rows.append(tt_data)
        return rows


class SenhisCsv(Csv[dict[int, list[SPSF]]]):

    def __init__(
        self,
        data: dict[int, list[SPSF]],
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

    def preprocess_data(self, data: dict[int, list[SPSF]]) -> list[str]:
        print("Preprocessing the data...")
        fields = [
            "tpsf_id",
            "sen_id",
            "sen_text",
            "sen_tu_type",
            "sen_ts",
            "ts_startpos",
            "ts_endpos",
            "sen_len",
            "operation",
            "sentence_segment",
            ]
        rows = [fields]
        for sen_id, senvers in data.items():
            for sv in senvers:
                sentrans_data = [
                    sv.tpsf_id,
                    sen_id,
                    sv.text,
                    sv.text_unit_type,
                    sv.ts.text,
                    sv.ts.startpos,
                    sv.ts.endpos,
                    len(sv.text),
                    sv.operation,
                    sv.sentence_segment
                ]
                rows.append(sentrans_data)
        return rows

