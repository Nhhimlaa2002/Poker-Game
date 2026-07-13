from game_engine.card import Deck
from game_engine.hand_evaluator import evaluate_hand
from itertools import combinations


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

    def get_active_players(self):
        """Players still in the hand (not folded)."""
        return [p for p in self.players if not p.is_folded]

    def betting_round(self, ai_decision_func=None, human_action_func=None):
        """Loop through active players until all bets are equalized."""
        active = self.get_active_players()
        if len(active) <= 1:
            return

        current_bet = max(p.current_bet for p in active)
        last_raiser = None
        idx = self.current_player_index

        while True:
            player = self.players[idx % len(self.players)]

            if not player.is_folded and (player.current_bet < current_bet or player is not last_raiser):
                if getattr(player, "is_ai", False) and ai_decision_func:
                    action = ai_decision_func(self, player)
                elif human_action_func and not getattr(player, "is_ai", False):
                    action = human_action_func(self, player)
                else:
                    action = "call"

                if action == "fold":
                    player.is_folded = True
                elif action == "call":
                    diff = min(current_bet - player.current_bet, player.chips)
                    player.chips -= diff
                    player.current_bet += diff
                    self.pot += diff
                elif action == "raise":
                    raise_to = current_bet + 20
                    total = min(raise_to - player.current_bet, player.chips)
                    player.chips -= total
                    player.current_bet += total
                    self.pot += total
                    current_bet = player.current_bet
                    last_raiser = player

                if len(self.get_active_players()) <= 1:
                    break

            idx += 1

            if last_raiser is None and idx > self.current_player_index + len(self.players):
                break
            if last_raiser and player is last_raiser:
                break