from collections import Counter

# Hand type ints (higher = better)
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


def _rank_counts(hand):
    return Counter(card.rank for card in hand)


def is_flush(hand):
    suits = [card.suit for card in hand]
    return len(set(suits)) == 1


def is_straight(hand):
    ranks = sorted(set(card.rank for card in hand))
    if len(ranks) != 5:
        return False
    # normal straight
    if ranks[-1] - ranks[0] == 4:
        return True
    # special case: A-2-3-4-5 (wheel), Ace counted low
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
    """
    Takes a list of 5 Card objects.
    Returns (hand_type_int, tiebreakers_list) where tiebreakers_list
    is ranks sorted by (count desc, rank desc) for comparing equal hand types.
    """
    counts = _rank_counts(hand)
    # sort ranks by frequency then rank value, both descending
    tiebreakers = sorted(counts.keys(), key=lambda r: (counts[r], r), reverse=True)

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