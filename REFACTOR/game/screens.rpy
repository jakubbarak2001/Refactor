################################################################################
## REFACTOR — Custom Game Screens
## Added at top of screens.rpy (before existing Ren'Py default screens)
################################################################################

## ---------------------------------------------------------------------------
## Class-color frame — thin top + bottom border bars in the player's class
## color. Used to frame full-screen modals (battle / deck / card-offer) so the
## class identity reads through.
## ---------------------------------------------------------------------------

## ---------------------------------------------------------------------------
## Dossier design tokens — shared by the main menu chrome, the prologue HUD
## strips, and the prologue say-window restyle. Treat as the single source
## of truth for the "case-file" aesthetic so future surfaces (daily menu,
## events, choice) can opt in without re-hardcoding colors / fonts.
## ---------------------------------------------------------------------------
define DOSSIER_FONT      = "fonts/RobotoMono-Regular.ttf"
define DOSSIER_BG_BAR    = "#0a0a0acc"
## Say-window backing — alpha 0xaa (~67%) lets the BG character art
## bleed through behind the dialogue. Dialogue text still reads cleanly
## via its default outline.
define DOSSIER_BG_SOLID  = "#0a0a0aaa"
define DOSSIER_INK       = "#c0d0e0"
define DOSSIER_INK_DIM   = "#667788"
define DOSSIER_RED       = "#cc2200"
define DOSSIER_GLYPH     = "►"

## Beat metadata strings shown in the top dossier_hud strip (and only
## while that strip is on-screen). Defaulted empty so the strip's
## right-side text simply doesn't render outside of opted-in labels.
default dossier_beat_time = ""
default dossier_beat_slug = ""

init python:
    def set_dossier_beat(time_str, slug):
        store.dossier_beat_time = time_str
        store.dossier_beat_slug = slug


screen class_color_frame(thickness=3, alpha_suffix=""):
    $ _ccf_color = class_accent_color() + alpha_suffix
    frame:
        xpos 0
        ypos 0
        xsize config.screen_width
        ysize thickness
        background Frame(_ccf_color, 0, 0)
    frame:
        xpos 0
        ypos (config.screen_height - thickness)
        xsize config.screen_width
        ysize thickness
        background Frame(_ccf_color, 0, 0)


## ---------------------------------------------------------------------------
## Stats Bar — displayed during gameplay via "show screen stats_bar"
## ---------------------------------------------------------------------------

## Dossier HUD strip — the always-on top band. Three zones (class identity |
## day countdown + 4-day strip | resource gauges), bracketed by class-color
## hairlines. Folds the former separate day_calendar screen into the center
## zone so the player reads one HUD, not two stacked widgets.
screen stats_bar():
    layer "screens"
    zorder 100

    python:
        ## ── Class identity ────────────────────────────────────────────────
        _class_track = ""
        _class_color = class_accent_color()
        if stats.player_class == "bodybuilder":
            _soma = getattr(store, 'bb_soma', 0)
            if _soma > 0:
                _class_track = "SOMA {}/10".format(_soma)
        elif stats.player_class == "dark_empath":
            _profs = getattr(store, 'de_profiles', {})
            _deep = sum(1 for n, c in _profs.items() if c >= 3)
            _total = sum(_profs.values()) if _profs else 0
            if _total > 0:
                _class_track = "PROFILES {} ({} deep)".format(_total, _deep)
        elif stats.player_class == "biohacker":
            _proto = getattr(store, 'bh_protocol', None)
            if _proto:
                _class_track = "STACK {}".format(_proto)

        ## Coding tier (1-5) — surfaced next to the raw skill so the player can
        ## read the live value every coding-scaled card refers to. The cap is
        ## shown too (X/cap) so the ceiling is never a surprise.
        _coding_tier = _coding_tier_int()
        _coding_cap = stats.coding_ceiling()

        ## ── Tooltips (threshold-gated) ────────────────────────────────────
        _coding_tt = None
        _hatred_tt = None
        if stats.coding_skill < 70 and stats.available_money < 25000:
            _coding_tt = "Low coding + low cash = forced back to the uniform. Build one or both fast."
        elif stats.coding_skill < 70:
            _coding_tt = "Coding is your way out. Higher = more cash from gigs and stronger endings."
        if stats.pcr_hatred >= 60:
            _hatred_tt = "Stay below {}. High hatred = breakdown ending.".format(hatred_cap())

        _deck_count_bar = len(player_deck.cards) if player_deck is not None else 0

        ## ── Run HP — persists across ladder + Colonel ────────────────────
        _run_hp_show = getattr(store, 'run_hp', None)
        _run_hp_max_show = getattr(store, 'run_hp_max', None)
        if _run_hp_show is None or _run_hp_max_show is None:
            _run_hp_max_show = class_max_hp(include_gym_bonus=False) if stats else 90
            _run_hp_show = _run_hp_max_show
        _hp_ratio = (_run_hp_show / float(_run_hp_max_show)) if _run_hp_max_show > 0 else 1.0
        if _hp_ratio >= 0.75:
            _hp_color = "#88ff88"
        elif _hp_ratio >= 0.5:
            _hp_color = "#ffdd44"
        elif _hp_ratio >= 0.25:
            _hp_color = "#ff8844"
        else:
            _hp_color = "#ff4444"
        _hp_tt = "Your body. Carries between fights. +5/night, +8 gym, +15 heavy gym. Hospital after a loss costs HP. 0 HP mid-fight = forced detour."

        ## ── Hatred — bar color ramps by severity ─────────────────────────
        _hatred_cap = hatred_cap()
        _hatred_ratio = min(1.0, stats.pcr_hatred / float(_hatred_cap))
        if _hatred_ratio < 0.3:
            _hatred_bar_color = "#88ff88"
        elif _hatred_ratio < 0.6:
            _hatred_bar_color = "#ffdd44"
        elif _hatred_ratio < 0.9:
            _hatred_bar_color = "#ff8844"
        else:
            _hatred_bar_color = "#ff4444"

        ## ── Day countdown + 4-day strip (folded in from day_calendar) ────
        _today = day_cycle.current_day if day_cycle is not None else 1
        _events = get_key_event_days()
        _colonel_day = stats.colonel_day if stats is not None else 30
        _days_to_colonel = max(0, _colonel_day - _today)
        _strip_end = min(_today + 3, 30)
        _strip_days = list(range(_today, _strip_end + 1))

        _money_str = "{:,} CZK".format(stats.available_money)
        _day_subhead = "day {:02d} / 30".format(_today)

    vbox:
        ypos 0
        xalign 0.5

        ## ▔▔▔ Top class-color hairline ▔▔▔
        frame:
            xfill True
            ysize 2
            background Frame(_class_color, 0, 0)

        ## ═══ Main strip — full-bleed band, content centered. A floating
        ## content-sized box read as a widget; a full-width band reads as
        ## the game's chrome. ═══
        frame:
            xfill True
            padding (24, 8)
            background Frame(DOSSIER_BG_BAR, 0, 0)

            hbox:
                xalign 0.5
                spacing 18
                yalign 0.5

                ## ── LEFT ZONE — class identity ────────────────────────────
                frame:
                    yalign 0.5
                    background None
                    padding (0, 0)

                    hbox:
                        spacing 12
                        yalign 0.5

                        frame:
                            xsize 14
                            ysize 14
                            yalign 0.5
                            background Frame(_class_color, 0, 0)

                        vbox:
                            spacing 2
                            yalign 0.5

                            if stats.player_class == "bodybuilder":
                                button:
                                    action NullAction()
                                    tooltip "Greek for body. Every rep is one more piece of you that takes up space in the room. The right amount means the Colonel still has to look at you across the desk."
                                    background None
                                    padding (0, 0)
                                    text "[[BODYBUILDER]":
                                        color _class_color
                                        size 16
                                        bold True
                                        font DOSSIER_FONT
                            elif stats.player_class == "dark_empath":
                                button:
                                    action NullAction()
                                    tooltip "A working theory of someone, built from small things they don't know they're showing you. The deeper the profile, the more predictable they get. You used to do this for suspects. Now you do it for everyone."
                                    background None
                                    padding (0, 0)
                                    text "[[DARK EMPATH]":
                                        color _class_color
                                        size 16
                                        bold True
                                        font DOSSIER_FONT
                            elif stats.player_class == "biohacker":
                                button:
                                    action NullAction()
                                    tooltip "The clinical word for the stack — exact compound, exact dose, exact timing. Started with caffeine. The right one buys you a turn the others don't get."
                                    background None
                                    padding (0, 0)
                                    text "[[BIOHACKER]":
                                        color _class_color
                                        size 16
                                        bold True
                                        font DOSSIER_FONT
                            else:
                                text "[[ROOKIE]":
                                    color _class_color
                                    size 16
                                    bold True
                                    font DOSSIER_FONT

                            if _class_track:
                                text _class_track:
                                    color _class_color
                                    size 11
                                    italic True
                                    font DOSSIER_FONT

                ## ── Divider ───────────────────────────────────────────────
                add Solid("#333333") xysize (1, 44) yalign 0.5

                ## ── CENTER ZONE — day headline (left) + 4-day strip ───────
                hbox:
                    spacing 12
                    yalign 0.5

                    vbox:
                        yalign 0.5
                        spacing 1

                        if _days_to_colonel > 0:
                            text _day_subhead:
                                color "#f5f0e0"
                                size 19
                                bold True
                                font DOSSIER_FONT
                        else:
                            text "{stshl=TODAY} · CONFRONTATION":
                                color "#f5f0e0"
                                size 19
                                bold True
                                font DOSSIER_FONT

                    hbox:
                        spacing 4
                        yalign 0.5

                        for _d in _strip_days:
                            $ _is_today = (_d == _today)
                            $ _ev       = _events.get(_d)

                            if _is_today:
                                $ _cell_bg   = _class_color
                                $ _cell_text = "#ffffff"
                            elif _ev is not None:
                                $ _cell_bg   = _ev[1]
                                $ _cell_text = "#ffffff"
                            else:
                                $ _cell_bg   = "#222222"
                                $ _cell_text = "#aaaaaa"

                            ## Use a `fixed` so the cell frame itself
                            ## yalign-centers in the strip — same vertical
                            ## anchor as "day 01 / 30" and the resource
                            ## gauges. The ▼ TODAY marker floats above the
                            ## cell as a positioned overlay so it doesn't
                            ## inflate the cell's visual height (the prior
                            ## vbox layout pushed the calendar ~10px below
                            ## every other zone element).
                            fixed:
                                xysize (66, 30)
                                yalign 0.5

                                frame:
                                    xfill True
                                    yfill True
                                    background Frame(_cell_bg, 3, 3)

                                    vbox:
                                        xalign 0.5
                                        yalign 0.5
                                        spacing 0

                                        text "DAY [_d]":
                                            color _cell_text
                                            size 11
                                            bold _is_today
                                            xalign 0.5
                                            font DOSSIER_FONT

                                        if _ev is not None:
                                            text "[_ev[0]]":
                                                color _cell_text
                                                size 9
                                                xalign 0.5
                                                font DOSSIER_FONT

                                if _is_today:
                                    text "▼":
                                        color _class_color
                                        size 10
                                        bold True
                                        xalign 0.5
                                        ypos -12

                ## ── Divider ───────────────────────────────────────────────
                add Solid("#333333") xysize (1, 44) yalign 0.5

                ## ── RIGHT ZONE — resource gauges ──────────────────────────
                frame:
                    yalign 0.5
                    background None
                    padding (0, 0)

                    hbox:
                        spacing 14
                        yalign 0.5
                        xalign 1.0

                        ## Money — gold; no bar (no cap to gauge against).
                        text _money_str:
                            color "#ffd700"
                            size 20
                            bold True
                            yalign 0.5
                            font DOSSIER_FONT

                        add Solid("#333333") xysize (1, 36) yalign 0.5

                        ## HP — number + 4px progress bar.
                        vbox:
                            spacing 3
                            yalign 0.5

                            button:
                                action NullAction()
                                tooltip _hp_tt
                                background None
                                padding (0, 0)
                                text "HP [_run_hp_show]/[_run_hp_max_show]":
                                    color _hp_color
                                    size 16
                                    bold True
                                    font DOSSIER_FONT

                            frame:
                                xsize 120
                                ysize 4
                                background Frame("#1a1a1a", 0, 0)
                                padding (0, 0)
                                add Solid(_hp_color) xysize (int(120 * _hp_ratio), 4)

                        add Solid("#333333") xysize (1, 36) yalign 0.5

                        ## Hatred — number + 4px progress bar.
                        vbox:
                            spacing 3
                            yalign 0.5

                            if _hatred_tt:
                                button:
                                    action NullAction()
                                    tooltip _hatred_tt
                                    background None
                                    padding (0, 0)
                                    text "Hatred [stats.pcr_hatred]/[_hatred_cap]":
                                        color "#ff4444"
                                        size 16
                                        bold True
                                        font DOSSIER_FONT
                            else:
                                text "Hatred [stats.pcr_hatred]/[_hatred_cap]":
                                    color "#ff4444"
                                    size 16
                                    bold True
                                    font DOSSIER_FONT

                            frame:
                                xsize 120
                                ysize 4
                                background Frame("#1a1a1a", 0, 0)
                                padding (0, 0)
                                add Solid(_hatred_bar_color) xysize (int(120 * _hatred_ratio), 4)

                        add Solid("#333333") xysize (1, 36) yalign 0.5

                        ## Coding — open-ended; no bar.
                        if _coding_tt:
                            button:
                                action NullAction()
                                tooltip _coding_tt
                                background None
                                padding (0, 0)
                                yalign 0.5
                                text "Coding [stats.coding_skill]/[_coding_cap] · T[_coding_tier]":
                                    color "#00ccff"
                                    size 15
                                    font DOSSIER_FONT
                        else:
                            text "Coding [stats.coding_skill]/[_coding_cap] · T[_coding_tier]":
                                color "#00ccff"
                                size 15
                                yalign 0.5
                                font DOSSIER_FONT

                        add Solid("#333333") xysize (1, 36) yalign 0.5

                        ## Deck — overlay, not Call(label). Strip is always-on,
                        ## so a pure Show()/Hide() pair around the deck viewer
                        ## keeps script flow intact (Call returned out of
                        ## daily_menu and dumped the player to main menu).
                        textbutton "Deck · [_deck_count_bar]":
                            yalign 0.5
                            action Show("deck_viewer")
                            tooltip "Click to view your deck."
                            text_color "#00cc88"
                            text_hover_color "#ffffff"
                            text_size 15
                            text_bold True
                            text_font DOSSIER_FONT
                            background None
                            hover_background None
                            padding (0, 0)

        ## ▁▁▁ Bottom class-color hairline ▁▁▁
        frame:
            xfill True
            ysize 2
            background Frame(_class_color, 0, 0)

    ## ── Tooltip relay — anchored below the strip (~120px tall). ────────
    $ _stats_tt = GetTooltip()
    if _stats_tt:
        frame:
            xalign 0.5
            ypos 86
            padding (12, 8)
            background Frame("#0d1018ee", 4, 4)
            text "[_stats_tt]":
                color "#cccccc"
                size 14
                xalign 0.5
                xmaximum 800
                text_align 0.5
                font DOSSIER_FONT


## ---------------------------------------------------------------------------
## Deck Viewer — shows the player's accumulated card collection
## Usage: call screen deck_viewer
## ---------------------------------------------------------------------------

