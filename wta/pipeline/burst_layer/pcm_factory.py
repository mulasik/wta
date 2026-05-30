from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tqdm import tqdm  # type: ignore[import-untyped]
else:
    from tqdm import tqdm

from wta.pipeline.transformation_layer.tpsf import TpsfPCM
from wta.settings import Settings

from ..preprocessing.action import (
    Action,
    Append,
    Deletion,
    Insertion,
    KeyboardAction,
    Midletion,
    Pasting,
    Replacement,
)


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
            # print(f"Processing action: {act.content} at pos {act.startpos}")
            act_startpos = act.startpos
            if isinstance(act, (Insertion, Append, Pasting)):
                after_end_pos = -1 if act.endpos is None else act.endpos + 1
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
            if (
                isinstance(act, KeyboardAction)
                and act.preceding_pause is not None
                and act.preceding_pause >= settings.config["pause_duration"]
            ):
                content = "".join(output[:-1])
                tpsf_pcm = TpsfPCM(revision_id, content, prev_pause)
                # print(f"Created TpsfPCM with revision_id {revision_id}, content: |{content}|, preceding_pause: {prev_pause}")
                tpsfs_pcm.append(tpsf_pcm)
                revision_id += 1
                prev_pause = act.preceding_pause
        content = "".join(output[:-1])
        tpsf_pcm = TpsfPCM(revision_id, content, prev_pause)
        tpsfs_pcm.append(tpsf_pcm)
        return tpsfs_pcm
