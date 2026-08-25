class StatsTracker:
    def __init__(self):
        self.total_hands = 0
        self.total_pot_accumulated = 0
        self.wins = {}  # Format: {player_name: win_count}

    def record_hand(self, winner_names, pot_amount):
        """Call this at the end of every hand with the list of winners and total pot."""
        self.total_hands += 1
        self.total_pot_accumulated += pot_amount

        # Handles split pots when multiple winners are returned
        for name in winner_names:
            self.wins[name] = self.wins.get(name, 0) + 1

    @property
    def average_pot(self):
        if self.total_hands == 0:
            return 0.0
        return self.total_pot_accumulated / self.total_hands

    def get_win_rate(self, player_name):
        if self.total_hands == 0:
            return 0.0
        return (self.wins.get(player_name, 0) / self.total_hands) * 100

    def get_formatted_stats(self):
        """Returns a clean multi-line string for the Tkinter stats panel."""
        lines = [
            f"Hands Played: {self.total_hands}",
            f"Avg Pot: ${self.average_pot:.1f}",
            "-------------------"
        ]
        for player, count in self.wins.items():
            rate = self.get_win_rate(player)
            lines.append(f"{player}: {count} W ({rate:.0f}%)")
        return "\n".join(lines)