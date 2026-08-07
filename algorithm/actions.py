def get_possible_actions(state):
    current_bet = state.get("current_bet", 0)
    chips = state.get("player_chips", None)

    actions = ["fold"]
    if current_bet <= 0:
        actions.append("check")
    else:
        actions.append("call")

    if chips is None or chips > current_bet:
        actions.append("raise")

    return actions


def order_actions(actions):
    preferred_order = ["raise", "call", "check", "fold"]
    ordered_actions = []
    for action_name in preferred_order:
        if action_name in actions:
            ordered_actions.append(action_name)
    return ordered_actions
