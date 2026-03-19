################################################################################
## REFACTOR — Custom Game Screens
## Added at top of screens.rpy (before existing Ren'Py default screens)
################################################################################

## ---------------------------------------------------------------------------
## Stats Bar — displayed during gameplay via "show screen stats_bar"
## ---------------------------------------------------------------------------

screen stats_bar():
    layer "screens"
    zorder 100

    frame:
        xalign 0.0
        yalign 0.0
        xoffset 10
        yoffset 10
        padding (10, 6)
        background Frame("#00000099", 4, 4)

        hbox:
            spacing 20

            ## Class badge — colour-coded per class
            if stats.player_class == "bodybuilder":
                text "[[BODYBUILDER]":
                    color "#ff6633"
                    size 16
                    bold True
            elif stats.player_class == "dark_empath":
                text "[[DARK EMPATH]":
                    color "#9944cc"
                    size 16
                    bold True
            elif stats.player_class == "biohacker":
                text "[[BIOHACKER]":
                    color "#00cc88"
                    size 16
                    bold True
            else:
                text "[[ROOKIE]":
                    color "#888888"
                    size 16
                    bold True

            text "|":
                color "#555555"
                size 18

            text "Money: [stats.available_money] CZK":
                color "#ffd700"
                size 18

            text "|":
                color "#555555"
                size 18

            text "Coding: [stats.coding_skill]":
                color "#00ccff"
                size 18

            text "|":
                color "#555555"
                size 18

            text "Hatred: [stats.pcr_hatred]/100":
                color "#ff4444"
                size 18

            text "|":
                color "#555555"
                size 18

            text "Day: [day_cycle.current_day]/30":
                color "#aaaaaa"
                size 18


## ---------------------------------------------------------------------------
## Outcome Panel — displays stat change summary, like Rich outcome boxes
## Usage: show screen outcome_panel("+ 5000 CZK, -10 PCR HATRED")
##        pause 2.0
##        hide screen outcome_panel
## ---------------------------------------------------------------------------

screen outcome_panel(outcome_text):
    layer "screens"
    zorder 200

    frame:
        xalign 0.5
        yalign 0.85
        padding (20, 12)
        background Frame("#001a00ee", 6, 6)

        vbox:
            spacing 4
            xalign 0.5

            text "OUTCOME":
                color "#00ff41"
                size 16
                bold True
                xalign 0.5

            text "───────────────────────":
                color "#005500"
                size 14
                xalign 0.5

            text "[outcome_text]":
                color "#ffffff"
                size 20
                bold True
                xalign 0.5

            text "▶ click to continue":
                color "#ffffff"
                size 13
                xalign 0.5


## ---------------------------------------------------------------------------
## Achievement Toast — slides in from top-right when an achievement unlocks
## ---------------------------------------------------------------------------

transform achievement_toast_anim:
    ## Start off-screen right, slide in to resting position
    xalign 1.0 yalign 0.0 xoffset 420 yoffset 80
    on show:
        linear 0.35 xoffset -20
    on hide:
        linear 0.3 xoffset 420

screen achievement_toast(ach_name, ach_desc):
    layer "screens"
    zorder 300

    frame at achievement_toast_anim:
        padding (18, 14)
        background Frame("#001a00ff", 4, 4)

        vbox:
            spacing 5
            xmaximum 360

            hbox:
                spacing 10
                text "★":
                    color "#ffdd00"
                    size 18
                text "ACHIEVEMENT UNLOCKED":
                    color "#00ff41"
                    size 14
                    bold True

            text "───────────────────────":
                color "#003300"
                size 12

            text "[ach_name]":
                color "#ffffff"
                size 16
                bold True

            text "[ach_desc]":
                color "#aaaaaa"
                size 13

    timer 4.0 action Hide("achievement_toast")


## ---------------------------------------------------------------------------
## Ending Screen — full-screen cinematic ending display
## Usage: call screen ending_screen("GOOD ENDING", "YOU ESCAPED", ...) then Jump("main_menu")
## ---------------------------------------------------------------------------

screen ending_screen(ending_label, ending_title, ending_flavor, ending_type, score=None, score_note=None, money=None, coding=None, diff_name=None):
    layer "screens"
    modal True

    ## Pre-compute accent color from ending type
    python:
        _ENDING_COLORS = {"perfect": "#ffdd00", "good": "#00ff41", "bittersweet": "#ffaa33", "difficult": "#ff6633", "neutral": "#8899bb", "burnout": "#cc7722", "secret": "#00ccff", "bad": "#cc3322"}
        _ec = _ENDING_COLORS.get(ending_type, "#ffffff")

    add "#000000"

    viewport:
        xfill True
        yfill True
        scrollbars "vertical"
        mousewheel True

        vbox:
            xfill True
            yminimum 1080
            spacing 0

            null height 80

            ## Ending type badge
            frame:
                xalign 0.5
                padding (28, 10)
                background Frame(_ec + "22", 4, 4)
                text "[ending_label]":
                    color _ec
                    size 16
                    bold True
                    xalign 0.5

            null height 24

            ## Main title
            text "[ending_title]":
                color "#ffffff"
                size 52
                bold True
                xalign 0.5
                text_align 0.5

            null height 30

            ## Divider
            text "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━":
                color "#333333"
                size 18
                xalign 0.5

            null height 28

            ## Flavor text
            text "[ending_flavor]":
                color "#cccccc"
                size 19
                xalign 0.5
                text_align 0.5

            ## Stats / Score panel
            if score is not None:

                null height 50

                frame:
                    xalign 0.5
                    xmaximum 700
                    padding (50, 30)
                    background Frame("#0d1a0dee", 6, 6)

                    vbox:
                        spacing 10
                        xalign 0.5

                        text "FINAL STATS":
                            color "#00ff41"
                            size 16
                            bold True
                            xalign 0.5

                        text "──────────────────────────────────":
                            color "#003300"
                            size 13
                            xalign 0.5

                        if money is not None:
                            hbox:
                                xalign 0.5
                                spacing 0
                                xmaximum 500
                                text "Money Saved":
                                    color "#888888"
                                    size 16
                                    xminimum 240
                                text "[money] CZK":
                                    color "#ffffff"
                                    size 16
                                    bold True

                        if coding is not None:
                            hbox:
                                xalign 0.5
                                spacing 0
                                xmaximum 500
                                text "Coding Skill":
                                    color "#888888"
                                    size 16
                                    xminimum 240
                                text "[coding] pts":
                                    color "#00ff41"
                                    size 16
                                    bold True

                        if diff_name is not None:
                            hbox:
                                xalign 0.5
                                spacing 0
                                xmaximum 500
                                text "Difficulty":
                                    color "#888888"
                                    size 16
                                    xminimum 240
                                text "[diff_name]":
                                    color "#ffdd00"
                                    size 16
                                    bold True

                        null height 6

                        text "──────────────────────────────────":
                            color "#003300"
                            size 13
                            xalign 0.5

                        if score_note is not None:
                            text "[score_note]":
                                color "#666666"
                                size 13
                                xalign 0.5

                        null height 4

                        text "FINAL SCORE  [score]":
                            color _ec
                            size 34
                            bold True
                            xalign 0.5

            null height 60

            ## Credits
            text "──────────────────────────────────":
                color "#222222"
                size 13
                xalign 0.5

            null height 16

            text "Thank you for playing":
                color "#aaaaaa"
                size 15
                xalign 0.5

            text "REFACTOR":
                color "#ffffff"
                size 26
                bold True
                xalign 0.5

            null height 6

            text "'Code your way out, or lose your mind trying.'":
                color "#cccccc"
                size 13
                italic True
                xalign 0.5

            text "— Jakub Barák":
                color "#aaaaaa"
                size 12
                xalign 0.5

            null height 50

            ## Return button
            textbutton "[[ RETURN TO MAIN MENU ]":
                xalign 0.5
                action MainMenu()
                text_color _ec
                text_size 18
                text_bold True
                text_hover_color "#ffffff"
                background Frame("#00000000", 0, 0)
                hover_background Frame(_ec + "22", 4, 4)
                padding (30, 14)

            null height 80


