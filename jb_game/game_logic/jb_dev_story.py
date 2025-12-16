"""Contains everything regarding storytelling."""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.theme import Theme

from jb_game.game_logic.jb_dev_stats import JBStats

# Setup a console with a custom theme for the game
custom_theme = Theme({
    "narrator": "italic cyan",
    "danger": "bold red",
    "highlight": "bold yellow",
    "money": "bold green"
})
console = Console(theme=custom_theme)

class Story:
    """Contains the most important story elements, mostly text strings."""
    def __init__(self, stats: JBStats):
        """Initialises itself."""
        self.stats = stats

    @staticmethod
    def start_game_message():
        """Gives a neatly formatted welcoming message, using Rich panels."""

        console.print("\n")
        console.print(Panel(
            "[bold white]Rise and shine, rise and shine JB...[/bold white] [dim]it's your big day today.[/dim]",
            title="[bold cyan]PROLOGUE[/bold cyan]",
            border_style="cyan"
        ))

        input("\n(Press Enter to continue...)")

        intro_text = (
            "Welcome to [bold magenta]JB - The Game[/bold magenta]!\n\n"
            "In this game, you will be playing as a [bold blue]young police officer[/bold blue], in the northern part of Bohemia.\n"
            "Initially, you love your job, but everything is about to change very soon...\n\n"
            "[italic]Will you become a victim of a broken system, or an architect who will create his own?[/italic]\n"
            "In this game, that is up to you..."
        )

        console.print(Panel(intro_text, title="INTRODUCTION", border_style="blue"))

        input("\n(Press Enter to continue...)")

        rules_text = (
            "Your time and resources are limited - you have to end your job as police officer soon!\n\n"
            "You have three main stats:\n"
            "1. [money]Money[/money] ($)\n"
            "2. [highlight]Coding Skills[/highlight] (</>)\n"
            "3. [danger]Hatred of Police[/danger] (1312)\n\n"
            "[bold red]LOSE CONDITIONS:[/bold red]\n"
            "- Money drops below 0\n"
            "- Police Hatred hits 100%"
        )

        console.print(Panel(rules_text, title="RULES OF ENGAGEMENT", border_style="red"))