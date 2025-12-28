#!/usr/bin/env python3
"""
Build script to create executable with all required resources.
This script ensures all MP3 files, GIF, and icon are included.
"""
import subprocess
import sys
import os
import time
import platform

def check_files_exist():
    """Check that all required resource files exist."""
    required_files = [
        # MP3 files
        'breakdown_theme.mp3',
        'coding_in_snow_theme.mp3',
        'colonel_arrives.mp3',
        'enter_the_code_theme.mp3',
        'martin_meeting_event_the_arrival.mp3',
        'martin_meeting_event_the_awakening.mp3',
        'menu_theme.mp3',
        'road_to_freedom.mp3',
        'sevirra_lenoloc.mp3',
        'tension_theme.mp3',
        # GIF file
        'gun_loop.gif',
        # Icon file
        'game_icon.ico',
        # Main files
        'run_game.py',
        'REFACTOR.spec',
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("ERROR: Missing required files:")
        for file in missing:
            print(f"  - {file}")
        return False
    
    print("✓ All required files found")
    return True

def remove_existing_exe():
    """Remove existing executable if it exists, handling file locks on Windows."""
    # Ensure dist directory exists
    dist_dir = "dist"
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir, exist_ok=True)
        return True
    
    dist_path = os.path.join(dist_dir, "REFACTOR.exe")
    
    if not os.path.exists(dist_path):
        return True
    
    print(f"Found existing executable: {dist_path}")
    print("Attempting to remove it...")
    
    # On Windows, try to remove the file multiple times with delays
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            # Try to remove read-only flag first (if set)
            if platform.system() == "Windows":
                os.chmod(dist_path, 0o777)
            
            os.remove(dist_path)
            print("✓ Successfully removed existing executable")
            # Small delay to ensure file system updates
            time.sleep(0.5)
            return True
        except PermissionError:
            if attempt < max_attempts - 1:
                print(f"  Attempt {attempt + 1}/{max_attempts} failed. Retrying in 1 second...")
                time.sleep(1)
            else:
                print("\n✗ ERROR: Cannot remove existing executable!")
                print("  The file is locked. Please ensure:")
                print("    1. REFACTOR.exe is not currently running")
                print("    2. No other program is using the file")
                print("    3. You have write permissions to the 'dist' folder")
                print("\n  You can manually delete 'dist/REFACTOR.exe' and try again.")
                return False
        except Exception as e:
            print(f"\n✗ Error removing existing executable: {e}")
            return False
    
    return False

def build_exe():
    """Build the executable using PyInstaller."""
    if not check_files_exist():
        sys.exit(1)
    
    # Try to remove existing executable first
    if not remove_existing_exe():
        sys.exit(1)
    
    print("\nBuilding executable with PyInstaller...")
    print("This may take a few minutes...\n")
    
    try:
        # Run PyInstaller with the spec file
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "REFACTOR.spec", "--clean"],
            check=True
        )
        print("\n✓ Build successful!")
        print("\nThe executable can be found in the 'dist' folder:")
        print("  dist/REFACTOR.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error: {e}")
        return False
    except FileNotFoundError:
        print("\n✗ PyInstaller not found. Please install it:")
        print("  pip install pyinstaller")
        return False

if __name__ == "__main__":
    if not build_exe():
        sys.exit(1)

