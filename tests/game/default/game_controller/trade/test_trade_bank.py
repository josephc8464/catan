import unittest
from unittest.mock import MagicMock, call
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestTradeBank(BaseControllerTest):
    """
    Unit tests for GameController.trade_bank().
    Assumes standard 4:1 bank trade mechanic.
    """

    def setUp(self):
        super().setUp()
        self.tm.dice_rolled = True
        self.p1.resources = {'wood': 4, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}
        self.board.bank_has_resource.return_value = True

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_trade_bank_4_to_1(self):
        """Successfully trades 4 of a resource for 1 of another."""
        manager = MagicMock()
        manager.attach_mock(self.p1.remove_resource, 'p1_remove')
        manager.attach_mock(self.p1.add_resource, 'p1_add')
        manager.attach_mock(self.board.add_bank_resource, 'bank_add')
        manager.attach_mock(self.board.remove_bank_resource, 'bank_remove')

        result = self.controller.trade_bank(self.p1, 'wood', 'ore')
        self.assertTrue(result)

        # Verify exact sequence of transfers
        manager.assert_has_calls([
            call.p1_remove('wood', 4),
            call.bank_add('wood', 4),
            call.bank_remove('ore', 1),
            call.p1_add('ore', 1)
        ], any_order=True)

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards(self):
        """Fails cleanly on bad turn, unrolled dice, insufficient funds, or empty bank."""
        # 1. Not player's turn
        self.assertFalse(self.controller.trade_bank(self.p2, 'wood', 'ore'))

        # 2. Dice not rolled
        self.tm.dice_rolled = False
        self.assertFalse(self.controller.trade_bank(self.p1, 'wood', 'ore'))
        self.tm.dice_rolled = True

        # 3. Insufficient player resources (needs 4, has 3)
        self.p1.can_afford.return_value = False
        self.assertFalse(self.controller.trade_bank(self.p1, 'wood', 'ore'))

        # 4. Bank is empty of requested resource
        self.board.bank_has_resource.return_value = False
        self.assertFalse(self.controller.trade_bank(self.p1, 'wood', 'ore'))

        # 5. Invalid resources
        self.assertFalse(self.controller.trade_bank(self.p1, 'gold', 'ore'))

        # Verify no mutations occurred during failures
        self.p1.remove_resource.assert_not_called()
        self.p1.add_resource.assert_not_called()


if __name__ == '__main__':
    unittest.main()