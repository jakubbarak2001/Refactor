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
            _run_hp_max_show = 115 if (stats and stats.player_class == "bodybuilder") else (75 if (stats and stats.player_class == "dark_empath") else 80)
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

                            vbox:
                                spacing 0

                                if _is_today:
                                    text "▼":
                                        color _class_color
                                        size 10
                                        xalign 0.5
                                        bold True
                                else:
                                    null height 12

                                frame:
                                    xsize 66
                                    ysize 30
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
        ## Group cards by TYPE — Attack / Skill / Power — with corruption
        ## (Rage / Status / Compromise) split out and anchored at the bottom
        ## so the player's clean kit reads top-of-screen.
        _GROUP_HEX = {
            "Attack":     "#cc4422",
            "Skill":      "#3388cc",
            "Power":      "#aa44cc",
            "Rage":       "#cc2200",
            "Status":     "#8a7a2a",
            "Compromise": "#7a7060",
        }
        _group_order = ["Attack", "Skill", "Power", "Rage", "Status", "Compromise"]

        _deck_cards = player_deck.cards if player_deck is not None else []
        _deck_count = len(_deck_cards)
        _deck_by_group = {}
        for _cid in _deck_cards:
            _c = CARD_LIBRARY.get(_cid)
            if _c is None:
                continue
            if _c.get("is_compromise"):
                _grp_key = "Compromise"
            elif _c.get("is_rage"):
                _grp_key = "Rage"
            elif (_c.get("effect") or "").startswith("status_"):
                _grp_key = "Status"
            else:
                _grp_key = _c.get("type", "Skill")
            _deck_by_group.setdefault(_grp_key, []).append(_cid)

    ## Class-color outer frame — "this is YOUR deck" without overriding per-card colors.
    use class_color_frame(thickness=3, alpha_suffix="aa")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14

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

        viewport:
            xsize 1500
            ysize 700
            scrollbars "vertical"
            mousewheel True
            draggable True

            vbox:
                spacing 14

                for _grp in _group_order:
                    if _deck_by_group.get(_grp):
                        $ _grp_hex = _GROUP_HEX.get(_grp, "#888888")
                        $ _grp_cards = _deck_by_group[_grp]

                        hbox:
                            spacing 10
                            text "{} ({})".format(_grp.upper(), len(_grp_cards)):
                                color _grp_hex
                                size 18
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"

                        ## Render cards in rows of 4
                        $ _rows = [_grp_cards[i:i+4] for i in range(0, len(_grp_cards), 4)]
                        vbox:
                            spacing 8
                            for _row in _rows:
                                hbox:
                                    spacing 8
                                    for _cid in _row:
                                        $ _c = CARD_LIBRARY.get(_cid, {})
                                        frame:
                                            xsize 350
                                            ysize 130
                                            background Frame("#0d0d0dee", 4, 4)
                                            padding (12, 10)

                                            vbox:
                                                spacing 4

                                                hbox:
                                                    spacing 6
                                                    text "[[ {} ]".format(_c.get("cost", 0)):
                                                        color _grp_hex
                                                        size 14
                                                        bold True
                                                    text _c.get("name", _cid):
                                                        color card_name_color(_c, "#ffffff")
                                                        size 16
                                                        bold True

                                                text "{} · {} · {}".format(_c.get("type", ""), _c.get("rarity", ""), _c.get("color", "")):
                                                    color "#666666"
                                                    size 11

                                                text effect_description(_c.get("effect", "")):
                                                    color "#cccccc"
                                                    size 13
                                                    xmaximum 326

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

screen _activity_tile(label_name, title, accent, cost_text, effect_text="", effect_chips=None, locked=False, lock_text="", class_relevant=False, flavor_text="", art_glyph="", cost_unaffordable=False):
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

                    ## EFFECT — chip row (preferred) or legacy "Reward:" string.
                    if effect_chips:
                        use _activity_chip_row(chips=effect_chips)
                    elif effect_text:
                        text "Reward: [effect_text]":
                            color "#cccccc"
                            size 13
                            xalign 0.5

                    ## FLAVOR / LOCK NOTE — italic at the bottom.
                    null height 2
                    if locked and lock_text:
                        text lock_text:
                            color "#554434"
                            size 11
                            italic True
                            xalign 0.5
                            text_align 0.5
                            xmaximum 280
                    elif flavor_text:
                        text flavor_text:
                            color "#888080"
                            size 11
                            italic True
                            xalign 0.5
                            text_align 0.5
                            xmaximum 280


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

    vbox:
        xalign 0.5
        ypos 140
        spacing 6

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

    ## Tile grid - auto-wrap to a 3-wide layout
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 28

        python:
            _opts_visible = [o for o in options if o.get("visible", True)]
            _per_row = 3
            _rows = [_opts_visible[i:i + _per_row] for i in range(0, len(_opts_visible), _per_row)]

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

            text "At 40 / 60 / 80 — a Rage card is forced into your deck. Deals damage at a cost.":
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
        ## Precomputed paid-tile affordability — drives the red cost text
        ## on the tile preempting an "insufficient funds" outcome.
        _recovery_cost = adjusted_cost(500)
        _recovery_short= (stats is not None) and (stats.available_money < _recovery_cost)

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
                effect_chips      = [("Upgrade", "Upgrade a card"), ("sep", "/"), ("Card", "Heal + Max HP")],
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
                label_name        = "activity_recovery",
                title             = "RECOVERY",
                accent            = class_accent_color("biohacker"),
                cost_text         = "{:,} CZK".format(_recovery_cost),
                cost_unaffordable = _recovery_short,
                effect_chips      = [("Hatred", -30)],
                flavor_text       = "Red light. Sauna. Cold plunge. Data clean.",
                class_relevant    = True,
            )

        ## BOUNCER - money path, neutral for every class.
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
            effect_chips   = [("Coding", "+ Coding"), ("sep", "/"), ("CZK", "+ CZK")],
            flavor_text    = "Freelance / Coach / Bootcamp.",
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
        _phone_msgs   = getattr(store, '_phone_notifications', [])
        _phone_count  = len(_phone_msgs)
        _hub_class_color = class_accent_color()
        ## Brackets render dimmer than the word so the verb (TRAIN/READ/STACK)
        ## reads as the hot focal point and the brackets frame it without
        ## competing for attention.
        _hub_cta_dim   = _hub_class_color + "aa"
        ## Dossier tag — case-file stamp on the day's marquee. Precomputed
        ## as a plain string so we don't lean on Ren'Py format-spec syntax
        ## inside the displayable.
        _dossier_tag       = "JBKZ-{:02d}".format(_today)
        _dossier_tag_closed = _dossier_tag + " · CLOSED"

        if stats and stats.player_class == "bodybuilder":
            _hub_cta_word  = "TRAIN"
            _hub_cta_sub   = "The body is the argument. Pick the rep."
            _hub_cta_color = _hub_class_color
            _hub_cta_hover = "#ff8855"
        elif stats and stats.player_class == "dark_empath":
            _hub_cta_word  = "READ"
            _hub_cta_sub   = "The room is the data. Pick what you watch."
            _hub_cta_color = _hub_class_color
            _hub_cta_hover = "#bb66dd"
        elif stats and stats.player_class == "biohacker":
            _hub_cta_word  = "STACK"
            _hub_cta_sub   = "The protocol is the answer. Pick the input."
            _hub_cta_color = _hub_class_color
            _hub_cta_hover = "#55ee88"
        else:
            _hub_cta_word  = "PICK YOUR MOVE"
            _hub_cta_sub   = "One choice. Earn cards. Build the deck."
            _hub_cta_color = "#cc2200"
            _hub_cta_hover = "#ff4422"

    ## ── Sidebar — PHONE (gated on unread notifications) ─────────────────────
    if _phone_msgs:
        frame:
            xpos 1700
            ypos 240
            xsize 200
            padding (14, 14)
            background Frame("#0a0a0aee", 4, 4)

            vbox:
                spacing 8
                xfill True

                textbutton "PHONE · [_phone_count]":
                    xalign 0.5
                    action Show("phone_screen")
                    text_color "#ffd700"
                    text_hover_color "#ffffff"
                    text_size 18
                    text_bold True
                    text_font "fonts/RobotoMono-Regular.ttf"
                    background "#00000000"
                    hover_background Frame("#1f1808dd", 3, 3)
                    padding (10, 8)
                    xfill True

                text "Unread.":
                    xalign 0.5
                    color "#888888"
                    size 12
                    italic True
                    font "fonts/RobotoMono-Regular.ttf"

    ## ── Sidebar — FIXER (day 10+; one shred per day; free time, doesn't
    ## burn your daily activity). Dimmed and disabled after today's shred.
    if _today >= 10:
        $ _fixer_done = bool(getattr(store, '_fixer_shredded_today', False))
        frame:
            xpos 1700
            ypos (380 if _phone_msgs else 240)
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

                    text "TODAY · DAY [_today] / 30":
                        color _hub_class_color
                        size 14
                        bold True
                        xalign 0.5
                        font DOSSIER_FONT

                    ## Split-bracket CTA — dim brackets frame the bright verb.
                    hbox:
                        xalign 0.5
                        spacing 8

                        text "[[":
                            color _hub_cta_dim
                            size 64
                            bold True
                            yalign 0.5
                            font DOSSIER_FONT

                        textbutton _hub_cta_word:
                            yalign 0.5
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

                        text "]":
                            color _hub_cta_dim
                            size 64
                            bold True
                            yalign 0.5
                            font DOSSIER_FONT

                    text _hub_cta_sub:
                        color "#a0a0a0"
                        size 17
                        italic True
                        xalign 0.5
                        font DOSSIER_FONT

                    null height 2

                    text "[DOSSIER_GLYPH] DOSSIER · [_dossier_tag]":
                        color DOSSIER_INK_DIM
                        size 11
                        xalign 0.5
                        font DOSSIER_FONT

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

