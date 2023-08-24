import difflib

from tqdm import tqdm

from wta.pipeline.sentence_histories.text_unit import SPSFBuilder

from ...settings import Settings
from .action import Action
from .ts import TransformingSequence


class TsFactory:
    """
    A class for generating objects of type TransformingSequence (TS).
    TSs are generated from action groups.
    Each action group is transformed into a TS.
    """

    @staticmethod
    def run(
        action_groups: dict[str, list[Action]], settings: Settings
    ) -> list[TransformingSequence]:
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
                settings,
            )
            tss.append(ts)
        return tss


def retrieve_sen_ts(
    s1: SPSFBuilder, s2: SPSFBuilder, settings: Settings
) -> TransformingSequence:
    seq_match = difflib.SequenceMatcher(None, s1.text, s2.text)
    prev_cur_comparison_results = seq_match.get_opcodes()
    prev_cur_mismatch = [
        res for res in prev_cur_comparison_results if res[0] != "equal"
    ]
    # there is always one mismatch range, as TPSF capturing happens upon each edit,
    # two separate edits on the same TPSF are not possible
    for m in prev_cur_mismatch:
        if m[0] == "delete":
            startpos = m[1]
            endpos = m[2] + 1
            relevant = s1
            label = "midletion" if endpos < len(relevant.text) else "deletion"
        elif m[0] == "insert":
            startpos = m[3]
            endpos = m[4] + 1
            relevant = s2
            label = "insertion" if endpos < len(relevant.text) else "append"
        elif m[0] == "replace":
            startpos = m[3]
            endpos = m[4] + 1
            relevant = s2
            label = "replacement"
        else:
            print(
                "ATTENTION: Encountered replacement or a different type of transforming operation."
            )
        mismatch_text = relevant.text[startpos:endpos]
        sen_ts = TransformingSequence(
            mismatch_text,
            label,
            startpos,
            endpos,
            None,
            None,
            None,
            None,
            None,
            settings,
        )
    return sen_ts
