# 🃏 Poker Game Simulator with Expectiminimax
**Course:** CSE 440 — Artificial Intelligence  
**Group:** 07 | **Section:** 01  
**Institution:** North South University  
**Semester:** Summer 2026

---

# 👥 Group Members
| Name | Student ID |
|------|------------|
| Nadira Halim Himla | 2221920642 |
| Sajiah Islam Chowdhury | 2212447642 |
| S. Anam Ridwan Shanto | 2022563042 |
| Mohammad Robiul Islam Hasib | 1911677642 |
| Isnat Hossain Rijon | 2211203042 |

---

# 📌 Project Overview
This project aims to develop a Poker Game Simulator that applies the **Expectiminimax algorithm** for intelligent decision-making in an environment involving uncertainty and chance events.

Unlike traditional Minimax, Expectiminimax considers probabilistic outcomes, making it suitable for games like Poker where card distributions introduce randomness. The project focuses on designing the game environment, implementing AI-based strategic gameplay, and evaluating the algorithm's overall performance.

---

# 🎯 Project Objective
Develop a Poker Game Simulator using the **Expectiminimax algorithm** for strategic decision-making under uncertainty by designing the game environment, implementing the required components, and evaluating the algorithm's performance across different game scenarios.

---

# ✨ Project Features

### 🎲 Game Environment
- Simulates a simplified Poker game between a human player and an AI opponent.
- Manages deck creation, shuffling, card dealing, betting rounds, and game flow.

### 🧠 Expectiminimax-Based AI
- Uses the **Expectiminimax algorithm** for optimal decision-making.
- Evaluates possible player actions while considering chance nodes caused by random card draws.
- Selects actions that maximize the AI's expected utility.

### 🃏 Poker Mechanics
- Standard deck of playing cards.
- Hand generation and comparison.
- Basic betting decisions (Check, Call, Raise, Fold).

### 📊 Hand Evaluation
- Detects Poker hand rankings such as:
  - High Card
  - One Pair
  - Two Pair
  - Three of a Kind
  - Straight
  - Flush
  - Full House
  - Four of a Kind
  - Straight Flush
  - Royal Flush

### 🧠 Additional AI & Gameplay Features
- Difficulty Levels (Easy/Medium/Hard)
- Adaptive Opponent Modeling
- Live Decision-Log Panel
- Win-Rate / Stats Tracker
- Hand History Export

### 📈 Performance Evaluation
- Measures AI decision quality.
- Compares outcomes across different gameplay scenarios.
- Analyzes the effectiveness of Expectiminimax under uncertainty.

---

# 🛠 Technologies & Tools
- Python 3.x
- Tkinter (GUI)
- Object-Oriented Programming (OOP)
- Git & GitHub

---

# 📅 Weekly Progress
| Week | Task |
|------|------|
| Week 1 | Repository setup, project planning, README preparation, requirement analysis, and initial game engine module (deck, card handling, hand evaluation logic). |
| Week 2 | Poker game environment, initial Expectiminimax implementation, hand evaluation, game tree development, player actions, GUI integration. |
| Week 3–5 | Continued algorithm and frontend development, initial integration and identification of outstanding issues (engine stability, AI performance, duplicate hand evaluators, illegal-action handling). |
| Week 6  | Stabilization sprint — fixing engine crash, optimizing AI decision speed, consolidating duplicate hand evaluators, fixing illegal-action bug, verifying full gameplay via GUI. |
| Week 7 | Feature development — difficulty levels (Easy/Medium/Hard), adaptive opponent modeling, live decision-log panel, win-rate/stats tracker. |
| Week 8 | Final integration, visual polish, performance experiments, report writing, demo video, and submission. |

---

# 🚀 Getting Started

### Clone the Repository
```bash
git clone https://github.com/Nhhimlaa2002/Poker-Game.git
```

### Navigate to the Project Directory
```bash
cd Poker-Game
```

### Install Required Libraries
```bash
pip install -r requirements.txt
```
> Note: Tkinter comes pre-installed with standard Python distributions and does not need to be installed separately via pip.

### Run the Project
```bash
python main.py
```

---

# 📈 Expected Outcome
The project will simulate intelligent Poker gameplay where the AI makes strategic decisions using the **Expectiminimax algorithm**. Performance will be evaluated by analyzing the quality of decisions made under uncertainty and comparing outcomes across multiple game scenarios.

---

# 📚 References
- Stuart Russell & Peter Norvig — *Artificial Intelligence: A Modern Approach*
- Expectiminimax Algorithm
- Poker Game Theory
- Python Documentation

---

# 📝 License
This project is developed for academic purposes as part of **CSE 440 — Artificial Intelligence** at **North South University**.