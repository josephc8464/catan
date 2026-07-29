from ..conftest import GameSetup

# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_moves_robber_to_new_tile(game: GameSetup):
    """Moving robber to any different valid tile updates placement and returns True."""
    game.board.robber_placement = 0

    # Move to intermediate tile
    result = game.controller.move_robber(5)
    assert result is True
    assert game.board.robber_placement == 5

    # Boundary check for max standard tile ID
    result_max = game.controller.move_robber(18)
    assert result_max is True
    assert game.board.robber_placement == 18

# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_same_tile(game: GameSetup):
    """Robber must be moved to a DIFFERENT tile; placement state remains unchanged."""
    game.board.robber_placement = 3

    result = game.controller.move_robber(3)

    assert result is False
    assert game.board.robber_placement == 3