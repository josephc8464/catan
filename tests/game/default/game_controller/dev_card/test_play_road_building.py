import pytest
from tests.game.default.game_controller.conftest import GameSetup

# Sample graph connected vertices for chain testing: V1 - V2 - V3
V1, V2, V3 = 0, 1, 4
V_UNCONNECTED_1, V_UNCONNECTED_2 = 40, 41


@pytest.fixture
def rb_game(game: GameSetup) -> GameSetup:
    """
    Pre-configures a valid state for playing Road Building:
    - Player 1 has 'road_building' in active_dev_cards
    - Player 1 has a structure at V1 so roads can connect
    - Dice have been rolled
    """
    game.p1.active_dev_cards.append('road_building')
    game.board.add_structure(V1, game.p1.color, 'settlement')
    game.p1.add_structure(V1, 'settlement')
    game.tm.set_dice_rolled()
    return game


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_places_two_roads(rb_game: GameSetup):
    """Successfully places two connected free roads and consumes dev card."""
    result = rb_game.controller.play_road_building(
        rb_game.p1, v1=V1, v2=V2, v3=V2, v4=V3, play_single=False
    )

    assert result is True
    assert (V1, V2) in rb_game.p1.roads or (V2, V1) in rb_game.p1.roads
    assert (V2, V3) in rb_game.p1.roads or (V3, V2) in rb_game.p1.roads
    assert 'road_building' not in rb_game.p1.active_dev_cards


def test_success_play_single_road(rb_game: GameSetup):
    """Successfully places only 1 road when play_single=True."""
    result = rb_game.controller.play_road_building(
        rb_game.p1, v1=V1, v2=V2, v3=0, v4=0, play_single=True
    )

    assert result is True
    assert (V1, V2) in rb_game.p1.roads or (V2, V1) in rb_game.p1.roads
    assert 'road_building' not in rb_game.p1.active_dev_cards


def test_success_single_road_when_only_one_piece_remaining(rb_game: GameSetup):
    """Succeeds with play_single=True when player has exactly 1 road piece left in supply."""
    max_roads = rb_game.context.get_max_pieces('road')
    # Fill supply so only 1 road remains
    for i in range(max_roads - 1):
        rb_game.p1.roads.add((100 + i, 200 + i))

    result = rb_game.controller.play_road_building(
        rb_game.p1, v1=V1, v2=V2, v3=0, v4=0, play_single=True
    )

    assert result is True
    assert len(rb_game.p1.roads) == max_roads


# =========================================================================
# FAILURE & ROLLBACK CASES
# =========================================================================

def test_fails_road1_invalid_no_mutation(rb_game: GameSetup):
    """Fails cleanly if first road placement is illegal (unconnected vertex)."""
    result = rb_game.controller.play_road_building(
        rb_game.p1, v1=V_UNCONNECTED_1, v2=V_UNCONNECTED_2, v3=V2, v4=V3, play_single=False
    )

    assert result is False
    assert (V_UNCONNECTED_1, V_UNCONNECTED_2) not in rb_game.p1.roads
    assert 'road_building' in rb_game.p1.active_dev_cards


def test_fails_road2_invalid_rolls_back_road1(rb_game: GameSetup):
    """Atomically rolls back road 1 if road 2 fails when play_single=False."""
    # First road (V1, V2) is valid, second road (V_UNCONNECTED_1, V_UNCONNECTED_2) is invalid
    result = rb_game.controller.play_road_building(
        rb_game.p1, v1=V1, v2=V2, v3=V_UNCONNECTED_1, v4=V_UNCONNECTED_2, play_single=False
    )

    assert result is False
    # Verify Road 1 was completely rolled back from both player model and board graph
    assert (V1, V2) not in rb_game.p1.roads and (V2, V1) not in rb_game.p1.roads
    assert rb_game.board.graph.get_edge_color(V1, V2) is None
    assert 'road_building' in rb_game.p1.active_dev_cards


def test_fails_insufficient_road_pieces_double(rb_game: GameSetup):
    """Fails when play_single=False if player has fewer than 2 roads remaining in supply."""
    max_roads = rb_game.context.get_max_pieces('road')
    # Leave only 1 road remaining in supply
    for i in range(max_roads - 1):
        rb_game.p1.roads.add((100 + i, 200 + i))

    result = rb_game.controller.play_road_building(
        rb_game.p1, v1=V1, v2=V2, v3=V2, v4=V3, play_single=False
    )

    assert result is False


def test_fails_insufficient_road_pieces_single(rb_game: GameSetup):
    """Fails when play_single=True if player has 0 roads remaining in supply."""
    max_roads = rb_game.context.get_max_pieces('road')
    # Fill supply completely
    for i in range(max_roads):
        rb_game.p1.roads.add((100 + i, 200 + i))

    result = rb_game.controller.play_road_building(
        rb_game.p1, v1=V1, v2=V2, v3=0, v4=0, play_single=True
    )

    assert result is False