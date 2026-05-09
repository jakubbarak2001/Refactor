################################################################################
## REFACTOR — Battle Screen (Phase 1.4)
##
## Renders the BattleState singleton. Cards in hand are clickable.
## "End Turn" advances the engine. Returns "victory" / "defeat" when over.
##
## Layout (1920x1080):
##                  ┌──────────────────────────────────────┐
##                  │  COLONEL  HP 100/100  [intent: ATK 25] │
##                  └──────────────────────────────────────┘
##                              [colonel portrait]
##  ┌──── battle log ────┐                ┌── upcoming intents ──┐
##  │ ...                │                │ ATK 22 → BUFF 6 → ... │
##  └────────────────────┘                └─────────────────────┘
##                                            [end-turn button]
##  ┌────── PLAYER ──────┐
##  │ JB  HP 80/80  Block 0 │   [energy 3/3]
##  └────────────────────┘
##  ┌── HAND (5 cards) ─────────────────────────────────────┐
##  │  [card] [card] [card] [card] [card]                   │
##  └────────────────────────────────────────────────────────┘
##  draw: 12              discard: 4
################################################################################

## ---------------------------------------------------------------------------
## Phase A juice — visual effect transforms
##
## These are read by `screen battle_screen()` to render damage popups, the
## colonel portrait shake on hits, and screen-edge flash overlays. The fx
## are gated on `battle_state.fx_events` and `battle_state.last_*_hit_time`,
## both populated by `cards/battle_engine.rpy`. If the engine never pushes
## events, these transforms simply never fire.
## ---------------------------------------------------------------------------

init python:
    import math as _juice_math

    def _colonel_shake_fn(trans, st, at):
        """Damped horizontal oscillation on the colonel portrait. Fires when
        battle_state.last_enemy_hit_time is recent (<0.35s). Returns None to
        stop the per-frame callback once the shake settles."""
        bs = battle_state
        if bs is None or getattr(bs, 'last_enemy_hit_time', -1.0) < 0:
            trans.xoffset = 0
            return None
        try:
            age = renpy.get_game_runtime() - bs.last_enemy_hit_time
        except Exception:
            trans.xoffset = 0
            return None
        if age >= 0.35:
            trans.xoffset = 0
            return None
        ## Decay envelope: amplitude tapers to 0 over 0.35s
        amp = 10.0 * (1.0 - age / 0.35)
        ## Sin oscillation at ~35 rad/s = ~5.5 Hz — fast snappy shake
        trans.xoffset = int(amp * _juice_math.sin(age * 35.0))
        return 0.016  ## ~60 fps refresh

    def _player_frame_shake_fn(trans, st, at):
        """Smaller shake on the player status frame when the player takes
        damage. Same pattern as colonel shake, lower amplitude."""
        bs = battle_state
        if bs is None or getattr(bs, 'last_player_hit_time', -1.0) < 0:
            trans.xoffset = 0
            return None
        try:
            age = renpy.get_game_runtime() - bs.last_player_hit_time
        except Exception:
            trans.xoffset = 0
            return None
        if age >= 0.30:
            trans.xoffset = 0
            return None
        amp = 6.0 * (1.0 - age / 0.30)
        trans.xoffset = int(amp * _juice_math.sin(age * 40.0))
        return 0.016

    def _energy_pulse_fn(trans, st, at):
        """Phase B juice — energy counter scales 1.0 -> 1.25 -> 1.0 over
        0.35s after a card is played (i.e. last_energy_spend_time was just
        bumped). Visual confirmation that the click registered."""
        bs = battle_state
        if bs is None or getattr(bs, 'last_energy_spend_time', -1.0) < 0:
            trans.zoom = 1.0
            return None
        try:
            age = renpy.get_game_runtime() - bs.last_energy_spend_time
        except Exception:
            trans.zoom = 1.0
            return None
        if age >= 0.35:
            trans.zoom = 1.0
            return None
        ## Triangle pulse: ramp up over first 40%, ramp down over remaining 60%.
        progress = age / 0.35
        if progress < 0.4:
            trans.zoom = 1.0 + 0.25 * (progress / 0.4)
        else:
            trans.zoom = 1.25 - 0.25 * ((progress - 0.4) / 0.6)
        return 0.016

    def _battle_end_fanfare_fn(trans, st, at):
        """Phase D juice — VICTORY/DEFEAT text scales from 0.3 -> 1.3 (bounce)
        -> 1.0 over 0.6s, fades in alpha 0 -> 1 over 0.4s. Driven by
        bs.battle_end_time which the engine sets when bs.over is assigned."""
        bs = battle_state
        if bs is None or getattr(bs, 'battle_end_time', -1.0) < 0:
            trans.zoom = 1.0
            trans.alpha = 1.0
            return None
        try:
            age = renpy.get_game_runtime() - bs.battle_end_time
        except Exception:
            return None
        if age >= 0.7:
            trans.zoom = 1.0
            trans.alpha = 1.0
            return None
        ## Scale curve: 0.3 -> 1.3 (overshoot) -> 1.0 (settle)
        if age < 0.45:
            p = age / 0.45
            ## Smooth ease-out from 0.3 to 1.3
            trans.zoom = 0.3 + 1.0 * (1.0 - (1.0 - p) ** 2)
        else:
            p = (age - 0.45) / 0.25
            trans.zoom = 1.3 - 0.3 * p
        ## Alpha fade in over first 0.4s
        if age < 0.4:
            trans.alpha = age / 0.4
        else:
            trans.alpha = 1.0
        return 0.016

    def _block_gain_pulse_fn(trans, st, at):
        """Phase E juice — player block text pulses 1.0 -> 1.3 -> 1.0 over
        0.4s after gain_block fires. Block is mechanically important but
        was visually silent; this gives the moment a beat."""
        bs = battle_state
        if bs is None or getattr(bs, 'last_player_block_gain_time', -1.0) < 0:
            trans.zoom = 1.0
            return None
        try:
            age = renpy.get_game_runtime() - bs.last_player_block_gain_time
        except Exception:
            trans.zoom = 1.0
            return None
        if age >= 0.4:
            trans.zoom = 1.0
            return None
        progress = age / 0.4
        if progress < 0.35:
            trans.zoom = 1.0 + 0.3 * (progress / 0.35)
        else:
            trans.zoom = 1.3 - 0.3 * ((progress - 0.35) / 0.65)
        return 0.016

    def _battle_end_subtitle_fn(trans, st, at):
        """Phase D juice — subtitle reveal delayed 0.4s after the main
        VICTORY/DEFEAT text starts, fades in over 0.5s."""
        bs = battle_state
        if bs is None or getattr(bs, 'battle_end_time', -1.0) < 0:
            trans.alpha = 1.0
            return None
        try:
            age = renpy.get_game_runtime() - bs.battle_end_time
        except Exception:
            return None
        if age < 0.4:
            trans.alpha = 0.0
            return 0.016
        if age >= 0.9:
            trans.alpha = 1.0
            return None
        trans.alpha = (age - 0.4) / 0.5
        return 0.016

