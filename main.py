"""Entry point for the Poker AI Simulator."""

import sys


def main():
    print("Poker AI Simulator")
    print("Launching game...")
    try:
        # GUI is owned by M3 (frontend/game_ui.py) - not yet available in Week 1-2.
        from frontend.game_ui import GameApp  # noqa: F401
        app = GameApp()
        app.run()
    except ModuleNotFoundError:
        print("Frontend GUI not yet available (scheduled for later weeks).")
        print("Running a headless AI-vs-AI demo round instead...\n")
        from game_engine.poker_game import GameState, Player, play_round

        players = [Player("Player_1", 1000), Player("AI_Opponent", 1000)]
        state = GameState(players)
        winner, pot = play_round(state)
        print(f"Winner: {winner.name} | Pot: ${pot}")
    except Exception as e:
        print(f"Error launching game: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