screen deck_viewer():
    modal True
    zorder 400

    ## Hovered card + its content-space slot origin — drives the anchored
    ## hover-inspect overlay (same pattern as fixer_removal_screen). Tuple is
    ## (cid, slot_x, slot_y, col); the adjustment tracks the grid's vertical
    ## scroll so the anchor stays glued while scrolled.
    default _dv_hover = None
    default _dv_yadj  = ui.adjustment()

    add "#0d0d11ee"

    python:
        ## Group cards by visual type — Attack / Skill / Power / Curse / Status.
        ## Order is `CARD_VISUAL_TYPES` so clean kit reads top-of-screen and
        ## corruption is anchored at the bottom (Curse/Status).
        _deck_cards = player_deck.cards if player_deck is not None else []
        _deck_count = len(_deck_cards)
        _deck_by_group = {}
        for _cid in _deck_cards:
            _c = CARD_LIBRARY.get(_cid)
            if _c is None:
                continue
            _grp_key = card_visual_type(_c)
            _deck_by_group.setdefault(_grp_key, []).append(_cid)

    ## Class-color outer frame — "this is YOUR deck" without overriding per-card colors.
    use class_color_frame(thickness=3, alpha_suffix="aa")

    ## Header — FIXED position (not centered-flow) so the grid below sits at
    ## known coordinates: the hover-inspect overlay anchors to the hovered
    ## card's slot, which needs deterministic grid geometry (fixer pattern).
    vbox:
        xalign 0.5
        ypos 24
        spacing 10

        text "> YOUR DECK <":
            xalign 0.5
            color "#cc2200"
            size 36
            bold True
            font "fonts/RobotoMono-Regular.ttf"
        text "[_deck_count] CARDS COLLECTED":
            xalign 0.5
            color "#888888"
            size 18

        ## Owned relics — gear strip under the deck header. Hover a chip for
        ## its name + effect (tooltip consumer below).
        if owned_relics():
            hbox:
                xalign 0.5
                spacing 10
                use relic_tray(size=40)
            $ _deck_relic_tt = GetTooltip()
            if _deck_relic_tt:
                text "[_deck_relic_tt]":
                    xalign 0.5
                    color "#cdbd97"
                    size 15
                    font "fonts/RobotoMono-Regular.ttf"

    ## Grid geometry constants — shared by the layout below AND the overlay
    ## anchor math. Slot stride = card (220/320) + gutter (16/28); group
    ## headers take a FIXED height so the content-space y cursor stays exact.
    python:
        _DV_VX, _DV_VY = 160, 210     ## viewport screen position
        _DV_PAD        = 36           ## inner padding (gem overhang room)
        _DV_SX, _DV_SY = 236, 348     ## slot stride x/y
        _DV_HDR_H      = 30           ## group-header band height

    ## ── Grid layout ───────────────────────────────────────────────────────
    ## Six cards per row at hand-mode size (220×316) via the canonical
    ## battle_card_view renderer. Hover a card for the full-size inspect
    ## overlay, same as the fixer. The padded frame gives the cost gems
    ## (which overhang each card's top-left) room inside the viewport's
    ## clip area. Viewport fits 6×220 + 5×16 = 1400 wide with margin.
    viewport:
        xpos _DV_VX
        ypos _DV_VY
        xsize 1600
        ysize 720
        yadjustment _dv_yadj
        scrollbars "vertical"
        mousewheel True
        draggable True

        frame:
            background None
            padding (_DV_PAD, _DV_PAD)
            vbox:
                spacing 24

                ## Content-space y cursor — advanced group by group below so
                ## every card's slot origin is exact for the overlay anchor.
                $ _dv_y = _DV_PAD

                for _grp in CARD_VISUAL_TYPES:
                    if _deck_by_group.get(_grp):
                        $ _grp_hex = TYPE_PALETTE.get(_grp, {}).get("frame", "#888888")
                        $ _grp_cards = _deck_by_group[_grp]

                        ## Group header — type label, color-coded, with count.
                        ## Color bar to the left of the label gives the
                        ## header weight and matches the card frames below.
                        hbox:
                            spacing 12
                            ysize _DV_HDR_H
                            frame:
                                ysize 22
                                xsize 8
                                yalign 0.5
                                background Frame(_grp_hex, 0, 0)
                            text "{} ({})".format(_grp.upper(), len(_grp_cards)):
                                yalign 0.5
                                color _grp_hex
                                size 22
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"
                                outlines [(1, "#000000", 0, 0)]

                        ## Rows begin under the header + one vbox gap.
                        $ _dv_y += _DV_HDR_H + 24
                        $ _rows = [_grp_cards[i:i+6] for i in range(0, len(_grp_cards), 6)]
                        vbox:
                            spacing 28
                            for _ri, _row in enumerate(_rows):
                                hbox:
                                    spacing 16
                                    for _ci, _cid in enumerate(_row):
                                        $ _slot_x = _DV_PAD + _ci * _DV_SX
                                        $ _slot_y = _dv_y + _ri * _DV_SY
                                        fixed:
                                            xysize (220, 320)
                                            ## Hover-tracking button — no
                                            ## click action; the viewer is
                                            ## read-only.
                                            button:
                                                xsize 220
                                                ysize 316
                                                background None
                                                hover_background None
                                                action NullAction()
                                                hovered SetScreenVariable("_dv_hover", (_cid, _slot_x, _slot_y, _ci))
                                                unhovered SetScreenVariable("_dv_hover", None)
                                                at fixer_card_nudge
                                                use battle_card_view(cid=_cid, mode="hand", playable=True)

                        ## Advance the cursor past this group's rows + gap.
                        $ _dv_y += len(_rows) * _DV_SY - 28 + 24

                if not _deck_cards:
                    text "Your deck is empty.\nDo activities, attend events, or talk to Martin to collect cards.":
                        color "#666666"
                        size 16
                        italic True
                        xalign 0.5
                        text_align 0.5

    textbutton "[[ CLOSE ]":
        xalign 0.5
        ypos 950
        ## Hide self — the Dossier HUD strip (zorder 100) renders above
        ## this modal anyway, so no other layer needs restoring. No
        ## Return() — Return is what triggered the "back to main menu"
        ## bug when called outside a label.
        action Hide("deck_viewer")
        text_style "class_select_btn"
        background "#220000"
        hover_background "#440000"
        padding (20, 10)

    ## Hover-inspect overlay — the full-size card, drawn after (= on top of)
    ## the grid so it's never clipped by the viewport or occluded by the
    ## neighbouring cards. Anchored to the hovered card's slot, flipping to
    ## the upper-left for the rightmost columns so it never runs offscreen.
    ## Vertical position is clamped to the screen and tracks the scroll.
    if _dv_hover:
        python:
            _dv_slot_x = _DV_VX + _dv_hover[1]
            _dv_slot_y = _DV_VY + _dv_hover[2] - int(_dv_yadj.value)
            _dv_ins_x = (_dv_slot_x - 414) if _dv_hover[3] >= 4 else (_dv_slot_x + 234)
            _dv_ins_y = max(16, min(_dv_slot_y - 200, 1080 - 588))
        fixed:
            xpos _dv_ins_x
            ypos _dv_ins_y
            xysize (400, 572)
            at inspect_overlay_in
            use battle_card_view(cid=_dv_hover[0], mode="inspect", playable=True)


## ---------------------------------------------------------------------------
## Activity stat-chip palette. Costs always negative (-), gains always positive
## (+), per-stat color so the eye doesn't have to parse +/- math. Used by the
## activity tile helper below; pass chips=[("CZK", -400), ("Hatred", -10), ...]
## via the `effect_chips` parameter.
## ---------------------------------------------------------------------------

init python:
    _ACT_CHIP_COLORS = {
        "CZK":     "#ffd700",
        "Hatred":  "#ff4444",
        "Coding":  "#00ccff",
        "Muscle":  "#ff6633",
        "Card":    "#00cc88",
        "Upgrade": "#ffd700",
        "sep":     "#666666",
        "?":       "#888888",
    }

    def _act_chip_label(stat, delta):
        """Format a chip label. delta=None renders as '?' (volatile / variable).
        delta as a string is treated as a literal label (stat field still drives chip color)."""
        if isinstance(delta, str):
            return delta
        if delta is None:
            return "? {}".format(stat)
        sign = "+" if delta >= 0 else "-"
        if stat == "CZK":
            return "{}{:,} {}".format(sign, abs(delta), stat) if delta != 0 else "0 {}".format(stat)
        if delta == 0:
            return "0 {}".format(stat)
        return "{}{} {}".format(sign, abs(delta), stat)


screen _activity_chip_row(chips):
    ## Render a horizontal row of colored stat-change chips. Each chip is a
    ## small pill: color from the stat, label "+N STAT" or "-N STAT".
    ## `_stat == "sep"` renders a plain text divider (no pill frame) — used to
    ## visually break a chip row into an "A / B" choice.
    hbox:
        spacing 4
        xalign 0.5
        for _stat, _delta in chips:
            ## Volatile / random outcomes render in neutral grey via the "?"
            ## palette entry — visually distinguishes "guaranteed +X" chips
            ## from "depends on the day" chips at a glance.
            $ _chip_color = _ACT_CHIP_COLORS.get("?" if _delta is None else _stat, "#cccccc")
            if _stat == "sep":
                text _act_chip_label(_stat, _delta):
                    color _chip_color
                    size 18
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                    yalign 0.5
            else:
                frame:
                    padding (9, 4)
                    background Frame("#1a1a1aee", 3, 3)
                    text _act_chip_label(_stat, _delta):
                        color _chip_color
                        size 16
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"


## ---------------------------------------------------------------------------
## Activity Tile — reusable button used in the activity selector grid.
## Calls a label on click. Renders title + cost + effect + flavor.
##
## Two effect-display modes:
##   1. effect_chips (preferred) — list of (stat, delta) tuples, rendered as
##      colored chip row. Use for new tiles and migrated top-level tiles.
##   2. effect_text (legacy) — freeform string with "Reward:" prefix. Kept
##      for sub-menus that haven't migrated yet.
## ---------------------------------------------------------------------------

## Activity-tile hover lift — gentle pop when the cursor lands on a tile.
## yoffset ONLY, deliberately no zoom: a zoomed child reports its scaled
## size back to the parent hbox, which re-flows the whole row — the old
## 1.04 zoom made every neighbouring tile shift and bounce on hover.
transform activity_hover_lift:
    on hover:
        ease 0.15 yoffset -10
    on idle, insensitive:
        ease 0.15 yoffset 0

## Hero-tile art hover — zoom + brighten INSIDE the tile's clipping viewport
## (same pattern as the class/difficulty columns), so the motion never
## leaks into layout or neighbouring tiles.
transform _acttile_art_hover:
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    zoom 1.0
    matrixcolor BrightnessMatrix(0.0)
    on hover:
        ease 0.20 zoom 1.07 matrixcolor BrightnessMatrix(0.07)
    on idle, insensitive:
        ease 0.20 zoom 1.0 matrixcolor BrightnessMatrix(0.0)

## Default glyph per activity title — keeps the icon zone meaningful without
## requiring every call site to pass an art_glyph. Falls through to ★.
## Glyphs restricted to the safe set RobotoMono actually renders (verified
## against its cmap) — emoji and dingbats like 🏋/❋/☏/☾/✂ render as tofu/'?'.
default _ACT_DEFAULT_GLYPHS = {
    "GYM": "≡",
    "COLD READ": "◊",
    "RECOVERY": "+",
    "BOUNCER": "$",
    "CODING": "</>",
    "OVERTIME": "◐",
    "PHONE": "@",
    "SLEEP": "~",
    "REST": "~",
    "VISIT FIXER": "×",
}

screen _activity_tile(label_name, title, accent, cost_text, effect_text="", effect_chips=None, locked=False, lock_text="", class_relevant=False, flavor_text="", art_glyph="", cost_unaffordable=False, stat_lines=None, art=None, art_xoff=0, tile_w=340, tile_h=320):
    ## Two render modes off one screen:
    ##   art != None  → HERO tile: full-bleed illustration on top (clipped
    ##                  hover-zoom), title plate + text zone under it. Used by
    ##                  the top-level PICK TODAY'S MOVE row.
    ##   art == None  → classic glyph tile (submenus). Same frame language.
    ## The OUTER fixed pins the layout footprint — hover motion (yoffset on
    ## the button, zoom inside the art viewport) can never re-flow the row.
    ## Hover feedback: border brightens (hover_background) + art zooms.
    python:
        if locked:
            _at_title_color   = "#554434"
            _at_glyph_color   = "#3a3a3a"
            _at_border_color  = "#3a2020"
        elif class_relevant:
            _at_title_color   = "#e8c878"
            _at_glyph_color   = accent
            _at_border_color  = accent
        else:
            _at_title_color   = "#e8e0d0"
            _at_glyph_color   = accent
            _at_border_color  = accent
        _at_glyph = art_glyph or _ACT_DEFAULT_GLYPHS.get(title, "◆")
        ## Cost line color — red preempts the click when funds are short.
        if locked:
            _at_cost_color = "#3a3a3a"
        elif cost_unaffordable:
            _at_cost_color = "#ff4444"
        else:
            _at_cost_color = "#ffd700"
        _at_inner_w = tile_w - 6
        ## Art zone: everything above the title plate (44) + text zone (130).
        _at_art_h   = max(0, tile_h - 6 - 44 - 130)

    fixed:
        xysize (tile_w, tile_h)

        button:
            xysize (tile_w, tile_h)
            ## The 3px periphery around the inner panel IS the border — the
            ## hover swap lights it up in the accent without moving a pixel.
            background Frame(Solid(_at_border_color + ("44" if locked else "77")), 0, 0)
            hover_background Frame(Solid(accent), 0, 0)
            padding (3, 3)
            sensitive (not locked)
            action Jump(label_name)
            at activity_hover_lift

            fixed:
                add Solid("#14100c")

                vbox:
                    xsize _at_inner_w

                    if art:
                        ## ART — full-bleed, clipped; zooms + brightens on
                        ## hover via _acttile_art_hover. Locked art reads as
                        ## a grey ghost.
                        viewport:
                            xysize (_at_inner_w, _at_art_h)
                            fixed:
                                at _acttile_art_hover
                                ## art_xoff pans the cover-cropped image inside
                                ## the clipping viewport (negative = slide the
                                ## picture left) so the subject can be framed
                                ## per-tile without touching the source file.
                                add art:
                                    xoffset art_xoff
                                    xysize (_at_inner_w, _at_art_h)
                                    fit "cover"
                                    matrixcolor (SaturationMatrix(0.15) * BrightnessMatrix(-0.25) if locked else IdentityMatrix())
                    else:
                        ## GLYPH ZONE — accent-tinted backdrop, large symbol.
                        frame:
                            xfill True
                            ysize max(64, _at_art_h)
                            background Frame(accent + "22", 4, 4)
                            text _at_glyph:
                                xalign 0.5
                                yalign 0.5
                                size 38
                                color _at_glyph_color
                                bold True
                                outlines [(2, "#000000", 0, 0)]

                    ## TITLE PLATE — sits between art and text zone.
                    frame:
                        xfill True
                        ysize 44
                        background Frame("#0a0806", 0, 0)
                        text title:
                            color _at_title_color
                            size 22
                            bold True
                            xalign 0.5
                            yalign 0.5
                            xmaximum (_at_inner_w - 20)
                            text_align 0.5
                            font "fonts/RobotoMono-Regular.ttf"

                    ## TITLE UNDERLINE — 2px hairline on every tile: gold for
                    ## the class-relevant one, the tile's own accent otherwise.
                    if not locked:
                        frame:
                            xfill True
                            ysize 2
                            background Frame(("#e8c878" if class_relevant else accent), 0, 0)

                    ## TEXT ZONE — cost (only when it costs something; FREE
                    ## carries no info), then lock note / stat lines / flavor.
                    frame:
                        xfill True
                        yfill True
                        background None
                        padding (14, 10)
                        vbox:
                            xfill True
                            spacing 5

                            if cost_text and cost_text != "FREE":
                                text cost_text:
                                    color _at_cost_color
                                    size 16
                                    bold True
                                    xalign 0.5
                                    font "fonts/RobotoMono-Regular.ttf"

                            if locked and lock_text:
                                text lock_text:
                                    color "#554434"
                                    size 12
                                    italic True
                                    xalign 0.5
                                    text_align 0.5
                                    xmaximum (_at_inner_w - 28)
                            elif stat_lines:
                                for _sl_label, _sl_value in stat_lines:
                                    python:
                                        _sl_sign = _sl_value[0] if _sl_value else ""
                                        if _sl_label == "BATTLE BONUS":
                                            _sl_color = "#ffd700"
                                        elif _sl_value in ("", "—"):
                                            _sl_color = "#777777"
                                        elif _sl_label == "HP":
                                            _sl_color = "#55dd66" if _sl_sign == "+" else ("#dd5544" if _sl_sign == "-" else "#cccccc")
                                        elif _sl_label == "HATRED":
                                            _sl_color = "#55dd66" if _sl_sign == "-" else ("#dd5544" if _sl_sign == "+" else "#cccccc")
                                        else:
                                            _sl_color = "#cccccc"
                                    hbox:
                                        xfill True
                                        spacing 6
                                        text _sl_label:
                                            color "#888070"
                                            size 12
                                            bold True
                                            font "fonts/RobotoMono-Regular.ttf"
                                            xsize 110
                                        text _sl_value:
                                            color _sl_color
                                            size 13
                                            bold True
                                            font "fonts/RobotoMono-Regular.ttf"
                                            xalign 1.0
                            elif flavor_text:
                                text flavor_text:
                                    color "#aaa090"
                                    size 14
                                    italic True
                                    xalign 0.5
                                    text_align 0.5
                                    xmaximum (_at_inner_w - 28)
                                    line_spacing 2


## ---------------------------------------------------------------------------
## Activity Sub-Menu - generic card-grid screen for sub-choices inside an
## activity (e.g. CODING's CODE FOR MONEY / PRACTICE / COACH / BOOTCAMP).
## Mirrors the top-level activity_select_screen visual language so the
## hierarchy reads consistently.
##
## options is a list of dicts. Each option supports:
##   label_name      - Jump target on click (required)
##   title           - bold title (required)
##   accent          - accent color hex (defaults to neutral if omitted)
##   cost_text       - top line - cost or FREE
##   effect_text     - "Reward: <delta>" line
##   flavor_text     - italic mood line (omitted when empty)
##   class_relevant  - bool - glow in the option's accent color
##   locked          - bool - gray out, click disabled
##   lock_text       - italic note shown in place of flavor when locked
## back_label is the Jump target for the floating BACK button.
## ---------------------------------------------------------------------------

screen activity_submenu(title, options, subtitle="", back_label="daily_menu"):
    modal True
    zorder 50

    add "#0a0a0acc"

    ## Title, subtitle, and tile grid live in a single vbox so the subtitle
    ## can't overlap the cards. Up to 5 visible options lay out as ONE row of
    ## hero tiles (same visual language as PICK TODAY'S MOVE — art on top via
    ## the option's "art" key, glyph fallback otherwise); 6+ falls back to a
    ## compact 3-wide grid of the classic glyph tiles.
    python:
        _opts_visible = [o for o in options if o.get("visible", True)]
        _sub_hero  = (len(_opts_visible) <= 5)
        _per_row   = len(_opts_visible) if _sub_hero else 3
        _rows      = [_opts_visible[i:i + _per_row] for i in range(0, len(_opts_visible), _per_row)]
        _sub_tw    = 340
        _sub_th    = 560 if _sub_hero else 320

    vbox:
        xalign 0.5
        ypos 110
        spacing 22

        text title:
            xalign 0.5
            color "#e8c878"
            size 48
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(3, "#000000", 0, 0)]

        if subtitle:
            text subtitle:
                xalign 0.5
                color "#888888"
                size 14
                italic True
                xmaximum 1200
                text_align 0.5
                font "fonts/RobotoMono-Regular.ttf"

        null height 14

        vbox:
            xalign 0.5
            spacing 28

            for _row in _rows:
                hbox:
                    spacing 22
                    xalign 0.5

                    for _opt in _row:
                        use _activity_tile(
                            label_name        = _opt.get("label_name", back_label),
                            title             = _opt.get("title", "?"),
                            accent            = _opt.get("accent", "#cccccc"),
                            cost_text         = _opt.get("cost_text", ""),
                            cost_unaffordable = _opt.get("cost_unaffordable", False),
                            effect_text       = _opt.get("effect_text", ""),
                            locked            = _opt.get("locked", False),
                            lock_text         = _opt.get("lock_text", ""),
                            class_relevant    = _opt.get("class_relevant", False),
                            flavor_text       = _opt.get("flavor_text", ""),
                            art_glyph         = _opt.get("art_glyph", ""),
                            stat_lines        = _opt.get("stat_lines", None),
                            art               = (_opt.get("art") if _sub_hero else None),
                            art_xoff          = _opt.get("art_xoff", 0),
                            tile_w            = _sub_tw,
                            tile_h            = _sub_th,
                        )

    ## Floating BACK button - same spot as the parent screen for muscle memory.
    textbutton "[[ ← BACK ]":
        xpos 60
        yalign 0.93
        action Jump(back_label)
        text_color "#888888"
        text_hover_color "#ffffff"
        text_size 18
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        background Frame("#0d0d0dee", 3, 3)
        hover_background Frame("#1a1a1aee", 3, 3)
        padding (18, 10)


## ---------------------------------------------------------------------------
## Hatred intro popup — fires once per run the first time PCR Hatred crosses
## 40 (the first Rage-injection threshold). State the mechanic, click to
## dismiss. Gated by store._hatred_intro_shown so it never fires twice.
## ---------------------------------------------------------------------------

