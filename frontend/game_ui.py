"""
frontend/game_ui.py
====================
Tkinter GUI for the Poker AI Simulator.
"""
 
import os
import sys
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox  
 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
 
import config
from game_engine.card import RANK_NAMES
from game_engine.poker_game import Player, GameState, GameHistory
from game_engine.tournament import Tournament
from algorithm import combined_strategy
from game_engine.stats_tracker import StatsTracker
 
 
def _lighten_color(hex_color, amount=30):
    """Lighten a hex color by a fixed amount per channel."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02x}{g:02x}{b:02x}"
 
 
def add_hover_effect(button, base_color, hover_amount=30):
    """Bind hover events to lighten a button's background on mouseover."""
    hover_color = _lighten_color(base_color, hover_amount)
 
    def on_enter(event):
        if button['state'] != 'disabled':
            button.config(bg=hover_color)
 
    def on_leave(event):
        if button['state'] != 'disabled':
            button.config(bg=base_color)
 
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
 
 
WINDOW_W, WINDOW_H = 1100, 680
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
        self.stats_tracker = StatsTracker()
 
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
        self.difficulty_var = tk.StringVar(value=config.DEFAULT_DIFFICULTY)
 
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
        stats_side = tk.Frame(self.root, bg=PANEL_BG, bd=1, relief="ridge")
        stats_side.place(x=780, y=185, width=204, height=140)
        tk.Label(stats_side, text="SESSION STATS", bg=PANEL_BG, fg=TEXT_MUTED,
                 font=("Georgia", 10, "bold")).pack(pady=(6, 2))
        self.stats_label = tk.Label(stats_side, text=self.stats_tracker.get_formatted_stats(),
                                    bg=PANEL_BG, fg=TEXT_LIGHT, font=("Consolas", 8), justify="left")
        self.stats_label.pack(pady=2, padx=4)
        self.pot_label = tk.Label(side, text="Pot: $0", bg=PANEL_BG, fg=TEXT_LIGHT, font=("Georgia", 11))
        self.pot_label.pack(pady=2)
        self.your_chips_label = tk.Label(side, bg=PANEL_BG, fg=TEXT_LIGHT, font=("Georgia", 10))
        self.your_chips_label.pack(pady=2)
 
        self.leaderboard_label = tk.Label(side, bg=PANEL_BG, fg=TEXT_MUTED,
                                            font=("Georgia", 9), justify="left")
        self.leaderboard_label.pack(pady=(6, 2))
 
        # -- Scrollable Action Toolbar Container -----------------------------
        actions_container = tk.Frame(self.root, bg=BG)
        actions_container.pack(fill="x", padx=10, pady=4)

        actions_canvas = tk.Canvas(actions_container, bg=BG, height=44, highlightthickness=0)
        actions_scrollbar = tk.Scrollbar(actions_container, orient="horizontal", command=actions_canvas.xview)
        actions_canvas.configure(xscrollcommand=actions_scrollbar.set)

        actions_scrollbar.pack(side="bottom", fill="x")
        actions_canvas.pack(side="top", fill="x", expand=True)

        actions = tk.Frame(actions_canvas, bg=BG)
        actions_canvas.create_window((0, 0), window=actions, anchor="nw")

        def _on_actions_configure(event):
            actions_canvas.configure(scrollregion=actions_canvas.bbox("all"))

        actions.bind("<Configure>", _on_actions_configure)

        # Shift + Mousewheel support for horizontal scrolling
        actions_canvas.bind_all("<Shift-MouseWheel>", 
            lambda e: actions_canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))
 
        # -- New Game button ------------------------------------------------
        self.new_game_btn = tk.Button(actions, text="New Game", bg="#3d8bfd", fg="white",
                                        font=("Georgia", 11, "bold"), width=10,
                                        command=self.on_new_game_click)
        self.new_game_btn.grid(row=0, column=0, padx=5)
        add_hover_effect(self.new_game_btn, "#3d8bfd")

        # -- Export Hand History Button ---------------------------------------
        self.export_btn = tk.Button(actions, text="Export History", bg="#e67e22", fg="white",
                                     font=("Georgia", 11, "bold"), width=12,
                                     command=self.on_export_hand_history_click)
        self.export_btn.grid(row=0, column=10, padx=5)
        add_hover_effect(self.export_btn, "#e67e22")
 
        # -- Difficulty selector (segmented buttons) ------------------------
        tk.Label(actions, text="Difficulty:", bg=BG, fg=TEXT_LIGHT,
                 font=("Georgia", 10)).grid(row=0, column=1, padx=(8, 2))
 
        difficulty_frame = tk.Frame(actions, bg=BG)
        difficulty_frame.grid(row=0, column=2, padx=2)
 
        self.difficulty_buttons = {}
        DIFFICULTY_COLORS = {"easy": "#2e8b57", "medium": "#d4a017", "hard": "#c0392b"}
 
        def _select_difficulty(level):
            self.difficulty_var.set(level)
            for lvl, btn in self.difficulty_buttons.items():
                if lvl == level:
                    btn.config(bg=DIFFICULTY_COLORS[lvl], relief="sunken", fg="white")
                else:
                    btn.config(bg="#2a2a2a", relief="raised", fg="#aaaaaa")
 
        for i, level in enumerate(["easy", "medium", "hard"]):
            btn = tk.Button(difficulty_frame, text=level.capitalize(), width=6,
                             font=("Georgia", 9, "bold"),
                             command=lambda l=level: _select_difficulty(l))
            btn.grid(row=0, column=i, padx=1)
            self.difficulty_buttons[level] = btn
 
        _select_difficulty(config.DEFAULT_DIFFICULTY)
 
        # -- Fold / Call / Raise ---------------------------------------------
        self.fold_btn = tk.Button(actions, text="Fold", bg="#c0392b", fg="white",
                                    font=("Georgia", 11, "bold"), width=8, state="disabled",
                                    command=lambda: self._submit_action("fold"))
        self.fold_btn.grid(row=0, column=3, padx=5)
        add_hover_effect(self.fold_btn, "#c0392b")
 
        self.call_btn = tk.Button(actions, text="Call", bg="#2f6fed", fg="white",
                                    font=("Georgia", 11, "bold"), width=8, state="disabled",
                                    command=lambda: self._submit_action("call"))
        self.call_btn.grid(row=0, column=4, padx=5)
        add_hover_effect(self.call_btn, "#2f6fed")
 
        self.raise_btn = tk.Button(actions, text="Raise", bg="#2e8b57", fg="white",
                                     font=("Georgia", 11, "bold"), width=8, state="disabled",
                                     command=self._on_raise_click)
        self.raise_btn.grid(row=0, column=5, padx=5)
        add_hover_effect(self.raise_btn, "#2e8b57")
 
        # -- Raise amount (Spinbox: type OR use up/down arrows) -------------
        tk.Label(actions, text="Raise $", bg=BG, fg=TEXT_LIGHT).grid(row=0, column=6, padx=(10, 2))
        self.raise_entry = tk.Spinbox(actions, width=5, from_=10, to=1000, increment=10,
                                        bg="#ffffff", fg="#000000", font=("Georgia", 10),
                                        buttonbackground="#3d8bfd")
        self.raise_entry.delete(0, "end")
        self.raise_entry.insert(0, "20")
        self.raise_entry.grid(row=0, column=7)
 
        # -- Tournament / Stats -----------------------------------------------
        self.tournament_btn = tk.Button(actions, text="Start Tournament", bg="#8e44ad", fg="white",
                                          font=("Georgia", 11, "bold"), width=13,
                                          command=self.on_start_tournament_click)
        self.tournament_btn.grid(row=0, column=8, padx=(8, 3))
        add_hover_effect(self.tournament_btn, "#8e44ad")
 
        self.stats_btn = tk.Button(actions, text="View Statistics", bg="#16a085", fg="white",
                                     font=("Georgia", 11, "bold"), width=12,
                                     command=self.on_view_statistics_click)
        self.stats_btn.grid(row=0, column=9, padx=5)
        add_hover_effect(self.stats_btn, "#16a085")
 
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

    # ------------------------------------------------------------- export --
    def on_export_hand_history_click(self):
        """Exports session hand history to a user-selected text file."""
        source_path = "data/hand_history.txt"

        if not os.path.exists(source_path) or os.path.getsize(source_path) == 0:
            messagebox.showwarning("Export History", "No hand history recorded yet. Play a hand first!")
            return

        target_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Hand History As",
            initialfile=f"poker_hand_history_session.txt"
        )

        if not target_file:
            return  # User cancelled

        try:
            with open(source_path, "r") as src, open(target_file, "w") as dst:
                dst.write(f"=== POKER AI SIMULATOR SESSION HAND HISTORY ===\n")
                dst.write(f"Total Hands Tracked: {self.hand_number}\n\n")
                dst.write(src.read())

            messagebox.showinfo("Export Success", f"Hand history successfully saved to:\n{target_file}")
            self._log(f"Exported hand history to {target_file}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export file: {e}")
 
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
        """Ask the AI engine for a decision, using the currently selected difficulty."""
        difficulty = self.difficulty_var.get()
        try:
            action = game_state.ai_make_decision(
                player, difficulty=difficulty, hand_number=self.hand_number,
                strategy=lambda state, phase: combined_strategy.decide(
                    state, phase, depth=config.DIFFICULTY_PRESETS[difficulty]["depth"]
                ),
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
        winner_names = [winner.name] if not isinstance(winner, list) else [w.name for w in winner]
        self.stats_tracker.record_hand(winner_names, pot_amount)
        if hasattr(self, 'stats_label'):
            self.stats_label.config(text=self.stats_tracker.get_formatted_stats())

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

        winner_names = [winner.name] if not isinstance(winner, list) else [w.name for w in winner]
        self.stats_tracker.record_hand(winner_names, pot)
        if hasattr(self, 'stats_label'):
            self.stats_label.config(text=self.stats_tracker.get_formatted_stats())
 
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