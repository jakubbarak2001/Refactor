import sys
import time
import os
import pygame

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
    def _slow_print(text, delay=0.03):
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

        red = "\033[91m"
        reset = "\033[0m"

        print(f"\n{red}==========================================")
        GameEndings._slow_print(f"GAME OVER: CRITICAL PSYCHOSIS (Hatred: {stats.pcr_hatred})")
        print(f"=========================================={reset}")

        GameEndings._slow_print("\nIt happens during a routine briefing.")
        GameEndings._slow_print("The Colonel is talking about 'Uniform Standards'.")
        GameEndings._slow_print("The sound of his voice turns into a high-pitched screeching noise.")
        GameEndings._slow_print("\nYou stand up. You aren't in control anymore.")
        GameEndings._slow_print("You scream. You flip the table. You throw your chair through the window.")

        input("\n(PRESS ENTER)")

        GameEndings._slow_print("\nThree colleagues have to tackle you.")
        GameEndings._slow_print("They sedate you. You wake up in a white room with soft walls.")
        GameEndings._slow_print("The doctor says you need 'rest'. A lot of rest.")
        GameEndings._slow_print("You lost your badge. You lost your gun. But finally... there is silence.")

        GameEndings._slow_print(f"\n{red}[BAD ENDING: INSTITUTIONALISED]{reset}")
        input("Try again?")
        sys.exit()

    @staticmethod
    def homeless_ending(stats):
        """Triggered when Money <= 0."""
        # 1. PLAY MUSIC
        GameEndings._play_ending_music("coding_in_snow_theme.mp3")

        red = "\033[91m"
        reset = "\033[0m"

        print(f"\n{red}==========================================")
        GameEndings._slow_print(f"GAME OVER: BANKRUPTCY (Money: {stats.available_money})")
        print(f"=========================================={reset}")

        GameEndings._slow_print("\nYour card is declined at the grocery store. For a rohlík.")
        GameEndings._slow_print("Your landlord calls. Eviction notice.")
        GameEndings._slow_print("You sell your laptop. Then your monitor. Then your phone.")
        GameEndings._slow_print("\nBut it's not enough.")
        GameEndings._slow_print("You end up sleeping in your car. Then you lose the car.")
        GameEndings._slow_print("You cannot code on paper crates in the snow.")

        GameEndings._slow_print(f"\n{red}[BAD ENDING: THE STREETS]{reset}")
        restart = input("Try again?")
        sys.exit()


class GoodEnding:
    """
    Handles the 'True' Ending of the game.
    The 'Truman Show' / 'Mr. Robot' realization where JB exits the simulation.
    """

    def __init__(self):
        self.green = "\033[92m"
        self.bold = "\033[1m"
        self.reset = "\033[0m"
        self.red = "\033[91m"

    def _slow_print(self, text, delay=0.05, color=None, bold=False):
        """Cinematic printing."""
        if color:
            sys.stdout.write(color)
        if bold:
            sys.stdout.write(self.bold)

        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)

        sys.stdout.write(self.reset)
        print()

    def trigger_ending(self):
        """
        The Final Sequence.
        JB laughs at the absurdity, types the exit command, and walks into reality.
        """
        # --- MUSIC START: ROAD TO FREEDOM ---
        # Starts playing immediately as the relief hits you
        GameEndings._play_ending_music("road_to_freedom.mp3")

        # --- THE LAUGHTER ---
        print("\n")
        self._slow_print("You start to chuckle.", delay=0.1)
        time.sleep(1)
        self._slow_print("The chuckle turns into a laugh.", delay=0.05)
        self._slow_print("A loud, liberating, uncontrollable laugh.", delay=0.05, bold=True)

        time.sleep(2)
        print(f"\n{self.red}COLONEL: 'WHY ARE YOU LAUGHING?! YOU THINK THIS IS FUNNY? YOUR LIFE IS OVER!'{self.reset}")
        time.sleep(1)

        # --- THE REALIZATION ---
        self._slow_print("\n'No, Colonel,' you say, wiping a tear from your eye.", delay=0.04)
        self._slow_print("'My life isn't over.'", delay=0.06)
        time.sleep(1)

        self._slow_print(f"\n{self.green}'It's just compiling.'{self.reset}", delay=0.1, bold=True)
        time.sleep(2)

        # --- THE EXIT ---
        print("\n" + "=" * 60)
        self._slow_print(f" > EXECUTING: sys.exit(0) ...", delay=0.05, color=self.green)
        self._slow_print(f" > TEARING DOWN: police_station_module.py ...", delay=0.05, color=self.green)
        self._slow_print(f" > RELEASING RESOURCES ...", delay=0.05, color=self.green)
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
        self._slow_print(f"{self.bold}The blinding light hits you.{self.reset}", delay=0.1)
        time.sleep(2)

        self._slow_print("You step out. You expect the grey, dirty street of the city.", delay=0.05)
        self._slow_print("Instead...", delay=0.1)

        self._slow_print("\nIt is a field. A vast, golden wheat field under a perfect blue sky.", delay=0.05)
        self._slow_print("The sun is warm on your face. The air smells of summer and freedom.", delay=0.05)

        time.sleep(1.5)
        self._slow_print("\nYou look back.", delay=0.06)
        self._slow_print("The Police Station isn't a building anymore.", delay=0.05)
        self._slow_print("It's just a small, grey, cardboard box sitting in the middle of the field.", delay=0.05)
        self._slow_print("You can still hear a tiny, squeaky voice inside yelling about regulations.", delay=0.03)

        time.sleep(2)
        self._slow_print("\nYou smile.", delay=0.1)
        self._slow_print("You reach out and touch the wheat. It feels real.", delay=0.06)
        self._slow_print("You take a deep breath.", delay=0.06)

        print("\n")
        self._slow_print(f"{self.green}SYSTEM: BUILD SUCCESSFUL.{self.reset}", delay=0.08, bold=True)
        self._slow_print(f"{self.green}WELCOME TO PRODUCTION, JB.{self.reset}", delay=0.08, bold=True)

        time.sleep(3)
        print("\n\n")
        print("=" * 30)
        print("       THE END")
        print("=" * 30)
        input("\n(PRESS ENTER TO EXIT GAME)")
        sys.exit()