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
## These are read by `screen battle_screen()` to render the floating "-N"
## damage popups, the colonel portrait shake on hits, and screen-edge flash
## overlays. All are gated on `battle_state.last_*_hit_time` / `last_damage_*`
## timestamps, set by `cards/battle_engine.rpy` the instant damage lands. If
## no hit has happened recently the transforms simply fade to alpha 0.
## ---------------------------------------------------------------------------

init python:
    import math as _juice_math

    def _colonel_shake_fn(trans, st, at):
        """Damped 2-axis oscillation on the enemy portrait (and anything else
        wearing this transform). Beefed up to feel like screen-shake on
        impact: ~26px horizontal + ~14px vertical oscillation, 0.45s decay.
        Fires when battle_state.last_enemy_hit_time is recent."""
        bs = battle_state
        if bs is None or getattr(bs, 'last_enemy_hit_time', -1.0) < 0:
            trans.xoffset = 0
            trans.yoffset = 0
            return None
        try:
            age = renpy.get_game_runtime() - bs.last_enemy_hit_time
        except Exception:
            trans.xoffset = 0
            trans.yoffset = 0
            return None
        if age >= 0.45:
            trans.xoffset = 0
            trans.yoffset = 0
            return None
        ## Decay envelope: amplitude tapers to 0 over 0.45s
        decay = 1.0 - age / 0.45
        ## Mixed-frequency oscillation feels chunkier than a clean sine
        trans.xoffset = int(26.0 * decay * _juice_math.sin(age * 32.0))
        trans.yoffset = int(14.0 * decay * _juice_math.sin(age * 47.0))
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

    def _enemy_idle_breath_fn(trans, st, at):
        """Continuous low-amplitude breathing on the enemy sprite — sells
        'alive' on a static PNG. Slow sine on zoom (1.000↔1.014) and a
        smaller out-of-phase sine on yoffset. Always returns 0.033 so the
        screen keeps polling (also keeps lunge/stance transforms reactive
        to fresh timestamps even when nothing else is animating)."""
        bs = battle_state
        if bs is None or getattr(bs, 'over', None):
            trans.zoom = 1.0
            trans.yoffset = 0
            return None
        phase = _juice_math.sin(st * (2.0 * _juice_math.pi / 3.2))
        trans.zoom = 1.0 + 0.014 * phase
        trans.yoffset = int(-2.5 * _juice_math.sin(st * (2.0 * _juice_math.pi / 3.2) + 0.4))
        return 0.033

    def _enemy_intent_stance_fn(trans, st, at):
        """Posture shift based on the current intent. Attack/compound → lean
        in (zoom up + yoffset down). Block → settle back (zoom down + lift).
        Other → neutral. Eases ~10%/frame toward target so transitions feel
        like the enemy shifting weight rather than snapping into pose."""
        bs = battle_state
        if bs is None or getattr(bs, 'over', None):
            target_z, target_y = 1.0, 0.0
        else:
            ic = bs.current_intent() if hasattr(bs, 'current_intent') else None
            kind = ic.get("intent", "") if ic else ""
            if kind in ("attack", "compound"):
                target_z, target_y = 1.020, 4.0
            elif kind == "block":
                target_z, target_y = 0.990, -2.0
            else:
                target_z, target_y = 1.0, 0.0
        ## In function-mode ATL the `trans` TransformState persists across
        ## frames, so this frame's write is next frame's read — that's the
        ## lerp's memory. (Unique pattern in this file; don't "simplify"
        ## back to a stateless recompute or the easing dies.)
        cur_z = trans.zoom if trans.zoom is not None else 1.0
        cur_y = float(trans.yoffset) if trans.yoffset is not None else 0.0
        trans.zoom = cur_z + (target_z - cur_z) * 0.10
        trans.yoffset = int(cur_y + (target_y - cur_y) * 0.10)
        return 0.033

    def _enemy_attack_lunge_fn(trans, st, at):
        """On enemy attack landing, snap forward (zoom up + yoffset down)
        over 0.08s, then ease back over 0.22s. Driven by
        last_enemy_attack_time, which is only set when source_kind='intent'
        — so the enemy doesn't lunge when the player plays a self-damage
        card."""
        bs = battle_state
        t_hit = getattr(bs, 'last_enemy_attack_time', -1.0) if bs is not None else -1.0
        if t_hit < 0:
            trans.zoom = 1.0
            trans.yoffset = 0
            return None
        try:
            age = renpy.get_game_runtime() - t_hit
        except Exception:
            trans.zoom = 1.0
            trans.yoffset = 0
            return None
        if age >= 0.30:
            trans.zoom = 1.0
            trans.yoffset = 0
            return None
        if age < 0.08:
            p = age / 0.08
            trans.zoom = 1.0 + 0.11 * p
            trans.yoffset = int(14 * p)
        else:
            p = (age - 0.08) / 0.22
            trans.zoom = 1.11 - 0.11 * p
            trans.yoffset = int(14 * (1.0 - p))
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

    def _dmg_popup_compute(trans, hit_time):
        """Float a damage number up ~70px and fade it over 0.85s, driven by
        a wall-clock hit timestamp. ALWAYS returns 0.016 — the transform must
        keep polling even after one animation finishes so a later hit can
        re-animate the same displayable without being remounted. Ren'Py
        will not restart a transform that returned None; that was the
        cause of the long-standing 'damage numbers only show sometimes'
        bug. Alpha drops to 0 between hits — the widget is permanently
        mounted but invisible when there's no recent damage to display."""
        if hit_time < 0:
            trans.alpha = 0.0
            return 0.016
        try:
            age = renpy.get_game_runtime() - hit_time
        except Exception:
            trans.alpha = 0.0
            return 0.016
        if age < 0.0 or age >= 0.85:
            trans.alpha = 0.0
            trans.yoffset = -70
            return 0.016
        trans.yoffset = int(-70.0 * (age / 0.85))
        trans.alpha = 1.0 if age < 0.5 else max(0.0, 1.0 - (age - 0.5) / 0.35)
        return 0.016

    def _dmg_popup_enemy_fn(trans, st, at):
        bs = battle_state
        if bs is None:
            trans.alpha = 0.0
            return None
        return _dmg_popup_compute(trans, getattr(bs, 'last_enemy_hit_time', -1.0))

    def _dmg_popup_player_fn(trans, st, at):
        bs = battle_state
        if bs is None:
            trans.alpha = 0.0
            return None
        return _dmg_popup_compute(trans, getattr(bs, 'last_player_hit_time', -1.0))

