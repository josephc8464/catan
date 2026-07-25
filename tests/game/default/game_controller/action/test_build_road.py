import unittest
from unittest.mock import MagicMock
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestBuildRoad(BaseControllerTest):
    """
    Unit tests for GameController.build_road().
    """

    def setUp(self):
        super().setUp()
        self.v1 = 5
        self.v2 = 6
        self.p1.roads = []
        self.road_cost = self.board_context.get_cost('road')
        self.tm.dice_rolled = True
        self.board.has_edge.return_value = True
        self.board.get_road_color.return_value = None
        self.board.has_connected_neighbor.return_value = True
        

    # -------------------------------------------------------------------------
    # SUCCESS PAID
    # -------------------------------------------------------------------------

    def test_success_paid_returns_true(self):
        result = self.controller.build_road(self.v1, self.v2, self.p1, free=False)
        self.assertTrue(result)

        self.board.add_road.assert_called_once_with(self.v1, self.v2, self.p1.color)
        self.p1.remove_resources.assert_called_once_with(self.road_cost)
        self.p1.add_road.assert_called_once()

    # -------------------------------------------------------------------------
    # SUCCESS FREE
    # -------------------------------------------------------------------------

    def test_success_free_returns_true_when_cant_afford(self):
        """free=True succeeds even when player cannot afford."""
        self.p1.can_afford.return_value = False
        result = self.controller.build_road(self.v1, self.v2, self.p1, free=True)
        self.assertTrue(result)

        self.board.add_road.assert_called_once_with(self.v1, self.v2, self.p1.color)
        self.p1.remove_resources.assert_not_called()
        self.p1.can_afford.assert_not_called()
        self.p1.add_road.assert_called_once()

    def test_success_free_returns_true_when_not_roll_dice(self):
        """free=True succeeds even when player hasn't rolled dice."""
        self.tm.dice_rolled = False
        result = self.controller.build_road(self.v1, self.v2, self.p1, free=True)
        self.assertTrue(result)
        
        self.board.add_road.assert_called_once_with(self.v1, self.v2, self.p1.color)
        self.p1.remove_resources.assert_not_called()
        self.p1.can_afford.assert_not_called()
        self.p1.add_road.assert_called_once()

    # -------------------------------------------------------------------------
    # FAIL PAID
    # -------------------------------------------------------------------------

    def test_fails_not_turn(self):
        result = self.controller.build_road(self.v1, self.v2, self.p2)
        self.assertFalse(result)
        self.board.add_road.assert_not_called()
        self.p2.remove_resources.assert_not_called()

    def test_fails_not_roll_dice(self):
        self.tm.dice_rolled = False
        result = self.controller.build_road(self.v1, self.v2, self.p1)
        self.assertFalse(result)
        self.board.add_road.assert_not_called()
        self.p2.remove_resources.assert_not_called()
    
    def test_fails_cant_afford(self):
        self.p1.can_afford.return_value = False
        result = self.controller.build_road(self.v1, self.v2, self.p1, free=False)
        self.assertFalse(result)
        self.board.add_road.assert_not_called()
        self.p2.remove_resources.assert_not_called()

    def test_fails_max_pieces_reached(self):
        """HAS_PIECES: player has placed all 15 roads."""
        self.p1.has_available_pieces.return_value = False
        result = self.controller.build_road(self.v1, self.v2, self.p1)
        self.assertFalse(result)
        self.board.add_road.assert_not_called()

    # -------------------------------------------------------------------------
    # FAIL EDGE CHECKS (PAID)
    # -------------------------------------------------------------------------
    def test_fails_cost_not_found(self):
        """Purchase must fail if the cost lookup returns None."""
        self.controller.board_context.get_cost = MagicMock(return_value=None)
        result = self.controller.build_road(self.v1, self.v2, self.p1)
        
        self.assertFalse(result)
        self.p1.remove_resources.assert_not_called()
        self.p1.add_dev_card.assert_not_called()
        
    def test_fails_edge_not_exist(self):
        self.board.has_edge.return_value = False
        result = self.controller.build_road(self.v1, self.v2, self.p1)
        self.assertFalse(result)

    def test_fails_edge_occupied_by_opponent(self):
        self.board.get_road_color.return_value = 'blue'
        result = self.controller.build_road(self.v1, self.v2, self.p1)
        self.assertFalse(result)

    def test_fails_edge_occupied_by_own_color(self):
        """Cannot place a second road on your own existing road."""
        self.board.get_road_color.return_value = self.p1.color
        result = self.controller.build_road(self.v1, self.v2, self.p1)
        self.assertFalse(result)

    def test_fails_no_connection(self):
        """Road must connect to player's own network."""
        self.board.has_connected_neighbor.return_value = False
        result = self.controller.build_road(self.v1, self.v2, self.p1)
        self.assertFalse(result)
        self.board.add_road.assert_not_called()


if __name__ == '__main__':
    unittest.main()