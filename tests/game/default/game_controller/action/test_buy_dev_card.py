import unittest
from unittest.mock import MagicMock
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestBuyDevCard(BaseControllerTest):
    """
    Unit tests for GameController.buy_dev_card().

    Key guards: TURN, CAN_AFFORD, deck must not be empty.
    Resources must only be removed AFTER a card is confirmed available [3].
    """

    def setUp(self):
        super().setUp()
        self.dev_cost = self.board_context.get_cost('dev_card')
        self.board.get_top_dev_card.return_value = 'knight'
        self.tm.dice_rolled = True

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_returns_true(self):
        result = self.controller.buy_dev_card(self.p1)
        self.assertTrue(result)
        self.p1.remove_resources.assert_called_once_with(self.dev_cost)
        self.p1.add_dev_card.assert_called_once_with('knight')

    def test_success_all_card_types(self):
        """Every valid card type can be purchased."""
        card_types = list(self.board_context.DEVELOPMENT_CARDS.keys())
        for card in card_types:
            with self.subTest(card=card):
                self.board.get_top_dev_card.return_value = card
                self.p1.add_dev_card.reset_mock()
                self.p1.remove_resources.reset_mock()
                result = self.controller.buy_dev_card(self.p1)
                self.assertTrue(result)
                self.p1.add_dev_card.assert_called_once_with(card)

    # -------------------------------------------------------------------------
    # FAIL
    # -------------------------------------------------------------------------
    def test_fails_cost_not_found(self):
        """Purchase must fail if the cost lookup returns None."""
        self.controller.board_context.get_cost = MagicMock(return_value=None)
        result = self.controller.buy_dev_card(self.p1)
        
        self.assertFalse(result)
        self.p1.remove_resources.assert_not_called()
        self.p1.add_dev_card.assert_not_called()

    def test_fails_not_turn(self):
        result = self.controller.buy_dev_card(self.p2)
        self.assertFalse(result)
        self.p2.add_dev_card.assert_not_called()
        self.p2.remove_resources.assert_not_called()       

    def test_fails_not_roll_dice(self):
        self.tm.dice_rolled = False
        result = self.controller.buy_dev_card(self.p1)
        self.assertFalse(result)
        self.p1.add_dev_card.assert_not_called()
        self.p1.remove_resources.assert_not_called() 

    def test_fails_cant_afford(self):
        self.p1.can_afford.return_value = False
        result = self.controller.buy_dev_card(self.p1)
        self.assertFalse(result)
        self.board.get_top_dev_card.assert_not_called()
        self.p1.add_dev_card.assert_not_called()

    def test_fails_deck_empty(self):
        """Purchase must fail when deck is exhausted."""
        self.board.get_top_dev_card.return_value = None
        result = self.controller.buy_dev_card(self.p1)
        self.assertFalse(result)
        self.p1.remove_resources.assert_not_called()
        self.p1.add_dev_card.assert_not_called()
        


if __name__ == '__main__':
    unittest.main()