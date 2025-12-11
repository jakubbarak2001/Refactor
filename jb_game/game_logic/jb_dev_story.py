"""Contains everything regarding storytelling."""
from jb_game.game_logic.jb_dev_stats import JBStats
from random import randint
from jb_game.game_logic.jb_dev_decision import Decision

class Story:
    """Contains the most important story elements, mostly text strings."""
    def __init__(self, stats: JBStats):
        """Initialises itself."""
        self.stats = stats

    @staticmethod
    def start_game_message():
        """Gives a neatly formatted welcoming message, for whenever you start a game."""
        print("\nWelcome to JB - the game! \n\nIn this game, you will be playing as a young and perspective police "
              "officer in northern part of Bohemia, where sun never rises and criminality is growing rapidly. "
              "\nThe game begins in 1.7.2025, at start you love your job, but that is soon to change, due to the "
              "unforeseen consequences. \nSoon, you will realise your path lies elsewhere - in software development. "
              "Your time and resources are limited - you have to end your job as police officer soon!"
              "\n\nYou will have to balance between 3 main stats: \n1. Money, \n2. Coding skills, \n3. Hatred of Police "
              "\n\nThe most important rule for you is always have more than 0 money and to keep your "
              "hatred of police under 100."
              "\nIn the following section, you will be able to choose your difficulty level, good luck and have fun!")