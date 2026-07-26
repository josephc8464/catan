import unittest
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestPlaceInitialRoad(BaseControllerTest):
    """
    Unit tests for GameController.place_initial_road().
    """

    def setUp(self):
        super().setUp()
        self.v1 = 5
        self.v2 = 6
        self.p1.structures = [(self.v1, 'settlement')]
        self.p1.roads = []
        self.board.get_road_color.return_value = None

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_places_initial_road(self):
        """Places road connected to the last settlement for free."""
        # Add a dummy older settlement to ensure it connects to the LAST one specifically
        self.p1.structures = [(3, 'settlement'), (self.v1, 'settlement')]
        
        result = self.controller.place_initial_road(self.p1, self.v1, self.v2)
        
        self.assertTrue(result)
        self.board.add_road.assert_called_once_with(self.v1, self.v2, self.p1.color)
        self.assertIn((self.v1, self.v2), self.p1.roads)
        self.p1.remove_resources.assert_not_called()
        
    def test_success_connects_via_vertex2(self):
        """Road can connect to the last settlement via vertex2 instead of vertex1."""
        self.p1.structures = [(self.v2, 'settlement')]
        self.assertTrue(self.controller.place_initial_road(self.p1, self.v1, self.v2))

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards(self):
        """Placement fails cleanly on bad turn, no settlement, invalid connection, or occupied edge."""
        # 1. Not player's turn
        self.p2.structures = [(self.v1, 'settlement')]
        self.assertFalse(self.controller.place_initial_road(self.p2, self.v1, self.v2))
        
        # 2. No settlement placed yet
        self.p1.structures = []
        self.assertFalse(self.controller.place_initial_road(self.p1, self.v1, self.v2))
        
        # 3. Valid settlement exists, but road doesn't connect to it
        self.p1.structures = [(self.v1, 'settlement')]
        self.assertFalse(self.controller.place_initial_road(self.p1, 7, 8))
        
        # 4. Valid settlement exists, but connects to the FIRST one, not the LAST
        self.p1.structures = [(3, 'settlement'), (self.v1, 'settlement')]
        self.assertFalse(self.controller.place_initial_road(self.p1, 3, 4))
        
        # 5. Edge already occupied
        self.board.get_road_color.return_value = 'blue'
        self.assertFalse(self.controller.place_initial_road(self.p1, self.v1, self.v2))
        
        # Verify board was never mutated during any failure
        self.board.add_road.assert_not_called()


if __name__ == '__main__':
    unittest.main()