transform colonel_hit_shake:
    function _colonel_shake_fn

transform player_frame_hit_shake:
    function _player_frame_shake_fn

## TURN N banner — standard ATL (not function-driven). Re-triggers fresh
## each turn via the `use ... id "turn_banner_<N>"` pattern in battle_screen.
## Duration: 1.4s — slide in 0.3s, hold 0.7s, slide out 0.4s.
transform turn_banner_atl:
    alpha 0.0
    xoffset -400
    ease 0.3 alpha 1.0 xoffset 0
    pause 0.7
    ease 0.4 alpha 0.0 xoffset 400

transform damage_popup_anim:
    yoffset 0
    alpha 1.0
    parallel:
        easeout 0.7 yoffset -70
    parallel:
        linear 0.45 alpha 1.0
        linear 0.25 alpha 0.0

transform damage_flash_player:
    alpha 0.0
    linear 0.05 alpha 0.5
    linear 0.30 alpha 0.0

transform damage_flash_enemy:
    alpha 0.0
    linear 0.05 alpha 0.3
    linear 0.25 alpha 0.0

transform energy_pulse:
    function _energy_pulse_fn

transform battle_end_fanfare:
    function _battle_end_fanfare_fn

transform battle_end_subtitle:
    function _battle_end_subtitle_fn

transform block_gain_pulse:
    function _block_gain_pulse_fn


## Inner screen for the TURN banner. Wrapped via `use turn_banner_inner(...)
## id "turn_banner_<N>"` from battle_screen — the keyed id forces Ren'Py to
## treat each turn's mount as fresh, restarting the ATL animation cleanly.
## Solves the "turn banner sometimes appears" timing bug from the function-
## driven version (which depended on a global timestamp set in the engine
## and read by the screen, with race-condition gaps when the screen mounted
## after the timestamp was already stale).
screen turn_banner_inner(turn_n):
    frame:
        xalign 0.5
        ypos 240
        padding (40, 16)
        background Frame("#0a0a0aee", 4, 4)
        at turn_banner_atl
        text "TURN [turn_n]":
            color "#ffaa00"
            size 56
            bold True
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(3, "#000000", 0, 0)]

## Phase B juice — card hover lift. Cards in hand scale up + lift slightly
## on mouse-hover, settle on idle. Smooth ease so the cursor's-on-this-card
## affordance is unmistakable. ATL `on hover` / `on idle` blocks fire when
## the parent button transitions states.
transform card_hover_lift:
    on hover:
        ease 0.14 zoom 1.07 yoffset -18
    on idle:
        ease 0.14 zoom 1.0 yoffset 0


