# 🃏 Poker Game Simulator with Expectiminimax

This project implements an AI-based Poker Game Simulator that uses the **Expectiminimax algorithm** for strategic decision-making under uncertainty. The simulator models chance events such as card dealing and enables an AI player to evaluate possible game states and choose the optimal action.

The project demonstrates how adversarial search with chance nodes can be applied to imperfect-information games like Poker.

---

## 📌 Project Objectives

- Develop a Poker game simulator.
- Implement the Expectiminimax algorithm for AI decision-making.
- Model uncertainty caused by random card distribution.
- Simulate gameplay between AI and opponent(s).
- Evaluate the performance of the Expectiminimax algorithm under different game scenarios.

---

## 🧠 AI Algorithm

The project implements the following algorithm:

- Expectiminimax

The algorithm extends the traditional Minimax algorithm by introducing **chance nodes**, allowing the AI to make optimal decisions in environments where outcomes depend on probability, such as randomly dealt cards.

---

## ♠ Game Components

The simulator includes:

- Standard 52-card deck
- Card shuffling and dealing
- Poker hand evaluation
- AI player using Expectiminimax
- Opponent player(s)
- Turn-based gameplay
- Win/Loss determination

---

## 🛠 Technologies Used

- Python
- Jupyter Notebook
- NumPy
- Matplotlib


---

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

---

## 📊 Performance Evaluation

The simulator is evaluated based on:

- Decision quality
- Winning percentage
- Average utility value
- Execution time
- Algorithm performance under uncertainty

---

## 📈 Expected Output

The simulator plays Poker using the Expectiminimax algorithm by evaluating possible future game states and probabilistic outcomes. The AI selects actions that maximize its expected utility while accounting for opponent moves and chance events.

---