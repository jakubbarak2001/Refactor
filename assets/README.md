# Assets Directory

This directory contains all visual assets for the game.

## Structure

```
assets/
├── sprites/          # Character portraits (832x1248, 2:3 ratio)
│   ├── colonel_neutral.png
│   ├── colonel_angry.png
│   ├── colonel_disappointed.png
│   ├── jb_default.png
│   ├── jb_tired.png
│   ├── jb_worried.png
│   ├── jb_determined.png
│   ├── martin_default.png
│   ├── martin_smiling.png
│   └── martin_serious.png
│
└── backgrounds/      # Scene backgrounds (1920x1080 recommended)
    ├── parking_lot.png
    ├── police_station_office.png
    ├── cafe.png
    ├── police_station_interior.png
    └── police_station_hallway.png
```

## Character Sprites

- **Format**: PNG with transparent background
- **Dimensions**: 832x1248 pixels (2:3 ratio)
- **Naming**: `{character}_{expression}.png`
  - Example: `colonel_angry.png`, `jb_worried.png`

## Backgrounds

- **Format**: PNG or JPG
- **Dimensions**: 1920x1080 pixels (16:9 ratio) recommended
- **Naming**: `{scene_name}.png`
  - Example: `parking_lot.png`, `police_station_office.png`

## Asset Mapping

Asset paths are configured in `assets.json` at the project root.
The `AssetManager` class loads and manages these assets.

## Notes

- All character sprites should be aligned (same eye/shoulder positions)
- Apply consistent color grading across all assets
- Keep file sizes reasonable (PNG compression recommended)
