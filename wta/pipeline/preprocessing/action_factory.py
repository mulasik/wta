from collections.abc import Collection

from tqdm import tqdm

from wta.pipeline.names import ActionTypes
from wta.settings import Settings

from .action import Action, KeyboardAction, Replacement
from .events.base import BaseEvent


class ActionFactory:
    """
    A class for generating Action objects and storing them in a list.
    Action corresponds to event. There are as many actions as events.
    """

    @staticmethod
    def run(evnts: Collection[BaseEvent]) -> list[Action]:
        """
        Generates a list of Action objects for all events.
        Args:
            evnts: a list of Event objects
        Returns:
            a list of Action objects
        """

        actions = []
        evnts = tqdm(evnts, "Generating actions")
        for evnt in evnts:
            # print()
            # print(f"Processing event {evnt.__class__.__name__}: {evnt.__dict__}")
            action = evnt.to_action()
            # print(f"Generated action: {action.__dict__}"  if action is not None else "No action generated.")
            if action is not None:
                actions.append(action)
        return actions


class ActionAggregator:
    """
    A class for aggregating Action objects.
    Aggregating actions enables identification of transforming sequences in the next pipeline step.
    Aggregation is triggered if the actions are of the same type
    and the actions are executed at consecutive positions,
    and they are of one of the following types:
    - append (consecutive means startpos, startpos+1, startpos+2, ...)
    - insertion (consecutive means startpos, startpos+1, startpos+2, ...)
    - deletion with backspace (consecutive means startpos, startpos-1, startpos-2, ...)
    - midletion (consecutive means startpos, startpos-1, startpos-2, ...)
    - deletion with del (consecutive means the position does not change and the text len gets shorter)
    Aggregation is not performed for the following action types:
    - replacement
    - pasting
    - navigation
    """

    @staticmethod
    def run(acts: list[Action], settings: Settings) -> dict[str, list[Action]]:
        """
        Aggregate Action objects into groups based on action type, position,
        and other predefined rules.

        Args:
            acts: List of Action objects.

        Returns:
            A dictionary mapping group identifiers to lists of Action objects.
        """
        act_groups: dict[str, list[Action]] = {}
        counter = 0
        prev_act_type = None
        current_group = None
        current_replacement_group: list[Action] = []

        for i, act in enumerate(acts):
            # print(f"* Act to be processed: {act.__dict__}")
            act_type = type(act).__name__
            prev_prev_act = acts[i - 2] if i > 1 else None
            prev_act = acts[i - 1] if i > 0 else None
            next_act = acts[i + 1] if i < len(acts) - 1 else None
            next_next_act = acts[i + 2] if i < len(acts) - 2 else None

            # print(f"\nProcessing {i}: {act_type} {act.__dict__}")
            # print("Prev type:", prev_act_type)
            # print(f"Current replacement group: {current_replacement_group}")
            # print(f"Act in current replacement group: {act in current_replacement_group}")
            # print("====")

            # --- Helper booleans ---
            non_linear = (
                prev_act is not None
                and abs(act.startpos - prev_act.startpos) > 1
            )

            consecutive_deletion = (
                isinstance(act, KeyboardAction)
                and prev_act is not None
                and act.startpos - prev_act.startpos == 0
                and isinstance(prev_act, KeyboardAction)
            )

            # --- Consecutive group starts ---
            starts_consecutive_deletion_group = (
                act_type in [ActionTypes.MID, ActionTypes.DEL]
                and next_act is not None
                and type(next_act).__name__ in [ActionTypes.MID, ActionTypes.DEL]
                and (prev_act is None or type(prev_act).__name__ not in [ActionTypes.MID, ActionTypes.DEL])
                and act.startpos - next_act.startpos == 1
            )

            starts_consecutive_insertion_group = (
                act_type in [ActionTypes.APP, ActionTypes.INS]
                and next_act is not None
                and type(next_act).__name__ in [ActionTypes.APP, ActionTypes.INS]
                and (prev_act is None or type(prev_act).__name__ not in [ActionTypes.APP, ActionTypes.INS])
                and act.startpos - next_act.startpos == -1
            )

            starts_replacement_group = (
                act_type == ActionTypes.REPL
                and next_act is not None
                and type(next_act).__name__ in [ActionTypes.APP, ActionTypes.INS, ActionTypes.DEL, ActionTypes.MID]
                and next_next_act is not None
                and type(next_next_act).__name__ == ActionTypes.REPL
            )

            if act in current_replacement_group:
                continue

            if act not in current_replacement_group and prev_act is not None and prev_act in current_replacement_group:
                current_replacement_group = []

            # ===========================
            #   DECIDE HOW TO PLACE ACT
            # ===========================

            if starts_consecutive_deletion_group or starts_consecutive_insertion_group:
                # print("Starting new consecutive deletion or insertion group")
                counter += 1
                current_group = f"{act_type}_{counter}"
                act_groups[current_group] = [act]

            elif settings.config["ksl_source_format"] == "inputlog_idfx" and starts_replacement_group:
                # print("Starting new inputlog replacement group")
                counter += 1
                current_group = f"{act_type}_{counter}"
                current_replacement_group = [act, next_act, next_next_act] if next_next_act is not None and next_act is not None else [act]
                # action which preceds the replacement group
                act_preceding_repl_group = acts[i - 1] if i > 2 else None
                act_groups[current_group] = handle_inputlog_replacement_group(
                    current_replacement_group, act_preceding_repl_group
                    )
                # print(f"Current temp replacement group actions: {[a.__dict__ for a in current_replacement_group]}")
                # print(f"Current group: {current_group}, size: {len(act_groups[current_group])}")

            elif (
                settings.config["ksl_source_format"] == "scriptlog_idfx"
                and
                (act_type != prev_act_type
                or act_type in [ActionTypes.REPL, ActionTypes.PAST, ActionTypes.NAV]
                or (non_linear and not consecutive_deletion))
            ) or (
                settings.config["ksl_source_format"] == "inputlog_idfx"
                and ((act_type != prev_act_type and act not in current_replacement_group)
                or act_type in [ActionTypes.PAST, ActionTypes.NAV]
                or (non_linear and not consecutive_deletion))
            ):
                # print("Creating new single-item action group")
                # print(f"Act: {act.__dict__}")
                counter += 1
                current_group = f"{act_type}_{counter}"
                act_groups[current_group] = [act]

            # --- Append to existing group ---
            elif (
                act_type == prev_act_type
                and act_type in [ActionTypes.MID, ActionTypes.DEL]
                and prev_act is not None
                and act.startpos - prev_act.startpos == -1
            ) or (
                act_type == prev_act_type
                and act_type in [ActionTypes.APP, ActionTypes.INS]
                and prev_act is not None
                and act.startpos - prev_act.startpos == 1
            ) or (
                settings.config["ksl_source_format"] == "inputlog_idfx"
                and act_type in [ActionTypes.APP, ActionTypes.INS]
                and prev_act is not None
                and type(prev_act).__name__ == ActionTypes.REPL
                and next_act is not None
                and type(next_act).__name__ == ActionTypes.REPL
            ) or (
                settings.config["ksl_source_format"] == "inputlog_idfx"
                and act_type == ActionTypes.REPL
                and prev_act is not None
                and type(prev_act).__name__ in [ActionTypes.APP, ActionTypes.INS]
                and prev_prev_act is not None
                and type(prev_prev_act).__name__ == ActionTypes.REPL
            ):
                # print(f"Appending to existing group {current_group}")
                # print(f"Act: {act.__dict__}")
                current_group = f"{act_type}_{counter}"
                act_groups[current_group].append(act)
                # print(f"Current group {current_group}: {len(act_groups[current_group])}")

            else:
                # Fallback: create single-item group
                print(
                    f"INFO: Action {act_type} did not match any rule. "
                    f"Action: {act.__dict__}. "
                    "Creating fallback single-item group. "
                    f"Next: {type(next_act).__name__}, next next: {type(next_next_act).__name__}"
                )
                counter += 1
                current_group = f"{act_type}_{counter}"
                act_groups[current_group] = [act]

            # print(f"Current group: {current_group}, size: {len(act_groups[current_group])}")
            prev_act_type = act_type

        return act_groups