screen outcome_panel(outcome_text):
    layer "screens"
    zorder 200

    ## Single frame > vbox > text-children — the canonical pattern. Earlier
    ## nested-frames-containing-text-directly + ATL-on-vbox combinations
    ## tripped Ren'Py's screen layout into ui.interact stack-imbalance
    ## crashes (seen on gym/coding card-offer flows). Visual stays flat
    ## (no green border, no header) so it doesn't look like a choice menu.
    frame:
        xalign 0.5
        yalign 0.86
        padding (28, 10)
        background Frame("#0a0a0acc", 0, 0)

        vbox:
            spacing 4
            xalign 0.5

            text outcome_text substitute False:
                color "#ffffff"
                size 22
                bold True
                xalign 0.5
                outlines [(2, "#000000aa", 0, 0)]

            text "› click to continue":
                color "#88aa88"
                size 11
                italic True
                xalign 0.5


## ---------------------------------------------------------------------------
## Card Shop — the bouncer-night market. Renders priced cards; BUY is gated on
## cash. Returns a card_id to buy, or "leave". The caller (bouncer_market)
## spends the money, grants the card, and re-shows until the player leaves.
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

    python:
        _cv_type     = card.get("type", "Skill")
        _cv_accent   = {"Attack": "#cc4422", "Skill": "#3388cc", "Power": "#aa44cc"}.get(_cv_type, "#888888")
        _cv_name     = card.get("name", "?")
        _cv_rarity   = card.get("rarity", "common")
        _cv_colorlab = card.get("color", "Special")
        _cv_cost     = card.get("cost", 0)
        _cv_flavor   = card.get("flavor", "")
        _cv_effect   = effect_description(card.get("effect"))
        _cv_subtitle = (_cv_type.upper() + " · " + _cv_rarity.upper() + " · " + _cv_colorlab.upper()).strip(" ·")
        _cv_art      = "images/cards/{}.png".format(card.get("id", ""))
        _cv_has_art  = renpy.loadable(_cv_art)
        _cv_glyph    = card.get("art_glyph") or {"Attack": "⚔", "Skill": "✦", "Power": "★"}.get(_cv_type, "●")

    fixed:
        xysize (420, 580)

        ## L1: glow halo
        add Solid(_cv_accent + "44") xpos 0 ypos 0 xysize (420, 580) at card_glow_pulse
        add Solid(_cv_accent + "77") xpos 8 ypos 8 xysize (404, 564) at card_glow_pulse

        ## L2: drop shadow
        add Solid("#000000aa") xpos 26 ypos 28 xysize (380, 540)

        ## L3 + L4: type-colored border wrapping warm-dark inner panel.
        frame:
            xpos 16
            ypos 16
            xsize 380
            ysize 540
            background Frame(_cv_accent, 6, 6)
            padding (8, 8)

            frame:
                xfill True
                yfill True
                background Frame("#1a1410", 4, 4)
                padding (12, 10)

                vbox:
                    xfill True
                    spacing 6

                    ## TITLE BANNER
                    frame:
                        xfill True
                        ysize 44
                        background Frame("#0a0806", 4, 4)
                        text _cv_name substitute False:
                            color card_name_color(card, "#e8c878")
                            size 24
                            bold True
                            xalign 0.5
                            yalign 0.5
                            xmaximum 320
                            text_align 0.5
                            font "fonts/RobotoMono-Regular.ttf"

                    ## ART ZONE
                    frame:
                        xfill True
                        ysize 200
                        background Frame(_cv_accent + "22", 4, 4)
                        if _cv_has_art:
                            add Transform(_cv_art, size=(320, 188)) xalign 0.5 yalign 0.5
                        else:
                            text _cv_glyph:
                                xalign 0.5
                                yalign 0.5
                                color _cv_accent
                                size 110
                                outlines [(3, "#000000", 0, 0)]

                    ## TYPE SUBTITLE
                    text _cv_subtitle substitute False:
                        xalign 0.5
                        size 11
                        color _cv_accent
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"

                    null height 2

                    ## DESCRIPTION BAND
                    frame:
                        xfill True
                        yminimum 100
                        background Frame("#241d15", 4, 4)
                        padding (12, 10)
                        if _cv_effect:
                            text _cv_effect substitute False:
                                color "#e8e0d0"
                                size 14
                                bold True
                                xalign 0.5
                                yalign 0.5
                                xmaximum 320
                                text_align 0.5
                                line_spacing 2

                    ## FLAVOR
                    if _cv_flavor:
                        text _cv_flavor substitute False:
                            color "#777777"
                            size 11
                            italic True
                            xalign 0.5
                            xmaximum 320
                            text_align 0.5

                    if card.get("exhaust"):
                        text "EXHAUST":
                            color "#cc4444"
                            size 11
                            bold True
                            xalign 0.5

        ## COST GEM — diamond overhanging the top-left corner.
        fixed:
            xpos -27
            ypos -28
            xysize (95, 95)
            add Transform(Solid(_cv_accent), size=(60, 60), rotate=45) xalign 0.5 yalign 0.5
            text "[_cv_cost]":
                xalign 0.5
                yalign 0.5
                color "#0a0806"
                size 34
                bold True
                font "fonts/RobotoMono-Regular.ttf"


