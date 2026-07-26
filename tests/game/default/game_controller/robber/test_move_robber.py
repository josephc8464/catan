import unittest
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestMoveRobber(BaseControllerTest):
    """
    Unit tests for GameController.move_robber().
    """

    def setUp(self):
        super().setUp()
        self.board.robber_placement = 0

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_moves_robber_to_new_tile(self):
        """Moving to any different valid tile updates placement and returns True."""
        result = self.controller.move_robber(5)
        
        self.assertTrue(result)
        self.assertEqual(self.board.robber_placement, 5)

        # Boundary check for max standard tile ID
        result_max = self.controller.move_robber(18)
        self.assertTrue(result_max)
        self.assertEqual(self.board.robber_placement, 18)

    # -------------------------------------------------------------------------
    # FAIL
    # -------------------------------------------------------------------------

    def test_fails_same_tile(self):
        """Robber must be moved to a DIFFERENT tile; state remains unchanged."""
        self.board.robber_placement = 3
        result = self.controller.move_robber(3)
        
        self.assertFalse(result)
        self.assertEqual(self.board.robber_placement, 3)


if __name__ == '__main__':
    unittest.main()