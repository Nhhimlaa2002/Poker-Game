class OpponentProfile:

    def __init__(self, player_name):
        self.player_name = player_name

        self.fold_count = 0
        self.call_count = 0
        self.raise_count = 0

        self.total_actions = 0


    def update(self, action):

        self.total_actions += 1

        if action == "fold":
            self.fold_count += 1

        elif action == "call":
            self.call_count += 1

        elif action == "raise":
            self.raise_count += 1



    def get_statistics(self):

        if self.total_actions == 0:
            return {
                "fold_frequency": 0,
                "call_frequency": 0,
                "raise_frequency": 0
            }


        return {

            "fold_frequency":
                self.fold_count / self.total_actions,

            "call_frequency":
                self.call_count / self.total_actions,

            "raise_frequency":
                self.raise_count / self.total_actions

        }



    def aggressiveness(self):

        stats = self.get_statistics()

        return stats["raise_frequency"]



    def bluff_likelihood(self):

        stats = self.get_statistics()

        return (
            stats["raise_frequency"]
            *
            (1 - stats["fold_frequency"])
        )