## ---------------------------------------------------------------------------
## Card Offer Screen — TAKE or PASS prompt for activity/event card drops.
## Returns "take" or "pass" via Return().
## ---------------------------------------------------------------------------

screen card_offer_screen(card, source_label="", pass_stats_text=""):
    modal True
    zorder 700

    add "#0a0a0aee"

    python:
        _CO_COLORS = {
            "Physical": "#ff6633",
            "Mental":   "#9944cc",
            "Money":    "#ffd700",
            "Logic":    "#00ccff",
            "Police":   "#3388cc",
            "Special":  "#00cc88",
        }
        _co_color   = _CO_COLORS.get(card.get("color", "Special"), "#888888")
        _co_name    = card.get("name", "?")
        _co_type    = card.get("type", "")
        _co_rarity  = card.get("rarity", "")
        ## Pre-compute stat-line list at screen scope so the conditional
        ## vbox below doesn't need an inline `python:` block (which would
        ## imbalance Ren'Py's screen widget stack on render).
        _stat_lines = [s.strip() for s in pass_stats_text.split(",") if s.strip()] if pass_stats_text else []
        _co_cost    = card.get("cost", 0)
        _co_flavor  = card.get("flavor", "")
        _co_color_label = card.get("color", "")

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
        _csolo_palette = {
            "Physical": "#ff6633", "Mental": "#9944cc", "Money": "#ffd700",
            "Logic": "#00ccff", "Police": "#3388cc", "Special": "#00cc88",
        }
        _co_color = _csolo_palette.get(card.get("color", "Special"), "#888888")

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

    python:
        _type_palette = {"Attack": "#cc4422", "Skill": "#3388cc", "Power": "#aa44cc"}

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
            python:
                _c        = CARD_LIBRARY.get(_cid, {})
                _name     = _c.get("name", _cid)
                _type     = _c.get("type", "Skill")
                _rarity   = _c.get("rarity", "common")
                _cost     = _c.get("cost", 0)
                _flavor   = _c.get("flavor", "")
                _colorlab = _c.get("color", "Special")
                _accent   = _type_palette.get(_type, "#888888")
                _effect_s = effect_description(_c.get("effect"))
                _hot_n    = _ctp_i + 1
                _subtitle = (_type.upper() + " · " + _rarity.upper() + " · " + _colorlab.upper()).strip(" ·")
                _art_path = "images/cards/{}.png".format(_cid)
                _has_art  = renpy.loadable(_art_path)
                _art_glyph = _c.get("art_glyph") or {"Attack": "⚔", "Skill": "✦", "Power": "★"}.get(_type, "●")
                ## Fan-out hover offset: left leans left, centre stays, right leans right.
                ## Indexed by position in the trio; 4th+ slot defaults to no shift.
                _hover_xoff = (-36, 0, 36)[_ctp_i] if _ctp_i < 3 else 0

            button:
                xsize 420
                ysize 580
                background None
                hover_background None
                action Return(_cid)
                at reward_card_hover(_hover_xoff)

                ## L1: glow halo — pulses softly, signaling all three are selectable.
                add Solid(_accent + "44") xpos 0 ypos 0 xysize (420, 580) at card_glow_pulse
                add Solid(_accent + "77") xpos 8 ypos 8 xysize (404, 564) at card_glow_pulse

                ## L2: drop shadow
                add Solid("#000000aa") xpos 26 ypos 28 xysize (380, 540)

                ## L3 + L4: type-colored border wrapping warm-dark inner panel.
                frame:
                    xpos 16
                    ypos 16
                    xsize 380
                    ysize 540
                    background Frame(_accent, 6, 6)
                    padding (8, 8)

                    frame:
                        xfill True
                        yfill True
                        background Frame("#1a1410", 4, 4)
                        padding (12, 10)

                        vbox:
                            xfill True
                            spacing 6

                            ## TITLE BANNER
                            frame:
                                xfill True
                                ysize 44
                                background Frame("#0a0806", 4, 4)
                                text _name substitute False:
                                    color card_name_color(_c, "#e8c878")
                                    size 24
                                    bold True
                                    xalign 0.5
                                    yalign 0.5
                                    xmaximum 320
                                    text_align 0.5
                                    font "fonts/RobotoMono-Regular.ttf"

                            ## ART ZONE
                            frame:
                                xfill True
                                ysize 200
                                background Frame(_accent + "22", 4, 4)
                                if _has_art:
                                    add Transform(_art_path, size=(320, 188)) xalign 0.5 yalign 0.5
                                else:
                                    text _art_glyph:
                                        xalign 0.5
                                        yalign 0.5
                                        color _accent
                                        size 110
                                        outlines [(3, "#000000", 0, 0)]

                            ## TYPE SUBTITLE
                            text _subtitle substitute False:
                                xalign 0.5
                                size 11
                                color _accent
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"

                            null height 2

                            ## DESCRIPTION BAND
                            frame:
                                xfill True
                                yminimum 100
                                background Frame("#241d15", 4, 4)
                                padding (12, 10)
                                if _effect_s:
                                    text _effect_s substitute False:
                                        color "#e8e0d0"
                                        size 14
                                        bold True
                                        xalign 0.5
                                        yalign 0.5
                                        xmaximum 320
                                        text_align 0.5
                                        line_spacing 2

                            ## FLAVOR
                            if _flavor:
                                text _flavor substitute False:
                                    color "#777777"
                                    size 11
                                    italic True
                                    xalign 0.5
                                    xmaximum 320
                                    text_align 0.5

                            if _c.get("exhaust"):
                                text "EXHAUST":
                                    color "#cc4444"
                                    size 11
                                    bold True
                                    xalign 0.5

                ## COST GEM — diamond overhanging card top-left.
                ## Geometry mirrors battle gem ratio (battle: xpos -11/-14 on
                ## a 220-wide slot → reward: scaled 1.9× for the 420-wide slot).
                fixed:
                    xpos -27
                    ypos -28
                    xysize (95, 95)
                    add Transform(Solid(_accent), size=(60, 60), rotate=45) xalign 0.5 yalign 0.5
                    text "[_cost]":
                        xalign 0.5
                        yalign 0.5
                        color "#0a0806"
                        size 34
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"

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
        ## Keep in sync with deck_viewer's _COLOR_HEX (and VISION.md card-add checklist).
        _DUP_COLOR_HEX = {
            "Physical":   "#ff6633",
            "Mental":     "#9944cc",
            "Money":      "#ffd700",
            "Logic":      "#00ccff",
            "Tech":       "#66ddff",
            "Police":     "#3388cc",
            "Special":    "#00cc88",
            "Rage":       "#cc2200",
            "Compromise": "#7a7060",
        }
        _dup_cards = player_deck.cards if player_deck is not None else []
        _dup_count = len(_dup_cards)
        _dup_by_color = {}
        for _cid in _dup_cards:
            _c = CARD_LIBRARY.get(_cid)
            if _c is None:
                continue
            _col = _c.get("color", "Special")
            _dup_by_color.setdefault(_col, []).append(_cid)
        _dup_color_order = ["Physical", "Mental", "Money", "Logic", "Tech", "Police", "Special", "Rage", "Compromise"]
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

        viewport:
            xsize 1500
            ysize 640
            scrollbars "vertical"
            mousewheel True
            draggable True

            vbox:
                spacing 14

                for _col in _dup_color_order:
                    if _dup_by_color.get(_col):
                        $ _col_hex = _DUP_COLOR_HEX.get(_col, "#888888")
                        $ _col_cards = _dup_by_color[_col]

                        hbox:
                            spacing 10
                            text "{} ({})".format(_col.upper(), len(_col_cards)):
                                color _col_hex
                                size 18
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"

                        $ _rows = [_col_cards[i:i+4] for i in range(0, len(_col_cards), 4)]
                        vbox:
                            spacing 8
                            for _row in _rows:
                                hbox:
                                    spacing 8
                                    for _cid in _row:
                                        $ _c = CARD_LIBRARY.get(_cid, {})
                                        $ _can_up = is_upgradeable(_cid)
                                        $ _bg_color = "#0d0d0dee" if _can_up else "#0a0a0a99"
                                        ## Already-upgraded cards render their name green
                                        ## here too — the picker won't let you pick them
                                        ## (they're non-upgradeable), but the green tells
                                        ## you why they're locked.
                                        $ _name_color = card_name_color(_c, "#ffffff" if _can_up else "#555555")
                                        $ _flavor_color = "#aaaaaa" if _can_up else "#3a3a3a"

                                        button:
                                            xsize 350
                                            ysize 130
                                            background Frame(_bg_color, 4, 4)
                                            hover_background (Frame("#2a1a00ee", 4, 4) if _can_up else Frame(_bg_color, 4, 4))
                                            sensitive _can_up
                                            action Return(_cid)
                                            padding (12, 10)

                                            vbox:
                                                spacing 4

                                                hbox:
                                                    spacing 6
                                                    text "[[ {} ]".format(_c.get("cost", 0)):
                                                        color _col_hex
                                                        size 14
                                                        bold True
                                                    text _c.get("name", _cid) substitute False:
                                                        color _name_color
                                                        size 16
                                                        bold True
                                                    if not _can_up:
                                                        text "·":
                                                            color "#3a3a3a"
                                                            size 14
                                                        text "can't upgrade":
                                                            color "#555533"
                                                            size 11
                                                            italic True

                                                text "{} · {} · {}".format(_c.get("type", ""), _c.get("rarity", ""), _c.get("color", "")):
                                                    color "#666666"
                                                    size 11

                                                text effect_description(_c.get("effect", "")) substitute False:
                                                    color _flavor_color
                                                    size 13
                                                    xmaximum 326

                if not _dup_cards:
                    text "Your deck is empty.":
                        color "#666666"
                        size 16
                        italic True
                        xalign 0.5
                        text_align 0.5

        textbutton "[[ ← BACK TO GYM ]":
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
        _CUP_COLORS = {
            "Physical": "#ff6633",
            "Mental":   "#9944cc",
            "Money":    "#ffd700",
            "Logic":    "#00ccff",
            "Police":   "#3388cc",
            "Special":  "#00cc88",
        }
        _cup_base = CARD_LIBRARY.get(base_id, {})
        _cup_plus_id = get_upgraded_id(base_id)
        _cup_plus = CARD_LIBRARY.get(_cup_plus_id, {}) if _cup_plus_id else {}
        _cup_color = _CUP_COLORS.get(_cup_base.get("color", "Special"), "#888888")
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
        spacing 30

        ## LEFT — base card
        use _upgrade_card_panel(card=_cup_base, accent_color=_cup_color, label="CURRENT")

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

        ## RIGHT — upgraded card
        use _upgrade_card_panel(card=_cup_plus, accent_color=_cup_upg_accent, label="UPGRADED")

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


