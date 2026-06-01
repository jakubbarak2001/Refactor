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

        ## ═══ Main strip — content-sized, no longer full-bleed ═══
        frame:
            padding (16, 6)
            background Frame(DOSSIER_BG_BAR, 0, 0)

            hbox:
                spacing 14
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
                                text "Coding [stats.coding_skill]":
                                    color "#00ccff"
                                    size 15
                                    font DOSSIER_FONT
                        else:
                            text "Coding [stats.coding_skill]":
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

    vbox:
        xalign 0.5
        yalign 0.5
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

        ## ── Grid layout ───────────────────────────────────────────────────
        ## Six cards per row at hand-mode size (220×316). Row pitch leaves
        ## clearance for the cost-gem overhang (-12px above each card) so
        ## adjacent rows don't visually collide. Viewport 1600×880 fits
        ## 6×220 + 5×16 = 1400 wide with margin to spare; tall enough to
        ## show a full row + group header without scrolling on small decks.
        viewport:
            xsize 1600
            ysize 880
            scrollbars "vertical"
            mousewheel True
            draggable True

            vbox:
                spacing 24

                for _grp in CARD_VISUAL_TYPES:
                    if _deck_by_group.get(_grp):
                        $ _grp_hex = TYPE_PALETTE.get(_grp, {}).get("frame", "#888888")
                        $ _grp_cards = _deck_by_group[_grp]

                        ## Group header — type label, color-coded, with count.
                        ## xoffset matches the row offset below so the header
                        ## color bar lines up with the first card's left edge.
                        hbox:
                            spacing 12
                            yalign 0.5
                            xoffset 28
                            ## Color bar to the left of the label gives the
                            ## header weight and matches the card frames below.
                            frame:
                                ysize 22
                                xsize 8
                                background Frame(_grp_hex, 0, 0)
                            text "{} ({})".format(_grp.upper(), len(_grp_cards)):
                                color _grp_hex
                                size 22
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"
                                outlines [(1, "#000000", 0, 0)]

                        ## Six cards per row, full StS card visuals via the
                        ## canonical battle_card_view renderer. xoffset 28
                        ## reserves room for the cost-gem overhang on the
                        ## leftmost card in each row (gem hangs xpos -22
                        ## from the card frame; without the shift the row's
                        ## first gem gets clipped at the viewport edge).
                        $ _rows = [_grp_cards[i:i+6] for i in range(0, len(_grp_cards), 6)]
                        vbox:
                            spacing 28
                            xoffset 28
                            for _row in _rows:
                                hbox:
                                    spacing 16
                                    for _cid in _row:
                                        fixed:
                                            xysize (220, 320)
                                            use battle_card_view(cid=_cid, mode="hand", playable=True)

                if not _deck_cards:
                    text "Your deck is empty.\nDo activities, attend events, or talk to Martin to collect cards.":
                        color "#666666"
                        size 16
                        italic True
                        xalign 0.5
                        text_align 0.5

        textbutton "[[ CLOSE ]":
            xalign 0.5
            ## Hide self — the Dossier HUD strip (zorder 100) renders above
            ## this modal anyway, so no other layer needs restoring. No
            ## Return() — Return is what triggered the "back to main menu"
            ## bug when called outside a label.
            action Hide("deck_viewer")
            text_style "class_select_btn"
            background "#220000"
            hover_background "#440000"
            padding (20, 10)


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
## Smaller scale than reward cards because tiles are bigger and the row
## of four shouldn't shove around dramatically.
transform activity_hover_lift:
    on hover:
        ease 0.15 zoom 1.04 yoffset -12
    on idle:
        ease 0.15 zoom 1.0 yoffset 0

## Default glyph per activity title — keeps the icon zone meaningful without
## requiring every call site to pass an art_glyph. Falls through to ★.
default _ACT_DEFAULT_GLYPHS = {
    "GYM": "🏋",
    "COLD READ": "◊",
    "RECOVERY": "❋",
    "BOUNCER": "$",
    "CODING": "</>",
    "OVERTIME": "◐",
    "PHONE": "☏",
    "SLEEP": "☾",
    "REST": "❋",
    "VISIT FIXER": "✂",
}

