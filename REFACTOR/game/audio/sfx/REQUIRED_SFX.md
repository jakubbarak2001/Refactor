# Battle SFX — required files

Phase A of the juice sprint expects these `.ogg` files in this directory.
The engine already calls them via `_play_battle_sfx()` in `cards/battle_engine.rpy`;
missing files are silently skipped (no error, no log spam), so the code works
with or without these files installed.

When you drop real audio in, name it exactly as listed below. The engine will
auto-pick it up — no code change needed.

## File list

| File | Triggered when | Length | Character |
|------|---------------|--------|-----------|
| `card_attack.ogg` | Player plays an Attack-type card (Strike, Heavy Set, etc.) | 0.15–0.30s | Sharp, percussive — sword swipe / glove punch / bat crack. Distinct *bite* on attack. |
| `card_skill.ogg` | Player plays a Skill-type card (Defend, Refactor, Read Him, etc.) | 0.15–0.30s | Soft thwip / paper-rustle / shield-up clink. Subtler than attack. |
| `card_power.ogg` | Player plays a Power-type card (Stoic Anchor, Iron Stance, Job Offer) | 0.40–0.80s | Rising synth swell / arcane chime / power-up flourish. Feels heavier — Power cards persist for the fight. |
| `hit_thud.ogg` | Either side takes damage > 0 | 0.10–0.25s | Body-thump / fist-on-flesh / muffled impact. Same sound for both sides — pitch can vary slightly via the engine if needed later. |
| `block_clang.ogg` | Player gains block (any amount) | 0.15–0.35s | Metallic clink / shield-set / armor-up. Crisp, brief. |
| `end_turn.ogg` | Player presses END TURN | 0.15–0.30s | UI commit sound — a "lock-in" tone or button-click with weight. Not a generic UI beep. |

## Where to source

- **freesound.org** (Creative Commons) — primary recommendation. Most categories above have hundreds of variants. Search keywords: `sword swing`, `paper rustle`, `synth swell`, `body punch`, `metal clang`, `ui confirm`.
- **zapsplat.com** (free with attribution) — secondary.
- **fesliyanstudios.com** — game SFX, free with attribution.

## After sourcing

1. Trim each clip to the duration listed above (avoid long tails — battles fire many sounds in succession; long tails overlap and muddy).
2. Normalize volumes so no single sound is >2x louder than another. Hit sounds slightly louder than UI sounds is fine.
3. Save as `.ogg` (Vorbis or Opus, both work in Ren'Py). Stereo 44.1kHz is overkill for SFX — mono 22kHz is plenty for percussive sounds and saves space.
4. Drop them in this directory with the exact filenames above.
5. Add attribution to `ATTRIBUTION.txt` (will be created when first CC-licensed sound lands).

## Future SFX (Phase A v2 / Phase D)

These aren't wired up yet; will be added when Phase A polish or Phase D fanfare lands:

- `block_break.ogg` — when an attack breaks through block to bare HP
- `victory_sting.ogg` — short triumphant cue on `bs.over == "victory"`
- `defeat_sting.ogg` — short downbeat cue on `bs.over == "defeat"`
- `card_draw.ogg` — start-of-turn card deal sound (low priority — repetitive)
- `combo_punch.ogg` — Personal Record / multi-hit doubling visual punch
