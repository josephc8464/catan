import sys
sys.path.append('.')

from game import GameController, Player, TurnManager
from game.board_presets.default import DefaultBoard

def setup_board() -> DefaultBoard:
    board = DefaultBoard()
    board.setup_board()

    return board

def buy_settlement():
