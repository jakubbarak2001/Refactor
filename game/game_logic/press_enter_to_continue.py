import sys

from rich import print
from rich.panel import Panel


def continue_prompt():
    """Display a 'PRESS ENTER TO CONTINUE' prompt with rich formatting
    and wait for the player to press Enter before continuing the game.
    Only accepts Enter key to continue (ignores all other keys)."""
    print(Panel.fit(
        "[italic yellow](PRESS ENTER TO CONTINUE)[/italic yellow]",
        border_style="bold",
        width=40
    ))
    
    # Windows: Use msvcrt to read keys directly (no echo, only Enter accepted)
    if sys.platform == "win32":
        import msvcrt
        while True:
            key = msvcrt.getwch()
            # Enter key is '\r' (carriage return)
            if key == '\r':
                break
            # Ignore all other keys - only Enter will continue
    else:
        # Non-Windows: Use getpass to hide input, only Enter works
        import getpass
        getpass.getpass("")

def game_over_prompt():
    """Display a 'GAME OVER' prompt with rich formatting
    and wait for the player to press Enter before continuing the game.
    Only accepts Enter key to continue (ignores all other keys)."""
    print(Panel.fit(
        "[italic red](GAME OVER)[/italic red]",
        border_style="bold",
        width=40
    ))
    
    # Windows: Use msvcrt to read keys directly (no echo, only Enter accepted)
    if sys.platform == "win32":
        import msvcrt
        while True:
            key = msvcrt.getwch()
            # Enter key is '\r' (carriage return)
            if key == '\r':
                break
            # Ignore all other keys - only Enter will continue
    else:
        # Non-Windows: Use getpass to hide input, only Enter works
        import getpass
        getpass.getpass("")