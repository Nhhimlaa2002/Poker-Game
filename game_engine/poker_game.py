from game_engine.card import Deck
from game_engine.hand_evaluator import evaluate_hand


class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.is_folded = False

    def __repr__(self):
        return f"Player({self.name}, chips={self.chips}, folded={self.is_folded})"


class GameState:
    PHASES = ['preflop', 'flop', 'turn', 'river', 'showdown']

    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_player_index = 0
        self.phase = 'preflop'

    def new_round(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_player_index = 0
        self.phase = 'preflop'
        for player in self.players:
            player.hand = []
            player.current_bet = 0
            player.is_folded = False

    def deal_hole_cards(self):
        for player in self.players:
            player.hand = self.deck.deal(2)

    def next_phase(self):
        current_index = self.PHASES.index(self.phase)
        if current_index < len(self.PHASES) - 1:
            self.phase = self.PHASES[current_index + 1]
        return self.phase

    def evaluate_hand(self, seven_cards):
        """Given 7 cards (2 hole + 5 community), return best 5-card evaluation."""
        from itertools import combinations
        best = None
        for combo in combinations(seven_cards, 5):
            result = evaluate_hand(list(combo))
            if best is None or result > best:
                best = result
        return best
    