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
        day_text = Text()
        day_text.append(f"Starting day ", style="bold white")
        day_text.append(f"#{self.current_day}", style="bold bright_yellow")
        day_text.append(f"/30", style="bold white")
        
        print("\n")
        print(Panel(
            day_text,
            border_style="bold bright_yellow",
            title="[bold white on bright_yellow] > NEW DAY < [/]",
            padding=(1, 3),
            expand=False
        ))

    def day_end_message(self):
        """Beautiful Rich TUI message about ending the current day."""
        day_text = Text()
        day_text.append(f"Ending day ", style="bold white")
        day_text.append(f"#{self.current_day}", style="bold bright_yellow")
        day_text.append(f"/30", style="bold white")
        
        print("\n")
        print(Panel(
            day_text,
            border_style="bold color(94)",
            title="[bold white on color(94)] > END OF DAY < [/]",
            padding=(1, 3),
            expand=False
        ))
