import csv
from pathlib import Path
from typing import Generic, TypeVar

from wta.output_handler import names
from wta.output_handler.storage.base import BaseStorage
from wta.pipeline.names import SenSegmentTypes
from wta.pipeline.sentence_layer.sentence_histories.sentence_transformation import SentenceTransformation
from wta.pipeline.transformation_layer.text_transformation import TextTransformation, TextTransformationDict
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


class TextTranshisCsv(Csv[list[TextTransformationDict]]):
    def __init__(
        self,
        data: list[TextTransformationDict],
        settings: Settings,
    ) -> None:

        csv_file = (
            f"{settings.filename}_{names.TEXT_TRANSHIS}.csv"
        )
        super().__init__(
            settings.paths.text_transhis_csv_dir / csv_file, self.preprocess_data(data)
        )

    def preprocess_data(self, data: list[TextTransformation]) -> list[str]:
        print("Preprocessing the data...")
        fields = [
            "tpsf_id",
            "tpsf_text",
            "transformation_text",
            "scope",
            "ts_label",
            # "duration",
            # "length",
            # "point_of_insc",
            # "writing_speed_per_min",
            # "avg_pause_duration",
            # "preceding_pause",
            "bursts",
            "sentence_segments",
            "sentence_beginning",
            "sentence_middle",
            "sentence_end"
            ]
        rows = [fields]
        for tt in data:
            tpsf_id = tt.tpsf_id
            tpsf_text = tt.tpsf_text
            transformation_text = tt.ts.text
            scope = tt.scope
            ts_label = tt.ts.label
            # duration = tt.duration
            # length = tt.length
            # point_of_insc = tt.point_of_insc
            # preceding_pause = tt.ts.preceding_pause
            segments = [(seg.segment_type, seg.text) for seg in tt.sentence_segments]
            bursts = [ss.to_dict() for ss in tt.ts.bursts]
            first = True
            for seg in segments:
                sentence_beginning = seg[1] if seg[0] == SenSegmentTypes.SEN_BEG else ""
                sentence_middle = seg[1] if seg[0] == SenSegmentTypes.SEN_MID else ""
                sentence_end = seg[1] if seg[0] == SenSegmentTypes.SEN_END else ""
                tt_data = [
                    tpsf_id if first else "",
                    tpsf_text if first else "",
                    transformation_text if first else "",
                    scope if first else "",
                    ts_label if first else "",
                    # duration,
                    # length,
                    # point_of_insc,
                    # preceding_pause,
                    bursts,
                    [seg.segment_type for seg in tt.sentence_segments],
                    sentence_beginning,
                    sentence_middle,
                    sentence_end
                    ]
                rows.append(tt_data)
                first = False
        return rows


class SenTranshisCsv(Csv[dict[int, list[SentenceTransformation]]]):

    def __init__(
        self,
        data: list[str],
        settings: Settings,
    ) -> None:

        csv_file = (
            f"{settings.filename}_{names.SEN_TRANSHIS}.csv"
        )
        super().__init__(
            settings.paths.sen_transhis_csv_dir / csv_file, self.preprocess_data(data)
        )

    def preprocess_data(self, data: list[SentenceTransformation]) -> list[str]:
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
        for sen_id, sentrans in data.items():
            for st in sentrans:
                sentrans_data = [
                    st.spsf.tpsf_id,
                    sen_id,
                    st.spsf.text,
                    st.spsf.text_unit_type,
                    st.spsf.ts.text,
                    st.spsf.ts.startpos,
                    st.spsf.ts.endpos,
                    len(st.spsf.text),
                    st.operation,
                    st.sentence_segment
                ]
                rows.append(sentrans_data)
        return rows


class SenTranshisSegmentsCsv(Csv[dict[int, list[SentenceTransformation]]]):

    def __init__(
        self,
        data: list[str],
        settings: Settings,
    ) -> None:

        csv_file = (
            f"{settings.filename}_{names.SEN_TRANSHIS}_sensegments.csv"
        )
        super().__init__(
            settings.paths.sen_transhis_csv_dir / csv_file, self.preprocess_data(data)
        )

    def preprocess_data(self, data: list[SentenceTransformation]) -> list[str]:
        print("Preprocessing the data...")
        rows = []
        for sen_id, sentrans in data.items():
            sentence_segments = [sen_id] + [st.sentence_segment for st in sentrans]
            rows.append(sentence_segments)
        return rows