## Inner screen for a single damage popup. Wrapped via `use ... id <tick>`
## from battle_screen so each popup gets a STABLE identity across redraws —
## otherwise Ren'Py respawns the displayable on every redraw and the ATL
## animation restarts from frame 0, freezing the popup visually.
screen _damage_popup_overlay(fx):
    $ _amt = fx.get('amount', 0)
    $ _is_player = fx.get('target') == 'player'
    $ _color = "#ff4422" if _is_player else "#ffdd44"
    $ _xpos = 200 if _is_player else 1000
    $ _ypos = 540 if _is_player else 220
    text "-[_amt]":
        xpos _xpos
        ypos _ypos
        color _color
        size 64
        bold True
        outlines [(3, "#000000", 0, 0)]
        font "fonts/RobotoMono-Regular.ttf"
        at damage_popup_anim


## ---------------------------------------------------------------------------
## Battle Help — accessible via "?" button. One-screen reference.
## ---------------------------------------------------------------------------

screen battle_help():
    modal True
    zorder 750

    add "#0a0a0aee"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14
        xmaximum 1100

        text "HOW THE FIGHT WORKS":
            xalign 0.5
            color "#ffdd00"
            size 32
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text "─────────────────────────────────────────":
            xalign 0.5
            color "#222222"
            size 14

        frame:
            xalign 0.5
            background Frame("#0d0d0dee", 4, 4)
            padding (32, 20)
            xmaximum 1000

            vbox:
                spacing 10

                text "TURN STRUCTURE":
                    color "#cc2200"
                    size 18
                    bold True
                text "Each turn you draw 5 cards and refill to 3 energy. Play cards by clicking. Click END TURN when done.":
                    color "#cccccc"
                    size 14
                    xmaximum 940

                null height 6

                text "ENEMY INTENT":
                    color "#cc2200"
                    size 18
                    bold True
                text "The icon above the colonel's name shows what he'll do next turn:":
                    color "#cccccc"
                    size 14
                text "  🗡 ATTACK — deals N damage   ⚔ COMPOUND — N×hits damage   ■ BLOCK — gains block":
                    color "#aaaaaa"
                    size 13
                text "  ↑ BUFF — strengthens his next attack   ↓ DEBUFF — weakens you":
                    color "#aaaaaa"
                    size 13

                null height 6

                text "BLOCK":
                    color "#cc2200"
                    size 18
                    bold True
                text "Block absorbs damage. It resets to 0 at the start of each player turn (some Power cards add starting block).":
                    color "#cccccc"
                    size 14
                    xmaximum 940

                null height 6

                text "ENERGY":
                    color "#cc2200"
                    size 18
                    bold True
                text "Each card costs energy (the number in the colored circle). You start with 3 max — Powers and Biohacker mechanics can change this.":
                    color "#cccccc"
                    size 14
                    xmaximum 940

                null height 6

                text "POWER CARDS":
                    color "#cc2200"
                    size 18
                    bold True
                text "Power-type cards activate at battle start (job_offer, stoic_anchor, iron_stance, etc.). They're persistent buffs for the rest of the fight.":
                    color "#cccccc"
                    size 14
                    xmaximum 940

                null height 6

                text "EXHAUST":
                    color "#cc2200"
                    size 18
                    bold True
                text "Cards marked [[EXHAUST] are removed for the rest of the fight after one use.":
                    color "#cccccc"
                    size 14
                    xmaximum 940

                null height 6

                text "HOVER ANY CARD IN HAND":
                    color "#cc2200"
                    size 18
                    bold True
                text "to see exactly what it does. Tooltip appears just above the hand.":
                    color "#cccccc"
                    size 14

        textbutton "[[ CLOSE ]":
            xalign 0.5
            action Hide("battle_help")
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 18
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#1a0000ee", 4, 4)
            hover_background Frame("#330000ee", 4, 4)
            padding (24, 10)

    key "K_ESCAPE" action Hide("battle_help")


## ---------------------------------------------------------------------------
## Battle Pile Peek — see what's left in draw / discard / exhaust.
## ---------------------------------------------------------------------------

