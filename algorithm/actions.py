"""
actions.py

This file just tells us what moves a player is allowed to make.
Kept in its own file so it is easy to change later
(for example, if raise amounts become more complex).
"""


def get_possible_actions(state):
    """
    Return the list of legal actions a player can take.

    state: the current game situation (not used yet in this simple
           version, but kept as a parameter so this function can be
           made smarter later, for example removing "check" if
           there is already a bet on the table)

    returns: a list of action names

    Example:
        get_possible_actions({})  ->  ["fold", "check", "call", "raise"]
    """
    actions = ["fold", "check", "call", "raise"]
    return actions