screen hatred_intro_popup():
    modal True
    zorder 800

    add "#000000aa"

    $ _hatred_collapse_cap = hatred_cap()
    $ _hp_pc = stats.player_class if stats else None

    frame:
        xalign 0.5
        yalign 0.5
        xsize 680
        background Frame("#0d0d11ee", 4, 4)
        padding (32, 24)

        vbox:
            spacing 12

            text "PCR HATRED":
                color "#ff4422"
                size 28
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            frame:
                xfill True
                ysize 2
                background Frame("#cc2200", 0, 0)

            text "The job's corruption clock. Bad events raise it. Relief activities drop it.":
                color "#cccccc"
                size 16
                xmaximum 620
                font "fonts/RobotoMono-Regular.ttf"

            ## Class-specific corruption description. BB carries it in the
            ## deck (Rage cards). BH carries it chemically (dependency in
            ## the nootropic stack). DE carries it relationally (profiles
            ## go cold). Only BB sees the Rage-card warning.
            if _hp_pc == "bodybuilder":
                text "At 40 / 60 / 80 — a Rage card is forced into your deck. Deals damage at a cost.":
                    color "#cccccc"
                    size 16
                    xmaximum 620
                    font "fonts/RobotoMono-Regular.ttf"
            elif _hp_pc == "biohacker":
                text "The body keeps the score. Recovery and a clean stack walk it back.":
                    color "#cccccc"
                    size 16
                    xmaximum 620
                    font "fonts/RobotoMono-Regular.ttf"
            else:
                text "Burn it off where you can. The number doesn't reset on its own.":
                    color "#cccccc"
                    size 16
                    xmaximum 620
                    font "fonts/RobotoMono-Regular.ttf"

            text "At [_hatred_collapse_cap] — collapse. The run ends.":
                color "#ff6655"
                size 16
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            null height 6

            textbutton "GOT IT":
                xalign 0.5
                action Return()
                text_color "#ffdd44"
                text_hover_color "#ffffff"
                text_size 18
                text_bold True
                text_font "fonts/RobotoMono-Regular.ttf"
                background Frame("#1a1410", 3, 3)
                hover_background Frame("#332b00ee", 3, 3)
                padding (24, 8)


screen activity_select_screen():
    modal True
    zorder 50

    add "#0a0a0acc"

    python:
        _pc = stats.player_class if stats else None
        _is_bb = (_pc == "bodybuilder")
        _is_de = (_pc == "dark_empath")
        _is_bh = (_pc == "biohacker")

    vbox:
        xalign 0.5
        ypos 130
        spacing 6

        text "PICK TODAY'S MOVE":
            xalign 0.5
            color "#e8c878"
            size 52
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(3, "#000000", 0, 0)]

        text "One activity per day. Choose carefully.":
            xalign 0.5
            color "#888888"
            size 15
            italic True
            font "fonts/RobotoMono-Regular.ttf"

    ## Tile row — hero art tiles. Slot 1 is the class-locked relief activity
    ## (only that class sees that tile). Slots 2-4 are universal. When the
    ## Fixer is in town a fifth tile joins on the right — free time, so it
    ## belongs on the board but reads as a side door, not a daily move.
    python:
        _act_today      = day_cycle.current_day if day_cycle is not None else 1
        _act_fixer_here = fixer_visits_today(_act_today)
        _act_fixer_done = bool(getattr(store, '_fixer_shredded_today', False))
        ## Repeat-penalty footers — red "(-X% · nth day in a row)" on the
        ## tiles whose payout bleeds on consecutive days (gym + bouncer).
        _act_gym_warn = activity_repeat_tile_warn("gym", "relief")
        _act_bnc_warn = activity_repeat_tile_warn("bouncer", "pay")

    hbox:
        xalign 0.5
        ypos 248
        spacing 22

        ## Slot 1 - CLASS-LOCKED relief activity. Each class sees only their own.
        if _is_bb:
            use _activity_tile(
                label_name        = "activity_gym",
                title             = "GYM",
                accent            = class_accent_color("bodybuilder"),
                cost_text         = "FREE",
                flavor_text       = "An hour where the bar tells the truth." + _act_gym_warn,
                class_relevant    = True,
                art               = "images/pictures/act_gym.png",
                art_xoff          = -140,
                tile_w            = 340,
                tile_h            = 560,
            )
        elif _is_de:
            use _activity_tile(
                label_name     = "activity_cold_read",
                title          = "COLD READ",
                accent         = class_accent_color("dark_empath"),
                cost_text      = "FREE",
                flavor_text    = "Regular for the card. Deep for the profile.",
                class_relevant = True,
                tile_w         = 340,
                tile_h         = 560,
            )
        elif _is_bh:
            use _activity_tile(
                label_name     = "activity_recovery",
                title          = "RECOVERY",
                accent         = class_accent_color("biohacker"),
                cost_text      = "FREE",
                flavor_text    = "Sauna, meditation, cold plunge, red light — today the body picks.",
                class_relevant = True,
                art            = "images/pictures/act_recovery.png",
                tile_w         = 340,
                tile_h         = 560,
            )

        ## Slot 2 - money/stack lane. BH gets the NOOTROPICS LAB tile (was a
        ## submenu of CODING; promoted to top-level since it's the BH signature
        ## activity). Other classes keep BOUNCER as their money path.
        if _is_bh:
            use _activity_tile(
                label_name     = "activity_nootropics",
                title          = "NOOTROPICS LAB",
                accent         = class_accent_color("biohacker"),
                cost_text      = "VARIES",
                flavor_text    = "Three tiers + Research PubMed. Build the stack, build the deck.",
                class_relevant = True,
                art            = "images/pictures/act_nootropics.png",
                tile_w         = 340,
                tile_h         = 560,
            )
        else:
            use _activity_tile(
                label_name     = "activity_bouncer",
                title          = "BOUNCER",
                accent         = "#ffd700",
                cost_text      = "FREE",
                flavor_text    = "Moonlighting pays well, but it's dangerous for cops." + _act_bnc_warn,
                art            = "images/pictures/act_bouncer.png",
                art_xoff       = -80,
                tile_w         = 340,
                tile_h         = 560,
            )

        ## CODING - everyone needs to learn the trade.
        use _activity_tile(
            label_name     = "activity_coding",
            title          = "CODING",
            accent         = "#00ccff",
            cost_text      = "FREE",
            flavor_text    = "Study sessions. The keyboard pays in cards.",
            art            = "images/pictures/act_coding.png",
            art_xoff       = -60,
            tile_w         = 340,
            tile_h         = 560,
        )

        ## OVERTIME - shared money + hatred trade.
        use _activity_tile(
            label_name     = "activity_overtime",
            title          = "OVERTIME",
            accent         = "#3388cc",
            cost_text      = "FREE",
            flavor_text    = "Trade time for money.",
            art            = "images/pictures/act_overtime.png",
            tile_w         = 340,
            tile_h         = 560,
        )

        ## THE FIXER — free time, no daily slot. Only when he's in town.
        if _act_fixer_here:
            use _activity_tile(
                label_name = "activity_fixer",
                title      = "THE FIXER",
                accent     = "#c08050",
                cost_text  = "FREE",
                flavor_text = ("He's done for the day." if _act_fixer_done else "Cards, gear, the shredder. Cash only."),
                locked     = _act_fixer_done,
                lock_text  = "He's done for the day.",
                art        = "images/backgrounds/bg_fixer_shop.jpg",
                art_xoff   = -150,
                tile_w     = 340,
                tile_h     = 560,
            )

    ## Floating BACK button - bottom-left, deliberately separate from the
    ## activity grid so it reads as navigation, not a tile.
    textbutton "[[ ← BACK ]":
        xpos 60
        yalign 0.93
        action Jump("daily_menu")
        text_color "#888888"
        text_hover_color "#ffffff"
        text_size 18
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        background Frame("#0d0d0dee", 3, 3)
        hover_background Frame("#1a1a1aee", 3, 3)
        padding (18, 10)


## ---------------------------------------------------------------------------
## Daily Hub — central morning ritual. PICK YOUR MOVE is the dominant CTA.
## Sidebar holds only the context-gated PHONE button. END DAY is a small
## "Skip Today" link, only visible when no activity has been chosen.
## ---------------------------------------------------------------------------

## WHEY-tub hover flourish: arrow darts in from the left and keeps nudging;
## "GYM" fades in just behind it.
transform _whey_arrow_in:
    xoffset -26 alpha 0.0
    easeout 0.16 xoffset 0 alpha 1.0
    block:
        easein 0.45 xoffset 5
        easeout 0.45 xoffset 0
        repeat

transform _whey_gym_in:
    alpha 0.0 xoffset -6
    pause 0.10
    easeout 0.20 alpha 1.0 xoffset 0

## TODAY marquee hover lift — small pop on the CTA, smaller than the
## activity-tile lift so the hub doesn't feel jumpy on idle hover.
transform _today_cta_lift:
    on hover:
        ease 0.18 zoom 1.04 yoffset -6
    on idle:
        ease 0.18 zoom 1.0 yoffset 0

## TODAY marquee entry fade — the panel rises into focus on each daily reset.
transform _today_panel_in:
    alpha 0.0 yoffset 20
    easeout 0.55 alpha 1.0 yoffset 0

screen daily_hub_screen():
    modal True
    zorder 50

    python:
        _today        = day_cycle.current_day if day_cycle is not None else 1
        _hub_class_color = class_accent_color()
        ## Dossier tag — case-file stamp used by the lock-in state's footer.
        _dossier_tag        = "JBKZ-{:02d}".format(_today)
        _dossier_tag_closed = _dossier_tag + " · CLOSED"

        if stats and stats.player_class == "bodybuilder":
            _hub_cta_word  = "TRAIN"
            _hub_cta_color = _hub_class_color
            _hub_cta_hover = "#ff8855"
        elif stats and stats.player_class == "dark_empath":
            _hub_cta_word  = "STUDY"
            _hub_cta_color = _hub_class_color
            _hub_cta_hover = "#bb66dd"
        elif stats and stats.player_class == "biohacker":
            _hub_cta_word  = "STACK"
            _hub_cta_color = _hub_class_color
            _hub_cta_hover = "#55ee88"
        else:
            _hub_cta_word  = "PICK YOUR MOVE"
            _hub_cta_color = "#cc2200"
            _hub_cta_hover = "#ff4422"

    ## (No hub-level FIXER widget — when the Fixer is in town his tile joins
    ## the PICK TODAY'S MOVE board instead; the hub stays clean.)

    ## ── BB only: the WHEY tub on the counter is a clickable shortcut to the gym ──
    default whey_hover = False
    if not activity_selected and stats and stats.player_class == "bodybuilder":
        button:
            xpos 1525
            ypos 424
            xysize (122, 172)
            background None
            hover_background "#ffae5530"
            action Jump("activity_gym")
            hovered SetScreenVariable("whey_hover", True)
            unhovered SetScreenVariable("whey_hover", False)
        if whey_hover:
            hbox:
                xpos 1586
                xanchor 0.5
                ypos 600
                spacing 5
                text "→":
                    at _whey_arrow_in
                    yoffset -2
                    size 19
                    bold True
                    color "#ffae55"
                    outlines [(2, "#000000cc", 0, 0)]
                    font "fonts/RobotoMono-Regular.ttf"
                text "GYM":
                    at _whey_gym_in
                    size 17
                    bold True
                    color "#ffae55"
                    outlines [(2, "#000000cc", 0, 0)]
                    font "fonts/RobotoMono-Regular.ttf"

    ## ── Center stage — the dominant action ──────────────────────────────────
    ## Banner pattern (class-color hairline → dark plate → hairline) mirrors
    ## the Dossier HUD strip's signature so the day's centerpiece reads as
    ## part of the same case-file aesthetic.
    if not activity_selected:
        vbox:
            xalign 0.5
            yalign 0.58
            xsize 760
            spacing 0
            at _today_panel_in

            ## Top class-color hairline
            frame:
                xfill True
                ysize 2
                background Frame(_hub_class_color, 0, 0)

            frame:
                xfill True
                padding (60, 28)
                background Frame(DOSSIER_BG_SOLID, 0, 0)

                vbox:
                    spacing 10
                    xalign 0.5

                    text "DAY [_today] / 30":
                        color _hub_class_color
                        size 14
                        bold True
                        xalign 0.5
                        font DOSSIER_FONT

                    textbutton _hub_cta_word:
                        xalign 0.5
                        action Jump("select_activity")
                        text_color _hub_cta_color
                        text_hover_color _hub_cta_hover
                        text_size 64
                        text_bold True
                        text_font DOSSIER_FONT
                        text_outlines [(3, "#000000", 0, 0)]
                        background "#00000000"
                        hover_background "#00000000"
                        padding (12, 6)
                        at _today_cta_lift

            ## Bottom class-color hairline
            frame:
                xfill True
                ysize 2
                background Frame(_hub_class_color, 0, 0)

    else:
        ## Lock-in state — class-coloured, same banner pattern as pick state
        ## so the only thing that changes is the message itself.
        vbox:
            xalign 0.5
            yalign 0.58
            xsize 760
            spacing 0
            at _today_panel_in

            frame:
                xfill True
                ysize 2
                background Frame(_hub_class_color, 0, 0)

            frame:
                xfill True
                padding (60, 28)
                background Frame(DOSSIER_BG_SOLID, 0, 0)

                vbox:
                    spacing 10
                    xalign 0.5

                    text "DAY [_today] / 30":
                        color _hub_class_color
                        size 14
                        bold True
                        xalign 0.5
                        font DOSSIER_FONT

                    text "MOVE COMPLETE":
                        color _hub_cta_color
                        size 40
                        bold True
                        xalign 0.5
                        font DOSSIER_FONT
                        outlines [(3, "#000000", 0, 0)]

                    text "Sleep on it.":
                        color "#a0a0a0"
                        size 17
                        italic True
                        xalign 0.5
                        font DOSSIER_FONT

                    null height 2

                    text "[DOSSIER_GLYPH] DOSSIER · [_dossier_tag_closed]":
                        color DOSSIER_INK_DIM
                        size 11
                        xalign 0.5
                        font DOSSIER_FONT

            frame:
                xfill True
                ysize 2
                background Frame(_hub_class_color, 0, 0)


## ---------------------------------------------------------------------------
## (day_calendar removed — its content lives in the Dossier HUD strip's
## center zone now. Phone screen still has the full 30-day grid.)
## ---------------------------------------------------------------------------


## ---------------------------------------------------------------------------
## Phone Screen — full 30-day overview + recent notifications. Reachable
## from the hub PHONE button (when notifications are pending). Modal.
## ---------------------------------------------------------------------------

screen phone_screen():
    modal True
    zorder 350
    tag phone

    add "#0a0a0aee"

    python:
        _phone_today = day_cycle.current_day if day_cycle is not None else 1
        _phone_events = get_key_event_days()
        _phone_colonel_day = stats.colonel_day if stats is not None else 30
        _phone_days_left = max(0, _phone_colonel_day - _phone_today)
        _phone_msgs_view = list(getattr(store, '_phone_notifications', []))

    vbox:
        xalign 0.5
        yalign 0.04
        spacing 6

        text "> PHONE <":
            xalign 0.5
            color "#cc2200"
            size 36
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "DAY [_phone_today] / 30":
            xalign 0.5
            color "#888888"
            size 16
            font "fonts/RobotoMono-Regular.ttf"

    ## ── Notifications panel ─────────────────────────────────────────────────
    frame:
        xalign 0.5
        yalign 0.18
        xsize 1200
        padding (24, 18)
        background Frame("#0d0d0dee", 4, 4)

        vbox:
            spacing 8
            xalign 0.5

            text "NOTIFICATIONS":
                color "#ffd700"
                size 16
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            text "─────────────────":
                color "#222222"
                size 11

            if _phone_msgs_view:
                for _msg in _phone_msgs_view:
                    text _msg:
                        color "#cccccc"
                        size 14
                        font "fonts/RobotoMono-Regular.ttf"
            else:
                text "No new notifications.":
                    color "#666666"
                    size 14
                    italic True
                    font "fonts/RobotoMono-Regular.ttf"

    ## ── Full 30-day calendar ────────────────────────────────────────────────
    frame:
        xalign 0.5
        yalign 0.46
        padding (24, 18)
        background Frame("#0d0d0dee", 4, 4)

        vbox:
            spacing 10
            xalign 0.5

            text "CALENDAR":
                xalign 0.5
                color "#cc2200"
                size 16
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            hbox:
                spacing 2
                xalign 0.5

                for _d in range(1, 31):
                    $ _is_today_p = (_d == _phone_today)
                    $ _is_past_p  = (_d < _phone_today)
                    $ _ev_p       = _phone_events.get(_d)

                    if _is_today_p:
                        $ _cell_bg_p   = "#cc2200"
                        $ _cell_text_p = "#ffffff"
                    elif _ev_p is not None:
                        $ _cell_bg_p   = _ev_p[1]
                        $ _cell_text_p = "#ffffff" if not _is_past_p else "#666666"
                    elif _is_past_p:
                        $ _cell_bg_p   = "#1a1a1a"
                        $ _cell_text_p = "#444444"
                    else:
                        $ _cell_bg_p   = "#222222"
                        $ _cell_text_p = "#888888"

                    frame:
                        xsize 42
                        ysize 40
                        background Frame(_cell_bg_p, 2, 2)

                        vbox:
                            xalign 0.5
                            yalign 0.5
                            text "[_d]":
                                color _cell_text_p
                                size 13
                                bold _is_today_p
                                xalign 0.5
                                font "fonts/RobotoMono-Regular.ttf"

            python:
                _upcoming_p = [(_d, _ev) for _d, _ev in sorted(_phone_events.items()) if _d >= _phone_today]

            if _upcoming_p:
                hbox:
                    spacing 18
                    xalign 0.5

                    for _d, _ev in _upcoming_p[:6]:
                        hbox:
                            spacing 4
                            frame:
                                xsize 10
                                ysize 10
                                background Frame(_ev[1], 0, 0)
                                yalign 0.5
                            text "D[_d] [_ev[0]]":
                                color "#aaaaaa"
                                size 12
                                font "fonts/RobotoMono-Regular.ttf"

    ## ── Close button — clears the unread queue ─────────────────────────────
    textbutton "[[ CLOSE ]":
        xalign 0.5
        yalign 0.92
        action [SetField(store, "_phone_notifications", []), Hide("phone_screen")]
        text_color "#cccccc"
        text_hover_color "#ffffff"
        text_size 18
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        background "#220000"
        hover_background "#440000"
        padding (20, 10)

    key "K_ESCAPE" action [SetField(store, "_phone_notifications", []), Hide("phone_screen")]


## ---------------------------------------------------------------------------
## Outcome Panel — displays stat change summary, like Rich outcome boxes
## Usage: show screen outcome_panel("+ 5000 CZK, -10 PCR HATRED")
##        pause 2.0
##        hide screen outcome_panel
## ---------------------------------------------------------------------------

## ---------------------------------------------------------------------------
## Martin Meeting affection panel — top-left floating, only shown during MM.
## Threshold ≥ 7 unlocks the boss-card pick. Martin's signature magenta accent
## (matches the affection tutorial popup); switches to gold once the threshold
## is cleared.
## ---------------------------------------------------------------------------

