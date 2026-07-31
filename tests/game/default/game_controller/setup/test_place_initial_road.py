import pytest
from ..conftest import GameSetup, assert_not_paid
from game.player import Player

# Target road vertices
V1, V2 = 0, 1
# Older settlement vertex
V_OLD = 6
# Unconnected vertex pair
V_OTHER1, V_OTHER2 = 8, 9


@pytest.fixture
def initial_road_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for initial road placement:
    - Player 1 has placed a settlement at V1
    """
    game.board.add_structure(V1, game.p1.color, 'settlement')
    game.p1.add_structure(V1, 'settlement')
    return game


def _assert_initial_road_unchanged(game: GameSetup, player: Player, result: bool) -> None:
    """Asserts that initial road placement failed and state remains untouched."""
    assert result is False
    assert (V1, V2) not in player.roads
    assert game.board.graph.get_edge_color(V1, V2) is None


def _assert_initial_road_changed(game: GameSetup, player: Player, result: bool) -> None:
    """Asserts that initial road placement succeeded and state was updated."""
    assert result is True
    assert (V1, V2) in player.roads
    assert game.board.graph.get_edge_color(V1, V2) == player.color


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_places_initial_road(initial_road_game: GameSetup):
    """Places road connected to the most recently placed settlement for free."""
    # Add an older settlement to ensure it connects to the LAST settlement specifically
    initial_road_game.p1.add_structure(V_OLD, 'settlement')
    initial_road_game.p1.add_structure(V1, 'settlement')
    start_res = initial_road_game.p1.resources.copy()

    result = initial_road_game.controller.place_initial_road(initial_road_game.p1, V1, V2)

    _assert_initial_road_changed(initial_road_game, initial_road_game.p1, result)
    assert_not_paid(initial_road_game.p1, start_res)


def test_success_connects_via_vertex2(game: GameSetup):
    """Road can connect to the last settlement via vertex2 instead of vertex1."""
    game.board.add_structure(V2, game.p1.color, 'settlement')
    game.p1.add_structure(V2, 'settlement')
    start_res = game.p1.resources.copy()

    result = game.controller.place_initial_road(game.p1, V1, V2)

    _assert_initial_road_changed(game, game.p1, result)
    assert_not_paid(game.p1, start_res)


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(initial_road_game: GameSetup):
    """Initial road placement fails if it is not the active player's turn."""
    initial_road_game.board.add_structure(V1, initial_road_game.p2.color, 'settlement')
    initial_road_game.p2.add_structure(V1, 'settlement')
    start_res = initial_road_game.p2.resources.copy()

    result = initial_road_game.controller.place_initial_road(initial_road_game.p2, V1, V2)

    _assert_initial_road_unchanged(initial_road_game, initial_road_game.p2, result)
    assert_not_paid(initial_road_game.p2, start_res)


def test_fails_no_settlement_placed(game: GameSetup):
    """Initial road placement fails if player has not placed any settlement yet."""
    start_res = game.p1.resources.copy()

    result = game.controller.place_initial_road(game.p1, V1, V2)

    _assert_initial_road_unchanged(game, game.p1, result)
    assert_not_paid(game.p1, start_res)


def test_fails_no_connection_to_last_settlement(initial_road_game: GameSetup):
    """Fails if the road does not connect to the player's last placed settlement."""
    start_res = initial_road_game.p1.resources.copy()

    result = initial_road_game.controller.place_initial_road(initial_road_game.p1, V_OTHER1, V_OTHER2)

    assert result is False
    assert (V_OTHER1, V_OTHER2) not in initial_road_game.p1.roads
    assert_not_paid(initial_road_game.p1, start_res)


def test_fails_connects_to_first_settlement_instead_of_last(game: GameSetup):
    """Fails if road connects to an earlier settlement instead of the MOST RECENT settlement."""
    game.board.add_structure(V_OLD, game.p1.color, 'settlement')
    game.p1.add_structure(V_OLD, 'settlement')

    game.board.add_structure(V1, game.p1.color, 'settlement')
    game.p1.add_structure(V1, 'settlement')

    start_res = game.p1.resources.copy()

    # Attempt to build off V_OLD (first settlement) instead of V1 (last settlement)
    result = game.controller.place_initial_road(game.p1, V_OLD, V2)

    assert result is False
    assert (V_OLD, V2) not in game.p1.roads
    assert_not_paid(game.p1, start_res)


def test_fails_edge_occupied(initial_road_game: GameSetup):
    """Fails if the target edge already contains a road."""
    initial_road_game.board.add_road(V1, V2, initial_road_game.p2.color)
    initial_road_game.p2.add_road(V1, V2)
    start_res = initial_road_game.p1.resources.copy()

    result = initial_road_game.controller.place_initial_road(initial_road_game.p1, V1, V2)

    assert result is False
    assert (V1, V2) not in initial_road_game.p1.roads
    assert initial_road_game.board.graph.get_edge_color(V1, V2) == initial_road_game.p2.color
    assert_not_paid(initial_road_game.p1, start_res)