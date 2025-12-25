"""Module for a variety of interactions with player."""
from random import randint


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
            str: A formatted tag like '[SAFE]', '[RISKY]', or '[TRIVIAL]'.
        """
        # 1. Handle the "Safe Option" (No RNG involved)
        if chance is None:
            return "[SAFE]"

        # 2. Handle Skill Checks (RNG or Stat-based)
        if chance >= 100:
            return "[TRIVIAL]"  # Skill is so high, failure is impossible.
        elif chance >= 80:
            return "[EASY]"  # 80-99%: Very high chance, but bad luck exists.
        elif chance >= 60:
            return "[LIKELY]"  # 60-79%: Good odds.
        elif chance >= 40:
            return "[UNCERTAIN]"  # 40-59%: Coin flip.
        elif chance >= 20:
            return "[RISKY]"  # 20-39%: Odds are against you.
        elif chance > 0:
            return "[SUICIDE]"  # 1-19%: You will almost certainly fail.
        else:
            return "[IMPOSSIBLE]"  # 0%: Skill is too low to even attempt.

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