## ---------------------------------------------------------------------------
## Affection Panel — used in Martin Meeting to show affection points
## Usage: show screen affection_panel(points, max_points)
## ---------------------------------------------------------------------------

screen affection_panel(points, max_points=12):
    layer "screens"
    zorder 200

    frame:
        xalign 0.5
        yalign 0.85
        padding (20, 12)
        background Frame("#1a001aee", 6, 6)

        vbox:
            spacing 4
            xalign 0.5

            text "AFFECTION POINTS":
                color "#cc66ff"
                size 16
                bold True
                xalign 0.5

            text "───────────────────────":
                color "#440044"
                size 14
                xalign 0.5

            text "[points] / [max_points] POINTS":
                color "#ffffff"
                size 20
                bold True
                xalign 0.5


## ---------------------------------------------------------------------------
## HP Bar Panel — used during the Colonel boss fight
## Usage: show screen hp_bar_panel(jb_hp, colonel_hp, round_name)
## ---------------------------------------------------------------------------

screen hp_bar_panel(jb_hp_val, colonel_hp_val, round_name="Combat"):
    layer "screens"
    zorder 200

    frame:
        xalign 0.5
        yalign 0.05
        padding (20, 12)
        background Frame("#0d0d0dee", 6, 6)
        minimum (400, 0)

        vbox:
            spacing 6
            xalign 0.5

            text "BOSS COMBAT — [round_name]":
                color "#ffffff"
                size 16
                bold True
                xalign 0.5

            text "─────────────────────────────────":
                color "#333333"
                size 14
                xalign 0.5

            hbox:
                spacing 12
                xalign 0.5

                text "JB":
                    color "#00ff41"
                    size 18
                    bold True

                bar:
                    value jb_hp_val
                    range 100
                    xsize 150
                    ysize 20
                    left_bar Frame("#00ff41", 2, 2)
                    right_bar Frame("#1a1a1a", 2, 2)

                text "[jb_hp_val] HP":
                    color "#00ff41"
                    size 16

            hbox:
                spacing 12
                xalign 0.5

                text "COL":
                    color "#ff2222"
                    size 18
                    bold True

                bar:
                    value colonel_hp_val
                    range 100
                    xsize 150
                    ysize 20
                    left_bar Frame("#ff2222", 2, 2)
                    right_bar Frame("#1a1a1a", 2, 2)

                text "[colonel_hp_val] HP":
                    color "#ff2222"
                    size 16


## ---------------------------------------------------------------------------
## Class Selection Screen
## Usage: call screen class_selection_screen
## Returns via SetVariable("stats.player_class", "bodybuilder") etc.
## ---------------------------------------------------------------------------
## ---------------------------------------------------------------------------
## Difficulty Selection Screen — Wolfenstein-style image cards
## ---------------------------------------------------------------------------
## Difficulty data — drives the selection screen and init_game()
## ---------------------------------------------------------------------------

init python:
    DIFF_DATA = [
        {
            "key":     "easy",
            "name":    "JUST LEARN TO CODE BRO",
            "flavor":  "You googled 'how to become a developer in 30 days' and actually believed it.",
            "money":   "55,000",
            "coding":  "10",
            "hatred":  "15",
            "portrait": "diff_easy",
            "color":   "#66cc66",
        },
        {
            "key":     "hard",
            "name":    "TECHNICAL DEBT",
            "flavor":  "You burned half your savings on a course you haven't finished.",
            "money":   "35,000",
            "coding":  "5",
            "hatred":  "25",
            "portrait": "diff_hard",
            "color":   "#ffaa33",
        },
        {
            "key":     "insane",
            "name":    "THANK YOU FOR YOUR APPLICATION",
            "flavor":  "Your CV has a gap. Your wallet has a bigger one.",
            "money":   "20,000",
            "coding":  "0",
            "hatred":  "35",
            "portrait": "diff_insane",
            "color":   "#ff4444",
        },
        {
            "key":     "ultra",
            "name":    "SYSTEM FAILURE",
            "flavor":  "You googled 'what is syntax' and still got it wrong.",
            "money":   "10,000",
            "coding":  "-25",
            "hatred":  "50",
            "portrait": "diff_ultra",
            "color":   "#cc44ff",
        },
    ]

## Portrait swap — fades in whenever a new portrait is shown
transform _diff_portrait_anim:
    on show:
        alpha 0.0
        linear 0.18 alpha 1.0
    alpha 1.0

