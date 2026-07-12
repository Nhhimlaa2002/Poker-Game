"""
evaluation.py

This file scores how strong a 5-card poker hand is.

A card is represented as a simple dictionary, like this:
    {"rank": 14, "suit": "hearts"}

Rank numbers: 2-10 are normal, 11=Jack, 12=Queen, 13=King, 14=Ace.

The score returned is a number from 0 to 9:
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

Higher score = stronger hand.
"""


def is_flush(hand):
    """
    Check if all 5 cards have the same suit.

    hand: a list of 5 card dictionaries
    returns: True if it is a flush, False otherwise
    """
    first_suit = hand[0]["suit"]

    for card in hand:
        if card["suit"] != first_suit:
            return False

    return True


def is_straight(hand):
    """
    Check if the 5 cards are in a row (like 5,6,7,8,9).

    hand: a list of 5 card dictionaries
    returns: True if it is a straight, False otherwise
    """
    # Get all the ranks and put them in order from smallest to largest
    rank_list = []
    for card in hand:
        rank_list.append(card["rank"])
    rank_list.sort()

    # Special case: Ace can be used as a "1" in the straight A-2-3-4-5
    if rank_list == [2, 3, 4, 5, 14]:
        return True

    # Check that there are no duplicate ranks
    # (a straight cannot have two cards of the same rank)
    for i in range(len(rank_list) - 1):
        if rank_list[i] == rank_list[i + 1]:
            return False

    # If the cards are in a row, the biggest minus the smallest should be 4
    biggest = rank_list[4]
    smallest = rank_list[0]
    if biggest - smallest == 4:
        return True

    return False


def count_ranks(hand):
    """
    Count how many times each rank appears in the hand.

    hand: a list of 5 card dictionaries
    returns: a dictionary like {14: 2, 9: 1, 3: 1, 2: 1}
             meaning rank 14 appeared twice, rank 9 once, etc.
    """
    rank_counts = {}

    for card in hand:
        rank = card["rank"]
        if rank in rank_counts:
            rank_counts[rank] = rank_counts[rank] + 1
        else:
            rank_counts[rank] = 1

    return rank_counts


def get_count_values_sorted(rank_counts):
    """
    Take the counts from count_ranks() and sort them from
    biggest to smallest. This tells us the "shape" of the hand.

    Example: a full house (three of one rank, two of another)
    gives counts like [3, 2].

    rank_counts: dictionary from count_ranks()
    returns: a list of numbers, sorted biggest to smallest
    """
    counts = []
    for rank in rank_counts:
        counts.append(rank_counts[rank])

    counts.sort(reverse=True)
    return counts


def evaluate_hand(hand):
    """
    Score a 5-card poker hand from 0 (weakest) to 9 (strongest).

    hand: a list of exactly 5 card dictionaries
    returns: an integer from 0 to 9

    Example:
        royal_flush = [
            {"rank": 14, "suit": "hearts"},
            {"rank": 13, "suit": "hearts"},
            {"rank": 12, "suit": "hearts"},
            {"rank": 11, "suit": "hearts"},
            {"rank": 10, "suit": "hearts"},
        ]
        evaluate_hand(royal_flush)  ->  9
    """
    if len(hand) != 5:
        raise ValueError("evaluate_hand needs exactly 5 cards")

    flush = is_flush(hand)
    straight = is_straight(hand)

    rank_counts = count_ranks(hand)
    counts = get_count_values_sorted(rank_counts)

    # We check the strongest possible hands first, and return
    # as soon as we find a match. This order matters!

    if flush and straight:
        rank_list = []
        for card in hand:
            rank_list.append(card["rank"])
        rank_list.sort()

        if rank_list == [10, 11, 12, 13, 14]:
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


# --- Example usage / quick manual test ---
if __name__ == "__main__":
    royal_flush = [
        {"rank": 14, "suit": "hearts"},
        {"rank": 13, "suit": "hearts"},
        {"rank": 12, "suit": "hearts"},
        {"rank": 11, "suit": "hearts"},
        {"rank": 10, "suit": "hearts"},
    ]
    print("Royal flush score:", evaluate_hand(royal_flush))  # should print 9

    one_pair = [
        {"rank": 5, "suit": "hearts"},
        {"rank": 5, "suit": "clubs"},
        {"rank": 9, "suit": "spades"},
        {"rank": 2, "suit": "diamonds"},
        {"rank": 11, "suit": "hearts"},
    ]
    print("One pair score:", evaluate_hand(one_pair))  # should print 1
