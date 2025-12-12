import sys
import time


class GameEndings:
    """
    Handles all Win/Loss states.
    Uses 'sys.exit()' to actually close the program after the story ends.
    """

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
        input("Try again?")
        sys.exit()