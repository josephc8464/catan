import unittest
from unittest.mock import patch
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestTradePort(BaseControllerTest):
    """
    Unit tests for GameController.trade_port().
    Assumes checks for 3:1 generic or 2:1 specialized port access at specified vertices.
    """

    def setUp(self):
        super().setUp()
        self.tm.dice_rolled = True
        self.p1.resources = {'wood': 3, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}
        self.board.bank_has_resource.return_value = True
        self.board.get_structure.return_value = ('settlement', 'red')
        self.v1, self.v2 = 1, 2

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_trade_generic_port_3_to_1(self):
        """Successfully trades 3 of a resource for 1 via generic port."""
        self.board.get_port.return_value = 'any'
        result = self.controller.trade_port(self.p1, (self.v1, self.v2), 'wood', 'ore')
        self.assertTrue(result)
            
        self.p1.remove_resource.assert_called_once_with('wood', 3)
        self.p1.add_resource.assert_called_once_with('ore', 1)

    def test_success_trade_special_port_2_to_1(self):
        """Successfully trades 2 of a resource for 1 via specialized port."""
        self.board.get_port.return_value = 'wood'
        result = self.controller.trade_port(self.p1, (self.v1, self.v2), 'wood', 'ore')
        self.assertTrue(result)
            
        self.p1.remove_resource.assert_called_once_with('wood', 2)
        self.p1.add_resource.assert_called_once_with('ore', 1)

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards(self):
        """Fails cleanly on bad turn, unrolled dice, missing port, or insufficient resources."""
        self.board.get_port.return_value = 'any'

        # 1. Not player's turn
        result = self.controller.trade_port(self.p2, (self.v1, self.v2), 'wood', 'ore')
        self.assertFalse(result)
    
        # 2. Dice not rolled
        self.tm.dice_rolled = False
        result = self.controller.trade_port(self.p1, (self.v1, self.v2), 'wood', 'ore')
        self.assertFalse(result)
        self.tm.dice_rolled = True
    
        # 3. Insufficient player resources (needs 3, has 2)
        self.p1.can_afford.return_value = False
        result = self.controller.trade_port(self.p1, (self.v1, self.v2), 'wood', 'ore')
        self.assertFalse(result)
        self.p1.can_afford.return_value = True
    
        # 4. Bank is empty of requested resource
        self.board.bank_has_resource.return_value = False
        result = self.controller.trade_port(self.p1, (self.v1, self.v2), 'wood', 'ore')
        self.assertFalse(result)
        self.board.bank_has_resource.return_value = True
    
        # 5. Player does not have valid port access (ratio returns 4, which is bank trade)
        self.board.get_structure.return_value = (None, None)
        result = self.controller.trade_port(self.p1, (self.v1, self.v2), 'wood', 'ore')
        self.assertFalse(result)

        # Verify no mutations occurred during failures
        self.p1.remove_resource.assert_not_called()
        self.p1.add_resource.assert_not_called()


if __name__ == '__main__':
    unittest.main()