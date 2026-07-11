"""
config.py
=========
Shared configuration constants for the Poker AI project.

Every module (algorithm/, game_engine/, frontend/) should import
settings from here rather than hardcoding values, so gameplay and
AI behaviour can be tuned from a single location.
"""

# --- Chip / betting configuration ---------------------------------------
STARTING_CHIPS: int = 1000
SMALL_BLIND: int = 10
BIG_BLIND: int = 20

# --- AI configuration -----------------------------------------------------
AI_DEPTH: int = 2          # Expectiminimax search depth (plies)
NUM_PLAYERS: int = 2       # Week 1 baseline; extended to 3-4 in Week 4

# --- Deck configuration ----------------------------------------------------
SUITS = ("hearts", "diamonds", "clubs", "spades")
RANKS = tuple(range(2, 15))  # 2-14, where 14 = Ace
RANK_NAMES = {
    11: "Jack", 12: "Queen", 13: "King", 14: "Ace",
    **{r: str(r) for r in range(2, 11)},
}
