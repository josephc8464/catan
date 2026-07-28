import pytest
from ..conftest import GameSetup, assert_not_paid, assert_paid
from game.player import Player

# Vertices to build target road
V1, V2 = 0, 1

# Vertices of existing network
V3, V4 = 0, 3

ROAD = 'road'

@pytest.fixture
def road_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for road building:
    - Player 1 has 1 wood and 1 brick
    - Player 1 has a settlement at V1 and a road at (V3, V4)
    - Dice have been rolled
    """
    game.p1.add_resources({'wood': 1, 'brick': 1})

    # Synchronize both Board and Player state
    game.board.add_structure(V1, game.p1.color, game.context.STRUCTURE_TYPES[0])
    game.p1.add_structure(V1, game.context.STRUCTURE_TYPES[0])

    game.board.add_road(V3, V4, game.p1.color)
    game.p1.add_road(V3, V4)
    
    game.tm.set_dice_rolled()

    return game

def _assert_road_unchanged(road_game: GameSetup, og_road_color: str | None, player: Player, result: bool) -> None:
    """Asserts that building a road failed and state remains untouched."""
    assert result is False
    assert (V1, V2) not in player.roads
    assert road_game.board.graph.get_edge_color(V1, V2) == og_road_color

def _assert_road_changed(road_game: GameSetup, player: Player, result: bool) -> None:
    """Asserts that building a road succeeded and state was updated."""
    assert result is True
    assert (V1, V2) in player.roads
    assert road_game.board.graph.get_edge_color(V1, V2) == player.color

# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_paid_returns_true(road_game: GameSetup):
    """Paid road build succeeds with connected network, resources, and dice rolled."""
    start_res = road_game.p1.resources.copy()
    result = road_game.controller.build_road(V1, V2, road_game.p1, free=False)

    _assert_road_changed(road_game, road_game.p1, result)
    assert_paid(road_game, road_game.p1, start_res, ROAD)

def test_success_free_returns_true_when_cant_afford(road_game: GameSetup):
    """free=True succeeds even when player has 0 resources."""
    road_game.p1.resources = {'wood': 0, 'brick': 0}
    start_res = road_game.p1.resources.copy()
    
    result = road_game.controller.build_road(V1, V2, road_game.p1, free=True)

    _assert_road_changed(road_game, road_game.p1, result)
    assert_not_paid(road_game.p1, start_res)

def test_success_free_returns_true_when_not_roll_dice(road_game: GameSetup):
    """free=True succeeds even when player hasn't rolled dice (e.g., setup phase)."""
    start_res = road_game.p1.resources.copy()
    road_game.tm.dice_rolled = False

    result = road_game.controller.build_road(V1, V2, road_game.p1, free=True)

    _assert_road_changed(road_game, road_game.p1, result)
    assert_not_paid(road_game.p1, start_res)

def _get_road_color(road_game: GameSetup) -> str | None:
    return road_game.board.graph.get_edge_color(V1, V2)

# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(road_game: GameSetup):
    """Building a road fails if it is not the player's turn."""
    start_res = road_game.p2.resources.copy()
    og_color = _get_road_color(road_game)
    result = road_game.controller.build_road(V1, V2, road_game.p2)

    _assert_road_unchanged(road_game, og_color, road_game.p2, result)
    assert_not_paid(road_game.p2, start_res)
    assert len(road_game.p2.roads) == 0

def test_fails_not_roll_dice(road_game: GameSetup):
    """Paid road build fails if dice have not been rolled yet this turn."""
    start_res = road_game.p1.resources.copy()
    og_color = _get_road_color(road_game)
    road_game.tm.dice_rolled = False

    result = road_game.controller.build_road(V1, V2, road_game.p1, free=False)

    _assert_road_unchanged(road_game, og_color, road_game.p1, result)
    assert_not_paid(road_game.p1, start_res)

def test_fails_cant_afford(road_game: GameSetup):
    """Paid road build fails if player lacks necessary resources."""
    road_game.p1.resources = {'wood': 0, 'brick': 0}
    og_color = _get_road_color(road_game)
    start_res = road_game.p1.resources.copy()

    result = road_game.controller.build_road(V1, V2, road_game.p1, free=False)

    _assert_road_unchanged(road_game, og_color, road_game.p1, result)
    assert_not_paid(road_game.p1, start_res)

def test_fails_max_pieces_reached(road_game: GameSetup):
    """Fails if player has already placed all 15 allowed roads."""
    start_res = road_game.p1.resources.copy()
    og_color = _get_road_color(road_game)
    for i in range(14):
        road_game.p1.add_road(100 + i, 200 + i)

    result = road_game.controller.build_road(V1, V2, road_game.p1)

    _assert_road_unchanged(road_game, og_color, road_game.p1, result)
    assert_not_paid(road_game.p1, start_res)
    assert len(road_game.p1.roads) == 15

def test_fails_road_occupied(road_game: GameSetup):
    """Fails if the edge already has an opponent's road on it."""
    start_res = road_game.p1.resources.copy()
    road_game.p2.add_road(V1, V2)
    road_game.board.add_road(V1, V2, road_game.p2.color)
    og_color = _get_road_color(road_game)
    
    result = road_game.controller.build_road(V1, V2, road_game.p1)

    _assert_road_unchanged(road_game, og_color, road_game.p1, result)
    assert_not_paid(road_game.p1, start_res)

def test_fails_no_connection(game: GameSetup):
    """Fails if road does not connect to player's existing network."""
    game.p1.add_resources({'wood': 1, 'brick': 1})
    game.tm.set_dice_rolled()
    start_res = game.p1.resources.copy()
    og_color = _get_road_color(game)

    result = game.controller.build_road(V1, V2, game.p1)

    _assert_road_unchanged(game, og_color, game.p1, result)
    assert_not_paid(game.p1, start_res)