"""
algorithm/evaluation.py
========================
A fast, coarse hand-strength evaluator used internally by the
Expectiminimax search (algorithm/expectiminimax.py) as its static
evaluation function.

This is intentionally lightweight: it returns a single integer score
(0-9) rather than detailed tiebreaker information. For determining an
actual showdown winner between two hands of the same category, use
``game_engine.hand_evaluator.evaluate_hand`` instead, which returns
tiebreaker kicker information as well.

Score scale
-----------
0 = High card
1 = Pair
2 = Two pair
3 = Three of a kind
4 = Straight
5 = Flush
6 = Full house
7 = Four of a kind
8 = Straight flush
9 = Royal flush

Card representation
--------------------
Each card is a ``dict`` with keys:
    - 'rank': int in range 2-14 (14 = Ace)
    - 'suit': str, one of 'hearts', 'diamonds', 'clubs', 'spades'

This dict-based representation (rather than the ``Card`` class from
``game_engine.card``) is used deliberately so that the algorithm/
package has no import dependency on game_engine/, letting the two
modules be developed independently.
"""

from collections import Counter
from typing import Dict, List

CardDict = Dict[str, object]


def is_flush(cards: List[CardDict]) -> bool:
    """Return True if all cards share the same suit.

    Args:
        cards: A list of 5 card dicts.

    Returns:
        True if every card has the same 'suit' value.

    Example:
        >>> hand = [{'rank': r, 'suit': 'hearts'} for r in (2, 4, 6, 8, 10)]
        >>> is_flush(hand)
        True
    """
    if not cards:
        return False
    first_suit = cards[0]["suit"]
    return all(card["suit"] == first_suit for card in cards)


def is_straight(cards: List[CardDict]) -> bool:
    """Return True if the cards form 5 consecutive ranks.

    Handles the special case of an Ace-low straight (A-2-3-4-5), where
    the Ace (rank 14) counts as rank 1.

    Args:
        cards: A list of 5 card dicts.

    Returns:
        True if the ranks are consecutive.

    Example:
        >>> hand = [{'rank': r, 'suit': 'spades'} for r in (10, 11, 12, 13, 14)]
        >>> is_straight(hand)
        True
    """
    if len(cards) != 5:
        return False

    ranks = sorted(card["rank"] for card in cards)
    if len(set(ranks)) != 5:
        return False  # can't be a straight with duplicate ranks

    if ranks == [2, 3, 4, 5, 14]:  # Ace-low straight (A-2-3-4-5)
        return True

    return ranks[-1] - ranks[0] == 4


def get_rank_counts(cards: List[CardDict]) -> Counter:
    """Count how many times each rank appears in the hand.

    Args:
        cards: A list of card dicts.

    Returns:
        A Counter mapping rank -> number of occurrences.

    Example:
        >>> hand = [{'rank': 10, 'suit': 'hearts'}, {'rank': 10, 'suit': 'clubs'}]
        >>> get_rank_counts(hand)[10]
        2
    """
    return Counter(card["rank"] for card in cards)


def evaluate_hand(cards: List[CardDict]) -> int:
    """Score a 5-card poker hand on a 0-9 scale.

    Args:
        cards: A list of exactly 5 card dicts, each with 'rank' (2-14)
            and 'suit' keys.

    Returns:
        An integer 0-9, where higher is a stronger hand
        (0=high card, ..., 9=royal flush).

    Raises:
        ValueError: If ``cards`` does not contain exactly 5 cards.

    Example:
        >>> royal_flush = [
        ...     {'rank': 14, 'suit': 'hearts'}, {'rank': 13, 'suit': 'hearts'},
        ...     {'rank': 12, 'suit': 'hearts'}, {'rank': 11, 'suit': 'hearts'},
        ...     {'rank': 10, 'suit': 'hearts'},
        ... ]
        >>> evaluate_hand(royal_flush)
        9
    """
    if len(cards) != 5:
        raise ValueError(f"evaluate_hand expects exactly 5 cards, got {len(cards)}")

    flush = is_flush(cards)
    straight = is_straight(cards)
    counts = sorted(get_rank_counts(cards).values(), reverse=True)

    if flush and straight:
        ranks = sorted(card["rank"] for card in cards)
        if ranks == [10, 11, 12, 13, 14]:
            return 9  # Royal flush
        return 8  # Straight flush

    if counts[0] == 4:
        return 7  # Four of a kind
    if counts[0] == 3 and counts[1] == 2:
        return 6  # Full house
    if flush:
        return 5
    if straight:
        return 4
    if counts[0] == 3:
        return 3  # Three of a kind
    if counts[0] == 2 and counts[1] == 2:
        return 2  # Two pair
    if counts[0] == 2:
        return 1  # Pair
    return 0  # High card


if __name__ == "__main__":
    # Quick manual sanity check (matches the Week 1 roadmap test):
    royal_flush = [
        {"rank": 14, "suit": "hearts"},
        {"rank": 13, "suit": "hearts"},
        {"rank": 12, "suit": "hearts"},
        {"rank": 11, "suit": "hearts"},
        {"rank": 10, "suit": "hearts"},
    ]
    print(evaluate_hand(royal_flush))  # -> 9
