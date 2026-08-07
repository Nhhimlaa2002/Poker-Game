"""
support/helpers.py

Small shared utilities: saving/loading result rows to/from CSV, and
computing a win rate from a set of results. Used by strategy_comparison.py
and available to tests/benchmark.py in later weeks.
"""

import csv
import os


def save_results_to_csv(rows, path, fieldnames=None):
    """
    Write a list of dict rows to a CSV file, creating parent directories
    as needed. If fieldnames isn't given, uses the keys of the first row.
    """
    if not rows:
        raise ValueError("save_results_to_csv: rows is empty")

    fieldnames = fieldnames or list(rows[0].keys())
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_results_from_csv(path):
    """
    Read a CSV file back into a list of dicts. Returns [] if the file
    doesn't exist yet.
    """
    if not os.path.exists(path):
        return []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def calculate_win_rate(wins, total_games):
    """
    Simple win-rate percentage, guarding against divide-by-zero.
    """
    if total_games <= 0:
        return 0.0
    return round((wins / total_games) * 100, 2)