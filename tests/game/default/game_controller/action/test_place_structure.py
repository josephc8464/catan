import pytest
from ..conftest import GameSetup, assert_not_paid, assert_paid
from game.player import Player

SETTLEMENT = 'settlement'

# Target vertex for structure placement
V1 = 0
# Connected vertex for road requirement
V2 = 1
# Neighboring vertex for distance rule checks
V_ADJ = 3


@pytest.fixture
def settlement_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for placing a settlement during normal play:
    - Player 1 has exact settlement resources
    - Player 1 has a connecting road at edge (V1, V2)
    - Dice have been rolled
    """
    cost = game.context.get_cost(SETTLEMENT)
    game.p1.add_resources(cost)

    # Synchronize connecting road on both board graph and player model
    game.board.add_road(V1, V2, game.p1.color)
    game.p1.add_road(V1, V2)

    game.tm.set_dice_rolled()
    return game


def _assert_settlement_unchanged(game: GameSetup, player: Player, result: bool, vertex: int) -> None:
    """Asserts that placing a settlement failed and state remains untouched."""
    assert result is False
    assert (vertex, game.context.STRUCTURE_TYPES[0]) not in player.structures
    struct_type, _ = game.board.get_structure(vertex)
    assert struct_type is None


def _assert_settlement_changed(game: GameSetup, player: Player, result: bool, vertex: int) -> None:
    """Asserts that placing a settlement succeeded and state was updated."""
    assert result is True
    assert (vertex, game.context.STRUCTURE_TYPES[0]) in player.structures
    struct_type, owner_color = game.board.get_structure(vertex)
    assert struct_type == SETTLEMENT
    assert owner_color == player.color


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_normal_play_returns_true(settlement_game: GameSetup):
    """Normal settlement placement succeeds with connected road, resources, and dice rolled."""
    start_res = settlement_game.p1.resources.copy()

    result = settlement_game.controller.place_structure(V1, settlement_game.p1)

    _assert_settlement_changed(settlement_game, settlement_game.p1, result, V1)
    assert_paid(settlement_game, settlement_game.p1, start_res, SETTLEMENT)

def test_success_init_setup_returns_true_when_cant_afford(game: GameSetup):
    """init_setup=True succeeds even when player has 0 resources."""
    game.p1.resources = {r: 0 for r in game.context.RESOURCES}
    start_res = game.p1.resources.copy()

    result = game.controller.place_structure(V1, game.p1, init_setup=True)

    _assert_settlement_changed(game, game.p1, result, V1)
    assert_not_paid(game.p1, start_res)


def test_success_init_setup_returns_true_when_not_roll_dice(game: GameSetup):
    """init_setup=True succeeds even when dice have not been rolled."""
    game.tm.dice_rolled = False
    start_res = game.p1.resources.copy()

    result = game.controller.place_structure(V1, game.p1, init_setup=True)

    _assert_settlement_changed(game, game.p1, result, V1)
    assert_not_paid(game.p1, start_res)

def test_success_init_setup_returns_true(game: GameSetup):
    """init_setup=True succeeds without resources, road connectivity, or rolled dice."""
    start_res = game.p1.resources.copy()

    result = game.controller.place_structure(V1, game.p1, init_setup=True)

    _assert_settlement_changed(game, game.p1, result, V1)
    assert_not_paid(game.p1, start_res)


# =========================================================================
# FAILURE CASES (NORMAL PLAY)
# =========================================================================

def test_fails_not_turn(settlement_game: GameSetup):
    """Placing a settlement fails if it is not the player's turn."""
    cost = settlement_game.context.get_cost(SETTLEMENT)
    settlement_game.p2.add_resources(cost)
    settlement_game.board.add_road(V1, V2, settlement_game.p2.color)
    settlement_game.p2.add_road(V1, V2)
    start_res = settlement_game.p2.resources.copy()

    result = settlement_game.controller.place_structure(V1, settlement_game.p2)

    _assert_settlement_unchanged(settlement_game, settlement_game.p2, result, V1)
    assert_not_paid(settlement_game.p2, start_res)


