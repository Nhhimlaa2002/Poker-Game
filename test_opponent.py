from algorithm.opponent_model import OpponentProfile


player = OpponentProfile("Player1")

player.update("raise")
player.update("raise")
player.update("call")
player.update("fold")

print(player.get_statistics())
print("Aggression:", player.aggressiveness())
print("Bluff:", player.bluff_likelihood())