import random
import statistics
import csv

from game_engine.poker_game import GameState, Player


NUM_HANDS = 100
STARTING_CHIPS = 1000


def random_baseline(state, player):
    """Choose a random legal action."""
    legal_actions = state.legal_actions_for(player)

    if not legal_actions:
        return "call"

    return random.choice(legal_actions)


def rule_based_baseline(state, player):
    """
    Simple rule-based opponent.

    - Raise when there is no bet to call and the player has
      enough chips.
    - Call when facing a bet.
    - Fold occasionally when the call is expensive.
    """

    legal_actions = state.legal_actions_for(player)

    if not legal_actions:
        return "call"

    table_bet = max(p.current_bet for p in state.players)
    to_call = max(0, table_bet - player.current_bet)

    # If there is no bet to call, sometimes raise.
    if to_call == 0 and "raise" in legal_actions:
        if random.random() < 0.5:
            return "raise"

    # If the call is expensive, sometimes fold.
    if to_call > 100 and "fold" in legal_actions:
        if random.random() < 0.5:
            return "fold"

    if "call" in legal_actions:
        return "call"

    return legal_actions[0]


def run_match(baseline_name, baseline_function, num_hands=NUM_HANDS):
    """
    Run AI against one baseline for a number of independent hands.
    """

    ai_wins = 0
    baseline_wins = 0
    ties = 0
    pots = []

    for hand_number in range(1, num_hands + 1):

        # Create fresh players for every hand so that one player
        # does not go bankrupt during a long experiment.
        ai_player = Player(
            "AI",
            STARTING_CHIPS,
            is_ai=True
        )

        baseline_player = Player(
            baseline_name,
            STARTING_CHIPS,
            is_ai=True
        )

        players = [ai_player, baseline_player]

        state = GameState(players)

        def decision_function(game_state, player):
            # AI uses the actual Expectiminimax decision.
            if player is ai_player:
                return game_state.ai_make_decision(
                    player,
                    hand_number=hand_number
                )

            # Opponent uses the selected baseline strategy.
            return baseline_function(
                game_state,
                player
            )

        winner, pot = state.play_round(
            ai_decision_func=decision_function,
            hand_number=hand_number
        )

        pots.append(pot)

        if winner is ai_player:
            ai_wins += 1

        elif winner is baseline_player:
            baseline_wins += 1

        else:
            ties += 1

        if hand_number % 10 == 0:
            print(
                f"{baseline_name}: "
                f"completed {hand_number}/{num_hands} hands"
            )

    ai_win_rate = ai_wins / num_hands

    average_pot = statistics.mean(pots) if pots else 0

    return {
        "opponent": baseline_name,
        "hands": num_hands,
        "ai_wins": ai_wins,
        "opponent_wins": baseline_wins,
        "ties": ties,
        "ai_win_rate": ai_win_rate,
        "average_pot": average_pot,
    }


def print_results(results):
    print("\n" + "=" * 80)
    print("WEEK 3 M2 EXPERIMENT RESULTS")
    print("=" * 80)

    print(
        f"{'Opponent':<20}"
        f"{'Hands':<10}"
        f"{'AI Wins':<10}"
        f"{'Opp Wins':<10}"
        f"{'Ties':<10}"
        f"{'AI Win %':<12}"
        f"{'Avg Pot':<10}"
    )

    print("-" * 80)

    for result in results:
        print(
            f"{result['opponent']:<20}"
            f"{result['hands']:<10}"
            f"{result['ai_wins']:<10}"
            f"{result['opponent_wins']:<10}"
            f"{result['ties']:<10}"
            f"{result['ai_win_rate'] * 100:<12.2f}"
            f"${result['average_pot']:<10.2f}"
        )

    print("=" * 80)


def main():
    print("Starting Week 3 M2 experiments...")
    print(f"Each experiment will run {NUM_HANDS} hands.\n")

    results = []

    print("Experiment 1: AI vs Random Baseline")
    print("-" * 50)

    random_result = run_match(
        "Random",
        random_baseline
    )

    results.append(random_result)

    print("\nExperiment 2: AI vs Rule-Based Baseline")
    print("-" * 50)

    rule_result = run_match(
        "RuleBased",
        rule_based_baseline
    )

    results.append(rule_result)

    print_results(results)


if __name__ == "__main__":
    main()