screen mm_affection_panel():
    zorder 90

    python:
        _mm_aff      = getattr(store, 'martin_affection', 0)
        _mm_max      = 10
        _mm_goal     = 7
        _mm_unlocked = _mm_aff >= _mm_goal
        _mm_accent   = "#cc88cc"
        _mm_color    = "#ffd24a" if _mm_unlocked else _mm_accent
        _mm_label    = "GIFT UNLOCKED" if _mm_unlocked else "AFFECTION"
        _mm_filled   = max(0, min(_mm_max, _mm_aff))
        _mm_pips     = ("●" * _mm_filled) + ("○" * (_mm_max - _mm_filled))

    frame:
        xpos 30
        ypos 126
        xsize 300
        padding (18, 14)
        background Frame("#0d0d0df2", 0, 0)

        vbox:
            spacing 7

            text "MARTIN":
                color _mm_accent
                size 13
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            frame:
                xfill True
                ysize 2
                background Frame(_mm_color, 0, 0)

            null height 1

            hbox:
                spacing 10
                text _mm_label:
                    color _mm_color
                    size 19
                    bold True
                    outlines [(1, "#000000cc", 0, 0)]
                    font "fonts/RobotoMono-Regular.ttf"
                text "[_mm_aff]{color=#888888}/[_mm_max]{/color}":
                    color "#ffffff"
                    size 19
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

            text _mm_pips:
                color _mm_color
                size 16
                font "fonts/RobotoMono-Regular.ttf"

            text ("✓ Boss card unlocked" if _mm_unlocked else "Reach [_mm_goal] to unlock the boss card"):
                color ("#ffd24a" if _mm_unlocked else "#9a9a9a")
                size 11
                font "fonts/RobotoMono-Regular.ttf"


## Outcome readout. Visually distinct from a choice menu — no boxed frame,
## no header banner, slides up from the bottom edge so it's read as
## "result of last action", not "make a decision now". Playtester read the
## old framed-and-bordered panel as a choice prompt and waited for options.
transform _outcome_slide_in:
    yoffset 40
    alpha 0.0
    parallel:
        easeout 0.4 yoffset 0
    parallel:
        linear 0.25 alpha 1.0

transform _outcome_continue_pulse:
    alpha 0.4
    linear 0.7 alpha 0.85
    linear 0.7 alpha 0.4
    repeat

transform _outcome_arrow_nudge:
    xoffset 0
    easeout 0.55 xoffset 5
    easein 0.55 xoffset 0
    repeat

## Parse a flat outcome string into per-line chunks with semantic colors.
## Paren-aware split so "TOOK THE HEAT (1E, exhaust — gain 10 block, draw 1)"
## stays as one chunk and only TOP-LEVEL stat boundaries get broken out.
## Split rules (in order): explicit pipe " | "; OR comma+space followed by a
## delta marker (+, -, +card, ✓, [). Naked commas inside numbers (-3,500)
## or paren groups never split.
##
## NOTE: `re` is accessed inline via __import__('re'), never bound to a store
## name. Importing modules at init python: scope binds them to the save store,
## and Ren'Py's pickle pass on save then crashes ("Could not pickle <module
## 're'>"). Same pattern the codebase uses for random everywhere.
##
## SAVE-RECOVERY: an earlier version of this file did `import re as _outcome_re`
## at init python and shipped that into player saves. Loading such a save
## restores the bad binding to the store and the next save crashes on pickle.
## We strip the legacy names on every save load so legacy saves heal in place.
init python:
    def _outcome_cleanup_stale_re():
        for _name in ("_outcome_re", "_OUTCOME_SPLIT_RE"):
            if hasattr(store, _name):
                delattr(store, _name)
    _outcome_cleanup_stale_re()
    config.after_load_callbacks.append(_outcome_cleanup_stale_re)

    def _outcome_parse(text):
        if not text:
            return []
        re = __import__('re')
        parens = []
        def _mask(m):
            parens.append(m.group(0))
            return "\x00{}\x00".format(len(parens) - 1)
        masked = re.sub(r'\([^)]*\)|\[[^\]]*\]', _mask, text)
        ## Split on (a) pipe, (b) comma + delta marker, (c) 3+ spaces (the
        ## call-site convention some outcomes use instead of commas).
        raw = re.split(r'\s*\|\s*|,\s+(?=[+\-]|\+\s*card|\+\s*CARD|✓|\[)|\s{3,}', masked)
        out = []
        for chunk in raw:
            for i, p in enumerate(parens):
                chunk = chunk.replace("\x00{}\x00".format(i), p)
            chunk = chunk.strip().rstrip('.').strip()
            if chunk:
                out.append((chunk, _outcome_chunk_color(chunk)))
        return out

    def _outcome_chunk_color(chunk):
        up = chunk.upper()
        sign = chunk[0] if chunk else ""
        ## Card grants — always gold. Match early so a card-name chunk
        ## that happens to contain "HP"/"CODING" doesn't get reclassified.
        if "CARD" in up and ("+" in chunk[:3] or "TAKEN" in up or "GAINED" in up):
            return "#ffd24a"
        ## Coding stat — canonical Skill-blue. Hoisted above the money
        ## branch so "Coding/night" type strings color as code, not cash.
        if "CODING" in up:
            return "#55a0ff"
        ## Money / HP / block gains read green up, red down.
        if any(k in up for k in ("CZK", "CASH", "MONEY", "HP", "SKILL", "BLOCK")):
            if sign == "+":
                return "#55dd66"
            if sign == "-":
                return "#dd5544"
        ## Hatred polarity inverts — gaining hatred is bad.
        if "HATRED" in up:
            if sign == "+":
                return "#dd5544"
            if sign == "-":
                return "#55dd66"
        ## Bracketed tag chunks ("[Kovář profile +1]") — accent gold.
        if chunk.startswith("[") and "]" in chunk:
            return "#e8c878"
        ## Fallback — readable cream.
        return "#e0e0d0"


screen outcome_panel(outcome_text):
    layer "screens"
    zorder 200

    python:
        _op_chunks = _outcome_parse(outcome_text)

    ## Single frame > vbox > text-children — the canonical pattern. Earlier
    ## nested-frames-containing-text-directly + ATL-on-vbox combinations
    ## tripped Ren'Py's screen layout into ui.interact stack-imbalance
    ## crashes (seen on gym/coding card-offer flows).
    frame:
        xalign 0.5
        yalign 0.86
        padding (32, 14)
        background Frame("#0a0a0add", 0, 0)

        vbox:
            spacing 8
            xalign 0.5

            ## STAT CHUNKS — one line each, colored by polarity. Falls back
            ## to the raw text rendered flat when parsing yields nothing
            ## (pure-prose outcomes like "No change. You don't need it.").
            if _op_chunks:
                for _chunk, _color in _op_chunks:
                    text _chunk substitute False:
                        color _color
                        size 22
                        bold True
                        xalign 0.5
                        outlines [(2, "#000000aa", 0, 0)]
                        font "fonts/RobotoMono-Regular.ttf"
            else:
                text outcome_text substitute False:
                    color "#e0e0d0"
                    size 20
                    italic True
                    xalign 0.5
                    xmaximum 900
                    text_align 0.5
                    outlines [(2, "#000000aa", 0, 0)]

            null height 4

            hbox:
                spacing 3
                xalign 0.5
                text "›" at _outcome_arrow_nudge:
                    color "#88aa88"
                    size 11
                    italic True
                text "click to continue":
                    color "#88aa88"
                    size 11
                    italic True


## ---------------------------------------------------------------------------
## Card Grant — celebration screen for an already-granted card. Modal, click
## to dismiss. Use AFTER `grant_card(card_id, silent=True)` so the player
## sees what entered their deck on its own beat instead of buried inside
## an outcome string. For interactive TAKE/PASS, use card_solo_offer_screen.
## ---------------------------------------------------------------------------

screen card_grant_screen(card_id):
    modal True
    zorder 700
    layer "screens"

    python:
        _gr_card = CARD_LIBRARY.get(card_id, {})

    add "#0a0a0aee"

    vbox:
        xalign 0.5
        yalign 0.08
        spacing 6

        text "+ CARD GAINED":
            xalign 0.5
            color "#ffd24a"
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(3, "#000000", 0, 0)]

        text "Added to your deck.":
            xalign 0.5
            color "#888888"
            size 14
            italic True
            font "fonts/RobotoMono-Regular.ttf"

    fixed:
        xalign 0.5
        yalign 0.5
        xysize (420, 580)
        use card_visual(_gr_card)

    textbutton "[[ CONTINUE ]":
        xalign 0.5
        yalign 0.92
        action Return(True)
        text_color "#ffffff"
        text_hover_color "#ffd24a"
        text_size 22
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        text_xalign 0.5
        background Frame("#1a1a1aee", 4, 4)
        hover_background Frame("#2a2a2aee", 4, 4)
        padding (22, 12)

    key "K_RETURN" action Return(True)
    key "K_KP_ENTER" action Return(True)
    key "K_SPACE" action Return(True)
    key "K_ESCAPE" action Return(True)


## ---------------------------------------------------------------------------
## Card Shop — paid-trio offer screen. Renders priced cards; BUY is gated on
## cash. Returns a card_id to buy, or "leave". Currently unwired (the legacy
## bouncer-market caller was removed when Bouncer collapsed to the flat money
## lane). Kept as a future-event utility — pairs with build_card_shop_offers
## in card_data.rpy.
## ---------------------------------------------------------------------------

screen card_shop_screen(offers):
    modal True
    zorder 700

    add "#0a0a0aee"
    use class_color_frame(thickness=3, alpha_suffix="aa")

    python:
        _shop_money = stats.available_money if stats else 0

    text "THE DEALER":
        xalign 0.5
        yalign 0.055
        color "#e8c878"
        size 52
        bold True
        font "fonts/RobotoMono-Regular.ttf"
        outlines [(3, "#000000", 0, 0)]

    text "Cash on hand:  [_shop_money] CZK":
        xalign 0.5
        yalign 0.135
        color "#ffd700"
        size 22
        bold True
        font "fonts/RobotoMono-Regular.ttf"

    hbox:
        xalign 0.5
        yalign 0.5
        spacing 44

        for _offer in offers:
            python:
                _sc_cid    = _offer["card_id"]
                _sc_price  = _offer["price"]
                _sc_card   = CARD_LIBRARY.get(_sc_cid, {})
                _sc_afford = _shop_money >= _sc_price

            vbox:
                spacing 14
                xalign 0.5

                use card_visual(_sc_card)

                text "[_sc_price] CZK":
                    xalign 0.5
                    color ("#ffd700" if _sc_afford else "#aa5544")
                    size 26
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

                textbutton ("[[ BUY ]" if _sc_afford else "[[ NOT ENOUGH CASH ]"):
                    xalign 0.5
                    sensitive _sc_afford
                    action Return(_sc_cid)
                    text_color ("#ffffff" if _sc_afford else "#6a5f55")
                    text_hover_color "#ffd700"
                    text_size 20
                    text_bold True
                    text_font "fonts/RobotoMono-Regular.ttf"
                    background Frame("#1a1a1aee", 4, 4)
                    hover_background Frame("#2a2a2aee", 4, 4)
                    padding (26, 12)

    textbutton "[[ LEAVE ]":
        xalign 0.5
        yalign 0.94
        action Return("leave")
        text_color "#bbbbbb"
        text_hover_color "#ffffff"
        text_size 20
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        background Frame("#1a1a1aee", 4, 4)
        hover_background Frame("#2a2a2aee", 4, 4)
        padding (24, 11)

    key "K_ESCAPE" action Return("leave")


## ---------------------------------------------------------------------------
## card_visual — the canonical "fancy card" render, identical to the post-
## combat reward card. Used by the offer screens so every card the player is
## shown looks the same. 420x580 footprint; the cost gem overhangs top-left.
## ---------------------------------------------------------------------------

screen card_visual(card):
    ## Thin wrapper around the canonical card renderer in battle_screen.rpy.
    ## Used by card_offer_screen, card_solo_offer_screen, fixer preview, and
    ## anywhere else the game shows a full-size StS-style card preview. The
    ## inspect-mode card_view fits the legacy 420×580 envelope this screen
    ## was built around (actual rendered size: 400×572 — close enough that
    ## existing 420×580 fixed-size callers still anchor correctly).
    use battle_card_view(cid=card.get("id", ""), mode="inspect", playable=True)


## ---------------------------------------------------------------------------
## Card Offer Screen — TAKE or PASS prompt for activity/event card drops.
## Returns "take" or "pass" via Return().
## ---------------------------------------------------------------------------

screen card_offer_screen(card, source_label="", pass_stats_text=""):
    modal True
    zorder 700

    add "#0a0a0aee"

    python:
        _co_color   = card_type_color(card, "frame")
        _co_name    = card.get("name", "?")
        _co_type    = card.get("type", "")
        _co_rarity  = card.get("rarity", "")
        ## Pre-compute stat-line list at screen scope so the conditional
        ## vbox below doesn't need an inline `python:` block (which would
        ## imbalance Ren'Py's screen widget stack on render).
        _stat_lines = [s.strip() for s in pass_stats_text.split(",") if s.strip()] if pass_stats_text else []
        _co_cost    = card.get("cost", 0)
        _co_flavor  = card.get("flavor", "")

    ## Outer class-color accent — frames the modal so the offer reads as YOURS.
    use class_color_frame(thickness=3, alpha_suffix="aa")

    vbox:
        xalign 0.5
        yalign 0.04
        spacing 6

        text "CHOOSE ONE":
            xalign 0.5
            color "#ffffff"
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        if source_label:
            text "From: [source_label]":
                xalign 0.5
                color "#666666"
                size 14
                font "fonts/RobotoMono-Regular.ttf"

    ## ── Side-by-side: TAKE-the-card on the left, PASS-keep-stats on the right ──
    hbox:
        xalign 0.5
        yalign 0.46
        spacing 50

        ## ─────────────── LEFT: card preview ───────────────
        fixed:
            xysize (420, 580)
            use card_visual(card)

        ## ─────────────── Thin vertical rule between the two paths ───────────────
        frame:
            yalign 0.5
            xsize 1
            ysize 460
            background Frame("#2a2a2a", 0, 0)

        ## ─────────────── RIGHT: PASS / stat reward preview ───────────────
        ## Stat side now uses the player's class accent color so it reads as
        ## equally serious as the card side. Strategy hints under each side
        ## tell the player WHY each path matters.
        $ _co_class_accent = class_accent_color()

        frame:
            xsize 420
            ysize 540
            background Frame("#0d0d0dee", 4, 4)
            padding (22, 18)

            vbox:
                spacing 12
                xalign 0.5

                frame:
                    xalign 0.5
                    xsize 360
                    ysize 5
                    background Frame(_co_class_accent, 0, 0)

                null height 6

                ## Stat icon — class-color circle, "+" glyph (gain)
                frame:
                    xsize 56
                    ysize 56
                    background Frame(_co_class_accent, 4, 4)
                    xalign 0.5
                    text "+":
                        color "#000000"
                        size 36
                        bold True
                        xalign 0.5
                        yalign 0.5

                null height 2

                text "STAT REWARD":
                    color "#ffffff"
                    size 30
                    bold True
                    xalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"

                text "Money · Coding · Hatred":
                    color _co_class_accent
                    size 13
                    xalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"

                null height 10

                text "─────────────────────────":
                    color "#222222"
                    size 12
                    xalign 0.5

                null height 6

                if _stat_lines:
                    ## One line per delta — scannable instead of one wrapped
                    ## paragraph. (Splitting precomputed at screen scope.)
                    ## `substitute False` is critical — _sl can contain
                    ## literal "[BODYBUILDER]" / "[STREAK x3]" tags from
                    ## activity outcome strings; without this, Ren'Py tries
                    ## to interpolate them as variables and NameError-crashes
                    ## the screen render mid-tree (which leaves transient-
                    ## layer Many<Fixed> open and trips the next pause's
                    ## ui.interact stack check). Same applies to _co_name /
                    ## _co_flavor / _co_effect above.
                    vbox:
                        spacing 6
                        xalign 0.5
                        for _sl in _stat_lines:
                            text _sl substitute False:
                                color "#ffcc66"
                                size 18
                                bold True
                                xalign 0.5
                                xmaximum 360
                                text_align 0.5
                else:
                    text "Keep the day's stat changes.":
                        color "#cccccc"
                        size 15
                        xalign 0.5
                        xmaximum 360
                        text_align 0.5

    ## ── TAKE / TAKE buttons — same color, same weight. The DECISION is
    ## about content (card vs stats), not action. Asymmetric button colors
    ## made stats look like the "safe / default" choice and players ignored
    ## cards. Both buttons are now identical white-on-dark; the panels above
    ## carry the visual differentiation.
    hbox:
        xalign 0.5
        yalign 0.93
        spacing 50

        textbutton "[[ TAKE THE CARD ]":
            xsize 420
            xalign 0.5
            action Return("take")
            text_color "#ffffff"
            text_hover_color _co_color
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            text_xalign 0.5
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (20, 14)

        null width 1

        textbutton "[[ TAKE THE STATS ]":
            xsize 420
            xalign 0.5
            action Return("pass")
            text_color "#ffffff"
            text_hover_color _co_class_accent
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            text_xalign 0.5
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (20, 14)

    text "T = card   ·   P = stats   ·   ESC = stats":
        xalign 0.5
        yalign 0.985
        color "#444444"
        size 12
        font "fonts/RobotoMono-Regular.ttf"

    ## Keyboard shortcuts
    key "K_t" action Return("take")
    key "K_RETURN" action Return("take")
    key "K_KP_ENTER" action Return("take")
    key "K_p" action Return("pass")
    key "K_ESCAPE" action Return("pass")


## ---------------------------------------------------------------------------
## Card Solo Offer — TAKE / PASS prompt for arc-reward cards where there is
## no stat alternative (e.g. Martin's legal nuke). Card preview
## centered; TAKE / PASS buttons underneath. Same visual language as
## card_offer_screen so the player learns one pattern.
## ---------------------------------------------------------------------------