transform colonel_hit_shake:
    function _colonel_shake_fn

transform enemy_idle_breath:
    function _enemy_idle_breath_fn

transform enemy_intent_stance:
    function _enemy_intent_stance_fn

transform enemy_attack_lunge:
    function _enemy_attack_lunge_fn

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

## End-turn warn pulse — slow alpha breathing on the END TURN button when
## the player still has unspent energy. Visual nag, not a hard block.
transform _energy_warn_pulse:
    alpha 1.0
    linear 0.7 alpha 0.55
    linear 0.7 alpha 1.0
    repeat

## Hatred-past-100 alarm — the combat readout throbs red once the player
## crosses into the final danger band (only reachable by Bodybuilder, whose
## breakdown cap is 125). Alpha pulse only — no zoom, so it never reflows the
## status vbox beneath it.
transform hatred_over_glow:
    alpha 1.0
    easeout 0.5 alpha 0.5
    easein 0.5 alpha 1.0
    repeat


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

transform enemy_dmg_popup:
    function _dmg_popup_enemy_fn

transform player_dmg_popup:
    function _dmg_popup_player_fn


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


## ATL for the "-N" damage popups. One-shot animation: float up 70px while
## fading out over 0.85s. Used by damage_popup_enemy_inner / _player_inner.
transform damage_popup_atl:
    alpha 1.0
    yoffset 0
    parallel:
        linear 0.85 yoffset -70
    parallel:
        pause 0.5
        linear 0.35 alpha 0.0

## Parameterized variant — multi-hit compound attacks pass a per-hit delay
## so the -N popups stagger in time (StS-style hit-by-hit visual feedback)
## instead of all five collapsing into the last frame. delay=0 behaves
## identically to damage_popup_atl above.
transform damage_popup_atl_delayed(delay=0.0):
    alpha 0.0
    pause delay
    alpha 1.0
    yoffset 0
    parallel:
        linear 0.85 yoffset -70
    parallel:
        pause 0.5
        linear 0.35 alpha 0.0


## Inner screens for damage popups. Wrapped via `use damage_popup_<x>_inner(
## damage=N) id "<x>_dmg_popup_<hit_time>"` from battle_screen — same proven
## pattern as turn_banner_inner above. Each hit gets a unique id (keyed on
## the hit timestamp), so Ren'Py mounts a fresh displayable + fires the ATL
## from frame 0 every time. Pure animation, no transform-function timing
## races. This is what replaces the long-standing flaky popup pipeline.
screen damage_popup_enemy_inner(damage, delay=0.0, xoff=0):
    ## zorder 800 — must render ABOVE battle_screen (zorder 600). Without this
    ## explicit zorder the popup mounts but draws BEHIND battle_screen's full-
    ## screen background, so it's invisible in-fight (but visible from console
    ## tests because the console opens at a higher zorder). This was the actual
    ## root cause of the "popups never show in fights" bug.
    zorder 800
    ## Per-popup thud — fires AT the visible-popup moment, not when damage is
    ## dealt. Multi-hit compounds now get one thud per number, staggered.
    ## hit_thud.* was never authored; enemy_hit.wav is the punch impact, and
    ## REQUIRED_SFX.md specs one shared hit sound for both sides.
    timer (delay if delay > 0 else 0.01) action Function(_play_battle_sfx, "enemy_hit") repeat False
    text "-[damage]":
        xalign 0.5
        xoffset xoff
        ypos 195
        color "#ffdd44"
        size 88
        bold True
        outlines [(4, "#000000", 0, 0)]
        font "fonts/RobotoMono-Regular.ttf"
        at damage_popup_atl_delayed(delay)

screen damage_popup_player_inner(damage, delay=0.0, xoff=0):
    zorder 800
    timer (delay if delay > 0 else 0.01) action Function(_play_battle_sfx, "enemy_hit") repeat False
    text "-[damage]":
        xpos 130
        xoffset xoff
        ypos 500
        color "#ff4422"
        size 88
        bold True
        outlines [(4, "#000000", 0, 0)]
        font "fonts/RobotoMono-Regular.ttf"
        at damage_popup_atl_delayed(delay)

## Phase B juice — card hover lift. Cards in hand scale up + lift slightly
## on mouse-hover, settle on idle. Smooth ease so the cursor's-on-this-card
## affordance is unmistakable. ATL `on hover` / `on idle` blocks fire when
## the parent button transitions states.
transform card_hover_lift:
    on hover:
        ease 0.14 zoom 1.07 yoffset -18
    on idle:
        ease 0.14 zoom 1.0 yoffset 0

## Slow alpha breath on the playable-card halo. Signals castability across
## the whole hand at a glance — eyes lock to the pulsing colored rings.
transform card_glow_pulse:
    alpha 0.55
    linear 1.2 alpha 0.95
    linear 1.2 alpha 0.55
    repeat

