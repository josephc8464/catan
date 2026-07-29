from ..conftest import GameSetup
from game.player import Player


def _set_player_vp(player: Player, target_vp: int) -> None:
    """Configures a player's structure state to equal the desired local VP count."""
    player.structures.clear()

    # Cities are worth 2 VP each, Settlements are worth 1 VP each
    cities_needed = target_vp // 2
    settlements_needed = target_vp % 2

    for i in range(cities_needed):
        player.add_structure(100 + i, 'city')
    for i in range(settlements_needed):
        player.add_structure(200 + i, 'settlement')


# =========================================================================
# SUCCESS SCENARIOS
# =========================================================================

def test_success_reaches_winning_threshold(game: GameSetup):
    """Player wins when local VP meets the victory threshold (10 VP)."""
    _set_player_vp(game.p1, 10)

    assert game.controller.check_victory(game.p1) is True


def test_success_exceeds_winning_threshold(game: GameSetup):
    """Player wins when local VP exceeds the victory threshold."""
    _set_player_vp(game.p1, 13)

    assert game.controller.check_victory(game.p1) is True


def test_success_with_longest_road_award(game: GameSetup):
    """Player wins with 8 local VP plus the Longest Road award (+2 VP)."""
    _set_player_vp(game.p1, 8)
    game.board.longest_road = game.p1.color

    assert game.controller.check_victory(game.p1) is True


def test_success_with_both_awards(game: GameSetup):
    """Player wins with 6 local VP plus both Longest Road and Largest Army awards (+4 VP)."""
    _set_player_vp(game.p1, 6)
    game.board.longest_road = game.p1.color
    game.board.largest_army = game.p1.color

    assert game.controller.check_victory(game.p1) is True


# =========================================================================
# FAILURE SCENARIOS
# =========================================================================

def test_fails_zero_vp(game: GameSetup):
    """Player with 0 VP does not trigger victory."""
    _set_player_vp(game.p1, 0)

    assert game.controller.check_victory(game.p1) is False


def test_fails_one_below_threshold(game: GameSetup):
    """Player with 9 VP (one below threshold) does not trigger victory."""
    _set_player_vp(game.p1, 9)

    assert game.controller.check_victory(game.p1) is False


def test_fails_opponent_holds_awards(game: GameSetup):
    """Player at 9 VP does not gain points from awards held by opponents."""
    _set_player_vp(game.p1, 9)
    game.board.longest_road = game.p2.color
    game.board.largest_army = game.p2.color

    assert game.controller.check_victory(game.p1) is False


# =========================================================================
# DYNAMIC CONTEXT
# =========================================================================

def test_dynamic_board_context_values(game: GameSetup):
    """Victory calculation dynamically references the context threshold and award values."""
    awards_total = sum(game.context.AWARDS.values())
    threshold = game.context.WINNING_VP_THRESHOLD

    needed_local_vp = threshold - awards_total
    _set_player_vp(game.p1, needed_local_vp)

    game.board.longest_road = game.p1.color
    game.board.largest_army = game.p1.color

    assert game.controller.check_victory(game.p1) is True