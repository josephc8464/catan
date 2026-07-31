import pytest
from tests.game.default.game_controller.conftest import GameSetup


@pytest.fixture
def monopoly_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for playing a Monopoly card:
    - Player 1 has 'monopoly' in active_dev_cards
    - Player 2 has 3 wood
    - Dice have been rolled
    """
    game.p1.active_dev_cards.append('monopoly')
    game.p1.resources = {r: 0 for r in game.context.RESOURCES}
    game.p2.resources = {r: 0 for r in game.context.RESOURCES}
    game.p2.add_resource('wood', 3)
    game.tm.set_dice_rolled()
    return game


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_plays_monopoly(monopoly_game: GameSetup):
    """Steals all of the chosen resource from opponents and consumes card."""
    result = monopoly_game.controller.play_monopoly(monopoly_game.p1, 'wood')

    assert result is True
    assert monopoly_game.p2.resources['wood'] == 0
    assert monopoly_game.p1.resources['wood'] == 3
    assert 'monopoly' not in monopoly_game.p1.active_dev_cards


def test_success_empty_opponents(monopoly_game: GameSetup):
    """Monopoly played on a resource unheld by any opponent succeeds without adding resources."""
    monopoly_game.p2.resources['wood'] = 0

    result = monopoly_game.controller.play_monopoly(monopoly_game.p1, 'wood')

    assert result is True
    assert monopoly_game.p1.resources['wood'] == 0
    assert 'monopoly' not in monopoly_game.p1.active_dev_cards


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(monopoly_game: GameSetup):
    """Fails if non-active player attempts to play Monopoly."""
    monopoly_game.p2.active_dev_cards.append('monopoly')

    result = monopoly_game.controller.play_monopoly(monopoly_game.p2, 'wood')

    assert result is False
    assert monopoly_game.p2.resources['wood'] == 3
    assert monopoly_game.p1.resources['wood'] == 0


def test_fails_card_not_in_active_dev_cards(monopoly_game: GameSetup):
    """Fails if player does not possess Monopoly in active dev cards."""
    monopoly_game.p1.active_dev_cards.remove('monopoly')

    result = monopoly_game.controller.play_monopoly(monopoly_game.p1, 'wood')

    assert result is False
    assert monopoly_game.p2.resources['wood'] == 3


def test_fails_already_played_dev_card_this_turn(monopoly_game: GameSetup):
    """Fails if player has already played a dev card during this turn."""
    monopoly_game.tm.set_played_dev_card()

    result = monopoly_game.controller.play_monopoly(monopoly_game.p1, 'wood')

    assert result is False
    assert monopoly_game.p2.resources['wood'] == 3


def test_fails_dice_not_rolled(monopoly_game: GameSetup):
    """Fails if dice have not been rolled yet this turn."""
    monopoly_game.tm.dice_rolled = False

    result = monopoly_game.controller.play_monopoly(monopoly_game.p1, 'wood')

    assert result is False
    assert monopoly_game.p2.resources['wood'] == 3
