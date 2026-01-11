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

    # ==========================================
    # TEST format_hatred_text()
    # ==========================================

    def test_format_hatred_text_lowercase(self):
        """Test format_hatred_text adds 😡 emoji before lowercase 'hatred'."""
        text = "You gain +10 PCR hatred."
        result = Interaction.format_hatred_text(text)
        self.assertIn("😡", result)
        self.assertIn("😡 hatred", result)

    def test_format_hatred_text_uppercase(self):
        """Test format_hatred_text adds 😡 emoji before uppercase 'HATRED'."""
        text = "You gain +10 PCR HATRED."
        result = Interaction.format_hatred_text(text)
        self.assertIn("😡", result)
        self.assertIn("😡 HATRED", result)

    def test_format_hatred_text_mixed_case(self):
        """Test format_hatred_text adds 😡 emoji before mixed case 'Hatred'."""
        text = "Your Hatred level is high."
        result = Interaction.format_hatred_text(text)
        self.assertIn("😡", result)
        self.assertIn("😡 Hatred", result)

    def test_format_hatred_text_multiple_occurrences(self):
        """Test format_hatred_text adds 😡 emoji before all 'hatred' mentions."""
        text = "Your hatred is rising. The hatred burns inside you."
        result = Interaction.format_hatred_text(text)
        # Should have 2 emojis (one for each hatred)
        self.assertEqual(result.count("😡"), 2)
        self.assertIn("😡 hatred", result)

    def test_format_hatred_text_pcr_hatred(self):
        """Test format_hatred_text handles 'PCR HATRED' correctly."""
        text = "- 10 PCR HATRED (Humiliation)."
        result = Interaction.format_hatred_text(text)
        self.assertIn("😡", result)
        self.assertIn("😡 HATRED", result)

    def test_format_hatred_text_no_hatred(self):
        """Test format_hatred_text doesn't modify text without 'hatred'."""
        text = "You gain +1000 CZK."
        result = Interaction.format_hatred_text(text)
        self.assertEqual(result, text)
        self.assertNotIn("😡", result)

    def test_format_hatred_text_with_rich_markup(self):
        """Test format_hatred_text works with Rich markup tags."""
        text = "[red]+ 25 PCR HATRED[/red]"
        result = Interaction.format_hatred_text(text)
        self.assertIn("😡", result)
        self.assertIn("😡 HATRED", result)
        # Should preserve Rich markup
        self.assertIn("[red]", result)
        self.assertIn("[/red]", result)

    def test_format_hatred_text_word_boundary(self):
        """Test format_hatred_text only matches 'hatred' as whole word."""
        text = "I hate red cars."  # Should not match "hate red"
        result = Interaction.format_hatred_text(text)
        self.assertNotIn("😡", result)
        self.assertEqual(result, text)

    def test_show_outcome_formats_hatred(self):
        """Test show_outcome automatically formats hatred with emoji."""
        with patch('game.game_logic.interaction.print') as mock_print:
            Interaction.show_outcome("- 10 PCR HATRED.")
            # Check that print was called with a Panel
            call_args = mock_print.call_args[0][0]
            # Panel object has a renderable attribute that contains the text
            panel_renderable = call_args.renderable
            # Convert to string to check for emoji
            renderable_str = str(panel_renderable)
            self.assertIn("😡", renderable_str)
            self.assertIn("HATRED", renderable_str)

    # ==========================================
    # TEST format_coding_text()
    # ==========================================

    def test_format_coding_text_lowercase(self):
        """Test format_coding_text adds 💻 emoji before lowercase 'coding'."""
        text = "You gain +10 coding skills."
        result = Interaction.format_coding_text(text)
        self.assertIn("💻", result)
        self.assertIn("💻 coding", result)

    def test_format_coding_text_uppercase(self):
        """Test format_coding_text adds 💻 emoji before uppercase 'CODING'."""
        text = "You gain +10 CODING SKILLS."
        result = Interaction.format_coding_text(text)
        self.assertIn("💻", result)
        self.assertIn("💻 CODING", result)

    def test_format_coding_text_mixed_case(self):
        """Test format_coding_text adds 💻 emoji before mixed case 'Coding'."""
        text = "Your Coding skill is high."
        result = Interaction.format_coding_text(text)
        self.assertIn("💻", result)
        self.assertIn("💻 Coding", result)

    def test_format_coding_text_multiple_occurrences(self):
        """Test format_coding_text adds 💻 emoji before all 'coding' mentions."""
        text = "Your coding is improving. The coding skills are valuable."
        result = Interaction.format_coding_text(text)
        # Should have 2 emojis (one for each coding)
        self.assertEqual(result.count("💻"), 2)
        self.assertIn("💻 coding", result)

    def test_format_coding_text_coding_skill(self):
        """Test format_coding_text handles 'CODING SKILL' correctly."""
        text = "+ 5 CODING SKILL points."
        result = Interaction.format_coding_text(text)
        self.assertIn("💻", result)
        self.assertIn("💻 CODING", result)

    def test_format_coding_text_no_coding(self):
        """Test format_coding_text doesn't modify text without 'coding'."""
        text = "You gain +1000 CZK."
        result = Interaction.format_coding_text(text)
        self.assertEqual(result, text)
        self.assertNotIn("💻", result)

    def test_format_coding_text_with_rich_markup(self):
        """Test format_coding_text works with Rich markup tags."""
        text = "[green]+ 10 CODING SKILL[/green]"
        result = Interaction.format_coding_text(text)
        self.assertIn("💻", result)
        self.assertIn("💻 CODING", result)
        # Should preserve Rich markup
        self.assertIn("[green]", result)
        self.assertIn("[/green]", result)

    def test_format_coding_text_word_boundary(self):
        """Test format_coding_text only matches 'coding' as whole word."""
        text = "I am encoding data."  # Should not match "encoding"
        result = Interaction.format_coding_text(text)
        self.assertNotIn("💻", result)
        self.assertEqual(result, text)

    # ==========================================
    # TEST format_money_text()
    # ==========================================

    def test_format_money_text_lowercase(self):
        """Test format_money_text adds 💰 emoji before lowercase 'money'."""
        text = "You gain +1000 money."
        result = Interaction.format_money_text(text)
        self.assertIn("💰", result)
        self.assertIn("💰 money", result)

    def test_format_money_text_uppercase(self):
        """Test format_money_text adds 💰 emoji before uppercase 'MONEY'."""
        text = "You gain +1000 MONEY."
        result = Interaction.format_money_text(text)
        self.assertIn("💰", result)
        self.assertIn("💰 MONEY", result)

    def test_format_money_text_mixed_case(self):
        """Test format_money_text adds 💰 emoji before mixed case 'Money'."""
        text = "Your Money amount is high."
        result = Interaction.format_money_text(text)
        self.assertIn("💰", result)
        self.assertIn("💰 Money", result)

    def test_format_money_text_multiple_occurrences(self):
        """Test format_money_text adds 💰 emoji before all 'money' mentions."""
        text = "Your money is increasing. The money helps you survive."
        result = Interaction.format_money_text(text)
        # Should have 2 emojis (one for each money)
        self.assertEqual(result.count("💰"), 2)
        self.assertIn("💰 money", result)

    def test_format_money_text_czk(self):
        """Test format_money_text handles 'CZK' currency correctly."""
        text = "+ 1000 CZK (Salary)."
        result = Interaction.format_money_text(text)
        self.assertIn("💰", result)
        # Should add emoji before CZK when it appears with money context
        self.assertIn("💰", result)

    def test_format_money_text_czk_with_period_separator(self):
        """Test format_money_text handles 'CZK' with period thousands separator."""
        text = "-8.000 CZK, + 25 PCR HATRED."
        result = Interaction.format_money_text(text)
        self.assertIn("💰", result)
        # Should match the full "8.000 CZK" not break it
        self.assertIn("💰 8.000 CZK", result)
        # Should not break the number
        self.assertNotIn("💰 000 CZK", result)

    def test_format_money_text_no_money(self):
        """Test format_money_text doesn't modify text without 'money'."""
        text = "You gain +10 coding skills."
        result = Interaction.format_money_text(text)
        self.assertEqual(result, text)
        self.assertNotIn("💰", result)

    def test_format_money_text_with_rich_markup(self):
        """Test format_money_text works with Rich markup tags."""
        text = "[green]+ 1000 CZK[/green]"
        result = Interaction.format_money_text(text)
        self.assertIn("💰", result)
        # Should preserve Rich markup
        self.assertIn("[green]", result)
        self.assertIn("[/green]", result)

    def test_format_money_text_word_boundary(self):
        """Test format_money_text only matches 'money' as whole word."""
        text = "I am monitoring the system."  # Should not match "monitoring"
        result = Interaction.format_money_text(text)
        self.assertNotIn("💰", result)
        self.assertEqual(result, text)

    def test_show_outcome_formats_coding(self):
        """Test show_outcome automatically formats coding with emoji."""
        with patch('game.game_logic.interaction.print') as mock_print:
            Interaction.show_outcome("+ 10 CODING SKILL.")
            call_args = mock_print.call_args[0][0]
            panel_renderable = call_args.renderable
            renderable_str = str(panel_renderable)
            self.assertIn("💻", renderable_str)
            self.assertIn("CODING", renderable_str)

    def test_show_outcome_formats_money(self):
        """Test show_outcome automatically formats money with emoji."""
        with patch('game.game_logic.interaction.print') as mock_print:
            Interaction.show_outcome("+ 1000 CZK.")
            call_args = mock_print.call_args[0][0]
            panel_renderable = call_args.renderable
            renderable_str = str(panel_renderable)
            self.assertIn("💰", renderable_str)


if __name__ == '__main__':
    unittest.main()

