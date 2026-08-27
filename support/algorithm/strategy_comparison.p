"""
strategy_comparison.py

Week 4: runs games of pure Expectiminimax, pure Monte Carlo, and the
Combined strategy against each other, records wins/losses/decision
time to data/algorithm_comparison.csv, generates comparison charts,
and updates combined_strategy.DEFAULT_STRATEGY to whichever strategy
won the most.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
from game_engine.poker_game import GameState, Player
from algorithm.expectiminimax import make_decision as expectiminimax_decision
from algorithm.monte_carlo import monte_carlo_decision
from algorithm import combined_strategy
from support.helpers import save_results_to_csv

STRATEGIES = {
    "expectiminimax": lambda state, phase: expectiminimax_decision(state, depth=config.AI_DEPTH),
    "monte_carlo": lambda state, phase: monte_carlo_decision(state, num_simulations=config.MONTE_CARLO_SIMULATIONS),
    "combined": lambda state, phase: combined_strategy.decide(state, phase, depth=config.AI_DEPTH),
}


def _make_ai_decision_func(strategy_name):
    """Wraps a strategy function into the ai_decision_func signature GameState.play_round expects."""
    strategy_fn = STRATEGIES[strategy_name]

    def ai_decision_func(game_state, player):
        start = time.time()
        action = game_state.ai_make_decision(player, strategy=strategy_fn)
        elapsed = time.time() - start
        ai_decision_func.last_time = elapsed
        return action

    ai_decision_func.last_time = 0.0
    return ai_decision_func


def run_strategy_games(strategy_name, num_games=100):
    """
    Play `num_games` heads-up rounds of strategy_name (as Player 2/AI)
    against a baseline opponent (also driven by the same strategy, to
    isolate raw performance/timing rather than a strategy-vs-strategy
    matchup). Returns (wins, losses, avg_decision_time).
    """
    wins, losses = 0, 0
    total_time, decisions = 0.0, 0
    ai_decision_func = _make_ai_decision_func(strategy_name)

    for game_num in range(1, num_games + 1):
        p1 = Player("Baseline", config.STARTING_CHIPS, is_ai=True)
        p2 = Player(strategy_name, config.STARTING_CHIPS, is_ai=True)
        state = GameState([p1, p2])

        start = time.time()
        winner, pot = state.play_round(ai_decision_func=ai_decision_func, hand_number=game_num)
        total_time += time.time() - start
        decisions += 1

        if winner is p2:
            wins += 1
        else:
            losses += 1

    avg_decision_time = total_time / decisions if decisions else 0.0
    return wins, losses, avg_decision_time


def compare_all_strategies(num_games=None, csv_path="data/algorithm_comparison.csv"):
    """
    Runs all three strategies, saves results to CSV, generates charts,
    and updates combined_strategy.DEFAULT_STRATEGY to the best performer.
    """
    num_games = num_games or config.COMPARISON_GAMES_PER_STRATEGY
    rows = []
    for name in ("expectiminimax", "monte_carlo", "combined"):
        print(f"Running {num_games} games for strategy: {name}...")
        wins, losses, avg_time = run_strategy_games(name, num_games=num_games)
        rows.append({
            "strategy": name,
            "wins": wins,
            "losses": losses,
            "avg_decision_time": round(avg_time, 4),
        })
        print(f"  {name}: {wins}W / {losses}L, avg decision time {avg_time:.4f}s")

    save_results_to_csv(rows, csv_path, fieldnames=["strategy", "wins", "losses", "avg_decision_time"])
    _generate_charts(rows)

    best = max(rows, key=lambda r: r["wins"])
    combined_strategy.set_default_strategy(best["strategy"])
    print(f"Best strategy: {best['strategy']} — set as combined_strategy.DEFAULT_STRATEGY")

    return rows


def _generate_charts(rows, out_dir="data/charts"):
    os.makedirs(out_dir, exist_ok=True)
    names = [r["strategy"] for r in rows]
    wins = [r["wins"] for r in rows]
    times = [r["avg_decision_time"] for r in rows]

    plt.figure(figsize=(6, 4))
    plt.bar(names, wins, color=["#3d8bfd", "#2e8b57", "#c0392b"])
    plt.title("Win Rate by Strategy")
    plt.ylabel("Wins")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "strategy_comparison.png"))
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.bar(names, times, color=["#3d8bfd", "#2e8b57", "#c0392b"])
    plt.title("Average Decision Time by Strategy")
    plt.ylabel("Seconds")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "decision_time_comparison.png"))
    plt.close()


if __name__ == "__main__":
    compare_all_strategies()