from tqdm import tqdm

from ...settings import Settings
from ..sentence_histories.text_unit import TextUnit
from ..sentence_histories.text_unit_factory import TextUnitFactory
from .action import Action
from .tpsf import TpsfECM, TpsfPCM
from .ts import TransformingSequence


class ECMFactory:
    """
    A class to retrieve text versions (TPSFs) in Edit Capturing Mode (ECM).
    TPSFs are generated based on transforming sequences (TSs).
    There are 4 types of TSs where text is produced:
    - append
    - insertion
    - pasting
    There are 2 types of TSs where text is deleted:
    - deletion
    - midletion
    There is 1 type of TSs where text is deleted and produced at the same time:
    - replacement
    There is 1 type of TSs where no changes to text are made:
    - navigation
    """

    @staticmethod
    def run(tss: list[TransformingSequence], settings: Settings) -> list[TpsfECM]:
        """
        Generates a list of objects of type Tpsf based on a list of transforming sequences.
        Args:
            tss: a list of objects of type TransformingSequence
        Returns:
            a list of objects of type TpsfECM
        """
        output: list[str] = []
        tpsfs = []
        aggregated_tss: list[TransformingSequence] = []
        tss = [ts for ts in tss if ts.label != "navigation"]
        prev_tpsf = None
        for i, ts in enumerate(tqdm(tss, "Extracting tpsfs")):
            if ts.label in ["append", "insertion", "pasting"]:
                startpos = ts.startpos
                for char in ts.text:
                    output.insert(startpos, char)
                    startpos += 1
            elif ts.label in ["deletion", "midletion"]:
                text = output[ts.startpos : ts.endpos + 1]
                ts.set_text("".join(text))
                del output[ts.startpos : ts.endpos + 1]
            elif ts.label == "replacement":
                del output[ts.startpos : ts.endpos + 1]
                startpos = ts.startpos
                for char in ts.text:
                    output.insert(startpos, char)
                    startpos += 1
            content = "".join(output)
            text_units = TextUnitFactory().run(content, i, ts, prev_tpsf, settings)
            relevance = (
                ts.relevance
                if settings.config["enable_spellchecking"] is False
                else _determine_tpsf_relevance(text_units, settings)
            )
            tpsf = TpsfECM(
                i, content, ts, prev_tpsf, text_units, relevance, aggregated_tss
            )
            if tpsf.relevance:
                aggregated_tss.clear()
            else:
                aggregated_tss.append(ts)
            tpsfs.append(tpsf)
            prev_tpsf = tpsf
        return tpsfs


def _determine_tpsf_relevance(
    textunits: tuple[TextUnit, ...], settings: Settings
) -> bool:
    impacted_tus = [tu for tu in textunits if tu.state in ["new", "modified"]]
    for itu in impacted_tus:
        tagged_tokens = (
            []
            if itu.text is None or itu.text == ""
            else settings.nlp_model.tag_words(itu.text)
        )
        if True in [t["is_typo"] for t in tagged_tokens]:
            return False
    return True


def filter_tpsfs(tpsfs: list[TpsfECM]) -> list[TpsfECM]:
    return [tpsf for tpsf in tpsfs if tpsf.relevance is True]


class PCMFactory:
    """
    A class to retrieve text versions in Pause Capturing Mode (PCM).
    """

    @staticmethod
    def run(actions: list[Action], settings: Settings) -> list[TpsfPCM]:
        """
        Generates a list of objects of type Tpsf based on a list of actions.
        Args:
            actions: a list of objects of type Action
        Returns:
            a list of objects of type TpsfPCM
        """
        output: list[str] = []
        revision_id = 0
        tpsfs_pcm = []
        prev_pause: float | None = None
        burst_actions: list[Action] = []
        for act in tqdm(actions, "Extracting tpsfs in PCM"):
            act_type = type(act).__name__
            act_startpos = act.startpos
            if act_type in ["Insertion", "Append", "Pasting"]:
                for char in act.content:
                    output.insert(act_startpos, char)
                    act_startpos += 1
            elif act_type in ["Deletion", "Midletion"]:
                del output[act_startpos : act.endpos + 1]
            elif act_type == "Replacement":
                del output[act_startpos : act.rplcmt_endpos + 1]
                for char in act.content:
                    output.insert(act_startpos, char)
                    act_startpos += 1
            burst_actions.append(act)
            # TODO add actions to Tpsf
            try:
                if (
                    act.pause is not None
                    and act.pause >= settings.config["pause_duration"]
                ):
                    content = "".join(output[:-1])
                    tpsf_pcm = TpsfPCM(revision_id, content, prev_pause)
                    tpsfs_pcm.append(tpsf_pcm)
                    revision_id += 1
                    prev_pause = act.pause
            except AttributeError:
                continue
        return tpsfs_pcm
