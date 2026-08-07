"""
tests/test_integration.py

Full play_round() integration test with two AI players, no GUI.
"""

from game_engine.poker_game import Player, GameState


def simple_ai_policy(game_state, player):
    """A trivial always-call policy so the round runs headlessly and fast."""
    return "call"


def test_full_round_two_ai_players():
    p1 = Player("AI_1", 1000, is_ai=True)
    p2 = Player("AI_2", 1000, is_ai=True)
    state = GameState([p1, p2])

    winner, pot = state.play_round(ai_decision_func=simple_ai_policy, hand_number=1)

    assert winner in (p1, p2)
    assert pot > 0
    assert winner.chips > 0


def test_multiple_consecutive_rounds():
    p1 = Player("AI_1", 1000, is_ai=True)
    p2 = Player("AI_2", 1000, is_ai=True)
    state = GameState([p1, p2])

    for hand_num in range(1, 6):
        if p1.chips <= 0 or p2.chips <= 0:
            break
        winner, pot = state.play_round(ai_decision_func=simple_ai_policy, hand_number=hand_num)
        assert winner in (p1, p2)

    total_chips = p1.chips + p2.chips
    assert total_chips == 2000  # chips are conserved across hands