screen _upgrade_card_panel(card, accent_color, label):
    ## Shared card preview tile for card_upgrade_preview. Same shape as the
    ## TAKE panel in card_offer_screen so the eye recognizes "this is a card".
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
                background Frame(accent_color, 0, 0)

            text label:
                color accent_color
                size 13
                xalign 0.5
                bold True
                font "fonts/RobotoMono-Regular.ttf"

            null height 4

            frame:
                xsize 56
                ysize 56
                background Frame(accent_color, 4, 4)
                xalign 0.5
                text "[card.get('cost', 0)]":
                    color "#000000"
                    size 32
                    bold True
                    xalign 0.5
                    yalign 0.5

            null height 2

            text card.get("name", "?") substitute False:
                color card_name_color(card, "#ffffff")
                size 28
                bold True
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"

            text "{} · {} · {}".format(card.get("type", ""), card.get("rarity", "").upper(), card.get("color", "")) substitute False:
                color accent_color
                size 13
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"

            null height 10

            text "─────────────────────────":
                color "#222222"
                size 12
                xalign 0.5

            null height 6

            $ _cup_eff = effect_description(card.get("effect"))
            if _cup_eff:
                text _cup_eff substitute False:
                    color "#ffffff"
                    size 16
                    bold True
                    xalign 0.5
                    xmaximum 360
                    text_align 0.5
                    line_spacing 3

                null height 8

            text card.get("flavor", "") substitute False:
                color "#888888"
                size 13
                italic True
                xalign 0.5
                xmaximum 360
                text_align 0.5

            if card.get("exhaust"):
                null height 6
                text "[[EXHAUST]":
                    color "#cc4444"
                    size 13
                    bold True
                    xalign 0.5


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
        _UR_COLORS = {
            "Physical": "#ff6633",
            "Mental":   "#9944cc",
            "Money":    "#ffd700",
            "Logic":    "#00ccff",
            "Police":   "#3388cc",
            "Special":  "#00cc88",
        }
        _ur_card = CARD_LIBRARY.get(plus_id, {})
        _ur_color = _UR_COLORS.get(_ur_card.get("color", "Special"), "#ffaa44")
        _ur_accent = "#ffaa44"

    frame at _upgrade_reveal_anim:
        xalign 0.5
        yalign 0.5
        xsize 480
        ysize 600
        background Frame("#0d0d0dee", 4, 4)
        padding (24, 20)

        vbox:
            spacing 14
            xalign 0.5

            text "UPGRADED":
                color _ur_accent
                size 18
                bold True
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"

            frame:
                xalign 0.5
                xsize 400
                ysize 5
                background Frame(_ur_accent, 0, 0)

            null height 6

            frame:
                xsize 64
                ysize 64
                background Frame(_ur_color, 4, 4)
                xalign 0.5
                text "[_ur_card.get('cost', 0)]":
                    color "#000000"
                    size 36
                    bold True
                    xalign 0.5
                    yalign 0.5

            null height 4

            text _ur_card.get("name", "?") substitute False:
                color card_name_color(_ur_card, "#ffffff")
                size 36
                bold True
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"

            text "{} · {} · {}".format(_ur_card.get("type", ""), _ur_card.get("rarity", "").upper(), _ur_card.get("color", "")) substitute False:
                color _ur_color
                size 14
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"

            null height 12

            text "─────────────────────────":
                color "#222222"
                size 12
                xalign 0.5

            null height 6

            $ _ur_eff = effect_description(_ur_card.get("effect"))
            if _ur_eff:
                text _ur_eff substitute False:
                    color "#ffffff"
                    size 18
                    bold True
                    xalign 0.5
                    xmaximum 420
                    text_align 0.5
                    line_spacing 3

            null height 10

            text _ur_card.get("flavor", "") substitute False:
                color "#aaaaaa"
                size 14
                italic True
                xalign 0.5
                xmaximum 420
                text_align 0.5

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
        _CARD_TOAST_COLORS = {
            "Physical": "#ff6633",
            "Mental":   "#9944cc",
            "Money":    "#ffd700",
            "Logic":    "#00ccff",
            "Police":   "#3388cc",
            "Special":  "#00cc88",
        }
        ## Corruption variants override the color palette + header. These
        ## cards aren't "acquired" — they're forced on you. Rage by hatred,
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
            _ct_color = _CARD_TOAST_COLORS.get(card.get("color", "Special"), "#888888")
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

            text "{} · {} · {}".format(card.get("type", ""), card.get("rarity", ""), card.get("color", "")):
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
    LOCKED_CLASSES = {"dark_empath", "biohacker"}
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
        "biohacker":   (75, 0, 749, 1264),
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
## _classcol_hero — the playable class (BB). Just centres the portrait: no
## blur, no dim, no zoom, ever. It's crisp + full-brightness from frame one,
## which is what makes it visibly own the screen next to the recessed locked
## columns. (No hover zoom — it scaled the bright portrait up just enough to
## poke past the bottom scrim's edges.)
transform _classcol_hero:
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    zoom 1.0

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

                ## Class name — centred on a scrim band over the upper portrait
                frame:
                    xfill True
                    ypos 70
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
                                    text ("PREVIEW ONLY — CAN'T SELECT YET" if _focus == _i else "IN DEVELOPMENT"):
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
            text "[_deny_name] is still in development — BODYBUILDER is the only class you can take right now.":
                color "#dd9d8c"
                size 16
                xalign 0.5
                font "fonts/RobotoMono-Regular.ttf"
        timer 1.2 action SetScreenVariable("_denied", -1)

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

    ## Canonical Ren'Py say screen — `window id="window"` and
    ## `text what id="what"` are produced by `say_dossier` at the same
    ## screen-root depth they used to occupy here, preserving the
    ## widget-tree-shape invariant. The previous
    ## `if not renpy.get_screen("choice"):` conditional wrapping (since
    ## removed) changed that shape based on runtime state and caused
    ## modal-stack corruption (gym → card-offer → pause crash with
    ## "ui.interact called with non-empty widget/layer stack"). Do not
    ## re-introduce a conditional that omits the window wrapper.
    ##
    ## The dialogue window will visually overlap menu choices unless an
    ## explicit `window hide` runs before each `menu:` statement. That
    ## trade-off is accepted to keep play crash-free.
    use say_dossier(who, what)


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
    yminimum gui.textbox_height
    ymaximum 320
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


