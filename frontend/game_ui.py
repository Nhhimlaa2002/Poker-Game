"""
frontend/game_ui.py
====================
Tkinter GUI for the Poker AI Simulator.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config
from game_engine.card import RANK_NAMES
from game_engine.poker_game import Player, GameState, GameHistory
from game_engine.tournament import Tournament
from algorithm import combined_strategy

WINDOW_W, WINDOW_H = 1000, 680
CARD_W, CARD_H = 60, 86

BG = "#0b3d24"
PANEL_BG = "#123524"
LOG_BG = "#0e1f16"
TEXT_LIGHT = "#f5f5f5"
TEXT_MUTED = "#9fd6b5"

SUIT_SYMBOLS = {"hearts": "\u2665", "diamonds": "\u2666", "clubs": "\u2663", "spades": "\u2660"}
RED_SUITS = {"hearts", "diamonds"}

WIN_STARS_SIMULATIONS = 250


def rank_display(rank):
    return RANK_NAMES.get(rank, str(rank))


class CardWidget(tk.Canvas):
    def __init__(self, parent, width=CARD_W, height=CARD_H, **kwargs):
        super().__init__(parent, width=width, height=height,
                          highlightthickness=0, bg=parent["bg"], **kwargs)
        self.card_width = width
        self.card_height = height
        self.card = None
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
                          text="?", fill="white", font=("Georgia", 18, "bold"))

    def _draw_face_up(self):
        rank, suit = self.card
        color = "#c0392b" if suit in RED_SUITS else "#1b1b1b"
        symbol = SUIT_SYMBOLS.get(suit, "?")
        label = rank_display(rank)

        self.create_rectangle(2, 2, self.card_width - 2, self.card_height - 2,
                               fill="white", outline="#333333", width=2)
        self.create_text(8, 10, text=label, fill=color, anchor="nw", font=("Georgia", 10, "bold"))
        self.create_text(8, 23, text=symbol, fill=color, anchor="nw", font=("Georgia", 10, "bold"))
        self.create_text(self.card_width / 2, self.card_height / 2, text=symbol,
                          fill=color, font=("Georgia", 22, "bold"))


class StatsWindow(tk.Toplevel):
    """Toplevel window showing win/chip stats with an embedded matplotlib chart."""

    def __init__(self, parent, players):
        super().__init__(parent)
        self.title("Statistics")
        self.geometry("500x420")
        self.configure(bg=PANEL_BG)

        names = [p.name for p in players]
        chips = [p.chips for p in players]

        fig = Figure(figsize=(4.5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(names, chips, color="#2e8b57")
        ax.set_title("Chip Counts")
        ax.set_ylabel("Chips")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        summary = tk.Label(
            self,
            text="\n".join(f"{p.name}: ${p.chips}" for p in players),
            bg=PANEL_BG, fg=TEXT_LIGHT, font=("Georgia", 10), justify="left",
        )
        summary.pack(pady=(0, 10))


class GameApp:
    """Wraps the Tkinter UI around a live GameState/Tournament and drives play."""

    def __init__(self, root):
        self.root = root
        self.root.title("Poker AI Simulator - Expectiminimax")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.history = GameHistory()

        num_players = max(2, min(4, config.NUM_PLAYERS))
        self.human = Player("You", chips=config.STARTING_CHIPS, is_ai=False)
        self.ais = [
            Player(f"AI Opponent {i+1}", chips=config.STARTING_CHIPS, is_ai=True)
            for i in range(num_players - 1)
        ]
        self.human.raise_increment = 20
        self.all_players = [self.human] + self.ais
        self.game_state = GameState(self.all_players, history=self.history)

        self.tournament = None
        self.tournament_mode = False

        self.action_var = tk.StringVar(value="")
        self.hand_number = 0
        self.round_in_progress = False

        self._build_layout()
        self._log("Welcome to the Poker AI Simulator.")
        self._log(f"Playing with {num_players} players. Click 'New Game' to deal the first hand.")

    # ------------------------------------------------------------------ UI --
    def _build_layout(self):
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", pady=(8, 0))

        self.opponent_panels = []
        opp_row = tk.Frame(top, bg=BG)
        opp_row.pack()
        for ai in self.ais:
            panel = self._build_opponent_panel(opp_row, ai)
            panel["frame"].pack(side="left", padx=14)
            self.opponent_panels.append(panel)

        mid = tk.Frame(self.root, bg=BG)
        mid.pack(pady=10)
        self.community_widgets = [CardWidget(mid) for _ in range(5)]
        for widget in self.community_widgets:
            widget.pack(side="left", padx=4)

        self.result_label = tk.Label(self.root, text="", bg=BG, fg="#ffd43b",
                                       font=("Georgia", 14, "bold"))
        self.result_label.pack(pady=2)

        bottom_top = tk.Frame(self.root, bg=BG)
        bottom_top.pack(pady=(4, 0))
        tk.Label(bottom_top, text="You", bg=BG, fg=TEXT_LIGHT,
                  font=("Georgia", 12, "bold")).pack()
        player_frame = tk.Frame(bottom_top, bg=BG)
        player_frame.pack(pady=4)
        self.player_cards = [CardWidget(player_frame) for _ in range(2)]
        for widget in self.player_cards:
            widget.pack(side="left", padx=4)

        self.win_stars_label = tk.Label(bottom_top, text="", bg=BG, fg="#ffd43b",
                                          font=("Georgia", 13, "bold"))
        self.win_stars_label.pack(pady=(2, 0))

        side = tk.Frame(self.root, bg=PANEL_BG, bd=1, relief="ridge")
        side.place(x=780, y=16, width=204, height=160)
        tk.Label(side, text="TABLE", bg=PANEL_BG, fg=TEXT_MUTED,
                  font=("Georgia", 10, "bold")).pack(pady=(8, 4))
        self.pot_label = tk.Label(side, text="Pot: $0", bg=PANEL_BG, fg=TEXT_LIGHT, font=("Georgia", 11))
        self.pot_label.pack(pady=2)
        self.your_chips_label = tk.Label(side, bg=PANEL_BG, fg=TEXT_LIGHT, font=("Georgia", 10))
        self.your_chips_label.pack(pady=2)

        self.leaderboard_label = tk.Label(side, bg=PANEL_BG, fg=TEXT_MUTED,
                                            font=("Georgia", 9), justify="left")
        self.leaderboard_label.pack(pady=(6, 2))

        actions = tk.Frame(self.root, bg=BG)
        actions.pack(pady=8)

        self.new_game_btn = tk.Button(actions, text="New Game", bg="#3d8bfd", fg="white",
                                        font=("Georgia", 11, "bold"), width=10,
                                        command=self.on_new_game_click)
        self.new_game_btn.grid(row=0, column=0, padx=5)

        self.fold_btn = tk.Button(actions, text="Fold", bg="#c0392b", fg="white",
                                    font=("Georgia", 11, "bold"), width=8, state="disabled",
                                    command=lambda: self._submit_action("fold"))
        self.fold_btn.grid(row=0, column=1, padx=5)

        self.call_btn = tk.Button(actions, text="Call", bg="#2f6fed", fg="white",
                                    font=("Georgia", 11, "bold"), width=8, state="disabled",
                                    command=lambda: self._submit_action("call"))
        self.call_btn.grid(row=0, column=2, padx=5)

        self.raise_btn = tk.Button(actions, text="Raise", bg="#2e8b57", fg="white",
                                     font=("Georgia", 11, "bold"), width=8, state="disabled",
                                     command=self._on_raise_click)
        self.raise_btn.grid(row=0, column=3, padx=5)

        tk.Label(actions, text="Raise $", bg=BG, fg=TEXT_LIGHT).grid(row=0, column=4, padx=(10, 2))
        self.raise_entry = tk.Entry(actions, width=5)
        self.raise_entry.insert(0, "20")
        self.raise_entry.grid(row=0, column=5)

        self.tournament_btn = tk.Button(actions, text="Start Tournament", bg="#8e44ad", fg="white",
                                          font=("Georgia", 11, "bold"), width=15,
                                          command=self.on_start_tournament_click)
        self.tournament_btn.grid(row=0, column=6, padx=(14, 5))

        self.stats_btn = tk.Button(actions, text="View Statistics", bg="#16a085", fg="white",
                                     font=("Georgia", 11, "bold"), width=14,
                                     command=self.on_view_statistics_click)
        self.stats_btn.grid(row=0, column=7, padx=5)

        log_frame = tk.Frame(self.root, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(6, 10))
        self.log_text = tk.Text(log_frame, height=8, bg=LOG_BG, fg="#d7f5e3",
                                  font=("Consolas", 9), state="disabled", wrap="word")
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._refresh_labels()

    def _build_opponent_panel(self, parent, ai_player):
        frame = tk.Frame(parent, bg=BG)
        name_label = tk.Label(frame, text=ai_player.name, bg=BG, fg=TEXT_LIGHT,
                                font=("Georgia", 11, "bold"))
        name_label.pack()
        cards_frame = tk.Frame(frame, bg=BG)
        cards_frame.pack(pady=3)
        cards = [CardWidget(cards_frame) for _ in range(2)]
        for c in cards:
            c.pack(side="left", padx=3)
        chips_label = tk.Label(frame, bg=BG, fg=TEXT_MUTED, font=("Georgia", 9))
        chips_label.pack()
        return {"frame": frame, "player": ai_player, "cards": cards, "chips_label": chips_label}

    # --------------------------------------------------------------- log ---
    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ----------------------------------------------------------- display ---
    def _refresh_labels(self):
        self.pot_label.config(text=f"Pot: ${self.game_state.pot}")
        self.your_chips_label.config(text=f"Your Chips: ${self.human.chips}")
        for panel in self.opponent_panels:
            panel["chips_label"].config(text=f"${panel['player'].chips}")

        board = self.tournament.leaderboard() if self.tournament else \
            sorted(self.all_players, key=lambda p: p.chips, reverse=True)
        lines = [f"{i+1}. {p.name}: ${p.chips}" for i, p in enumerate(board)]
        self.leaderboard_label.config(text="\n".join(lines))

    def _refresh_win_stars(self):
        if self.human.hand and not self.human.is_folded and self.round_in_progress:
            stars, win_prob = self.game_state.estimate_win_stars(
                self.human, simulations=WIN_STARS_SIMULATIONS
            )
            star_str = "\u2605" * stars + "\u2606" * (5 - stars)
            self.win_stars_label.config(text=f"{star_str}  ({win_prob*100:.0f}% to win)")
        else:
            self.win_stars_label.config(text="")

    def update_display(self):
        for i, widget in enumerate(self.player_cards):
            if i < len(self.human.hand):
                c = self.human.hand[i]
                widget.set_card((c.rank, c.suit), face_up=True)
            else:
                widget.clear()

        reveal = not self.round_in_progress
        for panel in self.opponent_panels:
            ai = panel["player"]
            for i, widget in enumerate(panel["cards"]):
                if i < len(ai.hand) and not (ai.is_folded and self.round_in_progress):
                    c = ai.hand[i]
                    widget.set_card((c.rank, c.suit), face_up=(reveal and not ai.is_folded))
                else:
                    widget.clear()

        for i, widget in enumerate(self.community_widgets):
            if i < len(self.game_state.community_cards):
                c = self.game_state.community_cards[i]
                widget.set_card((c.rank, c.suit), face_up=True)
            else:
                widget.clear()

        self._refresh_labels()
        self._refresh_win_stars()
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
        self.root.wait_variable(self.action_var)
        self._set_action_buttons_enabled(False)

        action = self.action_var.get() or "call"
        self._log(f"You chose to {action}.")
        return action

    def ai_decision_func(self, game_state, player):
        self.update_display()
        self._log(f"{player.name} is thinking...")
        self.root.update_idletasks()

        try:
            action = game_state.ai_make_decision(
                player, depth=config.AI_DEPTH, hand_number=self.hand_number,
                strategy=lambda state, phase: combined_strategy.decide(state, phase, depth=config.AI_DEPTH),
            )
        except Exception as exc:
            self._log(f"[AI error, defaulting to call: {exc}]")
            action = "call"

        self._log(f"{player.name} chooses to {action}.")
        return action

    # --------------------------------------------------------- round flow --
    def on_new_game_click(self):
        if self.round_in_progress:
            return
        self.tournament_mode = False
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

        broke_players = [p for p in self.all_players if p.chips <= 0]
        if broke_players:
            self._log("Match over - a player is out of chips.")
            self.new_game_btn.config(state="normal", text="Restart Match", command=self.reset_match)
            return

        self.new_game_btn.config(state="normal")
        self.root.after(3000, self._auto_next_round)

    def _auto_next_round(self):
        if not self.round_in_progress and not self.tournament_mode:
            self.on_new_game_click()

    def reset_match(self):
        for p in self.all_players:
            p.chips = config.STARTING_CHIPS
        self.hand_number = 0
        self.new_game_btn.config(text="New Game", command=self.on_new_game_click)
        self._log("\n--- New match started ---")
        self.on_new_game_click()

    # ------------------------------------------------------- tournament ----
    def on_start_tournament_click(self):
        if self.round_in_progress:
            return
        self.tournament_mode = True
        for p in self.all_players:
            p.chips = config.STARTING_CHIPS
        self.tournament = Tournament(self.all_players)
        self._log("\n===== Tournament started =====")
        self._run_tournament_round()

    def _run_tournament_round(self):
        if self.tournament.is_over():
            champion = self.tournament.active_players()[0]
            self._log(f"\nTournament over! Champion: {champion.name}")
            self.result_label.config(text=f"{champion.name} wins the tournament!")
            self.tournament_mode = False
            return

        self.round_in_progress = True
        self.hand_number += 1
        self._log(f"\n--- Tournament Round {self.tournament.round_number + 1} "
                   f"(blinds {self.tournament.small_blind}/{self.tournament.big_blind}) ---")

        self.game_state = GameState(self.tournament.active_players(), history=self.history)
        self.update_display()

        winner, pot = self.tournament.play_round(
            ai_decision_func=self.ai_decision_func,
            human_action_func=self.human_action_func if self.human in self.tournament.active_players() else None,
        )

        self.round_in_progress = False
        self.update_display()
        self._log(f"{winner.name} wins ${pot}. Chips: " +
                   ", ".join(f"{p.name}=${p.chips}" for p in self.all_players))

        self.root.after(2000, self._run_tournament_round)

    # ------------------------------------------------------------- stats --
    def on_view_statistics_click(self):
        StatsWindow(self.root, self.all_players)


def launch():
    """Entry point used by main.py."""
    root = tk.Tk()
    GameApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch()