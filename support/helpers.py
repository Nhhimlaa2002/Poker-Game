import csv
import os


def save_results_to_csv(rows, path, fieldnames=None):
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
    if not os.path.exists(path):
        return []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def calculate_win_rate(wins, total_games):
    if total_games <= 0:
        return 0.0
    return round((wins / total_games) * 100, 2)
