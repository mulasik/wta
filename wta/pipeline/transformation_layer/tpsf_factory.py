from tqdm import tqdm

from wta.pipeline.transformation_layer.text_transformation_classifier import TextTransformationClassifier

from ...settings import Settings
from .action import (
    Action,
    Append,
    Deletion,
    Insertion,
    KeyboardAction,
    Midletion,
    Pasting,
    Replacement,
)
from .text_unit import TextUnit
from .text_unit_factory import TextUnitFactory
from .tpsf import TpsfECM, TpsfPCM
from .ts import TransformingSequence


class TPSFFactory:
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
        aggregated_tss: tuple[TransformingSequence, ...] = ()
        tss = [ts for ts in tss if ts.label != "navigation"]
        prev_tpsf = None
        sequence_removed_by_repl = None
        for i, ts in enumerate(tqdm(tss, "Extracting tpsfs")):
            after_end_pos = -1 if ts.endpos is None else ts.endpos + 1
            if ts.label in ["append", "insertion", "pasting"]:
                startpos = ts.startpos
                for char in ts.text:
                    output.insert(startpos, char)
                    startpos += 1
            elif ts.label in ["deletion", "midletion"]:
                text = output[ts.startpos : after_end_pos]
                ts.set_text("".join(text))
                del output[ts.startpos : after_end_pos]
            elif ts.label == "replacement":
                sequence_removed_by_repl = "".join(output[ts.startpos : after_end_pos])
                del output[ts.startpos : after_end_pos]
                startpos = ts.startpos
                for char in ts.text:
                    output.insert(startpos, char)
                    startpos += 1
            tpsf_text = "".join(output)
            tus, deleted_tus, impacted_tus_prev = TextUnitFactory().run(tpsf_text, i, ts, prev_tpsf, sequence_removed_by_repl, settings)
            tpsf_text_prev = "" if not prev_tpsf else prev_tpsf.text
            transformation = TextTransformationClassifier().run(i, tpsf_text, ts, tus, deleted_tus, impacted_tus_prev, sequence_removed_by_repl, tpsf_text_prev)
            relevance = (
                ts.relevance
                if settings.config["enable_spellchecking"] is False
                else _determine_tpsf_relevance(tus, settings)
            )
            tpsf = TpsfECM(
                i, tpsf_text, ts, prev_tpsf, tus, relevance, aggregated_tss, transformation.scope, transformation.sentence_segments
            )
            aggregated_tss = () if tpsf.relevance else (*aggregated_tss, ts)
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
            act_startpos = act.startpos
            if isinstance(act, (Insertion, Append, Pasting)):
                for char in act.content:
                    output.insert(act_startpos, char)
                    act_startpos += 1
            elif isinstance(act, (Deletion, Midletion)):
                after_end_pos = -1 if act.endpos is None else act.endpos + 1
                del output[act_startpos:after_end_pos]
            elif isinstance(act, Replacement):
                del output[act_startpos : act.rplcmt_endpos + 1]
                for char in act.content:
                    output.insert(act_startpos, char)
                    act_startpos += 1
            burst_actions.append(act)
            # TODO add actions to Tpsf
            if (
                isinstance(act, KeyboardAction)
                and act.preceding_pause is not None
                and act.preceding_pause >= settings.config["pause_duration"]
            ):
                content = "".join(output[:-1])
                tpsf_pcm = TpsfPCM(revision_id, content, prev_pause)
                tpsfs_pcm.append(tpsf_pcm)
                revision_id += 1
                prev_pause = act.preceding_pause
        return tpsfs_pcm