## ---------------------------------------------------------------------------
## Difficulty Selection Screen — Wolfenstein-style
## Left: vertical list + stats. Right: large portrait that swaps on hover.
## ---------------------------------------------------------------------------

screen difficulty_selection_screen():
    modal True
    zorder 500

    ## Currently focused difficulty (0=easiest, 3=hardest)
    default _hov = 0

    ## ── Background ──────────────────────────────────────────────────────────
    add "#0a0a0a"

    ## Subtle dark red wash on left panel
    frame:
        xpos 0
        ypos 0
        xsize 720
        ysize 1080
        background "#0d000033"

    ## Vertical red separator line
    frame:
        xpos 718
        ypos 0
        xsize 3
        ysize 1080
        background "#cc2200"

    ## ── Title (top-left) ────────────────────────────────────────────────────
    vbox:
        xpos 70
        ypos 72
        spacing 6

        text "HOW HARD DO YOU WANT IT?":
            color "#cc2200"
            size 34
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "Choose your suffering. This cannot be undone.":
            color "#444444"
            size 19
            font "fonts/RobotoMono-Regular.ttf"

    ## ── Difficulty list (left) ──────────────────────────────────────────────

    ## Level 1 — CAN I GOOGLE IT?
    frame:
        xpos 0
        ypos 220
        xsize 718
        ysize 76
        background ("#cc220018" if _hov == 0 else "#00000000")

        hbox:
            yalign 0.5
            ## Left accent bar
            frame:
                xsize 5
                ysize 76
                background ("#cc2200" if _hov == 0 else "#1a0000")
            frame:
                xsize 22
                ysize 76
                background "#00000000"
            text ("▶  " if _hov == 0 else "   "):
                color "#cc2200"
                size 28
                yalign 0.5
                font "fonts/RobotoMono-Regular.ttf"
            textbutton "JUST LEARN TO CODE BRO":
                action [SetField(store, "_chosen_difficulty", "easy"), Return()]
                hovered SetScreenVariable("_hov", 0)
                text_color ("#ffffff" if _hov == 0 else "#555555")
                text_size  (32 if _hov == 0 else 28)
                text_bold  (_hov == 0)
                text_font  "fonts/RobotoMono-Regular.ttf"
                background "#00000000"
                hover_background "#00000000"
                yalign 0.5
                padding (0, 18, 0, 18)

    ## Level 2 — DON'T REJECT MY PR
    frame:
        xpos 0
        ypos 296
        xsize 718
        ysize 76
        background ("#cc220018" if _hov == 1 else "#00000000")

        hbox:
            yalign 0.5
            frame:
                xsize 5
                ysize 76
                background ("#cc2200" if _hov == 1 else "#1a0000")
            frame:
                xsize 22
                ysize 76
                background "#00000000"
            text ("▶  " if _hov == 1 else "   "):
                color "#cc2200"
                size 28
                yalign 0.5
                font "fonts/RobotoMono-Regular.ttf"
            textbutton "TECHNICAL DEBT":
                action [SetField(store, "_chosen_difficulty", "hard"), Return()]
                hovered SetScreenVariable("_hov", 1)
                text_color ("#ffffff" if _hov == 1 else "#555555")
                text_size  (32 if _hov == 1 else 28)
                text_bold  (_hov == 1)
                text_font  "fonts/RobotoMono-Regular.ttf"
                background "#00000000"
                hover_background "#00000000"
                yalign 0.5
                padding (0, 18, 0, 18)

    ## Level 3 — MASS LAYOFFS!
    frame:
        xpos 0
        ypos 372
        xsize 718
        ysize 76
        background ("#cc220018" if _hov == 2 else "#00000000")

        hbox:
            yalign 0.5
            frame:
                xsize 5
                ysize 76
                background ("#cc2200" if _hov == 2 else "#1a0000")
            frame:
                xsize 22
                ysize 76
                background "#00000000"
            text ("▶  " if _hov == 2 else "   "):
                color "#cc2200"
                size 28
                yalign 0.5
                font "fonts/RobotoMono-Regular.ttf"
            textbutton "THANK YOU FOR YOUR APPLICATION":
                action [SetField(store, "_chosen_difficulty", "insane"), Return()]
                hovered SetScreenVariable("_hov", 2)
                text_color ("#ffffff" if _hov == 2 else "#555555")
                text_size  (32 if _hov == 2 else 28)
                text_bold  (_hov == 2)
                text_font  "fonts/RobotoMono-Regular.ttf"
                background "#00000000"
                hover_background "#00000000"
                yalign 0.5
                padding (0, 18, 0, 18)

    ## Level 4 — I AM THE STACK OVERFLOW
    frame:
        xpos 0
        ypos 448
        xsize 718
        ysize 76
        background ("#cc220018" if _hov == 3 else "#00000000")

        hbox:
            yalign 0.5
            frame:
                xsize 5
                ysize 76
                background ("#cc2200" if _hov == 3 else "#1a0000")
            frame:
                xsize 22
                ysize 76
                background "#00000000"
            text ("▶  " if _hov == 3 else "   "):
                color "#cc2200"
                size 28
                yalign 0.5
                font "fonts/RobotoMono-Regular.ttf"
            textbutton "SYSTEM FAILURE":
                action [SetField(store, "_chosen_difficulty", "ultra"), Return()]
                hovered SetScreenVariable("_hov", 3)
                text_color ("#cc44ff" if _hov == 3 else "#555555")
                text_size  (32 if _hov == 3 else 28)
                text_bold  (_hov == 3)
                text_font  "fonts/RobotoMono-Regular.ttf"
                background "#00000000"
                hover_background "#00000000"
                yalign 0.5
                padding (0, 18, 0, 18)

    ## ── Stats block (bottom-left) ───────────────────────────────────────────

    ## Separator
    frame:
        xpos 70
        ypos 580
        xsize 580
        ysize 2
        background "#2a0000"

    vbox:
        xpos 70
        ypos 596
        spacing 8

        ## Stats — monospace gold
        text "Money   [DIFF_DATA[_hov]['money']] CZK":
            color "#C8A44E"
            size 23
            font "fonts/RobotoMono-Regular.ttf"

        text "Coding  [DIFF_DATA[_hov]['coding']]":
            color "#C8A44E"
            size 23
            font "fonts/RobotoMono-Regular.ttf"

        text "Hatred  [DIFF_DATA[_hov]['hatred']]":
            color "#C8A44E"
            size 23
            font "fonts/RobotoMono-Regular.ttf"

        ## Flavor text
        text "\"[DIFF_DATA[_hov]['flavor']]\"":
            color "#666666"
            size 18
            italic True
            font "fonts/RobotoMono-Regular.ttf"
            xmaximum 620

    ## Confirm instruction
    text "— CLICK OR PRESS ENTER TO CONFIRM YOUR FATE —":
        xpos 70
        ypos 970
        color "#551100"
        size 17
        font "fonts/RobotoMono-Regular.ttf"

    ## ── Portrait (right side, centered in right half) ───────────────────────
    ## Swaps with fade on hover. Images are ~420x630.

    ## Red border: outer red frame (2px larger each side) + black mask center
    frame:
        xpos 1048
        ypos 218
        xsize 424
        ysize 634
        background "#cc2200"
    frame:
        xpos 1050
        ypos 220
        xsize 420
        ysize 630
        background "#0a0a0a"

    if _hov == 0:
        add "diff_easy"   at _diff_portrait_anim xpos 1050 ypos 220
    elif _hov == 1:
        add "diff_hard"   at _diff_portrait_anim xpos 1050 ypos 220
    elif _hov == 2:
        add "diff_insane" at _diff_portrait_anim xpos 1050 ypos 220
    elif _hov == 3:
        add "diff_ultra"  at _diff_portrait_anim xpos 1050 ypos 220

    ## ── Keyboard navigation ─────────────────────────────────────────────────
    key "K_UP"       action SetScreenVariable("_hov", max(0, _hov - 1))
    key "K_DOWN"     action SetScreenVariable("_hov", min(3, _hov + 1))
    key "K_RETURN"   action [SetField(store, "_chosen_difficulty", DIFF_DATA[_hov]["key"]), Return()]
    key "K_KP_ENTER" action [SetField(store, "_chosen_difficulty", DIFF_DATA[_hov]["key"]), Return()]


