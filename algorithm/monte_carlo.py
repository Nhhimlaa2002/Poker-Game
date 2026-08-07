"""
monte_carlo.py

Week 4: faster decision-making via random sampling instead of building
the full expectiminimax tree. Repeatedly deals out plausible remaining
community cards / opponent holdings from the state's known deck,
evaluates the resulting hand, and averages the results into a single
win-probability estimate.
"""

import random

from algorithm.evaluation import evaluate_hand, _partial_hand_strength


def _simulate_one(state, rng):
    """
    Run a single random playout: fill out the board with random cards
    from the remaining deck, and score the resulting best-available hand.
    """
    deck = list(state["deck"])
    rng.shuffle(deck)

    community = list(state["community_cards"])
    needed = 5 - len(community)
    if needed > 0:
        community = community + deck[:needed]

    hand = state["player_hand"] + community
    if len(hand) >= 5:
        return evaluate_hand(hand[:5])
    return _partial_hand_strength(hand)


def monte_carlo_simulate(state, num_simulations=200, rng=None):
    """
    Sample unknown cards `num_simulations` times, evaluate the resulting
    hand each time, and return the average strength (0-9 scale).

    state: dict with player_hand, community_cards, deck
    num_simulations: how many random playouts to average over
    returns: float, average hand strength across all simulations
    """
    rng = rng or random.Random()
    if not state["deck"]:
        # No cards left to sample - just score what we have.
        known = state["player_hand"] + state["community_cards"]
        return _partial_hand_strength(known)

    total = 0.0
    for _ in range(num_simulations):
        total += _simulate_one(state, rng)
    return total / num_simulations


def monte_carlo_decision(state, num_simulations=200, rng=None):
    """
    Turn a Monte Carlo strength estimate into an action, using simple
    thresholds on the averaged 0-9 hand-strength score.
    """
    avg_strength = monte_carlo_simulate(state, num_simulations=num_simulations, rng=rng)
    current_bet = state.get("current_bet", 0)

    if avg_strength >= 5:
        return "raise"
    if avg_strength >= 2 or current_bet == 0:
        return "call" if current_bet > 0 else "check"
    return "fold"