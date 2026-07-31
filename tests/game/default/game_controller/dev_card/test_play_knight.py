import pytest
from tests.game.default.game_controller.conftest import GameSetup

TARGET_TILE = 5


@pytest.fixture
def knight_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for playing a Knight card:
    - Player 1 has 'knight' in active_dev_cards
    - Initial robber is at tile 0
    - Player 2 has resources available to steal
    """
    game.p1.active_dev_cards.append('knight')
    game.board.robber_placement = 0
    game.p2.resources = {r: 0 for r in game.context.RESOURCES}
    game.p2.add_resource('wood', 3)
    return game


def _assert_success(knight_game: GameSetup, result: bool):
    assert result is True
    assert knight_game.board.robber_placement == TARGET_TILE
    assert 'knight' not in knight_game.p1.active_dev_cards
    assert 'knight' in knight_game.p1.used_cards

def _assert_failed(knight_game: GameSetup, result: bool):
    assert result is False
    assert knight_game.board.robber_placement != TARGET_TILE
    assert 'knight' in knight_game.p1.active_dev_cards
    assert 'knight' not in knight_game.p1.used_cards

def _assert_robbed(knight_game: GameSetup, p1_start_total: int, p2_start_total: int):
    assert sum(knight_game.p1.resources.values()) == p1_start_total + 1
    assert sum(knight_game.p2.resources.values()) == p2_start_total - 1

def _assert_not_robbed(knight_game: GameSetup, p1_start_total: int, p2_start_total: int):
    assert sum(knight_game.p1.resources.values()) == p1_start_total 
    assert sum(knight_game.p2.resources.values()) == p2_start_total

# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_plays_knight(knight_game: GameSetup):
    """Successfully moves robber, steals a resource, and consumes dev card."""
    knight_game.tm.set_dice_rolled()
    p1_start_total = sum(knight_game.p1.resources.values())
    p2_start_total = sum(knight_game.p2.resources.values())

    result = knight_game.controller.play_knight(
        knight_game.p1, tile_id=TARGET_TILE, victim=knight_game.p2, selection=0
    )

    _assert_success(knight_game, result)
    _assert_robbed(knight_game, p1_start_total, p2_start_total) 

def test_success_playable_before_dice_rolled(knight_game: GameSetup):
    """Knight is unique as the only dev card playable before rolling dice."""
    knight_game.tm.dice_rolled = False
    p1_start_total = sum(knight_game.p1.resources.values())
    p2_start_total = sum(knight_game.p2.resources.values())

    result = knight_game.controller.play_knight(
        knight_game.p1, tile_id=TARGET_TILE, victim=knight_game.p2, selection=0
    )

    _assert_success(knight_game, result)
    _assert_robbed(knight_game, p1_start_total, p2_start_total) 

def test_success_victim_has_no_resources(knight_game: GameSetup):
    """Fails if targeted victim player has zero resources."""
    knight_game.p2.resources = {r: 0 for r in knight_game.context.RESOURCES}
    p1_start_total = sum(knight_game.p1.resources.values())
    p2_start_total = sum(knight_game.p2.resources.values())

    result = knight_game.controller.play_knight(
        knight_game.p1, tile_id=TARGET_TILE, victim=knight_game.p2, selection=0
    )

    _assert_success(knight_game, result)
    _assert_not_robbed(knight_game, p1_start_total, p2_start_total) 

# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_not_turn(knight_game: GameSetup):
    """Fails if non-active player attempts to play Knight."""
    knight_game.p2.active_dev_cards.append('knight')
    p1_start_total = sum(knight_game.p1.resources.values())
    p2_start_total = sum(knight_game.p2.resources.values())

    result = knight_game.controller.play_knight(
        knight_game.p2, tile_id=TARGET_TILE, victim=knight_game.p1, selection=0
    )

    _assert_failed(knight_game, result)
    _assert_not_robbed(knight_game, p1_start_total, p2_start_total) 

def test_fails_card_not_in_active_dev_cards(knight_game: GameSetup):
    """Fails if player does not possess Knight in active dev cards."""
    knight_game.p1.active_dev_cards.remove('knight')
    p1_start_total = sum(knight_game.p1.resources.values())
    p2_start_total = sum(knight_game.p2.resources.values())

    result = knight_game.controller.play_knight(
        knight_game.p1, tile_id=TARGET_TILE, victim=knight_game.p2, selection=0
    )

    assert result is False
    assert knight_game.board.robber_placement != TARGET_TILE
    _assert_not_robbed(knight_game, p1_start_total, p2_start_total) 

def test_fails_already_played_dev_card_this_turn(knight_game: GameSetup):
    """Fails if player has already played a dev card during this turn."""
    knight_game.tm.set_played_dev_card()
    p1_start_total = sum(knight_game.p1.resources.values())
    p2_start_total = sum(knight_game.p2.resources.values())

    result = knight_game.controller.play_knight(
        knight_game.p1, tile_id=TARGET_TILE, victim=knight_game.p2, selection=0
    )

    _assert_failed(knight_game, result)
    _assert_not_robbed(knight_game, p1_start_total, p2_start_total) 

def test_fails_robber_same_tile(knight_game: GameSetup):
    """Fails if trying to move robber to the tile it already occupies."""
    knight_game.board.robber_placement = TARGET_TILE
    p1_start_total = sum(knight_game.p1.resources.values())
    p2_start_total = sum(knight_game.p2.resources.values())

    result = knight_game.controller.play_knight(
        knight_game.p1, tile_id=TARGET_TILE, victim=knight_game.p2, selection=0
    )

    assert result is False
    assert 'knight' in knight_game.p1.active_dev_cards
    assert 'knight' not in knight_game.p1.used_cards
    _assert_not_robbed(knight_game, p1_start_total, p2_start_total) 

def test_fails_self_stealing(knight_game: GameSetup):
    """Player cannot target themselves as robber victim."""
    p1_start_total = knight_game.p1.resources
    

    result = knight_game.controller.play_knight(
        knight_game.p1, tile_id=TARGET_TILE, victim=knight_game.p1, selection=0
    )

    _assert_failed(knight_game, result)
    assert knight_game.p1.resources == p1_start_total