screen battle_pile_peek():
    modal True
    zorder 750

    add "#0a0a0aee"

    python:
        bs_p = battle_state
        _PEEK_COLORS = {
            "Physical": "#ff6633",
            "Mental":   "#9944cc",
            "Money":    "#ffd700",
            "Logic":    "#00ccff",
            "Police":   "#3388cc",
            "Special":  "#00cc88",
        }
        if bs_p:
            _peek_summary = "Draw {} · Discard {} · Exhaust {}".format(len(bs_p.draw_pile), len(bs_p.discard_pile), len(bs_p.exhaust_pile))
        else:
            _peek_summary = ""

    vbox:
        xalign 0.5
        yalign 0.05
        spacing 8

        text "PILES":
            xalign 0.5
            color "#ffdd00"
            size 28
            bold True
            font "fonts/RobotoMono-Regular.ttf"

        text _peek_summary:
            xalign 0.5
            color "#888888"
            size 14

    viewport:
        xpos 60
        ypos 130
        xsize 1800
        ysize 820
        scrollbars "vertical"
        mousewheel True
        draggable True

        vbox:
            spacing 14

            for _label, _pile, _accent in [("DRAW PILE", bs_p.draw_pile if bs_p else [], "#88ccff"), ("DISCARD PILE", bs_p.discard_pile if bs_p else [], "#cccc88"), ("EXHAUST PILE", bs_p.exhaust_pile if bs_p else [], "#cc4444")]:
                text "{} ({})".format(_label, len(_pile)):
                    color _accent
                    size 18
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

                if not _pile:
                    text "  (empty)":
                        color "#444444"
                        size 13
                        italic True
                else:
                    $ _peek_rows = [_pile[i:i+5] for i in range(0, len(_pile), 5)]
                    vbox:
                        spacing 6
                        for _row in _peek_rows:
                            hbox:
                                spacing 8
                                for _cid in _row:
                                    $ _c = CARD_LIBRARY.get(_cid, {})
                                    $ _ccol = _PEEK_COLORS.get(_c.get("color", "Special"), "#888888")
                                    frame:
                                        xsize 340
                                        background Frame("#0d0d0dee", 3, 3)
                                        padding (10, 6)
                                        hbox:
                                            spacing 8
                                            text "[[ {} ]".format(_c.get("cost", 0)):
                                                color _ccol
                                                size 14
                                                bold True
                                            text _c.get("name", _cid):
                                                color "#ffffff"
                                                size 14

    textbutton "[[ CLOSE ]":
        xalign 0.5
        yalign 0.97
        action Hide("battle_pile_peek")
        text_color "#888888"
        text_hover_color "#ffffff"
        text_size 18
        text_bold True
        text_font "fonts/RobotoMono-Regular.ttf"
        background Frame("#1a0000ee", 4, 4)
        hover_background Frame("#330000ee", 4, 4)
        padding (24, 10)

    key "K_ESCAPE" action Hide("battle_pile_peek")


