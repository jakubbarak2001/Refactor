"""Module for a variety of interactions with player."""
from random import randint

from rich import print
from rich.panel import Panel


class Interaction:
    """
    Helper class for handling user input, decision formatting, and difficulty tags.
    Centralizes how the player interacts with the game mechanics.
    """

    @staticmethod
    def get_difficulty_tag(chance: int = None) -> str:
        """
        Returns a descriptive tag based on the percentage chance of success.

        Args:
            chance (int, optional): The success probability (0-100+).
                                    If None, it represents a choice with NO RNG (Guaranteed/Safe).

        Returns:
            str: A formatted tag with Rich markup colors like '[green][SAFE][/green]',
                 '[bright_red][RISKY][/bright_red]', etc.
        """
        # 1. Handle the "Safe Option" (No RNG involved) - Green
        if chance is None:
            return "[green][SAFE][/green]"

        # 2. Handle Skill Checks (RNG or Stat-based)
        if chance >= 100:
            return "[bright_green][TRIVIAL][/bright_green]"  # Skill is so high, failure is impossible.
        elif chance >= 80:
            return "[bright_green][EASY][/bright_green]"  # 80-99%: Very high chance, but bad luck exists.
        elif chance >= 60:
            return "[yellow][LIKELY][/yellow]"  # 60-79%: Good odds.
        elif chance >= 40:
            return "[yellow][UNCERTAIN][/yellow]"  # 40-59%: Coin flip.
        elif chance >= 20:
            return "[bright_red][RISKY][/bright_red]"  # 20-39%: Odds are against you.
        elif chance > 0:
            return "[bright_red][SUICIDE][/bright_red]"  # 1-19%: You will almost certainly fail.
        else:
            return "[red][IMPOSSIBLE][/red]"  # 0%: Skill is too low to even attempt.

    @staticmethod
    def attempt_action(chance: int) -> bool:
        """
        Performs the RNG check for a skill or luck-based action.

        Args:
            chance (int): The percentage chance of success (0-100).
                          Values >= 100 always succeed.
                          Values <= 0 always fail.

        Returns:
            bool: True if the action succeeded, False otherwise.
        """
        if chance >= 100:
            return True
        if chance <= 0:
            return False

        roll = randint(1, 100)

        return roll <= chance

    @staticmethod
    def ask(options: tuple) -> str:
        """
        Prompts the user until they enter a valid option from the provided tuple.
        Returns the valid choice as a string.
        """
        while True:
            choice = input("> ").strip()
            if choice in options:
                return choice

            print(f"Invalid choice. Please enter one of: {', '.join(options)}")

    @staticmethod
    def show_decision(option_texts: list[tuple[str, str, str]]) -> str:
        """
        Display decision options in a Rich Panel, clearly separated from regular text.
        
        Args:
            option_texts: List of tuples (option_number, difficulty_tag, option_text)
                         Example: [("1", "[UNCERTAIN]", "THE 'MACGYVER' MANEUVER..."), ...]
        
        Returns:
            str: The selected option number
        """
        # Build the decision text with all options
        decision_lines = []
        option_numbers = []
        
        for option_num, difficulty_tag, option_text in option_texts:
            decision_lines.append(f"{option_num}. {difficulty_tag} {option_text}")
            option_numbers.append(option_num)
        
        decision_content = "\n".join(decision_lines)
        
        # Display in a Rich Panel with yellow/gold styling to match continue prompt
        print(Panel(
            decision_content,
            border_style="bold yellow",
            title="[bold white on yellow] ▶ DECISION ◀ [/]",
            padding=(1, 2),
            expand=False
        ))
        
        # Get user choice using existing ask method
        return Interaction.ask(tuple(option_numbers))
