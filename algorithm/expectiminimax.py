import os
import time

from algorithm.game_tree import generate_game_tree, evaluate_state
from algorithm.game_tree import apply_action, is_terminal, get_chance_outcomes
from algorithm.evaluation import should_bluff, _partial_hand_strength

SLOW_DECISION_WARNING_SECONDS = 3.0
DECISION_LOG_PATH = "data/decision_log.txt"


def search_tree(node):
    node_type = node["type"]

    if node_type == "leaf":
        value = evaluate_state(node["state"])
        return None, value

    if node_type == "chance":
        total_value = 0
        for child in node["children"]:
            _, child_value = search_tree(child)
            total_value += child["probability"] * child_value
        return None, total_value

    if node_type == "max":
        best_action, best_value = None, float("-inf")
        for child in node["children"]:
            _, child_value = search_tree(child)
            if child_value > best_value:
                best_value = child_value
                best_action = child["action"]
        return best_action, best_value

    if node_type == "min":
        best_action, best_value = None, float("inf")
        for child in node["children"]:
            _, child_value = search_tree(child)
            if child_value < best_value:
                best_value = child_value
                best_action = child["action"]
        return best_action, best_value

    raise ValueError("Unknown node type: " + str(node_type))


def expectiminimax(state, depth):
    tree = generate_game_tree(state, depth)
    best_action, expected_value = search_tree(tree)

    known_cards = state["player_hand"] + state["community_cards"]
    raw_strength = _partial_hand_strength(known_cards)
    if should_bluff(raw_strength, state.get("pot", 0)):
        actions = [c["action"] for c in generate_game_tree(state, 1)["children"]]
        if "raise" in actions:
            best_action = "raise"

    return best_action, expected_value


def log_decision(hand_number, phase, action, expected_value, time_taken):
    os.makedirs(os.path.dirname(DECISION_LOG_PATH), exist_ok=True)
    log_line = (
        "Hand #" + str(hand_number)
        + " | Phase: " + str(phase)
        + " | Action: " + str(action)
        + " | Expected value: " + str(round(expected_value, 2))
        + " | Time: " + str(round(time_taken, 4)) + "s\n"
    )
    with open(DECISION_LOG_PATH, "a") as log_file:
        log_file.write(log_line)


def make_decision(state, depth, hand_number=1):
    start_time = time.time()
    action, expected_value = expectiminimax(state, depth)
    time_taken = time.time() - start_time

    print("AI decision took", round(time_taken, 4), "seconds")
    if time_taken > SLOW_DECISION_WARNING_SECONDS:
        print("Warning: decision was slow. Consider lowering AI_DEPTH in config.py")

    log_decision(hand_number, state["phase"], action, expected_value, time_taken)
    return action