screen battle_screen():
    modal True
    zorder 600

    add "#0a0a0a"

    ## Card-color palette (mirrors deck_viewer)
    python:
        _CARD_COLORS = {
            "Physical": "#ff6633",
            "Mental":   "#9944cc",
            "Money":    "#ffd700",
            "Logic":    "#00ccff",
            "Police":   "#3388cc",
            "Special":  "#00cc88",
        }
        bs = battle_state

    ## Class-color top + bottom border framing the entire fight.
    use class_color_frame(thickness=6)

    if bs is None:
        text "[[BATTLE STATE NULL]]" xalign 0.5 yalign 0.5 color "#ff0000" size 32
    else:
        ## ── Background portrait ────────────────────────────────────────────────
        ## colonel_hit_shake oscillates xoffset for ~0.35s after enemy takes
        ## damage; otherwise it's a no-op (function returns None).
        if bs.enemy_hp > 0 and bs.enemy_hp <= bs.enemy_max_hp * 0.3:
            add "colonel angry" xalign 0.5 yalign 0.18 zoom 0.65 at colonel_hit_shake
        else:
            add "colonel normal" xalign 0.5 yalign 0.18 zoom 0.65 at colonel_hit_shake

        ## ── ENEMY HEADER ──────────────────────────────────────────────────────
        frame:
            xalign 0.5
            yalign 0.0
            yoffset 16
            padding (24, 12)
            background Frame("#0d0d0dee", 4, 4)
            xsize 1100

            vbox:
                spacing 6
                xalign 0.5

                hbox:
                    spacing 16
                    xalign 0.5

                    text "COLONEL":
                        color "#ff2222"
                        size 22
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"

                    bar:
                        value bs.enemy_hp
                        range bs.enemy_max_hp
                        xsize 360
                        ysize 22
                        left_bar Frame("#cc2200", 2, 2)
                        right_bar Frame("#1a0000", 2, 2)

                    text "[bs.enemy_hp]/[bs.enemy_max_hp] HP":
                        color "#ffaaaa"
                        size 18
                        font "fonts/RobotoMono-Regular.ttf"

                    if bs.enemy_block > 0:
                        text "■ [bs.enemy_block]":
                            color "#88aaff"
                            size 18

                ## Intent line — current + revealed peeks
                python:
                    _ic = bs.current_intent()
                    _peek = []
                    if _ic:
                        _peek.append(_ic)
                    ## Cap at 5 so DE PROFILES bonus (peek depth 1+deep_count) is visible
                    for _i in range(1, min(bs.intent_revealed, 5)):
                        idx = bs.intent_index + _i
                        if 0 <= idx < len(bs.intent_queue):
                            _peek.append(ENEMY_DECK_LIBRARY.get(bs.intent_queue[idx]))

                if _peek:
                    hbox:
                        spacing 8
                        xalign 0.5

                        text "INTENT:":
                            color "#aaaaaa"
                            size 14

                        for _i, _intent in enumerate(_peek):
                            if _intent:
                                $ _label = _intent.get("name", "?")
                                $ _itype = _intent.get("intent", "attack")
                                ## Phase C — compute total incoming damage so we
                                ## can scale the intent display by threat tier.
                                if _itype == "attack":
                                    $ _icon = "🗡"
                                    $ _ic_color = "#ff4422"
                                    $ _dmg = _intent.get("value", 0)
                                    $ _val_text = "{}".format(_dmg)
                                elif _itype == "compound":
                                    $ _icon = "⚔"
                                    $ _ic_color = "#ff6644"
                                    $ _dmg = _intent.get("value", 0) * _intent.get("value2", 1)
                                    $ _val_text = "{}x{}".format(_intent.get("value", 0), _intent.get("value2", 1))
                                elif _itype == "block":
                                    $ _icon = "■"
                                    $ _ic_color = "#88aaff"
                                    $ _dmg = 0
                                    $ _val_text = "+{}".format(_intent.get("value", 0))
                                elif _itype == "buff":
                                    $ _icon = "↑"
                                    $ _ic_color = "#ffaa44"
                                    $ _dmg = 0
                                    $ _val_text = "+{}".format(_intent.get("value", 0))
                                else:
                                    $ _icon = "↓"
                                    $ _ic_color = "#aa44cc"
                                    $ _dmg = 0
                                    $ _val_text = "DEBUFF"

                                ## Threat tier — only escalate styling on the
                                ## CURRENT intent (i==0); peeked ones stay
                                ## subdued so the player's eye lands on the
                                ## imminent hit.
                                python:
                                    _is_current = (_i == 0)
                                    if _is_current and _dmg >= 15:
                                        _intent_size = 22
                                        _intent_color = "#ff2222"
                                        _intent_bg = "#3a0000ee"
                                        _icon_size = 24
                                    elif _is_current and _dmg >= 8:
                                        _intent_size = 18
                                        _intent_color = "#ffcc44"
                                        _intent_bg = "#2a1a00dd"
                                        _icon_size = 20
                                    elif _is_current:
                                        _intent_size = 14
                                        _intent_color = "#ffffff"
                                        _intent_bg = "#1a1a1add"
                                        _icon_size = 16
                                    else:
                                        _intent_size = 14
                                        _intent_color = "#888888"
                                        _intent_bg = "#1a1a1add"
                                        _icon_size = 16

                                frame:
                                    background Frame(_intent_bg, 4, 4)
                                    padding (8, 4)
                                    hbox:
                                        spacing 4
                                        text _icon:
                                            color _ic_color
                                            size _icon_size
                                        text "[_label] [_val_text]":
                                            color _intent_color
                                            size _intent_size
                                            bold _is_current

        ## ── BATTLE LOG (left side) ────────────────────────────────────────────
        frame:
            xpos 20
            ypos 200
            xsize 360
            ysize 360
            background Frame("#0d0d0dcc", 4, 4)
            padding (12, 10)

            vbox:
                spacing 4

                text "BATTLE LOG":
                    color "#cc2200"
                    size 14
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

                text "─────────────────":
                    color "#222222"
                    size 12

                for _msg in bs.log[-10:]:
                    text "[_msg]":
                        color "#aaaaaa"
                        size 12

        ## ── PLAYER STATUS (left side, below log) ──────────────────────────────
        ## player_frame_hit_shake fires for ~0.30s after player takes damage.
        frame:
            at player_frame_hit_shake
            xpos 20
            ypos 580
            xsize 360
            padding (16, 12)
            background Frame("#0d0d0dee", 4, 4)

            vbox:
                spacing 8

                text "JB":
                    color "#00ff41"
                    size 22
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"

                hbox:
                    spacing 6
                    bar:
                        value bs.player_hp
                        range bs.player_max_hp
                        xsize 200
                        ysize 18
                        left_bar Frame("#00ff41", 2, 2)
                        right_bar Frame("#1a1a1a", 2, 2)
                    text "[bs.player_hp]/[bs.player_max_hp]":
                        color "#88ff88"
                        size 14

                if bs.player_block > 0:
                    ## Phase E — block_gain_pulse pumps zoom 1.0 -> 1.3 -> 1.0
                    ## over 0.4s after gain_block fires. No-op when no recent gain.
                    text "■ BLOCK [bs.player_block]":
                        color "#88aaff"
                        size 16
                        bold True
                        at block_gain_pulse

                ## Active buffs — human-readable, internal-key gibberish hidden
                python:
                    _BUFF_LABELS = {
                        "starting_block_+1":   "+1 Starting Block",
                        "stoic_anchor_block":  "Stoic Anchor (block)",
                        "stoic_anchor_heal":   "Stoic Anchor (heal)",
                        "presence_charges":    "Presence",
                        "read_charges":        "Read",
                        "kick_charges":        "Kick",
                        "mental_dr_50":        "Stoic Refactor",
                        "iron_stance_active":  "Iron Stance",
                        "vladeks_active":      "Vladek's Form",
                        "single_retaliate_dmg":"Iron Body",
                        "vigil_next_turn_block":"Vigil",
                        "insight_block":       "Insight",
                        "insight_turns_left":  "Insight (turns)",
                        "block_next_turn":     "Procedural Defense",
                        "double_next_attack":  "Personal Record",
                        "mirror_next":         "Mirror (armed)",
                        "mirror_cooldown":     "Mirror (cooldown)",
                        "reframe_next":        "Reframe (armed)",
                        "next_attack_reduction":"Frame Trap",
                        "bleed_dmg":           "Bleed (dmg)",
                        "bleed_turns":         "Bleed (turns)",
                        "crash_next_turn":     "Stack-Up Crash",
                        "max_energy_penalty_next_turn":"FLMod Ebb",
                        "skip_next_turn":      "FLMod Crash",
                        "enemy_attack_bonus":  "Pressure",
                        "player_draw_penalty": "Authority Display",
                    }
                    _active_buffs = []
                    for _k, _v in bs.buffs.items():
                        if not _v:
                            continue
                        _label = _BUFF_LABELS.get(_k, _k)
                        if isinstance(_v, int) and _v > 1:
                            _active_buffs.append("{} x{}".format(_label, _v))
                        else:
                            _active_buffs.append(_label)
                if _active_buffs:
                    text "BUFFS: {}".format(", ".join(_active_buffs)):
                        color "#ffdd44"
                        size 11
                        xmaximum 340

        ## ── ENERGY (right side) ───────────────────────────────────────────────
        frame:
            xpos 1700
            ypos 580
            xsize 200
            padding (16, 12)
            background Frame("#0d0d0dee", 4, 4)

            vbox:
                spacing 4
                xalign 0.5

                text "ENERGY":
                    color "#ffdd44"
                    size 14
                    bold True
                    xalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"

                ## Phase B — energy_pulse scales 1.0 -> 1.25 -> 1.0 over 0.35s
                ## after a card spend. No-op when no recent spend.
                text "[bs.energy] / [bs.max_energy]":
                    color "#ffffff"
                    size 38
                    bold True
                    xalign 0.5
                    at energy_pulse

        ## ── END TURN BUTTON ───────────────────────────────────────────────────
        textbutton "[[ END TURN ]":
            xpos 1700
            ypos 700
            action [Function(battle_end_player_turn), Function(renpy.restart_interaction)]
            text_color "#cc2200"
            text_hover_color "#ff4422"
            text_size 24
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#1a0000ee", 4, 4)
            hover_background Frame("#330000ee", 4, 4)
            padding (24, 14)

        ## ── DRAW / DISCARD piles ──────────────────────────────────────────────
        python:
            _draw_n = len(bs.draw_pile)
            _disc_n = len(bs.discard_pile)
            _exh_n  = len(bs.exhaust_pile)

        ## Click the pile counter to open a peek modal
        textbutton "Draw: [_draw_n]   Discard: [_disc_n]   Exhaust: [_exh_n]":
            xpos 30
            ypos 1010
            action ShowMenu("battle_pile_peek")
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 14
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#1a1a1add", 4, 4)
            hover_background Frame("#2a2a2add", 4, 4)
            padding (10, 6)

        ## ── HELP "?" button ──────────────────────────────────────────────────
        textbutton "?":
            xpos 1860
            ypos 20
            action ShowMenu("battle_help")
            text_color "#888888"
            text_hover_color "#ffdd00"
            text_size 28
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#0a0a0acc", 4, 4)
            hover_background Frame("#1a1a00cc", 4, 4)
            padding (12, 4)
            tooltip "How does this fight work?"

        ## ── Active tooltip text (renders at bottom-center on hover) ─────────
        $ _tt = GetTooltip()
        if _tt:
            frame:
                xalign 0.5
                ypos 770
                padding (16, 8)
                background Frame("#0d1018ee", 4, 4)
                text "[_tt]":
                    color "#ffffff"
                    size 16
                    xalign 0.5
                    xmaximum 1200
                    text_align 0.5

        ## ── HAND ──────────────────────────────────────────────────────────────
        ## Each card: 200×280 button. Color-coded border (4px) wrapping a dark
        ## inner panel. Cost gem overlaps the top-left corner. Effect text is
        ## the centerpiece — what the card actually does, not just flavor.
        frame:
            xalign 0.5
            ypos 790
            padding (16, 10)
            background Frame("#0a0a0acc", 4, 4)

            hbox:
                spacing 14
                xalign 0.5

                for _cid in bs.hand:
                    $ _card = CARD_LIBRARY.get(_cid, {})
                    $ _color = _CARD_COLORS.get(_card.get("color", "Special"), "#888888")
                    $ _ok, _reason = bs.hand_playable(_cid)
                    $ _border = _color if _ok else "#3a1010"
                    $ _border_hover = "#ffffff" if _ok else _border
                    $ _effect_text = EFFECT_DESCRIPTIONS.get(_card.get("effect"), _card.get("flavor", ""))
                    $ _ctype = _card.get("type", "Skill")
                    ## Geometric glyphs in BMP (well-supported across fonts) — visual hierarchy for type
                    $ _type_glyph = {"Attack": "▲", "Skill": "■", "Power": "★"}.get(_ctype, "●")

                    button:
                        xsize 200
                        ysize 280
                        background Solid(_border)
                        hover_background Solid(_border_hover)
                        sensitive _ok
                        action [Function(battle_play_card, _cid), Function(renpy.restart_interaction)]
                        at card_hover_lift

                        ## Inner panel — inset 4px from each edge for the border effect
                        frame:
                            xpos 4
                            ypos 4
                            xsize 192
                            ysize 272
                            background Solid("#0d0d0dff" if _ok else "#1a0a0aff")
                            padding (10, 10)

                            vbox:
                                spacing 3
                                xfill True

                                ## Top row: name centered, room left for the cost gem corner
                                frame:
                                    xfill True
                                    ysize 32
                                    background None
                                    text _card.get("name", _cid):
                                        color ("#ffffff" if _ok else "#666666")
                                        size 15
                                        bold True
                                        xalign 0.5
                                        yalign 0.5
                                        xmaximum 160
                                        text_align 0.5
                                        font "fonts/RobotoMono-Regular.ttf"

                                ## Type strip — colored, small caps feel
                                hbox:
                                    spacing 6
                                    xalign 0.5
                                    text _type_glyph:
                                        color _color
                                        size 12
                                    text _ctype.upper():
                                        color _color
                                        size 10
                                        bold True
                                        font "fonts/RobotoMono-Regular.ttf"
                                    text "·":
                                        color "#444444"
                                        size 10
                                    text _card.get("color", "").upper():
                                        color _color
                                        size 10
                                        font "fonts/RobotoMono-Regular.ttf"

                                ## Divider
                                frame:
                                    xalign 0.5
                                    xsize 150
                                    ysize 1
                                    background Solid(_color)

                                null height 3

                                ## EFFECT — the meaty middle
                                text _effect_text:
                                    color ("#e8e8e8" if _ok else "#555555")
                                    size 12
                                    xalign 0.5
                                    xmaximum 168
                                    text_align 0.5
                                    line_spacing 2

                                null height 4

                                ## Flavor — italic, gray, smaller
                                text _card.get("flavor", ""):
                                    color ("#777777" if _ok else "#3a3a3a")
                                    size 9
                                    italic True
                                    xalign 0.5
                                    xmaximum 168
                                    text_align 0.5

                        ## Cost gem — overlaps the top-left corner of the border
                        frame:
                            xpos -4
                            ypos -4
                            xsize 36
                            ysize 36
                            background Solid(_color if _ok else "#552222")
                            text "[_card.get('cost', 0)]":
                                color ("#000000" if _ok else "#222222")
                                size 20
                                bold True
                                xalign 0.5
                                yalign 0.5
                                font "fonts/RobotoMono-Regular.ttf"

                        ## Exhaust badge — centered horizontally near the bottom
                        ## of the card, below the effect/flavor text. Larger and
                        ## brighter than the previous corner pip so it actually
                        ## reads at-a-glance.
                        if _card.get("exhaust"):
                            frame:
                                xalign 0.5
                                ypos 250
                                xsize 110
                                ysize 22
                                background Solid("#5a0000")
                                text "EXHAUST":
                                    color "#ff8866"
                                    size 12
                                    bold True
                                    xalign 0.5
                                    yalign 0.5
                                    font "fonts/RobotoMono-Regular.ttf"

        ## ── ROUND COUNTER ─────────────────────────────────────────────────────
        text "Round [bs.turn]":
            xalign 0.95
            yalign 0.45
            color "#666666"
            size 13
            font "fonts/RobotoMono-Regular.ttf"

        ## ── PHASE A JUICE OVERLAYS ────────────────────────────────────────────
        ## Damage popups (`-N` floating text rising over the hit target) and
        ## flash overlays (red on player hit, green on enemy hit). Both are
        ## driven by the engine's fx_events queue and last_*_hit_time fields.
        ## Rendering happens here at the end of the screen tree so popups/
        ## flashes layer on TOP of all other UI.
        $ _fx_now = renpy.get_game_runtime()

        ## Per-event popups — delegate to the inner screen and pass `id` keyed
        ## on the event's monotonic tick so Ren'Py treats each popup as a
        ## stable displayable identity across redraws (ATL animation runs
        ## once per event instead of restarting every redraw).
        $ _fx_events_safe = getattr(bs, 'fx_events', [])
        for _fx in _fx_events_safe:
            if _fx.get('type') == 'damage' and (_fx_now - _fx.get('t', 0)) < 0.75:
                use _damage_popup_overlay(fx=_fx) id _fx.get('tick', 0)

        ## Player-hit flash — red wash over the whole screen, brief
        $ _last_player_hit = getattr(bs, 'last_player_hit_time', -1.0)
        $ _player_hit_age = (_fx_now - _last_player_hit) if _last_player_hit > 0 else 999.0
        if _player_hit_age < 0.35:
            add Solid("#ff2222") xsize 1920 ysize 1080 at damage_flash_player

        ## Enemy-hit flash — subtle green wash
        $ _last_enemy_hit = getattr(bs, 'last_enemy_hit_time', -1.0)
        $ _enemy_hit_age = (_fx_now - _last_enemy_hit) if _last_enemy_hit > 0 else 999.0
        if _enemy_hit_age < 0.30:
            add Solid("#00ff41") xsize 1920 ysize 1080 at damage_flash_enemy

        ## ── PHASE C TURN BANNER ───────────────────────────────────────────────
        ## use ... id keyed on bs.turn so each turn is a fresh ATL mount.
        ## Animation runs once on mount, settles invisible after 1.4s, persists
        ## quietly until the next turn change re-keys the id.
        if bs.turn > 0:
            use turn_banner_inner(turn_n=bs.turn) id "turn_banner_{}".format(bs.turn)

        ## ── Auto-end VICTORY / DEFEAT fanfare (Phase D) ──────────────────────
        ## Rendered LAST in the screen so the dim overlay + splash card layer
        ## on top of the colonel portrait, hand cards, and every other UI
        ## element. Earlier versions placed this near the top → portrait
        ## rendered after splash → covered the VICTORY text. Document order
        ## IS z-order in Ren'Py screens; this block must stay at the bottom.
        if bs.over == "victory":
            add Solid("#001a00cc") xsize 1920 ysize 1080
            frame:
                xalign 0.5
                yalign 0.5
                padding (80, 50)
                background Frame("#001a00ee", 6, 6)
                vbox:
                    spacing 14
                    xalign 0.5
                    text "VICTORY":
                        color "#00ff41"
                        size 96
                        bold True
                        xalign 0.5
                        font "fonts/RobotoMono-Regular.ttf"
                        outlines [(4, "#000000", 0, 0)]
                        at battle_end_fanfare
                    text "His face is empty. He has nothing left to say.":
                        color "#88ff88"
                        size 20
                        italic True
                        xalign 0.5
                        at battle_end_subtitle
                    text "HP {}/{}  ·  Round {}".format(bs.player_hp, bs.player_max_hp, bs.turn):
                        color "#557755"
                        size 14
                        xalign 0.5
                        font "fonts/RobotoMono-Regular.ttf"
                        at battle_end_subtitle
            timer 2.5 action Return("victory")

        if bs.over == "defeat":
            add Solid("#1a0000cc") xsize 1920 ysize 1080
            frame:
                xalign 0.5
                yalign 0.5
                padding (80, 50)
                background Frame("#1a0000ee", 6, 6)
                vbox:
                    spacing 14
                    xalign 0.5
                    text "DEFEAT":
                        color "#ff2222"
                        size 96
                        bold True
                        xalign 0.5
                        font "fonts/RobotoMono-Regular.ttf"
                        outlines [(4, "#000000", 0, 0)]
                        at battle_end_fanfare
                    text "You sit back down. The room goes quiet.":
                        color "#ff8888"
                        size 20
                        italic True
                        xalign 0.5
                        at battle_end_subtitle
                    text "Round {}".format(bs.turn):
                        color "#775555"
                        size 14
                        xalign 0.5
                        font "fonts/RobotoMono-Regular.ttf"
                        at battle_end_subtitle
            timer 2.5 action Return("defeat")
