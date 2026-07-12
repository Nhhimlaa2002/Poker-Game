"""
game_tree.py

This file is new this week. It does two important jobs:

1. Figures out what happens to the game state after a move
   (apply_action), and when the game is over (is_terminal).

2. Builds a "game tree" - a structure that maps out every possible
   future the AI is considering, several moves ahead. Instead of
   deciding moves one at a time while searching (like last week),
   we now build the whole tree FIRST, then search through it.

Hidden information (the opponent's cards, and future community
cards) is handled inside get_chance_outcomes(): since we cannot
know which card will appear next, we consider EVERY card still
left in the deck, each with an equal chance of appearing.

This file connects to:
    - evaluation.py   (used to score how strong a hand is)
    - actions.py      (used to get and order the legal moves)
    - expectiminimax.py (searches the tree this file builds)
"""

from algorithm.evaluation import evaluate_hand
from algorithm.actions import get_possible_actions, order_actions

# How much the pot grows when a player raises.
RAISE_AMOUNT = 20


def evaluate_state(state):
    """
    Estimate how good the current situation looks for the AI.
    Used when we stop searching further ahead (a "leaf" of the tree).

    state: a dictionary describing the game right now
    returns: a number - higher means better for the AI
    """
    known_cards = state["player_hand"] + state["community_cards"]

    if len(known_cards) >= 5:
        five_cards = known_cards[0:5]
        hand_score = evaluate_hand(five_cards)
    else:
        # Not enough cards yet (for example, before the flop).
        total_rank = 0
        for card in known_cards:
            total_rank = total_rank + card["rank"]

        if len(known_cards) > 0:
            average_rank = total_rank / len(known_cards)
        else:
            average_rank = 0

        hand_score = (average_rank - 2) / (14 - 2) * 9

    pot = state["pot"]
    final_score = hand_score * 10 + pot * 0.1
    return final_score


def is_terminal(state):
    """
    Check if the game is over and we should stop searching further.

    state: the current game situation
    returns: True if the hand is finished, False otherwise
    """
    if state["phase"] == "folded":
        return True
    if state["phase"] == "showdown":
        return True
    return False


def apply_action(state, action):
    """
    Figure out what the game looks like after a player takes an
    action. Builds and returns a NEW state - does not change the
    original one.

    Once both the AI and the opponent have acted in the current
    phase (2 actions), betting for this phase is done, and it
    becomes a "chance" turn - a new community card is about to be
    revealed, and we do not know which one in advance.

    state: the current game situation
    action: one of "fold", "check", "call", "raise"
    returns: a new state dictionary showing the result
    """
    new_state = dict(state)

    if action == "fold":
        new_state["phase"] = "folded"
        return new_state

    if action == "raise":
        new_state["pot"] = state["pot"] + RAISE_AMOUNT

    if action == "call":
        new_state["pot"] = state["pot"] + state["current_bet"]
        new_state["current_bet"] = 0

    # "check" does not change the pot at all.

    actions_so_far = state.get("actions_this_phase", 0) + 1
    new_state["actions_this_phase"] = actions_so_far

    if actions_so_far >= 2:
        # Both players have acted this phase.
        if state["phase"] == "river":
            # No more cards left to reveal - go straight to showdown.
            new_state["phase"] = "showdown"
            new_state["to_move"] = "max"
        else:
            # Time to reveal a new card - we don't know which one,
            # so this becomes a chance turn.
            new_state["to_move"] = "chance"
    else:
        # Only one player has acted so far - switch turns as normal.
        if state["to_move"] == "max":
            new_state["to_move"] = "min"
        else:
            new_state["to_move"] = "max"

    return new_state


def get_chance_outcomes(state):
    """
    Handle hidden information: we do not know which community card
    will be revealed next, so we look at EVERY card still left in
    the deck, and give each one an equal probability of appearing.

    state: the current game situation, including the remaining
           "deck" (list of cards not yet seen)
    returns: a list of (probability, new_state) pairs. The
             probabilities always add up to 1.0.
    """
    deck = state["deck"]

    if len(deck) == 0:
        # No cards left to reveal - nothing changes.
        return [(1.0, dict(state))]

    probability_each = 1.0 / len(deck)

    outcomes = []
    for card in deck:
        new_state = dict(state)
        new_state["community_cards"] = state["community_cards"] + [card]

        # Build a new deck with this card removed.
        new_deck = []
        for deck_card in deck:
            if deck_card is not card:
                new_deck.append(deck_card)
        new_state["deck"] = new_deck

        if state["phase"] == "preflop":
            new_state["phase"] = "flop"
        elif state["phase"] == "flop":
            new_state["phase"] = "turn"
        elif state["phase"] == "turn":
            new_state["phase"] = "river"
        else:
            new_state["phase"] = "showdown"

        new_state["to_move"] = "max"
        new_state["actions_this_phase"] = 0
        outcomes.append((probability_each, new_state))

    return outcomes


def generate_game_tree(state, depth):
    """
    Build the full tree of future possibilities, starting from the
    current state, looking "depth" moves ahead.

    Each node in the tree is a dictionary with:
        "type"     - "max", "min", "chance", or "leaf"
        "state"    - the game situation at this node
        "children" - a list of child nodes (empty for a leaf)

    Each child of a max/min node also has an "action" key (the move
    that leads to it). Each child of a chance node also has a
    "probability" key.

    state: the current game situation
    depth: how many moves ahead to build
    returns: the root node of the tree (a dictionary)
    """
    if depth <= 0 or is_terminal(state):
        return {"type": "leaf", "state": state, "children": []}

    turn_type = state["to_move"]

    if turn_type == "chance":
        outcomes = get_chance_outcomes(state)
        children = []
        for probability, next_state in outcomes:
            child_node = generate_game_tree(next_state, depth - 1)
            child_node["probability"] = probability
            children.append(child_node)
        return {"type": "chance", "state": state, "children": children}

    # turn_type is "max" or "min"
    actions = get_possible_actions(state)
    ordered_actions = order_actions(actions)

    children = []
    for action in ordered_actions:
        next_state = apply_action(state, action)
        child_node = generate_game_tree(next_state, depth - 1)
        child_node["action"] = action
        children.append(child_node)

    return {"type": turn_type, "state": state, "children": children}
