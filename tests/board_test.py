import sys
sys.path.append('.')

from game.board_presets.default_board import DefaultBoard

def test_default_board_setup():
    board = DefaultBoard()
    board.setup_board()

if __name__ == "__main__":
    test_default_board_setup()