"""A simple day calculator, accessible from main menu."""
from rich import print
from rich.panel import Panel
from rich.text import Text


class DayCycle:
    """Creates day counter, accessible from Game class's menu method."""

    def __init__(self, current_day=1):
        """Initialises itself, starting from day 1"""
        self.current_day = current_day

    def report_current_day(self):
        """Tells what day is it in neat format."""
        print(self.current_day)

    def next_day(self):
        """Skips to the next day."""
        self.current_day += 1

    def day_start_message(self):
        """Beautiful Rich TUI message about starting a new day."""
        pass

    def day_end_message(self):
        """Beautiful Rich TUI message about ending the current day."""
        pass
