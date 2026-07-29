import pytest
from ..conftest import GameSetup, assert_not_paid, assert_paid
from game.player import Player

CITY = 'city'
SETTLEMENT = 'settlement'


# Target vertex for upgrading
V1 = 10
# Vertex without any structure
V_EMPTY = 0


@pytest.fixture
def upgrade_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for upgrading a settlement to a city:
    - Player 1 has exact city resources
    - Player 1 owns a settlement at vertex V1
    - Dice have been rolled
    """
    cost = game.context.get_cost(CITY)
    game.p1.add_resources(cost)

    # Synchronize settlement placement across board graph and player model
    game.board.add_structure(V1, game.p1.color, SETTLEMENT)
    game.p1.add_structure(V1, SETTLEMENT)

    game.tm.set_dice_rolled()
    return game


def _assert_city_unchanged(game: GameSetup, player: Player, result: bool, vertex: int) -> None:
    """Asserts that upgrading a structure failed and state remains untouched."""
    assert result is False
    assert (vertex, game.context.STRUCTURE_TYPES[1]) not in player.structures

def _assert_city_changed(game: GameSetup, player: Player, result: bool, vertex: int) -> None:
    """Asserts that upgrading to a city succeeded and state was updated."""
    assert result is True
    assert (vertex, game.context.STRUCTURE_TYPES[1]) in player.structures
    assert (vertex, game.context.STRUCTURE_TYPES[0]) not in player.structures
    struct_type, owner_color = game.board.get_structure(vertex)
    assert struct_type == CITY
    assert owner_color == player.color


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_upgrades_structure(upgrade_game: GameSetup):
    """Successfully upgrades a settlement to a city and mutates all states."""
    start_res = upgrade_game.p1.resources.copy()

    result = upgrade_game.controller.upgrade_structure(V1, upgrade_game.p1)

    _assert_city_changed(upgrade_game, upgrade_game.p1, result, V1)
    assert_paid(upgrade_game, upgrade_game.p1, start_res, CITY)


# =========================================================================
# FAILURE CASES (VALIDATIONS)
# =========================================================================

def test_fails_not_turn(upgrade_game: GameSetup):
    """Upgrading fails if it is not the player's turn."""
    cost = upgrade_game.context.get_cost(CITY)
    upgrade_game.p2.add_resources(cost)
    start_res = upgrade_game.p2.resources.copy()

    result = upgrade_game.controller.upgrade_structure(V1, upgrade_game.p2)

    _assert_city_unchanged(upgrade_game, upgrade_game.p2, result, V1)
    assert_not_paid(upgrade_game.p2, start_res)


def test_fails_not_roll_dice(upgrade_game: GameSetup):
    """Upgrading fails if dice have not been rolled yet this turn."""
    start_res = upgrade_game.p1.resources.copy()
    upgrade_game.tm.dice_rolled = False

    result = upgrade_game.controller.upgrade_structure(V1, upgrade_game.p1)

    _assert_city_unchanged(upgrade_game, upgrade_game.p1, result, V1)
    assert_not_paid(upgrade_game.p1, start_res)


def test_fails_cant_afford(upgrade_game: GameSetup):
    """Upgrading fails if player lacks necessary resources."""
    upgrade_game.p1.resources = {r: 0 for r in upgrade_game.context.RESOURCES}
    start_res = upgrade_game.p1.resources.copy()

    result = upgrade_game.controller.upgrade_structure(V1, upgrade_game.p1)

    _assert_city_unchanged(upgrade_game, upgrade_game.p1, result, V1)
    assert_not_paid(upgrade_game.p1, start_res)


def test_fails_max_cities_reached(upgrade_game: GameSetup):
    """Fails if player has already placed all allowed cities (e.g. 4)."""
    start_res = upgrade_game.p1.resources.copy()
    for i in range(4):
        upgrade_game.p1.add_structure(100 + i, CITY)

    result = upgrade_game.controller.upgrade_structure(V1, upgrade_game.p1)

    _assert_city_unchanged(upgrade_game, upgrade_game.p1, result, V1)
    assert_not_paid(upgrade_game.p1, start_res)
    assert upgrade_game.p1.count_structure(CITY) == upgrade_game.context.get_max_pieces(CITY)


# =========================================================================
# FAILURE CASES (BOARD STATE & OWNERSHIP)
# =========================================================================

def test_fails_wrong_owner(upgrade_game: GameSetup):
    """Player cannot upgrade an opponent's settlement."""
    V2 = 20
    upgrade_game.board.add_structure(V2, upgrade_game.p2.color, SETTLEMENT)
    upgrade_game.p2.add_structure(V2, SETTLEMENT)
    start_res = upgrade_game.p1.resources.copy()

    result = upgrade_game.controller.upgrade_structure(V2, upgrade_game.p1)

    _assert_city_unchanged(upgrade_game, upgrade_game.p1, result, V2)
    assert_not_paid(upgrade_game.p1, start_res)


def test_fails_no_structure_at_vertex(upgrade_game: GameSetup):
    """Must fail if the target vertex is empty."""
    start_res = upgrade_game.p1.resources.copy()

    result = upgrade_game.controller.upgrade_structure(V_EMPTY, upgrade_game.p1)

    _assert_city_unchanged(upgrade_game, upgrade_game.p1, result, V_EMPTY)
    assert_not_paid(upgrade_game.p1, start_res)


def test_fails_already_fully_upgraded(upgrade_game: GameSetup):
    """Must fail if the structure is already at max tier (city)."""
    start_res = upgrade_game.p1.resources.copy()

    # Pre-upgrade the settlement at V1 to a city
    upgrade_game.p1.remove_structure(V1)
    upgrade_game.board.add_structure(V1, upgrade_game.p1.color, CITY)
    upgrade_game.p1.add_structure(V1, CITY)

    result = upgrade_game.controller.upgrade_structure(V1, upgrade_game.p1)

    assert result is False
    assert_not_paid(upgrade_game.p1, start_res)