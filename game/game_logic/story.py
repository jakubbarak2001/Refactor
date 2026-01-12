"""Contains everything regarding storytelling."""
from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.box import DOUBLE

from game.game_logic.press_enter_to_continue import continue_prompt
from game.game_logic.stats import Stats


class Arc:
    """
    Represents a story arc with consistent Rich TUI display formatting.
    All arcs use the same visual style for consistency.
    """
    
    @staticmethod
    def display_arc_title(arc_number: str, arc_title: str, border_color: str = "red") -> None:
        """
        Displays an arc title in a consistent Rich Panel format.
        
        Args:
            arc_number: The arc number (e.g., "I", "II", "III")
            arc_title: The arc title (e.g., "THE INCIDENT", "THE AWAKENING")
            border_color: The border color style (default: "red")
        """
        # Create beautifully styled text with visual hierarchy
        combined_text = Text()
        combined_text.append("┌─ ", style="dim white")
        combined_text.append(f"ARC {arc_number}", style=f"bold {border_color}")
        combined_text.append(" ─┐", style="dim white")
        combined_text.append("\n\n", style="")
        combined_text.append(arc_title, style="bold bright_white")
        
        # Create an elegant panel with double border and proper spacing
        print()
        print(Align.center(
            Panel(
                Align.center(combined_text),
                border_style=f"bold {border_color}",
                box=DOUBLE,
                padding=(2, 6),
                width=50
            )
        ))
        print()


class Story:
    """Contains the most important story elements, mostly text strings."""

    def __init__(self, stats: Stats):
        """Initialises itself."""
        self.stats = stats

    @staticmethod
    def start_game_message():
        """Gives a neatly formatted welcoming message, for whenever you start the game."""
        print("[bold]Welcome to REFACTOR![bold]")
        print("\nYou are a young police officer, in northern part of Bohemia.")
        print("At the beginning, being a cop is everything for you.")
        print("But soon, you will experience big changes.")
        print("\nYou can either become:\n")
        print("[red]• Victim[/red] of a broken system, following orders.")
        print("[cyan]• Architect[/cyan] that creates his own rules.")
        print("\nIn this game, that is entirely up to you.")
        continue_prompt()
        print("[bold]Your main stats are: \n\n💲 Money \n💻 Coding skills \n😠 Police Hatred[/bold]")
        print("\n[red][bold]0 Money / 100 Hatred == GAME OVER[/red][/bold]")
        continue_prompt()
