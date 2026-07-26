import unittest
from unittest.mock import MagicMock, patch
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestRollDice(BaseControllerTest):
    """
    Unit tests for GameController.roll_dice().
    """

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_rolls_and_distributes(self):
        """Successfully rolls dice, flags turn manager, and distributes resources."""
        with patch('random.randint', side_effect=[3, 4]):
            with patch.object(self.controller, '_distribute_resources') as mock_dist:
                result = self.controller.roll_dice(self.p1)
                
                self.assertEqual(result, (3, 4))
                self.tm.set_dice_rolled.assert_called_once()
                mock_dist.assert_called_once_with(7)

    def test_success_die_values_in_valid_range(self):
        """Each individual die value must be between 1 and 6 inclusive."""
        for _ in range(20):
            self.tm.dice_rolled = False
            result = self.controller.roll_dice(self.p1)
            
            if result != (0, 0):
                self.assertGreaterEqual(result[0], 1)
                self.assertLessEqual(result[0], 6)
                self.assertGreaterEqual(result[1], 1)
                self.assertLessEqual(result[1], 6)

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_not_turn(self):
        """Fails cleanly without mutating state if it is not the player's turn."""
        with patch.object(self.controller, '_distribute_resources') as mock_dist:
            result = self.controller.roll_dice(self.p2)
            
            self.assertEqual(result, (0, 0))
            mock_dist.assert_not_called()
            self.tm.set_dice_rolled.assert_not_called()

    def test_fails_dice_already_rolled(self):
        """Cannot roll twice in the same turn."""
        self.tm.dice_rolled = True
        
        with patch.object(self.controller, '_distribute_resources') as mock_dist:
            result = self.controller.roll_dice(self.p1)
            
            self.assertEqual(result, (0, 0))
            mock_dist.assert_not_called()


if __name__ == '__main__':
    unittest.main()