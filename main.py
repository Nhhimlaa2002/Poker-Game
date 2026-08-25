"""Entry point for the Poker AI Simulator."""

import sys


def main():
    print("Poker AI Simulator")
    print("Launching game...")
    try:
        from frontend.game_ui import launch
    except ModuleNotFoundError as e:
        if e.name == "tkinter":
            print("tkinter is not installed, running a headless AI-vs-AI demo round instead...")
            print("(Install it with: sudo apt install python3-tk)\n")
            from game_engine.poker_game import GameState, Player

            players = [Player("Player_1", 1000, is_ai=True), Player("AI_Opponent", 1000, is_ai=True)]
            state = GameState(players)
            winner, pot = state.play_round(hand_number=1)
            print(f"Winner: {winner.name} | Pot: ${pot}")
            return
        # Some other module failed to import (e.g. matplotlib, numpy, a typo'd
        # import) - don't hide it behind the "no GUI" message, surface it.
        print(f"Error loading frontend: {e}")
        sys.exit(1)

    try:
        launch()
    except Exception as e:
        print(f"Error launching game: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()