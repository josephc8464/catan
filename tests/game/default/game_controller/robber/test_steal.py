import unittest
from unittest.mock import patch
from tests.game.default.game_controller.conftest_base import BaseControllerTest


class TestSteal(BaseControllerTest):
    """
    Unit tests for GameController.steal().
    """

    def setUp(self):
        super().setUp()
        self.p2.resources = {'wood': 3, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}

    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------

    def test_success_steals_resource(self):
        """Successfully transfers exactly 1 of the same resource from victim to robber."""
        with patch('random.shuffle'):
            result = self.controller.steal(0, self.p1, self.p2)
            
        self.assertTrue(result)
        
        self.p1.add_resource.assert_called_once()
        self.p2.remove_resource.assert_called_once()
        
        add_resource, add_amount = self.p1.add_resource.call_args[0]
        remove_resource, remove_amount = self.p2.remove_resource.call_args[0]
        
        self.assertEqual(add_amount, 1)
        self.assertEqual(remove_amount, 1)
        self.assertEqual(add_resource, remove_resource)

    def test_success_out_of_bounds_selection(self):
        """Out-of-bounds selection falls back to random.choice safely."""
        with patch('random.choice', return_value='wood') as mock_choice:
            result = self.controller.steal(999, self.p1, self.p2)
            
        self.assertTrue(result)
        mock_choice.assert_called_once()
        self.p1.add_resource.assert_called_once_with('wood', 1)

    # -------------------------------------------------------------------------
    # FAIL
    # -------------------------------------------------------------------------

    def test_fails_victim_has_no_resources(self):
        self.p2.resources = {'wood': 0, 'brick': 0, 'sheep': 0, 'wheat': 0, 'ore': 0}
        
        result = self.controller.steal(0, self.p1, self.p2)
        
        self.assertTrue(result)
        self.p1.add_resource.assert_not_called()
        self.p2.remove_resource.assert_not_called()

    def test_fails_self_steal(self):
        """Player cannot steal from themselves."""
        result = self.controller.steal(0, self.p1, self.p1)
        
        self.assertFalse(result)
        self.p1.add_resource.assert_not_called()
        self.p1.remove_resource.assert_not_called()


if __name__ == '__main__':
    unittest.main()