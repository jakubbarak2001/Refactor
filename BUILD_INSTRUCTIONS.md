# Building REFACTOR Executable

This document explains how to build the REFACTOR game into an executable file.

## Required Resources

The following files must be present in the project root directory:

### Audio Files (MP3)
- `breakdown_theme.mp3`
- `coding_in_snow_theme.mp3`
- `colonel_arrives.mp3`
- `enter_the_code_theme.mp3`
- `martin_meeting_event_the_arrival.mp3`
- `martin_meeting_event_the_awakening.mp3`
- `menu_theme.mp3`
- `road_to_freedom.mp3`
- `sevirra_lenoloc.mp3`
- `tension_theme.mp3`

### Graphics Files
- `gun_loop.gif` - Animated GIF for the menu
- `game_icon.ico` - Application icon

## Building the Executable

### Option 1: Using the Build Script (Recommended)

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

The script will:
- Verify all required files are present
- Build the executable using PyInstaller
- Output the executable to `dist/REFACTOR.exe`

### Option 2: Using PyInstaller Directly

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build using the spec file:
   ```bash
   pyinstaller REFACTOR.spec --clean
   ```

The executable will be created in `dist/REFACTOR.exe`.

## Spec File Configuration

The `REFACTOR.spec` file includes:
- All 10 MP3 audio files
- The animated GIF (`gun_loop.gif`)
- Application icon (`game_icon.ico`)
- All necessary Python dependencies
- Configuration for a windowed (non-console) application

## Output

After building, you will find:
- `dist/REFACTOR.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)
- `dist/REFACTOR/` - If building in directory mode (unused in current config)

## Notes

- The executable bundles all resources internally
- The `resource_path()` function in the code handles loading resources from the bundled exe
- No external files are required to run the executable
- The build creates a single-file executable

## Troubleshooting

If you encounter issues:
1. Make sure all resource files are in the project root
2. Verify PyInstaller is installed: `pip install pyinstaller`
3. Try a clean build: `pyinstaller REFACTOR.spec --clean`
4. Check that all dependencies are installed: `pip install -r requirements.txt`

