"""
Character class selection module.
Allows players to choose from different character classes with unique perks.
"""
from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

from game.game_logic.interaction import Interaction
from game.game_logic.press_enter_to_continue import continue_prompt

console = Console(force_terminal=True, width=None)


class CharacterClass:
    """
    Represents a character class with description and perks.
    """
    
    CLASSES = {
        "1": {
            "name": "BODYBUILDER",
            "emoji": "",
            "color": "bright_red",
            "description": "You've dedicated your life to physical perfection. Every rep, every set, every protein shake has forged you into a weapon of muscle and will. Strength isn't just what you have — it's who you are.",
            "perks": [
                ("+", "Gym is 3x more effective", "bright_green"),
                ("+", "Brute force playstyle", "bright_green"),
                ("-", "Some dialogue options are locked for you", "bright_red"),
            ]
        },
        "2": {
            "name": "DARK EMPATH",
            "emoji": "",
            "color": "bright_magenta",
            "description": "You see through people. Their fears, their desires, their weaknesses — it's all laid bare before you. You don't just understand people; you understand how to use that understanding. The darkness in others doesn't scare you—it empowers you.",
            "perks": [
                ("\n", ""),
                ("+", "Understand people around you more deeply, use that to your advantage", "bright_green"),
                ("-", "Therapy is locked for you", "bright_red"),
            ]
        },
        "3": {
            "name": "BIOHACKER",
            "emoji": "",
            "color": "bright_cyan",
            "description": "Your body is a machine, and you're the engineer. Nootropics, supplements, cognitive enhancers — you've turned yourself into a living experiment. Peak performance isn't a goal; it's a baseline. But every enhancement comes with a price.",
            "perks": [
                ("\n", ""),
                ("+", "Buy nootropics, providing different buffs", "bright_green"),
                ("+", "New activity: study about nootropics, eventually unlocking legendary supplements like Modafinil", "bright_green"),
                ("-", "The withdrawal can be devastating", "bright_red"),
            ]
        }
    }

    @staticmethod
    def select_class(stats) -> str:
        """
        Displays character class selection in a large Rich panel.
        Returns the selected class name (lowercase).
        
        Args:
            stats: Stats object to store the selected class
            
        Returns:
            str: Selected class name in lowercase (e.g., "bodybuilder")
        """
        while True:
            # Build decision options for Interaction system
            decision_options = []
            for key in sorted(CharacterClass.CLASSES.keys()):
                class_data = CharacterClass.CLASSES[key]
                # Build option text with class info
                option_text = f"{class_data['name']}\n\n{class_data['description']}\n\nPERKS:\n"
                for perk_entry in class_data['perks']:
                    if len(perk_entry) == 2:  # Newline entry
                        option_text += "\n"
                        continue
                    symbol, perk_text, _ = perk_entry
                    if symbol == "+":
                        option_text += f"[+] {perk_text}\n"
                    elif symbol == "-":
                        option_text += f"[-] {perk_text}\n"
                decision_options.append((key, Interaction.get_difficulty_tag(), option_text))
            
            # Display decision using Interaction system (works in both terminal and GUI)
            choice = Interaction.show_decision(decision_options)

            if choice in CharacterClass.CLASSES:
                class_data = CharacterClass.CLASSES[choice]
                color = class_data['color']
                
                # Create confirmation message - use plain string with emojis for better GUI compatibility
                confirm_text = f"You selected: {class_data['name']}\n\n"
                confirm_text += "CLASS DESCRIPTION:\n"
                confirm_text += f"  {class_data['description']}\n\n"
                confirm_text += "YOUR PERKS:\n\n"
                
                for perk_entry in class_data['perks']:
                    # Handle newline entries (empty perk for spacing) - can be 2 or 3 tuple
                    if len(perk_entry) == 2 and perk_entry[0] == "\n":
                        confirm_text += "\n"
                        continue
                    
                    # Unpack 3-tuple (symbol, perk_text, perk_color)
                    symbol, perk_text, perk_color = perk_entry
                    
                    confirm_text += "  "
                    if symbol == "+":
                        confirm_text += "[+] "
                    elif symbol == "-":
                        confirm_text += "[-] "
                    
                    confirm_text += f"{perk_text}\n"
                
                confirm_text += "\nProceed with this class?"
                
                # Display confirmation using Interaction system
                Interaction.print_text(confirm_text, wait_for_input=False)
                confirm_select = Interaction.ask(("y", "n")).lower()
                if confirm_select != "y":
                    continue

                # Store selected class
                selected_class = class_data['name'].lower().replace(" ", "_")
                stats.player_class = selected_class
                
                # Display confirmation using Interaction system
                success_text = f"Class selected: {class_data['name']}\n\nYour journey begins..."
                Interaction.print_text(success_text, wait_for_input=False)
                continue_prompt()
                
                return selected_class
            else:
                # Display error using Interaction system
                error_text = "Invalid choice. Please enter 1, 2, or 3."
                Interaction.print_text(error_text)
