import sys
sys.path.append('.')

from game.board_presets.default_board import DefaultBoard

def test_default_board_setup():
    board = DefaultBoard()
    board.setup_board()

    # every vertex should have 2 or 3 neighbors
    for id, neighbors in board.graph.adj_list.items():
        print(f"vertex {id}: {len(neighbors)} neighbors")

if __name__ == "__main__":
    test_default_board_setup()