## ---------------------------------------------------------------------------
## Dossier HUD — top + bottom 36px case-file strips. Shown only during
## opted-in labels via `show screen dossier_hud`. Mirrors the main menu's
## top/bottom bars (mm_status font/size/color) so the player's eye
## recognizes the same chrome from the title screen.
## zorder 90 sits above stats_bar (100? — stats_bar is hidden in the
## prologue anyway) and below the choice overlay (250).
## ---------------------------------------------------------------------------
screen dossier_hud():
    zorder 90

    ## Top strip
    frame:
        xfill True
        ysize 36
        ypos 0
        background Solid(DOSSIER_BG_BAR)
        padding (0, 0)
        has fixed

        text "CASE FILE — JB  //  ARC I — THE INCIDENT":
            style "mm_status"
            xpos 28
            yalign 0.5

        if dossier_beat_time != "" or dossier_beat_slug != "":
            text "[dossier_beat_time]  //  [dossier_beat_slug]":
                style "mm_status"
                xalign 1.0
                xoffset -28
                yalign 0.5

    ## Bottom strip
    frame:
        xfill True
        ysize 36
        yalign 1.0
        background Solid(DOSSIER_BG_BAR)
        padding (0, 0)
        has fixed

        text "STATE POLICE  //  INTERNAL USE ONLY":
            style "mm_status"
            xpos 28
            yalign 0.5

        text "[[space] advance   [[esc] menu":
            style "mm_status"
            xalign 1.0
            xoffset -28
            yalign 0.5


