import pytest
from tests.game.default.game_controller.conftest import GameSetup


@pytest.fixture
def yop_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for playing a Year of Plenty card:
    - Player 1 has 'year_of_plenty' in active_dev_cards
    - Dice have been rolled
    - Player has not played a dev card yet this turn
    """
    game.p1.active_dev_cards.append('year_of_plenty')
    game.tm.set_dice_rolled()
    return game


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_two_different_resources(yop_game: GameSetup):
    """Successfully claims two distinct resources from the bank."""
    wood_start = yop_game.p1.resources['wood']
    ore_start = yop_game.p1.resources['ore']
    bank_wood_start = yop_game.board.bank['wood']
    bank_ore_start = yop_game.board.bank['ore']

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p1, resource1='wood', resource2='ore', play_single=False
    )

    assert result is True
    assert yop_game.p1.resources['wood'] == wood_start + 1
    assert yop_game.p1.resources['ore'] == ore_start + 1
    assert yop_game.board.bank['wood'] == bank_wood_start - 1
    assert yop_game.board.bank['ore'] == bank_ore_start - 1
    assert 'year_of_plenty' not in yop_game.p1.active_dev_cards


def test_success_two_same_resources(yop_game: GameSetup):
    """Successfully claims two units of the same resource when bank has at least 2."""
    wood_start = yop_game.p1.resources['wood']
    bank_wood_start = yop_game.board.bank['wood']

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p1, resource1='wood', resource2='wood', play_single=False
    )

    assert result is True
    assert yop_game.p1.resources['wood'] == wood_start + 2
    assert yop_game.board.bank['wood'] == bank_wood_start - 2
    assert 'year_of_plenty' not in yop_game.p1.active_dev_cards


def test_success_play_single_resource(yop_game: GameSetup):
    """Claims only resource1 when play_single=True, leaving resource2 untouched."""
    wood_start = yop_game.p1.resources['wood']
    ore_start = yop_game.p1.resources['ore']

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p1, resource1='wood', resource2='ore', play_single=True
    )

    assert result is True
    assert yop_game.p1.resources['wood'] == wood_start + 1
    assert yop_game.p1.resources['ore'] == ore_start  # Unchanged
    assert 'year_of_plenty' not in yop_game.p1.active_dev_cards


def test_success_play_single_when_bank_only_has_one_resource(yop_game: GameSetup):
    """Succeeds with play_single=True even if resource2 is completely empty in the bank."""
    yop_game.board.bank['ore'] = 0
    wood_start = yop_game.p1.resources['wood']

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p1, resource1='wood', resource2='ore', play_single=True
    )

    assert result is True
    assert yop_game.p1.resources['wood'] == wood_start + 1


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(yop_game: GameSetup):
    """Fails if non-active player attempts to play the card."""
    yop_game.p2.active_dev_cards.append('year_of_plenty')
    start_res = yop_game.p2.resources.copy()

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p2, resource1='wood', resource2='ore', play_single=False
    )

    assert result is False
    assert yop_game.p2.resources == start_res


def test_fails_card_not_in_active_dev_cards(yop_game: GameSetup):
    """Fails if player does not possess Year of Plenty in active dev cards."""
    yop_game.p1.active_dev_cards.remove('year_of_plenty')
    start_res = yop_game.p1.resources.copy()

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p1, resource1='wood', resource2='ore', play_single=False
    )

    assert result is False
    assert yop_game.p1.resources == start_res


def test_fails_dev_card_already_played_this_turn(yop_game: GameSetup):
    """Fails if player has already played a development card during this turn."""
    yop_game.tm.set_played_dev_card()
    start_res = yop_game.p1.resources.copy()

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p1, resource1='wood', resource2='ore', play_single=False
    )

    assert result is False
    assert yop_game.p1.resources == start_res


def test_fails_bank_lacks_same_resource_double(yop_game: GameSetup):
    """Fails when requesting 2 of same resource if bank only has 1 unit remaining."""
    yop_game.board.bank['wood'] = 1
    start_res = yop_game.p1.resources.copy()

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p1, resource1='wood', resource2='wood', play_single=False
    )

    assert result is False
    assert yop_game.p1.resources == start_res


def test_fails_bank_lacks_resource2_when_not_single(yop_game: GameSetup):
    """Fails when play_single=False and bank is empty for requested resource2."""
    yop_game.board.bank['ore'] = 0
    start_res = yop_game.p1.resources.copy()

    result = yop_game.controller.play_year_of_plenty(
        yop_game.p1, resource1='wood', resource2='ore', play_single=False
    )

    assert result is False
    assert yop_game.p1.resources == start_res