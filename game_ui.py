"""
frontend/game_ui.py
====================
Tkinter GUI for the Poker AI Simulator.

Covers the Week 1 + Week 2 scope:
  Week 1 - static layout: opponent area, community cards, action bar,
           chip/pot panel, game log, and a CardWidget that can flip
           between face-up and face-down.
  Week 2 - GameApp wraps the UI around a real GameState and wires
           Fold / Call / Raise to the actual game engine, with the AI
           opponent making real decisions via algorithm.expectiminimax.

Run standalone for a quick visual check:
    python frontend/game_ui.py

Or via the project entry point:
    python main.py
"""

import os
import sys

# Allow `python frontend/game_ui.py` to find the other packages even
# though only frontend/ itself would normally be on sys.path in that case.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk

import config
from game_engine.card import RANK_NAMES
from game_engine.poker_game import Player, GameState
from algorithm.expectiminimax import make_decision


# --- Look & feel -----------------------------------------------------------
WINDOW_W, WINDOW_H = 900, 600
CARD_W, CARD_H = 70, 100

BG = "#0b3d24"          # felt green
PANEL_BG = "#123524"
LOG_BG = "#0e1f16"
TEXT_LIGHT = "#f5f5f5"
TEXT_MUTED = "#9fd6b5"

SUIT_SYMBOLS = {"hearts": "\u2665", "diamonds": "\u2666", "clubs": "\u2663", "spades": "\u2660"}
RED_SUITS = {"hearts", "diamonds"}


def rank_display(rank):
    """2-10 show as their number; 11-14 show as J/Q/K/A (see card.RANK_NAMES)."""
    return RANK_NAMES.get(rank, str(rank))


# --- Card widget -------------------------------------------------------------
class CardWidget(tk.Canvas):
    """
    A single playing card drawn on a Canvas.

    Usage:
        widget.set_card((rank, suit), face_up=True)   # show a card
        widget.show_face_up(False)                    # flip it face-down
        widget.clear()                                 # empty placeholder
    """

    def __init__(self, parent, width=CARD_W, height=CARD_H, **kwargs):
        super().__init__(parent, width=width, height=height,
                          highlightthickness=0, bg=parent["bg"], **kwargs)
        self.card_width = width
        self.card_height = height
        self.card = None       # (rank, suit) tuple, or None for an empty slot
        self.face_up = True
        self._draw_empty()

    def set_card(self, card, face_up=True):
        self.card = card
        self.face_up = face_up
        self._redraw()

    def show_face_up(self, face_up):
        self.face_up = face_up
        self._redraw()

    def clear(self):
        self.card = None
        self._redraw()

    def _redraw(self):
        self.delete("all")
        if self.card is None:
            self._draw_empty()
        elif self.face_up:
            self._draw_face_up()
        else:
            self._draw_face_down()

    def _draw_empty(self):
        self.create_rectangle(2, 2, self.card_width - 2, self.card_height - 2,
                               outline="#2f6b4f", width=2, dash=(3, 2))

    def _draw_face_down(self):
        self.create_rectangle(2, 2, self.card_width - 2, self.card_height - 2,
                               fill="#1f4fa3", outline="#0d2c63", width=2)
        self.create_text(self.card_width / 2, self.card_height / 2,
                          text="?", fill="white", font=("Georgia", 22, "bold"))

    def _draw_face_up(self):
        rank, suit = self.card
        color = "#c0392b" if suit in RED_SUITS else "#1b1b1b"
        symbol = SUIT_SYMBOLS.get(suit, "?")
        label = rank_display(rank)

        self.create_rectangle(2, 2, self.card_width - 2, self.card_height - 2,
                               fill="white", outline="#333333", width=2)
        self.create_text(10, 12, text=label, fill=color, anchor="nw",
                          font=("Georgia", 11, "bold"))
        self.create_text(10, 26, text=symbol, fill=color, anchor="nw",
                          font=("Georgia", 11, "bold"))
        self.create_text(self.card_width / 2, self.card_height / 2, text=symbol,
                          fill=color, font=("Georgia", 26, "bold"))
        self.create_text(self.card_width - 10, self.card_height - 12, text=label,
                          fill=color, anchor="se", font=("Georgia", 11, "bold"))
        self.create_text(self.card_width - 10, self.card_height - 26, text=symbol,
                          fill=color, anchor="se", font=("Georgia", 11, "bold"))