def handle_inputlog_replacement_group(
        replacement_group: list[Action],
        act_preceding_repl_group: Action | None,
        ) -> list[Action]:
    """
    Handles a replacement group in inputlog format by splitting it into individual actions.

    Args:
        replacement_group: List of Action objects representing a replacement group.
    Returns:
        An Action object representing the replacement.
    """
    # for a in replacement_group:
    #     print(a.to_dict())
    # print("===")
    # print(f"act_preceding_repl_group: {act_preceding_repl_group.to_dict()}")
    # print("======")
    first_rplcmt_action = replacement_group[0]
    middle_action = replacement_group[1]
    second_rplcmt_action = replacement_group[-1]
    rplcmt_textlen = first_rplcmt_action.endpos - first_rplcmt_action.startpos if first_rplcmt_action.endpos is not None else None
    content = second_rplcmt_action.content
    startpos = second_rplcmt_action.startpos
    endpos = second_rplcmt_action.endpos
    starttime = getattr(middle_action, "starttime", None)
    endtime = getattr(middle_action, "endtime", None)
    act_preceding_endtime = getattr(act_preceding_repl_group, "endtime", None)
    preceding_pause =  None if starttime is None or act_preceding_endtime is None else round(starttime - act_preceding_endtime, 4)
    rplcmt_endpos = first_rplcmt_action.endpos - 1 if first_rplcmt_action.endpos is not None else None
    return [Replacement(
            content,
            startpos,
            endpos,
            starttime,
            endtime,
            preceding_pause,
            rplcmt_endpos,
            rplcmt_textlen,
        )]
