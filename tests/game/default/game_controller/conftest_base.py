"""
Shared base class for all GameController unit tests.
Import and subclass this instead of unittest.TestCase directly.
Each test file only needs to override setUp with what its method needs.
"""
import unittest
from unittest.mock import MagicMock
from game.game_controller import GameController
from game.board_presets.default.board_context import BoardContext


class BaseControllerTest(unittest.TestCase):
    """
    Provides the standard wired-up controller with two mocked players,
    a mocked board, and a real BoardContext.
    Subclasses call setUp() via super() then add method-specific defaults.
    """

    def setUp(self):
        # --- BOARD ---
        self.board = MagicMock()
        self.board.robber_placement = 0
        self.board.largest_army = None
        self.board.longest_road = None
        self.board.tiles = {}
        self.board.tile_vertices = {}

        # --- PLAYERS ---
        self.p1 = MagicMock()
        self.p1.name = "Player 1"
        self.p1.color = "red"
        self.p1.can_afford.return_value = True
        self.p1.has_available_pieces.return_value = True
        self.p1.has_dev_card.return_value = True
        self.p1.remove_dev_card.return_value = True
        self.p1.resources = {r: 5 for r in BoardContext().RESOURCES}
        self.p1.structures = []
        self.p1.roads = []
        self.p1.active_dev_cards = []
        self.p1.bought_dev_cards = []

        self.p2 = MagicMock()
        self.p2.name = "Player 2"
        self.p2.color = "blue"
        self.p2.can_afford.return_value = True
        self.p2.has_available_pieces.return_value = True
        self.p2.resources = {r: 5 for r in BoardContext().RESOURCES}
        self.p2.structures = []
        self.p2.roads = []
        self.p2.active_dev_cards = []
        self.p2.bought_dev_cards = []

        # --- TURN MANAGER ---
        self.tm = MagicMock()
        self.tm.is_current_player.side_effect = lambda p: p == self.p1
        self.tm.dice_rolled = False
        self.tm.played_dev_card = False

        # --- CONTROLLER ---
        self.board_context = BoardContext()
        self.controller = GameController(
            self.board, [self.p1, self.p2], self.tm, self.board_context
        )