## Reward-card hover lift — stronger than the battle hover-lift since reward
## cards are bigger and the player is meant to compare them up-close. Click
## anywhere on the card body to take it. `xoff` lets the call site spread
## the card AWAY from the centre on hover (left card leans left, right card
## leans right) so the lifted card doesn't visually overlap its neighbours.
transform reward_card_hover(xoff=0):
    on hover:
        ease 0.18 zoom 1.08 yoffset -24 xoffset xoff
    on idle:
        ease 0.18 zoom 1.0 yoffset 0 xoffset 0


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
                text "The icon above the enemy's head shows what they'll do next turn:":
                    color "#cccccc"
                    size 14
                text "  🗡 ATTACK — deals N damage   ⚔ COMPOUND — N×hits damage   🛡 BLOCK — gains block":
                    color "#aaaaaa"
                    size 13
                text "  ↑ BUFF — next attack +N dmg   🃏↓ DEBUFF — -N draw next turn   ⚡↓ DEBUFF — -N energy next turn":
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
                text "Power cards (job_offer, stoic_anchor, iron_stance, etc.) cost energy to play. Once played, the buff lasts the rest of the fight. The card exhausts on play and the buff resets every combat.":
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
                                    $ _c_is_status     = (_c.get("effect") or "").startswith("status_")
                                    $ _c_is_rage       = bool(_c.get("is_rage"))
                                    $ _c_is_compromise = bool(_c.get("is_compromise"))
                                    if _c_is_compromise:
                                        $ _ccol = "#5a5550"
                                        $ _c_prefix = "🚫 "
                                        $ _c_name_color = "#a09890"
                                    elif _c_is_rage:
                                        $ _ccol = "#aa1a1a"
                                        $ _c_prefix = "🔥 "
                                        $ _c_name_color = "#ff8866"
                                    elif _c_is_status:
                                        $ _ccol = "#8a7a2a"
                                        $ _c_prefix = "☠ "
                                        $ _c_name_color = "#d4c47a"
                                    else:
                                        $ _ccol = _PEEK_COLORS.get(_c.get("color", "Special"), "#888888")
                                        $ _c_prefix = ""
                                        ## Upgraded cards (clean — never corruption) → green name.
                                        $ _c_name_color = card_name_color(_c, "#ffffff")
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
                                            text "{}{}".format(_c_prefix, _c.get("name", _cid)):
                                                color _c_name_color
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
        ## Per-enemy battle background.
        ##   Colonel: state-tracked office (smug/normal/angry/shaken) progressively
        ##   collapses as his HP drops; falls back to pristine office if a state
        ##   render is missing.
        ##   Ladder enemies: static bg_<sprite_id>.jpg.
        _battle_bg_img = None
        _bg_is_colonel = False
        if bs is not None:
            _sprite_id = getattr(bs, 'enemy_sprite_id', '')
            if bs.enemy_hp <= 0 or bs.enemy_hp <= bs.enemy_max_hp * 0.12:
                _bg_state = "shaken"
            elif bs.enemy_hp <= bs.enemy_max_hp * 0.30:
                _bg_state = "angry"
            elif bs.enemy_hp >= bs.enemy_max_hp * 0.80:
                _bg_state = "smug"
            else:
                _bg_state = "normal"
            _bg_state_path  = "images/backgrounds/{}_office_{}.jpg".format(_sprite_id, _bg_state)
            ## bg_id override: enemies whose battle bg lives under a different
            ## filename than the sprite (e.g. lawyer → bg_courtroom.jpg) declare
            ## bg_id in ENEMY_LIBRARY. Defaults to sprite_id when unset.
            _bg_id = (ENEMY_LIBRARY.get(bs.enemy_id, {}) or {}).get("bg_id") or _sprite_id
            _bg_static_path = "images/backgrounds/bg_{}.jpg".format(_bg_id)
            if _sprite_id == "colonel":
                _bg_is_colonel = True
                if renpy.loadable(_bg_state_path):
                    _battle_bg_img = _bg_state_path
                else:
                    _battle_bg_img = "images/backgrounds/police_station_colonel_office.jpg"
            elif renpy.loadable(_bg_static_path):
                _battle_bg_img = _bg_static_path

    add "#0a0a0a"
    if _battle_bg_img:
        add Transform(_battle_bg_img, size=(config.screen_width, config.screen_height))
    ## Darken the bg so it sits behind the UI without fighting card colors.
    ## Colonel uses a lighter darken so the office destruction reads through.
    if _bg_is_colonel:
        add Solid("#00000066")
    else:
        add Solid("#00000099")

    ## Class-color top + bottom border framing the entire fight.
    use class_color_frame(thickness=6)

    if bs is None:
        text "[[BATTLE STATE NULL]" xalign 0.5 yalign 0.5 color "#ff0000" size 32
    else:
        ## ── Background portrait ────────────────────────────────────────────────
        ## Sprite tracks the fight: smug while he's winning, composed mid-fight,
        ## furious when cornered, mask cracking when nearly beaten.
        ## Ladder enemies only ship "<id> neutral" sprites — has_image check
        ## falls back to neutral when the emotional state isn't defined.
        python:
            _sprite_base = getattr(bs, 'enemy_sprite_id', 'colonel')
            if bs.enemy_hp <= 0 or bs.enemy_hp <= bs.enemy_max_hp * 0.12:
                _state = "shaken"
            elif bs.enemy_hp <= bs.enemy_max_hp * 0.30:
                _state = "angry"
            elif bs.enemy_hp >= bs.enemy_max_hp * 0.80:
                _state = "smug"
            else:
                _state = "normal"
            _sprite_tag = "{} {}".format(_sprite_base, _state)
            if not renpy.has_image(_sprite_tag, exact=True):
                _sprite_tag = "{} neutral".format(_sprite_base)
            ## Garda sprite sits 80px lower than the rest of the roster —
            ## the source art has more empty head-room above the figure, so
            ## the standard ypos floats him too high on screen.
            _sprite_ypos = 880 if _sprite_base == "garda" else 800
        ## Sprite is bottom-anchored so the (often torso-cropped) lower edge
        ## tucks behind the card hand instead of floating mid-screen.
        add _sprite_tag xalign 0.5 ypos _sprite_ypos yanchor 1.0 zoom 0.69 at (colonel_hit_shake, enemy_attack_lunge, enemy_intent_stance, enemy_idle_breath)

        ## ── VIGNETTE ──────────────────────────────────────────────────────────
        ## Bottom-band darken between sprite and UI: punches cards forward
        ## against a dimmed backdrop. All UI panels (HP, buffs, energy,
        ## end-turn, pile counter, hand) render ABOVE this layer so the
        ## info chrome stays bright while the play area dramatizes.
        add Solid("#000000bb") xsize 1920 ysize 320 ypos 760

        ## ── ENEMY HEADER ──────────────────────────────────────────────────────
        ## Shakes alongside the enemy portrait on hits so impact reads as
        ## a "screen shake" feel without wrapping the whole tree in a transform.
        frame at colonel_hit_shake:
            xalign 0.5
            yalign 0.0
            yoffset 16
            padding (24, 12)
            background None
            xsize 1100

            vbox:
                spacing 6
                xalign 0.5

                hbox:
                    spacing 16
                    xalign 0.5

                    text "[bs.enemy_name!u]":
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

                    ## Permanent Strength badge — flags the ramp boss intent.
                    ## Reads "STR +N" in red-orange, only visible when stacked.
                    if bs.enemy_strength > 0:
                        text "💪 +[bs.enemy_strength]":
                            color "#ff8822"
                            size 18
                            bold True
                            font "fonts/RobotoMono-Regular.ttf"

                    ## Hooligan CREW RAGE badge — visible on fanousek fights at
                    ## all times so the threshold mechanic is explicit from
                    ## turn 1. Dim grey + "armed" tooltip when above threshold,
                    ## bright red + "active" tooltip once HP drops below it.
                    ## Hover tooltip surfaces via GetTooltip() below the hand.
                    if bs.enemy_id == "fanousek":
                        python:
                            _crew_wd     = ENEMY_LIBRARY.get("fanousek", {}).get("wrinkle_data", {})
                            _crew_thr    = _crew_wd.get("hp_threshold", 0.5)
                            _crew_bonus  = _crew_wd.get("bonus_dmg", 4)
                            _crew_thr_hp = int(bs.enemy_max_hp * _crew_thr)
                            _crew_armed  = bs.enemy_hp <= _crew_thr_hp
                            if _crew_armed:
                                _crew_color = "#ff5522"
                                _crew_hover_bg = Frame("#330011cc", 4, 4)
                                _crew_tip = "Crew Rage: attacks +{} damage per hit.".format(_crew_bonus)
                            else:
                                _crew_color = "#886655"
                                _crew_hover_bg = Frame("#1a0a05cc", 4, 4)
                                _crew_tip = "Crew Rage: attacks gain +{} damage per hit at or below {} HP.".format(_crew_bonus, _crew_thr_hp)
                        textbutton "🔥 RAGE":
                            action NullAction()
                            tooltip _crew_tip
                            text_color _crew_color
                            text_hover_color "#ffffff"
                            text_size 18
                            text_bold True
                            text_font "fonts/RobotoMono-Regular.ttf"
                            background None
                            hover_background _crew_hover_bg
                            padding (6, 1)

                    ## Vlk BUY-IN badge — the Margin Call exposure counter.
                    ## Visible from turn 1 so the scaling mechanic is explicit;
                    ## colour climbs grey → orange → red as exposure builds.
                    if bs.enemy_id == "vlk":
                        python:
                            _buyin      = bs.buffs.get("vlk_buyin", 0)
                            _vlk_wd     = ENEMY_LIBRARY.get("vlk", {}).get("wrinkle_data", {})
                            _buyin_per  = _vlk_wd.get("margin_per_buyin", 5)
                            _buyin_drop = _vlk_wd.get("bluff_drop", 2)
                            if _buyin >= 6:
                                _buyin_color = "#ff3322"
                            elif _buyin >= 3:
                                _buyin_color = "#ffaa33"
                            else:
                                _buyin_color = "#887766"
                            _buyin_tip = "Buy-In {}: Margin Call deals +{} damage. Breaking his Sebejistota block drops it by {}.".format(_buyin, _buyin * _buyin_per, _buyin_drop)
                        textbutton "📈 BUY-IN [_buyin]":
                            action NullAction()
                            tooltip _buyin_tip
                            text_color _buyin_color
                            text_hover_color "#ffffff"
                            text_size 18
                            text_bold True
                            text_font "fonts/RobotoMono-Regular.ttf"
                            background None
                            hover_background Frame("#0a1430cc", 4, 4)
                            padding (6, 1)

                ## ── INTENT INFOGRAPHICS ───────────────────────────────────────
                ## Each peeked intent renders as a small icon+value panel with
                ## the intent name in italic gray below. Type → glyph + color:
                ##   attack       🗡 <dmg>             red       (+N if bonus queued)
                ##   compound     ⚔ <val>×<hits>      red
                ##   block        🛡 <block>          blue
                ##   buff         ↑ +N dmg next       orange    (enemy_attack_bonus stack)
                ##   debuff/draw  🃏↓ -N draw         purple
                ##   debuff/nrg   ⚡↓ -N energy       purple
                ## Threat tiering escalates ONLY on the current intent (i==0) so
                ## the player's eye lands on the imminent hit. Bonus-damage
                ## fidelity: when an attack is queued AND enemy_attack_bonus is
                ## sitting in buffs (cold_stare / rvac / fanousek chant ramp),
                ## the value renders as "<base> (+<bonus>)" — purely cosmetic,
                ## no buff mutation.
                python:
                    _ic = bs.current_intent()
                    _peek = []
                    if _ic:
                        _peek.append(_ic)
                    for _i in range(1, min(bs.intent_revealed, 5)):
                        idx = bs.intent_index + _i
                        if 0 <= idx < len(bs.intent_queue):
                            _peek.append(ENEMY_DECK_LIBRARY.get(bs.intent_queue[idx]))
                    _enemy_atk_bonus = bs.buffs.get("enemy_attack_bonus", 0)
                    ## Wrinkle damage bonuses that the display must reflect to
                    ## stay honest with the engine. Mirror the engine math from
                    ## _resolve_intent. Hooligan crew rage at low HP is the
                    ## only current case (garda formation is +above-50%, not a
                    ## per-hit bump on a single intent — applied silently).
                    _wrinkle_bonus = 0
                    if bs.enemy_id == "fanousek":
                        _fwd = ENEMY_LIBRARY.get("fanousek", {}).get("wrinkle_data", {})
                        _fthr = _fwd.get("hp_threshold", 0.5)
                        if bs.enemy_hp <= int(bs.enemy_max_hp * _fthr):
                            _wrinkle_bonus = _fwd.get("bonus_dmg", 4)

                if _peek:
                    hbox:
                        spacing 12
                        xalign 0.5

                        for _i, _intent in enumerate(_peek):
                            if _intent:
                                python:
                                    _label = _intent.get("name", "?")
                                    _itype = _intent.get("intent", "attack")
                                    _is_current = (_i == 0)

                                    if _itype == "attack":
                                        _icon = "🗡"
                                        _ic_color = "#ff4422"
                                        _base = _intent.get("value", 0) + _wrinkle_bonus
                                        ## Vlk Margin Call — gated on THIS peeked
                                        ## intent so the Buy-In scaling never
                                        ## leaks onto a peeked vlk_hard_sell.
                                        ## Mirrors battle_engine.rpy resolve math.
                                        if bs.enemy_id == "vlk" and _intent.get("id") == "vlk_margin_call":
                                            _mc_per = ENEMY_LIBRARY.get("vlk", {}).get("wrinkle_data", {}).get("margin_per_buyin", 5)
                                            _base += _mc_per * bs.buffs.get("vlk_buyin", 0)
                                        _dmg_for_threat = _base
                                        if _is_current and _enemy_atk_bonus > 0:
                                            _val_text = "{} (+{})".format(_base, _enemy_atk_bonus)
                                            _dmg_for_threat = _base + _enemy_atk_bonus
                                        else:
                                            _val_text = "{}".format(_base)
                                    elif _itype == "compound":
                                        _icon = "⚔"
                                        _ic_color = "#ff6644"
                                        _per_hit = _intent.get("value", 0) + _wrinkle_bonus
                                        _hits = _intent.get("value2", 1)
                                        _val_text = "{}×{}".format(_per_hit, _hits)
                                        _dmg_for_threat = _per_hit * _hits
                                    elif _itype == "block":
                                        _icon = "🛡"
                                        _ic_color = "#88aaff"
                                        _val_text = "{}".format(_intent.get("value", 0))
                                        _dmg_for_threat = 0
                                    elif _itype == "buff":
                                        _icon = "↑"
                                        _ic_color = "#ffaa44"
                                        _val_text = "+{} dmg next".format(_intent.get("value", 0))
                                        _dmg_for_threat = 0
                                    elif _itype == "strength":
                                        ## Permanent attack bump for the rest of the fight.
                                        ## Red-orange to read as "more dangerous over time."
                                        _icon = "💪"
                                        _ic_color = "#ff8822"
                                        _val_text = "+{} STR".format(_intent.get("value", 0))
                                        _dmg_for_threat = 0
                                    elif _itype == "restrict":
                                        ## Card-play cap on your next turn — purple, sharp glyph.
                                        _icon = "🚫"
                                        _ic_color = "#cc44cc"
                                        _val_text = "Max {} card(s)".format(_intent.get("value", 1))
                                        _dmg_for_threat = 0
                                    elif _itype == "debuff":
                                        _ic_color = "#aa44cc"
                                        _dkey = _intent.get("debuff_key", "player_draw_penalty")
                                        if _dkey == "max_energy_penalty_next_turn":
                                            _icon = "⚡↓"
                                            _val_text = "-{} energy".format(_intent.get("value", 1))
                                        else:
                                            _icon = "🃏↓"
                                            _val_text = "-{} draw".format(_intent.get("value", 1))
                                        _dmg_for_threat = 0
                                    elif _itype == "moneydrain":
                                        ## Vlk Buy-In — drains run money, not HP.
                                        _icon = "💸"
                                        _ic_color = "#cc66cc"
                                        _val_text = "-{} Kč".format(_intent.get("value", 0))
                                        _dmg_for_threat = 0
                                    elif _itype == "dividend":
                                        ## Vlk Dividend — heals you. The bait.
                                        _icon = "🎁"
                                        _ic_color = "#66cc88"
                                        _val_text = "+{} HP".format(_intent.get("value", 0))
                                        _dmg_for_threat = 0
                                    else:
                                        _icon = "?"
                                        _ic_color = "#888888"
                                        _val_text = "?"
                                        _dmg_for_threat = 0

                                    ## Threat tier — current intent only.
                                    if _is_current and _dmg_for_threat >= 15:
                                        _val_size = 24
                                        _val_color = "#ff2222"
                                        _panel_bg = "#3a0000ee"
                                        _icon_size = 26
                                    elif _is_current and _dmg_for_threat >= 8:
                                        _val_size = 22
                                        _val_color = "#ffcc44"
                                        _panel_bg = "#2a1a00dd"
                                        _icon_size = 24
                                    elif _is_current:
                                        _val_size = 20
                                        _val_color = "#ffffff"
                                        _panel_bg = "#1a1a1add"
                                        _icon_size = 22
                                    else:
                                        _val_size = 16
                                        _val_color = "#888888"
                                        _panel_bg = "#1a1a1add"
                                        _icon_size = 18

                                frame:
                                    background Frame(_panel_bg, 4, 4)
                                    padding (10, 6)
                                    vbox:
                                        spacing 1
                                        xalign 0.5
                                        hbox:
                                            spacing 6
                                            xalign 0.5
                                            text _icon:
                                                color _ic_color
                                                size _icon_size
                                            text "[_val_text]":
                                                color _val_color
                                                size _val_size
                                                bold _is_current
                                                font "fonts/RobotoMono-Regular.ttf"
                                        text "[_label]":
                                            color "#888888"
                                            size 11
                                            italic True
                                            xalign 0.5
                                            font "fonts/RobotoMono-Regular.ttf"

        ## ── BATTLE LOG removed per playtest report. Damage popups, intent
        ## icons, and the active-buff row carry the feedback channels. The
        ## log was screen-noise that the playtester didn't read.
        ## (Engine still appends to bs.log so debug_battle traces survive.)

        ## ── PLAYER STATUS (left side) ──────────────────────────────────────
        ## player_frame_hit_shake fires for ~0.30s after player takes damage.
        frame:
            at player_frame_hit_shake
            xpos 20
            ypos 580
            xsize 360
            padding (16, 12)
            background None

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

                ## Hatred readout — the run stat the Hatred archetype juggles.
                ## Climbs toward the breakdown cap; colour escalates as a warning.
                ## Past 100 (BB-only territory — their cap is 125) the readout
                ## throbs red: the final danger band before breakdown.
                python:
                    _hat_val = stats.pcr_hatred if stats else 0
                    _hat_cap = hatred_cap()
                    _hat_r   = (_hat_val / float(_hat_cap)) if _hat_cap else 0.0
                    _hat_over = _hat_val > 100
                    if _hat_over:
                        _hat_col = "#ff2a1a"
                    elif _hat_r >= 0.85:
                        _hat_col = "#ff3322"
                    elif _hat_r >= 0.6:
                        _hat_col = "#ffaa22"
                    else:
                        _hat_col = "#cc8866"
                if _hat_over:
                    text "HATRED [_hat_val] / [_hat_cap]":
                        color _hat_col
                        size 16
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"
                        at hatred_over_glow
                else:
                    text "HATRED [_hat_val] / [_hat_cap]":
                        color _hat_col
                        size 16
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"

                if bs.player_block > 0:
                    ## Phase E — block_gain_pulse pumps zoom 1.0 -> 1.3 -> 1.0
                    ## over 0.4s after gain_block fires. No-op when no recent gain.
                    text "🛡 [bs.player_block]":
                        color "#88aaff"
                        size 18
                        bold True
                        at block_gain_pulse

                ## Card-play restriction banner — appears when a 'restrict'
                ## intent has capped the player's plays this turn. Shows the
                ## remaining budget so the player can plan the one card that
                ## matters most.
                if bs.current_turn_max_cards is not None:
                    $ _restrict_left = max(0, bs.current_turn_max_cards - bs.cards_played_this_turn)
                    text "🚫 RESTRICTED: [_restrict_left]/[bs.current_turn_max_cards] cards":
                        color ("#ff5555" if _restrict_left == 0 else "#cc44cc")
                        size 16
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"

                ## Active buffs — icon grid. Each buff renders as a small icon
                ## chip with the stack count; hover surfaces the mechanic via
                ## the global GetTooltip() consumer below the hand.
                python:
                    ## Internal state flags that live on bs.buffs but aren't
                    ## meaningful player-facing buffs. Filtered out of the
                    ## chip row so they don't render as "✦"/"[?]" tofu.
                    _BUFF_HIDDEN = {
                        "rvac_doubled",
                        "grundza_detonated",
                        "mirror_armed_for_counter",
                        "paragraph_4b_armed",
                        "job_offer_armed",
                        "took_the_heat_armed",
                        "sprejeri_tags",
                        "thick_skull_used",
                    }
                    _BUFF_ICONS = {
                        "starting_block_+1":           "🛡",
                        "stoic_anchor_block":          "🛡",
                        "stoic_anchor_heal":           "❤",
                        "soma_starting_block":         "💪",
                        "presence_charges":            "🛡",
                        "read_charges":                "👁",
                        "kick_charges":                "🃏",
                        "mental_dr_50":                "🧠",
                        "special_dr_50":               "🧠",
                        "iron_stance_active":          "⚔",
                        "single_retaliate_dmg":        "⚔",
                        "vigil_next_turn_block":       "🛡",
                        "insight_block":               "🛡",
                        "insight_turns_left":          "⏳",
                        "block_next_turn":             "🛡",
                        "double_next_attack":          "⚡",
                        "mirror_next":                 "🪞",
                        "mirror_cooldown":             "⏳",
                        "reframe_next":                "🔄",
                        "next_attack_reduction":       "🛡",
                        "bleed_dmg":                   "🩸",
                        "bleed_turns":                 "⏳",
                        "crash_next_turn":             "💥",
                        "max_energy_penalty_next_turn":"⚡",
                        "skip_next_turn":              "💤",
                        "cards_cap_next_turn":         "🚫",
                        "enemy_attack_bonus":          "🔥",
                        "player_draw_penalty":         "🃏",
                        "see_red":                     "🔥",
                        "thick_skull":                 "🛡",
                        "iron_posture":                "🛡",
                        "roid_rage":                   "🩸",
                    }
                    _BUFF_LABELS = {
                        "starting_block_+1":   "+1 Starting Block",
                        "stoic_anchor_block":  "Stoic Anchor (block)",
                        "stoic_anchor_heal":   "Stoic Anchor (heal)",
                        "soma_starting_block": "SOMA",
                        "cards_cap_next_turn": "Card Restriction (next turn)",
                        "special_dr_50":       "Special DR",
                        "presence_charges":    "Presence",
                        "read_charges":        "Read",
                        "kick_charges":        "Kick",
                        "mental_dr_50":        "Stoic Refactor",
                        "iron_stance_active":  "Iron Stance",
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
                    _BUFF_TIPS = {
                        "starting_block_+1":    "Gain +1 block at the start of every turn.",
                        "stoic_anchor_block":   "Stoic Anchor: gain {v} extra block at the start of every turn.",
                        "stoic_anchor_heal":    "Stoic Anchor: heal {v} HP each time you take damage.",
                        "soma_starting_block":  "SOMA: +{v} starting block per turn (Bodybuilder stack bonus).",
                        "presence_charges":     "Presence (Bodybuilder): +3 free block at the start of each of your next {v} turn(s).",
                        "read_charges":         "Read (Dark Empath): see one extra upcoming enemy intent at the start of each of your next {v} turn(s).",
                        "kick_charges":         "Kick (Biohacker): draw 1 extra card at the start of each of your next {v} turn(s).",
                        "mental_dr_50":         "Stoic Refactor: MENTAL-typed enemy attacks deal half damage to you.",
                        "iron_stance_active":   "Iron Stance: when you take damage, retaliate for damage that grows each round (4 on round 1, +2 per round after).",
                        "single_retaliate_dmg": "Iron Body: the next time you take damage, retaliate for {v} damage (one use).",
                        "vigil_next_turn_block":"Vigil: gain +{v} block at the start of your next turn.",
                        "insight_block":        "Insight: gain bonus block at the start of your turn.",
                        "insight_turns_left":   "Insight: {v} more turn(s) of bonus block.",
                        "block_next_turn":      "Procedural Defense: block ALL damage on your next turn.",
                        "double_next_attack":   "Personal Record: your next Attack card hits twice.",
                        "mirror_next":          "Mirror (armed): reflect the enemy's next attack back at DOUBLE damage instead of taking it.",
                        "mirror_cooldown":      "Mirror: recharging — {v} more turn(s) until it can be armed again.",
                        "reframe_next":         "Reframe (armed): the enemy's next attack becomes block for you instead of damage.",
                        "next_attack_reduction":"Frame Trap: the enemy's next attack is reduced by {v} damage.",
                        "bleed_dmg":            "Bleed: the enemy takes {v} damage at the start of each of their turns.",
                        "bleed_turns":          "Bleed: {v} more turn(s) of bleed on the enemy.",
                        "crash_next_turn":      "Stack-Up Crash: you lose 2 energy next turn (the stim wearing off).",
                        "max_energy_penalty_next_turn":"FLMod Ebb: {v} less max energy next turn.",
                        "skip_next_turn":       "FLMod Crash: you lose your entire next turn.",
                        "enemy_attack_bonus":   "Pressure: the enemy's next attack deals +{v} extra damage to you.",
                        "player_draw_penalty":  "Authority Display: you draw {v} fewer card(s) at the start of your next turn.",
                        "cards_cap_next_turn":  "Card Restriction: you can only play {v} card(s) on your next turn.",
                        "special_dr_50":        "Special DR: SPECIAL-typed enemy attacks deal half damage to you.",
                        "see_red":              "See Red: each time you gain Hatred this fight, gain block.",
                        "thick_skull":          "Thick Skull: the first Hatred gain that would break you this fight is caught — Hatred held at 80, you wall up.",
                        "iron_posture":         "Iron Posture: at the start of each turn you keep half your block instead of losing all of it.",
                        "roid_rage":            "Roid Rage: each time you gain Hatred this fight, the enemy takes 3 damage.",
                    }
                    _active_buffs = []
                    for _k, _v in bs.buffs.items():
                        if not _v:
                            continue
                        ## Skip internal state flags — they're not player-facing buffs.
                        if _k in _BUFF_HIDDEN:
                            continue
                        _label = _BUFF_LABELS.get(_k, _k.replace("_", " ").title())
                        _icon  = _BUFF_ICONS.get(_k, "✦")
                        _count = _v if (isinstance(_v, int) and not isinstance(_v, bool) and _v > 1) else None
                        _chip  = "{} {}".format(_icon, _count) if _count is not None else _icon
                        ## Tooltip fallback: when no canonical tip is registered,
                        ## surface the readable label so the player at least sees
                        ## "Something Happening x3" instead of an empty hover.
                        _tip = _BUFF_TIPS.get(_k, _label)
                        if "{v}" in _tip:
                            _vv = "" if isinstance(_v, bool) else _v
                            try:
                                _tip = _tip.format(v=_vv)
                            except Exception:
                                _tip = _tip.replace("{v}", str(_vv))
                        _active_buffs.append((_chip, _tip))
                if _active_buffs:
                    hbox:
                        spacing 4
                        box_wrap True
                        xmaximum 330
                        for _chip, _bt in _active_buffs:
                            textbutton _chip:
                                action NullAction()
                                tooltip _bt
                                text_color "#ffdd44"
                                text_hover_color "#ffffff"
                                text_size 18
                                text_bold True
                                text_font "fonts/RobotoMono-Regular.ttf"
                                background Frame("#1a1410cc", 3, 3)
                                hover_background Frame("#332b00ee", 3, 3)
                                padding (6, 3)

        ## ── ENERGY (right side) ───────────────────────────────────────────────
        frame:
            xpos 1700
            ypos 580
            xsize 200
            padding (16, 12)
            background None

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

        ## ── END TURN BUTTON — pulses yellow when energy is unspent so the
        ## playtester stops ending the turn with cards still playable.
        python:
            _et_has_energy = bs.energy > 0
            _et_label = "[[ END TURN — {} ENERGY LEFT ]".format(bs.energy) if _et_has_energy else "[[ END TURN ]"
            _et_color  = "#ffaa00" if _et_has_energy else "#cc2200"
            _et_hover  = "#ffdd55" if _et_has_energy else "#ff4422"
            _et_bg     = Frame("#1a1500ee", 4, 4) if _et_has_energy else Frame("#1a0000ee", 4, 4)
            _et_hover_bg = Frame("#3a3000ee", 4, 4) if _et_has_energy else Frame("#330000ee", 4, 4)

        textbutton _et_label:
            xpos 1700
            ypos 700
            action [Function(battle_end_player_turn), Function(renpy.restart_interaction)]
            text_color _et_color
            text_hover_color _et_hover
            text_size 22
            text_bold True
            text_font "fonts/RobotoMono-Regular.ttf"
            background _et_bg
            hover_background _et_hover_bg
            padding (22, 14)
            if _et_has_energy:
                at _energy_warn_pulse

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

        ## ── HAND ──────────────────────────────────────────────────────────────
        ## Multi-layer card construction per slot (220×316 each):
        ##   L1: combo glow (only a card with a live bonus; pulsing gold)
        ##   L2: drop shadow (offset solid behind border)
        ##   L3: type-colored border (red=Attack/blue=Skill/purple=Power)
        ##   L4: warm-dark inner panel (#1a1410 — card-stock tone)
        ##   L5: zoned content (title band → art zone → type subtitle → description)
        ##   L6: cost gem (rotated-square diamond, overlaps top-left)
        ##   L7: exhaust badge (conditional, bottom-center)
        ## All halo + shadow stays inside the 220px slot so adjacent cards never bleed.
        ## xmaximum 1880 + spacing 2 gives headroom for hands up to 8 cards
        ## (8×220 + 7×2 = 1774) without overflowing the 1920px screen.
        frame:
            xalign 0.5
            ypos 780
            padding (10, 8)
            background None
            xmaximum 1880

            hbox:
                spacing 2
                xalign 0.5

                for _cid in bs.hand:
                    $ _card = CARD_LIBRARY.get(_cid, {})
                    $ _ctype = _card.get("type", "Skill")
                    ## Three corruption categories, each visually distinct:
                    ##   Status     — enemy-injected, single-fight (paperwork/fumes/...).
                    ##                Mustard #8a7a2a, ☠ glyph.
                    ##   Rage       — hatred-injected at 40/60/80, permanent in deck.
                    ##                Blood #aa1a1a, 🔥 glyph.
                    ##   Compromise — loss-injected on 2nd+ ladder loss, permanent
                    ##                AND unplayable (dead weight in hand).
                    ##                Broken gray #5a5550, 🚫 glyph.
                    $ _is_status     = (_card.get("effect") or "").startswith("status_")
                    $ _is_rage       = bool(_card.get("is_rage"))
                    $ _is_compromise = bool(_card.get("is_compromise"))
                    ## Upgraded cards (`_plus` variants) — single signal: the
                    ## name text flips to bright green. The "+" suffix on
                    ## name (auto-emitted by register_upgrade) stays. No
                    ## extra borders / halos / ribbons — they cluttered the
                    ## card without adding readability. Green-on-dark reads
                    ## from any zoom level. Upgrades and corruption never
                    ## co-occur (register_upgrade refuses status / rage /
                    ## compromise) so this branch is clean-cards only.
                    $ _is_upgraded   = bool(_card.get("is_upgraded"))
                    $ _UPGRADE_GREEN = "#44ee77"
                    ## Type-driven palette: Attack=red, Skill=blue, Power=purple.
                    ## Card "color" taxonomy (Physical/Mental/Money/...) reads as
                    ## random tinting to playtesters; type is unambiguous.
                    if _is_compromise:
                        $ _color = "#5a5550"
                    elif _is_rage:
                        $ _color = "#aa1a1a"
                    elif _is_status:
                        $ _color = "#8a7a2a"
                    else:
                        $ _color = {"Attack": "#cc4422", "Skill": "#3388cc", "Power": "#aa44cc"}.get(_ctype, "#888888")
                    $ _ok, _reason = bs.hand_playable(_cid)
                    $ _border = _color if _ok else "#3a2020"
                    ## A card whose bonus is LIVE right now (Production Push
                    ## after a Skill, Hotfix as the 3rd+ card) gets the only
                    ## glow in the hand — so it actually stands out.
                    $ _combo_live = (_cid in ("production_push", "production_push_plus") and bs.skill_played_this_turn) or (_cid in ("hotfix", "hotfix_plus") and bs.cards_played_this_turn >= 2)
                    $ _effect_text = effect_description(_card.get("effect")) or _card.get("flavor", "")
                    if _is_compromise:
                        $ _subtitle = "COMPROMISE · DEAD WEIGHT"
                    elif _is_rage:
                        $ _subtitle = "RAGE · CORRUPTED"
                    elif _is_status:
                        $ _subtitle = "STATUS · CURSE"
                    else:
                        $ _subtitle = (_ctype.upper() + " · " + (_card.get("color") or "").upper()).strip(" ·")
                    $ _art_path = "images/cards/{}.png".format(_cid)
                    $ _has_art  = renpy.loadable(_art_path)
                    if _is_compromise:
                        $ _art_glyph = "🚫"
                    elif _is_rage:
                        $ _art_glyph = "🔥"
                    elif _is_status:
                        $ _art_glyph = "☠"
                    else:
                        $ _art_glyph = _card.get("art_glyph") or {"Attack": "⚔", "Skill": "✦", "Power": "★"}.get(_ctype, "●")

                    button:
                        xsize 220
                        ysize 316
                        background None
                        hover_background None
                        sensitive _ok
                        action [Function(battle_play_card, _cid), Function(renpy.restart_interaction)]
                        at card_hover_lift

                        ## L1: combo glow — ONLY a card with a live bonus gets a
                        ## halo. Playability is already shown by the border and
                        ## the dimmed content, so a glow on every card was just
                        ## redundant noise that drowned this one out.
                        if _combo_live and _ok:
                            add Solid("#ffcc3344") xpos 0 ypos 0 xysize (220, 316) at card_glow_pulse
                            add Solid("#ffcc3377") xpos 4 ypos 4 xysize (212, 308) at card_glow_pulse

                        ## L2: drop shadow — offset solid behind the card body.
                        add Solid("#000000aa") xpos 16 ypos 14 xysize (200, 300)

                        ## L3 + L4: type-colored border wrapping warm-dark inner panel.
                        frame:
                            xpos 10
                            ypos 8
                            xsize 200
                            ysize 300
                            background Frame(_border, 6, 6)
                            padding (6, 6)

                            frame:
                                xfill True
                                yfill True
                                background Frame("#1a1410", 4, 4)
                                padding (6, 4)

                                vbox:
                                    xfill True
                                    spacing 4

                                    ## ── TITLE BANNER — gold serif on dark ribbon.
                                    ## Upgraded cards flip the name to bright green
                                    ## (sole upgrade signal — keeps the layout clean).
                                    frame:
                                        xfill True
                                        ysize 28
                                        background Frame("#0a0806", 4, 4)
                                        text _card.get("name", _cid):
                                            color (_UPGRADE_GREEN if (_is_upgraded and _ok) else ("#e8c878" if _ok else "#554434"))
                                            size 14
                                            bold True
                                            xalign 0.5
                                            yalign 0.5
                                            xmaximum 160
                                            text_align 0.5
                                            font "fonts/RobotoMono-Regular.ttf"

                                    ## ── ART ZONE — illustration or glyph fallback ──
                                    frame:
                                        xfill True
                                        ysize 100
                                        background Frame(_color + "22", 4, 4)
                                        if _has_art:
                                            add Transform(_art_path, size=(168, 92)) xalign 0.5 yalign 0.5
                                        else:
                                            text _art_glyph:
                                                xalign 0.5
                                                yalign 0.5
                                                color (_color if _ok else "#553333")
                                                size 60
                                                outlines [(2, "#000000", 0, 0)]

                                    ## ── TYPE SUBTITLE — small-caps line under art ──
                                    text _subtitle:
                                        xalign 0.5
                                        size 9
                                        color (_color if _ok else "#554040")
                                        bold True
                                        font "fonts/RobotoMono-Regular.ttf"

                                    ## ── DESCRIPTION — distinct parchment-tone band ──
                                    frame:
                                        xfill True
                                        yminimum 72
                                        background Frame("#241d15", 4, 4)
                                        padding (6, 6)
                                        text _effect_text:
                                            color ("#e8e0d0" if _ok else "#554840")
                                            size 12
                                            xalign 0.5
                                            yalign 0.5
                                            xmaximum 168
                                            text_align 0.5
                                            line_spacing 2

                        ## L6: cost gem — diamond (rotated square) overlapping
                        ## card top-left. Number rendered un-rotated on top.
                        fixed:
                            xpos -11
                            ypos -14
                            xysize (50, 50)
                            add Transform(Solid(_color if _ok else "#553333"), size=(32, 32), rotate=45) xalign 0.5 yalign 0.5
                            text "[_card.get('cost', 0)]":
                                xalign 0.5
                                yalign 0.5
                                color ("#0a0806" if _ok else "#221a1a")
                                size 18
                                bold True
                                font "fonts/RobotoMono-Regular.ttf"

                        ## L7: exhaust badge (conditional) — bottom-center over border.
                        if _card.get("exhaust"):
                            frame:
                                xpos 55
                                ypos 286
                                xsize 110
                                ysize 22
                                background Frame("#5a0000ee", 4, 4)
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

        ## ── Active tooltip text — buff chips / "?" button. Placed here (after
        ## the hand in document order) so it layers on top; sits just above
        ## the hand frame.
        $ _tt = GetTooltip()
        if _tt:
            frame:
                xalign 0.5
                ypos 742
                padding (16, 8)
                background Frame("#0d1018ee", 4, 4)
                text "[_tt]":
                    color "#ffffff"
                    size 16
                    xalign 0.5
                    xmaximum 1200
                    text_align 0.5

        ## ── PHASE A JUICE OVERLAYS ────────────────────────────────────────────
        ## Damage popups are no longer mounted from inside battle_screen at all
        ## — they're pushed IMPERATIVELY by deal_damage() in battle_engine via
        ## renpy.show_screen("damage_popup_*_inner", damage=N). That bypasses
        ## the screen-rebuild dependency that broke the previous attempts.
        ## Hit-flash washes stay here because they're cheap conditional
        ## Solid() draws that read state freshly via $ captures.
        $ _fx_now = renpy.get_game_runtime()
        $ _eh = getattr(bs, 'last_enemy_hit_time', -1.0)
        $ _ph = getattr(bs, 'last_player_hit_time', -1.0)

        ## Player-hit flash — red wash over the whole screen, brief.
        $ _player_hit_age = (_fx_now - _ph) if _ph > 0 else 999.0
        if _player_hit_age < 0.35:
            add Solid("#ff2222") xsize 1920 ysize 1080 at damage_flash_player

        ## Enemy-hit flash — subtle green wash.
        $ _enemy_hit_age = (_fx_now - _eh) if _eh > 0 else 999.0
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
