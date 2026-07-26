import unittest
from unittest.mock import MagicMock
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestUpgradeStructure(BaseControllerTest):
    """
    Unit tests for GameController.upgrade_structure().
    """

    def setUp(self):
        super().setUp()
        self.vertex = 10
        self.city_cost = self.board_context.get_cost('city')
        self.board.get_structure.return_value = ('settlement', self.p1.color)
        self.tm.dice_rolled = True

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_upgrades_structure(self):
        """Successfully upgrades a settlement to a city and mutates all states."""
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        
        self.assertTrue(result)
        self.board.add_structure.assert_called_once_with(self.vertex, self.p1.color, 'city')
        self.p1.remove_structure.assert_called_once_with(self.vertex)
        self.p1.add_structure.assert_called_once_with(self.vertex, 'city')
        self.p1.remove_resources.assert_called_once_with(self.city_cost)

    # -------------------------------------------------------------------------
    # FAIL VALIDATIONS
    # -------------------------------------------------------------------------

    def test_fails_not_turn(self):
        """Must fail if it is not the player's turn, without mutating state."""
        result = self.controller.upgrade_structure(self.vertex, self.p2)
        
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()
        self.p2.remove_resources.assert_not_called()

    def test_fails_not_roll_dice(self):
        """Must fail if the dice haven't been rolled yet."""
        self.tm.dice_rolled = False
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()
        self.p1.remove_resources.assert_not_called()

    def test_fails_cant_afford(self):
        """Must fail if the player cannot afford the upgrade."""
        self.p1.can_afford.return_value = False
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    def test_fails_max_cities_reached(self):
        """HAS_PIECES: Must fail and leave board unmutated if the city limit is reached."""
        self.p1.has_available_pieces.return_value = False
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    # -------------------------------------------------------------------------
    # FAIL BOARD STATE & OWNERSHIP
    # -------------------------------------------------------------------------

    def test_fails_wrong_owner(self):
        """Player cannot upgrade an opponent's structure."""
        self.board.get_structure.return_value = ('settlement', self.p2.color)
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        
        self.assertFalse(result)
        self.p1.can_afford.assert_not_called()
        self.board.add_structure.assert_not_called()

    def test_fails_no_structure_at_vertex(self):
        """Must fail if the vertex is empty."""
        self.board.get_structure.return_value = (None, None)
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        self.assertFalse(result)

    def test_fails_already_fully_upgraded(self):
        """Must fail if the structure is already at max tier (city)."""
        self.board.get_structure.return_value = ('city', self.p1.color)
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    # -------------------------------------------------------------------------
    # FAIL CONTEXT ERRORS
    # -------------------------------------------------------------------------

    def test_fails_missing_cost(self):
        """Must fail cleanly if the board context returns None for the cost."""
        self.controller.board_context.get_cost = MagicMock(return_value=None)
        result = self.controller.upgrade_structure(self.vertex, self.p1)
        
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()


if __name__ == '__main__':
    unittest.main()