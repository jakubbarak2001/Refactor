"""Module for a variety of interactions with player."""
import re
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
        Automatically formats all "Colonel" mentions in option texts.
        
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
            # Format Colonel, hatred, coding, and money mentions in option text
            formatted_option_text = Interaction.format_colonel_text(option_text)
            formatted_option_text = Interaction.format_hatred_text(formatted_option_text)
            formatted_option_text = Interaction.format_coding_text(formatted_option_text)
            formatted_option_text = Interaction.format_money_text(formatted_option_text)
            decision_lines.append(f"{option_num}. {difficulty_tag} {formatted_option_text}")
            option_numbers.append(option_num)
        
        decision_content = "\n".join(decision_lines)
        
        # Display in a Rich Panel with yellow/gold styling to match continue prompt
        print(Panel(
            decision_content,
            border_style="bold yellow",
            title="[bold white on yellow] > DECISION < [/]",
            padding=(1, 2),
            expand=False
        ))
        
        # Get user choice using existing ask method
        return Interaction.ask(tuple(option_numbers))

    @staticmethod
    def format_colonel_text(text: str) -> str:
        """
        Automatically formats all mentions of "Colonel" (case-insensitive) 
        to be styled as [bold dark_blue]Colonel[/bold dark_blue].
        
        Handles cases where "Colonel" might already be inside Rich markup tags.
        Uses regex to find word boundaries to avoid replacing parts of other words.
        
        Args:
            text: The text string to format
            
        Returns:
            str: Text with all "Colonel" mentions styled
        """
        # Pattern to match "Colonel" as a whole word (case-insensitive)
        # This avoids matching "Colonel" inside other words or already-styled text
        pattern = r'\b(Colonel|colonel|COLONEL)\b'
        
        def replace_colonel(match):
            original = match.group(1)
            # Preserve original case
            return f"[bold dark_blue]{original}[/bold dark_blue]"
        
        # Replace all occurrences
        formatted = re.sub(pattern, replace_colonel, text)
        return formatted

    @staticmethod
    def format_hatred_text(text: str) -> str:
        """
        Automatically formats all mentions of "hatred" (case-insensitive) 
        to be prefixed with 😡 emoji.
        
        Handles cases where "hatred" might already be inside Rich markup tags.
        Uses regex to find word boundaries to avoid replacing parts of other words.
        
        Args:
            text: The text string to format
            
        Returns:
            str: Text with all "hatred" mentions prefixed with 😡 emoji
        """
        # Pattern to match "hatred" as a whole word (case-insensitive)
        # This avoids matching "hatred" inside other words
        pattern = r'\b(hatred|Hatred|HATRED)\b'
        
        def replace_hatred(match):
            original = match.group(1)
            # Add emoji before the word, preserving original case
            return f"😡 {original}"
        
        # Replace all occurrences
        formatted = re.sub(pattern, replace_hatred, text)
        return formatted

    @staticmethod
    def format_coding_text(text: str) -> str:
        """
        Automatically formats all mentions of "coding" (case-insensitive) 
        to be prefixed with 💻 emoji.
        
        Handles cases where "coding" might already be inside Rich markup tags.
        Uses regex to find word boundaries to avoid replacing parts of other words.
        
        Args:
            text: The text string to format
            
        Returns:
            str: Text with all "coding" mentions prefixed with 💻 emoji
        """
        # Pattern to match "coding" as a whole word (case-insensitive)
        # This avoids matching "coding" inside other words like "encoding"
        pattern = r'\b(coding|Coding|CODING)\b'
        
        def replace_coding(match):
            original = match.group(1)
            # Add emoji before the word, preserving original case
            return f"💻 {original}"
        
        # Replace all occurrences
        formatted = re.sub(pattern, replace_coding, text)
        return formatted

    @staticmethod
    def format_money_text(text: str) -> str:
        """
        Automatically formats all mentions of "money" (case-insensitive) 
        to be prefixed with 💰 emoji.
        
        Also handles "CZK" currency mentions by adding emoji before CZK.
        Handles cases where "money" might already be inside Rich markup tags.
        Uses regex to find word boundaries to avoid replacing parts of other words.
        
        Args:
            text: The text string to format
            
        Returns:
            str: Text with all "money" and "CZK" mentions prefixed with 💰 emoji
        """
        # Pattern to match "money" as a whole word (case-insensitive)
        # This avoids matching "money" inside other words
        pattern = r'\b(money|Money|MONEY)\b'
        
        def replace_money(match):
            original = match.group(1)
            # Add emoji before the word, preserving original case
            return f"💰 {original}"
        
        # Replace all occurrences of "money"
        formatted = re.sub(pattern, replace_money, text)
        
        # Also handle CZK currency mentions - add emoji before CZK if not already preceded by emoji
        # Match CZK that appears after numbers (like "1000 CZK", "1,000 CZK", "8.000 CZK")
        # Handle both comma and period as thousands separators
        # Only add if there's no emoji immediately before it
        def add_emoji_to_czk(match):
            czk_match = match.group(0)
            # Check if there's already an emoji in the 10 characters before CZK
            start_pos = match.start()
            context_before = formatted[max(0, start_pos - 10):start_pos]
            if "💰" not in context_before:
                return f"💰 {czk_match}"
            return czk_match
        
        # Match patterns like:
        # - "1000 CZK" (simple number)
        # - "1,000 CZK" (comma separator)
        # - "8.000 CZK" (period separator)
        # - "1,234.56 CZK" (both separators)
        # Pattern: digits, optionally followed by comma/period and more digits, then optional space and CZK
        formatted = re.sub(r'(\d+[.,]?\d*[.,]?\d*\s*CZK)', add_emoji_to_czk, formatted)
        
        return formatted

    @staticmethod
    def print_colonel(*args, **kwargs):
        """
        Wrapper around Rich's print() that automatically formats all "Colonel" mentions.
        Use this instead of print() when you want automatic Colonel formatting.
        """
        # Format all string arguments
        formatted_args = []
        for arg in args:
            if isinstance(arg, str):
                formatted_args.append(Interaction.format_colonel_text(arg))
            else:
                formatted_args.append(arg)
        
        # Print with formatted text
        print(*formatted_args, **kwargs)

    @staticmethod
    def show_outcome(outcome_text: str) -> None:
        """
        Display an outcome message in a Rich Panel with styled [OUTCOME] tag.
        The [OUTCOME] tag is displayed in bright cyan/teal color, rest of text is normal.
        Automatically formats Colonel and hatred mentions.
        
        Args:
            outcome_text: The outcome message text (can include [OUTCOME] tag or will be prepended)
                         Example: "- 2500 CZK, - 10 PCR HATRED"
        """
        # Format Colonel, hatred, coding, and money mentions
        outcome_text = Interaction.format_colonel_text(outcome_text)
        outcome_text = Interaction.format_hatred_text(outcome_text)
        outcome_text = Interaction.format_coding_text(outcome_text)
        outcome_text = Interaction.format_money_text(outcome_text)
        
        # Check if [OUTCOME] is already in the text, if not prepend it
        if "[OUTCOME]" not in outcome_text:
            formatted_text = f"[bright_cyan][OUTCOME][/bright_cyan]: {outcome_text}"
        else:
            # Replace [OUTCOME] with styled version
            formatted_text = outcome_text.replace(
                "[OUTCOME]",
                "[bright_cyan][OUTCOME][/bright_cyan]"
            )
        
        # Display in a Rich Panel with cyan/teal border to match the outcome color
        print(Panel(
            formatted_text,
            border_style="bold cyan",
            title="[bold white on cyan] > OUTCOME < [/]",
            padding=(1, 2),
            expand=False
        ))
