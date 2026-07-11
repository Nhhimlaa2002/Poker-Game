"""
main.py
========
Entry point for the Poker AI Simulator. Run with:

    python main.py
"""

from frontend.game_ui import launch


def main() -> None:
    """Print a startup banner and launch the GUI (or its placeholder)."""
    print("Poker AI Simulator")
    try:
        launch()
    except Exception as exc:  # pragma: no cover - defensive, user-facing
        print(f"[main] Could not launch GUI: {exc}")


if __name__ == "__main__":
    main()
