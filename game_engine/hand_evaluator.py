from collections import Counter
from itertools import combinations

HIGH_CARD = 0
PAIR = 1
TWO_PAIR = 2
THREE_OF_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6
FOUR_OF_KIND = 7
STRAIGHT_FLUSH = 8
ROYAL_FLUSH = 9

HAND_NAMES = {
    HIGH_CARD: "High Card",
    PAIR: "Pair",
    TWO_PAIR: "Two Pair",
    THREE_OF_KIND: "Three of a Kind",
    STRAIGHT: "Straight",
    FLUSH: "Flush",
    FULL_HOUSE: "Full House",
    FOUR_OF_KIND: "Four of a Kind",
    STRAIGHT_FLUSH: "Straight Flush",
    ROYAL_FLUSH: "Royal Flush",
}

RANK_NAMES = {11: "Jacks", 12: "Queens", 13: "Kings", 14: "Aces"}


def _rank_counts(hand):
    return Counter(card.rank for card in hand)


def is_flush(hand):
    suits = [card.suit for card in hand]
    return len(set(suits)) == 1


def is_straight(hand):
    ranks = sorted(set(card.rank for card in hand))
    if len(ranks) != 5:
        return False
    if ranks[-1] - ranks[0] == 4:
        return True
    if ranks == [2, 3, 4, 5, 14]:
        return True
    return False


def is_pair(hand):
    counts = _rank_counts(hand)
    return 2 in counts.values()


def is_two_pair(hand):
    counts = _rank_counts(hand)
    pairs = [r for r, c in counts.items() if c == 2]
    return len(pairs) == 2


def is_three_of_kind(hand):
    counts = _rank_counts(hand)
    return 3 in counts.values()


def is_full_house(hand):
    counts = _rank_counts(hand)
    values = sorted(counts.values())
    return values == [2, 3]


def is_four_of_kind(hand):
    counts = _rank_counts(hand)
    return 4 in counts.values()


def is_straight_flush(hand):
    return is_straight(hand) and is_flush(hand)


def is_royal_flush(hand):
    if not is_straight_flush(hand):
        return False
    ranks = sorted(card.rank for card in hand)
    return ranks == [10, 11, 12, 13, 14]


def evaluate_hand(hand):
    counts = _rank_counts(hand)
    tiebreakers = sorted(counts.keys(), key=lambda r: (counts[r], r), reverse=True)

    ranks = sorted(card.rank for card in hand)
    if is_straight(hand) and ranks == [2, 3, 4, 5, 14]:
        tiebreakers = [1 if r == 14 else r for r in tiebreakers]
        tiebreakers.sort(reverse=True)

    if is_royal_flush(hand):
        return (ROYAL_FLUSH, tiebreakers)
    if is_straight_flush(hand):
        return (STRAIGHT_FLUSH, tiebreakers)
    if is_four_of_kind(hand):
        return (FOUR_OF_KIND, tiebreakers)
    if is_full_house(hand):
        return (FULL_HOUSE, tiebreakers)
    if is_flush(hand):
        return (FLUSH, tiebreakers)
    if is_straight(hand):
        return (STRAIGHT, tiebreakers)
    if is_three_of_kind(hand):
        return (THREE_OF_KIND, tiebreakers)
    if is_two_pair(hand):
        return (TWO_PAIR, tiebreakers)
    if is_pair(hand):
        return (PAIR, tiebreakers)
    return (HIGH_CARD, tiebreakers)


def best_of_seven(cards):
    if len(cards) < 5:
        raise ValueError("best_of_seven needs at least 5 cards")

    best_eval = None
    best_combo = None
    for combo in combinations(cards, 5):
        result = evaluate_hand(list(combo))
        if best_eval is None or result > best_eval:
            best_eval = result
            best_combo = combo

    return best_eval[0], best_eval[1], list(best_combo)


def hand_strength_description(hand_type_int, tiebreakers=None):
    name = HAND_NAMES.get(hand_type_int, "Unknown")
    if not tiebreakers:
        return name

    if hand_type_int == FULL_HOUSE and len(tiebreakers) >= 2:
        trip = RANK_NAMES.get(tiebreakers[0], str(tiebreakers[0]))
        pair = RANK_NAMES.get(tiebreakers[1], str(tiebreakers[1]))
        return f"Full House, {trip} over {pair}"

    if hand_type_int in (FOUR_OF_KIND, THREE_OF_KIND, PAIR) and tiebreakers:
        top = RANK_NAMES.get(tiebreakers[0], str(tiebreakers[0]))
        return f"{name}, {top}"

    if hand_type_int == TWO_PAIR and len(tiebreakers) >= 2:
        hi = RANK_NAMES.get(tiebreakers[0], str(tiebreakers[0]))
        lo = RANK_NAMES.get(tiebreakers[1], str(tiebreakers[1]))
        return f"Two Pair, {hi} and {lo}"

    return name
