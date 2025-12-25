"""Comprehensive tests for interaction.py to achieve 85%+ coverage."""
import unittest
from unittest.mock import patch, MagicMock

from game.game_logic.interaction import Interaction


class TestInteraction(unittest.TestCase):
    """Test Interaction class methods."""

    # ==========================================
    # TEST get_difficulty_tag()
    # ==========================================

    def test_get_difficulty_tag_none(self):
        """Test get_difficulty_tag with None (SAFE option)."""
        result = Interaction.get_difficulty_tag(None)
        self.assertEqual(result, "[SAFE]")

    def test_get_difficulty_tag_trivial_100(self):
        """Test get_difficulty_tag with 100 (TRIVIAL)."""
        result = Interaction.get_difficulty_tag(100)
        self.assertEqual(result, "[TRIVIAL]")

    def test_get_difficulty_tag_trivial_over_100(self):
        """Test get_difficulty_tag with > 100 (TRIVIAL)."""
        result = Interaction.get_difficulty_tag(150)
        self.assertEqual(result, "[TRIVIAL]")

    def test_get_difficulty_tag_easy_80(self):
        """Test get_difficulty_tag with 80 (EASY)."""
        result = Interaction.get_difficulty_tag(80)
        self.assertEqual(result, "[EASY]")

    def test_get_difficulty_tag_easy_99(self):
        """Test get_difficulty_tag with 99 (EASY)."""
        result = Interaction.get_difficulty_tag(99)
        self.assertEqual(result, "[EASY]")

    def test_get_difficulty_tag_likely_60(self):
        """Test get_difficulty_tag with 60 (LIKELY)."""
        result = Interaction.get_difficulty_tag(60)
        self.assertEqual(result, "[LIKELY]")

    def test_get_difficulty_tag_likely_79(self):
        """Test get_difficulty_tag with 79 (LIKELY)."""
        result = Interaction.get_difficulty_tag(79)
        self.assertEqual(result, "[LIKELY]")

    def test_get_difficulty_tag_uncertain_40(self):
        """Test get_difficulty_tag with 40 (UNCERTAIN)."""
        result = Interaction.get_difficulty_tag(40)
        self.assertEqual(result, "[UNCERTAIN]")

    def test_get_difficulty_tag_uncertain_59(self):
        """Test get_difficulty_tag with 59 (UNCERTAIN)."""
        result = Interaction.get_difficulty_tag(59)
        self.assertEqual(result, "[UNCERTAIN]")

    def test_get_difficulty_tag_risky_20(self):
        """Test get_difficulty_tag with 20 (RISKY)."""
        result = Interaction.get_difficulty_tag(20)
        self.assertEqual(result, "[RISKY]")

    def test_get_difficulty_tag_risky_39(self):
        """Test get_difficulty_tag with 39 (RISKY)."""
        result = Interaction.get_difficulty_tag(39)
        self.assertEqual(result, "[RISKY]")

    def test_get_difficulty_tag_suicide_1(self):
        """Test get_difficulty_tag with 1 (SUICIDE)."""
        result = Interaction.get_difficulty_tag(1)
        self.assertEqual(result, "[SUICIDE]")

    def test_get_difficulty_tag_suicide_19(self):
        """Test get_difficulty_tag with 19 (SUICIDE)."""
        result = Interaction.get_difficulty_tag(19)
        self.assertEqual(result, "[SUICIDE]")

    def test_get_difficulty_tag_impossible_0(self):
        """Test get_difficulty_tag with 0 (IMPOSSIBLE)."""
        result = Interaction.get_difficulty_tag(0)
        self.assertEqual(result, "[IMPOSSIBLE]")

    def test_get_difficulty_tag_impossible_negative(self):
        """Test get_difficulty_tag with negative (IMPOSSIBLE)."""
        result = Interaction.get_difficulty_tag(-10)
        self.assertEqual(result, "[IMPOSSIBLE]")

    # ==========================================
    # TEST attempt_action()
    # ==========================================

    def test_attempt_action_chance_100(self):
        """Test attempt_action with chance >= 100 always succeeds."""
        result = Interaction.attempt_action(100)
        self.assertTrue(result)

        result = Interaction.attempt_action(150)
        self.assertTrue(result)

    def test_attempt_action_chance_0(self):
        """Test attempt_action with chance <= 0 always fails."""
        result = Interaction.attempt_action(0)
        self.assertFalse(result)

        result = Interaction.attempt_action(-10)
        self.assertFalse(result)

    @patch('game.game_logic.interaction.randint')
    def test_attempt_action_success(self, mock_randint):
        """Test attempt_action when roll succeeds."""
        mock_randint.return_value = 30  # Roll 30, chance 50 -> success
        result = Interaction.attempt_action(50)
        self.assertTrue(result)
        mock_randint.assert_called_once_with(1, 100)

    @patch('game.game_logic.interaction.randint')
    def test_attempt_action_failure(self, mock_randint):
        """Test attempt_action when roll fails."""
        mock_randint.return_value = 60  # Roll 60, chance 50 -> failure
        result = Interaction.attempt_action(50)
        self.assertFalse(result)
        mock_randint.assert_called_once_with(1, 100)

    @patch('game.game_logic.interaction.randint')
    def test_attempt_action_boundary_success(self, mock_randint):
        """Test attempt_action with roll exactly at chance boundary (success)."""
        mock_randint.return_value = 50  # Roll 50, chance 50 -> success (<=)
        result = Interaction.attempt_action(50)
        self.assertTrue(result)

    @patch('game.game_logic.interaction.randint')
    def test_attempt_action_boundary_failure(self, mock_randint):
        """Test attempt_action with roll just above chance boundary (failure)."""
        mock_randint.return_value = 51  # Roll 51, chance 50 -> failure (>)
        result = Interaction.attempt_action(50)
        self.assertFalse(result)

    @patch('game.game_logic.interaction.randint')
    def test_attempt_action_high_chance(self, mock_randint):
        """Test attempt_action with high chance (80%)."""
        mock_randint.return_value = 75  # Roll 75, chance 80 -> success
        result = Interaction.attempt_action(80)
        self.assertTrue(result)

    @patch('game.game_logic.interaction.randint')
    def test_attempt_action_low_chance(self, mock_randint):
        """Test attempt_action with low chance (25%)."""
        mock_randint.return_value = 30  # Roll 30, chance 25 -> failure
        result = Interaction.attempt_action(25)
        self.assertFalse(result)

    # ==========================================
    # TEST ask()
    # ==========================================

    @patch('builtins.input')
    @patch('builtins.print')
    def test_ask_valid_first_try(self, mock_print, mock_input):
        """Test ask() with valid input on first try."""
        mock_input.return_value = "1"
        options = ("1", "2", "3")

        result = Interaction.ask(options)

        self.assertEqual(result, "1")
        mock_input.assert_called_once_with("> ")
        mock_print.assert_not_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_ask_valid_after_invalid(self, mock_print, mock_input):
        """Test ask() with invalid input then valid input."""
        mock_input.side_effect = ["invalid", "wrong", "2"]
        options = ("1", "2", "3")

        result = Interaction.ask(options)

        self.assertEqual(result, "2")
        self.assertEqual(mock_input.call_count, 3)
        self.assertEqual(mock_print.call_count, 2)  # Should print error twice

    @patch('builtins.input')
    @patch('builtins.print')
    def test_ask_strips_whitespace(self, mock_print, mock_input):
        """Test ask() strips whitespace from input."""
        mock_input.return_value = "  1  "
        options = ("1", "2", "3")

        result = Interaction.ask(options)

        self.assertEqual(result, "1")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_ask_empty_string_invalid(self, mock_print, mock_input):
        """Test ask() treats empty string as invalid."""
        mock_input.side_effect = ["", "1"]
        options = ("1", "2", "3")

        result = Interaction.ask(options)

        self.assertEqual(result, "1")
        self.assertEqual(mock_print.call_count, 1)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_ask_single_option(self, mock_print, mock_input):
        """Test ask() with single option."""
        mock_input.return_value = "yes"
        options = ("yes",)

        result = Interaction.ask(options)

        self.assertEqual(result, "yes")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_ask_case_sensitive(self, mock_print, mock_input):
        """Test ask() is case sensitive."""
        mock_input.side_effect = ["A", "a"]
        options = ("a", "b")

        result = Interaction.ask(options)

        self.assertEqual(result, "a")
        self.assertEqual(mock_print.call_count, 1)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_ask_error_message_includes_options(self, mock_print, mock_input):
        """Test ask() error message includes all options."""
        mock_input.side_effect = ["invalid", "1"]
        options = ("1", "2", "3")

        Interaction.ask(options)

        # Check that error message was printed with options
        error_call = mock_print.call_args[0][0]
        assert "1" in error_call
        assert "2" in error_call
        assert "3" in error_call


if __name__ == '__main__':
    unittest.main()

