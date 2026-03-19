"""
Continue prompt that works in both terminal and GUI mode.
Delegates to the Interaction system for proper mode handling.
"""
import sys
from typing import Optional

from rich.panel import Panel

from game.game_logic.interaction import Interaction


def continue_prompt(
    character: Optional[str] = None,
    expression: str = "neutral",
    bg: Optional[str] = None
) -> None:
    """
    Display a 'PRESS ENTER TO CONTINUE' prompt and wait for Enter.
    Works in both terminal and GUI mode.
    
    Args:
        character: Optional character name for visual display (GUI mode)
        expression: Character expression/emotion (GUI mode)
        bg: Optional background scene identifier (GUI mode)
    """
    Interaction.continue_prompt(character, expression, bg)

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