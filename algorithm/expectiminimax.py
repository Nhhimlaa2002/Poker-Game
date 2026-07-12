"""
expectiminimax.py

This file contains the AI's decision-making function: expectiminimax.

Expectiminimax is like minimax (used in games like chess), but it
also handles randomness. In poker, after we make a move, a new
community card might be revealed - and we don't know which one in
advance. So we add a third type of "turn":

    MAX turn    -> it's the AI's turn. Pick the move with the
                   HIGHEST expected value (best for the AI).

    MIN turn    -> it's the opponent's turn. We assume they play
                   smart, so we imagine they pick whatever is
                   LOWEST value for us (worst for the AI).

    CHANCE turn -> a new card is about to be revealed. Since we
                   don't know which card, we look at a few possible
                   cards and average the results.

This file connects to:
    - evaluation.py   (used to score how strong a hand is)
    - actions.py      (used to get the list of legal moves)
"""

from algorithm.evaluation import evaluate_hand
from algorithm.actions import get_possible_actions

# How much the pot grows when a player raises.
RAISE_AMOUNT = 20

# How many possible next cards we look at when guessing what
# card might come next. A real version would check every single
# card left in the deck, but that is slower and more advanced.
# For this beginner-friendly version, we just look at the first
# few cards left in the deck.
NUMBER_OF_CARDS_TO_CHECK = 3


def evaluate_state(state):
    """
    Estimate how good the current situation looks for the AI.
    This is called a "static evaluation function" - it is used
    when we stop searching further ahead (depth = 0).

    state: a dictionary describing the game right now
    returns: a number - higher means better for the AI
    """
    known_cards = state["player_hand"] + state["community_cards"]

    if len(known_cards) >= 5:
        # Use the first 5 known cards to estimate hand strength.
        # (A more advanced version would check every possible
        # 5-card combination and pick the best one - that comes
        # in a later week.)
        five_cards = known_cards[0:5]
        hand_score = evaluate_hand(five_cards)
    else:
        # Not enough cards yet (for example, before the flop).
        # Just estimate using the average rank of the cards we have.
        total_rank = 0
        for card in known_cards:
            total_rank = total_rank + card["rank"]

        if len(known_cards) > 0:
            average_rank = total_rank / len(known_cards)
        else:
            average_rank = 0

        # Scale the average rank (2-14) down to roughly a 0-9 scale,
        # so it can be compared fairly with hand_score above.
        hand_score = (average_rank - 2) / (14 - 2) * 9

    pot = state["pot"]

    # The final score cares mostly about hand strength, and a little
    # bit about how big the pot is (bigger pot = higher stakes).
    final_score = hand_score * 10 + pot * 0.1
    return final_score


def is_terminal(state):
    """
    Check if the game is over and we should stop searching further.

    state: the current game situation
    returns: True if the hand is finished (someone folded, or we
             reached showdown), False otherwise
    """
    if state["phase"] == "folded":
        return True
    if state["phase"] == "showdown":
        return True
    return False


def apply_action(state, action):
    """
    Figure out what the game looks like after a player takes an
    action. This does NOT change the original state - it builds
    and returns a new one.

    state: the current game situation
    action: one of "fold", "check", "call", "raise"
    returns: a new state dictionary showing the result
    """
    # Make a fresh copy of the state so we don't accidentally
    # change the original one.
    new_state = dict(state)

    if action == "fold":
        new_state["phase"] = "folded"
        return new_state

    if action == "raise":
        new_state["pot"] = state["pot"] + RAISE_AMOUNT

    if action == "call":
        new_state["pot"] = state["pot"] + state["current_bet"]
        new_state["current_bet"] = 0

    # "check" does not change the pot at all.

    # Switch whose turn it is (AI turn becomes opponent turn, and
    # the other way around).
    if state["to_move"] == "max":
        new_state["to_move"] = "min"
    else:
        new_state["to_move"] = "max"

    return new_state


