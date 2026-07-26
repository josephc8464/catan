import unittest
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestPlayMonopoly(BaseControllerTest):
    """
    Unit tests for GameController.play_monopoly().
    """

    def setUp(self):
        super().setUp()
        self.tm.dice_rolled = True
        self.p2.resources = {'wood': 3, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_plays_monopoly(self):
        """Steals all of a valid resource from opponents, consumes card, and sets flag."""
        self.p1.resources = {'wood': 5, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}
        
        self.assertTrue(self.controller.play_monopoly(self.p1, 'wood'))
        
        # Verify transfers (does not steal from self)
        self.p2.remove_resource.assert_called_once_with('wood', 3)
        self.p1.add_resource.assert_called_once_with('wood', 3)
        self.p1.remove_resource.assert_not_called()
        
        # Verify state
        self.p1.remove_dev_card.assert_called_once_with('monopoly')
        self.tm.set_played_dev_card.assert_called_once()

    def test_success_valid_resources_and_empty_opponents(self):
        """Monopoly on an unheld resource, or iterating through all valid resources, succeeds."""
        self.p2.resources = {k: 0 for k in self.p2.resources}
        self.assertTrue(self.controller.play_monopoly(self.p1, 'wood'))
        self.p1.add_resource.assert_not_called()

        for resource in self.board_context.RESOURCES:
            self.p1.has_dev_card.return_value = True
            self.assertTrue(self.controller.play_monopoly(self.p1, resource))

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards(self):
        """Fails cleanly on bad turn, no card, already played, unrolled dice, or bad resource."""
        # 1. Not player's turn
        self.assertFalse(self.controller.play_monopoly(self.p2, 'wood'))
        
        # 2. No monopoly card
        self.p1.has_dev_card.return_value = False
        self.assertFalse(self.controller.play_monopoly(self.p1, 'wood'))
        self.p1.has_dev_card.return_value = True # reset
        
        # 3. Already played a dev card this turn
        self.tm.played_dev_card = True
        self.assertFalse(self.controller.play_monopoly(self.p1, 'wood'))
        self.tm.played_dev_card = False # reset
        
        # 4. Dice not rolled
        self.tm.dice_rolled = False
        self.assertFalse(self.controller.play_monopoly(self.p1, 'wood'))
        self.tm.dice_rolled = True # reset
        
        # 5. Invalid resource
        self.assertFalse(self.controller.play_monopoly(self.p1, 'gold'))
        
        # Verify no resources were moved and card was not consumed
        self.p1.add_resource.assert_not_called()
        self.p1.remove_dev_card.assert_not_called()


if __name__ == '__main__':
    unittest.main()