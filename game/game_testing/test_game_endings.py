import pytest
from unittest.mock import patch
from game.game_logic.game_rules import Game
from game.game_logic.stats import Stats
from game.game_logic.day_cycle import DayCycle
from game.game_logic.random_events import RandomEvents


@pytest.fixture
def game_setup():
    stats = Stats(available_money=10000, coding_experience=0, pcr_hatred=0)
    day_cycle = DayCycle()
    events = RandomEvents()
    game = Game(stats, day_cycle, events)
    return game, stats


# ==========================================
# 1. PSYCHOSIS ENDING (Hatred >= 100)
# ==========================================

@patch('game.game_logic.game_rules.GameEndings')
def test_game_over_psychosis(mock_endings, game_setup):
    """
    Scenario: Hatred hits 100.
    Expectation: The 'mental_breakdown_ending' method MUST be called.
    """
    game, stats = game_setup

    # 1. Set Critical State
    stats.pcr_hatred = 100

    # 2. Trigger Check
    game.check_game_status()

    # 3. Verify the ending triggered
    mock_endings.mental_breakdown_ending.assert_called_once_with(stats)


@patch('game.game_logic.game_rules.GameEndings')
def test_game_over_psychosis_boundary(mock_endings, game_setup):
    """
    Scenario: Hatred is 99 (Safe) vs 101 (Dead).
    Expectation: 99 does nothing, 101 triggers death.
    """
    game, stats = game_setup

    # Case A: 99 Hatred (Safe)
    stats.pcr_hatred = 99
    game.check_game_status()
    mock_endings.mental_breakdown_ending.assert_not_called()

    # Case B: 101 Hatred (Dead)
    stats.pcr_hatred = 101
    game.check_game_status()
    mock_endings.mental_breakdown_ending.assert_called_once()


# ==========================================
# 2. BANKRUPTCY ENDING (Money <= 0)
# ==========================================

@patch('game.game_logic.game_rules.GameEndings')
def test_game_over_bankruptcy(mock_endings, game_setup):
    """
    Scenario: Money hits 0.
    Expectation: The 'homeless_ending' method MUST be called.
    """
    game, stats = game_setup

    stats.available_money = 0

    game.check_game_status()

    mock_endings.homeless_ending.assert_called_once_with(stats)


@patch('game.game_logic.game_rules.GameEndings')
def test_game_over_bankruptcy_negative(mock_endings, game_setup):
    """
    Scenario: Debt (Negative Money).
    Expectation: Still triggers homeless ending.
    """
    game, stats = game_setup

    stats.available_money = -500

    game.check_game_status()

    mock_endings.homeless_ending.assert_called_once()


# ==========================================
# 3. WARNING SYSTEMS (UI Checks)
# ==========================================

def test_warning_high_hatred(game_setup, capsys):
    """
    Scenario: Hatred is 75 (High, but not dead).
    Expectation: Prints a specific warning to console.
    """
    game, stats = game_setup
    stats.pcr_hatred = 75

    game.check_game_status()

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "HATRED AT 75%" in captured.out


def test_warning_low_money(game_setup, capsys):
    """
    Scenario: Money is 4000 (Low, but not broke).
    Expectation: Prints a low funds warning.
    """
    game, stats = game_setup
    stats.available_money = 4000

    game.check_game_status()

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "LOW FUNDS" in captured.out