from tqdm import tqdm

from .action import Action
from .ts import TransformingSequence


class TsFactory:
    """
    A class for generating objects of type TransformingSequence (TS).
    TSs are generated from action groups.
    Each action group is transformed into a TS.
    """

    @staticmethod
    def run(action_groups: dict[str, list[Action]]) -> list[TransformingSequence]:
        """
        Generates objects of type TransformingSequence from action groups.
        Args:
            action_groups: dict containing action group names as key and list of actions as value
        Returns:
            a list of objects of type TransformingSequence
        """
        tss = []
        prev_endtime = None
        rplcmt_textlen = None
        for acttyp, actgro in tqdm(
            action_groups.items(), "Extracting transforming sequences"
        ):
            text = "".join([a.content for a in actgro])
            actlbl = acttyp.split("_")[0].lower()
            startpos = actgro[0].startpos
            endpos = actgro[-1].endpos
            try:
                starttime = actgro[0].starttime
                endtime = actgro[-1].endtime
                duration = endtime - starttime
                preceding_pause = None if not prev_endtime else starttime - prev_endtime
            except AttributeError:
                starttime, endtime, duration, preceding_pause = None, None, None, None
            if actlbl in ["deletion", "midletion"]:
                startpos, endpos = endpos, startpos
            elif actlbl == "replacement":
                endpos = actgro[-1].rplcmt_endpos
                rplcmt_textlen = actgro[0].textlen
            prev_endtime = endtime
            ts = TransformingSequence(
                text,
                actlbl,
                startpos,
                endpos,
                starttime,
                endtime,
                duration,
                preceding_pause,
                rplcmt_textlen,
            )
            tss.append(ts)
        return tss
