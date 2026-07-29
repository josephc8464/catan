from ..conftest import GameSetup

# =========================================================================
# SUCCESS CASES
# =========================================================================

def test_end_turn_advances_current_player(game: GameSetup):
    """Ending turn advances current player to the next turn and resets dice roll state."""
    assert game.tm.get_current_player() == game.p1
    game.tm.set_dice_rolled()

    game.controller.end_turn()

    assert game.tm.get_current_player() == game.p2
    assert game.tm.dice_rolled is False


def test_end_turn_promotes_bought_dev_cards(game: GameSetup):
    """Ending turn updates outgoing player's bought dev cards while leaving opponents untouched."""
    # Place a bought card in p1's unplayable/bought inventory
    game.p1.bought_dev_cards.append('knight')
    assert len(game.p1.active_dev_cards) == 0

    game.controller.end_turn()

    # Outgoing player (p1) has cards updated to active
    assert 'knight' in game.p1.active_dev_cards
    assert len(game.p1.bought_dev_cards) == 0

    # Opponent (p2) dev card state is untouched
    assert len(game.p2.bought_dev_cards) == 0
    assert len(game.p2.active_dev_cards) == 0