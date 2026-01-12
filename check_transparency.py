"""Check if PNG files have transparency."""
from PIL import Image
import os

sprite_path = "assets/sprites/"

print("Checking character sprites for transparency...\n")

for filename in os.listdir(sprite_path):
    if filename.endswith('.png'):
        filepath = os.path.join(sprite_path, filename)
        try:
            img = Image.open(filepath)
            has_alpha = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            
            if has_alpha:
                print(f"[OK] {filename}: HAS transparency")
            else:
                print(f"[NO] {filename}: NO transparency (needs background removal)")
        except Exception as e:
            print(f"[ERROR] {filename}: Error - {e}")
