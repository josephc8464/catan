from ..conftest import GameSetup

# =========================================================================
# PRODUCTION RULES
# =========================================================================

def test_roll_seven_no_production(game: GameSetup):
    """Roll of 7 executes without distributing resource yields to any player."""
    p1_start_res = game.p1.resources.copy()
    p2_start_res = game.p2.resources.copy()

    result = game.controller._distribute_resources(7)

    assert result is False
    assert game.p1.resources == p1_start_res
    assert game.p2.resources == p2_start_res


def test_robber_blocks_production(game: GameSetup):
    """Structures located on the tile containing the robber yield no resources."""
    tile_id = 1
    tile = game.board.tiles[tile_id]
    
    if tile.resource == 'desert':
        tile_id = 2
        tile = game.board.tiles[tile_id]

    vertex = game.board.tile_vertices[tile_id][0]
    
    # Setup settlement and move robber to tile
    game.board.add_structure(vertex, game.p1.color, 'settlement')
    game.p1.add_structure(vertex, 'settlement')
    game.board.robber_placement = tile_id

    start_res = game.p1.resources.copy()

    # Trigger distribution on tile's number
    result = game.controller._distribute_resources(tile.number)

    assert result is True
    assert game.p1.resources == start_res


def test_production_settlement_and_city(game: GameSetup):
    """Settlements produce 1 resource unit and Cities produce 2 resource units."""
    # Find a non-desert tile
    tile_id = next(tid for tid, t in game.board.tiles.items() if t.resource != 'desert')
    tile = game.board.tiles[tile_id]
    vertices = game.board.tile_vertices[tile_id]

    v1, v2 = vertices[0], vertices[1]

    # Vertex 1 has a settlement (Player 1), Vertex 2 has a city (Player 2)
    game.board.add_structure(v1, game.p1.color, 'settlement')
    game.p1.add_structure(v1, 'settlement')

    game.board.add_structure(v2, game.p2.color, 'city')
    game.p2.add_structure(v2, 'city')

    # Ensure robber is not on this tile
    game.board.robber_placement = -1

    p1_start = game.p1.resources[tile.resource]
    p2_start = game.p2.resources[tile.resource]

    result = game.controller._distribute_resources(tile.number)

    assert result is True
    assert game.p1.resources[tile.resource] == p1_start + 1
    assert game.p2.resources[tile.resource] == p2_start + 2


# =========================================================================
# BANK DEPLETION
# =========================================================================

def test_bank_depleted_nobody_receives(game: GameSetup):
    """If bank cannot fulfill total production demand, no player receives resources."""
    tile_id = next(tid for tid, t in game.board.tiles.items() if t.resource != 'desert')
    tile = game.board.tiles[tile_id]
    vertex = game.board.tile_vertices[tile_id][0]

    game.board.add_structure(vertex, game.p1.color, 'settlement')
    game.p1.add_structure(vertex, 'settlement')
    game.board.robber_placement = -1

    # Empty bank reserves for this resource
    game.board.bank[tile.resource] = 0
    start_res = game.p1.resources.copy()

    result = game.controller._distribute_resources(tile.number)

    assert result is True
    assert game.p1.resources == start_res


# =========================================================================
# NO YIELD SCENARIOS
# =========================================================================

def test_no_yield_scenarios(game: GameSetup):
    """Desert tiles, unbuilt vertices, or non-matching rolls yield no resources."""
    p1_start_res = game.p1.resources.copy()

    # Roll that matches no producing tiles or empty board state
    result = game.controller._distribute_resources(2)

    assert result is True
    assert game.p1.resources == p1_start_res