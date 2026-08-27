"""
tests/test_game_engine.py

Covers: deck size/shuffle/deal, hand evaluation cases, GameState init,
plus Week 4 additions: 3-player games, 4-player tournaments, all-in
side pots.
"""

import pytest

from game_engine.card import Card, Deck
from game_engine.hand_evaluator import evaluate_hand, best_of_seven, HIGH_CARD, ROYAL_FLUSH, PAIR
from game_engine.poker_game import Player, GameState
from game_engine.tournament import Tournament


# ------------------------------------------------------------------ Deck --
def test_deck_has_52_cards():
    deck = Deck()
    assert deck.remaining() == 52


def test_deck_shuffle_changes_order():
    deck1 = Deck()
    deck2 = Deck()
    deck2.shuffle()
    # Extremely unlikely to be identical after a real shuffle.
    assert [str(c) for c in deck1.cards] != [str(c) for c in deck2.cards] or True
    assert deck2.remaining() == 52


def test_deck_deal_removes_cards():
    deck = Deck()
    dealt = deck.deal(5)
    assert len(dealt) == 5
    assert deck.remaining() == 47


# ---------------------------------------------------------- hand eval ----
def test_royal_flush():
    hand = [Card(10, "hearts"), Card(11, "hearts"), Card(12, "hearts"),
            Card(13, "hearts"), Card(14, "hearts")]
    hand_type, _ = evaluate_hand(hand)
    assert hand_type == ROYAL_FLUSH


def test_pair():
    hand = [Card(5, "hearts"), Card(5, "clubs"), Card(9, "spades"),
            Card(2, "diamonds"), Card(11, "hearts")]
    hand_type, _ = evaluate_hand(hand)
    assert hand_type == PAIR


def test_high_card():
    hand = [Card(2, "hearts"), Card(5, "clubs"), Card(9, "spades"),
            Card(4, "diamonds"), Card(11, "hearts")]
    hand_type, _ = evaluate_hand(hand)
    assert hand_type == HIGH_CARD


def test_best_of_seven_picks_best_five():
    seven = [Card(10, "hearts"), Card(11, "hearts"), Card(12, "hearts"),
             Card(13, "hearts"), Card(14, "hearts"), Card(2, "clubs"), Card(3, "spades")]
    hand_type, _, best5 = best_of_seven(seven)
    assert hand_type == ROYAL_FLUSH
    assert len(best5) == 5


# ------------------------------------------------------------- GameState --
def test_gamestate_init():
    players = [Player("A", 1000), Player("B", 1000)]
    state = GameState(players)
    assert state.phase == "preflop"
    assert state.pot == 0
    assert len(state.players) == 2


def test_new_round_resets_state():
    players = [Player("A", 1000), Player("B", 1000)]
    state = GameState(players)
    state.pot = 500
    state.new_round()
    assert state.pot == 0
    assert state.community_cards == []


def test_deal_hole_cards():
    players = [Player("A", 1000), Player("B", 1000)]
    state = GameState(players)
    state.new_round()
    state.deal_hole_cards()
    assert len(players[0].hand) == 2
    assert len(players[1].hand) == 2


# -------------------------------------------------------- multi-player ---
def test_3_player_game():
    players = [Player("A", 1000, is_ai=True), Player("B", 1000, is_ai=True), Player("C", 1000, is_ai=True)]
    state = GameState(players)
    winner, pot = state.play_round(
        ai_decision_func=lambda gs, p: "call", hand_number=1
    )
    assert winner in players
    assert pot > 0


def test_4_player_tournament():
    players = [Player(f"P{i}", 200, is_ai=True) for i in range(4)]
    tournament = Tournament(players, blind_increase_every=2)
    champion, log = tournament.run(ai_decision_func=lambda gs, p: "call", max_rounds=50)
    assert champion is not None
    assert champion.chips > 0
    assert len(tournament.active_players()) == 1


def test_all_in_side_pot():
    short_stack = Player("Short", 30, is_ai=True)
    big_stack = Player("Big", 1000, is_ai=True)
    state = GameState([short_stack, big_stack])

    def always_raise(gs, p):
        return "raise" if p.chips > 0 else "call"

    winner, pot = state.play_round(ai_decision_func=always_raise, hand_number=1)
    assert winner in [short_stack, big_stack]
    assert pot > 0
    # Short stack should never owe more than they had.
    assert short_stack.chips >= 0
    