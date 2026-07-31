import pytest
from tests.game.default.game_controller.conftest import GameSetup

GIVE_RES = 'wood'
GET_RES = 'ore'


@pytest.fixture
def bank_trade_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for standard 4:1 bank trading:
    - Player 1 has 4 wood
    - Dice have been rolled
    - Bank has available ore
    """
    game.p1.resources = {r: 0 for r in game.context.RESOURCES}
    game.p1.add_resource(GIVE_RES, 4)
    game.tm.set_dice_rolled()
    return game


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_trade_bank_4_to_1(bank_trade_game: GameSetup):
    """Successfully trades 4 units of a resource for 1 unit of another with the bank."""
    p1_give_start = bank_trade_game.p1.resources[GIVE_RES]
    p1_get_start = bank_trade_game.p1.resources[GET_RES]
    bank_give_start = bank_trade_game.board.bank[GIVE_RES]
    bank_get_start = bank_trade_game.board.bank[GET_RES]

    result = bank_trade_game.controller.trade_bank(bank_trade_game.p1, GIVE_RES, GET_RES)

    assert result is True
    assert bank_trade_game.p1.resources[GIVE_RES] == p1_give_start - 4
    assert bank_trade_game.p1.resources[GET_RES] == p1_get_start + 1
    assert bank_trade_game.board.bank[GIVE_RES] == bank_give_start + 4
    assert bank_trade_game.board.bank[GET_RES] == bank_get_start - 1


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(bank_trade_game: GameSetup):
    """Bank trade fails if it is not the player's turn."""
    bank_trade_game.p2.resources = {r: 0 for r in bank_trade_game.context.RESOURCES}
    bank_trade_game.p2.add_resource(GIVE_RES, 4)

    start_res = bank_trade_game.p2.resources.copy()

    result = bank_trade_game.controller.trade_bank(bank_trade_game.p2, GIVE_RES, GET_RES)

    assert result is False
    assert bank_trade_game.p2.resources == start_res


def test_fails_not_roll_dice(bank_trade_game: GameSetup):
    """Bank trade fails if dice have not been rolled yet this turn."""
    bank_trade_game.tm.dice_rolled = False
    start_res = bank_trade_game.p1.resources.copy()

    result = bank_trade_game.controller.trade_bank(bank_trade_game.p1, GIVE_RES, GET_RES)

    assert result is False
    assert bank_trade_game.p1.resources == start_res


def test_fails_insufficient_player_resources(bank_trade_game: GameSetup):
    """Bank trade fails if player has fewer than 4 of the offered resource."""
    bank_trade_game.p1.resources[GIVE_RES] = 3
    start_res = bank_trade_game.p1.resources.copy()

    result = bank_trade_game.controller.trade_bank(bank_trade_game.p1, GIVE_RES, GET_RES)

    assert result is False
    assert bank_trade_game.p1.resources == start_res


def test_fails_bank_empty(bank_trade_game: GameSetup):
    """Bank trade fails if the bank is out of the requested resource."""
    bank_trade_game.board.bank[GET_RES] = 0
    start_res = bank_trade_game.p1.resources.copy()

    result = bank_trade_game.controller.trade_bank(bank_trade_game.p1, GIVE_RES, GET_RES)

    assert result is False
    assert bank_trade_game.p1.resources == start_res