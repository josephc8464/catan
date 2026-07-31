import pytest
from tests.game.default.game_controller.conftest import GameSetup

# Port vertex edge configuration
V1, V2 = 0, 1


@pytest.fixture
def port_trade_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for port trading:
    - Player 1 has 3 wood
    - Player 1 owns a settlement on port vertex V1
    - Dice have been rolled
    """
    game.p1.resources = {r: 0 for r in game.context.RESOURCES}
    game.p1.add_resource('wood', 3)

    game.board.add_structure(V1, game.p1.color, 'settlement')
    game.p1.add_structure(V1, 'settlement')

    game.tm.set_dice_rolled()
    return game


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_trade_generic_port_3_to_1(port_trade_game: GameSetup):
    """Successfully trades 3 units of a resource for 1 unit via generic 3:1 port."""
    # Configure board to have generic port on edge (V1, V2)
    port_trade_game.board.ports[(V1, V2)] = 'any'

    result = port_trade_game.controller.trade_port(
        port_trade_game.p1, (V1, V2), 'wood', 'ore'
    )

    assert result is True
    assert port_trade_game.p1.resources['wood'] == 0
    assert port_trade_game.p1.resources['ore'] == 1


def test_success_trade_special_port_2_to_1(port_trade_game: GameSetup):
    """Successfully trades 2 units of a resource for 1 unit via specialized 2:1 port."""
    # Configure board to have specialized wood port on edge (V1, V2)
    port_trade_game.board.ports[(V1, V2)] = 'wood'

    result = port_trade_game.controller.trade_port(
        port_trade_game.p1, (V1, V2), 'wood', 'ore'
    )

    assert result is True
    # Only 2 wood spent instead of 3
    assert port_trade_game.p1.resources['wood'] == 1
    assert port_trade_game.p1.resources['ore'] == 1


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(port_trade_game: GameSetup):
    """Port trade fails if it is not the active player's turn."""
    port_trade_game.board.ports[(V1, V2)] = 'any'
    port_trade_game.p2.resources = {r: 0 for r in port_trade_game.context.RESOURCES}
    port_trade_game.p2.add_resource('wood', 3)
    port_trade_game.board.add_structure(V1, port_trade_game.p2.color, 'settlement')
    port_trade_game.p2.add_structure(V1, 'settlement')

    p2_start = port_trade_game.p2.resources.copy()

    result = port_trade_game.controller.trade_port(
        port_trade_game.p2, (V1, V2), 'wood', 'ore'
    )

    assert result is False
    assert port_trade_game.p2.resources == p2_start


def test_fails_not_roll_dice(port_trade_game: GameSetup):
    """Port trade fails if dice have not been rolled yet this turn."""
    port_trade_game.board.ports[(V1, V2)] = 'any'
    port_trade_game.tm.dice_rolled = False
    start_res = port_trade_game.p1.resources.copy()

    result = port_trade_game.controller.trade_port(
        port_trade_game.p1, (V1, V2), 'wood', 'ore'
    )

    assert result is False
    assert port_trade_game.p1.resources == start_res


def test_fails_insufficient_player_resources(port_trade_game: GameSetup):
    """Port trade fails if player lacks required trade ratio resources (e.g. 2 wood on 3:1 port)."""
    port_trade_game.board.ports[(V1, V2)] = 'any'
    port_trade_game.p1.resources['wood'] = 2
    start_res = port_trade_game.p1.resources.copy()

    result = port_trade_game.controller.trade_port(
        port_trade_game.p1, (V1, V2), 'wood', 'ore'
    )

    assert result is False
    assert port_trade_game.p1.resources == start_res


def test_fails_bank_empty(port_trade_game: GameSetup):
    """Port trade fails if the bank is depleted of requested resource."""
    port_trade_game.board.ports[(V1, V2)] = 'any'
    port_trade_game.board.bank['ore'] = 0
    start_res = port_trade_game.p1.resources.copy()

    result = port_trade_game.controller.trade_port(
        port_trade_game.p1, (V1, V2), 'wood', 'ore'
    )

    assert result is False
    assert port_trade_game.p1.resources == start_res


def test_fails_no_port_access(port_trade_game: GameSetup):
    """Port trade fails if the player has no structure built at the specified port location."""
    port_trade_game.board.ports[(V1, V2)] = 'any'
    
    # Remove player structure from port vertex
    port_trade_game.p1.structures.clear()
    port_trade_game.board.remove_structure(V1)
    start_res = port_trade_game.p1.resources.copy()

    result = port_trade_game.controller.trade_port(
        port_trade_game.p1, (V1, V2), 'wood', 'ore'
    )

    assert result is False
    assert port_trade_game.p1.resources == start_res