import unittest
from unittest.mock import MagicMock
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestDistributeResources(BaseControllerTest):
    """
    Unit tests for GameController._distribute_resources().
    """
    def setUp(self):
        super().setUp()
        self.controller.players = MagicMock()
        self.controller.players.__iter__.return_value = [self.p1, self.p2]

    def _make_tile(self, tile_id, resource, number, vertices, robber=False):
        """Wires a tile and its vertices into the mocked board[cite: 6]."""
        tile = MagicMock()
        tile.tile_id = tile_id
        tile.resource = resource
        tile.number = number
        self.board.tiles = {tile_id: tile}
        self.board.tile_vertices = {tile_id: vertices}
        if robber:
            self.board.robber_placement = tile_id
        return tile

    # -------------------------------------------------------------------------
    # PRODUCTION RULES
    # -------------------------------------------------------------------------

    def test_roll_seven_no_production(self):
        """Roll of 7 always returns False and never distributes resources"""
        self._make_tile(1, 'wood', 7, [5])
        self.board.get_structure.return_value = ('settlement', 'red')
        
        result = self.controller._distribute_resources(7)
        
        self.assertTrue(result)
        self.p1.add_resource.assert_not_called()

    def test_robber_blocks_production(self):
        """Structures on a tile with the robber do not receive resources."""
        self._make_tile(1, 'wood', 8, [5], robber=True)
        self.board.get_structure.return_value = ('settlement', 'red')
        self.board.bank_has_resource.return_value = True
        
        result = self.controller._distribute_resources(8)
        
        self.assertTrue(result)
        self.p1.add_resource.assert_not_called()

    def test_production_settlement_and_city(self):
        """Settlements produce 1, Cities produce 2, and the bank is debited."""
        self._make_tile(1, 'ore', 6, [5, 10])
        # Vertex 5 has a settlement (red/p1), Vertex 10 has a city (blue/p2)
        self.board.get_structure.side_effect = lambda v: {
            5: ('settlement', 'red'),
            10: ('city', 'blue'),
        }.get(v, (None, None))
        self.board.bank_has_resource.return_value = True
        self.board.get_tile_vertices.return_value = [5 , 10]
        
        result = self.controller._distribute_resources(6)
        
        self.assertTrue(result)
        self.p1.add_resource.assert_called_once_with('ore', 1)
        self.p2.add_resource.assert_called_once_with('ore', 2)
        self.board.remove_bank_resource.assert_any_call('ore', 1)
        self.board.remove_bank_resource.assert_any_call('ore', 2)

    # -------------------------------------------------------------------------
    # BANK DEPLETION
    # -------------------------------------------------------------------------

    def test_bank_depleted_nobody_receives(self):
        """If bank cannot cover total demand, NO player receives."""
        self._make_tile(1, 'brick', 5, [3])
        self.board.get_structure.return_value = ('settlement', 'red')
        self.board.bank_has_resource.return_value = False
        
        result = self.controller._distribute_resources(5)
        
        self.assertTrue(result)
        self.p1.add_resource.assert_not_called()
        self.board.remove_bank_resource.assert_not_called()

    # -------------------------------------------------------------------------
    # NO YIELD SCENARIOS
    # -------------------------------------------------------------------------

    def test_no_yield_scenarios(self):
        """Desert tiles, empty vertices, or unmatched rolls yield nothing."""
        self._make_tile(1, 'desert', 8, [5])
        self.board.get_structure.return_value = ('settlement', 'red')
        self.board.bank_has_resource.return_value = True
        
        # Test desert
        self.controller._distribute_resources(8)
        # Test unmatched roll
        self.controller._distribute_resources(4)
        # Test empty vertices (override mock)
        self.board.get_structure.return_value = (None, None)
        self.controller._distribute_resources(8)
        
        self.p1.add_resource.assert_not_called()


if __name__ == '__main__':
    unittest.main()