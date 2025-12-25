"""Comprehensive tests for colonel_event.py missing attack paths to achieve 85%+ coverage."""
import unittest
from unittest.mock import patch, MagicMock

from game.game_logic.colonel_event import ColonelEvent
from game.game_logic.stats import Stats


class TestColonelEventAttacks(unittest.TestCase):
    """Test ColonelEvent attack methods not covered by existing tests."""

    def setUp(self):
        """Setup test fixtures."""
        self.input_patcher = patch('builtins.input', return_value='')
        self.mock_input = self.input_patcher.start()
        self.sleep_patcher = patch('time.sleep')
        self.mock_sleep = self.sleep_patcher.start()
        self.music_patcher = patch.object(ColonelEvent, '_play_music')
        self.mock_music = self.music_patcher.start()
        self.print_patcher = patch.object(ColonelEvent, '_slow_print')
        self.mock_slow_print = self.print_patcher.start()
        self.print_hud_patcher = patch.object(ColonelEvent, '_print_hud')
        self.mock_print_hud = self.print_hud_patcher.start()

        self.event = ColonelEvent()
        self.stats = Stats(available_money=100000, coding_experience=50, pcr_hatred=50)

    def tearDown(self):
        """Clean up patches."""
        self.input_patcher.stop()
        self.sleep_patcher.stop()
        self.music_patcher.stop()
        self.print_patcher.stop()
        self.print_hud_patcher.stop()

    # ==========================================
    # TEST _attack_civilian_void() variants
    # ==========================================

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_civilian_void_coding_fail(self, mock_ask):
        """Test _attack_civilian_void with coding choice but low skill."""
        mock_ask.return_value = "1"
        self.stats.coding_skill = 50  # Below 100 threshold
        initial_jb_hp = self.event.jb_hp

        self.event._attack_civilian_void(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 15)
        self.assertEqual(self.event.colonel_hp, 100)  # No damage to colonel

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_civilian_void_hatred_success(self, mock_ask):
        """Test _attack_civilian_void with hatred choice and high hatred."""
        mock_ask.return_value = "2"
        self.stats.pcr_hatred = 70  # >= 60 threshold
        initial_col_hp = self.event.colonel_hp

        self.event._attack_civilian_void(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 15)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_civilian_void_hatred_fail(self, mock_ask):
        """Test _attack_civilian_void with hatred choice but low hatred."""
        mock_ask.return_value = "2"
        self.stats.pcr_hatred = 40  # Below 60 threshold
        initial_jb_hp = self.event.jb_hp

        self.event._attack_civilian_void(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 10)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_civilian_void_doubt(self, mock_ask):
        """Test _attack_civilian_void with doubt choice (always fails)."""
        mock_ask.return_value = "3"
        initial_jb_hp = self.event.jb_hp

        self.event._attack_civilian_void(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 20)

    # ==========================================
    # TEST _attack_brotherhood()
    # ==========================================

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_brotherhood_with_stoic_anchor(self, mock_ask):
        """Test _attack_brotherhood with STOIC_ANCHOR buff (auto-success)."""
        self.stats.final_boss_buff = "STOIC_ANCHOR"
        initial_col_hp = self.event.colonel_hp

        self.event._attack_brotherhood(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 10)
        mock_ask.assert_not_called()  # Should skip the choice menu

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_brotherhood_cold_high_hatred(self, mock_ask):
        """Test _attack_brotherhood with cold choice and high hatred."""
        mock_ask.return_value = "1"
        self.stats.final_boss_buff = ""
        self.stats.pcr_hatred = 60  # >= 50 threshold
        initial_col_hp = self.event.colonel_hp

        self.event._attack_brotherhood(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 15)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_brotherhood_cold_low_hatred(self, mock_ask):
        """Test _attack_brotherhood with cold choice but low hatred."""
        mock_ask.return_value = "1"
        self.stats.final_boss_buff = ""
        self.stats.pcr_hatred = 30  # Below 50 threshold
        initial_jb_hp = self.event.jb_hp

        self.event._attack_brotherhood(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 15)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_brotherhood_empathy(self, mock_ask):
        """Test _attack_brotherhood with empathy choice (always fails)."""
        mock_ask.return_value = "2"
        self.stats.final_boss_buff = ""
        initial_jb_hp = self.event.jb_hp

        self.event._attack_brotherhood(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 10)

    # ==========================================
    # TEST _attack_safety_net()
    # ==========================================

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_safety_net_money_success(self, mock_ask):
        """Test _attack_safety_net with money choice and high savings."""
        mock_ask.return_value = "1"
        self.stats.available_money = 200000  # >= 150k threshold
        initial_col_hp = self.event.colonel_hp

        self.event._attack_safety_net(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 25)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_safety_net_money_fail(self, mock_ask):
        """Test _attack_safety_net with money choice but low savings."""
        mock_ask.return_value = "1"
        self.stats.available_money = 50000  # Below 150k threshold
        initial_jb_hp = self.event.jb_hp

        self.event._attack_safety_net(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 15)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_safety_net_freedom(self, mock_ask):
        """Test _attack_safety_net with freedom choice (always succeeds)."""
        mock_ask.return_value = "2"
        initial_col_hp = self.event.colonel_hp

        self.event._attack_safety_net(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 10)

    # ==========================================
    # TEST _attack_debt_of_honor()
    # ==========================================

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_debt_of_honor_with_ghost_secret_blackmail(self, mock_ask):
        """Test _attack_debt_of_honor with GHOST_SECRET buff choosing blackmail."""
        mock_ask.return_value = "1"
        self.stats.final_boss_buff = "GHOST_SECRET"
        initial_col_hp = self.event.colonel_hp

        self.event._attack_debt_of_honor(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 40)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_debt_of_honor_with_ghost_secret_defensive(self, mock_ask):
        """Test _attack_debt_of_honor with GHOST_SECRET buff choosing defensive (choice 2 does nothing)."""
        mock_ask.return_value = "2"
        self.stats.final_boss_buff = "GHOST_SECRET"
        initial_col_hp = self.event.colonel_hp

        self.event._attack_debt_of_honor(self.stats)

        # When GHOST_SECRET is set and choice == "2", the code only handles choice == "1" and returns
        # So choice "2" does nothing - HP should remain unchanged
        self.assertEqual(self.event.colonel_hp, initial_col_hp)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_debt_of_honor_defensive(self, mock_ask):
        """Test _attack_debt_of_honor without buff choosing defensive."""
        mock_ask.return_value = "1"
        self.stats.final_boss_buff = ""
        initial_col_hp = self.event.colonel_hp

        self.event._attack_debt_of_honor(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 5)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_debt_of_honor_submit(self, mock_ask):
        """Test _attack_debt_of_honor without buff choosing submit."""
        mock_ask.return_value = "2"
        self.stats.final_boss_buff = ""
        initial_jb_hp = self.event.jb_hp

        self.event._attack_debt_of_honor(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 20)

    # ==========================================
    # TEST _attack_blacklist() variants
    # ==========================================

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_blacklist_confidence_high_skill(self, mock_ask):
        """Test _attack_blacklist with confidence choice and high coding skill."""
        mock_ask.return_value = "1"
        self.stats.final_boss_buff = ""
        self.stats.coding_skill = 60  # >= 50 threshold
        initial_col_hp = self.event.colonel_hp

        self.event._attack_blacklist(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 15)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_blacklist_confidence_low_skill(self, mock_ask):
        """Test _attack_blacklist with confidence choice but low coding skill."""
        mock_ask.return_value = "1"
        self.stats.final_boss_buff = ""
        self.stats.coding_skill = 30  # Below 50 threshold
        initial_jb_hp = self.event.jb_hp

        self.event._attack_blacklist(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 10)

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_blacklist_scare(self, mock_ask):
        """Test _attack_blacklist with scare choice (both take damage)."""
        mock_ask.return_value = "2"
        self.stats.final_boss_buff = ""
        initial_col_hp = self.event.colonel_hp
        initial_jb_hp = self.event.jb_hp

        self.event._attack_blacklist(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 10)
        self.assertEqual(self.event.jb_hp, initial_jb_hp - 5)

    # ==========================================
    # TEST _attack_money_check() variants
    # ==========================================

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_money_check_show_balance(self, mock_ask):
        """Test _attack_money_check with show balance option."""
        mock_ask.return_value = "2"
        self.stats.final_boss_buff = ""
        self.stats.available_money = 300000  # >= 200k
        initial_col_hp = self.event.colonel_hp

        self.event._attack_money_check(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 10)
        self.assertEqual(self.stats.available_money, 300000)  # Money not deducted

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_money_check_insufficient_funds(self, mock_ask):
        """Test _attack_money_check with insufficient funds."""
        mock_ask.return_value = "1"
        self.stats.final_boss_buff = ""
        self.stats.available_money = 50000  # Below 200k threshold
        initial_jb_hp = self.event.jb_hp

        self.event._attack_money_check(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 10)

    # ==========================================
    # TEST _attack_why_quit() with JOB_OFFER
    # ==========================================

    @patch('game.game_logic.colonel_event.Interaction.ask')
    def test_attack_why_quit_job_offer(self, mock_ask):
        """Test _attack_why_quit with JOB_OFFER buff (option 4)."""
        mock_ask.return_value = "4"
        self.stats.final_boss_buff = "JOB_OFFER"
        initial_col_hp = self.event.colonel_hp

        self.event._attack_why_quit(self.stats)

        self.assertEqual(self.event.colonel_hp, initial_col_hp - 20)

    # ==========================================
    # TEST _glitch_phase()
    # ==========================================

    @patch('game.game_logic.colonel_event.input')
    @patch('game.game_logic.colonel_event.GoodEnding')
    @patch('game.game_logic.colonel_event.sys.exit')
    def test_glitch_phase_choose_exit(self, mock_exit, mock_good_ending_cls, mock_input):
        """Test _glitch_phase choosing option 2 (sys.exit())."""
        mock_input.return_value = "2"
        self.event.colonel_hp = 0  # Trigger glitch phase

        self.event._glitch_phase(self.stats)

        mock_good_ending_cls.assert_called_once()
        mock_good_ending_cls.return_value.trigger_ending.assert_called_once()

    @patch('game.game_logic.colonel_event.input')
    @patch('game.game_logic.colonel_event.GoodEnding')
    def test_glitch_phase_choose_argue_then_exit(self, mock_good_ending_cls, mock_input):
        """Test _glitch_phase choosing option 1 then option 2."""
        mock_input.side_effect = ["1", "2"]
        self.event.colonel_hp = 0

        self.event._glitch_phase(self.stats)

        # Should loop once, then exit
        self.assertEqual(mock_input.call_count, 2)
        mock_good_ending_cls.return_value.trigger_ending.assert_called_once()

    @patch('game.game_logic.colonel_event.input')
    @patch('game.game_logic.colonel_event.GoodEnding')
    def test_glitch_phase_invalid_input_then_exit(self, mock_good_ending_cls, mock_input):
        """Test _glitch_phase with invalid input then valid exit."""
        mock_input.side_effect = ["invalid", "2"]
        self.event.colonel_hp = 0

        self.event._glitch_phase(self.stats)

        # Should eventually call GoodEnding after valid input
        mock_good_ending_cls.return_value.trigger_ending.assert_called_once()

    # ==========================================
    # TEST _check_fight_outcome() - Stalemate
    # ==========================================

    @patch('game.game_logic.colonel_event.input')
    @patch.object(ColonelEvent, '_print_hud')
    @patch.object(ColonelEvent, '_slow_print')
    @patch.object(ColonelEvent, '_glitch_phase')
    def test_check_fight_outcome_jb_wins_stalemate(self, mock_glitch, mock_slow_print, mock_hud, mock_input):
        """Test _check_fight_outcome when JB HP >= Colonel HP (stalemate win)."""
        self.event.jb_hp = 80
        self.event.colonel_hp = 50  # JB has more HP

        self.event._check_fight_outcome(self.stats)

        # Should trigger glitch phase (victory)
        mock_glitch.assert_called_once()
        self.assertEqual(self.event.colonel_hp, 0)  # Forced to 0

    @patch('game.game_logic.colonel_event.input')
    @patch.object(ColonelEvent, '_print_hud')
    @patch.object(ColonelEvent, '_slow_print')
    @patch.object(ColonelEvent, '_glitch_phase')
    def test_check_fight_outcome_colonel_wins_stalemate(self, mock_glitch, mock_slow_print, mock_hud, mock_input):
        """Test _check_fight_outcome when JB HP < Colonel HP (stalemate loss)."""
        self.event.jb_hp = 30
        self.event.colonel_hp = 80  # Colonel has more HP

        self.event._check_fight_outcome(self.stats)

        # Should not trigger glitch phase (defeat)
        mock_glitch.assert_not_called()
        # Verify defeat message was printed
        assert mock_slow_print.call_count > 0

    @patch.object(ColonelEvent, '_glitch_phase')
    def test_check_fight_outcome_jb_defeated(self, mock_glitch):
        """Test _check_fight_outcome when JB HP <= 0."""
        self.event.jb_hp = 0
        self.event.colonel_hp = 50

        self.event._check_fight_outcome(self.stats)

        mock_glitch.assert_not_called()

    @patch.object(ColonelEvent, '_glitch_phase')
    def test_check_fight_outcome_colonel_defeated(self, mock_glitch):
        """Test _check_fight_outcome when Colonel HP <= 0."""
        self.event.jb_hp = 50
        self.event.colonel_hp = 0

        self.event._check_fight_outcome(self.stats)

        mock_glitch.assert_called_once_with(self.stats)

    # ==========================================
    # TEST trigger_event() with FIRST_STRIKE
    # ==========================================

    @patch('builtins.input')
    @patch.object(ColonelEvent, '_round_one')
    @patch.object(ColonelEvent, '_round_two')
    @patch.object(ColonelEvent, '_round_three_logic')
    def test_trigger_event_first_strike_buff(self, mock_round3, mock_round2, mock_round1, mock_input):
        """Test trigger_event with FIRST_STRIKE buff."""
        self.stats.final_boss_buff = "FIRST_STRIKE"

        self.event.trigger_event(self.stats)

        self.assertEqual(self.event.colonel_hp, 80)  # -20 HP
        mock_round1.assert_called_once()
        mock_round2.assert_called_once()
        mock_round3.assert_called_once()

    # ==========================================
    # TEST _round_two() variants
    # ==========================================

    @patch('game.game_logic.colonel_event.continue_prompt')
    def test_round_two_imposter_syndrome(self, mock_prompt):
        """Test _round_two with IMPOSTER_SYNDROME debuff."""
        self.stats.final_boss_buff = "IMPOSTER_SYNDROME"
        initial_jb_hp = self.event.jb_hp

        self.event._round_two(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp - 10)

    @patch('game.game_logic.colonel_event.continue_prompt')
    def test_round_two_no_debuff(self, mock_prompt):
        """Test _round_two without debuff."""
        self.stats.final_boss_buff = "STOIC_ANCHOR"
        initial_jb_hp = self.event.jb_hp

        self.event._round_two(self.stats)

        self.assertEqual(self.event.jb_hp, initial_jb_hp)  # No damage


if __name__ == '__main__':
    unittest.main()

