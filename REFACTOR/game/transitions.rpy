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

## ---------------------------------------------------------------------------
## "It's REFACTORING time" — secret-boss title drop. Three stacked copies of
## the line: red + cyan chromatic ghosts jittering in opposite directions, and
## a green main layer that stutter-flickers. Shown as its own beat, dismissed
## on click. Used once, in colonel_ghost_phase.
## ---------------------------------------------------------------------------

transform _rg_red:
    subpixel True
    anchor (0.5, 0.5)
    pos (0.5, 0.43)
    alpha 0.6
    block:
        xoffset 6 yoffset -3
        pause 0.05
        xoffset -8 yoffset 2
        pause 0.04
        xoffset 4 yoffset 4
        pause 0.05
        xoffset -5 yoffset -2
        pause 0.04
        xoffset 7 yoffset 1
        pause 0.05
        repeat

transform _rg_cyan:
    subpixel True
    anchor (0.5, 0.5)
    pos (0.5, 0.43)
    alpha 0.6
    block:
        xoffset -7 yoffset 3
        pause 0.045
        xoffset 7 yoffset -2
        pause 0.05
        xoffset -4 yoffset -4
        pause 0.04
        xoffset 5 yoffset 2
        pause 0.05
        xoffset -6 yoffset -1
        pause 0.045
        repeat

transform _rg_main:
    subpixel True
    anchor (0.5, 0.5)
    pos (0.5, 0.43)
    block:
        zoom 1.0 alpha 1.0 xoffset 0
        pause 0.7
        zoom 1.02 alpha 0.85 xoffset 4
        pause 0.03
        zoom 1.0 alpha 1.0 xoffset -4
        pause 0.03
        zoom 1.0 alpha 1.0 xoffset 0
        pause 0.45
        alpha 0.55
        pause 0.02
        alpha 1.0
        pause 0.55
        repeat

screen refactoring_drop():
    zorder 160
    add "#05070a" alpha 0.82
    text "It's {size=150}{b}REFACTORING{/b}{/size} time" at _rg_red:
        font "fonts/RobotoMono-Regular.ttf"
        size 78
        color "#ff0033"
    text "It's {size=150}{b}REFACTORING{/b}{/size} time" at _rg_cyan:
        font "fonts/RobotoMono-Regular.ttf"
        size 78
        color "#00e5ff"
    text "It's {size=150}{color=#4dff73}{b}REFACTORING{/b}{/color}{/size} time" at _rg_main:
        font "fonts/RobotoMono-Regular.ttf"
        size 78
        color "#eaeaea"
        outlines [ (2, "#04130a", 0, 0) ]


## Arc title card transition — fade in from black
define arc_fade = Dissolve(0.8)

## Plain black filler scene + a gentle fade-up-from-black (used after arc title cards)
image black = Solid("#000000")
define fade_from_black = Dissolve(0.8)
