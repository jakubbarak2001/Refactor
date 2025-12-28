import os
import sys
import time

import pygame
from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group, Console

from game.game_logic.press_enter_to_continue import continue_prompt


def resource_path(relative_path):
    """ Get absolute path to resource (Works for Dev & EXE) """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class GameEndings:
    """
    Handles all Win/Loss states.
    Uses 'sys.exit()' to actually close the program after the story ends.
    """

    @staticmethod
    def _play_ending_music(track_name):
        """
        Helper to stop current music and play the ending theme.
        """
        try:
            # Ensure mixer is initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Stop the game loop music
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

            # Load the new tragic/epic theme
            path = resource_path(track_name)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)  # Loop forever until they close the window
            pygame.mixer.music.set_volume(0.6)  # Slightly louder for dramatic effect
        except Exception as e:
            print(f"[Audio Error]: {e}")

    @staticmethod
    def _slow_print(text, delay=0.02):
        """Optional helper to make text feel more dramatic."""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def mental_breakdown_ending(stats):
        """Triggered when PCR Hatred >= 100."""
        # 1. PLAY MUSIC
        GameEndings._play_ending_music("breakdown_theme.mp3")

        print("\n==========================================")
        GameEndings._slow_print(f"GAME OVER: CRITICAL PSYCHOSIS (Hatred: {stats.pcr_hatred})")
        print("==========================================")

        GameEndings._slow_print("\nIt happens during a routine briefing.")
        GameEndings._slow_print("The Colonel is talking about 'Uniform Standards'.")
        GameEndings._slow_print("The sound of his voice turns into a high-pitched screeching noise.")
        GameEndings._slow_print("\nYou stand up. You aren't in control anymore.")
        GameEndings._slow_print("You scream. You flip the table. You throw your chair through the window.")

        continue_prompt()

        GameEndings._slow_print("\nThree colleagues have to tackle you.")
        GameEndings._slow_print("They sedate you. You wake up in a white room with soft walls.")
        GameEndings._slow_print("The doctor says you need 'rest'. A lot of rest.")
        GameEndings._slow_print("You lost your badge. You lost your gun. But finally... there is silence.")

        GameEndings._slow_print("\n[BAD ENDING: INSTITUTIONALISED]")
        input("Try again?")
        sys.exit()

    @staticmethod
    def homeless_ending(stats):
        """Triggered when Money <= 0."""
        # 1. PLAY MUSIC
        GameEndings._play_ending_music("coding_in_snow_theme.mp3")

        print("\n==========================================")
        GameEndings._slow_print(f"GAME OVER: BANKRUPTCY (Money: {stats.available_money})")
        print("==========================================")

        GameEndings._slow_print("\nYour card is declined at the grocery store. For a rohlík.")
        GameEndings._slow_print("Your landlord calls. Eviction notice.")
        GameEndings._slow_print("You sell your laptop. Then your monitor. Then your phone.")
        GameEndings._slow_print("\nBut it's not enough.")
        GameEndings._slow_print("You end up sleeping in your car. Then you lose the car.")
        GameEndings._slow_print("You cannot code on paper crates in the snow.")

        GameEndings._slow_print("[BAD ENDING: THE STREETS]")
        restart = input("Try again?")
        sys.exit()


