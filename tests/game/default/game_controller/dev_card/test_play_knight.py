import unittest
from unittest.mock import patch
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestPlayKnight(BaseControllerTest):
    """
    Unit tests for GameController.play_knight().
    """

    def setUp(self):
        super().setUp()
        self.tile_id = 5
        self.board.robber_placement = 0
        self.p2.resources = {'wood': 3, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}

    def _play(self, player=None, tile=None, victim=None, selection=0):
        return self.controller.play_knight(
            player or self.p1,
            tile if tile is not None else self.tile_id,
            victim or self.p2,
            selection
        )

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_plays_knight(self):
        """Successfully moves robber, steals, consumes card, and sets flag[cite: 8]."""
        with patch.object(self.controller, 'move_robber', return_value=True) as mock_move, \
             patch.object(self.controller, 'steal', return_value=True) as mock_steal:
            
            self.assertTrue(self._play())
            
            mock_move.assert_called_once_with(self.tile_id)
            mock_steal.assert_called_once_with(0, self.p1, self.p2)
            
        self.p1.remove_dev_card.assert_called_once_with('knight')
        self.tm.set_played_dev_card.assert_called_once()

    def test_success_playable_before_dice_rolled(self):
        """Knight is the only card playable before rolling[cite: 8]."""
        self.tm.dice_rolled = False
        with patch.object(self.controller, 'move_robber', return_value=True), \
             patch.object(self.controller, 'steal', return_value=True):
            self.assertTrue(self._play())

    # -------------------------------------------------------------------------
    # FAIL GUARDS
    # -------------------------------------------------------------------------

    def test_fails_turn_and_card_guards(self):
        """Fails cleanly on bad turn, missing card, or already played flag[cite: 8]."""
        with patch.object(self.controller, 'move_robber', return_value=True) as mock_move:
            # 1. Not player's turn
            self.assertFalse(self._play(player=self.p2))
            
            # 2. No knight card
            self.p1.has_dev_card.return_value = False
            self.assertFalse(self._play())
            self.p1.has_dev_card.return_value = True # reset
            
            # 3. Already played a dev card this turn
            self.tm.played_dev_card = True
            self.assertFalse(self._play())
            
            mock_move.assert_not_called()

    def test_fails_game_logic(self):
        """Fails cleanly if robber stays on same tile, victim is empty, or self-stealing[cite: 8]."""
        with patch.object(self.controller, 'move_robber', return_value=True) as mock_move:
            # 1. Robber same tile
            self.board.robber_placement = self.tile_id
            self.assertFalse(self._play())
            self.board.robber_placement = 0 # reset
            
            # 2. Victim has no resources
            self.p2.resources = {k: 0 for k in self.p2.resources}
            self.assertFalse(self._play())
            self.p2.resources['wood'] = 3 # reset
            
            # 3. Self steal
            self.assertFalse(self._play(victim=self.p1))
            
            mock_move.assert_not_called()
            self.p1.remove_dev_card.assert_not_called()


if __name__ == '__main__':
    unittest.main()