screen card_solo_offer_screen(card, source_label=""):
    modal True
    zorder 700

    add "#0a0a0aee"

    python:
        ## Card colour — only the TAKE button's hover accent needs it now that
        ## card_visual renders the card body.
        _co_color = card_type_color(card, "frame")

    use class_color_frame(thickness=3, alpha_suffix="aa")

    vbox:
        xalign 0.5
        yalign 0.06
        spacing 6

        text "OFFER":
            xalign 0.5
            color "#ffffff"
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        if source_label:
            text "From: [source_label]":
                xalign 0.5
                color "#666666"
                size 14
                font "fonts/RobotoMono-Regular.ttf"

    ## Card preview — the canonical fancy render, centered.
    fixed:
        xalign 0.5
        yalign 0.5
        xysize (420, 580)
        use card_visual(card)

    ## TAKE / PASS — same visual weight; the choice is "do I want this card"
    ## not "card vs stats". No stat panel.
    hbox:
        xalign 0.5
        yalign 0.93
        spacing 30

        textbutton "[[ TAKE ]":
            xsize 200
            xalign 0.5
            action Return("take")
            text_color "#ffffff"
            text_hover_color _co_color
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            text_xalign 0.5
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (20, 14)

        textbutton "[[ PASS ]":
            xsize 200
            xalign 0.5
            action Return("pass")
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            text_xalign 0.5
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (20, 14)

    text "T = TAKE   ·   P = PASS   ·   ESC = PASS":
        xalign 0.5
        yalign 0.985
        color "#444444"
        size 12
        font "fonts/RobotoMono-Regular.ttf"

    key "K_t" action Return("take")
    key "K_RETURN" action Return("take")
    key "K_KP_ENTER" action Return("take")
    key "K_p" action Return("pass")
    key "K_ESCAPE" action Return("pass")


## ---------------------------------------------------------------------------
## Card Reward Trio — pick 1 of 3 cards from the basic pool (post-battle).
## Visual mirrors card_solo_offer_screen at a slightly smaller per-panel size
## so all 3 fit side-by-side. Returns the chosen card_id string, or "skip".
## Keyboard: 1/2/3 = TAKE corresponding card. S / ESC = SKIP.
## ---------------------------------------------------------------------------

screen card_reward_trio_screen(cards):
    modal True
    zorder 700

    add "#0a0a0aee"

    use class_color_frame(thickness=3, alpha_suffix="aa")

    text "CHOOSE A CARD":
        xalign 0.5
        yalign 0.12
        color "#e8c878"
        size 64
        bold True
        font "fonts/RobotoMono-Regular.ttf"
        outlines [(3, "#000000", 0, 0)]

    hbox:
        xalign 0.5
        yalign 0.5
        spacing 36

        for _ctp_i, _cid in enumerate(cards):
            ## Fan-out hover offset: left leans left, centre stays, right leans right.
            ## Indexed by position in the trio; 4th+ slot defaults to no shift.
            $ _hover_xoff = (-36, 0, 36)[_ctp_i] if _ctp_i < 3 else 0

            ## The fixed pins this slot's layout footprint — the hover zoom
            ## happens inside it, so the hbox never re-flows and the other
            ## two cards stay planted (same fix as the activity tiles).
            fixed:
                xysize (420, 580)
                button:
                    xsize 420
                    ysize 580
                    background None
                    hover_background None
                    action Return(_cid)
                    at reward_card_hover(_hover_xoff)

                    use battle_card_view(cid=_cid, mode="inspect", playable=True)

    textbutton "SKIP":
        xalign 0.5
        yalign 0.86
        action Return("skip")
        text_color "#bbbbbb"
        text_hover_color "#ffffff"
        text_size 22
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        text_xalign 0.5
        background Frame("#1a1a1aee", 6, 6)
        hover_background Frame("#3a1a1aee", 6, 6)
        padding (44, 14)

    key "K_1" action If(len(cards) >= 1, Return(cards[0]), NullAction())
    key "K_2" action If(len(cards) >= 2, Return(cards[1]), NullAction())
    key "K_3" action If(len(cards) >= 3, Return(cards[2]), NullAction())
    key "K_s" action Return("skip")
    key "K_ESCAPE" action Return("skip")


## ---------------------------------------------------------------------------
## Fixer Removal — scrollable picker for spending CZK to remove a card from
## the player's deck (vision §1 pillar 3: money is the only shop). Activity
## entrypoint is activity_fixer in script.rpy.
##
## Pricing is FLAT — every card costs the same `price` right now. The price
## escalates between visits (each successful shred bumps the next). `next_price`
## is telegraphed in the header so the player can decide if they want to scrub
## now or wait (and have a stronger reason).
##
## Receives:
##   entries    list of card_id strings (one per card instance — duplicates
##              render as separate rows so the player picks WHICH copy goes).
##   price      flat CZK cost to shred ANY card this visit.
##   next_price what the NEXT shred will cost (after this one resolves).
##
## Returns:
##   ("remove", card_id) — caller deducts `price` and removes the card.
##   ("leave", None)     — free reconnaissance, no day consumed.
## ---------------------------------------------------------------------------

## Subtle hover cue for the fixer grid — the real preview is the inspect
## overlay; the grid card itself just lifts a touch. Kept small so it stays
## inside the grid's gutters/padding (no neighbour occlusion, no viewport
## clipping — the big card_hover_lift zoom got shredded by both).
transform fixer_card_nudge:
    on hover:
        ease 0.12 yoffset -8
    on idle, insensitive:
        ease 0.12 yoffset 0


screen fixer_removal_screen(entries, price, next_price):
    modal True
    zorder 700

    ## Card instance under the cursor + its (row, col) grid slot — drives the
    ## inspect overlay and its anchor position. The adjustment tracks the
    ## grid's vertical scroll so the anchor stays glued while scrolled.
    default _fx_hover_cid = None
    default _fx_hover_rc  = (0, 0)
    default _fx_yadj      = ui.adjustment()

    add Transform("images/backgrounds/bg_fixer.jpg", size=(config.screen_width, config.screen_height))
    add "#0a0a0acc"

    use class_color_frame(thickness=3, alpha_suffix="aa")

    python:
        _CORRUPTION_COLOR = {
            "rage":       "#aa1a1a",
            "compromise": "#5a5550",
            "status":     "#8a7a2a",
        }
        ## Safe glyphs only (RobotoMono has no emoji — they render as '?').
        _CORRUPTION_GLYPH = {
            "rage":       "† ",
            "compromise": "× ",
            "status":     "☠ ",
        }
        _f_affordable = (stats.available_money >= price)
        _f_price_color = ("#ffd700" if _f_affordable else "#a04040")

    ## Header — FIXED position (not centered-flow) so the grid below sits at
    ## known coordinates: the hover-inspect overlay anchors to the hovered
    ## card's slot, which needs deterministic grid geometry.
    vbox:
        xalign 0.5
        ypos 30
        spacing 10

        text "FIXER · RUN A CARD THROUGH THE SHREDDER":
            xalign 0.5
            color "#9a8060"
            size 36
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(2, "#000000", 0, 0)]

        ## Pricing strip — current visit's flat price + escalation telegraph.
        hbox:
            xalign 0.5
            spacing 28
            text "TONIGHT'S PRICE: [price:,] CZK":
                color _f_price_color
                size 22
                bold True
                font "fonts/RobotoMono-Regular.ttf"
            text "·":
                color "#444444"
                size 22
            text "NEXT SHRED: [next_price:,] CZK":
                color "#888888"
                size 18
                italic True
                font "fonts/RobotoMono-Regular.ttf"
            text "·":
                color "#444444"
                size 22
            text "WALLET: [stats.available_money:,] CZK":
                color "#ffd700"
                size 18
                bold True
                font "fonts/RobotoMono-Regular.ttf"

    ## Grid geometry constants — shared by the layout below AND the overlay
    ## anchor math. Slot stride = card (220/320) + gutter (16/24).
    python:
        _FXG_VX, _FXG_VY = 220, 150   ## viewport screen position
        _FXG_PAD         = 36         ## inner padding (gem overhang room)
        _FXG_SX, _FXG_SY = 236, 344   ## slot stride x/y

    viewport:
        xpos _FXG_VX
        ypos _FXG_VY
        xsize 1480
        ysize 740
        yadjustment _fx_yadj
        scrollbars "vertical"
        mousewheel True
        draggable True

        ## Same card UI as inspecting your own deck — full card faces, so the
        ## shred decision sees exactly what each card DOES, not just a name.
        ## 6 per row; click a card to run it through the shredder. Cards dim
        ## when you can't cover tonight's price. The padded frame gives the
        ## cost gems (which overhang each card's top-left by 22px) room
        ## inside the viewport's clip area.
        $ _shred_rows = [entries[i:i+6] for i in range(0, len(entries), 6)]
        frame:
            background None
            padding (_FXG_PAD, _FXG_PAD)
            vbox:
                spacing 24
                for _ri, _shred_row in enumerate(_shred_rows):
                    hbox:
                        spacing 16
                        for _ci, _fcid in enumerate(_shred_row):
                            fixed:
                                xysize (220, 320)
                                ## Sensitive even when the price is out of
                                ## reach — inspecting your own deck must keep
                                ## working broke; only the SHRED action gates.
                                button:
                                    xsize 220
                                    ysize 316
                                    background None
                                    hover_background None
                                    action (Return(("remove", _fcid)) if _f_affordable else NullAction())
                                    hovered [SetScreenVariable("_fx_hover_cid", _fcid), SetScreenVariable("_fx_hover_rc", (_ri, _ci))]
                                    unhovered SetScreenVariable("_fx_hover_cid", None)
                                    at fixer_card_nudge
                                    use battle_card_view(cid=_fcid, mode="hand", playable=_f_affordable)

    textbutton "[[ ← LEAVE — no time lost ]":
        xalign 0.5
        ypos 930
        action Return(("leave", None))
        text_color "#888888"
        text_hover_color "#ffffff"
        text_size 18
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        background Frame("#0d0d0dee", 3, 3)
        hover_background Frame("#1a1a1aee", 3, 3)
        padding (24, 10)

    ## Hover-inspect overlay — the full-size card, drawn after (= on top of)
    ## the grid so it's never clipped by the viewport or occluded by the
    ## neighbouring cards. Anchored to the hovered card's slot: it floats at
    ## the card's upper-right, flipping to the upper-left for the rightmost
    ## column so it never runs offscreen. Vertical position is clamped to the
    ## screen and tracks the viewport scroll.
    if _fx_hover_cid:
        python:
            _ins_slot_x = _FXG_VX + _FXG_PAD + _fx_hover_rc[1] * _FXG_SX
            _ins_slot_y = _FXG_VY + _FXG_PAD + _fx_hover_rc[0] * _FXG_SY - int(_fx_yadj.value)
            _ins_x = (_ins_slot_x - 414) if _fx_hover_rc[1] >= 4 else (_ins_slot_x + 234)
            _ins_y = max(16, min(_ins_slot_y - 200, 1080 - 588))
        fixed:
            xpos _ins_x
            ypos _ins_y
            xysize (400, 572)
            at inspect_overlay_in
            use battle_card_view(cid=_fx_hover_cid, mode="inspect", playable=True)

    key "K_ESCAPE" action Return(("leave", None))