## ---------------------------------------------------------------------------
## say_dossier — canonical dialogue window. `screen say` unconditionally
## delegates here, so this is what every Character() line in the game
## renders through. Preserves the load-bearing widget IDs ("window",
## "what") that the Ren'Py modal-stack bookkeeping relies on — see the
## comment in `screen say` above about the prior crash. Do not
## restructure without re-testing menu/choice interactions.
##
## Geometry: caps height at `ymaximum 230` (fits ~3 lines of dialogue,
## the soft writing constraint). 67% alpha backing lets the BG bleed
## through. Beat metadata lives in the top dossier_hud strip — NOT
## here — so it stays fixed when the strip is on screen, and is silent
## otherwise. Per-character namebox color comes from `Character(color=)`.
## ---------------------------------------------------------------------------
screen say_dossier(who, what):
    ## Uppercase the speaker name in Python — text-widget [var!u]
    ## substitution doesn't apply to screen parameters reliably, which
    ## was rendering "[who!u]" as literal text.
    $ _dossier_who = who.upper() if who else ""

    window:
        id "window"
        background Frame(DOSSIER_BG_SOLID, 0, 0)
        padding (0, 0, 0, 0)
        xalign 0.5
        xfill True
        yalign gui.textbox_yalign
        ## Window auto-sizes to its content (1–3 body lines + reserved
        ## 28px name slot + padding). ymaximum 260 caps it so a runaway
        ## line can't blow past the quick_menu strip.
        yminimum 0
        ymaximum 260
        bottom_margin 44

        hbox:
            spacing 0
            xfill True

            ## 4px rust-red left spine — frame with yfill so it stretches
            ## to the hbox's natural height. (`add` doesn't accept yfill;
            ## a frame with a Solid background does.)
            frame:
                xsize 4
                yfill True
                background Solid(DOSSIER_RED)
                padding (0, 0)

            ## Inner content area. Tight vertical padding so the window
            ## stays short; horizontal padding mirrors the original say
            ## window (60) minus the 4px the spine ate.
            frame:
                background None
                padding (56, 14, 60, 16)
                xfill True

                vbox:
                    spacing 6
                    xfill True

                    ## Name slot — always 28px tall whether a speaker is
                    ## present or not. Reserving the slot keeps the body
                    ## text's Y position consistent between narrator and
                    ## character lines (the user-requested invariant).
                    ## When narrator: just blank space. When character:
                    ## name + 1px slate underline.
                    fixed:
                        xfill True
                        ysize 28

                        if who is not None:
                            vbox:
                                spacing 3
                                xalign 0.0
                                yalign 0.0

                                ## No inline `color` — let each Character(color=...)
                                ## drive the namebox tint (colonel blue, martin
                                ## green, inspector yellow, jb white). The slate
                                ## underline below + RobotoMono uppercase keep
                                ## the dossier vocabulary regardless of color.
                                text _dossier_who id "who":
                                    font DOSSIER_FONT
                                    size 20
                                    kerning 2
                                    outlines [(1, "#000000aa", 0, 0)]

                                frame:
                                    xsize 140
                                    ysize 1
                                    background Solid(DOSSIER_INK_DIM)
                                    padding (0, 0)

                    ## Body — preserve `id "what"` for Character() styling.
                    text what id "what"


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
    ## Each option = [class-color left strip | dark button with hover tint].
    ## The strip ties the choice into the rest of the game's visual system
    ## (stats bar underline, class-color frame in battle screen) so menus
    ## stop reading as bare default Ren'Py UI.
    ## zorder 250 keeps the menu above the lingering say-window. Combined
    ## with the conditional hide on the say screen below, the textbox stays
    ## out of the way during menus so choices have the full bottom band.
    zorder 250

    python:
        _choice_accent = class_accent_color(stats.player_class) if stats else "#888888"

    vbox:
        xalign 0.5
        yalign 0.88
        spacing 14

        for i in items:
            hbox:
                spacing 0
                xalign 0.5

                ## Left-edge accent strip — pulses class color on hover via a
                ## button's hover_background. Uses the textbutton's hover state
                ## by piggybacking the row layout rather than a separate widget.
                frame:
                    xsize 5
                    ysize 64
                    background Solid(_choice_accent)

                textbutton i.caption:
                    action i.action
                    style "choice_button"


style choice_button is button
style choice_button_text is button_text

style choice_button:
    properties gui.button_properties("choice_button")
    xminimum 900
    xmaximum 1200
    ysize 64
    background Frame("#0d0d11ee", 0, 0)
    hover_background Frame("#1a0000ee", 0, 0)
    padding (28, 16)

style choice_button_text:
    properties gui.text_properties("choice_button")
    color "#c8c8d8"
    hover_color "#ff6644"
    size 22
    bold True
    font "fonts/RobotoMono-Regular.ttf"
    xalign 0.0


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    ## Ensure this appears on top of other screens.
    zorder 100

    if quick_menu:

        frame:
            style "quick_menu_frame"

            hbox:
                style_prefix "quick"
                style "quick_menu"

                textbutton _("back") action Rollback()
                textbutton _("history") action ShowMenu('history')
                textbutton _("skip") action Skip() alternate Skip(fast=True, confirm=True)
                textbutton _("auto") action Preference("auto-forward", "toggle")
                textbutton _("save") action ShowMenu('save')
                textbutton _("q.save") action QuickSave()
                textbutton _("q.load") action QuickLoad()
                textbutton _("settings") action ShowMenu('preferences')


## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_menu is hbox
style quick_menu_frame is frame
style quick_button is default
style quick_button_text is button_text

style quick_menu_frame:
    xalign 0.5
    yalign 1.0
    background Solid("#0a0a0acc")
    padding (16, 6)

style quick_menu:
    spacing 18

style quick_button:
    padding (8, 2)

style quick_button_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    hover_color "#ff4422"
    selected_color "#cc2200"
    insensitive_color "#334455"
    size 18
    kerning 1


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

        xpos 90
        ypos 230
        yanchor 0.0

        spacing gui.navigation_spacing

        if main_menu:

            textbutton _("►  start") action Start()

        else:

            textbutton _("►  history") action ShowMenu("history")

            textbutton _("►  save") action ShowMenu("save")

        textbutton _("►  load") action ShowMenu("load")

        textbutton _("►  settings") action ShowMenu("preferences")

        if stats is not None:

            textbutton _("►  trophies") action [Hide("phone_screen"), ShowMenu("trophies_menu")]

        if _in_replay:

            textbutton _("►  end replay") action EndReplay(confirm=True)

        elif not main_menu:

            textbutton _("►  main menu") action MainMenu()

        textbutton _("►  about") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

            ## Help isn't necessary or relevant to mobile devices.
            textbutton _("►  help") action ShowMenu("help")

        textbutton _("►  back to main menu" if main_menu else "►  back to game") action Return()

        if renpy.variant("pc"):

            ## The quit button is banned on iOS and unnecessary on Android and
            ## Web.
            textbutton _("►  quit") action Quit(confirm=not main_menu)


style navigation_button is mm_button
style navigation_button_text is mm_button_text

style navigation_button:
    size_group "navigation"
    xsize 360

style navigation_button_text:
    size 26


## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## https://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():

    ## Replaces any other menu screen when shown.
    tag menu

    ## Full-bleed looping video stays the hero — chrome sits on top.
    add gui.main_menu_background

    ## Institutional case-file strips top and bottom.
    use main_menu_top_bar
    use main_menu_bottom_bar

    ## Vertical rust-red accent bar — case-file tab spine anchoring title + nav.
    ## Runs from title top (y=272) to just above the bottom status strip (y=1008).
    add Solid("#cc2200"):
        xpos 72
        ypos 310
        xsize 4
        ysize 566
        at mm_fade_in

    ## Title wordmark — pinned at y=272 to preserve the original placement.
    text "REFACTOR":
        style "mm_title"
        xpos 90
        ypos 272
        at mm_fade_in

    ## Navigation column — case-file commands.
    use main_menu_navigation

    ## Dev-only quick-jump to the Colonel deck-fight. Hidden in ship builds.
    ## ypos 50 keeps it clear of the 36-px top status strip.
    if config.developer:
        textbutton "[[DEV] SKIP TO COLONEL FIGHT":
            xalign 0.98
            ypos 50
            action Start("dev_skip_to_colonel")
            text_color "#444444"
            text_hover_color "#ffcc00"
            text_size 13
            text_font "fonts/RobotoMono-Regular.ttf"
            background "#00000000"
            hover_background Frame("#1a1a00aa", 3, 3)
            padding (10, 6)


