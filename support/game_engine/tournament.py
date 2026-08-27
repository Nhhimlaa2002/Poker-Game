import config
from game_engine.poker_game import GameState, GameHistory


class Tournament:
    def __init__(self, players, small_blind=None, big_blind=None,
                 blind_increase_every=None, blind_increase_factor=None):
        self.players = players
        self.small_blind = small_blind or config.SMALL_BLIND
        self.big_blind = big_blind or config.BIG_BLIND
        self.blind_increase_every = blind_increase_every or config.BLIND_INCREASE_EVERY_N_ROUNDS
        self.blind_increase_factor = blind_increase_factor or config.BLIND_INCREASE_FACTOR

        self.round_number = 0
        self.eliminated = []
        self.history = GameHistory()

    def active_players(self):
        return [p for p in self.players if p.chips > 0]

    def is_over(self):
        return len(self.active_players()) <= 1

    def _maybe_increase_blinds(self):
        if self.round_number > 0 and self.round_number % self.blind_increase_every == 0:
            self.small_blind = int(self.small_blind * self.blind_increase_factor)
            self.big_blind = int(self.big_blind * self.blind_increase_factor)

    def _check_eliminations(self):
        for p in self.players:
            if p.chips <= 0 and p not in self.eliminated:
                self.eliminated.append(p)

    def play_round(self, ai_decision_func=None, human_action_func=None):
        self.round_number += 1
        self._maybe_increase_blinds()

        active = self.active_players()
        config.SMALL_BLIND = self.small_blind
        config.BIG_BLIND = self.big_blind

        state = GameState(active, history=self.history)
        winner, pot = state.play_round(
            ai_decision_func=ai_decision_func,
            human_action_func=human_action_func,
            hand_number=self.round_number,
        )
        self._check_eliminations()
        return winner, pot

    def run(self, ai_decision_func=None, human_action_func=None, max_rounds=500):
        results_log = []
        while not self.is_over() and self.round_number < max_rounds:
            winner, pot = self.play_round(ai_decision_func, human_action_func)
            results_log.append({
                "round": self.round_number,
                "winner": winner.name,
                "pot": pot,
                "small_blind": self.small_blind,
                "big_blind": self.big_blind,
            })

        champion = self.active_players()[0] if self.active_players() else None
        return champion, results_log

    def leaderboard(self):
        return sorted(self.players, key=lambda p: p.chips, reverse=True)
