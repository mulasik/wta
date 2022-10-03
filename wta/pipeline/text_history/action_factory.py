from tqdm import tqdm


class ActionFactory:
    """
    A class for generating Action objects and storing them in a list.
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
        return actions


class ActionAggregator:
    """
    A class for aggregating Action objects.
    Aggregating actions enables identification of transforming sequences in the next pipeline step.
    Aggregation is triggered if the actions are of the same type
    and the actions are executed at consecutive positions
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
    def run(actions) -> dict:
        """
        Aggregates Action objects based on specific criteria.
        Args:
            actions: a list of Action objects
        Returns:
            A dict containing action group identifiers as keys and lists of Action objects as values.
        """
        # print('ACTIONS')
        # for a in actions:
        #     if a:
        #         print(type(a).__name__, a.__dict__)
        # print()
        action_groups = {}
        counter = 0
        prev_act_type = None
        for i, act in enumerate(actions):
            # print(f'{type(act).__name__}\n{act.__dict__}')
            act_type = type(act).__name__
            if act_type != prev_act_type or act_type in ['Replacement', 'Pasting', 'Navigation'] or abs(act.startpos - actions[i-1].startpos) != 1:
                action_groups[f'{act_type}_{counter}'] = [act]
                current_act_type = f'{act_type}_{counter}'
                counter += 1
            elif act_type == prev_act_type and abs(act.startpos - actions[i-1].startpos) == 1:
                action_groups[current_act_type].append(act)
            prev_act_type = act_type
        # print('ACTION GROUPS')
        # for at, aa in action_groups.items():
        #     print(at, len(aa), aa[0].startpos, aa[-1].endpos)
        #     print([a.__dict__['content'] for a in aa])
        # print()
        return action_groups

