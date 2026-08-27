import random
import itertools

from algorithm.evaluation import evaluate_hand, _partial_hand_strength


def _simulate_one(state, rng):
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
    rng = rng or random.Random()
    if not state["deck"]:
        known = state["player_hand"] + state["community_cards"]
        return _partial_hand_strength(known)

    total = 0.0
    for _ in range(num_simulations):
        total += _simulate_one(state, rng)
    return total / num_simulations


def monte_carlo_decision(state, num_simulations=200, rng=None):
    avg_strength = monte_carlo_simulate(state, num_simulations=num_simulations, rng=rng)
    current_bet = state.get("current_bet", 0)

    if avg_strength >= 5:
        return "raise"
    if avg_strength >= 2 or current_bet == 0:
        return "call" if current_bet > 0 else "check"
    return "fold"


def _best5(cards):
    if len(cards) < 5:
        return (_partial_hand_strength(cards), [])

    best = None
    for combo in itertools.combinations(cards, 5):
        score = (evaluate_hand(list(combo)), [])
        if best is None or score[0] > best[0]:
            best = score
    return best


def estimate_win_probability(player_hand, community_cards, deck, num_opponents=1,
                              simulations=300, rng=None):
    rng = rng or random.Random()
    if num_opponents <= 0:
        return 1.0
    if not player_hand:
        return 0.0

    wins = 0.0
    for _ in range(simulations):
        pool = list(deck)
        rng.shuffle(pool)

        idx = 0
        opponent_hands = []
        for _ in range(num_opponents):
            opponent_hands.append(pool[idx:idx + 2])
            idx += 2

        community = list(community_cards)
        needed = 5 - len(community)
        if needed > 0:
            community = community + pool[idx:idx + needed]
            idx += needed

        player_best = _best5(player_hand + community)
        opponent_bests = [_best5(oh + community) for oh in opponent_hands]

        best_opponent = max(opponent_bests) if opponent_bests else (-1, [])
        if player_best > best_opponent:
            wins += 1.0
        elif player_best == best_opponent:
            wins += 0.5

    return wins / simulations


def stars_for_probability(win_probability):
    if win_probability >= 0.80:
        return 5
    if win_probability >= 0.60:
        return 4
    if win_probability >= 0.40:
        return 3
    if win_probability >= 0.20:
        return 2
    return 1
