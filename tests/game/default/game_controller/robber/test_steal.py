from unittest.mock import patch
from ..conftest import GameSetup


# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_success_steals_resource(game: GameSetup):
    """Successfully transfers exactly 1 resource card from victim to robber player."""
    game.p1.resources = {r: 0 for r in game.context.RESOURCES}
    game.p2.resources = {'wood': 3, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}

    result = game.controller.steal(0, game.p1, game.p2)

    assert result is True
    assert game.p1.resources['wood'] == 1
    assert game.p2.resources['wood'] == 2


def test_success_out_of_bounds_selection(game: GameSetup):
    """Out-of-bounds selection index safely falls back to choosing a card from victim."""
    game.p1.resources = {r: 0 for r in game.context.RESOURCES}
    game.p2.resources = {'wood': 1, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}

    result = game.controller.steal(999, game.p1, game.p2)

    assert result is True
    assert game.p1.resources['wood'] == 1
    assert game.p2.resources['wood'] == 0

def test_success_victim_has_no_resources(game: GameSetup):
    """Steal succeeds gracefully without transferring cards if victim has 0 resources."""
    game.p1.resources = {r: 0 for r in game.context.RESOURCES}
    game.p2.resources = {r: 0 for r in game.context.RESOURCES}

    p1_start = game.p1.resources.copy()
    p2_start = game.p2.resources.copy()

    result = game.controller.steal(0, game.p1, game.p2)

    assert result is True
    assert game.p1.resources == p1_start
    assert game.p2.resources == p2_start

# =========================================================================
# FAILURE CASES
# =========================================================================

def test_fails_self_steal(game: GameSetup):
    """Player cannot target themselves for stealing."""
    game.p1.resources = {'wood': 3, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}
    p1_start = game.p1.resources.copy()

    result = game.controller.steal(0, game.p1, game.p1)
    
    assert result is False
    assert game.p1.resources == p1_start