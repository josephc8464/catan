import pytest
from ..conftest import GameSetup, assert_not_paid
from game.player import Player

SETTLEMENT = 'settlement'

V1 = 5
V_ADJ = 4


def _assert_initial_settlement_unchanged(game: GameSetup, player: Player, result: bool, vertex: int) -> None:
    """Asserts that placing an initial settlement failed and state remains untouched."""
    assert result is False
    assert (vertex, game.context.STRUCTURE_TYPES[0]) not in player.structures
    struct_type, _ = game.board.get_structure(vertex)
    assert struct_type is None


def _assert_initial_settlement_changed(game: GameSetup, player: Player, result: bool, vertex: int) -> None:
    """Asserts that placing an initial settlement succeeded and state was updated."""
    assert result is True
    assert (vertex, game.context.STRUCTURE_TYPES[0]) in player.structures
    struct_type, owner_color = game.board.get_structure(vertex)
    assert struct_type == SETTLEMENT
    assert owner_color == player.color


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_places_initial_settlement(game: GameSetup):
    """Places a free initial settlement on an empty, valid vertex."""
    start_res = game.p1.resources.copy()

    result = game.controller.place_initial_settlement(game.p1, V1)

    _assert_initial_settlement_changed(game, game.p1, result, V1)
    assert_not_paid(game.p1, start_res)


@pytest.mark.parametrize("vertex", [0, 53])
def test_success_boundary_vertices(game: GameSetup, vertex: int):
    """Validates boundary vertex extremes on standard board graph."""
    start_res = game.p1.resources.copy()

    result = game.controller.place_initial_settlement(game.p1, vertex)

    _assert_initial_settlement_changed(game, game.p1, result, vertex)
    assert_not_paid(game.p1, start_res)


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(game: GameSetup):
    """Initial settlement placement fails if it is not the player's turn."""
    start_res = game.p2.resources.copy()

    result = game.controller.place_initial_settlement(game.p2, V1)

    _assert_initial_settlement_unchanged(game, game.p2, result, V1)
    assert_not_paid(game.p2, start_res)


def test_fails_vertex_occupied(game: GameSetup):
    """Fails if target vertex already contains a structure."""
    game.board.add_structure(V1, game.p2.color, SETTLEMENT)
    game.p2.add_structure(V1, SETTLEMENT)
    start_res = game.p1.resources.copy()

    result = game.controller.place_initial_settlement(game.p1, V1)

    assert result is False
    assert V1 not in game.p1.structures
    assert_not_paid(game.p1, start_res)


def test_fails_distance_rule(game: GameSetup):
    """Fails if an adjacent vertex has a structure (distance rule violation)."""
    game.board.add_structure(V_ADJ, game.p2.color, SETTLEMENT)
    game.p2.add_structure(V_ADJ, SETTLEMENT)
    start_res = game.p1.resources.copy()

    result = game.controller.place_initial_settlement(game.p1, V1)

    _assert_initial_settlement_unchanged(game, game.p1, result, V1)
    assert_not_paid(game.p1, start_res)