class GoodEnding:
    """
    Handles the 'True' Ending of the game.
    The 'Truman Show' / 'Mr. Robot' realization where JB exits the simulation.
    """

    def __init__(self):
        pass

    def _slow_print(self, text, delay=0.05, color=None, bold=False):
        """
        Cinematic printing with Rich markup support.
        If text contains Rich markup, it will be rendered properly.
        """
        # Check if text already contains Rich markup tags
        if "[" in text and ("]" in text or "[/" in text):
            # Text contains Rich markup, print it directly with Rich
            print(text)
        else:
            # Plain text, apply optional styling and print
            if bold:
                text = f"[bold]{text}[/bold]"
            if color:
                text = f"[{color}]{text}[/{color}]"
            print(text)

    def trigger_ending(self, stats=None):
        """
        The Final Sequence.
        JB laughs at the absurdity, types the exit command, and walks into reality.
        
        Args:
            stats: Stats object to calculate final score (optional)
        """
        # --- MUSIC START: ROAD TO FREEDOM ---
        # Starts playing immediately as the relief hits you
        GameEndings._play_ending_music("road_to_freedom.mp3")

        # --- THE LAUGHTER ---
        print("\n")
        self._slow_print("You start to chuckle.", delay=0.05)
        time.sleep(1)
        self._slow_print("The chuckle turns into a laugh.", delay=0.05)
        self._slow_print("[bold]A loud, liberating, uncontrollable laugh.[/bold]", delay=0.05)

        time.sleep(2)
        print("\n[red]COLONEL: 'WHY ARE YOU LAUGHING?! YOU THINK THIS IS FUNNY? YOUR LIFE IS OVER!'[/red]")
        time.sleep(1)

        # --- THE REALIZATION ---
        self._slow_print("\n'No, Colonel,' you say, wiping a tear from your eye.", delay=0.04)
        self._slow_print("'My life isn't over.'", delay=0.06)
        time.sleep(1)

        self._slow_print("\n[bold green]'It's just compiling.'[/bold green]", delay=0.1)
        time.sleep(2)

        # --- THE EXIT ---
        print("\n" + "=" * 60)
        self._slow_print("[green] > EXECUTING: sys.exit(0) ...[/green]", delay=0.05)
        self._slow_print("[green] > TEARING DOWN: police_station_module.py ...[/green]", delay=0.05)
        self._slow_print("[green] > RELEASING RESOURCES ...[/green]", delay=0.05)
        print("=" * 60 + "\n")
        time.sleep(2)

        self._slow_print("You turn your back on him.", delay=0.06)
        self._slow_print("He is still screaming, his face red, veins popping.", delay=0.04)
        self._slow_print("But as you walk towards the exit door, his voice starts to fade.", delay=0.04)
        self._slow_print("Not because of distance. But because you lowered his volume slider.", delay=0.04)

        time.sleep(2)
        self._slow_print("\nYou reach the heavy metal door of the station.", delay=0.06)
        self._slow_print("It's supposed to be locked. It's supposed to be hard to leave.", delay=0.04)
        self._slow_print("You simply push it open.", delay=0.04)

        # --- THE WHEAT FIELD (Truman Show Theme) ---
        print("\n")
        self._slow_print("[bold]The blinding light hits you.[/bold]", delay=0.05)
        time.sleep(2)

        self._slow_print("You step out. You expect the grey, dirty street of the city.", delay=0.05)
        self._slow_print("Instead...", delay=0.1)

        self._slow_print("\nIt is a field. A vast, golden wheat field under a perfect blue sky.", delay=0.05)
        self._slow_print("The sun is warm on your face. The air smells of summer and freedom.", delay=0.05)

        time.sleep(1.5)
        self._slow_print("\nYou look back.", delay=0.06)
        self._slow_print("The Police Station isn't a building anymore.", delay=0.05)
        self._slow_print("It's just a small, grey, cardboard box sitting in the middle of the field.", delay=0.05)
        self._slow_print("You can still hear a tiny, squeaky voice inside yelling about regulations.", delay=0.02)

        time.sleep(2)
        self._slow_print("\nYou smile.", delay=0.1)
        self._slow_print("You reach out and touch the wheat. It feels real.", delay=0.06)
        self._slow_print("You take a deep breath.", delay=0.06)

        print("\n")
        self._slow_print("[bold green]SYSTEM: BUILD SUCCESSFUL.[/bold green]", delay=0.08)
        self._slow_print("[bold green]WELCOME TO PRODUCTION, JB.[/bold green]", delay=0.08)

        time.sleep(3)
        
        # Create EPIC ending display with ASCII art and multiple panels
        print("\n\n\n")
        
        # ASCII Art for "THE END"
        the_end_art = r"""
████████╗██╗  ██╗███████╗    ███████╗███╗   ██╗██████╗ 
╚══██╔══╝██║  ██║██╔════╝    ██╔════╝████╗  ██║██╔══██╗
   ██║   ███████║█████╗      █████╗  ██╔██╗ ██║██║  ██║
   ██║   ██╔══██║██╔══╝      ██╔══╝  ██║╚██╗██║██║  ██║
   ██║   ██║  ██║███████╗    ███████╗██║ ╚████║██████╔╝
   ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚══════╝╚═╝  ╚═══╝╚═════╝ 
"""
        
        # Process ASCII art with gradient effect (green to gold)
        art_lines = the_end_art.strip("\n").split("\n")
        styled_art = Text()
        for i, line in enumerate(art_lines):
            if line.strip():  # Skip empty lines
                # Create gradient from bright green to bright yellow
                if i < len(art_lines) / 2:
                    style = "bold bright_green"
                else:
                    style = "bold bright_yellow"
                styled_art.append(line + "\n", style=style)
        
        # Create the main ending panel with ASCII art
        console = Console()
        ending_panel = Panel(
            Align.center(styled_art, vertical="middle"),
            border_style="bold bright_white",
            title="[bold bright_white on black] ═══ FINAL SCENE ═══ [/]",
            subtitle="[bold bright_green] YOU ESCAPED THE SIMULATION [/]",
            padding=(2, 4),
            expand=False
        )
        
        # Create final score panel (replaces SYSTEM LOG)
        if stats:
            # Calculate base final score: (money / 100) + (coding_skill * 100)
            base_score = (stats.available_money / 100) + (stats.coding_skill * 100)
            
            # Apply difficulty multiplier
            difficulty_multiplier = 1.0
            difficulty_name = "Unknown"
            if stats.difficulty == "easy":
                difficulty_multiplier = 1.0
                difficulty_name = "Easy"
            elif stats.difficulty == "hard":
                difficulty_multiplier = 2.5
                difficulty_name = "Hard"
            elif stats.difficulty == "insane":
                difficulty_multiplier = 5.0
                difficulty_name = "Insane"
            
            final_score = base_score * difficulty_multiplier
            final_score = int(final_score)  # Convert to integer for display
            
            score_text = Text()
            score_text.append("💰 Total Money: ", style="bold cyan")
            score_text.append(f"{stats.available_money:,} CZK\n", style="bright_white")
            score_text.append("💻 Coding Skill: ", style="bold cyan")
            score_text.append(f"{stats.coding_skill} points\n", style="bright_white")
            score_text.append("🎚️  Difficulty: ", style="bold cyan")
            score_text.append(f"{difficulty_name} (x{difficulty_multiplier:.1f})\n", style="bright_white")
            score_text.append("═" * 35 + "\n", style="dim white")
            score_text.append("🏆 FINAL SCORE: ", style="bold bright_yellow")
            score_text.append(f"{final_score:,}", style="bold bright_yellow")
            
            message_panel = Panel(
                score_text,
                border_style="bold bright_yellow",
                title="[bold white on bright_yellow] > FINAL SCORE < [/]",
                padding=(1, 3),
                expand=False
            )
        else:
            # Fallback if stats not provided
            message_text = Text()
            message_text.append("FINAL SCORE: ", style="bold cyan")
            message_text.append("N/A", style="bright_white")
            
            message_panel = Panel(
                message_text,
                border_style="bold cyan",
                title="[bold white on cyan] > FINAL SCORE < [/]",
                padding=(1, 3),
                expand=False
            )
        
        # Create final credits panel
        credits_text = Text()
        credits_text.append("Thank you for playing\n", style="bold white")
        credits_text.append("REFACTOR\n", style="bold bright_yellow")
        credits_text.append("\n\"Code your way out, or lose your mind trying.\"\n", style="italic dim white")
        credits_text.append("\n- Jakub Barák", style="dim white")
        
        credits_panel = Panel(
            Align.center(credits_text),
            border_style="bold yellow",
            title="[bold white on yellow] > CREDITS < [/]",
            padding=(1, 4),
            expand=False
        )
        
        # Group all panels and center them
        final_group = Group(
            Align.center(ending_panel),
            Text(),  # Empty line for spacing
            Align.center(message_panel),
            Text(),  # Empty line for spacing
            Align.center(credits_panel)
        )
        
        console.print(final_group, justify="center")
        print("\n\n")
        
        # Display exit prompt using Panel like continue_prompt
        print(Panel.fit(
            "[italic yellow](PRESS ENTER TO EXIT GAME)[/italic yellow]",
            border_style="bold",
            width=40
        ))
        
        # Wait for Enter key (similar to continue_prompt)
        if sys.platform == "win32":
            import msvcrt
            while True:
                key = msvcrt.getwch()
                if key == '\r':  # Enter key
                    break
        else:
            import getpass
            getpass.getpass("")
        
        sys.exit()
