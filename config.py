# Shared configuration for Poker AI Simulator

STARTING_CHIPS = 1000
SMALL_BLIND = 10
BIG_BLIND = 20
AI_DEPTH = 4
DIFFICULTY_PRESETS = {
    "easy":   {"depth": 1, "samples": 5},
    "medium": {"depth": 2, "samples": 10},
    "hard":   {"depth": 4, "samples": 10},
}
DEFAULT_DIFFICULTY = "medium"
NUM_PLAYERS = 2

BLIND_INCREASE_EVERY_N_ROUNDS = 5
BLIND_INCREASE_FACTOR = 1.5

MONTE_CARLO_SIMULATIONS = 200

COMPARISON_GAMES_PER_STRATEGY = 100
