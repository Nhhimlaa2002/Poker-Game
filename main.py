"""Entry point for the Poker AI Simulator."""

import sys


def main():
    print("Poker AI Simulator")
    print("Launching game...")
    try:
        from frontend.game_ui import launch
        launch()
    except ModuleNotFoundError:
        print("Frontend GUI not available, running a headless AI-vs-AI demo round instead...\n")
        from game_engine.poker_game import GameState, Player

        players = [Player("Player_1", 1000, is_ai=True), Player("AI_Opponent", 1000, is_ai=True)]
        state = GameState(players)
        winner, pot = state.play_round(hand_number=1)
        print(f"Winner: {winner.name} | Pot: ${pot}")
    except Exception as e:
        print(f"Error launching game: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
