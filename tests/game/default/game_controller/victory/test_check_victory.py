import unittest
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestCheckVictory(BaseControllerTest):
    """
    Unit tests for GameController.check_victory().
    """

    def setUp(self):
        super().setUp()
        self.p1.local_vp.return_value = 0
        self.board.longest_road = None
        self.board.largest_army = None

    # -------------------------------------------------------------------------
    # SUCCESS SCENARIOS
    # -------------------------------------------------------------------------

    def test_success_victory_conditions(self):
        """Player wins if their local VP plus their awards meets or exceeds the threshold."""
        # Exactly 10 VP (no awards)
        self.p1.local_vp.return_value = 10
        self.assertTrue(self.controller.check_victory(self.p1))

        # Exceeds threshold
        self.p1.local_vp.return_value = 13
        self.assertTrue(self.controller.check_victory(self.p1))

        # Longest Road only (8 VP + 2 VP award = 10 VP)
        self.p1.local_vp.return_value = 8
        self.board.longest_road = self.p1.color
        self.assertTrue(self.controller.check_victory(self.p1))

        # Both awards (6 VP + 2 VP + 2 VP = 10 VP)
        self.board.largest_army = self.p1.color
        self.p1.local_vp.return_value = 6
        self.assertTrue(self.controller.check_victory(self.p1))

    # -------------------------------------------------------------------------
    # FAILURE SCENARIOS
    # -------------------------------------------------------------------------

    def test_fails_below_threshold(self):
        """Player does not win if they are below the threshold, even with opponents' awards."""
        # Zero VP
        self.p1.local_vp.return_value = 0
        self.assertFalse(self.controller.check_victory(self.p1))

        # One below threshold (9 VP)
        self.p1.local_vp.return_value = 9
        self.assertFalse(self.controller.check_victory(self.p1))

        # 9 VP, but the awards belong to an opponent
        self.board.longest_road = self.p2.color
        self.board.largest_army = self.p2.color
        self.assertFalse(self.controller.check_victory(self.p1))

    # -------------------------------------------------------------------------
    # DYNAMIC CONTEXT
    # -------------------------------------------------------------------------

    def test_dynamic_board_context_values(self):
        """Victory calculation correctly references the board context for thresholds and awards."""
        awards = self.board_context.AWARDS
        threshold = self.board_context.WINNING_VP_THRESHOLD
        
        # Set local VP to exactly the amount needed when adding both awards
        self.p1.local_vp.return_value = threshold - sum(awards.values())
        self.board.longest_road = self.p1.color
        self.board.largest_army = self.p1.color
        
        self.assertTrue(self.controller.check_victory(self.p1))


if __name__ == '__main__':
    unittest.main()