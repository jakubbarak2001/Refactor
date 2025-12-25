"""Contains everything regarding storytelling."""
from rich import print

from game.game_logic.press_enter_to_continue import continue_prompt
from game.game_logic.stats import Stats


class Story:
    """Contains the most important story elements, mostly text strings."""

    def __init__(self, stats: Stats):
        """Initialises itself."""
        self.stats = stats

    @staticmethod
    def start_game_message():
        """Gives a neatly formatted welcoming message, for whenever you start the game."""
        print("\nRise and shine, rise and shine JB.")
        print("Your life is about to turn upside down.")
        continue_prompt()
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
