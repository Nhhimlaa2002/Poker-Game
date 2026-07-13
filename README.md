# 🃏 Poker Game Simulator with Expectiminimax

This project implements an AI-based Poker Game Simulator that uses the **Expectiminimax algorithm** for strategic decision-making under uncertainty. The simulator models chance events such as card dealing and enables an AI player to evaluate possible game states and choose the optimal action.

The project demonstrates how adversarial search with chance nodes can be applied to imperfect-information games like Poker.


## 📌 Project Objectives

1.Develop a Poker game simulator.
2.Implement the Expectiminimax algorithm for AI decision-making.
3.Model uncertainty caused by random card distribution.
4.Simulate gameplay between AI and opponent(s).
5.Evaluate the performance of the Expectiminimax algorithm under different game scenarios.



## 🧠 AI Algorithm

The project implements the following algorithm:

 "Expectiminimax"

The algorithm extends the traditional Minimax algorithm by introducing **chance nodes**, allowing the AI to make optimal decisions in environments where outcomes depend on probability, such as randomly dealt cards.


## ♠ Game Components

The simulator includes:

1.Standard 52-card deck
2.Card shuffling and dealing
3.Poker hand evaluation
4.AI player using Expectiminimax
5.Opponent player(s)
6.Turn-based gameplay
7.Win/Loss determination


## 🛠 Technologies Used

- Python
- Jupyter Notebook
- NumPy
- Matplotlib



## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/Nhhimlaa2002/Poker-Game.git
```

### Navigate to the Project

```bash
cd Poker-Game
```

### Install Required Libraries

```bash
pip install -r requirements.txt
```

or install manually

```bash
pip install numpy matplotlib jupyter
```

### Run the Project

Launch Jupyter Notebook:

```bash
jupyter notebook
```

Open the project notebook and run all cells.

Nadira Halim Himla- 2221920642

## Week 1 Progress

- Created the `algorithm/` folder structure for the AI module.
- Added `evaluation.py` with a hand-strength scoring function (0-9 scale).
- Added `actions.py` listing legal player actions (fold, check, call, raise).
- Added the first version of `expectiminimax.py`, implementing the core algorithm with MAX, MIN, and CHANCE node types.
- Confirmed royal flush scores 9 and a pair scores 1 using `evaluate_hand()`.
- Confirmed the AI returns a valid action (fold/check/call/raise) without crashing.

## Week 2 Progress

- Added `game_tree.py` to build the full decision tree before searching, instead of generating moves during search.
- Implemented full-deck chance node handling in `get_chance_outcomes()`, so every possible next card is considered with an equal, correct probability (previously only a small sample was checked).
- Added `order_actions()` to `actions.py` for move ordering, so promising actions are explored first.
- Added timing and logging: every AI decision is now recorded to `data/decision_log.txt` with the action taken, expected value, and time spent.
- Found and fixed a bug where CHANCE nodes were never actually being reached during search, due to `to_move` never switching to `"chance"`. Added an `actions_this_phase` counter to correctly trigger chance nodes once both players have acted.
- Verified all changes using `check_my_code.py`, confirming hand evaluation, action ordering, and AI decision-making all work correctly.

## 📊 Performance Evaluation

The simulator is evaluated based on:

1.Decision quality
2.Winning percentage
3.Average utility value
4.Execution time
5.Algorithm performance under uncertainty


## 📈 Expected Output

The simulator plays Poker using the Expectiminimax algorithm by evaluating possible future game states and probabilistic outcomes. The AI selects actions that maximize its expected utility while accounting for opponent moves and chance events.
