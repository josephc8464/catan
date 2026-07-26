import unittest
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestPlaceInitialSettlement(BaseControllerTest):
    """
    Unit tests for GameController.place_initial_settlement().
    """

    def setUp(self):
        super().setUp()
        self.vertex = 5
        self.board.get_structure.return_value = (None, None)
        self.board.has_structure_neighbor.return_value = False

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_places_initial_settlement(self):
        """Places a free initial settlement on an empty, valid vertex."""
        self.p1.structures = []
        
        result = self.controller.place_initial_settlement(self.p1, self.vertex)
        
        self.assertTrue(result)
        self.board.add_structure.assert_called_once_with(self.vertex, self.p1.color, 'settlement')
        self.assertIn((self.vertex, 'settlement'), self.p1.structures)
        self.p1.remove_resources.assert_not_called()

    def test_success_boundary_vertices(self):
        """Validates standard board boundary vertex extremes."""
        self.assertTrue(self.controller.place_initial_settlement(self.p1, 0))
        self.assertTrue(self.controller.place_initial_settlement(self.p1, 53))

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards(self):
        """Fails cleanly on bad turn, vertex occupancy, or distance rule violations."""
        # 1. Not player's turn
        self.assertFalse(self.controller.place_initial_settlement(self.p2, self.vertex))
        
        # 2. Vertex occupied (settlement or city)
        self.board.get_structure.return_value = ('settlement', 'blue')
        self.assertFalse(self.controller.place_initial_settlement(self.p1, self.vertex))
        
        # 3. Distance rule violated (neighboring structure exists)
        self.board.get_structure.return_value = (None, None)
        self.board.has_structure_neighbor.return_value = True
        self.assertFalse(self.controller.place_initial_settlement(self.p1, self.vertex))
        
        # Verify board was never mutated during any failure
        self.board.add_structure.assert_not_called()


if __name__ == '__main__':
    unittest.main()