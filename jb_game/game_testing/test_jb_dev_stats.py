import pytest
from jb_game.game_logic.jb_dev_stats import JBStats


@pytest.fixture
def stats():
    """Creates a fresh JBStats instance for every test function."""
    return JBStats(available_money=1000, coding_experience=10, pcr_hatred=0)


def test_initial_values(stats):
    """Test that the game starts with the correct values."""
    assert stats.available_money == 1000
    assert stats.coding_experience == 10
    assert stats.pcr_hatred == 0


def test_increment_money(stats):
    """Test adding money (e.g., from a paycheck)."""
    stats.increment_stats_value_money(500)
    assert stats.available_money == 1500


def test_decrement_money(stats):
    """Test spending money (e.g., buying a course)."""
    stats.increment_stats_value_money(-500)
    assert stats.available_money == 500


def test_increment_hatred_logic(stats):
    """Test gaining hatred (e.g., bad event)."""
    stats.increment_stats_pcr_hatred(10)
    assert stats.pcr_hatred == 10


def test_stats_description_boundaries(stats):
    """
    Test that the text description changes correctly based on values.
    This ensures your 'stats_description_money' logic isn't broken.
    """
    # Test "broke" description
    stats.change_stats_value_money(0)
    assert "YOU HAVE NO MONEY LEFT" in stats.stats_description_money()

    # Test "rich" description
    stats.change_stats_value_money(1000001)
    assert "YOU ARE A MILLIONAIRE" in stats.stats_description_money()


def test_pcr_hatred_warning_trigger(stats, capsys):
    """
    Test if the warning prints when Hatred is high.
    We use 'capsys' to capture what you print to the console.
    """
    stats.change_stats_pcr_hatred(80)  # Above the 75 threshold
    stats.get_stats_command()

    captured = capsys.readouterr()
    assert "WARNING: YOUR PCR HATRED IS" in captured.out


@pytest.mark.parametrize("money_amount, expected_snippet", [
    (1000001, "MILLIONAIRE"),  # Above 1M
    (500001, "Half a million"),  # Just above 500k
    (500000, "Half a million"),  # Exactly on the boundary (Edge case!)
    (85000, "solid financial"),  # Exactly on 85k boundary
    (1000, "basically broke"),  # Way below
    (0, "NO MONEY LEFT"),  # Zero boundary
    (-500, "NO MONEY LEFT"),  # Negative boundary (Safety check)
])
def test_money_description_boundaries(stats, money_amount, expected_snippet):
    stats.change_stats_value_money(money_amount)
    description = stats.stats_description_money()

    # We check if the expected phrase is inside the returned description
    assert expected_snippet in description