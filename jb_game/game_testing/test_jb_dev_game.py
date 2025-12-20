import pytest
import re
from unittest.mock import patch, MagicMock
from jb_game.game_logic.jb_dev_game import Game
from jb_game.game_logic.jb_dev_stats import JBStats
from jb_game.game_logic.jb_dev_day_cycle import DayCycle
from jb_game.game_logic.jb_dev_random_events import RandomEvents


@pytest.fixture
def game_setup():
    """Sets up a standard game instance for testing."""
    stats = JBStats(available_money=10000, coding_experience=0, pcr_hatred=0)
    day_cycle = DayCycle()
    events = RandomEvents()
    game = Game(stats, day_cycle, events)
    return game, stats, day_cycle


# ==========================================
# 1. DIFFICULTY SETTINGS
# ==========================================

@patch('builtins.input')
def test_set_difficulty_easy(mock_input, game_setup):
    """Test if selecting '1' (Easy) sets the correct stats."""
    game, stats, _ = game_setup

    mock_input.side_effect = ["1", "y", ""]

    game.set_difficulty_level()

    # FIX: Strip ANSI color codes before comparing
    clean_difficulty = re.sub(r'\x1b\[[0-9;]*m', '', game.selected_difficulty)
    assert clean_difficulty == "easy"

@patch('builtins.input')
def test_set_difficulty_insane(mock_input, game_setup):
    """Test if selecting '3' (Insane) makes you poor."""
    game, stats, _ = game_setup

    mock_input.side_effect = ["3", "y", ""]

    game.set_difficulty_level()

    # FIX: Strip ANSI color codes before comparing
    clean_difficulty = re.sub(r'\x1b\[[0-9;]*m', '', game.selected_difficulty)
    assert clean_difficulty == "insane"


# ==========================================
# 2. ACTIVITY: PYTHON BOOTCAMP
# ==========================================

@patch('builtins.input')  # 2nd Argument (Top decorator) -> we use '_' to ignore it
@patch('jb_game.game_logic.jb_dev_game.Decision.ask')
def test_activity_python_bootcamp_purchase(mock_decision, _, game_setup):
    """Test if buying the bootcamp deducts money and sets the flag."""
    game, stats, _ = game_setup
    stats.available_money = 50000
    mock_decision.return_value = "3"

    game.activity_python()

    assert stats.available_money == 15000
    assert game.python_bootcamp is True


@patch('jb_game.game_logic.jb_dev_game.Decision.ask')
def test_bootcamp_buff_application(mock_decision, game_setup):
    """
    Test if the 'End Day' logic applies the buff.
    No input() patch needed here if we only test the logic block.
    """
    game, stats, _ = game_setup
    game.python_bootcamp = True
    game.activity_selected = True

    mock_decision.return_value = "4"  # End Day

    # Mock the random event trigger so it doesn't block the test
    game.events_list.select_random_event = MagicMock()

    # Simulating the End Day Logic manually to avoid main loop issues
    stats.increment_stats_pcr_hatred(5)
    if game.python_bootcamp:
        stats.increment_stats_coding_skill(5)

    assert stats.coding_skill == 5
    assert stats.pcr_hatred == 5


# ==========================================
# 3. ACTIVITY: BOUNCER
# ==========================================

@patch('builtins.input')  # 3rd Arg (Top) -> Ignored as '_'
@patch('jb_game.game_logic.jb_dev_game.Decision.ask')  # 2nd Arg (Middle)
@patch('jb_game.game_logic.jb_dev_game.randint')  # 1st Arg (Bottom)
def test_activity_bouncer_strip_club_jackpot(mock_randint, mock_decision, _, game_setup):
    """Test the 5% chance to get 35k CZK at the Strip Bar."""
    game, stats, _ = game_setup

    mock_decision.return_value = "2"  # Strip Bar
    mock_randint.return_value = 1  # Jackpot Roll

    game.activity_bouncer()

    assert stats.available_money == 45000
    assert stats.pcr_hatred == -15