## ---------------------------------------------------------------------------
## Fixer shop — the unified merchant screen. Everything on one table: cards
## (full widgets), gear (relic chips), the shred service, and LEAVE. Replaces
## the old menu + separate buy screens (and the dialogue-window glitch that
## came with a say-caption menu drawn over the scene).
##
## Receives the current stock + cash + shred state; returns a tuple action:
##   ("buy_card",  card_id)   ("buy_relic", relic_id)
##   ("shred",     None)      ("leave",     None)
## Driven by the fixer_shop_loop label in script.rpy, which re-calls the
## screen after each purchase so cash / stock / SOLD-OUT state stay live.
## ---------------------------------------------------------------------------
screen fixer_shop(card_offers, relic_offers, cash, shred_price, can_shred, shred_blocked):
    modal True
    zorder 700

    ## What the cursor is on: ("card", cid, col) / ("relic", rid, col) /
    ## ("shred",). Drives the hover-inspect overlays.
    default _sh_hover = None

    ## The scene IS the shop — full-bright, no dim wash, no header bar. The
    ## goods are laid out spatially on the Fixer's table; every item carries
    ## only a price tag. Hover an item to inspect it.
    add Transform("images/backgrounds/bg_fixer_shop.jpg", size=(config.screen_width, config.screen_height))

    python:
        ## Slot geometry — shared by layout + hover-overlay anchor math.
        _SH_CARD_W, _SH_CARD_GAP = 220, 36
        _SH_CARD_N  = max(len(card_offers), 1)
        _SH_CARD_X0 = (1920 - (_SH_CARD_N * _SH_CARD_W + (_SH_CARD_N - 1) * _SH_CARD_GAP)) // 2
        _SH_CARD_Y  = 330
        _SH_GEAR_X0, _SH_GEAR_Y = 360, 740
        _SH_GEAR_W,  _SH_GEAR_GAP = 150, 56
        _SH_SHRED_X, _SH_SHRED_Y = 1370, 710

    ## ── WALLET — small corner chip (the only readout on screen) ───────────
    frame:
        xanchor 1.0
        xpos 1894
        ypos 20
        background Frame("#0d0d0dcc", 4, 4)
        padding (16, 8)
        text "[cash:,] CZK":
            color "#ffd700"
            size 20
            bold True
            font "fonts/RobotoMono-Regular.ttf"

    ## ── CARDS — one row on the table, price tag under each ────────────────
    for _ci, _o in enumerate(card_offers):
        python:
            _ocid    = _o["card_id"]
            _oprice  = _o["price"]
            _osold   = bool(_o.get("sold"))
            _oafford = (not _osold) and (cash >= _oprice)
            _ox      = _SH_CARD_X0 + _ci * (_SH_CARD_W + _SH_CARD_GAP)
        if _osold:
            ## SOLD slot — the goods are gone, the spot stays (no reflow).
            frame:
                xpos _ox
                ypos _SH_CARD_Y
                xysize (220, 316)
                background Frame("#0a0806b4", 4, 4)
                text "SOLD":
                    align (0.5, 0.5)
                    color "#6a5a48"
                    size 30
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
        else:
            ## Stays sensitive even when unaffordable — hover-inspect must
            ## keep working with an empty wallet (insensitive buttons emit
            ## no hover events); only the BUY action is gated.
            button:
                xpos _ox
                ypos _SH_CARD_Y
                xsize 220
                ysize 316
                background None
                hover_background None
                padding (0, 0)
                action (Return(("buy_card", _ocid)) if _oafford else NullAction())
                hovered SetScreenVariable("_sh_hover", ("card", _ocid, _ci))
                unhovered SetScreenVariable("_sh_hover", None)
                at fixer_card_nudge
                use battle_card_view(cid=_ocid, mode="hand", playable=_oafford)
            frame:
                xanchor 0.5
                xpos (_ox + 110)
                ypos (_SH_CARD_Y + 326)
                background Frame("#0d0d0dcc", 4, 4)
                padding (14, 5)
                text "[_oprice:,] CZK":
                    color ("#ffd700" if _oafford else "#a04040")
                    size 19
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

    ## ── GEAR — relic objects on the table's left, price tag under each ────
    for _gi, _ro in enumerate(relic_offers):
        python:
            _rrid    = _ro["relic_id"]
            _rprice  = _ro["price"]
            _rsold   = bool(_ro.get("sold"))
            _rafford = (not _rsold) and (cash >= _rprice)
            _rhex    = relic_hex(_rrid) if _rafford else "#5a5042"
            _rx      = _SH_GEAR_X0 + _gi * (_SH_GEAR_W + _SH_GEAR_GAP)
        if _rsold:
            frame:
                xpos _rx
                ypos _SH_GEAR_Y
                xysize (_SH_GEAR_W, _SH_GEAR_W)
                background Frame("#0a0806b4", 3, 3)
                text "SOLD":
                    align (0.5, 0.5)
                    color "#6a5a48"
                    size 20
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
        else:
            button:
                xpos _rx
                ypos _SH_GEAR_Y
                xysize (_SH_GEAR_W, _SH_GEAR_W)
                background Frame(Solid(_rhex + "55"), 3, 3)
                hover_background Frame(Solid(_rhex + "99"), 3, 3)
                padding (4, 4)
                action (Return(("buy_relic", _rrid)) if _rafford else NullAction())
                hovered SetScreenVariable("_sh_hover", ("relic", _rrid, _gi))
                unhovered SetScreenVariable("_sh_hover", None)
                frame:
                    xfill True
                    yfill True
                    background "#11110cd0"
                    $ _ricon = relic_art_disp(_rrid, 118)
                    if _ricon is not None:
                        add _ricon align (0.5, 0.5) alpha (1.0 if _rafford else 0.35)
                    else:
                        text relic_glyph(_rrid):
                            align (0.5, 0.5)
                            color _rhex
                            size 48
                            bold True
                            font "fonts/RobotoMono-Regular.ttf"
            frame:
                xanchor 0.5
                xpos (_rx + _SH_GEAR_W // 2)
                ypos (_SH_GEAR_Y + _SH_GEAR_W + 10)
                background Frame("#0d0d0dcc", 4, 4)
                padding (12, 4)
                text "[_rprice:,] CZK":
                    color ("#ffd700" if _rafford else "#a04040")
                    size 17
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

    ## ── SHREDDER — the removal service as an object on the table ──────────
    python:
        _shred_afford = (cash >= shred_price)
        _shred_open   = can_shred and not shred_blocked
        _shred_usable = _shred_open and _shred_afford
    button:
        xpos _SH_SHRED_X
        ypos _SH_SHRED_Y
        xysize (190, 190)
        background Frame(Solid("#c0805055" if _shred_usable else "#3a302855"), 3, 3)
        hover_background Frame(Solid("#c0805099"), 3, 3)
        padding (4, 4)
        action (Return(("shred", None)) if _shred_usable else NullAction())
        hovered SetScreenVariable("_sh_hover", ("shred",))
        unhovered SetScreenVariable("_sh_hover", None)
        frame:
            xfill True
            yfill True
            background "#11110cd0"
            add Transform("images/pictures/shredder_icon.png", fit="contain", xysize=(170, 170)):
                align (0.5, 0.5)
                alpha (1.0 if _shred_usable else 0.4)
    frame:
        xanchor 0.5
        xpos (_SH_SHRED_X + 95)
        ypos (_SH_SHRED_Y + 200)
        background Frame("#0d0d0dcc", 4, 4)
        padding (12, 4)
        if _shred_open:
            text "[shred_price:,] CZK":
                color ("#ffd700" if _shred_afford else "#a04040")
                size 17
                bold True
                font "fonts/RobotoMono-Regular.ttf"
        else:
            text ("COOLED OFF" if shred_blocked else "NOTHING TO SHRED"):
                color "#6a5a48"
                size 14
                bold True
                font "fonts/RobotoMono-Regular.ttf"

    ## ── LEAVE — corner ribbon, StS style ──────────────────────────────────
    textbutton "← LEAVE":
        xpos 40
        ypos 980
        action Return(("leave", None))
        text_color "#c8b8a0"
        text_hover_color "#ffffff"
        text_size 24
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        background Frame("#1a0d08ee", 4, 4)
        hover_background Frame("#33201270", 4, 4)
        padding (28, 14)

    ## ── HOVER-INSPECT OVERLAYS — drawn last, layered over everything ──────
    if _sh_hover is not None and _sh_hover[0] == "card":
        python:
            _ins_slot_x = _SH_CARD_X0 + _sh_hover[2] * (_SH_CARD_W + _SH_CARD_GAP)
            _ins_x = (_ins_slot_x - 414) if _sh_hover[2] >= (_SH_CARD_N - 2) else (_ins_slot_x + 234)
            _ins_y = max(16, min(_SH_CARD_Y - 200, 1080 - 588))
        fixed:
            xpos _ins_x
            ypos _ins_y
            xysize (400, 572)
            at inspect_overlay_in
            use battle_card_view(cid=_sh_hover[1], mode="inspect", playable=True)

    elif _sh_hover is not None and _sh_hover[0] == "relic":
        python:
            _rh_rid  = _sh_hover[1]
            _rh_meta = RELIC_LIBRARY.get(_rh_rid, {})
            _rh_hex  = relic_hex(_rh_rid)
            _rh_x    = _SH_GEAR_X0 + _sh_hover[2] * (_SH_GEAR_W + _SH_GEAR_GAP)
        frame:
            xpos _rh_x
            yanchor 1.0
            ypos (_SH_GEAR_Y - 14)
            background Frame("#0d0a08f0", 4, 4)
            padding (18, 14)
            xmaximum 460
            at inspect_overlay_in
            vbox:
                spacing 6
                text _rh_meta.get("name", _rh_rid):
                    color _rh_hex
                    size 22
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                text (_rh_meta.get("rarity", "common").upper()):
                    color "#8a7a64"
                    size 13
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                text _rh_meta.get("hook", ""):
                    color "#e2d8c4"
                    size 17
                    xmaximum 420
                    font "fonts/RobotoMono-Regular.ttf"

    elif _sh_hover is not None and _sh_hover[0] == "shred":
        python:
            _sh_next = fixer_buy_price(fixer_next_price())
        frame:
            xanchor 1.0
            xpos (_SH_SHRED_X - 14)
            yanchor 1.0
            ypos (_SH_SHRED_Y + 190)
            background Frame("#0d0a08f0", 4, 4)
            padding (18, 14)
            xmaximum 460
            at inspect_overlay_in
            vbox:
                spacing 6
                text "THE SHREDDER":
                    color "#c08050"
                    size 22
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                text "Runs one card from your deck through. Permanently.":
                    color "#e2d8c4"
                    size 17
                    xmaximum 420
                    font "fonts/RobotoMono-Regular.ttf"
                text "Next shred: [_sh_next:,] CZK":
                    color "#8a7a64"
                    size 14
                    italic True
                    font "fonts/RobotoMono-Regular.ttf"

    key "K_ESCAPE" action Return(("leave", None))



## ---------------------------------------------------------------------------
## Gym Choice — post-session binary: UPGRADE a card vs HEAL+MAX HP.
## Mirrors the card_offer_screen visual language (side-by-side panels) so the
## player recognizes the "two paths" pattern. Returns "upgrade" or "heal".
## ---------------------------------------------------------------------------

screen gym_choice_screen(heal_stats_text=""):
    modal True
    zorder 700

    add "#0a0a0aee"

    use class_color_frame(thickness=3, alpha_suffix="aa")

    python:
        _gc_class_accent = class_accent_color()
        _gc_upgrade_accent = "#ffaa44"  ## gold-orange for "improvement"
        _gc_heal_lines = [s.strip() for s in heal_stats_text.split(",") if s.strip()] if heal_stats_text else []

    vbox:
        xalign 0.5
        yalign 0.04
        spacing 6

        text "AFTER THE SESSION":
            xalign 0.5
            color "#ffffff"
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "Body's quiet. Head's quieter. Pick what stays.":
            xalign 0.5
            color "#666666"
            size 14
            italic True
            font "fonts/RobotoMono-Regular.ttf"

    hbox:
        xalign 0.5
        yalign 0.46
        spacing 50

        ## ─────────────── LEFT: UPGRADE a card ───────────────
        frame:
            xsize 420
            ysize 540
            background Frame("#0d0d0dee", 4, 4)
            padding (22, 18)

            vbox:
                spacing 12
                xalign 0.5

                frame:
                    xalign 0.5
                    xsize 360
                    ysize 5
                    background Frame(_gc_upgrade_accent, 0, 0)

                null height 6

                frame:
                    xsize 56
                    ysize 56
                    background Frame(_gc_upgrade_accent, 4, 4)
                    xalign 0.5
                    text "↑":
                        color "#000000"
                        size 36
                        bold True
                        xalign 0.5
                        yalign 0.5

                null height 2

                text "UPGRADE A CARD":
                    color "#ffffff"
                    size 30
                    bold True
                    xalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"

                text "Sharpen the kit · permanent":
                    color _gc_upgrade_accent
                    size 13
                    xalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"

                null height 10

                text "─────────────────────────":
                    color "#222222"
                    size 12
                    xalign 0.5

                null height 6

                text "Pick one card from your deck. It becomes its '+' version for the rest of the run.":
                    color "#ffffff"
                    size 16
                    bold True
                    xalign 0.5
                    xmaximum 360
                    text_align 0.5
                    line_spacing 3

                null height 8

                text "Basic cards barely change. Rares get sharper. The good cards stay good for longer.":
                    color "#888888"
                    size 13
                    italic True
                    xalign 0.5
                    xmaximum 360
                    text_align 0.5

        ## ─────────────── Thin vertical rule ───────────────
        frame:
            yalign 0.5
            xsize 1
            ysize 460
            background Frame("#2a2a2a", 0, 0)

        ## ─────────────── RIGHT: HEAL + MAX HP (the existing reward) ───────────────
        frame:
            xsize 420
            ysize 540
            background Frame("#0d0d0dee", 4, 4)
            padding (22, 18)

            vbox:
                spacing 12
                xalign 0.5

                frame:
                    xalign 0.5
                    xsize 360
                    ysize 5
                    background Frame(_gc_class_accent, 0, 0)

                null height 6

                frame:
                    xsize 56
                    ysize 56
                    background Frame(_gc_class_accent, 4, 4)
                    xalign 0.5
                    text "+":
                        color "#000000"
                        size 36
                        bold True
                        xalign 0.5
                        yalign 0.5

                null height 2

                text "HEAL + MAX HP":
                    color "#ffffff"
                    size 30
                    bold True
                    xalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"

                text "Body · Hatred · Stat lift":
                    color _gc_class_accent
                    size 13
                    xalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"

                null height 10

                text "─────────────────────────":
                    color "#222222"
                    size 12
                    xalign 0.5

                null height 6

                if _gc_heal_lines:
                    vbox:
                        spacing 6
                        xalign 0.5
                        for _hl in _gc_heal_lines:
                            text _hl substitute False:
                                color "#ffcc66"
                                size 18
                                bold True
                                xalign 0.5
                                xmaximum 360
                                text_align 0.5
                else:
                    text "Keep the day's stat changes.":
                        color "#cccccc"
                        size 15
                        xalign 0.5
                        xmaximum 360
                        text_align 0.5

    hbox:
        xalign 0.5
        yalign 0.93
        spacing 50

        textbutton "[[ UPGRADE A CARD ]":
            xsize 420
            xalign 0.5
            action Return("upgrade")
            text_color "#ffffff"
            text_hover_color _gc_upgrade_accent
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            text_xalign 0.5
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (20, 14)

        null width 1

        textbutton "[[ HEAL + MAX HP ]":
            xsize 420
            xalign 0.5
            action Return("heal")
            text_color "#ffffff"
            text_hover_color _gc_class_accent
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            text_xalign 0.5
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (20, 14)

    text "U = upgrade   ·   H = heal   ·   ESC = heal":
        xalign 0.5
        yalign 0.985
        color "#444444"
        size 12
        font "fonts/RobotoMono-Regular.ttf"

    key "K_u" action Return("upgrade")
    key "K_h" action Return("heal")
    key "K_RETURN" action Return("heal")
    key "K_ESCAPE" action Return("heal")


## ---------------------------------------------------------------------------
## Deck Upgrade Picker — click any card in your deck to preview its '+' form.
## Non-upgradeable cards (status / rage / compromise / already-upgraded) are
## greyed out and non-clickable. Returns the chosen card_id, or "cancel" to
## back out to the gym-choice screen.
## ---------------------------------------------------------------------------

screen deck_upgrade_picker():
    modal True
    zorder 700

    ## Hovered card + its content-space slot origin — drives the anchored
    ## hover-inspect overlay (same pattern as fixer_removal_screen). Tuple is
    ## (cid, slot_x, slot_y, col); the adjustment tracks the grid's vertical
    ## scroll so the anchor stays glued while scrolled.
    default _dup_hover = None
    default _dup_yadj  = ui.adjustment()

    add "#0d0d11ee"

    python:
        ## Group by visual type — Attack / Skill / Power / Curse / Status —
        ## matches the deck_viewer grouping. Curse / Status sections are
        ## non-upgradeable (register_upgrade refuses corruption) but rendered
        ## anyway so the player sees the full deck while picking.
        _dup_cards = player_deck.cards if player_deck is not None else []
        _dup_count = len(_dup_cards)
        _dup_by_group = {}
        for _cid in _dup_cards:
            _c = CARD_LIBRARY.get(_cid)
            if _c is None:
                continue
            _grp = card_visual_type(_c)
            _dup_by_group.setdefault(_grp, []).append(_cid)
        _dup_group_order = list(CARD_VISUAL_TYPES)
        _dup_eligible_count = sum(1 for _cid in _dup_cards if is_upgradeable(_cid))

    use class_color_frame(thickness=3, alpha_suffix="aa")

    ## Header — FIXED position (not centered-flow) so the grid below sits at
    ## known coordinates: the hover-inspect overlay anchors to the hovered
    ## card's slot, which needs deterministic grid geometry (fixer pattern).
    vbox:
        xalign 0.5
        ypos 30
        spacing 10

        text "> UPGRADE A CARD <":
            xalign 0.5
            color "#ffaa44"
            size 36
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "[_dup_eligible_count] of [_dup_count] cards can be upgraded. Click one to preview.":
            xalign 0.5
            color "#888888"
            size 16

    ## Grid geometry constants — shared by the layout below AND the overlay
    ## anchor math. Slot stride = card (220/320) + gutter (16/28); group
    ## headers take a FIXED height so the content-space y cursor stays exact.
    python:
        _DUP_VX, _DUP_VY = 160, 150   ## viewport screen position
        _DUP_PAD         = 36         ## inner padding (gem overhang room)
        _DUP_SX, _DUP_SY = 236, 348   ## slot stride x/y
        _DUP_HDR_H       = 30         ## group-header band height

    ## ── Grid layout — full StS card visuals, click an upgradeable card to
    ## preview its `+` form. Non-upgradeable cards are dimmed (passed
    ## `playable=False` to battle_card_view) but stay hover-inspectable —
    ## only the pick action gates. Hover any card for the full-size inspect
    ## overlay, same as the fixer. Matches the deck_viewer grid; same
    ## 6-per-row pitch. The padded frame gives the cost gems (which overhang
    ## each card's top-left) room inside the viewport's clip area.
    viewport:
        xpos _DUP_VX
        ypos _DUP_VY
        xsize 1600
        ysize 760
        yadjustment _dup_yadj
        scrollbars "vertical"
        mousewheel True
        draggable True

        frame:
            background None
            padding (_DUP_PAD, _DUP_PAD)
            vbox:
                spacing 24

                ## Content-space y cursor — advanced group by group below so
                ## every card's slot origin is exact for the overlay anchor.
                $ _dup_y = _DUP_PAD

                for _col in _dup_group_order:
                    if _dup_by_group.get(_col):
                        $ _col_hex = TYPE_PALETTE.get(_col, {}).get("frame", "#888888")
                        $ _col_cards = _dup_by_group[_col]

                        ## Group header — color bar + count.
                        hbox:
                            spacing 12
                            ysize _DUP_HDR_H
                            frame:
                                ysize 22
                                xsize 8
                                yalign 0.5
                                background Frame(_col_hex, 0, 0)
                            text "{} ({})".format(_col.upper(), len(_col_cards)):
                                yalign 0.5
                                color _col_hex
                                size 22
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"
                                outlines [(1, "#000000", 0, 0)]

                        ## Rows begin under the header + one vbox gap.
                        $ _dup_y += _DUP_HDR_H + 24
                        $ _rows = [_col_cards[i:i+6] for i in range(0, len(_col_cards), 6)]
                        vbox:
                            spacing 28
                            for _ri, _row in enumerate(_rows):
                                hbox:
                                    spacing 16
                                    for _ci, _cid in enumerate(_row):
                                        $ _can_up = is_upgradeable(_cid)
                                        $ _slot_x = _DUP_PAD + _ci * _DUP_SX
                                        $ _slot_y = _dup_y + _ri * _DUP_SY

                                        ## fixed wrapper reserves the slot so
                                        ## the hover nudge never reflows the
                                        ## row.
                                        fixed:
                                            xysize (220, 320)
                                            ## Sensitive even when dimmed —
                                            ## inspecting the card must keep
                                            ## working; only the pick action
                                            ## gates on upgradeability.
                                            button:
                                                xsize 220
                                                ysize 316
                                                background None
                                                hover_background None
                                                action (Return(_cid) if _can_up else NullAction())
                                                hovered SetScreenVariable("_dup_hover", (_cid, _slot_x, _slot_y, _ci))
                                                unhovered SetScreenVariable("_dup_hover", None)
                                                at fixer_card_nudge
                                                use battle_card_view(cid=_cid, mode="hand", playable=_can_up)

                        ## Advance the cursor past this group's rows + gap.
                        $ _dup_y += len(_rows) * _DUP_SY - 28 + 24

                if not _dup_cards:
                    text "Your deck is empty.":
                        color "#666666"
                        size 16
                        italic True
                        xalign 0.5
                        text_align 0.5

    ## Class-aware back label — BB upgrades from gym, DE from cold-read
    ## (currently routed through gym-equivalent flow), BH from PubMed
    ## research. Falls back to plain BACK for unknown class.
    python:
        _dup_pc = stats.player_class if stats else None
        if _dup_pc == "biohacker":
            _dup_back_label = "[[ ← BACK TO RESEARCH ]"
        elif _dup_pc == "bodybuilder":
            _dup_back_label = "[[ ← BACK TO GYM ]"
        elif _dup_pc == "dark_empath":
            _dup_back_label = "[[ ← BACK ]"
        else:
            _dup_back_label = "[[ ← BACK ]"
    textbutton _dup_back_label:
        xalign 0.5
        ypos 940
        action Return("cancel")
        text_color "#aaaaaa"
        text_hover_color "#ffffff"
        text_size 20
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        background Frame("#1a1a1aee", 4, 4)
        hover_background Frame("#2a2a2aee", 4, 4)
        padding (24, 10)

    ## Hover-inspect overlay — the full-size card, drawn after (= on top of)
    ## the grid so it's never clipped by the viewport or occluded by the
    ## neighbouring cards. Anchored to the hovered card's slot, flipping to
    ## the upper-left for the rightmost columns so it never runs offscreen.
    ## Vertical position is clamped to the screen and tracks the scroll.
    if _dup_hover:
        python:
            _ins_slot_x = _DUP_VX + _dup_hover[1]
            _ins_slot_y = _DUP_VY + _dup_hover[2] - int(_dup_yadj.value)
            _ins_x = (_ins_slot_x - 414) if _dup_hover[3] >= 4 else (_ins_slot_x + 234)
            _ins_y = max(16, min(_ins_slot_y - 200, 1080 - 588))
        fixed:
            xpos _ins_x
            ypos _ins_y
            xysize (400, 572)
            at inspect_overlay_in
            use battle_card_view(cid=_dup_hover[0], mode="inspect", playable=True)

    key "K_ESCAPE" action Return("cancel")


## ---------------------------------------------------------------------------
## Card Upgrade Preview — side-by-side BASE → PLUS, with CONFIRM / CANCEL.
## Reuses the card-frame visual from card_offer_screen for both panels so
## the player reads the comparison instantly.
## ---------------------------------------------------------------------------

screen card_upgrade_preview(base_id):
    modal True
    zorder 710

    add "#0a0a0aee"

    use class_color_frame(thickness=3, alpha_suffix="aa")

    python:
        _cup_base = CARD_LIBRARY.get(base_id, {})
        _cup_plus_id = get_upgraded_id(base_id)
        _cup_plus = CARD_LIBRARY.get(_cup_plus_id, {}) if _cup_plus_id else {}
        _cup_color = card_type_color(_cup_base, "frame")
        _cup_upg_accent = "#ffaa44"
        ## Plain strings for the headline — dict .get() inside displayed text
        ## doesn't interpolate (the old `substitute False` band-aid rendered
        ## the raw expression on screen instead).
        _cup_headline = "{}   →   {}".format(_cup_base.get("name", base_id), _cup_plus.get("name", "?"))

    vbox:
        xalign 0.5
        yalign 0.04
        spacing 6

        text "CONFIRM UPGRADE":
            xalign 0.5
            color "#ffffff"
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text _cup_headline:
            xalign 0.5
            color _cup_upg_accent
            size 16
            bold True
            font "fonts/RobotoMono-Regular.ttf"

    hbox:
        xalign 0.5
        yalign 0.46
        spacing 40

        ## LEFT — base card (full StS visual via the canonical renderer).
        vbox:
            spacing 12
            xalign 0.5
            text "CURRENT":
                xalign 0.5
                color _cup_color
                size 16
                bold True
                font "fonts/RobotoMono-Regular.ttf"
            fixed:
                xysize (400, 580)
                use battle_card_view(cid=_cup_base.get("id", ""), mode="inspect", playable=True)

        ## Arrow glyph
        vbox:
            yalign 0.5
            xsize 80
            text "→":
                xalign 0.5
                yalign 0.5
                color _cup_upg_accent
                size 80
                bold True

        ## RIGHT — upgraded card.
        vbox:
            spacing 12
            xalign 0.5
            text "UPGRADED":
                xalign 0.5
                color _cup_upg_accent
                size 16
                bold True
                font "fonts/RobotoMono-Regular.ttf"
            fixed:
                xysize (400, 580)
                use battle_card_view(cid=_cup_plus.get("id", ""), mode="inspect", playable=True)

    hbox:
        xalign 0.5
        yalign 0.93
        spacing 50

        textbutton "[[ CANCEL ]":
            xsize 320
            xalign 0.5
            action Return("cancel")
            text_color "#aaaaaa"
            text_hover_color "#ffffff"
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            text_xalign 0.5
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (20, 14)

        null width 1

        textbutton "[[ CONFIRM ]":
            xsize 320
            xalign 0.5
            action Return("confirm")
            text_color "#ffffff"
            text_hover_color _cup_upg_accent
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            text_xalign 0.5
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (20, 14)

    text "ENTER = confirm   ·   ESC = cancel":
        xalign 0.5
        yalign 0.985
        color "#444444"
        size 12
        font "fonts/RobotoMono-Regular.ttf"

    key "K_RETURN" action Return("confirm")
    key "K_KP_ENTER" action Return("confirm")
    key "K_ESCAPE" action Return("cancel")


## ---------------------------------------------------------------------------
## Upgrade Reveal — fade-in, big card centered, 1s pause, fade-out. Used
## right after a confirmed upgrade, before end_day.
## ---------------------------------------------------------------------------

transform _upgrade_reveal_anim:
    alpha 0.0 zoom 0.85
    on show:
        parallel:
            ease 0.35 alpha 1.0
        parallel:
            ease 0.35 zoom 1.0

screen upgrade_reveal_screen(plus_id):
    modal True
    zorder 720

    add "#000000ff"

    python:
        _ur_accent = "#ffaa44"

    vbox at _upgrade_reveal_anim:
        xalign 0.5
        yalign 0.5
        spacing 18

        text "UPGRADED":
            xalign 0.5
            color _ur_accent
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(2, "#000000", 0, 0)]

        ## Big StS card centered. Same canonical renderer as everywhere else.
        fixed:
            xysize (400, 580)
            xalign 0.5
            use battle_card_view(cid=plus_id, mode="inspect", playable=True)

    timer 1.0 action Return(True)


