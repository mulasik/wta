import difflib

from tqdm import tqdm

from wta.pipeline.transformation_layer.text_unit import SPSFBuilder
from wta.pipeline.transformation_layer.ts_burst import TSBurst

from ...settings import Settings
from .action import Action, KeyboardAction, Replacement
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
        prev_endtime: int | None = None
        rplcmt_textlen = None
        for acttyp, actgro in tqdm(
            action_groups.items(), "Extracting transforming sequences"
        ):
            text = "".join([a.content for a in actgro])
            actlbl = acttyp.split("_")[0].lower()
            first_action = actgro[0]
            last_action = actgro[-1]
            startpos = first_action.startpos
            endpos = last_action.endpos
            bursts = []
            if isinstance(first_action, KeyboardAction) and isinstance(
                last_action, KeyboardAction
            ):
                starttime = first_action.starttime
                endtime = last_action.starttime
                duration = round(endtime - starttime, 4)
                preceding_pause = None if not prev_endtime else round(starttime - prev_endtime, 4)
                writing_speed_per_min = None if duration == 0 else round((len(text) * 60 / duration), 2)
                avg_pause_duration = round(sum([a.preceding_pause for a in actgro[1:]])/len(actgro), 4)
                seq = ""
                initial_pause = preceding_pause
                initial = True
                if actlbl not in ["deletion", "midletion"]:
                    for act in actgro:
                        if act.preceding_pause and act.preceding_pause <= 2:
                            seq += act.content
                        elif initial_pause and act.preceding_pause and act.preceding_pause > 2:
                            if (initial and initial_pause <= 2) or not initial:
                                bursts.append(TSBurst(initial_pause, seq))
                            seq = act.content
                            initial_pause = act.preceding_pause
                            initial = False
                    if initial_pause:
                        bursts.append(TSBurst(initial_pause, seq))
            else:
                starttime, endtime, duration, preceding_pause, writing_speed_per_min, avg_pause_duration = None, None, None, None, None, None
            if actlbl in ["deletion", "midletion"] and endpos is not None:
                startpos, endpos = endpos, startpos
            elif actlbl == "replacement" and isinstance(last_action, Replacement):
                endpos = last_action.rplcmt_endpos
                rplcmt_textlen = first_action.rplcmt_textlen
            prev_endtime = endtime
            ts = TransformingSequence(
                text,
                actlbl,
                startpos,
                endpos,
                starttime,
                endtime,
                duration,
                writing_speed_per_min,
                avg_pause_duration,
                preceding_pause,
                rplcmt_textlen,
                bursts,
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
            None,
            None,
            None,
            settings,
        )
    return sen_ts