def get_chance_outcomes(state):
    """
    Look at a few possible next cards and build a list of the
    resulting game states, each with a probability attached.

    state: the current game situation, including the remaining
           "deck" (list of cards not yet seen)
    returns: a list of (probability, new_state) pairs
    """
    deck = state["deck"]

    if len(deck) == 0:
        # No cards left to reveal - nothing changes.
        return [(1.0, dict(state))]

    # Only look at the first few cards in the deck, to keep things
    # simple and fast for this beginner-friendly version.
    cards_to_check = []
    number_to_check = NUMBER_OF_CARDS_TO_CHECK
    if number_to_check > len(deck):
        number_to_check = len(deck)

    for i in range(number_to_check):
        cards_to_check.append(deck[i])

    probability_each = 1.0 / len(cards_to_check)

    outcomes = []
    for card in cards_to_check:
        new_state = dict(state)
        new_state["community_cards"] = state["community_cards"] + [card]

        # Remove the revealed card from the deck copy.
        new_deck = []
        for deck_card in deck:
            if deck_card is not card:
                new_deck.append(deck_card)
        new_state["deck"] = new_deck

        # Move on to the next phase of the game.
        if state["phase"] == "preflop":
            new_state["phase"] = "flop"
        elif state["phase"] == "flop":
            new_state["phase"] = "turn"
        elif state["phase"] == "turn":
            new_state["phase"] = "river"
        else:
            new_state["phase"] = "showdown"

        new_state["to_move"] = "max"
        outcomes.append((probability_each, new_state))

    return outcomes


def expectiminimax(state, depth):
    """
    The main AI decision function. Looks ahead a fixed number of
    moves (depth) and returns the best action to take right now.

    state: the current game situation
    depth: how many moves ahead to think (0 means stop and just
           estimate the current situation)
    returns: (best_action, expected_value)
             best_action is None at chance nodes and leaf nodes,
             since no single action applies there.
    """
    # Base case: stop searching and just estimate the situation.
    if depth <= 0 or is_terminal(state):
        score = evaluate_state(state)
        return None, score

    turn_type = state["to_move"]

    if turn_type == "chance":
        outcomes = get_chance_outcomes(state)
        total_value = 0
        for probability, next_state in outcomes:
            _, value = expectiminimax(next_state, depth - 1)
            total_value = total_value + probability * value
        return None, total_value

    actions = get_possible_actions(state)

    if turn_type == "max":
        # AI's turn: pick the action with the HIGHEST value.
        best_action = None
        best_value = float("-inf")

        for action in actions:
            next_state = apply_action(state, action)
            _, value = expectiminimax(next_state, depth - 1)
            if value > best_value:
                best_value = value
                best_action = action

        return best_action, best_value

    if turn_type == "min":
        # Opponent's turn: pick the action with the LOWEST value
        # (we assume the opponent plays to hurt us the most).
        best_action = None
        best_value = float("inf")

        for action in actions:
            next_state = apply_action(state, action)
            _, value = expectiminimax(next_state, depth - 1)
            if value < best_value:
                best_value = value
                best_action = action

        return best_action, best_value

    raise ValueError("Unknown turn type: " + str(turn_type))


# --- Example usage ---
if __name__ == "__main__":
    example_deck = []
    for rank in range(2, 15):
        example_deck.append({"rank": rank, "suit": "clubs"})
        example_deck.append({"rank": rank, "suit": "diamonds"})

    example_state = {
        "player_hand": [
            {"rank": 14, "suit": "hearts"},
            {"rank": 13, "suit": "hearts"},
        ],
        "community_cards": [],
        "deck": example_deck,
        "pot": 30,
        "current_bet": 20,
        "phase": "preflop",
        "to_move": "max",
    }

    best_action, expected_value = expectiminimax(example_state, depth=2)
    print("Best action:", best_action)
    print("Expected value:", expected_value)
