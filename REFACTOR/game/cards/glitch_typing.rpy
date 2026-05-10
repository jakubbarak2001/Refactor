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


## Blinking caret transform — alternates the underscore alpha so it pulses
## like a terminal cursor. Stripped from the static `_` after playtest report.
transform _glitch_caret_blink:
    alpha 1.0
    linear 0.4 alpha 0.1
    linear 0.4 alpha 1.0
    repeat


screen glitch_typing_screen():
    modal True
    zorder 600

    add "#000000"

    python:
        _rant = GLITCH_RANT_LINES[glitch_typing.rant_index % len(GLITCH_RANT_LINES)]
        _solved = glitch_typing_validate()

    timer 3.0 repeat True action Function(glitch_typing.advance_rant)

    ## Looping colonel quote — sits low-alpha behind the prompt so the player
    ## feels the loop without being distracted by it. (Was a full bordered
    ## frame; the playtester said "too much going on".)
    text _rant:
        xalign 0.5
        ypos 140
        color "#552222"
        size 22
        italic True
        font "fonts/RobotoMono-Regular.ttf"
        xmaximum 1440
        text_align 0.5

    ## ── ONE instruction line, the prompt, and a blinking cursor. Nothing else.
    vbox:
        xalign 0.5
        ypos 420
        spacing 24

        text "Type sys.exit() to end this.":
            xalign 0.5
            color "#00ff41"
            size 22
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        ## Prompt + typed + blinking cursor. Rendered as three side-by-side
        ## texts so the cursor can have its own ATL transform without
        ## affecting the typed characters.
        hbox:
            xalign 0.5
            text "> ":
                color "#00ff41"
                size 56
                bold True
                font "fonts/RobotoMono-Regular.ttf"
            text "[glitch_typing.typed]":
                color "#00ff41"
                size 56
                bold True
                font "fonts/RobotoMono-Regular.ttf"
            text "_":
                color "#00ff41"
                size 56
                bold True
                font "fonts/RobotoMono-Regular.ttf"
                at _glitch_caret_blink

        ## Invisible input widget — captures keystrokes; restricted to the
        ## sys.exit() character set so other keys do nothing.
        input:
            xalign 0.5
            default ""
            value FieldInputValue(glitch_typing, "typed")
            allow "sysexit()."
            length 12
            color "#00000000"
            size 1

    if _solved:
        timer 0.6 action Return("wake_up")
