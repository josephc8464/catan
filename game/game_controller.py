from game import player
from board_presets import board

class GameController:
    def __init__(self, board, players):
        self.board = board
        self.players = players
        self.current_player_index = 0
        