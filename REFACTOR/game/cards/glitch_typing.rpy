################################################################################
## REFACTOR — Glitch-Phase Typing Minigame (Phase 5.3)
##
## Post-perfect-victory: the colonel loops a scripted rant. Player must type
## the literal `sys.exit()` to break the loop and reach `colonel_glitch_wake_up`.
## Mistyping resets the prompt and increments the attempt counter (which feeds
## the cycling rant flavour). ARGUE / OBSERVE buttons preserve the original
## narrative branches from `colonel_glitch_loop` so nothing is lost.
##
## State lives on a singleton; screen reads via FieldInputValue to capture keys.
################################################################################

default glitch_typing = None

init python:

    GLITCH_TARGET = "sys.exit()"

    GLITCH_RANT_LINES = [
        "'You are a COWARD, JB! You were never fit for this force!'",
        "'You think a laptop and some online course makes you better than us?'",
        "'I gave you a CAREER. I gave you a uniform. And THIS is how you repay me?'",
        "'You will be back in six months. They all come back.'",
        "'Type something, JB. ANYTHING. Defend yourself.'",
        "'You are a COWARD, JB! You were never fit for this force!'",
    ]

    class GlitchTyping(store.object):
        """Singleton state for the sys.exit() typing puzzle."""

        def __init__(self):
            self.typed = ""
            self.attempts = 0
            self.rant_index = 0
            self.done = False
            self.last_wrong = None

        def reset_input(self, wrong_char=None):
            self.typed = ""
            self.attempts += 1
            self.last_wrong = wrong_char
            self.rant_index = (self.rant_index + 1) % len(GLITCH_RANT_LINES)

        def advance_rant(self):
            self.rant_index = (self.rant_index + 1) % len(GLITCH_RANT_LINES)

    def glitch_typing_init():
        """Reset the singleton for a fresh attempt."""
        store.glitch_typing = GlitchTyping()


    def glitch_typing_validate():
        """Called on every interaction. Validates current `typed` against the
        target prefix; resets on mismatch; flags `done` on full match.
        Returns True if the puzzle is solved."""
        gt = glitch_typing
        if gt.done:
            return True
        if gt.typed == GLITCH_TARGET:
            gt.done = True
            return True
        if not GLITCH_TARGET.startswith(gt.typed):
            ## The last character pushed `typed` off the prefix. Capture it
            ## for flavour, then reset.
            gt.reset_input(wrong_char=gt.typed[-1] if gt.typed else None)
        return False


screen glitch_typing_screen():
    modal True
    zorder 600

    add "#000000"

    ## Cycling colonel rant (advances on attempt count + a slow timer)
    python:
        _rant = GLITCH_RANT_LINES[glitch_typing.rant_index % len(GLITCH_RANT_LINES)]
        _solved = glitch_typing_validate()

    ## Slow auto-advance of the rant so it feels alive even without typing
    timer 3.0 repeat True action Function(glitch_typing.advance_rant)

    ## ── Glitched colonel rant (top half) ──────────────────────────────────
    frame:
        xalign 0.5
        ypos 80
        xsize 1500
        padding (28, 22)
        background Frame("#1a0000cc", 6, 6)

        vbox:
            spacing 10
            xalign 0.5

            text "[[COLONEL — runtime: 32 years — looping]":
                xalign 0.5
                color "#ff4422"
                size 16
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            text _rant:
                xalign 0.5
                color "#ffaaaa"
                size 26
                italic True
                font "fonts/RobotoMono-Regular.ttf"
                xmaximum 1440
                text_align 0.5

    ## ── Typing prompt (center) ────────────────────────────────────────────
    frame:
        xalign 0.5
        ypos 360
        xsize 900
        padding (32, 28)
        background Frame("#0a0a0aee", 6, 6)

        vbox:
            spacing 14
            xalign 0.5

            text "TYPE TO STEP OUT OF THE SCRIPT":
                xalign 0.5
                color "#00ff41"
                size 18
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            text "Target: [GLITCH_TARGET!q]":
                xalign 0.5
                color "#666666"
                size 16
                font "fonts/RobotoMono-Regular.ttf"

            null height 6

            ## Display typed-so-far in big monospace, with a blinking caret.
            ## The actual input widget below captures keystrokes.
            text "> [glitch_typing.typed]_":
                xalign 0.5
                color "#00ff41"
                size 44
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            null height 8

            ## Keystroke capture. `allow` filters to characters in sys.exit()
            ## so accidental keys do nothing — but typing the wrong target
            ## character (e.g. 'e' before 'y') still resets via validate().
            input:
                xalign 0.5
                default ""
                value FieldInputValue(glitch_typing, "typed")
                allow "sysexit()."
                length 12
                color "#00000000"            ## invisible — we render typed above
                size 1

    ## ── Wrong-key flavour (only after at least one mistake) ───────────────
    if glitch_typing.attempts > 0 and not _solved:
        text "[[The argument starts again from line 1. The loop only feeds the loop.]":
            xalign 0.5
            ypos 600
            color "#cc4422"
            size 16
            italic True
            font "fonts/RobotoMono-Regular.ttf"

    ## ── Side narrative branches (preserve old menu options) ───────────────
    hbox:
        xalign 0.5
        ypos 760
        spacing 28

        textbutton "[[ ARGUE ]":
            action Return("argue")
            text_color "#cc2200"
            text_hover_color "#ff4422"
            text_size 16
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#1a0000aa", 4, 4)
            hover_background Frame("#330000cc", 4, 4)
            padding (20, 10)

        textbutton "[[ OBSERVE ]":
            action Return("observe")
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 16
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#1a1a1aaa", 4, 4)
            hover_background Frame("#333333cc", 4, 4)
            padding (20, 10)

    ## ── Status footer ─────────────────────────────────────────────────────
    text "Loops weathered: [glitch_typing.attempts]    |    Type each character of sys.exit() in order. Wrong key restarts.":
        xalign 0.5
        ypos 880
        color "#666666"
        size 13
        font "fonts/RobotoMono-Regular.ttf"

    ## ── Auto-return when solved ───────────────────────────────────────────
    if _solved:
        timer 0.6 action Return("wake_up")
