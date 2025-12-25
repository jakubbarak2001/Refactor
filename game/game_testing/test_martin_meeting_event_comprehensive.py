"""Comprehensive tests for martin_meeting_event.py missing phases to achieve 85%+ coverage."""
import unittest
from unittest.mock import patch, MagicMock

from game.game_logic.martin_meeting_event import MartinMeetingEvent
from game.game_logic.stats import Stats


class TestMartinMeetingEventComprehensive(unittest.TestCase):
    """Test MartinMeetingEvent methods not covered by existing tests."""

    def setUp(self):
        """Setup test fixtures."""
        self.input_patcher = patch('builtins.input', return_value='')
        self.mock_input = self.input_patcher.start()
        self.sleep_patcher = patch('time.sleep')
        self.mock_sleep = self.sleep_patcher.start()
        self.music_patcher = patch.object(MartinMeetingEvent, '_play_music')
        self.mock_music = self.music_patcher.start()

        self.stats = Stats(available_money=50000, coding_experience=100, pcr_hatred=50)
        self.event = MartinMeetingEvent()

    def tearDown(self):
        """Clean up patches."""
        self.input_patcher.stop()
        self.sleep_patcher.stop()
        self.music_patcher.stop()

    # ==========================================
    # TEST _drop_the_bomb_phase()
    # ==========================================

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch.object(MartinMeetingEvent, '_play_music')
    def test_drop_the_bomb_phase_high_hatred(self, mock_music, mock_slow_print, mock_prompt):
        """Test _drop_the_bomb_phase with hatred >= 60 (relief message only, no stat change)."""
        self.stats.pcr_hatred = 70
        initial_hatred = self.stats.pcr_hatred

        self.event._drop_the_bomb_phase(self.stats)

        # >= 60: Only prints relief message, doesn't modify hatred
        self.assertEqual(self.stats.pcr_hatred, initial_hatred)
        mock_music.assert_called_once_with("martin_meeting_event_the_awakening.mp3")

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch.object(MartinMeetingEvent, '_play_music')
    def test_drop_the_bomb_phase_low_hatred(self, mock_music, mock_slow_print, mock_prompt):
        """Test _drop_the_bomb_phase with hatred < 60 (increases hatred)."""
        self.stats.pcr_hatred = 40
        initial_hatred = self.stats.pcr_hatred

        self.event._drop_the_bomb_phase(self.stats)

        # < 60: Should increase hatred by 15
        self.assertEqual(self.stats.pcr_hatred, initial_hatred + 15)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch.object(MartinMeetingEvent, '_play_music')
    def test_drop_the_bomb_phase_boundary_60(self, mock_music, mock_slow_print, mock_prompt):
        """Test _drop_the_bomb_phase with hatred exactly 60 (>= 60, so no stat change)."""
        self.stats.pcr_hatred = 60
        initial_hatred = self.stats.pcr_hatred

        self.event._drop_the_bomb_phase(self.stats)

        # Exactly 60: >= 60 means relief message only, no hatred change
        self.assertEqual(self.stats.pcr_hatred, initial_hatred)

    # ==========================================
    # TEST _coding_reality_check() intermediate tiers
    # ==========================================

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    def test_coding_reality_check_tier_150_199(self, mock_print, mock_slow_print, mock_prompt):
        """Test _coding_reality_check with skill 150-199 (Senior)."""
        self.stats.coding_skill = 175
        initial_points = self.event.martin_meeting_affection_points

        self.event._coding_reality_check(self.stats)

        # Should gain 1 point and reduce hatred by 10
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points + 1)
        self.assertEqual(self.stats.pcr_hatred, 40)  # 50 - 10

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    def test_coding_reality_check_tier_100_149(self, mock_print, mock_slow_print, mock_prompt):
        """Test _coding_reality_check with skill 100-149 (Junior)."""
        self.stats.coding_skill = 125
        initial_points = self.event.martin_meeting_affection_points

        self.event._coding_reality_check(self.stats)

        # Should gain 0 points (neutral)
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points)
        self.assertEqual(self.stats.pcr_hatred, 50)  # No change

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    def test_coding_reality_check_tier_50_99(self, mock_print, mock_slow_print, mock_prompt):
        """Test _coding_reality_check with skill 50-99 (Intermediate)."""
        self.stats.coding_skill = 75
        initial_points = self.event.martin_meeting_affection_points

        self.event._coding_reality_check(self.stats)

        # Should lose 1 point and increase hatred by 10
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points - 1)
        self.assertEqual(self.stats.pcr_hatred, 60)  # 50 + 10

    # ==========================================
    # TEST _financial_reality_check() intermediate tiers
    # ==========================================

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    def test_financial_reality_check_150k_199k(self, mock_print, mock_slow_print, mock_prompt):
        """Test _financial_reality_check with 150k-199k money."""
        self.stats.change_stats_value_money(175000)
        initial_points = self.event.martin_meeting_affection_points

        self.event._financial_reality_check(self.stats)

        # Should gain 1 point
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points + 1)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    def test_financial_reality_check_100k_149k(self, mock_print, mock_slow_print, mock_prompt):
        """Test _financial_reality_check with 100k-149k money (neutral)."""
        self.stats.change_stats_value_money(125000)
        initial_points = self.event.martin_meeting_affection_points

        self.event._financial_reality_check(self.stats)

        # Should gain 0 points (neutral)
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    def test_financial_reality_check_50k_99k(self, mock_print, mock_slow_print, mock_prompt):
        """Test _financial_reality_check with 50k-99k money."""
        self.stats.change_stats_value_money(75000)
        initial_points = self.event.martin_meeting_affection_points

        self.event._financial_reality_check(self.stats)

        # Should lose 1 point
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points - 1)

    # ==========================================
    # TEST _hatred_motivation_check()
    # ==========================================

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_hatred_motivation_check_pure_rage(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _hatred_motivation_check with option 1 (Pure Rage)."""
        mock_ask.return_value = "1"
        initial_points = self.event.martin_meeting_affection_points
        initial_hatred = self.stats.pcr_hatred

        self.event._hatred_motivation_check(self.stats)

        # Should gain 2 points and increase hatred by 25
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points + 2)
        self.assertEqual(self.stats.pcr_hatred, initial_hatred + 25)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_hatred_motivation_check_hatred(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _hatred_motivation_check with option 2 (Hatred)."""
        mock_ask.return_value = "2"
        initial_points = self.event.martin_meeting_affection_points
        initial_hatred = self.stats.pcr_hatred

        self.event._hatred_motivation_check(self.stats)

        # Should gain 1 point and increase hatred by 10
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points + 1)
        self.assertEqual(self.stats.pcr_hatred, initial_hatred + 10)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_hatred_motivation_check_neutral(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _hatred_motivation_check with option 3 (Neutral)."""
        mock_ask.return_value = "3"
        initial_points = self.event.martin_meeting_affection_points
        initial_hatred = self.stats.pcr_hatred

        self.event._hatred_motivation_check(self.stats)

        # Should gain 0 points and no hatred change
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points)
        self.assertEqual(self.stats.pcr_hatred, initial_hatred)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_hatred_motivation_check_soft(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _hatred_motivation_check with option 4 (Soft)."""
        mock_ask.return_value = "4"
        initial_points = self.event.martin_meeting_affection_points
        initial_hatred = self.stats.pcr_hatred

        self.event._hatred_motivation_check(self.stats)

        # Should lose 1 point and reduce hatred by 25
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points - 1)
        self.assertEqual(self.stats.pcr_hatred, initial_hatred - 25)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_hatred_motivation_check_coping(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _hatred_motivation_check with option 5 (Coping)."""
        mock_ask.return_value = "5"
        initial_points = self.event.martin_meeting_affection_points
        initial_hatred = self.stats.pcr_hatred

        self.event._hatred_motivation_check(self.stats)

        # Should lose 2 points and reduce hatred by 50
        self.assertEqual(self.event.martin_meeting_affection_points, initial_points - 2)
        self.assertEqual(self.stats.pcr_hatred, initial_hatred - 50)

    # ==========================================
    # TEST _good_ending_selection() all choices
    # ==========================================

    @patch('builtins.print')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_good_ending_selection_legal_nuke(self, mock_ask, mock_slow_print, mock_print):
        """Test _good_ending_selection with option 1 (LEGAL_NUKE)."""
        mock_ask.return_value = "1"
        self.event.martin_meeting_affection_points = 10  # >= 8

        self.event._good_ending_selection(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "LEGAL_NUKE")

    @patch('builtins.print')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_good_ending_selection_ghost_secret(self, mock_ask, mock_slow_print, mock_print):
        """Test _good_ending_selection with option 2 (GHOST_SECRET)."""
        mock_ask.return_value = "2"
        self.event.martin_meeting_affection_points = 10

        self.event._good_ending_selection(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "GHOST_SECRET")

    @patch('builtins.print')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_good_ending_selection_job_offer(self, mock_ask, mock_slow_print, mock_print):
        """Test _good_ending_selection with option 3 (JOB_OFFER)."""
        mock_ask.return_value = "3"
        self.event.martin_meeting_affection_points = 10

        self.event._good_ending_selection(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "JOB_OFFER")

    @patch('builtins.print')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_good_ending_selection_stoic_heal(self, mock_ask, mock_slow_print, mock_print):
        """Test _good_ending_selection with option 4 (STOIC_HEAL)."""
        mock_ask.return_value = "4"
        self.event.martin_meeting_affection_points = 10

        self.event._good_ending_selection(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "STOIC_HEAL")

    @patch('builtins.print')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_good_ending_selection_first_strike(self, mock_ask, mock_slow_print, mock_print):
        """Test _good_ending_selection with option 5 (FIRST_STRIKE)."""
        mock_ask.return_value = "5"
        self.event.martin_meeting_affection_points = 10

        self.event._good_ending_selection(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "FIRST_STRIKE")

    # ==========================================
    # TEST _ending_phase() with different affection scores
    # ==========================================

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch.object(MartinMeetingEvent, '_good_ending_selection')
    def test_ending_phase_good_ending(self, mock_good_selection, mock_slow_print, mock_prompt):
        """Test _ending_phase with affection >= 8 (good ending)."""
        self.event.martin_meeting_affection_points = 9

        self.event._ending_phase(self.stats)

        mock_good_selection.assert_called_once_with(self.stats)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch.object(MartinMeetingEvent, '_good_ending_selection')
    def test_ending_phase_neutral_ending(self, mock_good_selection, mock_slow_print, mock_prompt):
        """Test _ending_phase with affection 5-8 (neutral ending)."""
        self.event.martin_meeting_affection_points = 6

        self.event._ending_phase(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "STOIC_ANCHOR")
        mock_good_selection.assert_not_called()

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch.object(MartinMeetingEvent, '_good_ending_selection')
    def test_ending_phase_bad_ending(self, mock_good_selection, mock_slow_print, mock_prompt):
        """Test _ending_phase with affection < 5 (bad ending)."""
        self.event.martin_meeting_affection_points = 3

        self.event._ending_phase(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "IMPOSTER_SYNDROME")
        mock_good_selection.assert_not_called()

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch.object(MartinMeetingEvent, '_good_ending_selection')
    def test_ending_phase_boundary_8(self, mock_good_selection, mock_slow_print, mock_prompt):
        """Test _ending_phase with affection exactly 8 (should be good ending)."""
        self.event.martin_meeting_affection_points = 8

        self.event._ending_phase(self.stats)

        mock_good_selection.assert_called_once_with(self.stats)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch.object(MartinMeetingEvent, '_good_ending_selection')
    def test_ending_phase_boundary_5(self, mock_good_selection, mock_slow_print, mock_prompt):
        """Test _ending_phase with affection exactly 5 (should be neutral ending)."""
        self.event.martin_meeting_affection_points = 5

        self.event._ending_phase(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "STOIC_ANCHOR")
        mock_good_selection.assert_not_called()

    # ==========================================
    # TEST _preparation_phase() option 2
    # ==========================================

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_preparation_phase_medium_outfit_success(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _preparation_phase with option 2 and enough money."""
        mock_ask.return_value = "2"
        self.stats.change_stats_value_money(5000)  # Enough for 2500

        self.event._preparation_phase(self.stats)

        self.assertEqual(self.stats.available_money, 2500)
        self.assertEqual(self.event.martin_meeting_affection_points, 1)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_preparation_phase_medium_outfit_insufficient(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _preparation_phase with option 2 but insufficient money."""
        mock_ask.return_value = "2"
        self.stats.change_stats_value_money(1000)  # Not enough

        self.event._preparation_phase(self.stats)

        self.assertEqual(self.stats.available_money, 1000)  # Unchanged
        self.assertEqual(self.event.martin_meeting_affection_points, 0)

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_preparation_phase_no_outfit(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _preparation_phase with option 3 (go as is)."""
        mock_ask.return_value = "3"

        self.event._preparation_phase(self.stats)

        self.assertEqual(self.event.martin_meeting_affection_points, 0)

    # ==========================================
    # TEST _meeting_phase() option 1
    # ==========================================

    @patch('game.game_logic.martin_meeting_event.continue_prompt')
    @patch.object(MartinMeetingEvent, '_slow_print')
    @patch('builtins.print')
    @patch('game.game_logic.interaction.Interaction.ask')
    def test_meeting_phase_vent_out(self, mock_ask, mock_print, mock_slow_print, mock_prompt):
        """Test _meeting_phase with option 1 (Vent out)."""
        mock_ask.return_value = "1"
        initial_hatred = self.stats.pcr_hatred

        self.event._meeting_phase(self.stats)

        # Should reduce hatred by 50
        self.assertEqual(self.stats.pcr_hatred, initial_hatred - 50)


if __name__ == '__main__':
    unittest.main()