screen _activity_tile(label_name, title, accent, cost_text, effect_text="", effect_chips=None, locked=False, lock_text="", class_relevant=False, flavor_text="", art_glyph="", cost_unaffordable=False, stat_lines=None):
    ## Layered construction mirrors the StS card render:
    ##   L2: drop shadow
    ##   L3: accent-colored border
    ##   L4: warm-dark inner panel (#1a1410)
    ##   L5: zoned content (title banner → underline → glyph zone → cost → chips → flavor)
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
        _at_glyph = art_glyph or _ACT_DEFAULT_GLYPHS.get(title, "★")
        ## Cost line color — red preempts the click when funds are short.
        if locked:
            _at_cost_color = "#3a3a3a"
        elif cost_unaffordable:
            _at_cost_color = "#ff4444"
        else:
            _at_cost_color = "#ffd700"

    button:
        xsize 340
        ysize 320
        background None
        hover_background None
        sensitive (not locked)
        action Jump(label_name)
        at activity_hover_lift

        ## L2: drop shadow
        add Solid("#00000099") xpos 22 ypos 22 xysize (320, 280)

        ## L3 + L4: accent border wrapping warm-dark inner panel.
        frame:
            xpos 10
            ypos 10
            xsize 320
            ysize 280
            background Frame(_at_border_color, 6, 6)
            padding (6, 6)

            frame:
                xfill True
                yfill True
                background Frame("#1a1410", 4, 4)
                padding (10, 8)

                vbox:
                    xfill True
                    spacing 5

                    ## TITLE BANNER — gold on dark ribbon
                    frame:
                        xfill True
                        ysize 38
                        background Frame("#0a0806", 4, 4)
                        text title:
                            color _at_title_color
                            size 22
                            bold True
                            xalign 0.5
                            yalign 0.5
                            xmaximum 280
                            text_align 0.5
                            font "fonts/RobotoMono-Regular.ttf"

                    ## CLASS-RELEVANT UNDERLINE — 2px gold hairline. Visual
                    ## cue beyond the title color that this tile is the one
                    ## the current class is built around.
                    if class_relevant and not locked:
                        frame:
                            xfill True
                            ysize 2
                            background Frame("#e8c878", 0, 0)

                    ## GLYPH ZONE — accent-tinted backdrop with a large symbol.
                    frame:
                        xfill True
                        ysize 64
                        background Frame(accent + "22", 4, 4)
                        text _at_glyph:
                            xalign 0.5
                            yalign 0.5
                            size 38
                            color _at_glyph_color
                            bold True
                            outlines [(2, "#000000", 0, 0)]

                    ## COST — only render when the activity actually costs
                    ## something. FREE is the default and carries no info, so
                    ## suppressing it lets the outcome chips below be the
                    ## visual headline (was the #1 playtest complaint: the
                    ## big bold FREE made players miss the real outcomes).
                    if cost_text and cost_text != "FREE":
                        text cost_text:
                            color _at_cost_color
                            size 16
                            bold True
                            xalign 0.5
                            font "fonts/RobotoMono-Regular.ttf"

                    ## EFFECT chips DELIBERATELY NOT RENDERED. The previous
                    ## XCOM-style "+ HP", "+/-", "?", "+ Card", "+5,000 CZK"
                    ## pill row felt clinical and dated. Modern hybrids
                    ## (StS, Hades) lean on prose + icons. Outcome is
                    ## carried by `flavor_text` below; cost is carried by
                    ## `cost_text` above. `effect_chips` / `effect_text`
                    ## parameters are kept on the signature so existing
                    ## call sites don't break, but they no longer render.

                    ## STAT LINES — structured per-stat readout. Pass
                    ## stat_lines=[(label, value), ...] in the option dict
                    ## when the tile should show explicit stat deltas
                    ## instead of prose flavor. Used by Recovery so each
                    ## modality shows BATTLE BONUS / HP / HATRED on its
                    ## own line. Value polarity drives color: HP+ green,
                    ## HP- red, HATRED- green (relief), HATRED+ red.
                    null height 4
                    if locked and lock_text:
                        text lock_text:
                            color "#554434"
                            size 11
                            italic True
                            xalign 0.5
                            text_align 0.5
                            xmaximum 280
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
                            size 13
                            italic True
                            xalign 0.5
                            yalign 0.5
                            text_align 0.5
                            xmaximum 280
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
    ## can't overlap the cards (it used to: title was top-pinned, grid was
    ## yalign 0.5 → on a 4-tile 2x2 the grid climbed into the subtitle).
    python:
        _opts_visible = [o for o in options if o.get("visible", True)]
        ## 4 options → 2x2 (symmetric). Anything else → 3-wide.
        _per_row = 2 if len(_opts_visible) == 4 else 3
        _rows = [_opts_visible[i:i + _per_row] for i in range(0, len(_opts_visible), _per_row)]

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
                    spacing 28
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
        ypos 270
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

    ## Tile row — 4 tiles in a single row. Slot 1 is the class-locked relief
    ## activity (only that class sees that tile). Slots 2-4 are universal.
    hbox:
        xalign 0.5
        yalign 0.5
        spacing 28

        ## Slot 1 - CLASS-LOCKED relief activity. Each class sees only their own.
        if _is_bb:
            use _activity_tile(
                label_name        = "activity_gym",
                title             = "GYM",
                accent            = class_accent_color("bodybuilder"),
                cost_text         = "FREE",
                effect_chips      = [("Upgrade", "Upgrade a card"), ("Card", "or Heal + Max HP")],
                flavor_text       = "An hour where the bar tells the truth.",
                class_relevant    = True,
            )
        elif _is_de:
            use _activity_tile(
                label_name     = "activity_cold_read",
                title          = "COLD READ",
                accent         = class_accent_color("dark_empath"),
                cost_text      = "FREE",
                effect_chips   = [("Hatred", -20)],
                flavor_text    = "Regular for the card. Deep for the profile.",
                class_relevant = True,
            )
        elif _is_bh:
            use _activity_tile(
                label_name     = "activity_recovery",
                title          = "RECOVERY",
                accent         = class_accent_color("biohacker"),
                cost_text      = "FREE",
                effect_chips   = [("HP", "+ HP"), ("?", "+/- ?")],
                flavor_text    = "Sauna, meditation, cold plunge, red light — today the body picks.",
                class_relevant = True,
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
                effect_chips   = [("Coding", "+ Coding"), ("Card", "+ Card")],
                flavor_text    = "Three tiers + Research PubMed. Build the stack, build the deck.",
                class_relevant = True,
            )
        else:
            use _activity_tile(
                label_name     = "activity_bouncer",
                title          = "BOUNCER",
                accent         = "#ffd700",
                cost_text      = "FREE",
                effect_chips   = [("CZK", "+ CZK"), ("Hatred", "+ Hatred")],
                flavor_text    = "Moonlighting pays well, but it's dangerous for cops.",
                class_relevant = False,
            )

        ## CODING - everyone needs to learn the trade.
        use _activity_tile(
            label_name     = "activity_coding",
            title          = "CODING",
            accent         = "#00ccff",
            cost_text      = "FREE",
            effect_chips   = [("Card", "+ Card")],
            flavor_text    = "Study sessions. The keyboard pays in cards.",
            class_relevant = False,
        )

        ## OVERTIME - shared money + hatred trade.
        use _activity_tile(
            label_name     = "activity_overtime",
            title          = "OVERTIME",
            accent         = "#3388cc",
            cost_text      = "FREE",
            effect_chips   = [("CZK", +5000), ("Hatred", +15)],
            flavor_text    = "Trade time for money.",
            class_relevant = False,
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

    ## ── Sidebar — FIXER (day 10+; one shred per day; free time, doesn't
    ## burn your daily activity). Dimmed and disabled after today's shred.
    if _today >= 10:
        $ _fixer_done = bool(getattr(store, '_fixer_shredded_today', False))
        frame:
            xpos 1700
            ypos 240
            xsize 200
            padding (14, 14)
            background Frame("#0a0a0aee", 4, 4)

            vbox:
                spacing 8
                xfill True

                textbutton ("FIXER · DONE" if _fixer_done else "✂  FIXER"):
                    xalign 0.5
                    action Jump("activity_fixer")
                    sensitive (not _fixer_done)
                    text_color ("#5a5550" if _fixer_done else "#9a8060")
                    text_hover_color "#ffffff"
                    text_size 18
                    text_bold True
                    text_font "fonts/RobotoMono-Regular.ttf"
                    background "#00000000"
                    hover_background Frame("#1a1410dd", 3, 3)
                    padding (10, 8)
                    xfill True

                text ("He's done for the day." if _fixer_done else "Shred a card. Free time."):
                    xalign 0.5
                    color "#888888"
                    size 12
                    italic True
                    font "fonts/RobotoMono-Regular.ttf"

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

screen fixer_removal_screen(entries, price, next_price):
    modal True
    zorder 700

    add "#0a0a0aee"

    use class_color_frame(thickness=3, alpha_suffix="aa")

    python:
        _CORRUPTION_COLOR = {
            "rage":       "#aa1a1a",
            "compromise": "#5a5550",
            "status":     "#8a7a2a",
        }
        _CORRUPTION_GLYPH = {
            "rage":       "🔥 ",
            "compromise": "🚫 ",
            "status":     "☠ ",
        }
        _f_affordable = (stats.available_money >= price)
        _f_price_color = ("#ffd700" if _f_affordable else "#a04040")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14

        text "FIXER · RUN A CARD THROUGH THE SHREDDER":
            xalign 0.5
            color "#9a8060"
            size 36
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(2, "#000000", 0, 0)]

        text "He doesn't take cards. He shreds them. Pick what disappears.":
            xalign 0.5
            color "#888888"
            size 15
            italic True
            font "fonts/RobotoMono-Regular.ttf"

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

        viewport:
            xsize 1100
            ysize 580
            scrollbars "vertical"
            mousewheel True
            draggable True

            vbox:
                spacing 6

                for _fcid in entries:
                    python:
                        _fc    = CARD_LIBRARY.get(_fcid, {})
                        _fname = _fc.get("name", _fcid)
                        _ftype = _fc.get("type", "Skill")
                        _frar  = _fc.get("rarity", "common")
                        ## Classify corruption category for visual prefix.
                        if _fc.get("is_rage"):
                            _fcorr = "rage"
                        elif _fc.get("is_compromise"):
                            _fcorr = "compromise"
                        elif (_fc.get("effect") or "").startswith("status_"):
                            _fcorr = "status"
                        else:
                            _fcorr = None
                        _fglyph = _CORRUPTION_GLYPH.get(_fcorr, "")
                        _fcol   = _CORRUPTION_COLOR.get(_fcorr) or {"Attack": "#cc4422", "Skill": "#3388cc", "Power": "#aa44cc"}.get(_ftype, "#888888")

                    frame:
                        xsize 1080
                        ysize 56
                        background Frame("#0d0d0dee", 3, 3)
                        padding (14, 6)

                        hbox:
                            spacing 18
                            yalign 0.5

                            ## Cost gem
                            text "[[ [_fc.get('cost', 0)] ]":
                                color _fcol
                                size 18
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"
                                xsize 60

                            ## Name with corruption prefix. Upgraded cards
                            ## (not corruption — register_upgrade refuses
                            ## status/rage/compromise) render the name green
                            ## so the shred decision sees "you'd be paying
                            ## to nuke an upgrade" at a glance.
                            text "[_fglyph][_fname]":
                                color card_name_color(_fc, "#ffffff")
                                size 18
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"
                                xsize 420

                            ## Type · rarity
                            text "[_ftype.upper()] · [_frar.upper()]":
                                color "#888888"
                                size 13
                                font "fonts/RobotoMono-Regular.ttf"
                                xsize 360

                            ## SHRED button
                            textbutton "[[ SHRED ]":
                                sensitive _f_affordable
                                action Return(("remove", _fcid))
                                text_color ("#ff8866" if _f_affordable else "#553333")
                                text_hover_color "#ffaa88"
                                text_size 16
                                text_bold True
                                text_font "fonts/RobotoMono-Regular.ttf"
                                background Frame("#1a0d0dee" if _f_affordable else "#0d0d0dee", 3, 3)
                                hover_background Frame("#3a1a1aee", 3, 3)
                                padding (16, 6)

        textbutton "[[ ← LEAVE — no time lost ]":
            xalign 0.5
            action Return(("leave", None))
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 18
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#0d0d0dee", 3, 3)
            hover_background Frame("#1a1a1aee", 3, 3)
            padding (24, 10)

    key "K_ESCAPE" action Return(("leave", None))


