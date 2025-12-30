import pygame
import os
import sys
from rich import print

# Add project root to Python path when running directly (not via run_game.py)
# Get the directory containing this file (game/game_logic/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root (go up two levels: game/game_logic/ -> game/ -> project root)
project_root = os.path.dirname(os.path.dirname(current_dir))
# Add to sys.path if not already there (prevents import errors when running directly)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game.game_logic.car_incident_event import CarIncident
from game.game_logic.random_events import RandomEvents
from game.game_logic.stats import Stats
from game.game_logic.day_cycle import DayCycle
from game.game_logic.game_rules import Game
from game.game_logic.story import Story


def resource_path(relative_path):
    """ Get absolute path to resource (Works for Dev & EXE) """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def play_background_music():
    """Starts the main game loop music."""
    MUSIC_FILE = "enter_the_code_theme.mp3"

    try:
        music_path = resource_path(MUSIC_FILE)
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.15)  # 50% of original volume
    except Exception as e:
        print(f"\n[SYSTEM] Audio Warning: Could not play music ({e})")


def main():
    play_background_music()

    stats = Stats()
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