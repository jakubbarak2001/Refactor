"""
Character class selection module.
Allows players to choose from different character classes with unique perks.
"""
from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

console = Console(force_terminal=True, width=None)


class CharacterClass:
    """
    Represents a character class with description and perks.
    """
    
    CLASSES = {
        "1": {
            "name": "BODYBUILDER",
            "emoji": "💪",
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
            "emoji": "🎭",
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
            "emoji": "💊",
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
            print("\n")
            
            # Create class selection text with styling
            class_text = Text()
            class_text.append("SELECT YOUR CLASS\n", style="bold white")
            class_text.append("═" * 60 + "\n", style="dim white")
            
            # Build each class option with description and perks
            for key in sorted(CharacterClass.CLASSES.keys()):
                class_data = CharacterClass.CLASSES[key]
                color = class_data['color']
                
                # Class name with emoji
                class_text.append(f"\n[{key}] ", style=f"bold {color}")
                class_text.append(f"{class_data['emoji']} ", style="")
                class_text.append(f"{class_data['name']}\n", style=f"bold {color}")
                
                # Description - emoji and text on same line
                class_text.append("\n📖 ", style="dim white")
                class_text.append(class_data['description'], style="dim white")
                class_text.append("\n", style="")
                
                # Perks section
                class_text.append("\n   ", style="")
                class_text.append("PERKS:\n", style="bold cyan")
                class_text.append("\n", style="")
                
                for perk_entry in class_data['perks']:
                    # Handle newline entries (empty perk for spacing) - can be 2 or 3 tuple
                    if len(perk_entry) == 2 and perk_entry[0] == "\n":
                        class_text.append("\n", style="")
                        continue
                    
                    # Unpack 3-tuple (symbol, perk_text, perk_color)
                    symbol, perk_text, perk_color = perk_entry
                    
                    class_text.append("   ", style="")
                    if symbol == "+":
                        class_text.append("✅ ", style=perk_color)
                    elif symbol == "-":
                        class_text.append("❌ ", style=perk_color)
                    
                    # Handle bold text in perks (for Modafinil/Adderall)
                    if "Modafinil" in perk_text or "Adderall" in perk_text:
                        parts = perk_text.split(" like ")
                        if len(parts) == 2:
                            class_text.append(parts[0] + " like ", style=perk_color)
                            # Make the supplement names bold
                            supplements = parts[1].split(" or ")
                            if len(supplements) == 2:
                                class_text.append(supplements[0], style=f"bold {perk_color}")
                                class_text.append(" or ", style=perk_color)
                                class_text.append(supplements[1], style=f"bold {perk_color}")
                            else:
                                class_text.append(parts[1], style=perk_color)
                        else:
                            class_text.append(perk_text, style=perk_color)
                    else:
                        class_text.append(perk_text, style=perk_color)
                    class_text.append("\n", style="")
                
                class_text.append("\n" + "─" * 60 + "\n", style="dim white")
            
            # Display in a large styled panel
            print(Panel(
                class_text,
                border_style="bold bright_yellow",
                title="[bold black on bright_yellow] > CHARACTER CLASS SELECTION < [/]",
                padding=(1, 4),
                expand=False
            ))
            
            # Get user input
            choice = console.input("\n[bold cyan]Enter your choice[/bold cyan] [dim](1-3)[/dim]: ").strip()

            if choice in CharacterClass.CLASSES:
                class_data = CharacterClass.CLASSES[choice]
                color = class_data['color']
                
                # Create confirmation message
                confirm_text = Text()
                confirm_text.append("You selected: ", style="bold white")
                confirm_text.append(f"{class_data['emoji']} ", style="")
                confirm_text.append(f"{class_data['name']}", style=f"bold {color}")
                confirm_text.append("\n\n", style="")
                confirm_text.append("CLASS DESCRIPTION:\n", style="bold cyan")
                confirm_text.append(f"  {class_data['description']}\n", style="dim white")
                confirm_text.append("\n", style="")
                confirm_text.append("YOUR PERKS:\n", style="bold cyan")
                confirm_text.append("\n", style="")
                
                for perk_entry in class_data['perks']:
                    # Handle newline entries (empty perk for spacing) - can be 2 or 3 tuple
                    if len(perk_entry) == 2 and perk_entry[0] == "\n":
                        confirm_text.append("\n", style="")
                        continue
                    
                    # Unpack 3-tuple (symbol, perk_text, perk_color)
                    symbol, perk_text, perk_color = perk_entry
                    
                    confirm_text.append("  ", style="")
                    if symbol == "+":
                        confirm_text.append("✅ ", style=perk_color)
                    elif symbol == "-":
                        confirm_text.append("❌ ", style=perk_color)
                    
                    # Handle bold text in perks (for Modafinil/Adderall)
                    if "Modafinil" in perk_text or "Adderall" in perk_text:
                        parts = perk_text.split(" like ")
                        if len(parts) == 2:
                            confirm_text.append(parts[0] + " like ", style=perk_color)
                            # Make the supplement names bold
                            supplements = parts[1].split(" or ")
                            if len(supplements) == 2:
                                confirm_text.append(supplements[0], style=f"bold {perk_color}")
                                confirm_text.append(" or ", style=perk_color)
                                confirm_text.append(supplements[1], style=f"bold {perk_color}")
                            else:
                                confirm_text.append(parts[1], style=perk_color)
                        else:
                            confirm_text.append(perk_text, style=perk_color)
                    else:
                        confirm_text.append(perk_text, style=perk_color)
                    confirm_text.append("\n", style="")
                
                confirm_text.append("\nProceed with this class?", style="italic")
                
                print("\n")
                print(Panel(
                    confirm_text,
                    border_style=f"bold {color}",
                    title=f"[bold white on {color}] > CONFIRM CLASS SELECTION < [/]",
                    padding=(1, 3),
                    expand=False
                ))
                
                confirm_select = console.input("\n[bold](y/n)[/bold]: ").strip().lower()
                if confirm_select != "y":
                    continue

                # Store selected class
                selected_class = class_data['name'].lower().replace(" ", "_")
                stats.player_class = selected_class
                
                # Display confirmation
                success_text = Text()
                success_text.append("Class selected: ", style="bold white")
                success_text.append(f"{class_data['emoji']} ", style="")
                success_text.append(f"{class_data['name']}", style=f"bold {color}")
                success_text.append("\n\n", style="")
                success_text.append("Your journey begins...", style="dim white")
                
                print("\n")
                print(Panel(
                    success_text,
                    border_style=f"bold {color}",
                    title=f"[bold white on {color}] > CLASS LOCKED IN < [/]",
                    padding=(1, 2),
                    expand=False
                ))
                
                return selected_class
            else:
                print("\n[bold red]Invalid choice. Please enter 1, 2, or 3.[/bold red]")
