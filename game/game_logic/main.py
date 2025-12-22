import pygame
import os
import sys
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
        pygame.mixer.music.set_volume(0.3)
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