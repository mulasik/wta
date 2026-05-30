from typing import TypedDict

from wta.pipeline.BL2TL_projection.burst import Burst, BurstDict
from wta.pipeline.names import OperationTypes, TUTypes
from wta.pipeline.sentence_layer.sentence_histories.spsf import Spsf, SpsfDict


class SentenceHistoryDict(TypedDict):
    sen_id: int | None
    senversions: list[SpsfDict]
    production_time: float | None
    bursts: list[BurstDict]
    bursts_with_significant_preceding_pauses: list[BurstDict]
    number_deleted_characters: int
    number_produced_characters: int
    deletion_ratio: float
    number_precontextual_revisions: int
    number_contextual_revisions: int
    number_sentence_reopenings: int
    sentence_production_pattern: str


class SentenceHistory:

    def __init__(self, sen_id: int, senversions: list[Spsf]) -> None:
        self.sen_id: int = sen_id
        self.senversions: list[Spsf] = senversions
        self.production_time: float | None = self.calculate_production_time()
        self.bursts: list[Burst] = self.retrieve_bursts()
        self.bursts_with_significant_preceding_pauses: list[Burst] = self.retrieve_bursts_with_significant_preceding_pauses()
        self.number_bursts: int = len(self.bursts)
        self.number_deleted_characters: int = self.calculate_number_of_deleted_characters()
        self.number_produced_characters: int = self.calculate_number_of_produced_characters()
        self.deletion_ratio: float = self.number_deleted_characters / self.number_produced_characters if self.number_produced_characters > 0 else 0.0
        self.number_precontextual_revisions: int = self.extract_number_of_precontextual_revisions()
        self.number_contextual_revisions: int = self.extract_number_of_contextual_revisions()
        self.number_sentence_reopenings: int = self.extract_number_of_sentence_reopenings()
        self.sentence_production_pattern: str = self.extract_sentence_production_pattern()
        self.final_sentence_length: int = len(self.senversions[-1].text) if len(self.senversions) > 0 else 0
        # dict_version = self.to_dict()
        # for key, value in dict_version.items():
        #      if isinstance(value, list):
        #          print(f"{key}: {[str(v) for v in value]}")
        #      else:
        #           print(f"{key}: {value}")


    def calculate_production_time(self) -> float | None:
        # production time is calculated as the sum of the production times of all sentence versions, which is the time between the start and end time of the TS of each sentence version.
        # If any sentence version does not have a valid production time, the function returns None.
        production_time = 0.0
        for senver in self.senversions:
            production_time += senver.production_time if senver.production_time is not None else 0.0
        return production_time

    def retrieve_bursts(self) -> list[Burst]:
        bursts = []
        for senver in self.senversions:
            if senver.ts and senver.ts.bursts:
                bursts.extend(senver.ts.bursts)
        return bursts

    def retrieve_bursts_with_significant_preceding_pauses(self) -> list[Burst]:
        bursts_with_significant_preceding_pauses = []
        for senver in self.senversions:
            if senver.ts and senver.ts.bursts:
                for b in senver.ts.bursts:
                    if (b.preceding_pause and b.preceding_pause > 2.0):
                        bursts_with_significant_preceding_pauses.append(b)
        return bursts_with_significant_preceding_pauses

    def calculate_number_of_deleted_characters(self) -> int:
        number_of_deleted_characters = 0
        for senver in self.senversions:
            if senver.operation in [OperationTypes.CON_DEL, OperationTypes.PRECON_DEL]:
                number_of_deleted_characters += len(senver.ts.text) if senver.ts else 0
        return number_of_deleted_characters

    def calculate_number_of_produced_characters(self) -> int:
        number_of_produced_characters = 0
        for senver in self.senversions:
            if senver.operation in [OperationTypes.PROD, OperationTypes.PRECON_INS, OperationTypes.CON_INS]:
                number_of_produced_characters += len(senver.ts.text) if senver.ts else 0
        return number_of_produced_characters

    def extract_number_of_precontextual_revisions(self) -> int:
        number_of_precontextual_revisions = 0
        for senver in self.senversions:
            if senver.operation in [OperationTypes.PRECON_DEL, OperationTypes.PRECON_INS]:
                number_of_precontextual_revisions += 1
        return number_of_precontextual_revisions

    def extract_number_of_contextual_revisions(self) -> int:
        number_of_contextual_revisions = 0
        for senver in self.senversions:
            if senver.operation in [OperationTypes.CON_DEL, OperationTypes.CON_INS]:
                number_of_contextual_revisions += 1
        return number_of_contextual_revisions

    def extract_number_of_sentence_reopenings(self) -> int:
        number_of_sentence_reopenings = 0
        for i, senver in enumerate(self.senversions):
            if senver.tu_type == TUTypes.SEC and i>0 and self.senversions[i-1].tu_type == TUTypes.SEN:
                number_of_sentence_reopenings += 1
        return number_of_sentence_reopenings

    def extract_sentence_production_pattern(self) -> str:
        sentence_production_pattern = []
        for i, senver in enumerate(self.senversions):
            if senver.tu_type == TUTypes.SEN and (i == 0 or self.senversions[i-1].tu_type != TUTypes.SEN):
                sentence_production_pattern.append("SEN")
            if senver.tu_type == TUTypes.SEC and (i == 0 or self.senversions[i-1].tu_type != TUTypes.SEC):
                sentence_production_pattern.append("SEC")
        return "-".join(sentence_production_pattern)

    def to_dict(self) -> SentenceHistoryDict:
        return {
            "sen_id": self.sen_id,
            "senversions": [s.to_dict() for s in self.senversions],
            "production_time": self.production_time,
            "bursts": [b.to_dict() for b in self.bursts],
            "bursts_with_significant_preceding_pauses": [b.to_dict() for b in self.bursts_with_significant_preceding_pauses],
            "number_deleted_characters": self.number_deleted_characters,
            "number_produced_characters": self.number_produced_characters,
            "deletion_ratio": self.deletion_ratio,
            "number_precontextual_revisions": self.number_precontextual_revisions,
            "number_contextual_revisions": self.number_contextual_revisions,
            "number_sentence_reopenings": self.number_sentence_reopenings,
            "sentence_production_pattern": self.sentence_production_pattern
        }