## ---------------------------------------------------------------------------
## Forced-card Toast — slides in from top-right ONLY for corruption cards
## (Rage / Compromise) jammed into the deck by grant_card. Voluntary grants
## no longer toast (the pick flow already showed the card).
## ---------------------------------------------------------------------------

transform _card_toast_anim:
    xalign 1.0 yalign 0.0 xoffset 480 yoffset 80
    on show:
        linear 0.35 xoffset -20
    on hide:
        linear 0.3 xoffset 480

screen card_acquired_toast(card):
    layer "screens"
    zorder 310

    python:
        ## Corruption variants override the color + header. These cards
        ## aren't "acquired" — they're forced on you. Rage by hatred,
        ## Compromise by losing fights.
        _ct_is_rage       = bool(card.get("is_rage"))
        _ct_is_compromise = bool(card.get("is_compromise"))
        if _ct_is_rage:
            _ct_color = "#ff3322"
            _ct_header = "† RAGE FORCED"
            _ct_bg = "#1a0a0aff"
        elif _ct_is_compromise:
            _ct_color = "#a09890"
            _ct_header = "× COMPROMISE LANDED"
            _ct_bg = "#0d0d0aff"
        else:
            _ct_color = card_type_color(card, "frame")
            _ct_header = "CARD ACQUIRED"
            _ct_bg = "#0d1018ff"

    frame at _card_toast_anim:
        padding (18, 14)
        background Frame(_ct_bg, 4, 4)

        vbox:
            spacing 5
            xmaximum 380

            hbox:
                spacing 10
                text "[[ {} ]".format(card.get("cost", 0)):
                    color _ct_color
                    size 18
                    bold True
                text _ct_header:
                    color _ct_color
                    size 14
                    bold True

            text "─────────────────────────":
                color "#222222"
                size 12

            text card.get("name", ""):
                color card_name_color(card, "#ffffff")
                size 18
                bold True

            text "{} · {}".format(card_visual_type(card), card.get("rarity", "").upper()):
                color "#888888"
                size 11

            text card.get("flavor", ""):
                color "#cccccc"
                size 12

    timer 3.0 action Hide("card_acquired_toast")


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
                text "◆":
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
    zorder 250

    ## Pre-compute accent color from ending type
    python:
        _ENDING_COLORS = {"perfect": "#ffdd00", "good": "#00ff41", "bittersweet": "#ffaa33", "difficult": "#ff6633", "neutral": "#8899bb", "burnout": "#cc7722", "secret": "#00ccff", "bad": "#cc3322"}
        _ec = _ENDING_COLORS.get(ending_type, "#ffffff")

    ## Drop the in-game HUD — the ending is a clean fullscreen.
    timer 0.01 action [Hide("stats_bar"), Hide("dossier_hud"), Hide("quick_menu")] repeat False

    add "#000000"
    ## Faint ending-tinted wash so the void isn't dead-flat black.
    add Solid(_ec + "0c")

    ## Ending-color hairlines top and bottom — the "this screen matters" frame
    ## the battle and reward screens wear.
    frame:
        xfill True
        yalign 0.0
        ysize 4
        background Frame(_ec, 0, 0)
    frame:
        xfill True
        yalign 1.0
        ysize 4
        background Frame(_ec, 0, 0)

    viewport:
        xfill True
        yfill True
        scrollbars "vertical"
        mousewheel True
        draggable True

        vbox:
            xfill True
            yminimum 1080
            spacing 0

            null height 70

            ## Ending-type badge
            frame:
                xalign 0.5
                padding (26, 9)
                background Frame(_ec + "1e", 4, 4)
                text "[ending_label]":
                    color _ec
                    size 15
                    bold True
                    xalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"

            null height 20

            ## Main title
            text "[ending_title]":
                color "#ffffff"
                size 56
                bold True
                xalign 0.5
                text_align 0.5
                font "fonts/RobotoMono-Regular.ttf"
                outlines [(3, "#000000", 0, 0)]

            null height 14

            ## Hairline divider
            frame:
                xalign 0.5
                xsize 440
                ysize 2
                background Frame(_ec + "55", 0, 0)

            null height 20

            ## Flavor line
            text "[ending_flavor]":
                color "#c8c8c8"
                size 18
                xalign 0.5
                text_align 0.5
                xmaximum 920
                font "fonts/RobotoMono-Regular.ttf"

            ## Score panel
            if score is not None:

                null height 36

                frame:
                    xalign 0.5
                    xsize 620
                    background Frame("#0c0c0cf2", 0, 0)
                    padding (46, 22)

                    vbox:
                        xfill True
                        spacing 10

                        ## Accent line
                        frame:
                            xfill True
                            ysize 3
                            background Frame(_ec, 0, 0)

                        null height 2

                        text "FINAL STATS":
                            color _ec
                            size 15
                            bold True
                            xalign 0.5
                            font "fonts/RobotoMono-Regular.ttf"

                        null height 2

                        if money is not None:
                            hbox:
                                xalign 0.5
                                xsize 500
                                text "MONEY SAVED":
                                    color "#888888"
                                    size 15
                                    xminimum 320
                                    font "fonts/RobotoMono-Regular.ttf"
                                text "[money] CZK":
                                    color "#ffffff"
                                    size 15
                                    bold True
                                    font "fonts/RobotoMono-Regular.ttf"

                        if coding is not None:
                            hbox:
                                xalign 0.5
                                xsize 500
                                text "CODING SKILL":
                                    color "#888888"
                                    size 15
                                    xminimum 320
                                    font "fonts/RobotoMono-Regular.ttf"
                                text "[coding] pts":
                                    color _ec
                                    size 15
                                    bold True
                                    font "fonts/RobotoMono-Regular.ttf"

                        if diff_name is not None:
                            hbox:
                                xalign 0.5
                                xsize 500
                                text "DIFFICULTY":
                                    color "#888888"
                                    size 15
                                    xminimum 320
                                    font "fonts/RobotoMono-Regular.ttf"
                                text "[diff_name]":
                                    color "#ffdd00"
                                    size 15
                                    bold True
                                    font "fonts/RobotoMono-Regular.ttf"

                        ## Run recap + the score chase — the "one more run" hook.
                        ## best_score is still the PRIOR best here (the record is
                        ## written after this screen), so > means a genuine new best.
                        python:
                            _rs_deck = len(player_deck.cards) if (player_deck is not None) else None
                            _rs_relics = len(getattr(store, "player_relics", None) or [])
                            _rs_prev_best = persistent.best_score or 0
                            _rs_is_win = ending_type in ("perfect", "good", "secret")
                            _rs_new_best = bool(_rs_is_win and score is not None and score > _rs_prev_best)

                        if _rs_deck is not None:
                            hbox:
                                xalign 0.5
                                xsize 500
                                text "DECK / RELICS":
                                    color "#888888"
                                    size 15
                                    xminimum 320
                                    font "fonts/RobotoMono-Regular.ttf"
                                text "[_rs_deck] cards  ·  [_rs_relics] relics":
                                    color "#ffffff"
                                    size 15
                                    bold True
                                    font "fonts/RobotoMono-Regular.ttf"

                        if _rs_is_win or _rs_prev_best > 0:
                            hbox:
                                xalign 0.5
                                xsize 500
                                text "BEST SCORE":
                                    color "#888888"
                                    size 15
                                    xminimum 320
                                    font "fonts/RobotoMono-Regular.ttf"
                                text ("◆ NEW BEST!" if _rs_new_best else "[_rs_prev_best]"):
                                    color ("#ffdd00" if _rs_new_best else "#ffffff")
                                    size 15
                                    bold True
                                    font "fonts/RobotoMono-Regular.ttf"

                        null height 5

                        frame:
                            xfill True
                            ysize 1
                            background Frame("#2a2a2a", 0, 0)

                        if score_note is not None:
                            text "[score_note]":
                                color "#666666"
                                size 12
                                xalign 0.5
                                font "fonts/RobotoMono-Regular.ttf"

                        null height 2

                        text "FINAL SCORE":
                            color "#888888"
                            size 13
                            bold True
                            xalign 0.5
                            font "fonts/RobotoMono-Regular.ttf"

                        text "[score]":
                            color _ec
                            size 54
                            bold True
                            xalign 0.5
                            font "fonts/RobotoMono-Regular.ttf"
                            outlines [(3, "#000000", 0, 0)]

            null height 44

            ## Credits
            frame:
                xalign 0.5
                xsize 280
                ysize 1
                background Frame("#2a2a2a", 0, 0)

            null height 16

            text "THANK YOU FOR PLAYING":
                color "#999999"
                size 13
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"

            null height 6

            text "REFACTOR":
                color "#ffffff"
                size 30
                bold True
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"
                outlines [(2, "#000000", 0, 0)]

            null height 10

            text "'Code your way out, or lose your mind trying.'":
                color "#bbbbbb"
                size 13
                italic True
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"

            text "— Jakub Barák":
                color "#888888"
                size 12
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"

            null height 38

            ## Return button — Return() (not MainMenu()) so the calling
            ## ending label keeps control. good_ending uses this to play the
            ## post-credit scene between the score card and the restart.
            textbutton "[[ RETURN TO MAIN MENU ]":
                xalign 0.5
                action Return()
                text_color _ec
                text_size 18
                text_bold True
                text_hover_color "#ffffff"
                text_font "fonts/RobotoMono-Regular.ttf"
                background Frame("#0c0c0cf2", 4, 4)
                hover_background Frame(_ec + "28", 4, 4)
                padding (32, 15)

            null height 70


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
## Class Selection Screen
## Usage: call screen class_selection_screen
## Returns via SetVariable("stats.player_class", "bodybuilder") etc.
## ---------------------------------------------------------------------------
## ---------------------------------------------------------------------------
## Difficulty Selection Screen — full-bleed triptych (matches class selection)
## ---------------------------------------------------------------------------
## Difficulty data — drives the selection screen and init_game(). `crop` is the
## (x, y, w, h) window cut from the source png before it's scaled to fill a
## 640x1080 column (sources are ~843x1264; 749px wide matches the column's
## aspect, x centres the subject).
## ---------------------------------------------------------------------------

init python:
    DIFF_DATA = [
        {
            "key":     "easy",
            "year":    "2022",
            "title":   "JUST LEARN TO CODE BRO",
            "flavor":  "You googled 'how to become a developer in 30 days' and actually believed it.",
            "money":   "50,000",
            "coding":  "25",
            "hatred":  "10",
            "portrait": "images/pictures/easy_difficulty_pic.png",
            "crop":    (49, 0, 749, 1264),
            "color":   "#66cc66",
        },
        {
            "key":     "hard",
            "year":    "2025",
            "title":   "AI MASS LAYOFFS",
            "flavor":  "Your CV has a gap. Your wallet has a bigger one.",
            "money":   "30,000",
            "coding":  "10",
            "hatred":  "20",
            "portrait": "images/pictures/hard_difficulty_pic.png",
            "crop":    (49, 0, 749, 1264),
            "color":   "#ffaa33",
        },
        {
            "key":     "insane",
            "year":    "2026",
            "title":   "THANK YOU FOR YOUR APPLICATION",
            "flavor":  "IS ANYBODY OUT THERE???",
            "money":   "20,000",
            "coding":  "0",
            "hatred":  "30",
            "portrait": "images/pictures/insane_difficulty_pic.png",
            "crop":    (49, 0, 749, 1264),
            "color":   "#ff4444",
        },
    ]
    DIFF_COL_W = 640   # 1920 / 3
    DIFF_TITLE_H = 64  # full-width question band along the top

## ---------------------------------------------------------------------------
## Difficulty Selection Screen — triptych. One full-bleed column per
## difficulty, escalating left→right. Reuses the class-selection transforms
## (_classcol_enter / _classcol_hero / _select_pulse) so the two screens read
## as one set.
## ---------------------------------------------------------------------------

screen difficulty_selection_screen():
    modal True
    zorder 500

    add "#050505"

    ## --- The three columns ---
    for _i, _diff in enumerate(DIFF_DATA):
        $ _accent = _diff["color"]
        $ _x      = _i * DIFF_COL_W
        ## Plain strings for the text widgets — dict lookups inside displayed
        ## text are a known crash (see memory: dict interpolation).
        $ _money_line  = "💸 Money   " + _diff["money"] + " CZK"
        $ _coding_line = "💻 Coding  " + _diff["coding"]
        $ _hatred_line = "🤬 Hatred  " + _diff["hatred"]
        $ _flavor_line = "\"" + _diff["flavor"] + "\""

        button:
            xpos _x
            ypos 0
            xsize DIFF_COL_W
            ysize 1080
            background "#00000000"
            ## Kill the default 6px button borders (gui.button_borders) —
            ## they inset the whole column's content, leaving a dead strip
            ## of background along the column's left/top edge.
            padding (0, 0)
            action [SetField(store, "_chosen_difficulty", _diff["key"]), Return()]

            fixed:
                ## Outer fixed: whole-column fade-up on entry; overlays stay
                ## crisp — only the portrait layer gets the hover treatment.
                at _classcol_enter

                ## --- Portrait layer (zooms + brightens on hover). The
                ## viewport clips the hover zoom to the column, so it can't
                ## bleed over the separators into a neighbouring column. ---
                viewport:
                    xysize (DIFF_COL_W, 1080)
                    fixed:
                        at _classcol_hero
                        add _diff["portrait"]:
                            crop _diff["crop"]
                            xysize (DIFF_COL_W, 1080)

                ## Bottom info. The identity plate lives down here (not over
                ## the upper portrait like the class screen) because these
                ## sources have almost no headroom — anything up top covers
                ## the hair. Identity (year + tagline + flavor) sits left,
                ## the stats block sits against the right edge, both
                ## bottom-aligned on the same line above the SELECT pill.

                ## Year + tagline + flavor (bottom-left)
                frame:
                    xpos 32
                    yalign 1.0
                    yoffset -96
                    background "#0b0b0bf0"
                    padding (14, 10)
                    xmaximum 314
                    vbox:
                        spacing 4
                        text _diff["year"]:
                            color _accent
                            size 44
                            bold True
                            font "fonts/RobotoMono-Regular.ttf"
                        text _diff["title"]:
                            color "#ffffff"
                            size 19
                            bold True
                            font "fonts/RobotoMono-Regular.ttf"
                        text _flavor_line:
                            color "#e2e2e2"
                            size 16
                            italic True
                            xmaximum 286
                            font "fonts/RobotoMono-Regular.ttf"

                ## Stats block (bottom-right)
                frame:
                    xanchor 1.0
                    xpos (DIFF_COL_W - 32)
                    yalign 1.0
                    yoffset -96
                    background "#0b0b0bf0"
                    padding (14, 10)
                    vbox:
                        spacing 6
                        text _money_line:
                            color "#C8A44E"
                            size 19
                            font "fonts/RobotoMono-Regular.ttf"
                        text _coding_line:
                            color "#4EC8C6"
                            size 19
                            font "fonts/RobotoMono-Regular.ttf"
                        text _hatred_line:
                            color "#DA4621"
                            size 19
                            font "fonts/RobotoMono-Regular.ttf"

                ## SELECT pill — accent-bordered, breathing, same as the
                ## class screen's affordance.
                frame:
                    xpos 32
                    yalign 1.0
                    yoffset -32
                    background (_accent + "cc")
                    padding (2, 2)
                    at _select_pulse
                    frame:
                        background "#0c0c0cdd"
                        padding (22, 11)
                        text ">  SELECT":
                            color _accent
                            size 24
                            bold True
                            outlines [(1, "#000000", 0, 0)]
                            font "fonts/RobotoMono-Regular.ttf"

    ## --- Full-width question band along the top (over all columns) ---
    frame:
        xpos 0
        ypos 0
        xsize 1920
        ysize DIFF_TITLE_H
        background "#0a0a0aee"
        text "WHAT IS THE JOB MARKET SITUATION?":
            align (0.5, 0.5)
            color "#cc2200"
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"
    ## Per-difficulty accent bars — drawn after the band so they can sit on
    ## top of it (4px above the band's bottom edge); anything drawn inside
    ## the columns would be hidden behind the band's near-opaque background.
    for _i, _diff in enumerate(DIFF_DATA):
        add Solid(_diff["color"]):
            at _classcol_enter
            xpos (_i * DIFF_COL_W)
            ypos (DIFF_TITLE_H - 4)
            xysize (DIFF_COL_W, 6)

    ## Keyboard nav is Ren'Py's built-in button focus: Left/Right move focus
    ## between the columns, Enter activates the focused one — same path as a
    ## click. (Matches the class screen; no explicit `key` handlers, which
    ## would double-dispatch against the focused button's own activation.)


