import unittest
from unittest.mock import MagicMock, call
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestEndTurn(BaseControllerTest):
    """
    Unit tests for GameController.end_turn().
    """

    def test_end_turn_sequence(self):
        """
        Successfully updates the outgoing player's dev cards before advancing the turn.
        """
        self.tm.get_current_player.return_value = self.p1
        
        # Set up a manager to track the exact order of calls across different mocks
        manager = MagicMock()
        manager.attach_mock(self.p1.update_dev_cards, 'update_dev_cards')
        manager.attach_mock(self.tm.next_turn, 'next_turn')

        self.controller.end_turn()

        # Verify the exact execution order: update_dev_cards MUST happen before next_turn
        manager.assert_has_calls([
            call.update_dev_cards(),
            call.next_turn()
        ])
        
        # Ensure the opponent's dev cards were untouched
        self.p2.update_dev_cards.assert_not_called()


if __name__ == '__main__':
    unittest.main()