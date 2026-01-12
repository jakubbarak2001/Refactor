# How to Remove Backgrounds and Make PNG Files Transparent

## The Problem
Converting JPG to PNG doesn't automatically add transparency. You need to **remove the background** in an image editor.

## Solution: Use GIMP (Free)

### Step-by-Step Guide

#### Method 1: Select by Color (Easiest for solid backgrounds)

1. **Open your PNG file in GIMP**
   - File → Open → Select your character sprite

2. **Add Alpha Channel (Enable Transparency)**
   - Right-click the layer → "Add Alpha Channel"
   - OR: Layer → Transparency → Add Alpha Channel

3. **Select Background**
   - Tool: **Select by Color** (Shift+O)
   - Click on the background color
   - Adjust tolerance (15-25) if needed
   - Press Delete to remove selected area

4. **Clean Up Edges**
   - Use **Eraser Tool** (Shift+E) for any remaining background bits
   - Use **Fuzzy Select Tool** (U) for complex areas

5. **Save with Transparency**
   - File → Export As
   - Choose filename: `character_name.png`
   - **IMPORTANT**: In export dialog, check "Save color values from transparent pixels"
   - Click Export
   - In PNG export options, make sure "Save background color" is UNCHECKED
   - Click Export

#### Method 2: Foreground Select (Better for complex backgrounds)

1. **Open file and add Alpha Channel** (same as above)

2. **Select Foreground**
   - Tool: **Foreground Select Tool** (Shift+F)
   - Roughly mark around your character
   - Press Enter
   - Mark areas to keep (green) and remove (red)
   - Press Enter again

3. **Invert Selection**
   - Select → Invert
   - Press Delete

4. **Save** (same as Method 1)

## Quick Checklist

- [ ] Opened PNG in GIMP
- [ ] Added Alpha Channel to layer
- [ ] Selected and deleted background
- [ ] Cleaned up edges with eraser
- [ ] Exported as PNG with transparency enabled
- [ ] Verified transparency (should see checkerboard in GIMP)

## Alternative: Online Tools

If you prefer not to use GIMP:

1. **Remove.bg** (https://www.remove.bg/)
   - Upload your image
   - Download result (automatically transparent PNG)
   - Free tier available

2. **Photopea** (https://www.photopea.com/)
   - Free online Photoshop alternative
   - Same process as GIMP

## Verify Transparency

After saving, you should see:
- **In GIMP**: Checkerboard pattern where background was
- **In File Explorer**: Preview should show transparent background
- **In game**: Character should appear on top of background without white/colored box

## Your Files to Process

Process these files to add transparency:
- `jb_worried.png`
- `jb_neutral.png`
- `jb_determined.png`
- `jb_bored.png`
- `colonel_normal.png` (when you add it)
- `colonel_angry.png` (when you add it)
- `colonel_dissapointed.png` (when you add it)

## Tips

- **Save originals**: Keep a backup of files before removing backgrounds
- **Consistent backgrounds**: If all characters have same background color, use "Select by Color" for speed
- **Edge quality**: Use "Feather" (Select → Feather) with 1-2px before deleting for smoother edges
- **Batch processing**: GIMP supports batch operations if you have many files
