# Asset Creation Guide

## Overview
This guide explains how to create and organize visual assets for the game using the recommended workflow.

## Workflow Summary

### 1. Leonardo.ai (Character & Background Generation)

#### Character Portraits
**Prompt Template:**
```
Portrait of [character description], 
dark satirical game art style, 
moody cinematic lighting, 
realistic but stylized, 
Northern Bohemia police setting, 
consistent character design, 
game character portrait, 
transparent background preferred
```

**Characters to Generate:**
- **Colonel**: neutral, angry, disappointed expressions
- **JB (Player)**: default, tired, determined, worried expressions  
- **Martin**: default, smiling, serious expressions

**Tips:**
- Use the same reference image for all expressions of the same character
- Generate at 512x512 or 1024x1024 resolution
- Request transparent background or use "remove.bg" API

#### Backgrounds
**Prompt Template:**
```
[Location description], 
dark moody atmosphere, 
Northern Bohemia setting, 
noir game background art, 
cinematic composition, 
1920x1080 resolution
```

**Backgrounds Needed:**
- Police station parking lot (early morning, moody)
- Police station office (Colonel's office, bureaucratic)
- Cafe (meeting location, cozy but dim)
- Police station interior/hallway

### 2. GIMP Post-Processing

#### Character Sprites
1. **Background Removal**
   - Use "Select by Color" tool (tolerance ~15-25)
   - Or use "Foreground Select" tool for complex edges
   - Delete selection, save as PNG with transparency

2. **Alignment Check**
   - Open all expressions of same character
   - Layer them on top of each other
   - Align eyes and shoulders using guides
   - Ensure consistent size (recommend 512x512 or 1024x1024)

3. **Color Grading**
   - Apply consistent color curve to all character expressions
   - Desaturate slightly (10-15%)
   - Increase contrast slightly
   - Apply same settings to all expressions

#### Backgrounds
1. **Color Grading**
   - Apply "Noir" filter or adjust curves
   - Desaturate (20-30% for moody feel)
   - Darken shadows, slightly brighten highlights
   - Ensure all backgrounds have consistent color palette

2. **Resolution**
   - Resize to 1920x1080 (or your target resolution)
   - Use high-quality resampling (Lanczos)

### 3. File Organization

Create this directory structure:
```
assets/
  sprites/
    colonel_neutral.png
    colonel_angry.png
    colonel_disappointed.png
    jb_default.png
    jb_tired.png
    jb_determined.png
    jb_worried.png
    martin_default.png
    martin_smiling.png
    martin_serious.png
  backgrounds/
    parking_lot.png
    police_station_office.png
    cafe.png
    police_station_interior.png
    police_station_hallway.png
```

### 4. JSON Configuration

Update `assets.json` with your actual file paths. The `AssetManager` class will automatically load these mappings.

## Integration with Code

### Example Usage:

```python
from game.game_logic.asset_manager import AssetManager

# Initialize asset manager
asset_manager = AssetManager("assets.json")

# Get background for a scene
bg_path = asset_manager.get_background("parking_lot")

# Get character sprite
colonel_angry = asset_manager.get_character_sprite("colonel", "angry")

# Get complete scene assets
bg, char_name, expression = asset_manager.get_scene_assets("colonel_office_angry")
character_sprite = asset_manager.get_character_sprite(char_name, expression) if char_name else None
```

## Tips for Consistency

1. **Color Palette**: Use a consistent color palette across all assets
   - Dark blues, grays, muted tones
   - Low saturation (10-20% desaturation)
   - High contrast in key areas

2. **Lighting**: Maintain consistent lighting direction
   - All characters should have light from same direction
   - Backgrounds should match character lighting

3. **Style**: Keep art style consistent
   - Same level of detail
   - Same brush/texture style
   - Same level of stylization

4. **Resolution**: 
   - Character sprites: 512x512 or 1024x1024
   - Backgrounds: 1920x1080 (or match your game window size)

## Cost Estimate

- **Leonardo.ai**: Free tier (150 images/day) or $10/month (unlimited)
- **GIMP**: Free
- **Total**: $0-10/month depending on generation needs

## Timeline Estimate

- Character portraits (3 characters × 3-4 expressions): 2-3 hours
- Backgrounds (5 scenes): 1-2 hours  
- GIMP post-processing: 3-4 hours
- **Total**: 6-9 hours for complete asset set
