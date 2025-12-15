import pygame  # <--- NEW IMPORT
import os  # <--- NEW IMPORT
import sys  # <--- NEW IMPORT
from jb_game.game_logic.jb_dev_car_incident_event import CarIncident
from jb_game.game_logic.jb_dev_random_events import RandomEvents
from jb_game.game_logic.jb_dev_stats import JBStats
from jb_game.game_logic.jb_dev_day_cycle import DayCycle
from jb_game.game_logic.jb_dev_game import Game
from jb_game.game_logic.jb_dev_story import Story


def resource_path(relative_path):
    """ Get absolute path to resource (Works for Dev & EXE) """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def play_background_music():
    """Starts the main game loop music."""
    # CHANGE THIS to the name of your in-game music file
    MUSIC_FILE = "enter_the_code_theme.mp3"

    try:
        music_path = resource_path(MUSIC_FILE)
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # Loop forever
        pygame.mixer.music.set_volume(0.3)  # Lower volume for background
    except Exception as e:
        print(f"\n[SYSTEM] Audio Warning: Could not play music ({e})")


def main():
    # 1. Start Music immediately
    play_background_music()

    # 2. Initialize Game Logic
    stats = JBStats()
    day_cycle = DayCycle()
    events_list = RandomEvents()
    game = Game(stats, day_cycle, events_list)

    story = Story(stats)
    story.start_game_message()

    game.set_difficulty_level()

    CarIncident.car_incident_event(stats)

    game.main_menu()


if __name__ == "__main__":
    main()