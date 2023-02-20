from tqdm import tqdm


class ActionFactory:
    """
    A class for generating Action objects and storing them in a list.
    Action corresponds to event. There are as many actions as events.
    """

    @staticmethod
    def run(evnts) -> list:
        """
        Generates a list of Action objects for all events.
        Args:
            evnts: a list of Event objects
        Returns:
            a list of Action objects
        """
        # print('EVENTS')
        # for e in evnts:
        #     print(type(e).__name__, e.__dict__['content'], e.__dict__['startpos'], e.__dict__['endpos'])
        # print()
        actions = []
        evnts = tqdm(evnts, 'Generating actions')
        for evnt in evnts:
            if evnt.to_action() is not None:
                a = evnt.to_action()
                actions.append(a)
            else:
                print(f'INFO: No action found for event {type(evnt).__name__} *{evnt.content}* at pos {evnt.startpos}-{evnt.endpos}')
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
    def run(acts) -> dict:
        """
        Aggregates Action objects based on specific criteria.
        Args:
            acts: a list of Action objects
        Returns:
            A dict containing action group identifiers as keys and lists of Action objects as values.
        """
        # print('ACTIONS')
        # for a in actions:
        #     if a:
        #         print(type(a).__name__, a.__dict__)
        # print()
        act_groups = {}
        counter = 0
        prev_act_type = None
        for i, act in enumerate(acts):
            act_type = type(act).__name__
            non_consecutive_act = abs(act.startpos - acts[i-1].startpos) > 1
            consecutive_del = abs(act.startpos - acts[i-1].startpos) == 0 and act.textlen < acts[i-1].textlen
            # if the action type has just changed
            # or this is an action of type 'Replacement', 'Pasting' or 'Navigation'
            # or it is not a consecutive action
            # (absolute diff between startpos of the currect action and startpos of the prev action is more than 1)
            # neither is a consecutive deletion with delete
            if act_type != prev_act_type or act_type in ['Replacement', 'Pasting', 'Navigation'] or (non_consecutive_act and not consecutive_del):
                act_groups[f'{act_type}_{counter}'] = [act]
                current_act_type = f'{act_type}_{counter}'
                counter += 1
            elif act_type == prev_act_type and abs(act.startpos - acts[i - 1].startpos) == 1:
                act_groups[current_act_type].append(act)
            else:
                print(f'INFO: The action of type {act_type} does not meet pre-defined criteria for aggregation. '
                      f'It will be added to the action groups as a separate single-item group.')
                act_groups[current_act_type] = [act]
            prev_act_type = act_type
        return act_groups

