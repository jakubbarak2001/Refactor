################################################################################
## REFACTOR — Coding Mini-Game Screen (Phase 2)
##
## Renders the active puzzle from coding_minigame.rpy state.
## Returns "pass" or "fail" via puzzle_result.
################################################################################

screen coding_puzzle_screen():
    modal True
    zorder 600

    add "#0a0d12"

    python:
        _p = PUZZLES.get(puzzle_id, {})
        _spec = _p.get("spec", "")
        _tests = _p.get("tests", [])
        _reward = _p.get("reward_coding", 0)
        _attempts_left = max(0, puzzle_max_attempts - puzzle_attempts)

    ## ── Header ─────────────────────────────────────────────────────────────
    vbox:
        xalign 0.5
        yalign 0.04
        spacing 6

        text "> CODING PRACTICE — TIER [_p.get('tier', 0)] <":
            xalign 0.5
            color "#00ccff"
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "Solve the spec. Click blocks in order. Wrong order or wrong blocks fails the test.":
            xalign 0.5
            color "#888888"
            size 14
            font "fonts/RobotoMono-Regular.ttf"

    ## ── Spec ───────────────────────────────────────────────────────────────
    frame:
        xalign 0.5
        ypos 130
        xsize 1400
        padding (24, 16)
        background Frame("#0d1018ee", 4, 4)

        vbox:
            spacing 8

            text "SPEC:":
                color "#00ccff"
                size 14
                bold True

            text _spec:
                color "#ffffff"
                size 18
                xmaximum 1352

            null height 4

            text "TESTS:":
                color "#888888"
                size 12

            for _t in _tests:
                text "  ▸ [_t]":
                    color "#aaaaaa"
                    size 13
                    font "fonts/RobotoMono-Regular.ttf"

    ## ── Solution panel ─────────────────────────────────────────────────────
    frame:
        xpos 60
        ypos 320
        xsize 900
        ysize 460
        padding (16, 14)
        background Frame("#0d0d0dee", 4, 4)

        vbox:
            spacing 6

            hbox:
                spacing 10
                text "YOUR SOLUTION":
                    color "#00ff41"
                    size 16
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                text "({} lines)".format(len(puzzle_chosen)):
                    color "#666666"
                    size 13

            text "─────────────────────────────────────────────":
                color "#222222"
                size 11

            null height 4

            if not puzzle_chosen:
                text "(empty — click blocks below to assemble)":
                    color "#444444"
                    size 14
                    italic True

            for _i, _block in enumerate(puzzle_chosen):
                button:
                    xsize 856
                    background Frame("#1a1a1add", 3, 3)
                    hover_background Frame("#2a0000dd", 3, 3)
                    action [Function(puzzle_unpick_block, _block), Function(renpy.restart_interaction)]
                    padding (12, 6)

                    hbox:
                        spacing 12
                        text "{:>2}".format(_i + 1):
                            color "#666666"
                            size 14
                            font "fonts/RobotoMono-Regular.ttf"
                        text _block:
                            color "#ffffff"
                            size 14
                            font "fonts/RobotoMono-Regular.ttf"

    ## ── Block pool ─────────────────────────────────────────────────────────
    frame:
        xpos 980
        ypos 320
        xsize 900
        ysize 460
        padding (16, 14)
        background Frame("#0d0d0dee", 4, 4)

        vbox:
            spacing 6

            hbox:
                spacing 10
                text "AVAILABLE BLOCKS":
                    color "#ffaa44"
                    size 16
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                text "({} remaining)".format(len(puzzle_pool)):
                    color "#666666"
                    size 13

            text "─────────────────────────────────────────────":
                color "#222222"
                size 11

            null height 4

            for _block in puzzle_pool:
                button:
                    xsize 856
                    background Frame("#1f1408dd", 3, 3)
                    hover_background Frame("#3a200add", 3, 3)
                    action [Function(puzzle_pick_block, _block), Function(renpy.restart_interaction)]
                    padding (12, 6)

                    text _block:
                        color "#ffeebb"
                        size 14
                        font "fonts/RobotoMono-Regular.ttf"

    ## ── Footer / controls ──────────────────────────────────────────────────
    hbox:
        xalign 0.5
        ypos 820
        spacing 16

        textbutton "[[ RESET ]":
            action [Function(puzzle_reset), Function(renpy.restart_interaction)]
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 18
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#1a1a1add", 4, 4)
            hover_background Frame("#333333dd", 4, 4)
            padding (20, 10)

        textbutton "[[ SUBMIT ]":
            action [Function(puzzle_submit), Function(renpy.restart_interaction)]
            text_color "#00ff41"
            text_hover_color "#ffffff"
            text_size 22
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#001a00dd", 4, 4)
            hover_background Frame("#003300dd", 4, 4)
            padding (28, 12)
            sensitive (len(puzzle_chosen) > 0)

        textbutton "[[ GIVE UP ]":
            action [SetVariable("puzzle_result", "fail"), Function(renpy.restart_interaction)]
            text_color "#666666"
            text_hover_color "#cc2200"
            text_size 16
            text_font "fonts/RobotoMono-Regular.ttf"
            background "#00000000"
            padding (20, 10)

    ## ── Status line ────────────────────────────────────────────────────────
    text "Attempts left: [_attempts_left]    |    Reward on pass: +[_reward] Coding Skill":
        xalign 0.5
        ypos 900
        color "#888888"
        size 14
        font "fonts/RobotoMono-Regular.ttf"

    ## ── Auto-return when result is set ─────────────────────────────────────
    if puzzle_result is not None:
        timer 0.6 action Return(puzzle_result)
