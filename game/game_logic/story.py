"""Contains everything regarding storytelling."""
from game.game_logic.stats import Stats
from random import randint
from game.game_logic.decision_options import Decision

class Story:
    """Contains the most important story elements, mostly text strings."""
    def __init__(self, stats: Stats):
        """Initialises itself."""
        self.stats = stats

    @staticmethod
    def start_game_message():
        """Gives a neatly formatted welcoming message, for whenever you start the game."""
        print("\nRise and shine, rise and shine JB...it's your big day today.")
        input("(Press any key to continue...)")
        print("\nWelcome to JB - the game!")
        print("In this game, you will be playing as a young police officer, in northern part of Bohemia.")
        print("Initially, you love your job, but everything is about to change very soon...")
        print("\nWill you become a victim of a broken system, or an architect who will create his own?")
        print("In this game, that is up to you...")
        input("(Press any key to continue...)")
        print("Your time and resources are limited - you have to end your job as police officer soon!")
        print("You have three main stats: \n1. Money, \n2. Coding skills, \n3. Hatred of Police")
        print("If you have less than 0 Money, or more than 100 Hatred of Police - you will loose!")