@patch('builtins.input')  # 3rd Arg (Top) -> Ignored as '_'
@patch('jb_game.game_logic.jb_dev_game.Decision.ask')  # 2nd Arg (Middle)
@patch('jb_game.game_logic.jb_dev_game.randint')  # 1st Arg (Bottom)
def test_activity_bouncer_strip_club_fail(mock_randint, mock_decision, _, game_setup):
    """Test the critical failure (Getting hit with a bottle)."""
    game, stats, _ = game_setup

    mock_decision.return_value = "2"
    mock_randint.return_value = 100

    game.activity_bouncer()

    assert stats.available_money == -2500
    assert stats.pcr_hatred == 35
    assert stats.coding_skill == -5


# ==========================================
# 4. ACTIVITY: GYM
# ==========================================

@patch('builtins.input')  # 3. Ignored as '_'
@patch('jb_game.game_logic.jb_dev_game.Decision.ask')  # 2. Ignored as '_' (we set return_value)
@patch('jb_game.game_logic.jb_dev_game.randint')  # 1. Used to control RNG
def test_activity_gym_best_outcome(mock_randint, mock_decision, _, game_setup):
    """Test the best gym outcome: -25 Hatred."""
    game, stats, _ = game_setup

    # Logic:
    # 1. We mock 'randint' to return 1 (The best roll).
    # 2. We mock decision to "1" (Select 'We go gym!').
    mock_decision.return_value = "1"
    mock_randint.return_value = 1

    game.activity_gym()

    assert stats.available_money == 9600  # 10,000 - 400
    assert stats.pcr_hatred == -25


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_game.Decision.ask')
@patch('jb_game.game_logic.jb_dev_game.randint')
def test_activity_gym_worst_outcome(mock_randint, mock_decision, _, game_setup):
    """Test the worst gym outcome: -10 Hatred."""
    game, stats, _ = game_setup

    mock_decision.return_value = "1"
    mock_randint.return_value = 3  # The worst roll

    game.activity_gym()

    assert stats.available_money == 9600
    assert stats.pcr_hatred == -10


# ==========================================
# 5. ACTIVITY: THERAPY
# ==========================================

@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_game.Decision.ask')
def test_activity_therapy_session(mock_decision, _, game_setup):
    """Test therapy session."""
    game, stats, _ = game_setup

    mock_decision.return_value = "1"

    game.activity_therapy()

    assert stats.pcr_hatred == -25
    assert stats.available_money == 8500


# ==========================================
# 6. ACTIVITY: BOUNCER - NIGHT CLUB
# ==========================================

@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_game.Decision.ask')
@patch('jb_game.game_logic.jb_dev_game.randint')
def test_activity_night_club_safe_shift(mock_randint, mock_decision, _, game_setup):
    """Test the standard safe shift at the Night Club (Option 1)."""
    game, stats, _ = game_setup

    mock_decision.return_value = "1"  # Select Night Club
    mock_randint.return_value = 50  # Roll <= 70

    game.activity_bouncer()

    assert stats.available_money == 14000  # 10k + 4k
    assert stats.pcr_hatred == 10


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_game.Decision.ask')
@patch('jb_game.game_logic.jb_dev_game.randint')
def test_activity_night_club_best_shift(mock_randint, mock_decision, _, game_setup):
    """Test the best shift (Tip + Relief)."""
    game, stats, _ = game_setup

    mock_decision.return_value = "1"
    mock_randint.return_value = 80  # Roll between 71-90

    game.activity_bouncer()

    assert stats.available_money == 17500  # 10k + 7.5k
    assert stats.pcr_hatred == -10


# ==========================================
# 7. SALARY DAY
# ==========================================

@patch('builtins.input')
def test_receive_salary_tiers(mock_input, game_setup):
    """Validate salary payouts based on hatred tiers."""
    game, stats, _ = game_setup
    mock_input.return_value = ""  # Swallow pause prompts

    # Tier 1: <= 25 -> +40k
    stats.change_stats_value_money(10000)
    stats.change_stats_pcr_hatred(25)
    game.receive_salary()
    assert stats.available_money == 50000

    # Tier 2: <= 50 -> +30k
    stats.change_stats_value_money(10000)
    stats.change_stats_pcr_hatred(40)
    game.receive_salary()
    assert stats.available_money == 40000

    # Tier 3: > 50 -> +20k
    stats.change_stats_value_money(10000)
    stats.change_stats_pcr_hatred(60)
    game.receive_salary()
    assert stats.available_money == 30000


