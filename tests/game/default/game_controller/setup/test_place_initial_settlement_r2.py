import unittest
from unittest.mock import MagicMock
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestPlaceInitialSettlementR2(BaseControllerTest):
    """
    Unit tests for GameController.place_initial_settlement_r2().
    """

    def setUp(self):
        super().setUp()
        self.vertex = 10
        self.board.get_structure.return_value = (None, None)
        self.board.has_structure_neighbor.return_value = False
        self.board.bank_has_resource.return_value = True

    def _make_tile(self, tile_id, resource, number, vertices):
        """Helper: wires a tile into board.tiles and board.tile_vertices."""
        tile = MagicMock()
        tile.tile_id = tile_id
        tile.resource = resource
        tile.number = number
        return tile

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_grants_resources_from_adjacent_tiles(self):
        """Places settlement and grants exactly 1 resource per adjacent producing tile."""
        tile1 = self._make_tile(1, 'wood', 8, [self.vertex, 11, 12])
        tile2 = self._make_tile(2, 'ore', 5, [self.vertex])
        
        self.board.tiles = {1: tile1, 2: tile2}
        self.board.tile_vertices = {1: [self.vertex, 11, 12], 2: [self.vertex]}

        result = self.controller.place_initial_settlement_r2(self.p1, self.vertex)
        
        self.assertTrue(result)
        self.p1.add_resource.assert_any_call('wood', 1)
        self.p1.add_resource.assert_any_call('ore', 1)
        self.board.remove_bank_resource.assert_any_call('wood', 1)
        self.board.remove_bank_resource.assert_any_call('ore', 1)

    def test_success_no_resources_granted_from_desert_or_empty_bank(self):
        """Desert tiles and depleted bank resources yield nothing."""
        tile1 = self._make_tile(1, 'desert', None, [self.vertex])
        tile2 = self._make_tile(2, 'wheat', 5, [self.vertex])
        
        self.board.tiles = {1: tile1, 2: tile2}
        self.board.tile_vertices = {1: [self.vertex], 2: [self.vertex]}
        self.board.bank_has_resource.return_value = False  # Bank is empty
        
        result = self.controller.place_initial_settlement_r2(self.p1, self.vertex)
        
        self.assertTrue(result)
        self.p1.add_resource.assert_not_called()
        self.board.remove_bank_resource.assert_not_called()

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_guards_no_resources_granted(self):
        """Fails cleanly without distributing resources on bad turn or distance rules."""
        tile1 = self._make_tile(1, 'wood', 6, [self.vertex])
        self.board.tiles = {1: tile1}
        self.board.tile_vertices = {1: [self.vertex]}
        
        # 1. Not player's turn
        self.assertFalse(self.controller.place_initial_settlement_r2(self.p2, self.vertex))
        
        # 2. Occupancy/Distance rule violated
        self.board.has_structure_neighbor.return_value = True
        self.assertFalse(self.controller.place_initial_settlement_r2(self.p1, self.vertex))
        
        # Ensure no resources were falsely granted during failures
        self.p1.add_resource.assert_not_called()
        self.p2.add_resource.assert_not_called()


if __name__ == '__main__':
    unittest.main()