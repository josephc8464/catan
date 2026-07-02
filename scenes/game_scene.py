from rendering.default.board.board_renderer import DefaultBoardRenderer
from rendering.default.ui.ui_renderer import UIRenderer

class GameScene():
    def __init__(self):
        self.placeholder = 0
        self.ui = UIRenderer()
        self.board_renderer = DefaultBoardRenderer()

    def draw():
        self.board_renderer.render_board()
