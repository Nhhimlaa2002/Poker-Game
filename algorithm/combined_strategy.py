from algorithm.expectiminimax import make_decision as expectiminimax_decision
from algorithm.evaluation import evaluate_situation, should_bluff, _partial_hand_strength
from algorithm.monte_carlo import monte_carlo_decision

EXPENSIVE_PHASES = ("preflop", "flop")
CHEAP_PHASES = ("turn", "river")

DEFAULT_STRATEGY = "combined"


def cheap_heuristic_decision(state, hand_number=1):
    score = evaluate_situation(state)
    current_bet = state.get("current_bet", 0)

    known_cards = state["player_hand"] + state["community_cards"]
    raw_strength = _partial_hand_strength(known_cards)
    if should_bluff(raw_strength, state.get("pot", 0)):
        return "raise"

    if score >= 65:
        return "raise"
    if score >= 30 or current_bet == 0:
        return "call" if current_bet > 0 else "check"
    return "fold"


def decide(state, phase, depth=2, hand_number=1, opponent_aggressiveness=None):
    if opponent_aggressiveness is None:
        opponent_aggressiveness = state.get("opponent_aggressiveness")
    if phase in EXPENSIVE_PHASES:
        return expectiminimax_decision(
            state, depth=depth, hand_number=hand_number,
            opponent_aggressiveness=opponent_aggressiveness,
        )
    return cheap_heuristic_decision(state, hand_number=hand_number)


def decide_with_default(state, phase, depth=2, hand_number=1):
    if DEFAULT_STRATEGY == "expectiminimax":
        return expectiminimax_decision(state, depth=depth, hand_number=hand_number)
    if DEFAULT_STRATEGY == "monte_carlo":
        return monte_carlo_decision(state)
    return decide(state, phase, depth=depth, hand_number=hand_number)


def set_default_strategy(name):
    global DEFAULT_STRATEGY
    if name not in ("expectiminimax", "monte_carlo", "combined"):
        raise ValueError(f"Unknown strategy: {name}")
    DEFAULT_STRATEGY = name