# Interaction Refactoring Guide

## Overview

The `Interaction` class has been refactored into an abstract interface pattern, allowing you to swap between terminal and GUI rendering without changing your game logic.

## Architecture

### Components

1. **`InteractionInterface`** (Abstract Base Class)
   - Defines the contract for all interaction implementations
   - Methods include: `ask()`, `show_decision()`, `show_outcome()`, `print_text()`
   - All methods accept optional visual context: `character`, `expression`, `bg`

2. **`TerminalInteraction`** (Current Implementation)
   - Implements `InteractionInterface` using Rich TUI
   - Ignores visual context parameters (for now)
   - Maintains all existing formatting functionality

3. **`Interaction`** (Backward Compatibility Wrapper)
   - Static interface that delegates to the current provider
   - **Your existing code doesn't need to change!**
   - All current `Interaction.ask()`, `Interaction.show_decision()` calls still work

4. **Provider Pattern**
   - Global `_interaction_provider` can be swapped
   - `get_interaction()` returns current provider
   - `set_interaction()` allows switching implementations

## Current Usage (No Changes Required)

Your existing code continues to work exactly as before:

```python
# This still works exactly as before
choice = Interaction.show_decision([
    ("1", difficulty_tag, "Option 1"),
    ("2", difficulty_tag, "Option 2")
])

Interaction.show_outcome("- 2500 CZK, - 10 PCR HATRED")
```

## Future Usage (With Visual Context)

When you're ready to add visual context, you can start tagging scenes:

```python
# Old way (still works)
choice = Interaction.show_decision([
    ("1", difficulty_tag, "Option 1"),
    ("2", difficulty_tag, "Option 2")
])

# New way (with visual context - terminal ignores these for now)
choice = Interaction.show_decision(
    [
        ("1", difficulty_tag, "Option 1"),
        ("2", difficulty_tag, "Option 2")
    ],
    character="colonel",
    expression="angry",
    bg="police_station_office"
)
```

## Switching to GUI Mode

When you create a `GUIInteraction` class, switching is one line:

```python
# In main.py
from game.game_logic.interaction import set_interaction, GUIInteraction

# Switch to GUI mode
set_interaction(GUIInteraction())

# All existing Interaction.ask(), Interaction.show_decision() calls
# now use GUI instead of terminal!
```

## Method Signatures

All interaction methods now accept optional visual context:

```python
def ask(
    options: tuple, 
    character: Optional[str] = None, 
    expression: str = "neutral", 
    bg: Optional[str] = None
) -> str

def show_decision(
    option_texts: list[tuple[str, str, str]],
    character: Optional[str] = None,
    expression: str = "neutral",
    bg: Optional[str] = None
) -> str

def show_outcome(
    outcome_text: str,
    character: Optional[str] = None,
    expression: str = "neutral",
    bg: Optional[str] = None
) -> None

def print_text(
    text: str,
    character: Optional[str] = None,
    expression: str = "neutral",
    bg: Optional[str] = None
) -> None
```

## Migration Path

### Phase 1: Current (No Changes)
- All existing code works as-is
- Terminal mode is default
- Visual context parameters are ignored

### Phase 2: Tagging (Optional)
- Start adding `character`, `expression`, `bg` parameters to key scenes
- Terminal still ignores them, but they're ready for GUI

### Phase 3: GUI Implementation
- Create `GUIInteraction` class implementing `InteractionInterface`
- Use `AssetManager` to load sprites/backgrounds
- Switch provider in `main.py`

## Example: Tagging a Scene

```python
# In car_incident_event.py

# Before:
choice = Interaction.show_decision([
    ("1", difficulty_tag, "THE 'MACGYVER' MANEUVER..."),
    ("2", Interaction.get_difficulty_tag(), "THE 'GOOD SOLDIER'...")
])

# After (with visual context):
choice = Interaction.show_decision(
    [
        ("1", difficulty_tag, "THE 'MACGYVER' MANEUVER..."),
        ("2", Interaction.get_difficulty_tag(), "THE 'GOOD SOLDIER'...")
    ],
    character="jb",  # Player character
    expression="worried",  # Worried expression
    bg="parking_lot"  # Parking lot background
)
```

## Benefits

1. **Zero Breaking Changes**: All existing code works immediately
2. **Gradual Migration**: Add visual context tags when convenient
3. **Easy Testing**: Switch between terminal and GUI with one line
4. **Clean Architecture**: Game logic separated from UI rendering
5. **Future-Proof**: Ready for GUI implementation without refactoring

## Next Steps

1. ✅ **Done**: Abstract interface created
2. ✅ **Done**: Terminal implementation working
3. ✅ **Done**: Backward compatibility maintained
4. 🔄 **Next**: Start tagging key scenes with visual context (optional)
5. 🔄 **Future**: Create `GUIInteraction` class
6. 🔄 **Future**: Switch provider in `main.py`
