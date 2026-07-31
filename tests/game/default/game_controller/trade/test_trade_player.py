import pytest
from tests.game.default.game_controller.conftest import GameSetup


@pytest.fixture
def player_trade_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for player-to-player domestic trading:
    - Player 1 has 2 wood to offer
    - Player 2 has 1 ore to give back
    - Dice have been rolled
    """
    game.p1.add_resource('wood', 2)
    game.p2.add_resource('ore', 1)

    game.tm.set_dice_rolled()
    return game


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_domestic_trade(player_trade_game: GameSetup):
    """Successfully executes a resource trade between two players."""
    offer = {'wood': 2}
    request = {'ore': 1}

    result = player_trade_game.controller.trade_player(
        player_trade_game.p1, player_trade_game.p2, offer, request
    )

    assert result is True
    # Player 1 gives wood, gains ore
    assert player_trade_game.p1.resources['wood'] == 0
    assert player_trade_game.p1.resources['ore'] == 1
    # Player 2 gives ore, gains wood
    assert player_trade_game.p2.resources['ore'] == 0
    assert player_trade_game.p2.resources['wood'] == 2


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(player_trade_game: GameSetup):
    """Domestic trade fails if is neither player's turn."""
    offer = {'ore': 1}
    request = {'wood': 2}

    p3_start = player_trade_game.p3.resources.copy()
    p2_start = player_trade_game.p2.resources.copy()

    result = player_trade_game.controller.trade_player(
        player_trade_game.p2, player_trade_game.p3, offer, request
    )

    assert result is False
    assert player_trade_game.p3.resources == p3_start
    assert player_trade_game.p2.resources == p2_start


def test_fails_not_roll_dice(player_trade_game: GameSetup):
    """Domestic trade fails if dice have not been rolled yet this turn."""
    player_trade_game.tm.dice_rolled = False
    offer = {'wood': 2}
    request = {'ore': 1}

    p1_start = player_trade_game.p1.resources.copy()
    p2_start = player_trade_game.p2.resources.copy()

    result = player_trade_game.controller.trade_player(
        player_trade_game.p1, player_trade_game.p2, offer, request
    )

    assert result is False
    assert player_trade_game.p1.resources == p1_start
    assert player_trade_game.p2.resources == p2_start


def test_fails_active_player_lacks_offered_resources(player_trade_game: GameSetup):
    """Domestic trade fails if active player lacks the resources offered."""
    offer = {'wood': 5}
    request = {'ore': 1}

    p1_start = player_trade_game.p1.resources.copy()
    p2_start = player_trade_game.p2.resources.copy()

    result = player_trade_game.controller.trade_player(
        player_trade_game.p1, player_trade_game.p2, offer, request
    )

    assert result is False
    assert player_trade_game.p1.resources == p1_start
    assert player_trade_game.p2.resources == p2_start


def test_fails_target_player_lacks_requested_resources(player_trade_game: GameSetup):
    """Domestic trade fails if target player lacks the requested resources."""
    offer = {'wood': 2}
    request = {'ore': 3}

    p1_start = player_trade_game.p1.resources.copy()
    p2_start = player_trade_game.p2.resources.copy()

    result = player_trade_game.controller.trade_player(
        player_trade_game.p1, player_trade_game.p2, offer, request
    )

    assert result is False
    assert player_trade_game.p1.resources == p1_start
    assert player_trade_game.p2.resources == p2_start


def test_fails_self_trade(player_trade_game: GameSetup):
    """Player cannot trade resources with themselves."""
    offer = {'wood': 2}
    request = {'wood': 1}

    p1_start = player_trade_game.p1.resources.copy()

    result = player_trade_game.controller.trade_player(
        player_trade_game.p1, player_trade_game.p1, offer, request
    )

    assert result is False
    assert player_trade_game.p1.resources == p1_start