## Class display data — order + portrait + flavor. Triptych layout: one
## full-bleed column per class. The playable column (BB) stays crisp + bright;
## DE/BH are locked previews — blurred + dimmed, lightening a touch on their
## own hover. Not selectable.
init python:
    CLASS_SELECT_ORDER = ["bodybuilder", "dark_empath", "biohacker"]
    LOCKED_CLASSES = {"dark_empath"}
    CLASS_PORTRAITS = {
        "bodybuilder": "images/sprites/jb_bodybuilder.jpg",
        "dark_empath": "images/sprites/jb_dark_empath.jpg",
        "biohacker":   "images/sprites/jb_biohacker.jpg",
    }
    ## Crop rect (x, y, w, h) applied to each source jpg before it's scaled to
    ## fill a column. Source images are 1264px tall; a column is 640x1080 → the
    ## crop window is 749px wide. x is biased toward the right edge of the source
    ## so the subject sits a touch left of centre in the column (looked shoved
    ## right with a plain cover-fit, which anchors the crop top-left).
    CLASS_CROP = {
        "bodybuilder": (50, 0, 749, 1264),
        "dark_empath": (70, 0, 749, 1264),
        "biohacker":   (75, -50, 749, 1264),
    }
    CLASS_HOVER_SFX = {
        "bodybuilder": "audio/sfx/gym_plates.mp3",
        "dark_empath": "audio/sfx/dark_empath_whispers.mp3",
        "biohacker":   "audio/sfx/biohacker_lab.mp3",
    }
    ## Brief flavor lines. The playable class (BB) also shows one perk-flavored
    ## identity line (CLASS_IDENTITY) under the name; the locked previews fall
    ## back to these. Full perks/decks/trades stay cut from this screen by design.
    CLASS_FLAVOR = {
        "bodybuilder": "Hatred is fuel. Words bounce off muscle.",
        "dark_empath": "The Colonel is a function with predictable inputs.",
        "biohacker":   "BPM 58, HRV 84, cortisol low — ready for action.",
    }
    CLASS_IDENTITY = {
        "bodybuilder": "Hatred is your fuel. Words bounce off muscle.",
        "biohacker":   "BPM 58, HRV 84, cortisol low — ready for action.",
    }
    CLASS_COL_W = 640   # 1920 / 3

    def _class_select_action(idx):
        """Click/Enter action for class column `idx`: commit it if playable,
        else fire the locked-column 'denied' feedback (recoil pulse + flash
        message, both driven off the `_denied` screen var)."""
        k = CLASS_SELECT_ORDER[idx]
        if k in LOCKED_CLASSES:
            return SetScreenVariable("_denied", idx)
        return [SetField(stats, "player_class", k), Return()]


## Per-column focus transforms — these wrap only the PORTRAIT layer. The
## overlays (accent bar, name plate, bottom scrim, stamp/pill) sit *outside*
## this, so they stay crisp + full-brightness no matter what's focused.
##
## _classcol_hero — playable class columns (BB, BH). Crisp + full-brightness
## by default. Hover bumps brightness slightly and adds a tiny zoom so the
## player can SEE which column the cursor is over without breaking the
## "this column owns the screen" feel. Keep the change small — anything more
## than ~3% zoom pokes past the bottom scrim.
transform _classcol_hero:
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    zoom 1.0
    matrixcolor BrightnessMatrix(0.0)
    on hover:
        ease 0.18 zoom 1.025 matrixcolor BrightnessMatrix(0.08)
    on idle:
        ease 0.18 zoom 1.0 matrixcolor BrightnessMatrix(0.0)

## _classcol_locked_idle — DE / BH previews. Heavily blurred + dimmed at rest;
## hovering un-blurs them just enough to read as a teaser, but they stay dim
## (and the portrait keeps an image-level desaturation) so they never compete
## with BB. Bare ATL == `on idle` target → no entry flicker. No zoom, so the
## portrait can never poke past its column / the scrim either.
transform _classcol_locked_idle:
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    blur 11.0
    matrixcolor BrightnessMatrix(-0.45)
    on hover:
        ease 0.25 blur 1.5 matrixcolor BrightnessMatrix(-0.25)
    on idle:
        ease 0.25 blur 11.0 matrixcolor BrightnessMatrix(-0.45)

## Whole-column fade-up on screen entry (composed onto each column's outer
## fixed). No `on` handlers, so the button's focus events pass straight through
## to the portrait transform without disturbing the fade.
transform _classcol_enter:
    alpha 0.0
    linear 0.40 alpha 1.0

## Gentle breathing on the SELECT pill so the eye finds the click target.
transform _select_pulse:
    alpha 1.0
    easein 0.9 alpha 0.6
    easeout 0.9 alpha 1.0
    repeat

## Locked-column recoil — applied to the clicked column's LOCKED stamp.
transform _deny_pulse:
    zoom 1.0
    easeout 0.10 zoom 1.16
    easein 0.22 zoom 1.0

## No-op transform — the `else` branch of a conditional `at` (Ren'Py needs a
## real transform there, not None).
transform _xf_none:
    alpha 1.0

## "that one's locked" flash message — fade in, hold, fade out (~1.15s).
transform _deny_msg:
    alpha 0.0
    linear 0.15 alpha 1.0
    pause 0.70
    linear 0.30 alpha 0.0


screen class_selection_screen():
    modal True
    zorder 500

    ## Which column the keyboard / last hover is "on" (0 = BB). Drives the
    ## locked-column sub-text and the Enter-to-commit target.
    default _focus  = 0
    ## A locked column the player just tried to take (-1 = none). A timer
    ## clears it; while set it drives the recoil pulse + the flash message.
    default _denied = -1

    add "#050505"

    ## --- The three columns ---
    for _i, _cls_key in enumerate(CLASS_SELECT_ORDER):
        $ _cd     = CLASS_DATA[_cls_key]
        $ _accent = _cd["color"]
        $ _locked = _cls_key in LOCKED_CLASSES
        $ _x      = _i * CLASS_COL_W
        $ _hsfx   = CLASS_HOVER_SFX.get(_cls_key)
        $ _idline = (CLASS_IDENTITY.get(_cls_key) or CLASS_FLAVOR[_cls_key])

        button:
            xpos _x
            ypos 0
            xsize CLASS_COL_W
            ysize 1080
            background "#00000000"
            action _class_select_action(_i)
            hovered [SetScreenVariable("_focus", _i), (Play("sound", _hsfx) if _hsfx else NullAction())]

            fixed:
                ## Outer fixed: just fades the whole column up on entry. The
                ## overlays below it stay un-blurred / full-brightness — only
                ## the inner portrait layer gets the blur/dim/zoom treatment.
                at _classcol_enter

                ## --- Portrait layer (the only thing that blurs + dims) ---
                fixed:
                    at (_classcol_hero if not _locked else _classcol_locked_idle)
                    ## Full-bleed portrait — source jpg cropped to the column's
                    ## aspect (see CLASS_CROP), scaled to fill. Locked portraits
                    ## also carry an image-level desaturation so they read as a
                    ## ghost preview even when hovered.
                    add CLASS_PORTRAITS[_cls_key]:
                        crop CLASS_CROP[_cls_key]
                        xysize (CLASS_COL_W, 1080)
                        matrixcolor (SaturationMatrix(0.18) * BrightnessMatrix(-0.05) if _locked else IdentityMatrix())

                ## --- Overlays (crisp, full brightness) ---

                ## Top accent bar
                add Solid(_accent if not _locked else "#666666"):
                    xysize (CLASS_COL_W, 6)

                ## Class name — centred on a scrim band over the upper portrait.
                ## the top accent bar and out of the portrait's face area.
                frame:
                    xfill True
                    ypos 40
                    background "#000000aa"
                    padding (0, 14)
                    text _cd["name"]:
                        xalign 0.5
                        color (_accent if not _locked else "#888888")
                        size 36
                        bold True
                        outlines [(2, "#000000", 0, 0)]
                        font "fonts/RobotoMono-Regular.ttf"

                ## No bottom scrim — the portrait stays fully visible. The bits
                ## of text/UI below each carry their own tight backing so they
                ## read on a bright portrait without darkening it.

                ## Bottom info: one identity line → SELECT pill / LOCKED stamp.
                ## (The class name is in the plate up top, over the portrait.)
                vbox:
                    xpos 32
                    yalign 1.0
                    yoffset -32
                    spacing 14
                    xmaximum (CLASS_COL_W - 56)

                    frame:
                        background "#0b0b0bba"
                        padding (14, 8)
                        text _idline:
                            color ("#e2e2e2" if not _locked else "#a8a8a8")
                            size 18
                            italic True
                            xmaximum (CLASS_COL_W - 84)
                            font "fonts/RobotoMono-Regular.ttf"

                    if _locked:
                        ## LOCKED stamp — 2px border via a nested frame; recoils
                        ## (_deny_pulse) when this column was just clicked.
                        frame:
                            background "#5a3a3a"
                            padding (2, 2)
                            at (_deny_pulse if _denied == _i else _xf_none)
                            frame:
                                background "#0a0606ee"
                                padding (22, 10)
                                vbox:
                                    spacing 4
                                    text "LOCKED":
                                        color "#cccccc"
                                        size 25
                                        bold True
                                        font "fonts/RobotoMono-Regular.ttf"
                    else:
                        ## SELECT pill — the click affordance (the whole column
                        ## is the hit target; this just shows where to click).
                        ## Dark-backed + accent-bordered so it pops on the
                        ## un-scrimmed bright portrait.
                        frame:
                            background (_accent + "cc")
                            padding (2, 2)
                            at _select_pulse
                            frame:
                                background "#0c0c0cdd"
                                padding (22, 11)
                                text ">  SELECT":
                                    color _accent
                                    size 24
                                    bold True
                                    outlines [(1, "#000000", 0, 0)]
                                    font "fonts/RobotoMono-Regular.ttf"

    ## --- "that column is locked" flash + auto-clear. Sits over the upper
    ## portrait, below the name plates and clear of the bottom UI cluster. ---
    if _denied >= 0:
        $ _deny_name = CLASS_DATA[CLASS_SELECT_ORDER[_denied]]["name"]
        frame:
            xalign 0.5
            ypos 210
            background "#1a0606ee"
            padding (28, 12)
            at _deny_msg
            text "[_deny_name] is still in development — Select ANOTHER class.":
                color "#dd9d8c"
                size 16
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"
        timer 2.0 action SetScreenVariable("_denied", -1)

    ## Keyboard nav is Ren'Py's built-in button focus: Left/Right move focus
    ## between the three columns, Enter activates the focused one (same path as
    ## a click — its `action _class_select_action(_i)`). `hovered` fires on
    ## keyboard focus too, so it keeps `_focus` in sync and the `on hover`/
    ## `on idle` ATL events animate the portrait under keyboard nav as well.
    ## (No explicit `key` handlers — they'd double-dispatch against the focused
    ## button's own activation, and a locked column's no-Return action would
    ## then let the still-focused BB button commit by accident.)


style class_select_btn is button_text:
    color "#ffffff"
    size 16
    bold True


## ---------------------------------------------------------------------------
## Achievements list — render-only sub-screen used by trophies_menu (and
## reusable wherever else we want to surface trophies). Counts + grid only;
## caller supplies the container, header, and dismiss control.
## ---------------------------------------------------------------------------

screen _achievements_list():
    python:
        _unlocked = persistent.achievements_unlocked or set()
        _ach_total = len(ACHIEVEMENTS)
        _ach_count = len(_unlocked)
        _ach_categories = ["Story", "Combat", "Collection", "Secret"]
        _ach_by_cat = {c: [] for c in _ach_categories}
        for _k, _v in ACHIEVEMENTS.items():
            _cat = _v.get("category", "Story")
            _ach_by_cat.setdefault(_cat, []).append((_k, _v))
        _ach_cat_counts = {
            _c: (sum(1 for _k, _ in _items if _k in _unlocked), len(_items))
            for _c, _items in _ach_by_cat.items()
        }

    $ _FNT = "fonts/RobotoMono-Regular.ttf"
    $ _meta_wins = persistent.runs_won or 0
    $ _meta_best = persistent.best_score or 0
    $ _ach_frac  = (_ach_count / float(_ach_total)) if _ach_total else 0.0
    $ _bar_w = 480
    ## Full-width three-column grid: the whole wall fits without a long scroll.
    $ _GRID_W = 1712
    $ _COLS   = 3
    $ _CARD_W = 560

    vbox:
        spacing 16

        ## ── Header band: completion meter (left) + cross-run records (right) ──
        fixed:
            xysize (_GRID_W, 108)
            add Solid("#13100bf2")

            ## Completion: count + at-a-glance meter.
            vbox:
                xpos 26
                yalign 0.5
                spacing 8
                text "CASE FILE · COMMENDATIONS":
                    color "#8a7a58"
                    size 13
                    bold True
                    font _FNT
                hbox:
                    spacing 10
                    yalign 1.0
                    text "[_ach_count]":
                        color "#ffcc44"
                        size 42
                        bold True
                        font _FNT
                        outlines [(2, "#000000", 0, 0)]
                    text "/ [_ach_total] unlocked":
                        color "#8a8a8a"
                        size 17
                        yalign 1.0
                        yoffset -8
                        font _FNT
                fixed:
                    xysize (_bar_w, 8)
                    add Solid("#241d12") xysize (_bar_w, 8)
                    add Solid("#ffcc44") xysize (max(3, int(_bar_w * _ach_frac)), 8)

            ## Cross-run records — the persisted meta-progression chase.
            vbox:
                xpos (_GRID_W - 26)
                xanchor 1.0
                yalign 0.5
                spacing 12
                hbox:
                    xalign 1.0
                    spacing 10
                    text "RUNS WON":
                        color "#6a6055"
                        size 13
                        yalign 0.5
                        min_width 132
                        font _FNT
                    text "[_meta_wins]":
                        color "#cdbd97"
                        size 24
                        bold True
                        font _FNT
                hbox:
                    xalign 1.0
                    spacing 10
                    text "BEST SCORE":
                        color "#6a6055"
                        size 13
                        yalign 0.5
                        min_width 132
                        font _FNT
                    text "[_meta_best]":
                        color "#ffd700"
                        size 24
                        bold True
                        font _FNT

        ## ── Category sections ─────────────────────────────────────────────
        for _cat in _ach_categories:
            if _ach_by_cat.get(_cat):
                $ _cat_done, _cat_total = _ach_cat_counts.get(_cat, (0, 0))

                vbox:
                    spacing 10

                    ## Category header + divider rule.
                    hbox:
                        spacing 12
                        yalign 0.5
                        text "[_cat!u]":
                            color "#cc4422"
                            size 17
                            bold True
                            font _FNT
                        text "[_cat_done] / [_cat_total]":
                            color "#6a6055"
                            size 15
                            yalign 0.5
                            yoffset 1
                            font _FNT
                    add Solid("#2a1a14") xysize (_GRID_W, 2)

                    $ _entries = _ach_by_cat[_cat]
                    $ _rows = [_entries[_i:_i + _COLS] for _i in range(0, len(_entries), _COLS)]

                    for _row in _rows:
                        hbox:
                            spacing 16

                            for _entry in _row:
                                $ _ach_key, _ach_data = _entry
                                $ _is_unlocked = _ach_key in _unlocked
                                $ _is_secret   = _ach_data.get("category") == "Secret"
                                python:
                                    if _is_unlocked:
                                        _acc, _fbg, _glyph, _gc, _nc, _dc = "#ffcc44", "#16120af6", "✓", "#ffcc44", "#ffdd55", "#c8c0b0"
                                    elif _is_secret:
                                        _acc, _fbg, _glyph, _gc, _nc, _dc = "#3a1812", "#0c0a08f6", "?", "#7a3a2a", "#6a6a6a", "#4a4a4a"
                                    else:
                                        _acc, _fbg, _glyph, _gc, _nc, _dc = "#2a2620", "#0c0a08f6", "·", "#555555", "#8a8a8a", "#5a5a5a"
                                    ## Names always show (so every real trophy is visible on
                                    ## the wall); only a locked secret's criterion stays masked.
                                    _nm = _ach_data["name"]
                                    if _is_unlocked:
                                        _ds = _ach_data["desc"]
                                    elif _is_secret:
                                        _ds = "Classified — unlock to reveal."
                                    else:
                                        _ds = _ach_data.get("hint", "Locked.")
                                ## Accent-bordered card (gold = earned, pops off the bg).
                                frame:
                                    xsize _CARD_W
                                    background _acc
                                    padding (2, 2)
                                    frame:
                                        background _fbg
                                        padding (14, 11)
                                        xfill True
                                        hbox:
                                            spacing 13
                                            text _glyph:
                                                color _gc
                                                size 22
                                                bold True
                                                min_width 24
                                                yalign 0.0
                                                font _FNT
                                            vbox:
                                                spacing 3
                                                text _nm:
                                                    color _nc
                                                    size 16
                                                    bold True
                                                    font _FNT
                                                text _ds:
                                                    color _dc
                                                    size 13
                                                    italic (not _is_unlocked)
                                                    font _FNT
                                                    xmaximum 480

                            ## Keep column widths stable when a row is short.
                            for _i in range(_COLS - len(_row)):
                                frame:
                                    xsize _CARD_W
                                    background None


## ---------------------------------------------------------------------------
## Trophies Menu — dedicated full-screen wall (NOT routed through game_menu, so
## the content pins high under the title instead of dropping into game_menu's
## ~235px top band). Three-column grid means the whole roster fits with little
## or no scroll. Opened from the main menu and the in-game pause sidebar.
## ---------------------------------------------------------------------------

screen trophies_menu():
    tag menu
    modal True

    if main_menu:
        add gui.main_menu_background
    else:
        add Solid("#0a0a0af2")

    use dossier_top_bar(left_text="REFACTOR  //  case-file: trophies")
    use dossier_bottom_bar(right_text="[[esc] back")

    ## Title pinned high — the trophy wall starts right beneath it.
    add Solid("#cc2200"):
        xpos 72
        ypos 64
        xsize 4
        ysize 58
        at mm_fade_in

    text "TROPHIES":
        style "mm_title"
        size 60
        kerning 3
        xpos 90
        ypos 52
        at mm_fade_in

    ## Compact back control (mm_button forces xsize 560, so style it inline).
    textbutton _("◄  back"):
        xpos 1830
        xanchor 1.0
        ypos 64
        padding (12, 6)
        background None
        hover_background Frame("#1a0000dd", 8, 4)
        text_font "fonts/RobotoMono-Regular.ttf"
        text_size 26
        text_color "#9aa8b8"
        text_hover_color "#ff4422"
        action (ShowMenu("main_menu") if main_menu else Return())

    viewport:
        xpos 90
        ypos 150
        xsize 1760
        ysize 842
        scrollbars "vertical"
        mousewheel True
        draggable True
        pagekeys True
        side_yfill True
        at mm_fade_in

        use _achievements_list

    key "game_menu" action (ShowMenu("main_menu") if main_menu else Return())


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
transform _day_card_anim:
    alpha 0.0
    linear 0.3 alpha 1.0
    pause 1.6
    linear 0.6 alpha 0.0

screen day_transition_screen(day_num):
    modal True
    zorder 500

    add "#0d0d0d"

    vbox:
        xalign 0.5
        yalign 0.45
        spacing 16
        at _day_card_anim

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

    timer 2.6 action Return()


