import pytest
from ..conftest import GameSetup, assert_not_paid, assert_paid
from game.player import Player

DEV_CARD = 'dev_card'

@pytest.fixture
def dev_card_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for buying a development card:
    - Player 1 has exact resources needed for a dev card
    - Dice have been rolled
    """
    cost = game.context.get_cost(DEV_CARD)
    game.p1.add_resources(cost)
    game.tm.set_dice_rolled()

    return game

def _assert_dev_card_unchanged(player: Player, result: bool, start_card_count: int) -> None:
    """Asserts that buying a dev card failed and player's card count is unchanged."""
    assert result is False
    assert len(_get_card_count(player)) == start_card_count

def _assert_dev_card_changed(player: Player, result: bool, start_card_count: int) -> None:
    """Asserts that buying a dev card succeeded and player gained a card."""
    assert result is True
    assert len(_get_card_count(player)) == start_card_count + 1

def _get_card_count(player: Player) -> list[str]:
    return (player.active_dev_cards + player.bought_dev_cards + player.used_cards)

# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_returns_true(dev_card_game: GameSetup):
    """Paid dev card purchase succeeds when player has resources, turn, and dice rolled."""
    start_res = dev_card_game.p1.resources.copy()
    start_cards = len(_get_card_count(dev_card_game.p1))

    result = dev_card_game.controller.buy_dev_card(dev_card_game.p1)

    _assert_dev_card_changed(dev_card_game.p1, result, start_cards)
    assert_paid(dev_card_game, dev_card_game.p1, start_res, DEV_CARD)


# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(dev_card_game: GameSetup):
    """Buying a dev card fails if it is not the player's turn."""
    cost = dev_card_game.context.get_cost(DEV_CARD)
    dev_card_game.p2.add_resources(cost)
    start_res = dev_card_game.p2.resources.copy()
    start_cards = len(_get_card_count(dev_card_game.p1))

    result = dev_card_game.controller.buy_dev_card(dev_card_game.p2)

    _assert_dev_card_unchanged(dev_card_game.p2, result, start_cards)
    assert_not_paid(dev_card_game.p2, start_res)


def test_fails_not_roll_dice(dev_card_game: GameSetup):
    """Buying a dev card fails if dice have not been rolled yet this turn."""
    start_res = dev_card_game.p1.resources.copy()
    start_cards = len(_get_card_count(dev_card_game.p1))
    dev_card_game.tm.dice_rolled = False

    result = dev_card_game.controller.buy_dev_card(dev_card_game.p1)

    _assert_dev_card_unchanged(dev_card_game.p1, result, start_cards)
    assert_not_paid(dev_card_game.p1, start_res)

def test_fails_cant_afford(dev_card_game: GameSetup):
    """Buying a dev card fails if player lacks necessary resources."""
    dev_card_game.p1.resources = {r: 0 for r in dev_card_game.context.RESOURCES}
    start_res = dev_card_game.p1.resources.copy()
    start_cards = len(_get_card_count(dev_card_game.p1))

    result = dev_card_game.controller.buy_dev_card(dev_card_game.p1)

    _assert_dev_card_unchanged(dev_card_game.p1, result, start_cards)
    assert_not_paid(dev_card_game.p1, start_res)

def test_fails_deck_empty(dev_card_game: GameSetup):
    """Purchase must fail when development card deck is exhausted."""
    dev_card_game.board.development_cards.clear()
    start_res = dev_card_game.p1.resources.copy()
    start_cards = len(_get_card_count(dev_card_game.p1))

    result = dev_card_game.controller.buy_dev_card(dev_card_game.p1)

    _assert_dev_card_unchanged(dev_card_game.p1, result, start_cards)
    assert_not_paid(dev_card_game.p1, start_res)