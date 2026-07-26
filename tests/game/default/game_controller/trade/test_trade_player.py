import unittest
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestTradePlayer(BaseControllerTest):
    """
    Unit tests for GameController.trade_player().
    Takes dicts for offered resources and requested resources.
    """

    def setUp(self):
        super().setUp()
        self.tm.dice_rolled = True
        
        # P1 has wood to offer
        self.p1.can_afford.return_value = True
        self.p1.resources = {'wood': 2, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}
        self.offer = {'wood': 2}
        
        # P2 has ore to trade back
        self.p2.can_afford.return_value = True
        self.p2.resources = {'wood': 0, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 1}
        self.request = {'ore': 1}

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_domestic_trade(self):
        """Successfully executes a trade between two players."""
        result = self.controller.trade_player(self.p1, self.p2, self.offer, self.request)
        self.assertTrue(result)

        # Player 1 gives wood, gets ore
        self.p1.remove_resources.assert_called_once_with(self.offer)
        self.p1.add_resources.assert_called_once_with(self.request)

        # Player 2 gives ore, gets wood
        self.p2.remove_resources.assert_called_once_with(self.request)
        self.p2.add_resources.assert_called_once_with(self.offer)

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards(self):
        """Fails cleanly on bad turn, unrolled dice, missing resources, or self-trade."""
        # 1. Not active player's turn
        self.assertFalse(self.controller.trade_player(self.p2, self.p1, self.request, self.offer))

        # 2. Dice not rolled
        self.tm.dice_rolled = False
        self.assertFalse(self.controller.trade_player(self.p1, self.p2, self.offer, self.request))
        self.tm.dice_rolled = True

        # 3. Active player lacks offered resources
        self.p1.can_afford.return_value = False
        self.assertFalse(self.controller.trade_player(self.p1, self.p2, self.offer, self.request))
        self.p1.can_afford.return_value = True

        # 4. Target player lacks requested resources
        self.p2.can_afford.return_value = False
        self.assertFalse(self.controller.trade_player(self.p1, self.p2, self.offer, self.request))
        self.p2.can_afford.return_value = True

        # 5. Cannot trade with self
        self.assertFalse(self.controller.trade_player(self.p1, self.p1, self.offer, self.request))

        # Verify no mutations occurred during failures
        self.p1.remove_resource.assert_not_called()
        self.p1.add_resource.assert_not_called()
        self.p2.remove_resource.assert_not_called()
        self.p2.add_resource.assert_not_called()


if __name__ == '__main__':
    unittest.main()