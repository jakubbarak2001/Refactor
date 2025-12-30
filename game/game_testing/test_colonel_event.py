import unittest
from unittest.mock import patch, MagicMock

from game.game_logic.colonel_event import ColonelEvent
from game.game_logic.stats import Stats


class TestColonelEvent(unittest.TestCase):
    def setUp(self):
        # Patch input to auto-advance prompts
        self.input_patcher = patch('builtins.input', return_value='')
        self.mock_input = self.input_patcher.start()
        # Patch time.sleep to speed up tests
        self.sleep_patcher = patch('time.sleep')
        self.mock_sleep = self.sleep_patcher.start()
        # Instance and default stats
        self.event = ColonelEvent()
        self.stats = Stats(available_money=10000, coding_experience=0, pcr_hatred=0)

    def tearDown(self):
        self.input_patcher.stop()
        self.sleep_patcher.stop()

    # 1. Passive buff LEGAL_NUKE reduces Colonel HP at start
    @patch('builtins.input', return_value='')
    def test_trigger_event_initial_passive_legal_nuke(self, _):
        self.stats.final_boss_buff = 'LEGAL_NUKE'
        # Stub inner rounds to avoid long flow
        self.event._round_one = MagicMock()
        self.event._round_two = MagicMock()
        self.event._round_three_logic = MagicMock()

        self.event.trigger_event(self.stats)

        self.assertEqual(self.event.colonel_hp, 65)

    # 2. Round one applies anxiety hit when no good buffs
    @patch('builtins.input', return_value='')
    def test_round_one_anxiety_damage_without_buff(self, _):
        self.stats.final_boss_buff = 'IMPOSTER_SYNDROME'
        self.event._round_one(self.stats)
        self.assertEqual(self.event.jb_hp, 90)

    # 3. Round one no damage when under good buffs
    @patch('builtins.input', return_value='')
    def test_round_one_defense_with_good_buff(self, _):
        self.stats.final_boss_buff = 'STOIC_ANCHOR'
        self.event._round_one(self.stats)
        self.assertEqual(self.event.jb_hp, 100)

    # 4. Money check attack: LEGAL_NUKE auto-counter deals 15 and skips choices
    def test_attack_money_check_legal_nuke_auto(self):
        self.stats.final_boss_buff = 'LEGAL_NUKE'
        start_hp = self.event.colonel_hp
        self.event._attack_money_check(self.stats)
        self.assertEqual(self.event.colonel_hp, start_hp - 15)

    # 5. Money check with high savings: choose pay 80k deals 20 and deducts money
    @patch('game.game_logic.interaction.Interaction.ask', return_value='1')
    def test_attack_money_check_pay_80k(self, mock_ask):
        self.stats.final_boss_buff = ''
        self.stats.available_money = 300000
        start_col_hp = self.event.colonel_hp
        self.event._attack_money_check(self.stats)
        self.assertEqual(self.stats.available_money, 220000)
        self.assertEqual(self.event.colonel_hp, start_col_hp - 20)

    # 6. Motivation check success path scales damage by chance
    @patch('game.game_logic.colonel_event.random.randint', return_value=10)
    @patch('game.game_logic.interaction.Interaction.ask', return_value='2')
    def test_attack_why_quit_success_damage_scaled(self, _, __):
        self.stats.coding_skill = 100
        start_col_hp = self.event.colonel_hp
        self.event._attack_why_quit(self.stats)
        self.assertEqual(self.event.colonel_hp, start_col_hp - 20)

    # 7. Motivation check failure deals 20 to JB
    @patch('game.game_logic.colonel_event.random.randint', return_value=100)
    @patch('game.game_logic.interaction.Interaction.ask', return_value='3')
    def test_attack_why_quit_failure_hurts_jb(self, _, __):
        self.stats.available_money = 0  # chance_money 0 -> fail
        self.event._attack_why_quit(self.stats)
        self.assertEqual(self.event.jb_hp, 80)

    # 8. Civilian void: coding success when skill >= 100
    @patch('game.game_logic.interaction.Interaction.ask', return_value='1')
    def test_attack_civilian_void_coding_success(self, _):
        self.stats.coding_skill = 120
        start_col_hp = self.event.colonel_hp
        self.event._attack_civilian_void(self.stats)
        self.assertEqual(self.event.colonel_hp, start_col_hp - 20)

    # 9. Blacklist with JOB_OFFER auto-critical -30
    def test_attack_blacklist_job_offer_auto(self):
        self.stats.final_boss_buff = 'JOB_OFFER'
        start_col_hp = self.event.colonel_hp
        self.event._attack_blacklist(self.stats)
        self.assertEqual(self.event.colonel_hp, start_col_hp - 30)

    # 10. Glitch phase resets colonel HP to 100 and calls GoodEnding on choosing sys.exit path
    @patch('builtins.input')
    @patch('sys.exit')  # Safety net: Catch exit if it happens
    @patch('game.game_logic.colonel_event.GoodEnding')  # <--- FIXED PATH
    def test_glitch_phase_flow_and_good_ending(self, mock_good_cls, mock_exit, mock_input):
        # NOTE: Argument order is reversed from decorators:
        # 1. ColonelEvent.GoodEnding (Bottom) -> mock_good_cls
        # 2. sys.exit (Middle) -> mock_exit
        # 3. builtins.input (Top) -> mock_input

        # Simulate choosing '2' immediately
        mock_input.side_effect = ['2', '']

        # Put colonel to 0 to trigger glitch
        self.event.colonel_hp = 0

        # Trigger check -> glitch -> good ending chosen
        self.event._check_fight_outcome(self.stats)

        # Assertions
        mock_good_cls.assert_called_once()
        mock_good_cls.return_value.trigger_ending.assert_called_once()

    # 11. Defeat ending path when JB HP <= 0
    @patch.object(ColonelEvent, '_slow_print')
    @patch('game.game_logic.colonel_event.continue_prompt')
    @patch.object(ColonelEvent, '_glitch_phase')
    def test_check_fight_outcome_jb_defeated_path(self, mock_glitch, mock_prompt, mock_slow_print):
        """Test that _check_fight_outcome takes defeat path when JB HP <= 0."""
        # Set JB HP to 0 (defeat condition)
        self.event.jb_hp = 0
        self.event.colonel_hp = 50

        # Trigger check -> should not trigger glitch phase (defeat path instead)
        self.event._check_fight_outcome(self.stats)

        # Verify glitch phase is NOT called (defeat path instead)
        mock_glitch.assert_not_called()
        # Verify defeat message was printed
        assert mock_slow_print.called


if __name__ == '__main__':
    unittest.main()
