"""
algorithm/expectiminimax.py
=============================
Week 1 implementation of the Expectiminimax search algorithm for
heads-up Texas Hold'em decision making.

Expectiminimax extends classic minimax with a third node type to
handle randomness (in poker: unknown community cards):

    * MAX node   -> the AI's turn. Pick the action with the highest
                    expected value.
    * MIN node   -> the opponent's turn. Assuming a rational,
                    adversarial opponent, pick the action that
                    minimizes the AI's expected value.
    * CHANCE node -> a community card is about to be revealed. The
                    value is the probability-weighted average over
                    all possible cards.

Scope note (Week 1 vs Week 2)
------------------------------
This module provides a *runnable, correct* baseline:
    - Depth-limited recursion (search stops at depth 0).
    - Deterministic MAX/MIN transitions between fold/check/call/raise.
    - CHANCE nodes sample a bounded number of possible next cards
      from the remaining deck (see ``get_chance_outcomes``) rather
      than enumerating the full outcome space with exact
      combinatorial probabilities.

Per the project roadmap, exact chance-node enumeration and a
persistent game-tree structure are implemented in Week 2's
``algorithm/game_tree.py``. This file's ``expectiminimax`` function is
designed so that Week 2 can swap in a fully enumerated
``get_chance_outcomes`` without changing the public API.
"""

import itertools
import random
from typing import Dict, List, Optional, Tuple

from algorithm.evaluation import evaluate_hand

State = Dict[str, object]

VALID_ACTIONS = ("fold", "check", "call", "raise")
_RAISE_INCREMENT = 20  # Chips added to the pot on a 'raise' action.

# How many possible next cards to sample at a CHANCE node in this
# Week 1 baseline. A full implementation (Week 2) would enumerate all
# remaining cards; sampling keeps runtime bounded for now.
_CHANCE_SAMPLE_SIZE = 4


def get_possible_actions(state: State) -> List[str]:
    """Return the legal actions available at the current state.

    Args:
        state: The current game state dict.

    Returns:
        A list of action strings drawn from
        ``('fold', 'check', 'call', 'raise')``.

    Example:
        >>> get_possible_actions({'current_bet': 0})
        ['fold', 'check', 'call', 'raise']
    """
    return list(VALID_ACTIONS)


def _best_five_card_score(cards: List[Dict[str, object]]) -> float:
    """Compute a heuristic strength score for a set of known cards.

    If 5 or more cards are known (hole cards + community cards), the
    best possible 5-card combination is scored with
    ``evaluate_hand`` (0-9 scale). If fewer than 5 cards are known
    (e.g. preflop), a simple normalized high-card heuristic is used
    instead, since a full hand cannot yet be formed.

    Args:
        cards: All known cards available to a player (hole cards plus
            any revealed community cards).

    Returns:
        A float score, roughly on a 0-9 scale, where higher is
        stronger.
    """
    if len(cards) >= 5:
        best_score = 0
        for combo in itertools.combinations(cards, 5):
            score = evaluate_hand(list(combo))
            best_score = max(best_score, score)
        return float(best_score)

    if not cards:
        return 0.0

    # Preflop / partial-information heuristic: normalize average rank
    # (2-14) onto roughly the same 0-9 scale used post-flop.
    avg_rank = sum(card["rank"] for card in cards) / len(cards)
    return (avg_rank - 2) / (14 - 2) * 9


def evaluate_state(state: State) -> float:
    """Static evaluation function used at depth-limited leaf nodes.

    Scores the state from the AI's perspective: higher is better for
    the AI. Combines the AI's best hand strength with the size of the
    pot it stands to win (larger pot -> higher stakes -> the strength
    differential matters more).

    Args:
        state: The current game state dict. Must contain
            'player_hand', 'community_cards', and 'pot'.

    Returns:
        A float expected-value estimate for the AI.

    Example:
        >>> s = {
        ...     'player_hand': [{'rank': 14, 'suit': 'hearts'},
        ...                     {'rank': 13, 'suit': 'hearts'}],
        ...     'community_cards': [],
        ...     'pot': 30,
        ... }
        >>> evaluate_state(s) > 0
        True
    """
    known_cards = list(state["player_hand"]) + list(state["community_cards"])
    hand_strength = _best_five_card_score(known_cards)
    pot = float(state.get("pot", 0))
    # Weight hand strength heavily; let pot size act as a mild scaling
    # factor representing "how much is at stake".
    return hand_strength * 10.0 + pot * 0.1


def is_terminal(state: State) -> bool:
    """Return True if no further search should happen at this state.

    A state is terminal if a player has folded or the hand has
    reached showdown.

    Args:
        state: The current game state dict.

    Returns:
        True if the state is terminal.
    """
    return state.get("phase") in ("folded", "showdown")


def apply_action(state: State, action: str) -> State:
    """Apply an action to a state and return the resulting new state.

    This is a simplified, deterministic state-transition function
    intended for Week 1. It does not mutate the input state.

    Args:
        state: The current game state dict.
        action: One of 'fold', 'check', 'call', 'raise'.

    Returns:
        A new state dict reflecting the result of the action.

    Raises:
        ValueError: If ``action`` is not a recognized action.

    Example:
        >>> s = {'pot': 20, 'current_bet': 0, 'to_move': 'max', 'phase': 'preflop',
        ...      'player_hand': [], 'community_cards': [], 'deck': []}
        >>> new_s = apply_action(s, 'raise')
        >>> new_s['pot'] > s['pot']
        True
    """
    if action not in VALID_ACTIONS:
        raise ValueError(f"Unknown action: {action!r}")

    new_state = dict(state)  # shallow copy is sufficient here
    new_state["pot"] = state.get("pot", 0)

    if action == "fold":
        new_state["phase"] = "folded"
        return new_state

    if action == "raise":
        new_state["pot"] = state.get("pot", 0) + _RAISE_INCREMENT
        new_state["current_bet"] = state.get("current_bet", 0) + _RAISE_INCREMENT

    if action == "call":
        new_state["pot"] = state.get("pot", 0) + state.get("current_bet", 0)
        new_state["current_bet"] = 0

    # 'check' leaves the pot unchanged.

    # Alternate whose turn it is; the caller decides when a chance
    # node (new community card) should interrupt this alternation.
    new_state["to_move"] = "min" if state.get("to_move") == "max" else "max"
    return new_state


