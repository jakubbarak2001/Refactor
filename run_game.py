import sys
import os
import ctypes
import subprocess
import shutil
import tkinter.messagebox as messagebox
# CRITICAL: Do NOT import game logic here. Move it to the bottom.

def enforce_modern_terminal():
    """Relaunches application inside Windows Terminal if detected running in legacy console."""
    if "WT_SESSION" in os.environ:
        return

    wt_exe = shutil.which("wt.exe")
    if not wt_exe:
        return

    cmd = [wt_exe, "--"]
    if getattr(sys, 'frozen', False):
        cmd.append(sys.executable)
    else:
        cmd.append(sys.executable)
        cmd.append(os.path.abspath(sys.argv[0]))

    try:
        subprocess.Popen(cmd)
        sys.exit(0)
    except Exception as e:
        print(f"Failed to launch Windows Terminal: {e}")

def spawn_game_console():
    """Manually attaches to console and enables colors."""
    if sys.platform == "win32":
        ctypes.windll.kernel32.AllocConsole()
        sys.stdout = open("CONOUT$", "w", encoding="utf-8")
        sys.stderr = open("CONOUT$", "w", encoding="utf-8")
        sys.stdin = open("CONIN$", "r", encoding="utf-8")
        
        # Enable ANSI Colors
        kernel32 = ctypes.windll.kernel32
        hOut = kernel32.GetStdHandle(-11)
        out_mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(hOut, ctypes.byref(out_mode))
        out_mode.value |= 0x0004
        kernel32.SetConsoleMode(hOut, out_mode)

if __name__ == '__main__':
    # 1. Enforce Terminal FIRST
    enforce_modern_terminal()
    
    # 2. Spawn Console Environment
    spawn_game_console()

    # 3. NOW load the game (Lazy Loading)
    try:
        from game.game_logic.main import main
        from game.game_logic.gui_menu import show_startup_menu
    except ImportError as e:
        print(f"\nCRITICAL ERROR: {e}")
        print("Required libraries failed to load.")
        input("Press Enter to exit...")
        sys.exit(1)

    # 4. Start Game
    if show_startup_menu():
        main()
