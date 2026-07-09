import random

class TurnManager():
    def __init__(self, players):
        self.players = players
        self.current_player_index = 0
        self.dice_rolled = False

    def is_current_player(self, player):
        return self.players[self.current_player_index] == player
    
    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def roll_dice(self) -> int | None:
        if self.dice_rolled:
            return None
    
        dice_roll = random.randint(1, 6) + random.randint(1, 6)
        self.dice_rolled = True
        return dice_roll