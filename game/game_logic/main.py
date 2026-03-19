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
from game.game_logic.character_class import CharacterClass
from game.game_logic.random_events import RandomEvents
from game.game_logic.stats import Stats
from game.game_logic.day_cycle import DayCycle
from game.game_logic.game_rules import Game
from game.game_logic.story import Story
from game.game_logic.interaction import set_interaction


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
        pygame.mixer.music.set_volume(0.15)  # 15% volume
    except Exception as e:
        print(f"\n[SYSTEM] Audio Warning: Could not play music ({e})")


def play_game_theme_music():
    """Starts the main game theme music. Works in both GUI and terminal mode."""
    MUSIC_FILE = "enter_the_code_theme.mp3"
    
    try:
        # Re-initialize mixer if needed (it may have been quit by startup menu)
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except:
            # Mixer was quit, need to re-initialize
            pygame.mixer.quit()
            pygame.mixer.init()
        
        # Play the main game theme
        music_path = resource_path(MUSIC_FILE)
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            pygame.mixer.music.set_volume(0.15)  # 15% volume
        else:
            print(f"[SYSTEM] Audio Warning: Theme music file not found at {music_path}")
    except Exception as e:
        print(f"[SYSTEM] Audio Warning: Could not play theme music ({e})")


def main(use_gui: bool = False, use_new_gui: bool = False):
    """
    Main game entry point.
    
    Args:
        use_gui: If True, uses GUI mode (pygame). If False, uses terminal mode (Rich TUI).
        use_new_gui: If True, uses the new pygame-gui based GUI (GUIInteractionV2).
                     If False, uses the old manual GUI (GUIInteraction).
    """
    # Initialize interaction provider (GUI or Terminal)
    if use_gui:
        try:
            from game.game_logic.interaction import get_interaction
            
            if use_new_gui:
                # Use new pygame-gui based GUI
                from game.game_logic.gui_interaction_v2 import GUIInteractionV2
                current_interaction = get_interaction()
                if not isinstance(current_interaction, GUIInteractionV2):
                    import sys
                    import io
                    # Set console encoding to UTF-8 for Windows to handle emojis
                    if sys.platform == "win32":
                        try:
                            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
                        except (ValueError, AttributeError):
                            # stdout/stderr already redirected or closed, skip
                            pass
                    
                    gui = GUIInteractionV2()
                    set_interaction(gui)
                    try:
                        print("[SYSTEM] Modern GUI mode enabled (pygame-gui)")
                    except (ValueError, OSError):
                        # stdout unavailable, ignore
                        pass
            else:
                # Use old manual GUI
                from game.game_logic.gui_interaction import GUIInteraction
                current_interaction = get_interaction()
                if not isinstance(current_interaction, GUIInteraction):
                    import sys
                    import io
                    # Set console encoding to UTF-8 for Windows to handle emojis
                    if sys.platform == "win32":
                        try:
                            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
                        except (ValueError, AttributeError):
                            # stdout/stderr already redirected or closed, skip
                            pass
                    
                    gui = GUIInteraction()
                    set_interaction(gui)
                    try:
                        print("[SYSTEM] GUI mode enabled (legacy)")
                    except (ValueError, OSError):
                        # stdout unavailable, ignore
                        pass
        except Exception as e:
            try:
                print(f"[SYSTEM] Failed to initialize GUI, falling back to terminal: {e}")
            except (ValueError, OSError):
                # stdout unavailable, ignore
                pass
            use_gui = False
    
    # Play background music - theme song starts when game begins
    play_game_theme_music()

    stats = Stats()
    day_cycle = DayCycle()
    events_list = RandomEvents()
    game = Game(stats, day_cycle, events_list)

    story = Story(stats)
    story.start_game_message()

    game.set_difficulty_level()
    
    # Character class selection
    CharacterClass.select_class(stats)

    CarIncident.car_incident_event(stats)

    game.main_menu()


if __name__ == "__main__":
    main()
