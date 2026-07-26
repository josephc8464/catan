import unittest
from unittest.mock import patch
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestPlayRoadBuilding(BaseControllerTest):
    """
    Unit tests for GameController.play_road_building().
    """

    def setUp(self):
        super().setUp()
        self.tm.dice_rolled = True
        self.p1.count_roads.return_value = 10
        self.v1, self.v2, self.v3, self.v4 = 1, 2, 3, 4

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_places_two_roads(self):
        """Successfully places two free roads, consumes card, and sets flag."""
        with patch.object(self.controller, 'build_road', return_value=True) as mock_build:
            self.assertTrue(self.controller.play_road_building(self.p1, self.v1, self.v2, self.v3, self.v4))

            print("\nACTUAL CALLS:", mock_build.call_args_list)

            self.assertEqual(mock_build.call_count, 2)
            mock_build.assert_any_call(self.v1, self.v2, self.p1, free=True)
            mock_build.assert_any_call(self.v3, self.v4, self.p1, free=True)
            
        self.p1.remove_dev_card.assert_called_once_with('road_building')
        self.tm.set_played_dev_card.assert_called_once()

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards(self):
        """Fails cleanly on bad turn, no card, already played, unrolled dice, or piece counts[cite: 10]."""
        with patch.object(self.controller, 'build_road') as mock_build:
            self.assertFalse(self.controller.play_road_building(self.p2, self.v1, self.v2, self.v3, self.v4))
            
            self.p1.has_dev_card.return_value = False
            self.assertFalse(self.controller.play_road_building(self.p1, self.v1, self.v2, self.v3, self.v4))
            self.p1.has_dev_card.return_value = True 
            
            self.tm.played_dev_card = True
            self.assertFalse(self.controller.play_road_building(self.p1, self.v1, self.v2, self.v3, self.v4))
            self.tm.played_dev_card = False 
            
            self.tm.dice_rolled = False
            self.assertFalse(self.controller.play_road_building(self.p1, self.v1, self.v2, self.v3, self.v4))
            self.tm.dice_rolled = True 
            
            self.p1.count_roads.return_value = 14 # Only room for 1
            self.assertFalse(self.controller.play_road_building(self.p1, self.v1, self.v2, self.v3, self.v4))
            
            mock_build.assert_not_called()
            
        self.p1.remove_dev_card.assert_not_called()

    # -------------------------------------------------------------------------
    # ATOMIC ROLLBACK
    # -------------------------------------------------------------------------

    def test_fails_and_rolls_back_first_road(self):
        """If the second road fails, the first road is completely rolled back[cite: 10]."""
        self.p1.roads = [(self.v1, self.v2)]
        
        with patch.object(self.controller, 'build_road', side_effect=[True, False]):
            self.assertFalse(self.controller.play_road_building(self.p1, self.v1, self.v2, self.v3, self.v4))
            
        # Verify Rollback
        self.board.graph.clear_edge_color.assert_called_once_with(self.v1, self.v2)
        self.assertNotIn((self.v1, self.v2), self.p1.roads)
        self.p1.remove_dev_card.assert_not_called()


if __name__ == '__main__':
    unittest.main()