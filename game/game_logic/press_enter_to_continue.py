from rich import print
from rich.panel import Panel

def continue_prompt():
    """Display a 'PRESS ENTER TO CONTINUE' prompt with rich formatting
    and wait for the player to press Enter before continuing the game."""
    print(Panel.fit(
        "[italic](PRESS ENTER TO CONTINUE)[/italic]",
        border_style="bold",
        width=40
    ))
    input()