## ---------------------------------------------------------------------------
## Fixer shop — BUY A CARD. offers = [{card_id, price}]. Returns a card_id to
## buy, or "back". Unaffordable rows render dim and are not clickable.
## ---------------------------------------------------------------------------
screen fixer_card_buy_screen(offers, cash):
    modal True
    zorder 700

    add "#0a0a0aee"
    use class_color_frame(thickness=3, alpha_suffix="aa")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14

        text "FIXER · BUY A CARD":
            xalign 0.5
            color "#9a8060"
            size 36
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(2, "#000000", 0, 0)]

        text "WALLET: [cash:,] CZK":
            xalign 0.5
            color "#ffd700"
            size 20
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        vbox:
            xalign 0.5
            spacing 8

            for _o in offers:
                python:
                    _ocid   = _o["card_id"]
                    _oprice = _o["price"]
                    _oc     = CARD_LIBRARY.get(_ocid, {})
                    _oname  = _oc.get("name", _ocid)
                    _otype  = _oc.get("type", "Skill")
                    _orar   = _oc.get("rarity", "common")
                    _odesc  = effect_description(_oc.get("effect")) or _oc.get("flavor", "")
                    _oafford = (cash >= _oprice)
                    _orar_color = RARITY_COLOR.get(_orar, "#cccccc") if _oafford else "#5a5042"
                    _oprice_color = ("#ffd700" if _oafford else "#a04040")

                button:
                    xysize (1060, 74)
                    background Frame(Solid("#1a1410"), 4, 4)
                    hover_background Frame(Solid("#3a2a1a"), 4, 4)
                    sensitive _oafford
                    action Return(_ocid)
                    hbox:
                        spacing 16
                        yalign 0.5
                        vbox:
                            spacing 2
                            yalign 0.5
                            xsize 760
                            text "[_oname]  ([_otype!u])":
                                color _orar_color
                                size 20
                                font "fonts/RobotoMono-Regular.ttf"
                            text "[_odesc]":
                                color ("#ccc4b4" if _oafford else "#5a5042")
                                size 14
                                font "fonts/RobotoMono-Regular.ttf"
                        text "[_oprice:,] CZK":
                            color _oprice_color
                            size 22
                            bold True
                            yalign 0.5
                            font "fonts/RobotoMono-Regular.ttf"

        textbutton "BACK":
            xalign 0.5
            action Return("back")
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 18
            text_font "fonts/RobotoMono-Regular.ttf"
            top_margin 8

    key "K_ESCAPE" action Return("back")


