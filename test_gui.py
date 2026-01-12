"""
Quick test script to see the GUI renderer in action.
Run this to see your assets displayed!
"""
import sys
import os
import pygame

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from game.game_logic.gui_interaction import GUIInteraction
from game.game_logic.interaction import set_interaction

def test_gui():
    """Test the GUI with a simple scene."""
    print("Starting GUI test...")
    print("You should see a pygame window open!")
    print("Close the window or press ESC to exit.")
    
    # Switch to GUI mode
    gui = GUIInteraction()
    set_interaction(gui)
    
    # Test 1: Show a decision with background and character
    print("\nTest 1: Decision with background and character")
    choice = gui.show_decision(
        [
            ("1", "[RISKY]", "THE 'MACGYVER' MANEUVER. Try to buff out the scratch with spit and your sleeve."),
            ("2", "[SAFE]", "THE 'GOOD SOLDIER'. Go inside, report it, fill out the forms.")
        ],
        character="jb",
        expression="worried",
        bg="parking_lot"
    )
    print(f"You selected: {choice}")
    
    # Test 2: Show outcome
    print("\nTest 2: Outcome display")
    gui.show_outcome(
        "-2.000 CZK (Deductible), - 10 PCR HATRED (Humiliation).",
        character="jb",
        expression="bored",
        bg="police_station_office"
    )
    
    # Test 3: Show text
    print("\nTest 3: Text display")
    gui.print_text(
        "You stand between the cars. The silence of the parking lot is heavy.",
        character="jb",
        expression="worried",
        bg="parking_lot"
    )
    
    # Test 4: Colonel scene
    print("\nTest 4: Colonel scene")
    gui.show_decision(
        [
            ("1", "[SAFE]", "SUBMIT. Pay the money. Eat the dirt. Keep your job."),
            ("2", "[RISKY]", "CALL PAUL GOODMAN. Sue the department. Burn the bridge.")
        ],
        character="colonel",
        expression="angry",
        bg="police_station_office"
    )
    
    print("\nGUI test complete!")
    pygame.quit()

if __name__ == "__main__":
    try:
        test_gui()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        pygame.quit()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