screen class_selection_screen():
    modal True
    zorder 500

    add "#0d0d0d"

    vbox:
        xalign 0.5
        yalign 0.04
        spacing 10

        text "WHO ARE YOU, JB?":
            xalign 0.5
            color "#cc2200"
            size 44
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "Your class shapes your perks, your dialogue, and your destiny.":
            xalign 0.5
            color "#888888"
            size 22
            font "fonts/RobotoMono-Regular.ttf"

    ## Three cards in a row
    hbox:
        xalign 0.5
        yalign 0.52
        spacing 40

        ## --- BODYBUILDER ---
        frame:
            xsize 360
            ysize 480
            background Frame("#1a0800dd", 6, 6)
            padding (20, 18)

            vbox:
                spacing 12

                text "BODYBUILDER":
                    color "#ff6633"
                    size 26
                    bold True
                    xalign 0.5

                text "Iron body. Iron will.\nLimited vocabulary.":
                    color "#ccaa88"
                    size 18
                    xalign 0.5
                    text_align 0.5

                text "──────────────────":
                    color "#442200"
                    size 14
                    xalign 0.5

                text "PERKS:":
                    color "#ff6633"
                    size 16
                    bold True

                text "+ Gym: extra -5 Hatred always":
                    color "#e8e8e8"
                    size 16

                text "+ Bouncer shifts: +1,500 CZK/shift":
                    color "#e8e8e8"
                    size 16

                text "+ Brotherhood guilt never lands":
                    color "#e8e8e8"
                    size 16

                text "+ Brute-force options in key events":
                    color "#e8e8e8"
                    size 16

                text "PASSIVE: -5 Coding Skill at start":
                    color "#ff9966"
                    size 15
                    italic True

                textbutton "SELECT BODYBUILDER":
                    xalign 0.5
                    yalign 1.0
                    action [SetField(stats, "player_class", "bodybuilder"), Return()]
                    text_style "class_select_btn"
                    background "#cc3300"
                    hover_background "#ff5500"
                    padding (16, 10)

        ## --- DARK EMPATH ---
        frame:
            xsize 360
            ysize 480
            background Frame("#0d001add", 6, 6)
            padding (20, 18)

            vbox:
                spacing 12

                text "DARK EMPATH":
                    color "#9944cc"
                    size 26
                    bold True
                    xalign 0.5

                text "You feel everything.\nYou weaponize it.":
                    color "#bb99cc"
                    size 18
                    xalign 0.5
                    text_align 0.5

                text "──────────────────":
                    color "#220044"
                    size 14
                    xalign 0.5

                text "PERKS:":
                    color "#9944cc"
                    size 16
                    bold True

                text "+ Auto +1 Affection per phase":
                    color "#e8e8e8"
                    size 16

                text "+ Colonel dmg halved (2 attacks)":
                    color "#e8e8e8"
                    size 16

                text "+ Fatal Strike on Civilian Void":
                    color "#e8e8e8"
                    size 16

                text "+ Unique reads throughout the game":
                    color "#e8e8e8"
                    size 16

                text "PASSIVE: -10 Hatred start, Cold Read replaces Therapy":
                    color "#cc99ff"
                    size 15
                    italic True

                textbutton "SELECT DARK EMPATH":
                    xalign 0.5
                    yalign 1.0
                    action [SetField(stats, "player_class", "dark_empath"), Return()]
                    text_style "class_select_btn"
                    background "#550088"
                    hover_background "#8800cc"
                    padding (16, 10)

        ## --- BIOHACKER ---
        frame:
            xsize 360
            ysize 480
            background Frame("#00100add", 6, 6)
            padding (20, 18)

            vbox:
                spacing 12

                text "BIOHACKER":
                    color "#00cc88"
                    size 26
                    bold True
                    xalign 0.5

                text "Optimized. Caffeinated.\nSlightly illegal.":
                    color "#88ccaa"
                    size 18
                    xalign 0.5
                    text_align 0.5

                text "──────────────────":
                    color "#004422"
                    size 14
                    xalign 0.5

                text "PERKS:":
                    color "#00cc88"
                    size 16
                    bold True

                text "+ Nootropics Lab (T1-T5 compounds)":
                    color "#e8e8e8"
                    size 16

                text "+ Israeli Dev always max reward":
                    color "#e8e8e8"
                    size 16

                text "+ Fiverr always +25 Coding":
                    color "#e8e8e8"
                    size 16

                text "+ Safety Net auto-countered":
                    color "#e8e8e8"
                    size 16

                text "PASSIVE: +10 Coding start, Bootcamp LOCKED":
                    color "#66ffbb"
                    size 15
                    italic True

                textbutton "SELECT BIOHACKER":
                    xalign 0.5
                    yalign 1.0
                    action [SetField(stats, "player_class", "biohacker"), Return()]
                    text_style "class_select_btn"
                    background "#007744"
                    hover_background "#00aa66"
                    padding (16, 10)


