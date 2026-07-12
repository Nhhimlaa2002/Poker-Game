"""
actions.py

This file tells us what moves a player is allowed to make, and in
what order the AI should consider them.
"""


def get_possible_actions(state):
    """
    Return the list of legal actions a player can take.

    state: the current game situation (not used yet in this simple
           version, but kept as a parameter so this function can be
           made smarter later)

    returns: a list of action names

    Example:
        get_possible_actions({})  ->  ["fold", "check", "call", "raise"]
    """
    actions = ["fold", "check", "call", "raise"]
    return actions


def order_actions(actions):
    """
    Sort a list of actions so the most promising ones come first.

    actions: a list of action names, e.g. ["fold", "check", "call", "raise"]
    returns: the same actions, sorted using ACTION_PRIORITY

    Example:
        order_actions(["call", "fold", "raise"])  ->  ["raise", "fold", "call"]
    """
    # Go through our preferred order, and for each action, check if
    # it is in the list we were given. If it is, add it to the result.
    # This avoids using sorted()/lambda and keeps things simple.
    preferred_order = ["raise", "fold", "call", "check"]

    ordered_actions = []
    for action_name in preferred_order:
        if action_name in actions:
            ordered_actions.append(action_name)

    return ordered_actions
