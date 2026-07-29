import itertools
from unittest.mock import patch
from ..conftest import GameSetup

# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_rolls_and_distributes(game: GameSetup):
    """Successfully rolls dice, updates TurnManager state, and triggers resource distribution."""
    assert game.tm.dice_rolled is False

    with patch('random.randint', side_effect=[3, 4]):
        result = game.controller.roll_dice(game.p1)

    assert result == (3, 4)
    assert game.tm.dice_rolled is True


def test_success_die_values_in_valid_range(game: GameSetup):
    """Each individual die value must be an integer between 1 and 6 inclusive."""
    for die1, die2 in itertools.product(range(1, 7), repeat=2):
        game.tm.dice_rolled = False

        with patch('random.randint', side_effect=[die1, die2]):
            d1, d2 = game.controller.roll_dice(game.p1)

        assert (d1, d2) == (die1, die2)
        assert 1 <= d1 <= 6
        assert 1 <= d2 <= 6


# =========================================================================
# FAILURE CASES (GUARDS)
# =========================================================================

def test_fails_not_turn(game: GameSetup):
    """Rolling dice fails without modifying turn state if it is not the active player's turn."""
    result = game.controller.roll_dice(game.p2)

    assert result == (0, 0)
    assert game.tm.dice_rolled is False


def test_fails_dice_already_rolled(game: GameSetup):
    """Cannot roll the dice more than once during the same turn."""
    game.tm.set_dice_rolled()

    result = game.controller.roll_dice(game.p1)

    assert result == (0, 0)