def test_fails_not_roll_dice(settlement_game: GameSetup):
    """Normal settlement build fails if dice have not been rolled yet this turn."""
    start_res = settlement_game.p1.resources.copy()
    settlement_game.tm.dice_rolled = False

    result = settlement_game.controller.place_structure(V1, settlement_game.p1)

    _assert_settlement_unchanged(settlement_game, settlement_game.p1, result, V1)
    assert_not_paid(settlement_game.p1, start_res)


def test_fails_cant_afford_normal_play(settlement_game: GameSetup):
    """Normal settlement build fails if player lacks necessary resources."""
    settlement_game.p1.resources = {r: 0 for r in settlement_game.context.RESOURCES}
    start_res = settlement_game.p1.resources.copy()

    result = settlement_game.controller.place_structure(V1, settlement_game.p1)

    _assert_settlement_unchanged(settlement_game, settlement_game.p1, result, V1)
    assert_not_paid(settlement_game.p1, start_res)


def test_fails_max_settlements_reached(settlement_game: GameSetup):
    """Fails if player has already placed all allowed settlements (e.g. 5)."""
    start_res = settlement_game.p1.resources.copy()
    for i in range(5):
        settlement_game.p1.add_structure(100 + i, SETTLEMENT)

    result = settlement_game.controller.place_structure(V1, settlement_game.p1)

    _assert_settlement_unchanged(settlement_game, settlement_game.p1, result, V1)
    assert_not_paid(settlement_game.p1, start_res)
    assert len(settlement_game.p1.structures) == 5


def test_fails_vertex_occupied(settlement_game: GameSetup):
    """Fails if the vertex already contains another structure."""
    start_res = settlement_game.p1.resources.copy()
    settlement_game.board.add_structure(V1, settlement_game.p2.color, SETTLEMENT)
    settlement_game.p2.add_structure(V1, SETTLEMENT)

    result = settlement_game.controller.place_structure(V1, settlement_game.p1)

    assert result is False
    assert (V1, settlement_game.context.STRUCTURE_TYPES[0]) not in settlement_game.p1.structures
    assert_not_paid(settlement_game.p1, start_res)

def test_fails_distance_rule_normal_play(settlement_game: GameSetup):
    """Fails if an adjacent vertex has a structure (distance rule violation)."""
    start_res = settlement_game.p1.resources.copy()
    settlement_game.board.add_structure(V_ADJ, settlement_game.p2.color, SETTLEMENT)
    settlement_game.p2.add_structure(V_ADJ, SETTLEMENT)

    result = settlement_game.controller.place_structure(V1, settlement_game.p1)

    _assert_settlement_unchanged(settlement_game, settlement_game.p1, result, V1)
    assert_not_paid(settlement_game.p1, start_res)


def test_fails_no_road_connection_normal_play(game: GameSetup):
    """Normal settlement build fails if player has no connecting road network."""
    cost = game.context.get_cost(SETTLEMENT)
    game.p1.add_resources(cost)
    game.tm.set_dice_rolled()
    start_res = game.p1.resources.copy()

    result = game.controller.place_structure(V1, game.p1)

    _assert_settlement_unchanged(game, game.p1, result, V1)
    assert_not_paid(game.p1, start_res)


# =========================================================================
# FAILURE CASES (INIT SETUP)
# =========================================================================

def test_fails_distance_rule_init_setup(game: GameSetup):
    """Distance rule is strictly enforced even during initial setup phase."""
    game.board.add_structure(V_ADJ, game.p2.color, SETTLEMENT)
    game.p2.add_structure(V_ADJ, SETTLEMENT)
    start_res = game.p1.resources.copy()

    result = game.controller.place_structure(V1, game.p1, init_setup=True)

    _assert_settlement_unchanged(game, game.p1, result, V1)
    assert_not_paid(game.p1, start_res)