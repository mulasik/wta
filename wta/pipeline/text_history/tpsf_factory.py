from tqdm import tqdm

from ...settings import Settings
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
            tpsf = TpsfECM(i, content, ts, prev_tpsf, settings)
            tpsfs.append(tpsf)
            prev_tpsf = tpsf
        return tpsfs


def filter_tpsfs(tpsfs: list[TpsfECM]) -> list[TpsfECM]:
    aggregated_tss = []
    for tpsf in tpsfs:
        if tpsf.relevance is False:
            aggregated_tss.append(tpsf.ts)
        else:
            tpsf.set_irrelevant_tss_aggregated(aggregated_tss)
            aggregated_tss = []
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
                print(f"Collected chars from action {act_type}: {''.join(output)}")
            elif act_type in ["Deletion", "Midletion"]:
                del output[act_startpos : act.endpos + 1]
                print(f"Deleted chars from action {act_type}: {''.join(output)}")
            elif act_type == "Replacement":
                del output[act_startpos : act.rplcmt_endpos + 1]
                for char in act.content:
                    output.insert(act_startpos, char)
                    act_startpos += 1
                print(f"Collected chars from action {act_type}: {''.join(output)}")
            print()
            burst_actions.append(act)
            # TODO add actions to Tpsf
            try:
                if act.pause is not None and act.pause >= settings.config["pause_duration"]:
                    content = "".join(output[:-1])
                    tpsf_pcm = TpsfPCM(revision_id, content, prev_pause)
                    tpsfs_pcm.append(tpsf_pcm)
                    revision_id += 1
                    prev_pause = act.pause
            except AttributeError:
                continue
        return tpsfs_pcm
