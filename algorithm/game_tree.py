import random
from algorithm.evaluation import evaluate_situation
from algorithm.actions import get_possible_actions, order_actions
SAMPLE_SIZE = 10
RAISE_AMOUNT = 20


def evaluate_state(state):
    return evaluate_situation(state)


def is_terminal(state):
    if state["phase"] == "folded":
        return True
    if state["phase"] == "showdown":
        return True
    return False


def apply_action(state, action):
    new_state = dict(state)

    if action == "fold":
        new_state["phase"] = "folded"
        return new_state

    if action == "raise":
        new_state["pot"] = state["pot"] + RAISE_AMOUNT
        new_state["current_bet"] = 0

    if action == "call":
        new_state["pot"] = state["pot"] + state["current_bet"]
        new_state["current_bet"] = 0

    actions_so_far = state.get("actions_this_phase", 0) + 1
    new_state["actions_this_phase"] = actions_so_far

    if actions_so_far >= 2:
        if state["phase"] == "river":
            new_state["phase"] = "showdown"
            new_state["to_move"] = "max"
        else:
            new_state["to_move"] = "chance"
    else:
        new_state["to_move"] = "min" if state["to_move"] == "max" else "max"

    return new_state

def get_chance_outcomes(state):
    deck = state["deck"]

    if len(deck) == 0:
        return [(1.0, dict(state))]

    n = min(SAMPLE_SIZE, len(deck))
    sampled = random.sample(deck, n)
    probability_each = 1.0 / n

    outcomes = []
    for card in sampled:
        new_state = dict(state)
        new_state["community_cards"] = state["community_cards"] + [card]
        new_state["deck"] = [c for c in deck if c is not card]

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

    actions = get_possible_actions(state)
    ordered_actions = order_actions(actions)

    children = []
    for action in ordered_actions:
        next_state = apply_action(state, action)
        child_node = generate_game_tree(next_state, depth - 1)
        child_node["action"] = action
        children.append(child_node)

    return {"type": turn_type, "state": state, "children": children}
