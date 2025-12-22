import unittest
from unittest.mock import patch, MagicMock
from game.game_logic.stats import Stats
from game.game_logic.martin_meeting_event import MMEvent
from game.game_logic.decision_options import Decision

class TestMMEvent(unittest.TestCase):

    def setUp(self):
        """Setup a fresh stats object and event instance before each test."""
        # --- FIX 1: Mock input() to prevent OSError crash ---
        self.input_patcher = patch('builtins.input', return_value='')
        self.mock_input = self.input_patcher.start()

        # --- FIX 2: Mock time.sleep() to make tests run instantly ---
        self.sleep_patcher = patch('time.sleep')
        self.mock_sleep = self.sleep_patcher.start()

        # --- FIX 3: Mock _play_music to avoid audio driver checks/errors ---
        self.music_patcher = patch.object(MMEvent, '_play_music')
        self.mock_music = self.music_patcher.start()

        # Initialize the objects
        self.stats = Stats(available_money=50000, coding_experience=100, pcr_hatred=50)
        self.event = MMEvent()

    def tearDown(self):
        """Stop all patchers after each test to clean up."""
        self.input_patcher.stop()
        self.sleep_patcher.stop()
        self.music_patcher.stop()

    # --- PHASE 1: PREPARATION (Money & Outfits) ---
    @patch('game.game_logic.decision_options.Decision.ask')
    def test_preparation_phase_expensive_outfit(self, mock_ask):
        """Test buying the expensive outfit (Option 1)."""
        mock_ask.return_value = "1"
        self.stats.change_stats_value_money(20000)  # Enough money

        self.event._preparation_phase(self.stats)

        # Should spend 12,500 and gain 2 MM points
        self.assertEqual(self.stats.available_money, 7500)
        self.assertEqual(self.event.mm_points, 2)

    @patch('game.game_logic.decision_options.Decision.ask')
    def test_preparation_phase_expensive_outfit_declined(self, mock_ask):
        """Test trying to buy expensive outfit with no money."""
        mock_ask.return_value = "1"
        self.stats.change_stats_value_money(100)  # Broke

        self.event._preparation_phase(self.stats)

        # Money should be unchanged, MM points 0
        self.assertEqual(self.stats.available_money, 100)
        self.assertEqual(self.event.mm_points, 0)

    # --- PHASE 2: MEETING (Topic Choice) ---
    @patch('game.game_logic.decision_options.Decision.ask')
    def test_meeting_phase_brag_coding(self, mock_ask):
        """Test Option 2: Bragging about Python."""
        mock_ask.return_value = "2"
        initial_skill = self.stats.coding_skill

        self.event._meeting_phase(self.stats)

        # Should gain +25 Coding Skill
        self.assertEqual(self.stats.coding_skill, initial_skill + 25)

    @patch('game.game_logic.decision_options.Decision.ask')
    def test_meeting_phase_listen(self, mock_ask):
        """Test Option 3: Listening."""
        mock_ask.return_value = "3"

        self.event._meeting_phase(self.stats)

        # Should gain +2 MM points (implementation currently increments by 2)
        self.assertEqual(self.event.mm_points, 2)

    # --- PHASE 4: CODING REALITY CHECK ---
    def test_coding_check_god_tier(self):
        """Test outcome for >200 coding skill."""
        self.stats.coding_skill = 210
        self.event._coding_reality_check(self.stats)

        # +2 MM Points, -20 Hatred (Confidence)
        self.assertEqual(self.event.mm_points, 2)
        # Note: In setUp hatred is 50. 50 - 20 = 30.
        self.assertEqual(self.stats.pcr_hatred, 30)

    def test_coding_check_fail(self):
        """Test outcome for <50 coding skill."""
        self.stats.coding_skill = 10
        self.event._coding_reality_check(self.stats)

        # -2 MM Points, +20 Hatred (Shame)
        self.assertEqual(self.event.mm_points, -2)
        self.assertEqual(self.stats.pcr_hatred, 70)

    # --- PHASE 5: FINANCIAL REALITY CHECK ---
    def test_financial_check_rich(self):
        """Test outcome for >200k money."""
        self.stats.change_stats_value_money(250000)
        self.event._financial_reality_check(self.stats)

        # +2 MM Points
        self.assertEqual(self.event.mm_points, 2)

    def test_financial_check_broke(self):
        """Test outcome for <50k money."""
        self.stats.change_stats_value_money(1000)
        self.event._financial_reality_check(self.stats)

        # -2 MM Points
        self.assertEqual(self.event.mm_points, -2)

    # --- PHASE 7: TIMING DECISION ---
    @patch('game.game_logic.decision_options.Decision.ask')
    def test_timing_brave(self, mock_ask):
        """Test choosing to fight tomorrow (Option 1)."""
        mock_ask.return_value = "1"

        self.event._timing_decision_phase(self.stats)

        # Should set boss fight day to 25 and add +2 MM points
        self.assertEqual(self.stats.colonel_day, 25)
        self.assertEqual(self.event.mm_points, 2)

    @patch('game.game_logic.decision_options.Decision.ask')
    def test_timing_wait(self, mock_ask):
        """Test choosing to wait (Option 2)."""
        mock_ask.return_value = "2"

        self.event._timing_decision_phase(self.stats)

        self.assertEqual(self.stats.colonel_day, 30)
        # No points change for waiting
        self.assertEqual(self.event.mm_points, 0)

    # --- PHASE 8: ENDINGS ---
    @patch('game.game_logic.decision_options.Decision.ask')
    def test_good_ending_selection(self, mock_ask):
        """Test achieving >8 points and selecting the 'Legal Nuke'."""
        self.event.mm_points = 10
        mock_ask.return_value = "1"  # Option 1: Legal Nuke

        self.event._ending_phase(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "LEGAL_NUKE")

    def test_neutral_ending_auto(self):
        """Test neutral ending (5-8 points) auto-assigns Stoic Anchor."""
        self.event.mm_points = 6

        self.event._ending_phase(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "STOIC_ANCHOR")

    def test_bad_ending_auto(self):
        """Test bad ending (<5 points) auto-assigns Imposter Syndrome."""
        self.event.mm_points = 0

        self.event._ending_phase(self.stats)

        self.assertEqual(self.stats.final_boss_buff, "IMPOSTER_SYNDROME")


if __name__ == '__main__':
    unittest.main()