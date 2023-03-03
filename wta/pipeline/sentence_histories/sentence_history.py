import uuid
from itertools import zip_longest

from tqdm import tqdm

from wta.pipeline.sentence_histories.text_unit import TextUnit

from ..names import SenLabels
from ..text_history.tpsf import TpsfECM


class SentenceHistoryGenerator:
    def run(self, tpsfs: list[TpsfECM]) -> dict[int, list[TextUnit]]:
        sentence_history = {}
        global_new_sens = []
        progress = tqdm(tpsfs, "Generating sentence histories")
        for i, tpsf in enumerate(progress):
            print([(tu.state.upper(), tu.text) for tu in tpsf.textunits])
            if i == 0:
                for tu in tpsf.textunits:
                    uid = uuid.uuid1().int
                    sentence_history[uid] = [tu]
                    tu.set_id(uid)
            elif i > 0 and len(tpsf.textunits) == len(tpsfs[i - 1].textunits):
                print(f"Number of sentences ({len(tpsf.textunits)}) has not changed.")
                for ctu, ptu in zip(tpsf.textunits, tpsfs[i - 1].textunits):
                    ctu.set_id(ptu.tu_id)
            elif i > 0 and len(tpsf.textunits) < len(tpsfs[i - 1].textunits):
                print(
                    f"Sentence deletion detected: from {len(tpsfs[i-1].textunits)} to {len(tpsf.textunits)}"
                )
                for ctu, ptu in zip_longest(tpsf.textunits, tpsfs[i - 1].textunits):
                    if ctu.state == SenLabels.UNC_PRE:
                        ctu.set_id(ptu.tu_id)
                    elif ctu.state == SenLabels.MOD:
                        ...
            elif i > 0 and len(tpsf.textunits) > len(tpsfs[i - 1].textunits):
                print(
                    f"Sentence creation detected: from {len(tpsfs[i - 1].textunits)} to {len(tpsf.textunits)}"
                )
                for ctu, ptu in zip_longest(tpsf.textunits, tpsfs[i - 1].textunits):
                    if ctu.state == SenLabels.UNC_PRE:
                        try:
                            ctu.set_id(ptu.tu_id)
                        except AttributeError:
                            continue
                    elif ctu.state == SenLabels.NEW:
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
            else:
                ...  # TODO
        # return self.eliminate_duplicates(sentence_history)

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
