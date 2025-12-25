from unittest.mock import patch

import pytest

from game.game_logic.car_incident_event import CarIncident
from game.game_logic.stats import Stats


@pytest.fixture
def stats():
    """Start with enough money so penalties don't make it negative immediately."""
    return Stats(available_money=20000, coding_experience=0, pcr_hatred=0)


# ==========================================
# PATH 1: The "Good Soldier" (Confession)
# ==========================================
@patch('builtins.input')
@patch('game.game_logic.car_incident_event.Interaction.ask')
def test_incident_confession(mock_decision, _, stats):
    """
    Scenario: Player chooses Option 2 (Confess).
    Outcome: - 2000 Money, +10 Hatred.
    """
    mock_decision.return_value = "2"  # Select "Safe" option

    CarIncident.car_incident_event(stats)

    assert stats.available_money == 18000  # 20,000 - 2,000
    assert stats.pcr_hatred == 10


# ==========================================
# PATH 2: The "MacGyver" (Cover Up) - SUCCESS
# ==========================================
@patch('builtins.input')
@patch('game.game_logic.car_incident_event.Interaction.ask')
@patch('game.game_logic.car_incident_event.randint')
def test_incident_coverup_success(mock_randint, mock_decision, _, stats):
    """
    Scenario: Player chooses Option 1 (Cover Up) AND Rolls Success (<= 50).
    Outcome: 0 Money Lost, -5 Hatred.
    """
    mock_decision.return_value = "1"
    mock_randint.return_value = 10  # Roll <= 50 (Success)

    CarIncident.car_incident_event(stats)

    assert stats.available_money == 20000  # No change
    assert stats.pcr_hatred == -5


# ==========================================
# PATH 3: Cover Up Fails -> Caught -> SUBMIT
# ==========================================
@patch('builtins.input')
@patch('game.game_logic.car_incident_event.Interaction.ask')
@patch('game.game_logic.car_incident_event.randint')
def test_incident_caught_submit(mock_randint, mock_decision, _, stats):
    """
    Scenario:
    1. Cover Up Fails (Roll > 50).
    2. Player chooses Option 1 (Submit/Pay Fine).
    Outcome: -8000 Money, +25 Hatred.
    """
    # Decision 1: Cover Up ("1")
    # Decision 2: Submit ("1")
    mock_decision.side_effect = ["1", "1"]

    # RNG: Roll > 50 (Failure)
    mock_randint.return_value = 80

    CarIncident.car_incident_event(stats)

    assert stats.available_money == 12000  # 20,000 - 8,000
    assert stats.pcr_hatred == 25


# ==========================================
# PATH 4: Cover Up Fails -> Caught -> PAUL GOODMAN (WIN)
# ==========================================
@patch('builtins.input')
@patch('game.game_logic.car_incident_event.Interaction.ask')
@patch('game.game_logic.car_incident_event.randint')
def test_incident_paul_goodman_win(mock_randint, mock_decision, _, stats):
    """
    Scenario:
    1. Cover Up Fails (Roll > 50).
    2. Player chooses Option 2 (Call Paul).
    3. Paul Wins Case (Roll <= 30).
    Outcome: + 15,000 Money, -30 Hatred.
    """
    # Decision 1: Cover Up ("1")
    # Decision 2: Call Paul ("2")
    mock_decision.side_effect = ["1", "2"]

    mock_randint.side_effect = [90, 30]

    CarIncident.car_incident_event(stats)

    assert stats.available_money == 35000  # 20,000 + 15,000
    assert stats.pcr_hatred == -30


# ==========================================
# PATH 5: Cover Up Fails -> Caught -> PAUL GOODMAN (LOSS)
# ==========================================
@patch('builtins.input')
@patch('game.game_logic.car_incident_event.Interaction.ask')
@patch('game.game_logic.car_incident_event.randint')
def test_incident_paul_goodman_loss(mock_randint, mock_decision, _, stats):
    """
    Scenario:
    1. Cover Up Fails (Roll > 50).
    2. Player chooses Option 2 (Call Paul).
    3. Paul Loses Case (Roll > 30).
    Outcome: -12,000 Money, +50 Hatred.
    """
    # Decision 1: Cover Up ("1")
    # Decision 2: Call Paul ("2")
    mock_decision.side_effect = ["1", "2"]

    mock_randint.side_effect = [90, 70]

    CarIncident.car_incident_event(stats)

    assert stats.available_money == 8000  # 20,000 - 12,000
    assert stats.pcr_hatred == 50