def get_chance_outcomes(state: State) -> List[Tuple[float, State]]:
    """Generate possible outcomes of the next community card reveal.

    Week 1 simplified version: samples up to ``_CHANCE_SAMPLE_SIZE``
    cards uniformly at random from the remaining deck and assigns each
    an equal probability. Week 2's ``game_tree.get_chance_outcomes``
    replaces this with exhaustive enumeration of all remaining cards
    (exact probabilities).

    Args:
        state: The current game state dict. Must contain a 'deck' key
            listing remaining unseen cards.

    Returns:
        A list of ``(probability, new_state)`` tuples whose
        probabilities sum to 1.0.

    Example:
        >>> deck = [{'rank': r, 'suit': 'clubs'} for r in range(2, 10)]
        >>> s = {'deck': deck, 'community_cards': [], 'phase': 'preflop',
        ...      'pot': 20, 'current_bet': 0, 'to_move': 'chance',
        ...      'player_hand': []}
        >>> outcomes = get_chance_outcomes(s)
        >>> abs(sum(p for p, _ in outcomes) - 1.0) < 1e-9
        True
    """
    deck = list(state.get("deck", []))
    if not deck:
        # No cards left to reveal; treat as a single deterministic
        # "no-op" outcome so the caller can still recurse safely.
        return [(1.0, dict(state))]

    sample_size = min(_CHANCE_SAMPLE_SIZE, len(deck))
    sampled_cards = random.sample(deck, sample_size)
    probability = 1.0 / sample_size

    outcomes: List[Tuple[float, State]] = []
    phase_order = {"preflop": "flop", "flop": "turn", "turn": "river", "river": "showdown"}

    for card in sampled_cards:
        new_state = dict(state)
        new_state["community_cards"] = list(state["community_cards"]) + [card]
        new_state["deck"] = [c for c in deck if c is not card]
        new_state["phase"] = phase_order.get(state.get("phase", "preflop"), "showdown")
        new_state["to_move"] = "max"  # AI acts first after a new card, for simplicity
        outcomes.append((probability, new_state))

    return outcomes


def expectiminimax(state: State, depth: int) -> Tuple[Optional[str], float]:
    """Recursively search the game tree and return the best action.

    Args:
        state: The current game state dict. Expected keys:
            'player_hand', 'community_cards', 'deck', 'pot',
            'current_bet', 'phase', and 'to_move' (one of
            'max', 'min', 'chance').
        depth: Remaining search depth (plies). Search stops and falls
            back to ``evaluate_state`` when depth reaches 0.

    Returns:
        A tuple ``(best_action, expected_value)``. ``best_action`` is
        ``None`` at leaf/chance nodes, since no single discrete action
        applies there.

    Example:
        >>> s = {
        ...     'player_hand': [{'rank': 14, 'suit': 'hearts'},
        ...                     {'rank': 13, 'suit': 'hearts'}],
        ...     'community_cards': [],
        ...     'deck': [{'rank': r, 'suit': 'clubs'} for r in range(2, 10)],
        ...     'pot': 30,
        ...     'current_bet': 20,
        ...     'phase': 'preflop',
        ...     'to_move': 'max',
        ... }
        >>> action, value = expectiminimax(s, depth=2)
        >>> action in ('fold', 'check', 'call', 'raise')
        True
    """
    if depth <= 0 or is_terminal(state):
        return None, evaluate_state(state)

    node_type = state.get("to_move", "max")

    if node_type == "chance":
        outcomes = get_chance_outcomes(state)
        expected_value = sum(
            probability * expectiminimax(child_state, depth - 1)[1]
            for probability, child_state in outcomes
        )
        return None, expected_value

    actions = get_possible_actions(state)
    best_action: Optional[str] = None

    if node_type == "max":
        best_value = float("-inf")
        for action in actions:
            child_state = apply_action(state, action)
            _, value = expectiminimax(child_state, depth - 1)
            if value > best_value:
                best_value = value
                best_action = action
        return best_action, best_value

    if node_type == "min":
        best_value = float("inf")
        for action in actions:
            child_state = apply_action(state, action)
            _, value = expectiminimax(child_state, depth - 1)
            if value < best_value:
                best_value = value
                best_action = action
        return best_action, best_value

    raise ValueError(f"Unknown node type in state['to_move']: {node_type!r}")


if __name__ == "__main__":
    # Minimal runnable example.
    example_deck = [{"rank": r, "suit": s} for r in range(2, 15) for s in ("clubs", "diamonds")]
    example_state: State = {
        "player_hand": [{"rank": 14, "suit": "hearts"}, {"rank": 13, "suit": "hearts"}],
        "community_cards": [],
        "deck": example_deck,
        "pot": 30,
        "current_bet": 20,
        "phase": "preflop",
        "to_move": "max",
    }
    best_action, expected_value = expectiminimax(example_state, depth=2)
    print(f"Best action: {best_action}, expected value: {expected_value:.2f}")
