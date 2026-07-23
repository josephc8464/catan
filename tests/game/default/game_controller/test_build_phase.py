import unittest
from unittest.mock import MagicMock
from game.game_controller import GameController
from game.board_presets.default.board_context import BoardContext

class TestControllerBuild(unittest.TestCase):
    def setUp(self):
        # 1. SETUP PERFECT DEFAULTS FOR ALL TESTS
        self.board = MagicMock()
        
        self.p1 = MagicMock()
        self.p1.name = "Player 1"
        self.p1.color = "red"
        self.p1.can_afford.return_value = True
        self.p1.has_available_pieces.return_value = True
        
        self.tm = MagicMock()
        self.tm.is_current_player.return_value = True
        
        self.controller = GameController(self.board, [self.p1], self.tm)
        self.controller.board_context = BoardContext()

    # ==========================================
    # --- BUY DEV CARD TESTS ---
    # ==========================================
    
    def setup_buy_dev_card_defaults(self):
        self.dev_cost = {'ore': 1, 'wheat': 1, 'wool': 1}
        self.board.get_top_dev_card.return_value = "knight"
        self.controller.board_context.get_cost = MagicMock(return_value=self.dev_cost)

    def test_buy_dev_card_success(self):
        self.setup_buy_dev_card_defaults()
        
        result = self.controller.buy_dev_card(self.p1)
        
        self.assertTrue(result)
        self.p1.remove_resources.assert_called_once_with(self.dev_cost)
        self.p1.add_dev_card.assert_called_once_with("knight")

    def test_buy_dev_card_fails_not_turn(self):
        self.setup_buy_dev_card_defaults()
        self.tm.is_current_player.return_value = False
        self.assertFalse(self.controller.buy_dev_card(self.p1))

    def test_buy_dev_card_fails_cost_none(self):
        self.setup_buy_dev_card_defaults()
        self.controller.board_context.get_cost = MagicMock(return_value=None)
        self.assertFalse(self.controller.buy_dev_card(self.p1))

    def test_buy_dev_card_fails_cant_afford(self):
        self.setup_buy_dev_card_defaults()
        self.p1.can_afford.return_value = False
        self.assertFalse(self.controller.buy_dev_card(self.p1))

    def test_buy_dev_card_fails_empty_deck(self):
        self.setup_buy_dev_card_defaults()
        self.board.get_top_dev_card.return_value = None
        self.assertFalse(self.controller.buy_dev_card(self.p1))

    # ==========================================
    # --- BUILD ROAD TESTS ---
    # ==========================================
    
    def setup_build_road_defaults(self):
        self.road_cost = {'wood': 1, 'brick': 1}
        self.v1, self.v2 = 4, 5
        self.board.get_road_color.return_value = None
        self.board.has_edge.return_value = True
        self.board.has_connected_neighbor.return_value = True
        self.controller.board_context.get_cost = MagicMock(return_value=self.road_cost)

    def test_build_road_success_paid(self):
        self.setup_build_road_defaults()
        
        result = self.controller.build_road(self.v1, self.v2, self.p1, free=False)
        
        self.assertTrue(result)
        self.board.add_road.assert_called_once_with(self.v1, self.v2, self.p1.color)
        self.p1.remove_resources.assert_called_once_with(self.road_cost)

    def test_build_road_success_free(self):
        self.setup_build_road_defaults()
        self.p1.can_afford.return_value = False # Proves free bypasses cost check
        
        result = self.controller.build_road(self.v1, self.v2, self.p1, free=True)
        
        self.assertTrue(result)
        self.board.add_road.assert_called_once_with(self.v1, self.v2, self.p1.color)
        self.p1.remove_resources.assert_not_called()

    def test_build_road_fails_not_turn(self):
        self.setup_build_road_defaults()
        self.tm.is_current_player.return_value = False
        self.assertFalse(self.controller.build_road(self.v1, self.v2, self.p1))

    def test_build_road_fails_cant_afford(self):
        self.setup_build_road_defaults()
        self.p1.can_afford.return_value = False
        self.assertFalse(self.controller.build_road(self.v1, self.v2, self.p1, free=False))

    def test_build_road_fails_no_edge(self):
        self.setup_build_road_defaults()
        self.board.has_edge.return_value = False
        self.assertFalse(self.controller.build_road(self.v1, self.v2, self.p1))

    def test_build_road_fails_occupied(self):
        self.setup_build_road_defaults()
        self.board.get_road_color.return_value = "blue"
        self.assertFalse(self.controller.build_road(self.v1, self.v2, self.p1))

    def test_build_road_fails_no_connection(self):
        self.setup_build_road_defaults()
        self.board.has_connected_neighbor.return_value = False
        self.assertFalse(self.controller.build_road(self.v1, self.v2, self.p1))

    def test_build_road_fails_no_pieces(self):
        self.setup_build_road_defaults()
        self.p1.has_available_pieces.return_value = False
        self.assertFalse(self.controller.build_road(self.v1, self.v2, self.p1))

    # ==========================================
    # --- PLACE STRUCTURE TESTS ---
    # ==========================================
    
    def setup_place_structure_defaults(self):
        self.vertex = 10
        self.board.get_structure.return_value = (None, None)
        self.board.has_structure_neighbor.return_value = False
        self.board.has_road_neighbor.return_value = True

    def test_place_structure_success(self):
        self.setup_place_structure_defaults()
        
        result = self.controller.place_structure(self.vertex, self.p1, init_setup=False)
        
        self.assertTrue(result)
        self.board.add_structure.assert_called_once_with(self.vertex, self.p1.color, 'settlement')
        self.p1.add_structure.assert_called_once_with(self.vertex, 'settlement')
        self.p1.remove_resources.assert_called_once()

    def test_place_structure_fails_not_turn(self):
        self.setup_place_structure_defaults()
        self.tm.is_current_player.return_value = False
        self.assertFalse(self.controller.place_structure(self.vertex, self.p1))

    def test_place_structure_fails_cant_afford(self):
        self.setup_place_structure_defaults()
        self.p1.can_afford.return_value = False
        self.assertFalse(self.controller.place_structure(self.vertex, self.p1, init_setup=False))

    def test_place_structure_fails_occupied(self):
        self.setup_place_structure_defaults()
        self.board.get_structure.return_value = ("settlement", "blue")
        self.assertFalse(self.controller.place_structure(self.vertex, self.p1))

    def test_place_structure_fails_distance_rule(self):
        self.setup_place_structure_defaults()
        self.board.has_structure_neighbor.return_value = True
        self.assertFalse(self.controller.place_structure(self.vertex, self.p1))

    def test_place_structure_fails_no_road(self):
        self.setup_place_structure_defaults()
        self.board.has_road_neighbor.return_value = False
        self.assertFalse(self.controller.place_structure(self.vertex, self.p1, init_setup=False))

    def test_place_structure_fails_no_pieces(self):
        self.setup_place_structure_defaults()
        self.p1.has_available_pieces.return_value = False
        self.assertFalse(self.controller.place_structure(self.vertex, self.p1))

    # ==========================================
    # --- UPGRADE STRUCTURE TESTS ---
    # ==========================================
    
    def setup_upgrade_structure_defaults(self):
        self.vertex = 5
        self.upgrade_cost = {'ore': 3, 'wheat': 2}
        self.board.get_structure.return_value = ("settlement", "red")
        self.controller.board_context.get_next_upgrade = MagicMock(return_value="city")
        self.controller.board_context.get_cost = MagicMock(return_value=self.upgrade_cost)

    def test_upgrade_structure_success(self):
        self.setup_upgrade_structure_defaults()
        
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        
        self.assertTrue(result)
        self.p1.remove_resources.assert_called_once_with(self.upgrade_cost)
        self.board.add_structure.assert_called_once_with(self.vertex, self.p1.color, "city")

    def test_upgrade_structure_fails_not_turn(self):
        self.setup_upgrade_structure_defaults()
        self.tm.is_current_player.return_value = False
        self.assertFalse(self.controller.upgrade_structure(self.vertex, self.p1))

    def test_upgrade_structure_fails_no_structure(self):
        self.setup_upgrade_structure_defaults()
        self.board.get_structure.return_value = (None, None)
        self.assertFalse(self.controller.upgrade_structure(self.vertex, self.p1))

    def test_upgrade_structure_fails_fully_upgraded(self):
        self.setup_upgrade_structure_defaults()
        self.controller.board_context.get_next_upgrade = MagicMock(return_value=None)
        self.assertFalse(self.controller.upgrade_structure(self.vertex, self.p1))

    def test_upgrade_structure_fails_wrong_owner(self):
        self.setup_upgrade_structure_defaults()
        self.board.get_structure.return_value = ("settlement", "blue")
        self.assertFalse(self.controller.upgrade_structure(self.vertex, self.p1))

    def test_upgrade_structure_fails_no_pieces(self):
        self.setup_upgrade_structure_defaults()
        self.p1.has_available_pieces.return_value = False
        self.assertFalse(self.controller.upgrade_structure(self.vertex, self.p1))