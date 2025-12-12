import sys
import ctypes
from jb_game.game_logic.jb_dev_main import main
from jb_game.game_logic.jb_dev_gui_menu import show_startup_menu


def spawn_game_console():
    """
    Manually creates a black console window and attaches Python to it.
    This allows us to start with NO console, and create one later.
    """
    # 1. Ask Windows to allocate a new console
    ctypes.windll.kernel32.AllocConsole()

    # 2. Set the Title
    ctypes.windll.kernel32.SetConsoleTitleW("JB: THE DARKEST SHIFT")

    # 3. CRITICAL: Re-connect system inputs/outputs
    # Without this, print() and input() would crash because they have nowhere to go.
    sys.stdout = open("CONOUT$", "w", encoding="utf-8")
    sys.stderr = open("CONOUT$", "w", encoding="utf-8")
    sys.stdin = open("CONIN$", "r", encoding="utf-8")


if __name__ == '__main__':
    # 1. Start the GUI
    # Since we will build with --noconsole, ONLY the GUI appears here.
    show_startup_menu()

    # 2. GUI Closed -> Spawn the Console
    spawn_game_console()

    # 3. Start the Game Logic
    main()