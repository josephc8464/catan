import unittest
from unittest.mock import MagicMock, call
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestPlayYearOfPlenty(BaseControllerTest):
    """
    Unit tests for GameController.play_year_of_plenty().
    """

    def setUp(self):
        super().setUp()
        self.tm.dice_rolled = True
        self.board.bank_has_resource.return_value = True

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_grants_two_resources(self):
        """Successfully grants 2 resources to player before debiting bank, then consumes card."""
        # Use a mock manager to strictly enforce exact sequence of calls
        manager = MagicMock()
        manager.attach_mock(self.p1.add_resource, 'add')
        manager.attach_mock(self.board.remove_bank_resource, 'remove')

        self.assertTrue(self.controller.play_year_of_plenty(self.p1, 'wood', 'ore'))

        # Verify additions happened BEFORE removals
        manager.assert_has_calls([
            call.add('wood', 1),
            call.add('ore', 1),
            call.remove('wood', 1),
            call.remove('ore', 1)
        ])
        
        self.p1.remove_dev_card.assert_called_once_with('year_of_plenty')
        self.tm.set_played_dev_card.assert_called_once()

    def test_success_same_resource_twice(self):
        """Requesting the same resource twice succeeds if the bank has at least 2."""
        self.assertTrue(self.controller.play_year_of_plenty(self.p1, 'ore', 'ore'))

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards(self):
        """Fails cleanly on bad turn, no card, played flag, unrolled dice, invalid res, or empty bank."""
        self.assertFalse(self.controller.play_year_of_plenty(self.p2, 'wood', 'ore'))
        
        self.p1.has_dev_card.return_value = False
        self.assertFalse(self.controller.play_year_of_plenty(self.p1, 'wood', 'ore'))
        self.p1.has_dev_card.return_value = True
        
        self.tm.played_dev_card = True
        self.assertFalse(self.controller.play_year_of_plenty(self.p1, 'wood', 'ore'))
        self.tm.played_dev_card = False
        
        self.tm.dice_rolled = False
        self.assertFalse(self.controller.play_year_of_plenty(self.p1, 'wood', 'ore'))
        self.tm.dice_rolled = True
        
        self.assertFalse(self.controller.play_year_of_plenty(self.p1, 'gold', 'ore'))
        
        self.board.bank_has_resource.return_value = False
        self.assertFalse(self.controller.play_year_of_plenty(self.p1, 'wood', 'ore'))

        # If requesting same twice, bank needs 2. Return False if amount checked > 1
        self.board.bank_has_resource.side_effect = lambda r, a: a <= 1
        self.assertFalse(self.controller.play_year_of_plenty(self.p1, 'ore', 'ore'))
        
        # Verify no mutations occurred during failures
        self.p1.add_resource.assert_not_called()
        self.p1.remove_dev_card.assert_not_called()


if __name__ == '__main__':
    unittest.main()