screen dossier_top_bar(left_text="REFACTOR  //  case-file-jb", right_text=None):
    frame:
        xfill True
        ysize 36
        ypos 0
        background Solid("#0a0a0acc")
        padding (0, 0)
        has fixed

        text left_text:
            style "mm_status"
            xpos 28
            yalign 0.5

        text (right_text if right_text is not None else "v[config.version]  //  northern bohemia"):
            style "mm_status"
            xalign 1.0
            xoffset -28
            yalign 0.5


screen dossier_bottom_bar(left_text="STATE POLICE  //  INTERNAL USE ONLY", right_text="[[esc] back   [[enter] confirm"):
    frame:
        xfill True
        ysize 36
        yalign 1.0
        background Solid("#0a0a0acc")
        padding (0, 0)
        has fixed

        text left_text:
            style "mm_status"
            xpos 28
            yalign 0.5

        text right_text:
            style "mm_status"
            xalign 1.0
            xoffset -28
            yalign 0.5


screen main_menu_top_bar():
    use dossier_top_bar


screen main_menu_bottom_bar():
    use dossier_bottom_bar(right_text="[[esc] exit   [[enter] go")


screen main_menu_navigation():
    ## Per-button hover sound — Play action fires reliably on every focus-enter,
    ## unlike style-level `hover_sound` which can be swallowed by mouse-hover paths.
    $ _mm_hover_sfx = Play("sound", "audio/sfx/ui_hover.wav")

    vbox:
        xpos 90
        ypos 470
        yanchor 0.0
        spacing 8
        at mm_fade_in

        textbutton _("►  new investigation") style "mm_button" action Start("mm_start_fade") hovered _mm_hover_sfx

        if renpy.newest_slot() is not None:
            textbutton _("►  continue") style "mm_button" action FileLoad(renpy.newest_slot()) hovered _mm_hover_sfx

        textbutton _("►  case archive") style "mm_button" action ShowMenu("load") hovered _mm_hover_sfx

        if stats is not None:
            textbutton _("►  trophies") style "mm_button" action [Hide("phone_screen"), ShowMenu("trophies_menu")] hovered _mm_hover_sfx

        textbutton _("►  settings") style "mm_button" action ShowMenu("preferences") hovered _mm_hover_sfx

        textbutton _("►  about") style "mm_button" action ShowMenu("about") hovered _mm_hover_sfx

        if renpy.variant("pc"):
            textbutton _("►  exit") style "mm_button" action Quit(confirm=False) hovered _mm_hover_sfx


transform mm_fade_in:
    alpha 0.0
    ease 0.6 alpha 1.0


## Polish entry point: brief freeze, music fadeout, fade-to-black, then hand off
## to the regular `start` label (which begins on bg_black + fades in its own music).
label mm_start_fade:
    pause 0.2
    stop music fadeout 1.0
    scene bg_black with Dissolve(0.6)
    pause 0.4
    jump start


style mm_title is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#e8e8e8"
    size 120
    kerning 4
    outlines [(3, "#000000cc", 0, 0)]

style mm_status is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 16
    outlines [(1, "#000000aa", 0, 0)]

style mm_button is button:
    background None
    hover_background Frame("#1a0000dd", 8, 4)
    padding (12, 6)
    xsize 560
    activate_sound "audio/sfx/ui_click.mp3"

style mm_button_text is button_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    hover_color "#ff4422"
    insensitive_color "#334455"
    size 34
    outlines [(2, "#000000cc", 0, 0)]


style dossier_section_label is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 22
    kerning 2

style dossier_subtitle is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 18
    kerning 1

style dossier_body_text is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 22

style dossier_body_text_dim is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 18

style dossier_pref_button is mm_button:
    background None
    hover_background Frame("#1a0000dd", 4, 4)
    selected_background Frame("#1a0000dd", 4, 4)
    padding (10, 4)
    xsize 320
    activate_sound "audio/sfx/ui_click.mp3"

style dossier_pref_button_text is mm_button_text:
    size 22
    color "#8899aa"
    hover_color "#ff4422"
    selected_color "#cc2200"
    insensitive_color "#334455"

style dossier_slot_button is button:
    background Frame("#0d0d11ee", 4, 4)
    hover_background Frame("#1a0000dd", 4, 4)
    padding (12, 12)
    activate_sound "audio/sfx/ui_click.mp3"

style dossier_slot_time_text is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 16

style dossier_slot_name_text is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 18

style dossier_page_button is mm_button:
    background None
    hover_background Frame("#1a0000dd", 4, 4)
    selected_background Frame("#1a0000dd", 4, 4)
    padding (10, 4)
    xsize None
    activate_sound "audio/sfx/ui_click.mp3"

style dossier_page_button_text is mm_button_text:
    size 18
    color "#8899aa"
    hover_color "#ff4422"
    selected_color "#cc2200"

style dossier_help_label is gui_label:
    xsize 280
    right_padding 24

style dossier_help_label_text is gui_label_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 22
    kerning 2
    xalign 1.0
    textalign 1.0

style dossier_help_text is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 22
    xsize 1000


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 420
    yfill True

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
        add Solid("#0a0a0aee")

    use dossier_top_bar(left_text="REFACTOR  //  case-file: " + title.lower())
    use dossier_bottom_bar()

    add Solid("#cc2200"):
        xpos 72
        ypos 130
        xsize 4
        ysize 680
        at mm_fade_in

    text title.upper():
        style "mm_title"
        size 64
        kerning 3
        xpos 90
        ypos 120
        at mm_fade_in

    use navigation

    frame:
        style "game_menu_outer_frame"

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

style game_menu_outer_frame:
    xpos 480
    ypos 235
    xsize 1380
    ysize 800
    background None
    padding (0, 0)

style game_menu_navigation_frame:
    xsize 360
    yfill False

style game_menu_content_frame:
    padding (0, 0)

style game_menu_viewport:
    xsize 1380

style game_menu_vscrollbar:
    unscrollable gui.unscrollable
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")
    xsize 6

style game_menu_side:
    spacing 12

## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    use game_menu(_("About"), scroll="viewport"):

        vbox:
            spacing 24
            xsize 1320

            frame:
                background Frame("#0d0d11ee", 4, 4)
                padding (28, 22)
                xfill True

                vbox:
                    spacing 8
                    text "CASE FILE //" style "dossier_section_label"
                    null height 6
                    text "[config.name!t]":
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#e8e8e8"
                        size 44
                        kerning 2
                    text "Version [config.version!t]":
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#c0d0e0"
                        size 22
                    text "Northern Bohemia  ·  State Police  ·  Internal Use Only":
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#667788"
                        size 18

            if gui.about:

                frame:
                    background Frame("#0d0d11ee", 4, 4)
                    padding (28, 22)
                    xfill True

                    vbox:
                        spacing 8
                        text "SUBJECT //" style "dossier_section_label"
                        null height 6
                        text "[gui.about!t]":
                            font "fonts/RobotoMono-Regular.ttf"
                            color "#c0d0e0"
                            size 20

            frame:
                background Frame("#0d0d11ee", 4, 4)
                padding (28, 22)
                xfill True

                vbox:
                    spacing 8
                    text "TOOLING //" style "dossier_section_label"
                    null height 6
                    text _("Made with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only]"):
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#c0d0e0"
                        size 20
                    text "[renpy.license!t]":
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#667788"
                        size 16


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text


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

    default page_name_value = FilePageNameInputValue(pattern=_("FILE :: {}"), auto=_("AUTO-LOG"), quick=_("QUICK-CACHE"))

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
                ypos 0
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                ypos 56

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        null height 6

                        text FileTime(slot, format=_("%Y-%m-%d  //  %H:%M"), empty=_("[[ empty slot ]")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## Buttons to access other pages.
            vbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                frame:
                    background Solid("#0a0a0a88")
                    padding (16, 8)
                    xalign 0.5

                    hbox:
                        xalign 0.5

                        spacing 6

                        textbutton _("[[ prev ]") action FilePagePrevious()
                        key "save_page_prev" action FilePagePrevious()

                        if config.has_autosave:
                            textbutton _("[[ A ]") action FilePage("auto")

                        if config.has_quicksave:
                            textbutton _("[[ Q ]") action FilePage("quick")

                        ## range(1, 10) gives the numbers from 1 to 9.
                        for page in range(1, 10):
                            textbutton "[[ [page] ]" action FilePage(page)

                        textbutton _("[[ next ]") action FilePageNext()
                        key "save_page_next" action FilePageNext()

                null height 8

                if config.has_sync:
                    if CurrentScreenName() == "save":
                        textbutton _("►  upload sync"):
                            action UploadSync()
                            xalign 0.5
                    else:
                        textbutton _("►  download sync"):
                            action DownloadSync()
                            xalign 0.5


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is dossier_page_button
style page_button_text is dossier_page_button_text

style slot_button is dossier_slot_button
style slot_button_text is dossier_slot_name_text
style slot_time_text is dossier_slot_time_text
style slot_name_text is dossier_slot_name_text

style page_label:
    xpadding 28
    ypadding 6
    xalign 0.5

style page_label_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    hover_color "#ff4422"
    size 22
    kerning 2
    textalign 0.5
    layout "subtitle"
    caret Solid("#cc2200")


## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    use game_menu(_("Settings"), scroll="viewport"):

        vbox:
            spacing 14

            hbox:
                box_wrap True
                spacing 60

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        spacing 4
                        text "DISPLAY //" style "dossier_section_label"
                        null height 6
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")

                vbox:
                    style_prefix "check"
                    spacing 4
                    text "SKIP //" style "dossier_section_label"
                    null height 6
                    textbutton _("Unseen Text") action Preference("skip", "toggle")
                    textbutton _("After Choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

            null height (3 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True
                spacing 60

                vbox:
                    spacing 6
                    text "PLAYBACK //" style "dossier_section_label"
                    null height 6

                    text "text speed" style "dossier_subtitle"
                    bar value Preference("text speed")

                    null height 8

                    text "auto-forward time" style "dossier_subtitle"
                    bar value Preference("auto-forward time")

                vbox:
                    spacing 6
                    text "AUDIO //" style "dossier_section_label"
                    null height 6

                    if config.has_music:
                        text "music volume" style "dossier_subtitle"

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        text "sound volume" style "dossier_subtitle"

                        hbox:
                            spacing 12
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("[[ test ]") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        text "voice volume" style "dossier_subtitle"

                        hbox:
                            spacing 12
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("[[ test ]") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("►  mute all"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is dossier_pref_button
style radio_button_text is dossier_pref_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is dossier_pref_button
style check_button_text is dossier_pref_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is dossier_pref_button
style slider_button_text is dossier_pref_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is dossier_pref_button
style mute_all_button_text is dossier_pref_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 3

style pref_label_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 22
    yalign 1.0

style pref_vbox:
    xsize 360

style radio_vbox:
    spacing 4

style check_vbox:
    spacing 4

style slider_slider:
    xsize 480
    ysize 20
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")
    thumb_offset 0

style slider_button:
    yalign 0.5
    left_margin 12

style slider_vbox:
    xsize 580
    spacing 4

style bar:
    ysize 20
    left_bar Solid("#cc2200")
    right_bar Solid("#1a2a3a")
    thumb None
    bar_resizing True

style scrollbar:
    ysize 6
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style vscrollbar:
    xsize 6
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")


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
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 20
    kerning 2

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    textalign gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 20

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
            spacing 18

            text "INPUT DEVICE //" style "dossier_section_label"

            hbox:
                spacing 32

                textbutton ("▶  keyboard" if device == "keyboard" else "►  keyboard"):
                    action SetScreenVariable("device", "keyboard")
                textbutton ("▶  mouse" if device == "mouse" else "►  mouse"):
                    action SetScreenVariable("device", "mouse")

                if GamepadExists():
                    textbutton ("▶  gamepad" if device == "gamepad" else "►  gamepad"):
                        action SetScreenVariable("device", "gamepad")

            null height 12

            text "BINDINGS //" style "dossier_section_label"

            null height 4

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


style help_button is dossier_pref_button
style help_button_text is dossier_pref_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    xmargin 0

style help_button_text:
    size 22

style help_label:
    xsize 280
    right_padding 24

style help_label_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 22
    kerning 2
    xalign 1.0
    textalign 1.0

style help_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 22



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

    add Solid("#000000bb")

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 28

            text "►  CONFIRMATION":
                style "confirm_header"
                xalign 0.5

            null height 8

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            null height 12

            hbox:
                xalign 0.5
                spacing 80

                textbutton _("►  yes") action yes_action
                textbutton _("◄  no") action no_action

    ## Right-click and escape answer "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is mm_button
style confirm_button_text is mm_button_text
style confirm_header is gui_text

style confirm_frame:
    background Frame("#0d0d11ee", 4, 4)
    padding (60, 48, 60, 48)
    xalign .5
    yalign .5

style confirm_header:
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 22
    kerning 3

style confirm_prompt_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 26
    textalign 0.5
    layout "subtitle"

style confirm_button:
    xsize 240

style confirm_button_text:
    size 28


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

            text "►" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "►" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "►" at delayed_blink(0.4, 1.0) style "skip_triangle"


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

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    xpos 540
    xsize 1320
    background None

style game_menu_navigation_frame:
    variant "small"
    xsize 480

style game_menu_content_frame:
    variant "small"
    padding (0, 0)

style game_menu_viewport:
    variant "small"
    xsize 1320

style pref_vbox:
    variant "small"
    xsize 600

style bar:
    variant "small"
    ysize 28
    left_bar Solid("#cc2200")
    right_bar Solid("#1a2a3a")

style vbar:
    variant "small"
    xsize 28
    top_bar Solid("#cc2200")
    bottom_bar Solid("#1a2a3a")

style scrollbar:
    variant "small"
    ysize 12
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style vscrollbar:
    variant "small"
    xsize 12
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style slider:
    variant "small"
    ysize 28
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style vslider:
    variant "small"
    xsize 28
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 900
