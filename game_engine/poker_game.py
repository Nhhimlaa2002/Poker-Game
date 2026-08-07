import json
import os

from game_engine.card import Deck
from game_engine.hand_evaluator import best_of_seven, hand_strength_description
import config


class Player:
    def __init__(self, name, chips=1000, is_ai=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.total_bet_this_hand = 0
        self.is_folded = False
        self.is_all_in = False
        self.is_ai = is_ai
        self.raise_increment = 20

    def __repr__(self):
        return f"Player({self.name}, chips={self.chips}, folded={self.is_folded})"


class GameHistory:
    def __init__(self, path="data/game_history.json"):
        self.path = path
        self._ensure_dir()
        self.records = self._load()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def log_action(self, hand_number, phase, player_name, action, pot_after):
        self.records.append({
            "hand": hand_number,
            "phase": phase,
            "player": player_name,
            "action": action,
            "pot_after": pot_after,
        })

    def log_result(self, hand_number, winners, pot_amount):
        self.records.append({
            "hand": hand_number,
            "phase": "showdown",
            "winners": [w.name for w in winners],
            "pot_awarded": pot_amount,
        })
        self.save()

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.records, f, indent=2)


class GameState:
    PHASES = ["preflop", "flop", "turn", "river", "showdown"]
    LEGAL_ACTIONS = ("fold", "call", "raise")

    def __init__(self, players, history=None):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_player_index = 0
        self.phase = "preflop"
        self.history = history

    def new_round(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_player_index = 0
        self.phase = "preflop"
        for player in self.players:
            player.hand = []
            player.current_bet = 0
            player.total_bet_this_hand = 0
            player.is_folded = False
            player.is_all_in = False
            if player.chips <= 0:
                player.is_folded = True

    def deal_hole_cards(self):
        for player in self.players:
            if not player.is_folded:
                player.hand = self.deck.deal(2)

    def next_phase(self):
        current_index = self.PHASES.index(self.phase)
        if current_index < len(self.PHASES) - 1:
            self.phase = self.PHASES[current_index + 1]
        return self.phase

    def evaluate_hand(self, seven_cards):
        hand_type, tiebreakers, _ = best_of_seven(seven_cards)
        return (hand_type, tiebreakers)

    def get_active_players(self):
        return [p for p in self.players if not p.is_folded]

    def get_actionable_players(self):
        return [p for p in self.get_active_players() if not p.is_all_in]

    def legal_actions_for(self, player):
        if player.is_folded or player.is_all_in:
            return []
        actions = ["fold", "call"]
        table_bet = max((p.current_bet for p in self.players), default=0)
        to_call = table_bet - player.current_bet
        if player.chips > to_call:
            actions.append("raise")
        return actions

    def betting_round(self, ai_decision_func=None, human_action_func=None):
        active = self.get_active_players()
        if len(active) <= 1:
            return
        if len(self.get_actionable_players()) == 0:
            return

        current_bet = max(p.current_bet for p in active)
        last_raiser = None
        idx = self.current_player_index
        acted_since_raise = 0
        num_players = len(self.players)

        while True:
            player = self.players[idx % num_players]

            if not player.is_folded and not player.is_all_in and (
                player.current_bet < current_bet or player is not last_raiser
            ):
                if getattr(player, "is_ai", False) and ai_decision_func:
                    action = ai_decision_func(self, player)
                elif human_action_func and not getattr(player, "is_ai", False):
                    action = human_action_func(self, player)
                else:
                    action = "call"

                self._apply_action(player, action, current_bet)

                if action == "raise":
                    current_bet = player.current_bet
                    last_raiser = player
                    acted_since_raise = 0
                else:
                    acted_since_raise += 1

                if self.history:
                    self.history.log_action(
                        getattr(self, "hand_number", 0), self.phase,
                        player.name, action, self.pot,
                    )

                if len(self.get_active_players()) <= 1:
                    break
                if len(self.get_actionable_players()) == 0:
                    break

            idx += 1

            if last_raiser is None and acted_since_raise >= len(self.get_actionable_players()):
                break
            if last_raiser and acted_since_raise >= len(self.get_actionable_players()):
                break
            if idx > self.current_player_index + 4 * num_players:
                break

    def _apply_action(self, player, action, current_bet):
        if action == "fold":
            player.is_folded = True
            return

        if action == "call":
            diff = min(current_bet - player.current_bet, player.chips)
            diff = max(diff, 0)
            player.chips -= diff
            player.current_bet += diff
            player.total_bet_this_hand += diff
            self.pot += diff
            if player.chips == 0:
                player.is_all_in = True
            return

        if action == "raise":
            raise_to = current_bet + getattr(player, "raise_increment", 20)
            total = min(raise_to - player.current_bet, player.chips)
            total = max(total, 0)
            player.chips -= total
            player.current_bet += total
            player.total_bet_this_hand += total
            self.pot += total
            if player.chips == 0:
                player.is_all_in = True
            return

    def reset_bets(self):
        for player in self.players:
            player.current_bet = 0
        self.current_player_index = self._first_active_index()

    def _first_active_index(self):
        for i, p in enumerate(self.players):
            if not p.is_folded and not p.is_all_in:
                return i
        return 0

    def deal_flop(self):
        self.deck.deal(1)
        self.community_cards.extend(self.deck.deal(3))

    def deal_turn(self):
        self.deck.deal(1)
        self.community_cards.extend(self.deck.deal(1))

    def deal_river(self):
        self.deck.deal(1)
        self.community_cards.extend(self.deck.deal(1))

    def _build_side_pots(self):
        contributors = [p for p in self.players if p.total_bet_this_hand > 0]
        if not contributors:
            return [(self.pot, self.get_active_players())]

        levels = sorted(set(p.total_bet_this_hand for p in contributors))
        pots = []
        previous_level = 0
        for level in levels:
            layer_contributors = [p for p in contributors if p.total_bet_this_hand >= level]
            layer_amount = (level - previous_level) * len(layer_contributors)
            eligible = [p for p in layer_contributors if not p.is_folded]
            if layer_amount > 0:
                pots.append((layer_amount, eligible))
            previous_level = level

        return pots if pots else [(self.pot, self.get_active_players())]

    def showdown(self):
        active = self.get_active_players()

        if len(active) == 1:
            winner = active[0]
            winner.chips += self.pot
            if self.history:
                self.history.log_result(getattr(self, "hand_number", 0), [winner], self.pot)
            return winner, self.pot

        side_pots = self._build_side_pots()
        results = {}
        for player in active:
            seven = player.hand + self.community_cards
            hand_type, tiebreakers, best5 = best_of_seven(seven)
            results[player] = (hand_type, tiebreakers, best5)

        all_winners = []
        total_awarded = 0
        for amount, eligible in side_pots:
            if not eligible:
                continue
            best_score = max((results[p][0], results[p][1]) for p in eligible)
            pot_winners = [p for p in eligible if (results[p][0], results[p][1]) == best_score]
            share = amount // len(pot_winners)
            remainder = amount - share * len(pot_winners)
            for i, w in enumerate(pot_winners):
                award = share + (remainder if i == 0 else 0)
                w.chips += award
                total_awarded += award
                if w not in all_winners:
                    all_winners.append(w)

        if self.history:
            self.history.log_result(getattr(self, "hand_number", 0), all_winners, total_awarded)

        primary_winner = all_winners[0] if all_winners else active[0]
        return primary_winner, total_awarded

    def save_hand_history(self, hand_number, winner, pot_amount, path="data/hand_history.txt"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        lines = [f"=== Hand #{hand_number} ==="]
        lines.append(f"Community: {self.community_cards}")
        for p in self.players:
            status = "folded" if p.is_folded else "active"
            lines.append(f"  {p.name} ({status}): {p.hand}")
        lines.append(f"Winner: {winner.name} | Pot: ${pot_amount}\n")
        with open(path, "a") as f:
            f.write("\n".join(lines) + "\n")

    def ai_make_decision(self, player, depth=None, hand_number=1, strategy=None):
        if depth is None:
            depth = config.AI_DEPTH

        table_bet = max(p.current_bet for p in self.players)
        state = {
            "player_hand": [{"rank": c.rank, "suit": c.suit} for c in player.hand],
            "community_cards": [{"rank": c.rank, "suit": c.suit} for c in self.community_cards],
            "deck": [{"rank": c.rank, "suit": c.suit} for c in self.deck.cards],
            "pot": self.pot,
            "current_bet": max(0, table_bet - player.current_bet),
            "phase": self.phase,
            "to_move": "max",
            "actions_this_phase": 0,
            "player_chips": player.chips,
            "num_active_opponents": len(self.get_active_players()) - 1,
        }

        if strategy is not None:
            action = strategy(state, self.phase)
        else:
            from algorithm.expectiminimax import make_decision
            action = make_decision(state, depth=depth, hand_number=hand_number)

        legal = self.legal_actions_for(player)
        if action not in legal:
            action = "call" if "call" in legal else ("fold" if "fold" in legal else "raise")
        return action

    def estimate_win_stars(self, player, simulations=250):
        from algorithm.monte_carlo import estimate_win_probability, stars_for_probability

        opponents = [p for p in self.get_active_players() if p is not player]
        if not opponents or not player.hand:
            return 0, 0.0

        player_hand = [{"rank": c.rank, "suit": c.suit} for c in player.hand]
        community = [{"rank": c.rank, "suit": c.suit} for c in self.community_cards]
        deck = [{"rank": c.rank, "suit": c.suit} for c in self.deck.cards]

        win_prob = estimate_win_probability(
            player_hand, community, deck,
            num_opponents=len(opponents), simulations=simulations,
        )
        return stars_for_probability(win_prob), win_prob

    def play_round(self, ai_decision_func=None, human_action_func=None, hand_number=1):
        self.hand_number = hand_number
        self.new_round()
        self.deal_hole_cards()

        active_idxs = [i for i, p in enumerate(self.players) if not p.is_folded]
        if len(active_idxs) < 2:
            winner = self.players[active_idxs[0]] if active_idxs else self.players[0]
            return winner, 0

        sb = self.players[active_idxs[0]]
        bb = self.players[active_idxs[1 % len(active_idxs)]]
        self._post_blind(sb, config.SMALL_BLIND)
        self._post_blind(bb, config.BIG_BLIND)
        self.current_player_index = active_idxs[2 % len(active_idxs)] if len(active_idxs) > 2 else active_idxs[0]

        self.betting_round(ai_decision_func, human_action_func)
        if len(self.get_active_players()) <= 1:
            winner, pot = self.showdown()
            self.save_hand_history(hand_number, winner, pot)
            return winner, pot

        for deal_fn in (self.deal_flop, self.deal_turn, self.deal_river):
            self.reset_bets()
            deal_fn()
            self.next_phase()
            self.betting_round(ai_decision_func, human_action_func)
            if len(self.get_active_players()) <= 1:
                winner, pot = self.showdown()
                self.save_hand_history(hand_number, winner, pot)
                return winner, pot

        self.next_phase()
        winner, pot = self.showdown()
        self.save_hand_history(hand_number, winner, pot)
        return winner, pot

    def _post_blind(self, player, amount):
        amount = min(amount, player.chips)
        player.chips -= amount
        player.current_bet += amount
        player.total_bet_this_hand += amount
        self.pot += amount
        if player.chips == 0:
            player.is_all_in = True
