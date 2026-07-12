"""
expectiminimax.py

This file contains the AI's decision-making logic.

Last week, this file built moves "on the fly" while searching.
This week, it works in two clear steps instead:

    1. Build the whole game tree first (using game_tree.py).
    2. Search through that already-built tree to find the best move.

Splitting it into two steps makes it easier to see and explain what
the AI is "thinking about" - the tree itself represents every future
the AI is imagining, several moves ahead.

This file connects to:
    - game_tree.py   (builds the tree and knows the game rules)
    - evaluation.py  (indirectly, through game_tree.py)
    - actions.py     (indirectly, through game_tree.py)
"""

import time

from algorithm.game_tree import generate_game_tree, evaluate_state

# Re-exported here so other files/tests can still do
# "from algorithm.expectiminimax import apply_action" if needed.
from algorithm.game_tree import apply_action, is_terminal, get_chance_outcomes

# If a decision takes longer than this many seconds, we print a
# warning suggesting the search depth be reduced.
SLOW_DECISION_WARNING_SECONDS = 3.0

# Where decisions get logged, so we have proof the AI is "thinking".
DECISION_LOG_PATH = "data/decision_log.txt"


def search_tree(node):
    """
    Walk through an already-built game tree and find the best
    action and its expected value.

    node: a tree node, as built by game_tree.generate_game_tree()
    returns: (best_action, expected_value)
             best_action is None at leaf nodes and chance nodes,
             since no single action applies there.
    """
    node_type = node["type"]

    if node_type == "leaf":
        value = evaluate_state(node["state"])
        return None, value

    if node_type == "chance":
        total_value = 0
        for child in node["children"]:
            _, child_value = search_tree(child)
            total_value = total_value + child["probability"] * child_value
        return None, total_value

    if node_type == "max":
        best_action = None
        best_value = float("-inf")
        for child in node["children"]:
            _, child_value = search_tree(child)
            if child_value > best_value:
                best_value = child_value
                best_action = child["action"]
        return best_action, best_value

    if node_type == "min":
        best_action = None
        best_value = float("inf")
        for child in node["children"]:
            _, child_value = search_tree(child)
            if child_value < best_value:
                best_value = child_value
                best_action = child["action"]
        return best_action, best_value

    raise ValueError("Unknown node type: " + str(node_type))


def expectiminimax(state, depth):
    """
    Decide the best action for the current state by building the
    game tree and searching it.

    state: the current game situation
    depth: how many moves ahead to think
    returns: (best_action, expected_value)

    Example:
        action, value = expectiminimax(my_state, depth=2)
    """
    tree = generate_game_tree(state, depth)
    best_action, expected_value = search_tree(tree)
    return best_action, expected_value


def log_decision(hand_number, phase, action, expected_value, time_taken):
    """
    Write one line to the decision log file, recording what the AI
    decided and how long it took. Useful for showing proof of work
    and for spotting slow decisions later.

    hand_number: which hand of poker this is (1, 2, 3, ...)
    phase: the game phase, e.g. "preflop"
    action: the action the AI chose
    expected_value: the expected value the AI calculated
    time_taken: how many seconds the decision took
    """
    log_line = (
        "Hand #" + str(hand_number)
        + " | Phase: " + str(phase)
        + " | Action: " + str(action)
        + " | Expected value: " + str(round(expected_value, 2))
        + " | Time: " + str(round(time_taken, 4)) + "s\n"
    )

    log_file = open(DECISION_LOG_PATH, "a")
    log_file.write(log_line)
    log_file.close()


def make_decision(state, depth, hand_number=1):
    """
    The main function other files should call to get the AI's move.
    Times the decision, logs it, and warns if it was slow.

    state: the current game situation
    depth: how many moves ahead to think
    hand_number: which hand of poker this is, used for the log

    returns: the chosen action (a string)

    Example:
        action = make_decision(my_state, depth=2, hand_number=1)
    """
    start_time = time.time()
    action, expected_value = expectiminimax(state, depth)
    end_time = time.time()

    time_taken = end_time - start_time
    print("AI decision took", round(time_taken, 4), "seconds")

    if time_taken > SLOW_DECISION_WARNING_SECONDS:
        print("Warning: decision was slow. Consider lowering AI_DEPTH in config.py")

    log_decision(hand_number, state["phase"], action, expected_value, time_taken)

    return action


# --- Example usage ---
if __name__ == "__main__":
    example_deck = []
    for rank in range(2, 15):
        example_deck.append({"rank": rank, "suit": "clubs"})
        example_deck.append({"rank": rank, "suit": "diamonds"})

    example_state = {
        "player_hand": [
            {"rank": 14, "suit": "hearts"},
            {"rank": 13, "suit": "hearts"},
        ],
        "community_cards": [],
        "deck": example_deck,
        "pot": 30,
        "current_bet": 20,
        "phase": "preflop",
        "to_move": "max",
        "actions_this_phase": 0,
    }

    chosen_action = make_decision(example_state, depth=2, hand_number=1)
    print("Chosen action:", chosen_action)
