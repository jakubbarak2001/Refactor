################################################################################
## REFACTOR — Tutorial popups
##
## Onboarding sequence after `car_incident_end` and one-off context popups
## (e.g. affection mechanic on first Martin meeting). Persistent flags gate
## each popup so they never replay across runs.
##
## Public API:
##   tutorial_intro                       — 6-popup main onboarding sequence
##   tutorial_affection_first_seen        — single contextual popup
################################################################################

default persistent.tutorial_seen = False
default persistent.affection_tutorial_seen = False


screen tutorial_popup(title, body, step=None, total=None, accent="#cc2200"):
    modal True
    zorder 900

    ## Dim — heavy enough to focus attention on the popup, light enough that
    ## context behind (e.g. the affection panel for the affection tutorial)
    ## is still visually present. Resolution-agnostic via config.screen_*.
    add Solid("#000000bb") xsize config.screen_width ysize config.screen_height

    frame:
        xalign 0.5
        yalign 0.5
        xsize 720
        padding (40, 32)
        background Frame("#0d0d0dee", 4, 4)

        vbox:
            spacing 16
            xfill True

            ## Step indicator (only when part of a sequence)
            if step is not None and total is not None:
                text "{}/{}".format(step, total):
                    color "#666666"
                    size 12
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

            text title:
                color accent
                size 28
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            ## Accent rule under the title.
            frame:
                xfill True
                ysize 2
                background Frame(accent, 0, 0)

            null height 6

            text body:
                color "#dddddd"
                size 18
                line_spacing 4
                font "fonts/RobotoMono-Regular.ttf"

            null height 12

            ## CTA — bigger, identical wording across the sequence so the
            ## click motion becomes muscle memory.
            textbutton ("Got it →" if step is None or step == total else "Next →"):
                xalign 1.0
                action Return()
                text_color "#ffffff"
                text_hover_color accent
                text_size 18
                text_bold True
                text_font "fonts/RobotoMono-Regular.ttf"
                background Frame("#1a1a1aee", 4, 4)
                hover_background Frame("#2a2a2aee", 4, 4)
                padding (22, 12)


label tutorial_intro:

    ## Replays are blocked by the persistent flag — designed to fire exactly
    ## once per save profile, after the prologue. Flag set BEFORE the popups
    ## so a save mid-sequence (autosave or manual) doesn't replay the whole
    ## intro on reload — the player saw at least step 1.
    if persistent.tutorial_seen:
        return
    $ persistent.tutorial_seen = True

    python:
        _tut_total = 6
        _hcap = hatred_cap()
        _tut_class_label = {
            "bodybuilder": "BODYBUILDER",
            "dark_empath": "DARK EMPATH",
            "biohacker":   "BIOHACKER",
        }.get(stats.player_class, "ROOKIE")
        _tut_class_color = class_accent_color()
        _tut_class_blurb = {
            "bodybuilder": "Hatred is fuel. SOMA stacks each gym session — every 2 stacks = +1 starting block in the Colonel fight. Some menu options are BB-only.",
            "dark_empath": "Profile NPCs to learn them. Deep profiles let you peek further into the Colonel's intent next month.",
            "biohacker":   "Stack compounds. Different protocols unlock different battle perks.",
        }.get(stats.player_class, "Pick a path. Stick to it.")

    call screen tutorial_popup(
        title="YOUR CLASS — [_tut_class_label]",
        body="[_tut_class_blurb]",
        step=1, total=_tut_total, accent=_tut_class_color,
    )

    call screen tutorial_popup(
        title="MONEY",
        body="If you hit 0 CZK before Day 30, the Colonel collects on his loan and the run ends. Watch the gold number.",
        step=2, total=_tut_total, accent="#ffd700",
    )

    call screen tutorial_popup(
        title="CODING",
        body="Your way out. Higher coding = more CZK from gigs and stronger endings. 250 is the ceiling that matters most.",
        step=3, total=_tut_total, accent="#00ccff",
    )

    call screen tutorial_popup(
        title="HATRED",
        body="Hit [_hcap] and you break — that's a loss. The Hatred chip shifts colour as you climb; once it's red, you're close.",
        step=4, total=_tut_total, accent="#ff4444",
    )

    call screen tutorial_popup(
        title="YOUR DECK",
        body="On Day 30 you fight the Colonel with cards, NOT stats. Build the deck. Take cards when offered. The deck button (top of screen) shows what you've got.",
        step=5, total=_tut_total, accent="#00cc88",
    )

    call screen tutorial_popup(
        title="THE 30 DAYS",
        body="One activity per day. Random events between days. Make the move that buys you the most for the trade. There are no reloads.",
        step=6, total=_tut_total, accent="#cc2200",
    )

    return


label tutorial_affection_first_seen:

    ## One-off contextual popup — fires the first time the player encounters
    ## the affection mechanic (Martin meeting). Generic "powerful advantage"
    ## phrasing per design — DO NOT spoil specific card payouts.
    if persistent.affection_tutorial_seen:
        return
    $ persistent.affection_tutorial_seen = True

    call screen tutorial_popup(
        title="AFFECTION",
        body="Martin's trust. Build it through the meeting and he'll give you a powerful advantage against the Colonel. Lose it and you walk away empty-handed.",
        accent="#cc88cc",
    )

    return
