"""Module for a variety of interactions with player."""
import re
from abc import ABC, abstractmethod
from random import randint
from typing import Optional

from rich import print
from rich.panel import Panel


class InteractionInterface(ABC):
    """
    Abstract interface for player interactions.
    Allows swapping between terminal and GUI implementations.
    """

    @abstractmethod
    def ask(
        self, 
        options: tuple, 
        character: Optional[str] = None, 
        expression: str = "neutral", 
        bg: Optional[str] = None
    ) -> str:
        """
        Prompts the user until they enter a valid option from the provided tuple.
        
        Args:
            options: Tuple of valid option strings (e.g., ("1", "2", "3"))
            character: Optional character name for visual display (e.g., "colonel", "jb")
            expression: Character expression/emotion (e.g., "angry", "neutral", "smiling")
            bg: Optional background scene identifier (e.g., "office", "parking_lot")
            
        Returns:
            str: The selected option
        """
        pass

    @abstractmethod
    def show_decision(
        self, 
        option_texts: list[tuple[str, str, str]],
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> str:
        """
        Display decision options and get user choice.
        
        Args:
            option_texts: List of tuples (option_number, difficulty_tag, option_text)
            character: Optional character name for visual display
            expression: Character expression/emotion
            bg: Optional background scene identifier
            
        Returns:
            str: The selected option number
        """
        pass

    @abstractmethod
    def show_outcome(
        self, 
        outcome_text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> None:
        """
        Display an outcome message.
        
        Args:
            outcome_text: The outcome message text
            character: Optional character name for visual display
            expression: Character expression/emotion
            bg: Optional background scene identifier
        """
        pass

    @abstractmethod
    def print_text(
        self, 
        text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None,
        wait_for_input: bool = True,
        animated: bool = False,
        animation_delay: float = 0.03
    ) -> None:
        """
        Display text (replaces print() calls).
        
        Args:
            text: Text to display
            character: Optional character name for visual display
            expression: Character expression/emotion
            bg: Optional background scene identifier
            wait_for_input: If True, waits for Enter key. If False, just displays text without waiting.
            animated: If True, displays text with typewriter effect (GUI mode only)
            animation_delay: Delay between characters in seconds (default 0.03)
        """
        pass

    @abstractmethod
    def continue_prompt(
        self,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> None:
        """
        Display a "Press Enter to continue" prompt and wait for Enter key.
        
        Args:
            character: Optional character name for visual display
            expression: Character expression/emotion
            bg: Optional background scene identifier
        """
        pass


class TerminalInteraction(InteractionInterface):
    """
    Terminal-based implementation of InteractionInterface.
    Uses Rich TUI for display and input() for user input.
    """

    @staticmethod
    def get_difficulty_tag(chance: int = None) -> str:
        """
        Returns a descriptive tag based on the percentage chance of success.
        (Static utility method - doesn't need to be abstract)

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
        (Static utility method - doesn't need to be abstract)

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

    def ask(
        self, 
        options: tuple, 
        character: Optional[str] = None, 
        expression: str = "neutral", 
        bg: Optional[str] = None
    ) -> str:
        """
        Prompts the user until they enter a valid option from the provided tuple.
        Terminal implementation ignores character, expression, and bg parameters.
        """
        while True:
            choice = input("> ").strip()
            if choice in options:
                return choice

            print(f"Invalid choice. Please enter one of: {', '.join(options)}")

    def show_decision(
        self, 
        option_texts: list[tuple[str, str, str]],
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> str:
        """
        Display decision options in a Rich Panel, clearly separated from regular text.
        Automatically formats all "Colonel" mentions in option texts.
        Terminal implementation ignores character, expression, and bg parameters.
        """
        # Build the decision text with all options
        decision_lines = []
        option_numbers = []
        
        for option_num, difficulty_tag, option_text in option_texts:
            # Format Colonel, hatred, coding, and money mentions in option text
            formatted_option_text = TerminalInteraction.format_colonel_text(option_text)
            formatted_option_text = TerminalInteraction.format_hatred_text(formatted_option_text)
            formatted_option_text = TerminalInteraction.format_coding_text(formatted_option_text)
            formatted_option_text = TerminalInteraction.format_money_text(formatted_option_text)
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
        return self.ask(tuple(option_numbers), character, expression, bg)

    def show_outcome(
        self, 
        outcome_text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> None:
        """
        Display an outcome message in a Rich Panel with styled [OUTCOME] tag.
        Terminal implementation ignores character, expression, and bg parameters.
        """
        # Format Colonel, hatred, coding, and money mentions
        outcome_text = TerminalInteraction.format_colonel_text(outcome_text)
        outcome_text = TerminalInteraction.format_hatred_text(outcome_text)
        outcome_text = TerminalInteraction.format_coding_text(outcome_text)
        outcome_text = TerminalInteraction.format_money_text(outcome_text)
        
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

    def print_text(
        self, 
        text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None,
        wait_for_input: bool = True,
        animated: bool = False,
        animation_delay: float = 0.03
    ) -> None:
        """
        Display text (replaces print() calls).
        Terminal implementation ignores character, expression, bg, wait_for_input, animated, and animation_delay parameters.
        """
        # Format Colonel, hatred, coding, and money mentions
        text = TerminalInteraction.format_colonel_text(text)
        text = TerminalInteraction.format_hatred_text(text)
        text = TerminalInteraction.format_coding_text(text)
        text = TerminalInteraction.format_money_text(text)
        
        if animated:
            # Terminal mode: use slow print effect
            import sys
            import time
            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(animation_delay)
            print()  # Newline at end
        else:
            print(text)

    def continue_prompt(
        self,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> None:
        """
        Display a "Press Enter to continue" prompt and wait for Enter key.
        Terminal implementation ignores character, expression, and bg parameters.
        """
        print(Panel.fit(
            "[italic yellow](PRESS ENTER TO CONTINUE)[/italic yellow]",
            border_style="bold",
            width=40
        ))
        
        # Windows: Use msvcrt to read keys directly (no echo, only Enter accepted)
        import sys
        if sys.platform == "win32":
            import msvcrt
            while True:
                key = msvcrt.getwch()
                # Enter key is '\r' (carriage return)
                if key == '\r':
                    break
        else:
            # Non-Windows: Use getpass to hide input, only Enter works
            import getpass
            getpass.getpass("")

    @staticmethod
    def format_colonel_text(text: str) -> str:
        """
        Automatically formats all mentions of "Colonel" (case-insensitive) 
        to be styled as [bold bright_blue]Colonel[/bold bright_blue].
        (Static utility method)
        """
        # First, update any existing dark_blue Colonel styling to bright_blue
        text = text.replace('[bold dark_blue]', '[bold bright_blue]')
        text = text.replace('[/bold dark_blue]', '[/bold bright_blue]')
        
        # Pattern to match "Colonel" as a whole word (case-insensitive)
        pattern = r'\b(Colonel|colonel|COLONEL)\b'
        
        def replace_colonel(match):
            original = match.group(1)
            start = match.start()
            end = match.end()
            
            # Check if this instance is already inside [bold bright_blue] tags
            text_before = text[:start]
            text_after = text[end:]
            
            last_open = text_before.rfind('[bold bright_blue]')
            first_close = text_after.find('[/bold bright_blue]')
            
            if last_open != -1 and first_close != -1:
                between_tags = text[last_open + len('[bold bright_blue]'):start]
                if '[/bold bright_blue]' not in between_tags:
                    return original
            
            return f"[bold bright_blue]{original}[/bold bright_blue]"
        
        formatted = re.sub(pattern, replace_colonel, text)
        return formatted

    @staticmethod
    def format_hatred_text(text: str) -> str:
        """Automatically formats all mentions of "hatred" with 😡 emoji. (Static utility method)"""
        # Don't add emoji if it's already in the text (prevents double emojis)
        if "😡" in text:
            return text
            
        pattern = r'\b(hatred|Hatred|HATRED)\b'
        
        def replace_hatred(match):
            original = match.group(1)
            # Check if emoji is already before this word
            start_pos = match.start()
            context_before = text[max(0, start_pos - 5):start_pos]
            if "😡" in context_before:
                return original
            return f"😡 {original}"
        
        formatted = re.sub(pattern, replace_hatred, text)
        return formatted

    @staticmethod
    def format_coding_text(text: str) -> str:
        """Automatically formats all mentions of "coding" with 💻 emoji. (Static utility method)"""
        # Don't add emoji if it's already in the text (prevents double emojis)
        if "💻" in text:
            return text
            
        pattern = r'\b(coding|Coding|CODING)\b'
        
        def replace_coding(match):
            original = match.group(1)
            # Check if emoji is already before this word
            start_pos = match.start()
            context_before = text[max(0, start_pos - 5):start_pos]
            if "💻" in context_before:
                return original
            return f"💻 {original}"
        
        formatted = re.sub(pattern, replace_coding, text)
        return formatted

    @staticmethod
    def format_money_text(text: str) -> str:
        """Automatically formats all mentions of "money" and "CZK" with 💰 emoji. (Static utility method)"""
        # Don't add emoji if it's already in the text (prevents double emojis)
        if "💰" in text:
            return text
        
        pattern = r'\b(money|Money|MONEY)\b'
        
        def replace_money(match):
            original = match.group(1)
            # Check if emoji is already before this word
            start_pos = match.start()
            context_before = text[max(0, start_pos - 5):start_pos]
            if "💰" in context_before:
                return original
            return f"💰 {original}"
        
        formatted = re.sub(pattern, replace_money, text)
        
        def add_emoji_to_czk(match):
            czk_match = match.group(0)
            start_pos = match.start()
            context_before = formatted[max(0, start_pos - 10):start_pos]
            if "💰" not in context_before:
                return f"💰 {czk_match}"
            return czk_match
        
        formatted = re.sub(r'(\d+[.,]?\d*[.,]?\d*\s*CZK)', add_emoji_to_czk, formatted)
        
        return formatted

    @staticmethod
    def print_colonel(*args, **kwargs):
        """
        Wrapper around Rich's print() that automatically formats all "Colonel" mentions.
        Use this instead of print() when you want automatic Colonel formatting.
        (Static utility method - kept for backward compatibility)
        """
        formatted_args = []
        for arg in args:
            if isinstance(arg, str):
                formatted_args.append(TerminalInteraction.format_colonel_text(arg))
            else:
                formatted_args.append(arg)
        
        print(*formatted_args, **kwargs)


# Global interaction provider - can be swapped between Terminal and GUI
_interaction_provider: Optional[InteractionInterface] = None


def get_interaction() -> InteractionInterface:
    """
    Get the current interaction provider instance.
    Returns TerminalInteraction by default if not set.
    """
    global _interaction_provider
    if _interaction_provider is None:
        _interaction_provider = TerminalInteraction()
    return _interaction_provider


def set_interaction(interaction: InteractionInterface) -> None:
    """
    Set the interaction provider (allows switching between Terminal and GUI).
    
    Args:
        interaction: An instance of InteractionInterface (TerminalInteraction or GUIInteraction)
    """
    global _interaction_provider
    _interaction_provider = interaction


# Backward compatibility: Create a static-like interface that delegates to the provider
class Interaction:
    """
    Backward-compatible wrapper that delegates to the current interaction provider.
    Maintains the old static interface while using the provider pattern under the hood.
    """
    
    @staticmethod
    def get_difficulty_tag(chance: int = None) -> str:
        """Static utility method - delegates to TerminalInteraction."""
        return TerminalInteraction.get_difficulty_tag(chance)
    
    @staticmethod
    def attempt_action(chance: int) -> bool:
        """Static utility method - delegates to TerminalInteraction."""
        return TerminalInteraction.attempt_action(chance)
    
    @staticmethod
    def ask(
        options: tuple, 
        character: Optional[str] = None, 
        expression: str = "neutral", 
        bg: Optional[str] = None
    ) -> str:
        """Delegates to current interaction provider."""
        return get_interaction().ask(options, character, expression, bg)
    
    @staticmethod
    def show_decision(
        option_texts: list[tuple[str, str, str]],
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> str:
        """Delegates to current interaction provider."""
        return get_interaction().show_decision(option_texts, character, expression, bg)
    
    @staticmethod
    def show_outcome(
        outcome_text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> None:
        """Delegates to current interaction provider."""
        return get_interaction().show_outcome(outcome_text, character, expression, bg)
    
    @staticmethod
    def print_text(
        text: str,
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None,
        wait_for_input: bool = True,
        animated: bool = False,
        animation_delay: float = 0.03
    ) -> None:
        """Delegates to current interaction provider.
        
        Args:
            text: Text to display
            character: Optional character name for visual display
            expression: Character expression/emotion
            bg: Optional background scene identifier
            wait_for_input: If True, waits for Enter key. If False, just displays text without waiting.
            animated: If True, displays text with typewriter effect (GUI mode only)
            animation_delay: Delay between characters in seconds (default 0.03)
        """
        return get_interaction().print_text(text, character, expression, bg, wait_for_input, animated, animation_delay)
    
    
    @staticmethod
    def format_colonel_text(text: str) -> str:
        """Static utility method - delegates to TerminalInteraction."""
        return TerminalInteraction.format_colonel_text(text)
    
    @staticmethod
    def format_hatred_text(text: str) -> str:
        """Static utility method - delegates to TerminalInteraction."""
        return TerminalInteraction.format_hatred_text(text)
    
    @staticmethod
    def format_coding_text(text: str) -> str:
        """Static utility method - delegates to TerminalInteraction."""
        return TerminalInteraction.format_coding_text(text)
    
    @staticmethod
    def format_money_text(text: str) -> str:
        """Static utility method - delegates to TerminalInteraction."""
        return TerminalInteraction.format_money_text(text)
    
    @staticmethod
    def print_colonel(*args, **kwargs):
        """Static utility method - delegates to TerminalInteraction."""
        return TerminalInteraction.print_colonel(*args, **kwargs)
    
    @staticmethod
    def continue_prompt(
        character: Optional[str] = None,
        expression: str = "neutral",
        bg: Optional[str] = None
    ) -> None:
        """Delegates to current interaction provider."""
        return get_interaction().continue_prompt(character, expression, bg)