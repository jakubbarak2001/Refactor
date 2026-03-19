"""A simple day calculator, accessible from main menu."""
from rich import print
from rich.align import Align
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
        day_text = Text()
        day_text.append(f"DAY {self.current_day}", style="bold bright_white")
        day_text.append(" / 30", style="dim white")

        print(Panel(
            Align.center(day_text),
            border_style="bold cyan",
            title="[bold white on cyan] > NEW DAY < [/]",
            padding=(1, 4),
            expand=False
        ))

    def day_end_message(self):
        """Beautiful Rich TUI message about ending the current day."""
        day_text = Text()
        day_text.append(f"END OF DAY {self.current_day}", style="bold dim white")

        print(Panel(
            Align.center(day_text),
            border_style="dim cyan",
            title="[bold white on color(236)] > DAY OVER < [/]",
            padding=(1, 4),
            expand=False
        ))
