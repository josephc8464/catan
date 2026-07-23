import unittest
from unittest.mock import MagicMock
from game.game_controller import GameController
from game.board_presets.default.board_context import BoardContext

class TestControllerTrade(unittest.TestCase):
    def setUp(self):
        # 1. SETUP PERFECT DEFAULTS FOR ALL TESTS
        self.board = MagicMock()
        
        self.p1 = MagicMock()
        self.p1.name = "Player 1"
        self.p1.color = "red"
        
        self.p2 = MagicMock()
        self.p2.name = "Player 2"
        self.p2.color = "blue"
        
        self.tm = MagicMock()
        self.tm.is_current_player.return_value = True
        
        # Initialize controller with the REAL BoardContext
        self.controller = GameController(self.board, [self.p1, self.p2], self.tm)
        self.controller.board_context = BoardContext()

    # ==========================================
    # --- TRADE PLAYER TESTS ---
    # ==========================================

    def setup_trade_player_defaults(self):
        self.req1 = {'wood': 1}
        self.req2 = {'wheat': 1}
        
        self.p1.can_afford.return_value = True
        self.p2.can_afford.return_value = True
        
        # Mocking the real BoardContext method just for this test grouping
        self.controller.board_context.is_valid_resource_cost = MagicMock(return_value=True)

    def test_trade_player_success(self):
        self.setup_trade_player_defaults()
        
        result = self.controller.trade_player(self.p1, self.p2, self.req1, self.req2)
        
        self.assertTrue(result)
        self.p1.add_resources.assert_called_once_with(self.req2)
        self.p2.add_resources.assert_called_once_with(self.req1)
        self.p1.remove_resources.assert_called_once_with(self.req1)
        self.p2.remove_resources.assert_called_once_with(self.req2)

    def test_trade_player_fails_not_turn(self):
        self.setup_trade_player_defaults()
        self.tm.is_current_player.return_value = False
        self.assertFalse(self.controller.trade_player(self.p1, self.p2, self.req1, self.req2))

    def test_trade_player_fails_p1_invalid_cost(self):
        self.setup_trade_player_defaults()
        self.controller.board_context.is_valid_resource_cost = MagicMock(side_effect=lambda req: req != self.req1)
        self.assertFalse(self.controller.trade_player(self.p1, self.p2, self.req1, self.req2))

    def test_trade_player_fails_p2_invalid_cost(self):
        self.setup_trade_player_defaults()
        self.controller.board_context.is_valid_resource_cost = MagicMock(side_effect=lambda req: req != self.req2)
        self.assertFalse(self.controller.trade_player(self.p1, self.p2, self.req1, self.req2))

    def test_trade_player_fails_p1_cant_afford(self):
        self.setup_trade_player_defaults()
        self.p1.can_afford.return_value = False
        self.assertFalse(self.controller.trade_player(self.p1, self.p2, self.req1, self.req2))

    def test_trade_player_fails_p2_cant_afford(self):
        self.setup_trade_player_defaults()
        self.p2.can_afford.return_value = False
        self.assertFalse(self.controller.trade_player(self.p1, self.p2, self.req1, self.req2))

    # ==========================================
    # --- TRADE PORT TESTS ---
    # ==========================================

    def setup_trade_port_defaults(self):
        self.vertices = (1, 2)
        self.resource_out = 'ore'
        self.resource_in = 'wheat'
        
        self.p1.can_afford.return_value = True
        
        # Resetting player resource methods
        self.p1.add_resource = MagicMock()
        self.p1.remove_resource = MagicMock()
        
        # Board mocks
        self.board.get_port.return_value = "wheat"
        self.board.get_structure.side_effect = lambda v: ("settlement", "red") if v == 1 else (None, None)
        self.board.bank_has_resource.return_value = True
        self.board.remove_bank_resource = MagicMock()
        self.board.add_bank_resource = MagicMock()
        
        # Context mock
        self.controller.board_context.get_port_ratio = MagicMock(return_value=(2, 1))

    def test_trade_port_success(self):
        self.setup_trade_port_defaults()
        
        result = self.controller.trade_port(self.p1, self.vertices, self.resource_in, self.resource_out)
        
        self.assertTrue(result)
        self.p1.add_resource.assert_called_once_with(self.resource_out, 1)
        self.p1.remove_resource.assert_called_once()
        self.board.remove_bank_resource.assert_called_once_with(self.resource_out, 1)
        self.board.add_bank_resource.assert_called_once()

    def test_trade_port_fails_not_turn(self):
        self.setup_trade_port_defaults()
        self.tm.is_current_player.return_value = False
        self.assertFalse(self.controller.trade_port(self.p1, self.vertices, self.resource_in, self.resource_out))

    def test_trade_port_fails_no_port(self):
        self.setup_trade_port_defaults()
        self.board.get_port.return_value = None
        self.assertFalse(self.controller.trade_port(self.p1, self.vertices, self.resource_in, self.resource_out))

    def test_trade_port_fails_no_structure(self):
        self.setup_trade_port_defaults()
        self.board.get_structure.side_effect = lambda v: (None, None)
        self.assertFalse(self.controller.trade_port(self.p1, self.vertices, self.resource_in, self.resource_out))

    def test_trade_port_fails_invalid_ratio(self):
        self.setup_trade_port_defaults()
        self.controller.board_context.get_port_ratio = MagicMock(return_value=(0, 0))
        self.assertFalse(self.controller.trade_port(self.p1, self.vertices, self.resource_in, self.resource_out))

    def test_trade_port_fails_cant_afford(self):
        self.setup_trade_port_defaults()
        self.p1.can_afford.return_value = False
        self.assertFalse(self.controller.trade_port(self.p1, self.vertices, self.resource_in, self.resource_out))

    def test_trade_port_fails_bank_empty(self):
        self.setup_trade_port_defaults()
        self.board.bank_has_resource.return_value = False
        self.assertFalse(self.controller.trade_port(self.p1, self.vertices, self.resource_in, self.resource_out))

    # ==========================================
    # --- TRADE BANK TESTS ---
    # ==========================================

    def setup_trade_bank_defaults(self):
        self.resource_in = 'wood'
        self.resource_out = 'brick'
        
        self.p1.can_afford.return_value = True
        self.p1.add_resource = MagicMock()
        self.p1.remove_resource = MagicMock()
        
        self.board.bank_has_resource.return_value = True
        self.board.remove_bank_resource = MagicMock()
        self.board.add_bank_resource = MagicMock()
        
        self.controller.board_context.get_bank_ratio = MagicMock(return_value=(4, 1))
        self.controller.board_context.is_valid_resource_cost = MagicMock(return_value=True)

    def test_trade_bank_success(self):
        self.setup_trade_bank_defaults()
        
        result = self.controller.trade_bank(self.p1, self.resource_in, self.resource_out)
        
        self.assertTrue(result)
        self.p1.remove_resource.assert_called_once_with(self.resource_in, 4)
        self.p1.add_resource.assert_called_once_with(self.resource_out, 1)
        self.board.add_bank_resource.assert_called_once_with(self.resource_in, 4)
        self.board.remove_bank_resource.assert_called_once_with(self.resource_out, 1)

    def test_trade_bank_fails_not_turn(self):
        self.setup_trade_bank_defaults()
        self.tm.is_current_player.return_value = False
        self.assertFalse(self.controller.trade_bank(self.p1, self.resource_in, self.resource_out))

    def test_trade_bank_fails_no_ratio(self):
        self.setup_trade_bank_defaults()
        self.controller.board_context.get_bank_ratio = MagicMock(return_value=None)
        self.assertFalse(self.controller.trade_bank(self.p1, self.resource_in, self.resource_out))

    def test_trade_bank_fails_invalid_resource(self):
        self.setup_trade_bank_defaults()
        self.controller.board_context.is_valid_resource_cost = MagicMock(return_value=False)
        self.assertFalse(self.controller.trade_bank(self.p1, self.resource_in, self.resource_out))

    def test_trade_bank_fails_cant_afford(self):
        self.setup_trade_bank_defaults()
        self.p1.can_afford.return_value = False
        self.assertFalse(self.controller.trade_bank(self.p1, self.resource_in, self.resource_out))

    def test_trade_bank_fails_bank_empty(self):
        self.setup_trade_bank_defaults()
        self.board.bank_has_resource.return_value = False
        self.assertFalse(self.controller.trade_bank(self.p1, self.resource_in, self.resource_out))