style class_select_btn is button_text:
    color "#ffffff"
    size 16
    bold True


## ---------------------------------------------------------------------------
## Full Stats Screen — detailed breakdown with descriptions
## Usage: call screen full_stats_screen
## ---------------------------------------------------------------------------
screen full_stats_screen():
    modal True
    zorder 400

    add "#0d0d11ee"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 20

        text "> SYSTEM STATUS <":
            xalign 0.5
            color "#cc2200"
            size 36
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        ## Class + Difficulty row
        hbox:
            xalign 0.5
            spacing 30

            if stats.player_class == "bodybuilder":
                text "CLASS: [[BODYBUILDER]]":
                    color "#ff6633"
                    size 20
                    bold True
            elif stats.player_class == "dark_empath":
                text "CLASS: [[DARK EMPATH]]":
                    color "#9944cc"
                    size 20
                    bold True
            elif stats.player_class == "biohacker":
                text "CLASS: [[BIOHACKER]]":
                    color "#00cc88"
                    size 20
                    bold True

            text "|":
                color "#333333"
                size 20

            text "DIFFICULTY: [stats.difficulty.upper() if stats.difficulty else 'UNKNOWN']":
                color "#888888"
                size 20

        ## Stats grid
        frame:
            xalign 0.5
            background Frame("#0d0011cc", 4, 4)
            padding (30, 20)
            xsize 800

            vbox:
                spacing 14

                text "MONEY":
                    color "#ffd700"
                    size 18
                    bold True
                text "[stats.available_money:,] CZK":
                    color "#ffffff"
                    size 22
                    bold True
                text "[stats.stats_description_money()]":
                    color "#aaaaaa"
                    size 16

                text "─────────────────────────────────────────────":
                    color "#222222"
                    size 12

                text "CODING SKILL":
                    color "#00ccff"
                    size 18
                    bold True
                text "[stats.coding_skill] / 250":
                    color "#ffffff"
                    size 22
                    bold True
                text "[stats.stats_description_coding_experience()]":
                    color "#aaaaaa"
                    size 16

                text "─────────────────────────────────────────────":
                    color "#222222"
                    size 12

                text "POLICE HATRED":
                    color "#ff4444"
                    size 18
                    bold True
                text "[stats.pcr_hatred] / 100":
                    color "#ffffff"
                    size 22
                    bold True
                text "[stats.stats_description_police_hatred()]":
                    color "#aaaaaa"
                    size 16

        ## Buffs active
        if stats.ai_paperwork_buff:
            text "[[SELF-AWARE BUFF ACTIVE]] — -5 Hatred per night":
                xalign 0.5
                color "#00ff99"
                size 16

        if stats.daily_btc_income > 0:
            text "[[BTC INCOME]] — [stats.daily_btc_income] CZK per night":
                xalign 0.5
                color "#ffaa00"
                size 16

        textbutton "[[ CLOSE ]":
            xalign 0.5
            action Return()
            text_style "class_select_btn"
            background "#220000"
            hover_background "#440000"
            padding (20, 10)


## ---------------------------------------------------------------------------
## Achievements Screen
## Usage: call screen achievements_screen
## ---------------------------------------------------------------------------
screen achievements_screen():
    modal True
    zorder 400

    add "#0d0d11ee"

    vbox:
        xalign 0.5
        yalign 0.1
        spacing 10

        text "> ACHIEVEMENTS <":
            xalign 0.5
            color "#cc2200"
            size 32
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        python:
            _unlocked = getattr(store, '_achievements_unlocked', set())
            _ach_count = len(_unlocked)
            _ach_total = len(ACHIEVEMENTS)

        text "[_ach_count] / [_ach_total] UNLOCKED":
            xalign 0.5
            color "#888888"
            size 18

        grid 2 7:
            xalign 0.5
            spacing 15

            for _ach_key, _ach_data in ACHIEVEMENTS.items():
                $ _frame_bg = Frame("#1a0011dd", 4, 4) if _ach_key in _unlocked else Frame("#0d0d0ddd", 4, 4)
                frame:
                    xsize 450
                    background _frame_bg
                    padding (14, 10)

                    vbox:
                        spacing 4
                        if _ach_key in _unlocked:
                            text _ach_data["name"]:
                                color "#ffdd00"
                                size 16
                                bold True
                            text _ach_data["desc"]:
                                color "#cccccc"
                                size 14
                        else:
                            text "???":
                                color "#444444"
                                size 16
                                bold True
                            text "Achievement locked.":
                                color "#333333"
                                size 14

        textbutton "[[ CLOSE ]":
            xalign 0.5
            action Return()
            text_style "class_select_btn"
            background "#220000"
            hover_background "#440000"
            padding (20, 10)


## ---------------------------------------------------------------------------
## Arc Title Card
## Usage: call screen arc_title_card("I", "THE INCIDENT")
##        or call screen arc_title_card("II", "THE AWAKENING")
## ---------------------------------------------------------------------------
transform _arc_card_anim:
    alpha 0.0
    linear 0.3 alpha 1.0
    pause 1.6
    linear 0.6 alpha 0.0

screen arc_title_card(arc_number, arc_name):
    modal True
    zorder 500

    add "#0d0d0d"

    vbox:
        xalign 0.5
        yalign 0.45
        spacing 20
        at _arc_card_anim

        text "ARC [arc_number]":
            xalign 0.5
            color "#cc2200"
            size 52
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text arc_name:
            xalign 0.5
            color "#e8e8e8"
            size 72
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "─────────────────────":
            xalign 0.5
            color "#1a2a4a"
            size 36

    timer 2.5 action Return()


