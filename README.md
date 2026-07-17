# Poker Game Simulator with Expectiminimax

A Texas Hold'em poker simulator where an AI opponent uses the Expectiminimax algorithm
(with Monte Carlo simulation) to make strategic betting decisions.

## Team

| Role | Member | Owns |
|------|--------|------|
| M1 | AI Algorithm Engineer | `algorithm/` |
| M2 | Game Engine Developer | `game_engine/` |
| M3 | Frontend Developer | `frontend/` |
| M4 | Integration & Testing | `tests/`, repo mgmt, report |

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

## How to Run Tests

```bash
python -m pytest tests/ -v
```

## Project Status (End of Week 2)

- Repo structure and shared config in place.
- Card/Deck classes and hand evaluator implemented.
- Basic game loop (`play_round`) with betting, flop/turn/river, and showdown works.
- Basic hand evaluation function (0-9 score) implemented.
- Integration test confirms a full AI-vs-AI round runs end-to-end and returns a winner.
- 6 unit tests + 1 integration test in `tests/`, all passing (7/7).
- `support/helpers.py` provides CSV save/load and win-rate utilities.
- 10 initial AI-vs-AI games logged to `data/initial_test_results.csv`.
- GUI, full Expectiminimax search, and Monte Carlo simulation are scheduled for later weeks.

## Known Issues

See `others/known_issues.md`.

## Repository Structure

See `others/final_report.pdf` (in later weeks) for full architecture details. Top-level layout:

```
poker-ai-project/
|-- main.py
|-- README.md
|-- requirements.txt
|-- config.py
|-- algorithm/      # M1 owns this folder
|-- game_engine/     # M2 owns this folder
|-- frontend/         # M3 owns this folder
|-- tests/             # M4 owns this folder
|-- data/
|-- support/
+-- others/
```
