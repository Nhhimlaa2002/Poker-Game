"""
combined_strategy.py

Week 3: uses full expectiminimax search on preflop/flop (when there's
plenty of time and the decision matters most), and a cheaper heuristic
on turn/river (when the tree would be large and speed matters more).

Week 4: also exposes DEFAULT_STRATEGY, which strategy_comparison.py can
update to point at whichever of the three strategies wins most often.
"""

from algorithm.expectiminimax import make_decision as expectiminimax_decision
from algorithm.evaluation import evaluate_situation, should_bluff, _partial_hand_strength
from algorithm.monte_carlo import monte_carlo_decision

EXPENSIVE_PHASES = ("preflop", "flop")
CHEAP_PHASES = ("turn", "river")

# Updated by strategy_comparison.py after running the Week 4 comparison.
DEFAULT_STRATEGY = "combined"


def cheap_heuristic_decision(state, hand_number=1):
    """
    A fast, non-search-based decision for turn/river: score the current
    situation directly and pick an action from that score, with the
    Week 3 bluff heuristic layered on top.
    """
    score = evaluate_situation(state)   # 0-100
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


def decide(state, phase, depth=2, hand_number=1):
    """
    Main entry point: routes to expectiminimax (preflop/flop) or the
    cheap heuristic (turn/river) based on the current phase.
    """
    if phase in EXPENSIVE_PHASES:
        return expectiminimax_decision(state, depth=depth, hand_number=hand_number)
    return cheap_heuristic_decision(state, hand_number=hand_number)


def decide_with_default(state, phase, depth=2, hand_number=1):
    """
    Routes to whichever strategy is currently DEFAULT_STRATEGY
    ("expectiminimax", "monte_carlo", or "combined"). Used once
    strategy_comparison.py has picked a winner (Week 4 item 2).
    """
    if DEFAULT_STRATEGY == "expectiminimax":
        return expectiminimax_decision(state, depth=depth, hand_number=hand_number)
    if DEFAULT_STRATEGY == "monte_carlo":
        return monte_carlo_decision(state)
    return decide(state, phase, depth=depth, hand_number=hand_number)


def set_default_strategy(name):
    """Called by strategy_comparison.py to update the winning strategy."""
    global DEFAULT_STRATEGY
    if name not in ("expectiminimax", "monte_carlo", "combined"):
        raise ValueError(f"Unknown strategy: {name}")
    DEFAULT_STRATEGY = name