import unittest
from unittest.mock import patch, MagicMock
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestPlaceStructure(BaseControllerTest):
    """
    Unit tests for GameController.place_structure().
    """

    def setUp(self):
        super().setUp()
        self.vertex = 5
        self.settlement_cost = self.board_context.get_cost('settlement')
        
        self.board.get_structure.return_value = (None, None)
        self.board.has_structure_neighbor.return_value = False
        self.board.has_road_neighbor.return_value = True
        self.tm.dice_rolled = True

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_normal_play_returns_true(self):
        result = self.controller.place_structure(self.vertex, self.p1)
        
        self.assertTrue(result)
        self.board.add_structure.assert_called_once_with(self.vertex, self.p1.color, 'settlement')
        self.p1.add_structure.assert_called_once_with(self.vertex, 'settlement')
        self.p1.remove_resources.assert_called_once_with(self.settlement_cost)

    def test_success_init_setup_returns_true(self):
        """init_setup=True successfully skips resource and road connectivity checks."""
        self.p1.can_afford.return_value = False
        self.board.has_road_neighbor.return_value = False
        
        result = self.controller.place_structure(self.vertex, self.p1, init_setup=True)
        
        self.assertTrue(result)
        self.board.add_structure.assert_called_once_with(self.vertex, self.p1.color, 'settlement')
        self.p1.remove_resources.assert_not_called()
        self.board.has_road_neighbor.assert_not_called()

    # -------------------------------------------------------------------------
    # FAIL NORMAL PLAY
    # -------------------------------------------------------------------------

    def test_fails_not_turn(self):
        result = self.controller.place_structure(self.vertex, self.p2)
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    def test_fails_not_roll_dice(self):
        """Must fail if the dice haven't been rolled during normal play."""
        self.tm.dice_rolled = False
        result = self.controller.place_structure(self.vertex, self.p1)
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    def test_fails_cant_afford_normal_play(self):
        self.p1.can_afford.return_value = False
        result = self.controller.place_structure(self.vertex, self.p1)
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    def test_fails_max_settlements_reached(self):
        """HAS_PIECES: Must fail and leave board unmutated if piece limit is reached."""
        self.p1.has_available_pieces.return_value = False
        result = self.controller.place_structure(self.vertex, self.p1)
        
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    def test_fails_vertex_occupied(self):
        self.board.get_structure.return_value = ('settlement', 'blue')
        result = self.controller.place_structure(self.vertex, self.p1)
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    def test_fails_distance_rule_normal_play(self):
        self.board.has_structure_neighbor.return_value = True
        result = self.controller.place_structure(self.vertex, self.p1)
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    def test_fails_no_road_connection_normal_play(self):
        self.board.has_road_neighbor.return_value = False
        result = self.controller.place_structure(self.vertex, self.p1)
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()
    
    # -------------------------------------------------------------------------
    # FAIL INIT SETUP
    # -------------------------------------------------------------------------

    def test_fails_distance_rule_init_setup(self):
        """Distance rule is ALWAYS enforced, even during setup."""
        self.board.has_structure_neighbor.return_value = True
        result = self.controller.place_structure(self.vertex, self.p1, init_setup=True)
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()

    # -------------------------------------------------------------------------
    # FAIL CONTEXT ERRORS
    # -------------------------------------------------------------------------

    def test_fails_missing_starting_building(self):
        """Must fail if the board context is missing the starting building type."""
        with patch.object(self.controller.board_context, 'STRUCTURE_TYPES', [None]):
            result = self.controller.place_structure(self.vertex, self.p1)
            self.assertFalse(result)
            self.board.add_structure.assert_not_called()
        

    def test_fails_missing_cost(self):
        """Must fail if the board context returns None for the building cost."""
        self.controller.board_context.get_cost = MagicMock(return_value=None)
        
        result = self.controller.place_structure(self.vertex, self.p1)
        self.assertFalse(result)
        self.board.add_structure.assert_not_called()


if __name__ == '__main__':
    unittest.main()