# --- Main application --------------------------------------------------------
class GameApp:
    """Wraps the Tkinter UI around a live GameState and drives full hands."""

    def __init__(self, root):
        self.root = root
        self.root.title("Poker AI Simulator - Expectiminimax")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.human = Player("You", chips=config.STARTING_CHIPS, is_ai=False)
        self.ai = Player("AI Opponent", chips=config.STARTING_CHIPS, is_ai=True)
        self.human.raise_increment = 20
        self.game_state = GameState([self.human, self.ai])

        self.action_var = tk.StringVar(value="")
        self.hand_number = 0
        self.round_in_progress = False

        self._build_layout()
        self._log("Welcome to the Poker AI Simulator.")
        self._log("Click 'New Game' to deal the first hand.")

    # ------------------------------------------------------------------ UI --
    def _build_layout(self):
        # Opponent area
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", pady=(10, 0))
        tk.Label(top, text="AI Opponent", bg=BG, fg=TEXT_LIGHT,
                  font=("Georgia", 12, "bold")).pack()
        opp_frame = tk.Frame(top, bg=BG)
        opp_frame.pack(pady=4)
        self.opponent_cards = [CardWidget(opp_frame) for _ in range(2)]
        for widget in self.opponent_cards:
            widget.pack(side="left", padx=4)

        # Community cards
        mid = tk.Frame(self.root, bg=BG)
        mid.pack(pady=12)
        self.community_widgets = [CardWidget(mid) for _ in range(5)]
        for widget in self.community_widgets:
            widget.pack(side="left", padx=4)

        # Result banner
        self.result_label = tk.Label(self.root, text="", bg=BG, fg="#ffd43b",
                                       font=("Georgia", 15, "bold"))
        self.result_label.pack(pady=2)

        # Player area
        bottom_top = tk.Frame(self.root, bg=BG)
        bottom_top.pack(pady=(6, 0))
        tk.Label(bottom_top, text="You", bg=BG, fg=TEXT_LIGHT,
                  font=("Georgia", 12, "bold")).pack()
        player_frame = tk.Frame(bottom_top, bg=BG)
        player_frame.pack(pady=4)
        self.player_cards = [CardWidget(player_frame) for _ in range(2)]
        for widget in self.player_cards:
            widget.pack(side="left", padx=4)

        # Side panel: pot / chip counts
        side = tk.Frame(self.root, bg=PANEL_BG, bd=1, relief="ridge")
        side.place(x=680, y=16, width=204, height=132)
        tk.Label(side, text="TABLE", bg=PANEL_BG, fg=TEXT_MUTED,
                  font=("Georgia", 10, "bold")).pack(pady=(8, 4))
        self.pot_label = tk.Label(side, text="Pot: $0", bg=PANEL_BG, fg=TEXT_LIGHT,
                                    font=("Georgia", 11))
        self.pot_label.pack(pady=2)
        self.your_chips_label = tk.Label(side, bg=PANEL_BG, fg=TEXT_LIGHT, font=("Georgia", 10))
        self.your_chips_label.pack(pady=2)
        self.opp_chips_label = tk.Label(side, bg=PANEL_BG, fg=TEXT_LIGHT, font=("Georgia", 10))
        self.opp_chips_label.pack(pady=2)

        # Action bar
        actions = tk.Frame(self.root, bg=BG)
        actions.pack(pady=10)

        self.new_game_btn = tk.Button(actions, text="New Game", bg="#3d8bfd", fg="white",
                                        font=("Georgia", 11, "bold"), width=10,
                                        command=self.on_new_game_click)
        self.new_game_btn.grid(row=0, column=0, padx=6)

        self.fold_btn = tk.Button(actions, text="Fold", bg="#c0392b", fg="white",
                                    font=("Georgia", 11, "bold"), width=10, state="disabled",
                                    command=lambda: self._submit_action("fold"))
        self.fold_btn.grid(row=0, column=1, padx=6)

        self.call_btn = tk.Button(actions, text="Call", bg="#2f6fed", fg="white",
                                    font=("Georgia", 11, "bold"), width=10, state="disabled",
                                    command=lambda: self._submit_action("call"))
        self.call_btn.grid(row=0, column=2, padx=6)

        self.raise_btn = tk.Button(actions, text="Raise", bg="#2e8b57", fg="white",
                                     font=("Georgia", 11, "bold"), width=10, state="disabled",
                                     command=self._on_raise_click)
        self.raise_btn.grid(row=0, column=3, padx=6)

        tk.Label(actions, text="Raise by $", bg=BG, fg=TEXT_LIGHT).grid(row=0, column=4, padx=(12, 2))
        self.raise_entry = tk.Entry(actions, width=6)
        self.raise_entry.insert(0, "20")
        self.raise_entry.grid(row=0, column=5)

        # Game log
        log_frame = tk.Frame(self.root, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(6, 10))
        self.log_text = tk.Text(log_frame, height=8, bg=LOG_BG, fg="#d7f5e3",
                                  font=("Consolas", 9), state="disabled", wrap="word")
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._refresh_chip_labels()

    # --------------------------------------------------------------- log ---
    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ----------------------------------------------------------- display ---
    def _refresh_chip_labels(self):
        self.pot_label.config(text=f"Pot: ${self.game_state.pot}")
        self.your_chips_label.config(text=f"Your Chips: ${self.human.chips}")
        self.opp_chips_label.config(text=f"Opponent Chips: ${self.ai.chips}")

    def update_display(self):
        """Redraw every card widget and label from the current game state."""
        for i, widget in enumerate(self.player_cards):
            if i < len(self.human.hand):
                c = self.human.hand[i]
                widget.set_card((c.rank, c.suit), face_up=True)
            else:
                widget.clear()

        # Opponent stays face-down while a hand is in progress; reveal at
        # showdown (unless they folded, in which case there's nothing to see).
        reveal_opponent = (not self.round_in_progress) and (not self.ai.is_folded)
        for i, widget in enumerate(self.opponent_cards):
            if i < len(self.ai.hand):
                c = self.ai.hand[i]
                widget.set_card((c.rank, c.suit), face_up=reveal_opponent)
            else:
                widget.clear()

        for i, widget in enumerate(self.community_widgets):
            if i < len(self.game_state.community_cards):
                c = self.game_state.community_cards[i]
                widget.set_card((c.rank, c.suit), face_up=True)
            else:
                widget.clear()

        self._refresh_chip_labels()
        self.root.update_idletasks()

    # -------------------------------------------------------------- input --
    def _set_action_buttons_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.fold_btn.config(state=state)
        self.call_btn.config(state=state)
        self.raise_btn.config(state=state)

    def _submit_action(self, action):
        self.action_var.set(action)

    def _on_raise_click(self):
        try:
            amount = int(self.raise_entry.get())
            if amount <= 0:
                amount = 20
        except ValueError:
            amount = 20
        self.human.raise_increment = amount
        self._submit_action("raise")

    # ------------------------------------------------- engine callbacks ----
    def human_action_func(self, game_state, player):
        """Called by GameState.play_round() whenever it's the human's turn."""
        self.update_display()

        table_bet = max(p.current_bet for p in game_state.players)
        to_call = max(0, table_bet - player.current_bet)
        self.call_btn.config(text=f"Call ${to_call}" if to_call else "Check")

        if to_call:
            self._log(f"Your turn ({game_state.phase}). You owe ${to_call} to stay in.")
        else:
            self._log(f"Your turn ({game_state.phase}). Nothing owed - check or raise.")

        self._set_action_buttons_enabled(True)
        self.action_var.set("")
        self.root.wait_variable(self.action_var)   # blocks here, but the GUI stays responsive
        self._set_action_buttons_enabled(False)

        action = self.action_var.get() or "call"
        self._log(f"You chose to {action}.")
        return action

    def ai_decision_func(self, game_state, player):
        """Called by GameState.play_round() whenever it's the AI's turn."""
        self.update_display()
        self._log("AI is thinking...")
        self.root.update_idletasks()

        state = self._build_algorithm_state(game_state, player)
        try:
            action = make_decision(state, depth=config.AI_DEPTH, hand_number=self.hand_number)
        except Exception as exc:  # pragma: no cover - defensive, keeps the game playable
            self._log(f"[AI error, defaulting to call: {exc}]")
            action = "call"

        if action not in ("fold", "call", "check", "raise"):
            action = "call"
        if action == "check":
            action = "call"

        self._log(f"AI chooses to {action}.")
        return action

    def _build_algorithm_state(self, game_state, player):
        """
        Adapter: converts the real GameState/Player/Card objects into the
        plain-dict state shape that algorithm.expectiminimax expects
        (player_hand / community_cards / deck as lists of {'rank','suit'}
        dicts, plus pot / current_bet / phase / to_move / actions_this_phase).
        """
        table_bet = max(p.current_bet for p in game_state.players)
        return {
            "player_hand": [{"rank": c.rank, "suit": c.suit} for c in player.hand],
            "community_cards": [{"rank": c.rank, "suit": c.suit} for c in game_state.community_cards],
            "deck": [{"rank": c.rank, "suit": c.suit} for c in game_state.deck.cards],
            "pot": game_state.pot,
            "current_bet": max(0, table_bet - player.current_bet),
            "phase": game_state.phase,
            "to_move": "max",
            "actions_this_phase": 0,
        }

    # --------------------------------------------------------- round flow --
    def on_new_game_click(self):
        if self.round_in_progress:
            return

        self.new_game_btn.config(state="disabled")
        self.result_label.config(text="")
        self.hand_number += 1
        self.round_in_progress = True
        self._log(f"\n===== Hand #{self.hand_number} =====")
        self.update_display()

        winner, pot_amount = self.game_state.play_round(
            ai_decision_func=self.ai_decision_func,
            human_action_func=self.human_action_func,
            hand_number=self.hand_number,
        )

        self.round_in_progress = False
        self.update_display()
        self.display_result(winner, pot_amount)

    def display_result(self, winner, pot_amount):
        you_won = winner is self.human
        text = f"{'You win' if you_won else winner.name + ' wins'} ${pot_amount}!"
        self.result_label.config(text=text)
        self._log(text)

        if self.human.chips <= 0 or self.ai.chips <= 0:
            self._log("Match over - one player is out of chips.")
            self.new_game_btn.config(state="normal", text="Restart Match", command=self.reset_match)
            return

        self.new_game_btn.config(state="normal")
        self.root.after(3000, self._auto_next_round)

    def _auto_next_round(self):
        if not self.round_in_progress:
            self.on_new_game_click()

    def reset_match(self):
        self.human.chips = config.STARTING_CHIPS
        self.ai.chips = config.STARTING_CHIPS
        self.hand_number = 0
        self.new_game_btn.config(text="New Game", command=self.on_new_game_click)
        self._log("\n--- New match started ---")
        self.on_new_game_click()


def launch():
    """Entry point used by main.py."""
    root = tk.Tk()
    GameApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
