import random

SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = list(range(2, 15))  # 2-14, 14 = Ace

RANK_NAMES = {
    11: 'J', 12: 'Q', 13: 'K', 14: 'A'
}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        rank_str = RANK_NAMES.get(self.rank, str(self.rank))
        return f"{rank_str}{self.suit[0].upper()}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, n):
        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        return dealt

    def remaining(self):
        return len(self.cards)