
from tqdm import tqdm

from wta.settings import Settings

from ..preprocessing.action import Action, KeyboardAction, Midletion, Replacement
from .ts import TSBuilder


class TsBuilderFactory:
    """
    A class for generating objects of type TsBuilder (TransformingSequenceBuilder).
    TSs are generated from action groups.
    Each action group is transformed into a TsBuilder.
    """

    @staticmethod
    def run(
        action_groups: dict[str, list[Action]], settings: Settings
    ) -> list[TSBuilder]:
        """
        Generates objects of type TransformingSequence from action groups.
        Args:
            action_groups: dict containing action group names as key and list of actions as value
        Returns:
            a list of objects of type TransformingSequence
        """
        tss = []
        rplcmt_textlen = None
        for acttyp, actgro in tqdm(action_groups.items(), "Extracting transforming sequences"):
            text = "".join([a.content for a in actgro])
            actlbl = acttyp.split("_")[0].lower()
            first_action = actgro[0]
            last_action = actgro[-1]
            startpos = first_action.startpos
            endpos = last_action.endpos

            group_it = iter(action_groups)
            for key in group_it:
                if key == acttyp:
                    break
            try:
                next_key = next(group_it)
                next_action = action_groups[next_key][0]
            except StopIteration:
                next_action = None


            # bursts = []
            # for a in actgro:
            #     if isinstance(a, (Midletion, Replacement)):
            #         print(a.__class__)
            #         print(a.to_dict())
            if (
                isinstance(first_action, KeyboardAction)
                and isinstance(last_action, KeyboardAction)
            ):
                starttime = first_action.starttime
                endtime = last_action.starttime
                pauses: list[float] = [getattr(a, "preceding_pause", 0) for a in actgro]
                seq = ""

                initial_pause = pauses[0]
                if next_action is not None:
                    following_pause = next_action.preceding_pause if isinstance(next_action, (KeyboardAction, Replacement)) else None
                # retrieve the following pause from the following action group

                if actlbl not in ["deletion", "midletion"]:
                    for act in actgro:
                        ap = getattr(act, "preceding_pause", 0)
                        if ap and ap <= 2:
                            seq += act.content
                        elif initial_pause and ap and ap > 2:
                            seq = act.content
                            initial_pause = ap
            else:
                starttime, endtime, pauses, following_pause = None, None, [], None

            if actlbl in ["deletion", "midletion"] and endpos is not None:
                startpos, endpos = endpos, startpos
            elif actlbl == "replacement" and isinstance(last_action, Replacement):

                # print(f"Cur action: {actlbl}, next action {next_action.__class__.__name__}: {None if next_action is None else next_action.to_dict()}")

                if settings.config["ksl_source_format"] == "scriptlog_idfx":
                    rplcmt_textlen = getattr(first_action, "rplcmt_textlen", 0)
                    endpos = None if endpos is None else endpos-1
                if settings.config["ksl_source_format"] == "inputlog_idfx":
                    starttime = getattr(first_action, "starttime", None)
                    endtime = getattr(last_action, "endtime", None)
                    if next_action is not None and isinstance(next_action, KeyboardAction):
                        next_act_preceding_pause = round(next_action.starttime - starttime, 4)
                        next_action.set_preceding_pause(next_act_preceding_pause)
                        following_pause = next_action.preceding_pause if isinstance(next_action, (KeyboardAction, Replacement)) else None
                    pauses = [getattr(a, "preceding_pause", 0) for a in actgro]
                    text = last_action.content
                    startpos = last_action.startpos
                    endpos = last_action.endpos
                    rplcmt_textlen = getattr(first_action, "rplcmt_textlen", 0)
            ts = TSBuilder(
                None,
                text,
                actlbl,
                startpos,
                endpos,
                starttime,
                endtime,
                pauses,
                following_pause,
                rplcmt_textlen,
                actgro
            )
            tss.append(ts)
        return tss

