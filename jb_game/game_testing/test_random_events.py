import pytest
from unittest.mock import patch
from jb_game.game_logic.jb_dev_random_events import RandomEvents
from jb_game.game_logic.jb_dev_stats import JBStats


@pytest.fixture
def events():
    return RandomEvents()


@pytest.fixture
def stats():
    return JBStats(available_money=10000, coding_experience=0, pcr_hatred=0)


# ==========================================
# 1. OVERTIME EVENT
# ==========================================

@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
@patch('jb_game.game_logic.jb_dev_random_events.randint')
def test_event_overtime_take_money(mock_randint, mock_decision, _, events, stats):
    # Note the '_' above. It replaces 'mock_input'
    mock_decision.return_value = '1'
    mock_randint.return_value = 5000
    events.random_event_overtime_offer(stats)
    assert stats.available_money == 15000


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
@patch('jb_game.game_logic.jb_dev_random_events.randint')
def test_event_overtime_study_python(mock_randint, mock_decision, _, events, stats):
    mock_decision.return_value = '2'
    mock_randint.return_value = 20
    events.random_event_overtime_offer(stats)
    assert stats.coding_experience == 20


# ==========================================
# 2. BIRTHDAY EVENT
# ==========================================

@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
def test_event_birthday_pay(mock_decision, _, events, stats):
    mock_decision.return_value = '1'
    events.random_event_birthday_gift(stats)
    assert stats.available_money == 9000
    assert stats.pcr_hatred == 5


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
def test_event_birthday_refuse(mock_decision, _, events, stats):
    mock_decision.return_value = '2'
    events.random_event_birthday_gift(stats)
    assert stats.pcr_hatred == 15


# ==========================================
# 3. CIVILIAN SMALL TALK
# ==========================================

@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
@patch('jb_game.game_logic.jb_dev_random_events.randint')
def test_event_small_talk_vent_success(mock_randint, mock_decision, _, events, stats):
    """Scenario: Vent out (1) and succeed (Roll <= 80)."""
    mock_decision.return_value = '1'
    mock_randint.return_value = 50
    stats.pcr_hatred = 50

    events.random_event_civilian_small_talk(stats)
    assert stats.pcr_hatred == 25


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
@patch('jb_game.game_logic.jb_dev_random_events.randint')
def test_event_small_talk_vent_fail(mock_randint, mock_decision, _, events, stats):
    """Scenario: Vent out (1) and fail (Roll > 80)."""
    mock_decision.return_value = '1'
    mock_randint.return_value = 90

    events.random_event_civilian_small_talk(stats)
    assert stats.pcr_hatred == 25
    assert stats.available_money == 7500


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
def test_event_small_talk_keep_inside(mock_decision, _, events, stats):
    mock_decision.return_value = '2'
    events.random_event_civilian_small_talk(stats)
    assert stats.pcr_hatred == 10


# ==========================================
# 4. CORPSE IN CARE HOME
# ==========================================

@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
@patch('jb_game.game_logic.jb_dev_random_events.randint')
def test_event_corpse_refuse_success(mock_randint, mock_decision, _, events, stats):
    mock_decision.return_value = '1'
    mock_randint.return_value = 20
    events.random_event_corpse_in_care_home(stats)
    # Based on code logic: Prints "0 PCR HATRED" but does not subtract existing.
    # If stats started at 0, adding +10 for entering room means result is 10.
    assert stats.pcr_hatred == 10


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
@patch('jb_game.game_logic.jb_dev_random_events.randint')
def test_event_corpse_drag_disaster(mock_randint, mock_decision, _, events, stats):
    mock_decision.return_value = '2'
    mock_randint.return_value = 3
    events.random_event_corpse_in_care_home(stats)
    # Enter room (+10) + Disaster (+30) = 40
    assert stats.pcr_hatred == 40


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
@patch('jb_game.game_logic.jb_dev_random_events.randint')
def test_event_corpse_refuse_fail_then_ok(mock_randint, mock_decision, _, events, stats):
    mock_decision.return_value = '1'
    # side_effect: First roll=80 (Refuse Fail), Second roll=90 (Drag Safe)
    mock_randint.side_effect = [80, 90]

    events.random_event_corpse_in_care_home(stats)
    # Enter (+10) + Fail Refuse (+5) + Drag Safe (+20) = 35
    assert stats.pcr_hatred == 35


# ==========================================
# 5. ADMIN MISTAKE
# ==========================================

@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
def test_event_admin_mistake_leave(mock_decision, _, events, stats):
    mock_decision.return_value = '1'
    stats.pcr_hatred = 20
    events.random_event_admin_mistake_after_shift(stats)
    assert stats.available_money == 7500
    assert stats.pcr_hatred == 10


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
def test_event_admin_mistake_stay(mock_decision, _, events, stats):
    mock_decision.return_value = '2'
    events.random_event_admin_mistake_after_shift(stats)
    assert stats.pcr_hatred == 20


# ==========================================
# 6. ISRAELI DEVELOPER
# ==========================================

@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
def test_event_dev_low_skill(mock_decision, _, events, stats):
    stats.coding_experience = 10
    mock_decision.return_value = '2'
    events.random_event_israeli_developer(stats)
    assert stats.coding_experience == 20


@patch('builtins.input')
@patch('jb_game.game_logic.jb_dev_random_events.Decision.ask')
def test_event_dev_high_skill_success(mock_decision, _, events, stats):
    stats.coding_experience = 60
    mock_decision.return_value = '1'
    events.random_event_israeli_developer(stats)
    assert stats.coding_experience == 90


# ==========================================
# 7. NIGHTMARE WOLF
# ==========================================

@patch('builtins.input')
def test_event_nightmare_wolf(_, events, stats):
    # Only patched 'input', so only one '_' needed
    events.random_event_nightmare_wolf(stats)
    assert stats.pcr_hatred == 20