import sys
import os
import ctypes
from jb_game.game_logic.jb_dev_main import main
from jb_game.game_logic.jb_dev_gui_menu import show_startup_menu


def enable_ansi_support():
    """
    Forces Windows Console to accept ANSI escape sequences (colors).
    """
    kernel32 = ctypes.windll.kernel32

    # Get the handle to Standard Output
    STD_OUTPUT_HANDLE = -11
    hOut = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    # Get the current mode
    out_mode = ctypes.c_ulong()
    if not kernel32.GetConsoleMode(hOut, ctypes.byref(out_mode)):
        return  # Failed to get mode

    # Flag for Virtual Terminal Processing (ANSI Support)
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    # Set the new mode
    out_mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kernel32.SetConsoleMode(hOut, out_mode)


def spawn_game_console():
    """
    Manually creates a black console window and attaches Python to it.
    """
    # 1. Ask Windows to allocate a new console
    ctypes.windll.kernel32.AllocConsole()

    # 2. Set the Title
    ctypes.windll.kernel32.SetConsoleTitleW("JB: THE DARKEST SHIFT")

    # 3. CRITICAL: Re-connect system inputs/outputs
    sys.stdout = open("CONOUT$", "w", encoding="utf-8")
    sys.stderr = open("CONOUT$", "w", encoding="utf-8")
    sys.stdin = open("CONIN$", "r", encoding="utf-8")

    # 4. CRITICAL: Enable Colors
    enable_ansi_support()


if __name__ == '__main__':
    # 1. Start the GUI
    should_run_game = show_startup_menu()

    if not should_run_game:
        sys.exit()

    # 2. Spawn Console & Fix Colors
    spawn_game_console()

    # 3. Run Game
    main()