import pytest
from ..conftest import GameSetup, assert_not_paid
from game.player import Player

SETTLEMENT = 'settlement'

# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_grants_resources_from_adjacent_tiles(game: GameSetup):
    """Places Round 2 setup settlement and grants exactly 1 resource per adjacent producing tile."""
    # Find a non-desert tile and one of its vertices
    tile_id = next(tid for tid, t in game.board.tiles.items() if t.resource != 'desert')
    tile = game.board.tiles[tile_id]
    vertex = game.board.tile_vertices[tile_id][0]

    start_amount = game.p1.resources[tile.resource]

    result = game.controller.place_initial_settlement_r2(game.p1, vertex)

    assert result is True
    assert (vertex, game.context.STRUCTURE_TYPES[0]) in game.p1.structures
    assert game.p1.resources[tile.resource] > start_amount


def test_success_no_resources_granted_from_desert_or_empty_bank(game: GameSetup):
    """Desert tiles and depleted bank resources yield no bonus starting resources."""
    tile_id = next(tid for tid, t in game.board.tiles.items() if t.resource != 'desert')
    tile = game.board.tiles[tile_id]
    vertex = game.board.tile_vertices[tile_id][0]

    # Empty the bank for this resource type
    game.board.bank[tile.resource] = 0
    start_res = game.p1.resources.copy()

    result = game.controller.place_initial_settlement_r2(game.p1, vertex)

    assert result is True
    assert (vertex, game.context.STRUCTURE_TYPES[0]) in game.p1.structures
    assert game.p1.resources == start_res


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(game: GameSetup):
    """Round 2 initial settlement placement fails if it is not the active player's turn."""
    vertex = 10
    start_res = game.p2.resources.copy()

    result = game.controller.place_initial_settlement_r2(game.p2, vertex)

    assert result is False
    assert (vertex, game.context.STRUCTURE_TYPES[0]) not in game.p2.structures
    assert game.p2.resources == start_res


def test_fails_distance_rule(game: GameSetup):
    """Round 2 placement fails without granting resources if distance rule is violated."""
    vertex = 10
    v_adj = 5
    game.board.add_structure(v_adj, game.p2.color, SETTLEMENT)
    game.p2.add_structure(v_adj, SETTLEMENT)

    start_res = game.p1.resources.copy()

    result = game.controller.place_initial_settlement_r2(game.p1, vertex)

    assert result is False
    assert (vertex, game.context.STRUCTURE_TYPES[0]) not in game.p1.structures
    assert game.p1.resources == start_res