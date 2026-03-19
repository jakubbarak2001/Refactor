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
    # Check for GUI mode flag (command line argument or environment variable)
    # Check for GUI mode flag (command line argument or environment variable)
    # Default is now NEW GUI
    use_terminal = '--terminal' in sys.argv
    use_old_gui = '--old-gui' in sys.argv
    
    use_gui = not use_terminal
    use_new_gui = use_gui and not use_old_gui
    
    if not use_gui:
        # Terminal mode: spawn console
        # 1. Enforce Terminal FIRST
        enforce_modern_terminal()
        
        # 2. Spawn Console Environment
        spawn_game_console()
    else:
        # GUI mode: Still need stdin for any fallback input calls
        # Create a dummy stdin that returns empty string
        import io
        sys.stdin = io.StringIO()
    
    # 3. NOW load the game (Lazy Loading)
    try:
        from game.game_logic.main import main
        
        if use_new_gui:
            from game.game_logic.gui_menu_v2 import show_startup_menu_v2 as show_startup_menu
        else:
            from game.game_logic.gui_menu import show_startup_menu
            
    except ImportError as e:
        print(f"\nCRITICAL ERROR: {e}")
        print("Required libraries failed to load.")
        input("Press Enter to exit...")
        sys.exit(1)

    # 4. Start Game
    if show_startup_menu():
        main(use_gui=use_gui, use_new_gui=use_new_gui)
