################################################################################
## REFACTOR — Custom Transitions
################################################################################

## Fast "code compile" flash — used for most scene changes
define compile_flash = MultipleTransition([
    False,     Fade(0.08, 0.0, 0.0, color="#0d0d0d"),
    "#0d0d0d",  Dissolve(0.15),
    True
])

## Slow emotional dissolve — used for heavy emotional moments
define slow_dissolve = Dissolve(1.5)

## Glitch transition — used in Colonel boss fight
## Dark flicker only — no white or red strobes
define glitch_transition = MultipleTransition([
    False,     Fade(0.08, 0.0, 0.0, color="#0d0d0d"),
    "#0d0d0d",  Fade(0.06, 0.0, 0.0, color="#1a0000"),
    "#1a0000",  Fade(0.08, 0.0, 0.0, color="#0d0d0d"),
    "#0d0d0d",  Dissolve(0.25),
    True
])

## Arc title card transition — fade in from black
define arc_fade = Dissolve(0.8)