## ---------------------------------------------------------------------------
## Alert Screen — red !!! with flash animation, auto-dismisses
## Usage: show screen alert_exclamation then hide after pause
## ---------------------------------------------------------------------------

screen alert_exclamation():
    zorder 200

    hbox:
        xalign 0.85
        yalign 0.18
        spacing 10

        text "!":
            color "#ff0000"
            size 120
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            at _exclaim_flash

        text "!":
            color "#ff0000"
            size 120
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            at _exclaim_flash_delay1

        text "!":
            color "#ff0000"
            size 120
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            at _exclaim_flash_delay2

transform _exclaim_flash:
    alpha 0.0
    linear 0.08 alpha 1.0
    linear 0.08 alpha 0.2
    linear 0.08 alpha 1.0
    linear 0.08 alpha 0.2
    linear 0.08 alpha 1.0

transform _exclaim_flash_delay1:
    alpha 0.0
    pause 0.1
    linear 0.08 alpha 1.0
    linear 0.08 alpha 0.2
    linear 0.08 alpha 1.0
    linear 0.08 alpha 0.2
    linear 0.08 alpha 1.0

transform _exclaim_flash_delay2:
    alpha 0.0
    pause 0.2
    linear 0.08 alpha 1.0
    linear 0.08 alpha 0.2
    linear 0.08 alpha 1.0
    linear 0.08 alpha 0.2
    linear 0.08 alpha 1.0


## ---------------------------------------------------------------------------
## Day Transition Screen
## Usage: call screen day_transition_screen(current_day)
## ---------------------------------------------------------------------------
screen day_transition_screen(day_num):
    modal True
    zorder 500

    add "#0d0d0d"

    vbox:
        xalign 0.5
        yalign 0.45
        spacing 16

        text "> INITIALIZING DAY [day_num] / 30":
            xalign 0.5
            color "#cc2200"
            size 38
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "[ STATUS: ACTIVE ]":
            substitute False
            xalign 0.5
            color "#334455"
            size 24
            font "fonts/RobotoMono-Regular.ttf"

    timer 1.5 action Return()


################################################################################
## Initialization  (original screens.rpy content below)
################################################################################

init offset = -1


################################################################################
## Styles
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## In-game screens
################################################################################


## Say screen ##################################################################
##
## The say screen is used to display dialogue to the player. It takes two
## parameters, who and what, which are the name of the speaking character and
## the text to be displayed, respectively. (The who parameter can be None if no
## name is given.)
##
## This screen must create a text displayable with id "what", as Ren'Py uses
## this to manage text display. It can also create displayables with id "who"
## and id "window" to apply style properties.
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen say(who, what):

    window:
        id "window"
        background Frame("#0d0d1aee", 8, 8)

        vbox:
            spacing 8

            if who is not None:
                window:
                    id "namebox"
                    style "namebox"
                    text who id "who"

            text what id "what"


    ## If there's a side image, display it above the text. Do not display on the
    ## phone variant - there's no room.
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0


## Make the namebox available for styling through the Character object.
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    yminimum 100
    ymaximum 420
    bottom_margin 50

    background Frame("#0d0d1aee", 8, 8)
    padding (60, 30, 60, 30)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")

    xpos gui.dialogue_xpos
    xsize gui.dialogue_width

    adjust_spacing False

## Input screen ################################################################
##
## This screen is used to display renpy.input. The prompt parameter is used to
## pass a text prompt in.
##
## This screen must create an input displayable with id "input" to accept the
## various input parameters.
##
## https://www.renpy.org/doc/html/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xanchor gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width


## Choice screen ###############################################################
##
## This screen is used to display the in-game choices presented by the menu
## statement. The one parameter, items, is a list of objects, each with caption
## and action fields.
##
## https://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 405
    yanchor 0.5
    spacing 22

style choice_button is default:
    properties gui.button_properties("choice_button")
    xminimum 900
    background Frame("#0d0d11ee", 4, 4)
    hover_background Frame("#1a0000ee", 4, 4)
    padding (30, 18)

style choice_button_text is default:
    properties gui.text_properties("choice_button")
    color "#c8c8d8"
    hover_color "#ff4422"
    size 30
    xalign 0.5


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    ## Ensure this appears on top of other screens.
    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"
            style "quick_menu"

            textbutton _("Back") action Rollback()
            textbutton _("History") action ShowMenu('history')
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Save") action ShowMenu('save')
            textbutton _("Q.Save") action QuickSave()
            textbutton _("Q.Load") action QuickLoad()
            textbutton _("Prefs") action ShowMenu('preferences')


## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_menu is hbox
style quick_button is default
style quick_button_text is button_text

style quick_menu:
    xalign 0.5
    yalign 1.0

style quick_button:
    properties gui.button_properties("quick_button")

style quick_button_text:
    properties gui.text_properties("quick_button")


################################################################################
## Main and Game Menu Screens
################################################################################

## Navigation screen ###########################################################
##
## This screen is included in the main and game menus, and provides navigation
## to other menus, and to start the game.

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing gui.navigation_spacing

        if main_menu:

            textbutton _("Start") action Start()

        else:

            textbutton _("History") action ShowMenu("history")

            textbutton _("Save") action ShowMenu("save")

        textbutton _("Load") action ShowMenu("load")

        textbutton _("Preferences") action ShowMenu("preferences")

        if _in_replay:

            textbutton _("End Replay") action EndReplay(confirm=True)

        elif not main_menu:

            textbutton _("Main Menu") action MainMenu()

        textbutton _("About") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

            ## Help isn't necessary or relevant to mobile devices.
            textbutton _("Help") action ShowMenu("help")

        if renpy.variant("pc"):

            ## The quit button is banned on iOS and unnecessary on Android and
            ## Web.
            textbutton _("Quit") action Quit(confirm=not main_menu)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text:
    properties gui.text_properties("navigation_button")


## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## https://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():

    ## This ensures that any other menu screen is replaced.
    tag menu

    add gui.main_menu_background

    ## This empty frame darkens the main menu.
    frame:
        style "main_menu_frame"

    ## The use statement includes another screen inside this one. The actual
    ## contents of the main menu are in the navigation screen.
    use navigation

    if gui.show_name:

        vbox:
            style "main_menu_vbox"

            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"

    text "30 days. One life. No reloads.":
        xalign 0.5
        yalign 0.62
        color "#cc2200"
        size 28
        font "fonts/RobotoMono-Regular.ttf"


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 420
    yfill True

    background "gui/overlay/main_menu.png"

