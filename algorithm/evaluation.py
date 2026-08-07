import random


def is_flush(hand):
    first_suit = hand[0]["suit"]
    for card in hand:
        if card["suit"] != first_suit:
            return False
    return True


def is_straight(hand):
    rank_list = sorted(card["rank"] for card in hand)
    if rank_list == [2, 3, 4, 5, 14]:
        return True
    for i in range(len(rank_list) - 1):
        if rank_list[i] == rank_list[i + 1]:
            return False
    return rank_list[4] - rank_list[0] == 4


def count_ranks(hand):
    rank_counts = {}
    for card in hand:
        rank = card["rank"]
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    return rank_counts


def get_count_values_sorted(rank_counts):
    counts = list(rank_counts.values())
    counts.sort(reverse=True)
    return counts


def evaluate_hand(hand):
    if len(hand) != 5:
        raise ValueError("evaluate_hand needs exactly 5 cards")

    flush = is_flush(hand)
    straight = is_straight(hand)
    rank_counts = count_ranks(hand)
    counts = get_count_values_sorted(rank_counts)

    if flush and straight:
        rank_list = sorted(card["rank"] for card in hand)
        return 9 if rank_list == [10, 11, 12, 13, 14] else 8
    if counts[0] == 4:
        return 7
    if counts[0] == 3 and counts[1] == 2:
        return 6
    if flush:
        return 5
    if straight:
        return 4
    if counts[0] == 3:
        return 3
    if counts[0] == 2 and counts[1] == 2:
        return 2
    if counts[0] == 2:
        return 1
    return 0


def _partial_hand_strength(known_cards):
    if len(known_cards) >= 5:
        return evaluate_hand(known_cards[:5])

    if not known_cards:
        return 0

    total_rank = sum(c["rank"] for c in known_cards)
    average_rank = total_rank / len(known_cards)

    ranks = [c["rank"] for c in known_cards]
    pair_bonus = 1.5 if len(ranks) == 2 and ranks[0] == ranks[1] else 0

    return (average_rank - 2) / (14 - 2) * 9 + pair_bonus


def pot_odds_score(pot, current_bet):
    if current_bet <= 0:
        return 20.0
    odds = pot / current_bet
    return min(20.0, odds * 4.0)


def position_score(to_move, actions_this_phase):
    if actions_this_phase == 0:
        return 5.0
    return 15.0


def stack_ratio_score(player_chips, pot):
    if pot <= 0:
        return 10.0
    ratio = player_chips / pot
    return min(10.0, ratio * 2.0)


def board_texture_score(community_cards):
    if len(community_cards) < 3:
        return 15.0

    suits = [c["suit"] for c in community_cards]
    suit_counts = {}
    for s in suits:
        suit_counts[s] = suit_counts.get(s, 0) + 1
    max_suit_count = max(suit_counts.values())

    ranks = sorted(set(c["rank"] for c in community_cards))
    max_run = 1
    current_run = 1
    for i in range(1, len(ranks)):
        if ranks[i] - ranks[i - 1] == 1:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1

    danger = 0
    if max_suit_count >= 3:
        danger += 8
    if max_run >= 3:
        danger += 7

    return max(0.0, 15.0 - danger)


def evaluate_situation(state):
    known_cards = state["player_hand"] + state["community_cards"]
    raw_strength = _partial_hand_strength(known_cards)
    hand_strength = min(40.0, (raw_strength / 9.0) * 40.0)

    pot = state.get("pot", 0)
    current_bet = state.get("current_bet", 0)
    odds = pot_odds_score(pot, current_bet)

    position = position_score(
        state.get("to_move", "max"), state.get("actions_this_phase", 0)
    )

    texture = board_texture_score(state["community_cards"])

    chips = state.get("player_chips", pot if pot > 0 else 100)
    stack = stack_ratio_score(chips, pot)

    return hand_strength + odds + position + texture + stack


def should_bluff(hand_strength_0_to_9, pot, bluff_rate=0.15, large_pot_threshold=100, rng=None):
    rng = rng or random
    is_weak = hand_strength_0_to_9 <= 2
    is_large_pot = pot >= large_pot_threshold
    if is_weak and is_large_pot:
        return rng.random() < bluff_rate
    return False