## ---------------------------------------------------------------------------
## Fixer shop — BUY GEAR (relic). offers = [{relic_id, price}]. Returns a
## relic_id to buy, or "back". Unaffordable rows dim and non-clickable.
## ---------------------------------------------------------------------------
screen fixer_relic_buy_screen(offers, cash):
    modal True
    zorder 700

    add "#0a0a0aee"
    use class_color_frame(thickness=3, alpha_suffix="aa")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14

        text "FIXER · BUY GEAR":
            xalign 0.5
            color "#9a8060"
            size 36
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(2, "#000000", 0, 0)]

        text "Build-defining. He only ever has a few. Gold = rare.":
            xalign 0.5
            color "#888888"
            size 15
            italic True
            font "fonts/RobotoMono-Regular.ttf"

        text "WALLET: [cash:,] CZK":
            xalign 0.5
            color "#ffd700"
            size 20
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        vbox:
            xalign 0.5
            spacing 8

            for _ro in offers:
                python:
                    _rrid   = _ro["relic_id"]
                    _rprice = _ro["price"]
                    _rmeta  = RELIC_LIBRARY.get(_rrid, {})
                    _rname  = _rmeta.get("name", _rrid)
                    _rhook  = _rmeta.get("hook", "")
                    _rrarity = _rmeta.get("rarity", "common").upper()
                    _rafford = (cash >= _rprice)
                    _rhex   = relic_hex(_rrid) if _rafford else "#5a5042"
                    _rrar_col = relic_rarity_hex(_rrid) if _rafford else "#5a5042"
                    _rprice_color = ("#ffd700" if _rafford else "#a04040")

                button:
                    xysize (1060, 84)
                    background Frame(Solid("#161210"), 4, 4)
                    hover_background Frame(Solid("#322617"), 4, 4)
                    sensitive _rafford
                    action Return(_rrid)
                    hbox:
                        spacing 16
                        yalign 0.5
                        frame:
                            xysize (54, 54)
                            yalign 0.5
                            background Frame(Solid(_rhex), 3, 3)
                            padding (3, 3)
                            frame:
                                xfill True
                                yfill True
                                background "#11110caa"
                                text relic_glyph(_rrid):
                                    xalign 0.5
                                    yalign 0.5
                                    color _rhex
                                    size 26
                                    bold True
                                    font "fonts/RobotoMono-Regular.ttf"
                        vbox:
                            spacing 2
                            yalign 0.5
                            xsize 720
                            hbox:
                                spacing 10
                                text "[_rname]":
                                    color _rhex
                                    size 20
                                    bold True
                                    font "fonts/RobotoMono-Regular.ttf"
                                text "[_rrarity]":
                                    color _rrar_col
                                    size 13
                                    bold True
                                    yalign 0.5
                                    font "fonts/RobotoMono-Regular.ttf"
                            text "[_rhook]":
                                color ("#ccc4b4" if _rafford else "#5a5042")
                                size 14
                                font "fonts/RobotoMono-Regular.ttf"
                        text "[_rprice:,] CZK":
                            color _rprice_color
                            size 22
                            bold True
                            yalign 0.5
                            font "fonts/RobotoMono-Regular.ttf"

        textbutton "BACK":
            xalign 0.5
            action Return("back")
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 18
            text_font "fonts/RobotoMono-Regular.ttf"
            top_margin 8

    key "K_ESCAPE" action Return("back")


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

    default _dup_tab = "deck"

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

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14

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

        ## ── Grid layout — full StS card visuals, click an upgradeable card
        ## to preview its `+` form. Non-upgradeable cards are dimmed (passed
        ## `playable=False` to battle_card_view) and not clickable. Matches
        ## the deck_viewer grid; same 6-per-row pitch.
        viewport:
            xsize 1600
            ysize 760
            scrollbars "vertical"
            mousewheel True
            draggable True

            vbox:
                spacing 24

                for _col in _dup_group_order:
                    if _dup_by_group.get(_col):
                        $ _col_hex = TYPE_PALETTE.get(_col, {}).get("frame", "#888888")
                        $ _col_cards = _dup_by_group[_col]

                        ## Group header — color bar + count.
                        hbox:
                            spacing 12
                            yalign 0.5
                            frame:
                                ysize 22
                                xsize 8
                                background Frame(_col_hex, 0, 0)
                            text "{} ({})".format(_col.upper(), len(_col_cards)):
                                color _col_hex
                                size 22
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"
                                outlines [(1, "#000000", 0, 0)]

                        $ _rows = [_col_cards[i:i+6] for i in range(0, len(_col_cards), 6)]
                        vbox:
                            spacing 28
                            for _row in _rows:
                                hbox:
                                    spacing 16
                                    for _cid in _row:
                                        $ _can_up = is_upgradeable(_cid)

                                        ## fixed wrapper reserves the slot
                                        ## so non-upgradeable cards (no
                                        ## button) take the same footprint
                                        ## as the clickable ones.
                                        fixed:
                                            xysize (220, 320)
                                            if _can_up:
                                                button:
                                                    xsize 220
                                                    ysize 316
                                                    background None
                                                    hover_background None
                                                    action Return(_cid)
                                                    at card_hover_lift
                                                    use battle_card_view(cid=_cid, mode="hand", playable=True)
                                            else:
                                                ## Dimmed via playable=False — frame desaturates,
                                                ## cost gem darkens, description fades. No hover lift.
                                                use battle_card_view(cid=_cid, mode="hand", playable=False)

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
            action Return("cancel")
            text_color "#aaaaaa"
            text_hover_color "#ffffff"
            text_size 20
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#1a1a1aee", 4, 4)
            hover_background Frame("#2a2a2aee", 4, 4)
            padding (24, 10)

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

        text "[_cup_base.get('name', base_id)]   →   [_cup_plus.get('name', '?')]" substitute False:
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
## Card Acquired Toast — slides in from top-right when grant_card fires non-silently.
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
            _ct_header = "🔥 RAGE FORCED"
            _ct_bg = "#1a0a0aff"
        elif _ct_is_compromise:
            _ct_color = "#a09890"
            _ct_header = "🚫 COMPROMISE LANDED"
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

        text "30 days. One life. No reloads.":
            color "#888888"
            size 16
            font "fonts/RobotoMono-Regular.ttf"

        text "Choose your suffering. This cannot be undone.":
            color "#444444"
            size 19
            font "fonts/RobotoMono-Regular.ttf"

    ## ── Difficulty list (left) ──────────────────────────────────────────────
    ## Whole-row click target — playtest hit on the ▶ glyph (passive marker)
    ## three times with no response. The `button` wraps the entire 718x76
    ## strip so anywhere in the row commits the choice.
    for _i, _diff in enumerate(DIFF_DATA):
        button:
            xpos 0
            ypos (220 + _i * 76)
            xsize 718
            ysize 76
            background ("#cc220033" if _hov == _i else "#00000000")
            hover_background "#cc220033"
            action [SetField(store, "_chosen_difficulty", _diff["key"]), Return()]
            hovered SetScreenVariable("_hov", _i)

            hbox:
                yalign 0.5
                frame:
                    xsize 5
                    ysize 76
                    background ("#cc2200" if _hov == _i else "#1a0000")
                frame:
                    xsize 22
                    ysize 76
                    background "#00000000"
                text ("▶  " if _hov == _i else "   "):
                    color "#cc2200"
                    size 28
                    yalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"
                text _diff["name"]:
                    color ("#ffffff" if _hov == _i else "#555555")
                    size  (32 if _hov == _i else 28)
                    bold  (_hov == _i)
                    font  "fonts/RobotoMono-Regular.ttf"
                    yalign 0.5

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
    key "K_DOWN"     action SetScreenVariable("_hov", min(len(DIFF_DATA) - 1, _hov + 1))
    key "K_RETURN"   action [SetField(store, "_chosen_difficulty", DIFF_DATA[_hov]["key"]), Return()]
    key "K_KP_ENTER" action [SetField(store, "_chosen_difficulty", DIFF_DATA[_hov]["key"]), Return()]


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
        "bodybuilder": "Words bounce off muscle. The grind pays — in cash and calm. Code comes slower.",
        "biohacker":   "The body is the lab. Today's protocol decides tomorrow's combat edge. Coding ramps fastest.",
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
                                    text ("IN DEVELOPMENT"):
                                        color ("#bdbdbd" if _focus == _i else "#9a9a9a")
                                        size 14
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
                                text "▶  SELECT":
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
        _unlocked = getattr(store, '_achievements_unlocked', set())
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

    vbox:
        spacing 14

        text "[_ach_count] / [_ach_total] UNLOCKED":
            color "#888888"
            size 18
            font "fonts/RobotoMono-Regular.ttf"

        for _cat in _ach_categories:
            if _ach_by_cat.get(_cat):
                $ _cat_done, _cat_total = _ach_cat_counts.get(_cat, (0, 0))

                text "{} ({}/{})".format(_cat.upper(), _cat_done, _cat_total):
                    color "#cc2200"
                    size 18
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

                $ _entries = _ach_by_cat[_cat]
                $ _pairs = [(_entries[i], _entries[i+1] if i+1 < len(_entries) else None) for i in range(0, len(_entries), 2)]

                for _left, _right in _pairs:
                    hbox:
                        spacing 12

                        for _entry in (_left, _right):
                            if _entry is None:
                                frame:
                                    xsize 460
                                    background "#00000000"
                            else:
                                $ _ach_key, _ach_data = _entry
                                $ _is_unlocked = _ach_key in _unlocked
                                $ _is_secret   = _ach_data.get("category") == "Secret"
                                $ _frame_bg    = Frame("#1a0011dd", 4, 4) if _is_unlocked else Frame("#0d0d0ddd", 4, 4)
                                frame:
                                    xsize 460
                                    background _frame_bg
                                    padding (14, 10)

                                    vbox:
                                        spacing 4
                                        if _is_unlocked:
                                            text _ach_data["name"]:
                                                color "#ffdd00"
                                                size 16
                                                bold True
                                            text _ach_data["desc"]:
                                                color "#cccccc"
                                                size 14
                                        elif _is_secret:
                                            text "???":
                                                color "#444444"
                                                size 16
                                                bold True
                                            text "Secret achievement — discover it to reveal.":
                                                color "#333333"
                                                size 14
                                        else:
                                            text _ach_data["name"]:
                                                color "#666666"
                                                size 16
                                                bold True
                                            text _ach_data.get("hint", "Locked."):
                                                color "#555555"
                                                size 14
                                                italic True


## ---------------------------------------------------------------------------
## Trophies Menu — opened from the navigation/escape menu.
## ---------------------------------------------------------------------------

screen trophies_menu():
    tag menu

    use game_menu(_("Trophies"), scroll="viewport"):
        use _achievements_list


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