style main_menu_vbox:
    xalign 1.0
    xoffset -30
    xmaximum 1200
    yalign 1.0
    yoffset -30

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")

style main_menu_version:
    properties gui.text_properties("version")


## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid".
## This screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen game_menu(title, scroll=None, yinitial=0.0, spacing=0):

    style_prefix "game_menu"

    if main_menu:
        add gui.main_menu_background
    else:
        add gui.game_menu_background

    frame:
        style "game_menu_outer_frame"

        hbox:

            ## Reserve space for the navigation section.
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        vbox:
                            spacing spacing

                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial yinitial

                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        spacing spacing

                        transclude

                else:

                    transclude

    use navigation

    textbutton _("Return"):
        style "return_button"

        action Return()

    label title

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 45
    top_padding 180

    background "gui/overlay/game_menu.png"

style game_menu_navigation_frame:
    xsize 420
    yfill True

style game_menu_content_frame:
    left_margin 60
    right_margin 30
    top_margin 15

style game_menu_viewport:
    xsize 1380

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 15

style game_menu_label:
    xpos 75
    ysize 180

style game_menu_label_text:
    size 75
    color gui.accent_color
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -45


## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    ## This use statement includes the game_menu screen inside this one. The
    ## vbox child is then included inside the viewport inside the game_menu
    ## screen.
    use game_menu(_("About"), scroll="viewport"):

        style_prefix "about"

        vbox:

            label "[config.name!t]"
            text _("Version [config.version!t]\n")

            ## gui.about is usually set in options.rpy.
            if gui.about:
                text "[gui.about!t]\n"

            text _("Made with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only].\n\n[renpy.license!t]")


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size


## Load and Save screens #######################################################
##
## These screens are responsible for letting the player save the game and load
## it again. Since they share nearly everything in common, both are implemented
## in terms of a third screen, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save https://
## www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("Save"))


screen load():

    tag menu

    use file_slots(_("Load"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))

    use game_menu(title):

        fixed:

            ## This ensures the input will get the enter event before any of the
            ## buttons do.
            order_reverse True

            ## The page name, which can be edited by clicking on a button.
            button:
                style "page_label"

                key_events True
                xalign 0.5
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("empty slot")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## Buttons to access other pages.
            vbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                hbox:
                    xalign 0.5

                    spacing gui.page_spacing

                    textbutton _("<") action FilePagePrevious()
                    key "save_page_prev" action FilePagePrevious()

                    if config.has_autosave:
                        textbutton _("{#auto_page}A") action FilePage("auto")

                    if config.has_quicksave:
                        textbutton _("{#quick_page}Q") action FilePage("quick")

                    ## range(1, 10) gives the numbers from 1 to 9.
                    for page in range(1, 10):
                        textbutton "[page]" action FilePage(page)

                    textbutton _(">") action FilePageNext()
                    key "save_page_next" action FilePageNext()

                if config.has_sync:
                    if CurrentScreenName() == "save":
                        textbutton _("Upload Sync"):
                            action UploadSync()
                            xalign 0.5
                    else:
                        textbutton _("Download Sync"):
                            action DownloadSync()
                            xalign 0.5


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 75
    ypadding 5
    xalign 0.5

style page_label_text:
    textalign 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.text_properties("slot_button")


## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    use game_menu(_("Preferences"), scroll="viewport"):

        vbox:

            hbox:
                box_wrap True

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        label _("Display")
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")

                vbox:
                    style_prefix "check"
                    label _("Skip")
                    textbutton _("Unseen Text") action Preference("skip", "toggle")
                    textbutton _("After Choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

                ## Additional vboxes of type "radio_pref" or "check_pref" can be
                ## added here, to add additional creator-defined preferences.

            null height (4 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True

                vbox:

                    label _("Text Speed")

                    bar value Preference("text speed")

                    label _("Auto-Forward Time")

                    bar value Preference("auto-forward time")

                vbox:

                    if config.has_music:
                        label _("Music Volume")

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        label _("Sound Volume")

                        hbox:
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("Test") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        label _("Voice Volume")

                        hbox:
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("Mute All"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 3

style pref_label_text:
    yalign 1.0

style pref_vbox:
    xsize 338

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.text_properties("radio_button")

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.text_properties("check_button")

style slider_slider:
    xsize 525

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 15

style slider_button_text:
    properties gui.text_properties("slider_button")

style slider_vbox:
    xsize 675


## History screen ##############################################################
##
## This is a screen that displays the dialogue history to the player. While
## there isn't anything special about this screen, it does have to access the
## dialogue history stored in _history_list.
##
## https://www.renpy.org/doc/html/history.html

screen history():

    tag menu

    ## Avoid predicting this screen, as it can be very large.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0, spacing=gui.history_spacing):

        style_prefix "history"

        for h in _history_list:

            window:

                ## This lays things out properly if history_height is None.
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        ## Take the color of the who text from the Character, if
                        ## set.
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("The dialogue history is empty.")


## This determines what tags are allowed to be displayed on the history screen.

define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    textalign gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    textalign gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## Help screen #################################################################
##
## A screen that gives information about key and mouse bindings. It uses other
## screens (keyboard_help, mouse_help, and gamepad_help) to display the actual
## help.

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("Help"), scroll="viewport"):

        style_prefix "help"

        vbox:
            spacing 23

            hbox:

                textbutton _("Keyboard") action SetScreenVariable("device", "keyboard")
                textbutton _("Mouse") action SetScreenVariable("device", "mouse")

                if GamepadExists():
                    textbutton _("Gamepad") action SetScreenVariable("device", "gamepad")

            if device == "keyboard":
                use keyboard_help
            elif device == "mouse":
                use mouse_help
            elif device == "gamepad":
                use gamepad_help


screen keyboard_help():

    hbox:
        label _("Enter")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Space")
        text _("Advances dialogue without selecting choices.")

    hbox:
        label _("Arrow Keys")
        text _("Navigate the interface.")

    hbox:
        label _("Escape")
        text _("Accesses the game menu.")

    hbox:
        label _("Ctrl")
        text _("Skips dialogue while held down.")

    hbox:
        label _("Tab")
        text _("Toggles dialogue skipping.")

    hbox:
        label _("Page Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Page Down")
        text _("Rolls forward to later dialogue.")

    hbox:
        label "H"
        text _("Hides the user interface.")

    hbox:
        label "S"
        text _("Takes a screenshot.")

    hbox:
        label "V"
        text _("Toggles assistive {a=https://www.renpy.org/l/voicing}self-voicing{/a}.")

    hbox:
        label "Shift+A"
        text _("Opens the accessibility menu.")


screen mouse_help():

    hbox:
        label _("Left Click")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Middle Click")
        text _("Hides the user interface.")

    hbox:
        label _("Right Click")
        text _("Accesses the game menu.")

    hbox:
        label _("Mouse Wheel Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Mouse Wheel Down")
        text _("Rolls forward to later dialogue.")


screen gamepad_help():

    hbox:
        label _("Right Trigger\nA/Bottom Button")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Left Trigger\nLeft Shoulder")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Right Shoulder")
        text _("Rolls forward to later dialogue.")

    hbox:
        label _("D-Pad, Sticks")
        text _("Navigate the interface.")

    hbox:
        label _("Start, Guide, B/Right Button")
        text _("Accesses the game menu.")

    hbox:
        label _("Y/Top Button")
        text _("Hides the user interface.")

    textbutton _("Calibrate") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 12

style help_button_text:
    properties gui.text_properties("help_button")

style help_label:
    xsize 375
    right_padding 30

style help_label_text:
    size gui.text_size
    xalign 1.0
    textalign 1.0



################################################################################
## Additional screens
################################################################################


## Confirm screen ##############################################################
##
## The confirm screen is called when Ren'Py wants to ask the player a yes or no
## question.
##
## https://www.renpy.org/doc/html/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 45

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 150

                textbutton _("Yes") action yes_action
                textbutton _("No") action no_action

    ## Right-click and escape answer "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame([ "gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5

style confirm_prompt_text:
    textalign 0.5
    layout "subtitle"

style confirm_button:
    properties gui.button_properties("confirm_button")

style confirm_button_text:
    properties gui.text_properties("confirm_button")


## Skip indicator screen #######################################################
##
## The skip_indicator screen is displayed to indicate that skipping is in
## progress.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 9

            text _("Skipping")

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## This transform is used to blink the arrows one after another.
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## We have to use a font that has the BLACK RIGHT-POINTING SMALL TRIANGLE
    ## glyph in it.
    font "DejaVuSans.ttf"


## Notify screen ###############################################################
##
## The notify screen is used to show the player a message. (For example, when
## the game is quicksaved or a screenshot has been taken.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL screen ##################################################################
##
## This screen is used for NVL-mode dialogue and menus.
##
## https://www.renpy.org/doc/html/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## Displays dialogue in either a vpgrid or the vbox.
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## Displays the menu, if given. The menu may be displayed incorrectly if
        ## config.narrator_menu is set to True.
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


## This controls the maximum number of NVL-mode entries that can be displayed at
## once.
define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    textalign gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    textalign gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    textalign gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.text_properties("nvl_button")


## Bubble screen ###############################################################
##
## The bubble screen is used to display dialogue to the player when using speech
## bubbles. The bubble screen takes the same parameters as the say screen, must
## create a displayable with the id of "what", and can create displayables with
## the "namebox", "who", and "window" ids.
##
## https://www.renpy.org/doc/html/bubble.html#bubble-screen

screen bubble(who, what):
    style_prefix "bubble"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "bubble_namebox"

                text who:
                    id "who"

        text what:
            id "what"

        default ctc = None
        showif ctc:
            add ctc

style bubble_window is empty
style bubble_namebox is empty
style bubble_who is default
style bubble_what is default

style bubble_window:
    xpadding 30
    top_padding 5
    bottom_padding 5

style bubble_namebox:
    xalign 0.5

style bubble_who:
    xalign 0.5
    textalign 0.5
    color "#000"

style bubble_what:
    align (0.5, 0.5)
    text_align 0.5
    layout "subtitle"
    color "#000"

define bubble.frame = Frame("gui/bubble.png", 55, 55, 55, 95)
define bubble.thoughtframe = Frame("gui/thoughtbubble.png", 55, 55, 55, 55)

define bubble.properties = {
    "bottom_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "bottom_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "top_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "top_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "thought" : {
        "window_background" : bubble.thoughtframe,
    }
}

define bubble.expand_area = {
    "bottom_left" : (0, 0, 0, 22),
    "bottom_right" : (0, 0, 0, 22),
    "top_left" : (0, 22, 0, 0),
    "top_right" : (0, 22, 0, 0),
    "thought" : (0, 0, 0, 0),
}



################################################################################
## Mobile Variants
################################################################################

style pref_vbox:
    variant "medium"
    xsize 675

## Since a mouse may not be present, we replace the quick menu with a version
## that uses fewer and bigger buttons that are easier to touch.
screen quick_menu():
    variant "touch"

    zorder 100

    if quick_menu:

        hbox:
            style "quick_menu"
            style_prefix "quick"

            textbutton _("Back") action Rollback()
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Menu") action ShowMenu()


style window:
    variant "small"
    background "gui/phone/textbox.png"

style radio_button:
    variant "small"
    foreground "gui/phone/button/radio_[prefix_]foreground.png"

style check_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 510

style game_menu_content_frame:
    variant "small"
    top_margin 0

style game_menu_viewport:
    variant "small"
    xsize 1305

style pref_vbox:
    variant "small"
    xsize 600

style bar:
    variant "small"
    ysize gui.bar_size
    left_bar Frame("gui/phone/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/phone/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    variant "small"
    xsize gui.bar_size
    top_bar Frame("gui/phone/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/phone/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    variant "small"
    ysize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    variant "small"
    xsize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    variant "small"
    ysize gui.slider_size
    base_bar Frame("gui/phone/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/horizontal_[prefix_]thumb.png"

style vslider:
    variant "small"
    xsize gui.slider_size
    base_bar Frame("gui/phone/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/vertical_[prefix_]thumb.png"

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 900