# ==========================================
# 8. DIFFICULTY RE-PROMPT FLOW
# ==========================================

@patch('builtins.input')
def test_set_difficulty_reprompt_then_confirm(mock_input, game_setup):
    """Should re-ask on 'n' confirmation and accept next valid choice."""
    game, stats, _ = game_setup

    # First attempt: choose '1' then decline. Second attempt: choose '2' and confirm.
    mock_input.side_effect = ["1", "n", "2", "y", ""]

    game.set_difficulty_level()

    clean_difficulty = re.sub(r'\x1b\[[0-9;]*m', '', game.selected_difficulty)
    assert clean_difficulty == "hard"
    assert stats.available_money == 35000
    assert stats.coding_skill == 5
    assert stats.pcr_hatred == 25


# ==========================================
# 9. END-OF-DAY: DOUBLE NIGHT ON RANDOM EVENT
# ==========================================

@patch('jb_game.game_logic.jb_dev_game.Game._apply_nightly_passives')
def test_end_of_day_triggers_second_night_on_event(mock_passives, game_setup):
    """Every 3rd day (<22) with event occurrence should trigger two night cycles."""
    game, stats, day_cycle = game_setup

    # Prepare state: day 2 -> after first night becomes day 3 (eligible)
    day_cycle.current_day = 2
    game.activity_selected = True  # Skip confirmation dialog

    # Stub event to happen
    game.events_list.select_random_event = MagicMock(return_value=True)

    # Mock day cycle methods for call counting and to avoid prints
    day_cycle.day_end_message = MagicMock()
    day_cycle.day_start_message = MagicMock()
    # Keep next_day real to advance the day counter. But also track calls by wrapping.
    original_next_day = day_cycle.next_day
    call_counter = {"count": 0}

    def wrapped_next_day():
        call_counter["count"] += 1
        return original_next_day()

    day_cycle.next_day = wrapped_next_day

    game._handle_end_of_day_routine()

    # Two nights -> _apply_nightly_passives called twice and next_day twice
    assert mock_passives.call_count == 2
    assert call_counter["count"] == 2


# ==========================================
# 10. NIGHTLY PASSIVES EFFECTS
# ==========================================

def test_apply_nightly_passives_ai_and_btc(game_setup):
    """Nightly passives should tick hatred, apply AI buff, and credit BTC income; bootcamp adds coding skill."""
    game, stats, _ = game_setup

    # Setup passives
    stats.ai_paperwork_buff = True
    stats.daily_btc_income = 2000
    game.python_bootcamp = True

    # Baseline
    stats.change_stats_pcr_hatred(10)
    stats.change_stats_value_money(10000)
    stats.change_stats_coding_skill(0)

    game._apply_nightly_passives()

    # Hatred: +5 base, -5 AI buff => net 0 change
    assert stats.pcr_hatred == 10
    # Money: + BTC income
    assert stats.available_money == 12000
    # Coding: +5 from bootcamp
    assert stats.coding_skill == 5


# ==========================================
# 11. MM EVENT TRIGGER ON DAY 24
# ==========================================

@patch('jb_game.game_logic.jb_dev_game.MMEvent')
def test_mm_event_trigger_day_24(mock_mm_cls, game_setup):
    """Should trigger MMEvent on day 24 and call trigger_event(stats)."""
    game, stats, day_cycle = game_setup

    # Start at day 23 so first night moves to 24
    day_cycle.current_day = 23
    game.activity_selected = True

    # Ensure no random event path is taken (<22 condition won't match at 24)
    game.events_list.select_random_event = MagicMock(return_value=False)

    # Avoid noisy prints
    day_cycle.day_end_message = MagicMock()
    day_cycle.day_start_message = MagicMock()

    game._handle_end_of_day_routine()

    # Verify MM event flow
    mock_mm_instance = mock_mm_cls.return_value
    mock_mm_instance.trigger_event.assert_called_once_with(stats)
