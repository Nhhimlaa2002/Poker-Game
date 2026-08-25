def get_possible_actions(state, player=None):
    """
    Returns only legally valid actions based on current game state and player stack.
    Supports both a dictionary state (Expectiminimax search tree) and a GameState instance.
    """
    if isinstance(state, dict):
        current_bet = state.get("current_bet", 0)
        chips = state.get("player_chips", None)
    elif hasattr(state, "players") and player is not None:
        table_bet = max((p.current_bet for p in state.players), default=0)
        current_bet = max(0, table_bet - player.current_bet)
        chips = player.chips
    else:
        current_bet = getattr(state, "current_bet", 0)
        chips = getattr(state, "player_chips", None)

    actions = ["fold"]

    # Check vs Call Logic
    if current_bet <= 0:
        actions.append("check")
    else:
        if chips is None or chips > 0:
            actions.append("call")

    # Raise Logic
    if chips is None or chips > current_bet:
        actions.append("raise")

    return actions


def order_actions(actions):
    """
    Orders actions in preferred evaluation priority for Expectiminimax tree traversal.
    """
    preferred_order = ["raise", "call", "check", "fold"]
    return [action for action in preferred_order if action in actions]