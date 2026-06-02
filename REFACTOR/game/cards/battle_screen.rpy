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
    ## DON'T bind `math` to a store name (`import math as _juice_math` OR
    ## `_juice_math = __import__('math')` — same result, same bug). The
    ## module lands on store and is unpicklable; saves silently drop the
    ## name and on load every transform NameErrors. Same lesson as
    ## `_battle_rand` / `_daily_music_rand`. Call via `__import__('math')`
    ## inline at the call sites; sys.modules caches it so the 60fps cost
    ## is a dict hit.

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
        trans.xoffset = int(26.0 * decay * __import__('math').sin(age * 32.0))
        trans.yoffset = int(14.0 * decay * __import__('math').sin(age * 47.0))
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
        trans.xoffset = int(amp * __import__('math').sin(age * 40.0))
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
        phase = __import__('math').sin(st * (2.0 * __import__('math').pi / 3.2))
        trans.zoom = 1.0 + 0.014 * phase
        trans.yoffset = int(-2.5 * __import__('math').sin(st * (2.0 * __import__('math').pi / 3.2) + 0.4))
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

## StS-style card hover. Hovered card scales up ~1.55× IN PLACE and lifts
## ~140px so it reads clearly above the hand row. No overlay, no popup —
## same card, just brought forward. The card's parent `button` keeps its
## 220×316 slot footprint so neighbours don't get shoved around; the
## scaled content bleeds outside the slot (intentional — neighbours may
## be partially occluded, exactly like StS).
transform card_hover_lift:
    on hover:
        ease 0.14 zoom 1.55 yoffset -140
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
                text "  † ATTACK — deals N damage   † COMPOUND — N×hits damage   ◆ BLOCK — gains block":
                    color "#aaaaaa"
                    size 13
                text "  ↑ BUFF — next attack +N dmg   ↓ DEBUFF — -N draw next turn   ↓ DEBUFF — -N energy next turn":
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
                                    $ _c_vtype = card_visual_type(_c)
                                    $ _ccol = card_type_color(_c, "frame")
                                    if _c_vtype == "Curse":
                                        $ _c_prefix = "× " if _c.get("is_compromise") else "† "
                                        $ _c_name_color = "#a09890" if _c.get("is_compromise") else "#ff8866"
                                    elif _c_vtype == "Status":
                                        $ _c_prefix = "☠ "
                                        $ _c_name_color = "#d4c47a"
                                    else:
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


## ---------------------------------------------------------------------------
## Inspect-overlay entrance — quick fade + tiny zoom-up so the big hover-card
## doesn't pop in jarringly. Paired with `_hover_card_cid` tracking on the
## hand buttons (battle_screen sets it via hovered/unhovered actions) and the
## `use battle_card_view(... mode="inspect")` call after the hand frame.
## ---------------------------------------------------------------------------
transform inspect_overlay_in:
    alpha 0.0
    zoom 0.88
    parallel:
        ease 0.10 alpha 1.0
    parallel:
        ease 0.10 zoom 1.0


## ---------------------------------------------------------------------------
## battle_card_view — single source of truth for card visuals.
##
## Drives the in-hand card AND the StS-style hover-inspect overlay. `mode`
## picks the size table:
##   "hand"    → 220×316 (fits in the bottom row, 8 cards across)
##   "inspect" → ~400×572 (1.82× scale, readable at any monitor size)
##
## Card construction (top → bottom in z-order):
##   1. Drop shadow (offset solid).
##   2. Border frame (deep type-color outline).
##   3. Frame body (saturated type color — Attack red / Skill blue / Power
##      purple / Curse near-black / Status toxic-yellow).
##   4. Inner well — vbox of four sections:
##        a. Name plate (dark band, gold text)
##        b. Art zone (illustration or glyph fallback over art_bg tone)
##        c. Type tab (small centered grey banner: ATTACK / SKILL / POWER / …)
##        d. Description panel (parchment tone, keyword-highlighted text)
##   5. Cost gem (stacked-diamond, overlapping top-left, orange beveled).
##   6. Combo glow (pulsing halo — only on cards with a LIVE combo bonus).
##   7. Exhaust badge (conditional, bottom-center over the border).
##
## `playable` controls the dim-out branch — unplayable cards desaturate and
## drop alpha so the eye skips them. Caller computes via bs.hand_playable.
## ---------------------------------------------------------------------------
screen battle_card_view(cid, mode="hand", playable=True):
    python:
        _card = CARD_LIBRARY.get(cid, {})
        _vtype = card_visual_type(_card)
        _palette = TYPE_PALETTE.get(_vtype, TYPE_PALETTE["Skill"])
        _frame_c   = _palette["frame"]
        _border_c  = _palette["border"]
        _artbg_c   = _palette["art_bg"]
        _accent_c  = _palette["accent"]

        ## CLASS-COLOR OVERRIDE — every card in the player's deck takes on
        ## their class color so the deck reads as "theirs" at a glance.
        ## BB = orange, DE = purple, BH = green. Resolution order:
        ##   1. Curse / Status keep the type palette (corruption signal must
        ##      stay visually distinct — black for Curse, toxic for Status).
        ##   2. Otherwise: prefer the active player's class color. This
        ##      covers basic Strike / Defend AND class-locked signatures.
        ##   3. Fall back to the card's own `class_lock` when no player
        ##      class is set (character-select previews etc.).
        ##   4. Final fallback: the type palette already loaded above.
        def _mix(hex_a, hex_b, t):
            a = int(hex_a[1:3], 16), int(hex_a[3:5], 16), int(hex_a[5:7], 16)
            b = int(hex_b[1:3], 16), int(hex_b[3:5], 16), int(hex_b[5:7], 16)
            m = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
            return "#{:02x}{:02x}{:02x}".format(*m)

        _override_cls = None
        if _vtype not in ("Curse", "Status"):
            if stats is not None and stats.player_class in ("bodybuilder", "dark_empath", "biohacker"):
                _override_cls = stats.player_class
            elif _card.get("class_lock"):
                _override_cls = _card.get("class_lock")

        if _override_cls:
            _cls_hex = class_accent_color(_override_cls)
            _frame_c  = _cls_hex
            _accent_c = _cls_hex
            ## Border ~50% darker than frame, art_bg ~70% darker — same
            ## structural hierarchy the type palette had, just keyed off
            ## the class color instead.
            _border_c = _mix(_cls_hex, "#000000", 0.55)
            _artbg_c  = _mix(_cls_hex, "#000000", 0.78)

        _is_upgraded = bool(_card.get("is_upgraded"))

        ## Rarity tint on the name plate background. StS-style signal: common
        ## stays dark, uncommon goes steel-blue, rare goes gold-bronze, boss
        ## goes deep red. Subtle enough to coexist with the gold name text.
        _rarity = (_card.get("rarity") or "common").lower()
        _name_bg = {
            "uncommon": "#1a2030ee",
            "rare":     "#3a2810ee",
            "boss":     "#3a0a0aee",
        }.get(_rarity, "#0a0806ee")

        ## Inspect mode is a uniform 1.82× scale on every numeric dimension.
        ## Single multiplier table keeps the two views layout-identical so the
        ## hover-zoom feels like the SAME card, just bigger.
        if mode == "inspect":
            _W, _H        = 400, 572
            _name_h       = 50
            _art_h        = 200
            _tab_h        = 36
            _name_sz      = 26
            _tab_sz       = 19
            _desc_sz      = 22
            _gem_outer    = 90
            _gem_inner    = 72
            _gem_sz       = 40
            _gem_xpos     = -42
            _gem_ypos     = -44
            _shadow_off   = 14
            _exhaust_w    = 200
            _exhaust_h    = 38
            _exhaust_sz   = 22
            _exhaust_y    = 520
            _exhaust_xpos = 100
            _glyph_sz     = 110
        else:
            _W, _H        = 220, 316
            _name_h       = 28
            _art_h        = 110
            _tab_h        = 22
            _name_sz      = 15
            _tab_sz       = 11
            _desc_sz      = 13
            _gem_outer    = 50
            _gem_inner    = 40
            _gem_sz       = 22
            _gem_xpos     = -22
            _gem_ypos     = -22
            _shadow_off   = 8
            _exhaust_w    = 110
            _exhaust_h    = 22
            _exhaust_sz   = 12
            _exhaust_y    = 286
            _exhaust_xpos = 55
            _glyph_sz     = 60

        ## Playability dim — desaturates the frame and drops opacity so
        ## unplayable cards step back visually without disappearing.
        if not playable:
            _frame_c  = "#3a2020"
            _border_c = "#1a0d0d"
            _artbg_c  = "#1a1010"
            _accent_c = "#664444"

        ## Inner-well sizes (everything after the 4px border + 4px inset).
        _inner_w = _W - 16   ## L,R: 4(border)+4(padding) = 8 each side
        _inner_h = _H - 16

        ## Combo glow predicate — Production Push after a Skill, Hotfix as 3rd+ card.
        _combo_live = False
        try:
            _bs = battle_state
            if _bs is not None and playable:
                if cid in ("production_push", "production_push_plus") and _bs.skill_played_this_turn:
                    _combo_live = True
                elif cid in ("hotfix", "hotfix_plus") and _bs.cards_played_this_turn >= 2:
                    _combo_live = True
        except Exception:
            _combo_live = False

        _art_path  = "images/cards/{}.png".format(cid)
        _has_art   = renpy.loadable(_art_path)
        ## Upgrade fallback — `<id>_plus` reuses the base card's art when no
        ## dedicated upgrade illustration exists. Matches StS convention; the
        ## green "+" suffix on the name plate is the only required upgrade tell.
        if not _has_art and cid.endswith("_plus"):
            _art_path = "images/cards/{}.png".format(cid[:-5])
            _has_art = renpy.loadable(_art_path)
        ## Safe-glyph fallback (RobotoMono ships no emoji — ⚔/✦/★ render as
        ## tofu). Only used until a card's illustration exists.
        _art_glyph = _card.get("art_glyph") or {
            "Attack": "†", "Skill": "◊", "Power": "◆",
            "Curse":  "×", "Status": "☠",
        }.get(_vtype, "●")

        _name_text = _card.get("name", cid)
        ## Upgraded card sole signal: name flips bright green. Matches the
        ## existing convention across reward / deck / fixer screens (per
        ## card_name_color helper).
        _name_color = "#44ee77" if (_is_upgraded and playable) else ("#f0d088" if playable else "#5a4a32")

        _type_label = _vtype.upper()
        _desc_raw   = effect_description(_card.get("effect")) or _card.get("flavor", "")
        _desc       = kw_highlight(_desc_raw)
        _desc_color = "#ece4d4" if playable else "#5a4f3f"

        _cost_text  = str(_card.get("cost", 0))
        _cost_color = "#ffffff" if playable else "#554a40"

    fixed:
        xysize (_W, _H)

        ## L1: drop shadow — soft offset solid behind the card body.
        add Solid("#000000aa") xpos _shadow_off ypos _shadow_off xysize (_W - _shadow_off - 2, _H - _shadow_off - 2)

        ## L2 + L3: border frame wrapping frame body.
        frame:
            xpos 0
            ypos 0
            xysize (_W, _H)
            background Frame(_border_c, 6, 6)
            padding (4, 4)

            frame:
                xfill True
                yfill True
                background Frame(_frame_c, 4, 4)
                padding (4, 4)

                ## L4: inner content well (art_bg-toned).
                frame:
                    xfill True
                    yfill True
                    background Frame(_artbg_c, 4, 4)
                    padding (6, 6)

                    vbox:
                        xfill True
                        spacing 4

                        ## (a) Name plate — rarity-tinted band, gold serif-ish text.
                        frame:
                            xfill True
                            ysize _name_h
                            background Frame(_name_bg, 4, 4)
                            text _name_text substitute False:
                                color _name_color
                                size _name_sz
                                bold True
                                xalign 0.5
                                yalign 0.5
                                xmaximum (_inner_w - 24)
                                text_align 0.5
                                font "fonts/RobotoMono-Regular.ttf"
                                outlines [(1, "#000000", 0, 0)]

                        ## (b) Art zone — illustration or glyph fallback.
                        ## Three-sided border (top + left + bottom). The right
                        ## edge is intentionally open — gives the art a slight
                        ## "page bleeds off" feel toward the card's outer trim.
                        fixed:
                            xfill True
                            ysize _art_h
                            if _has_art:
                                ## size=() stretches to fill the panel without
                                ## preserving aspect. The aspect mismatch is
                                ## kept tiny by standardizing all card art on
                                ## ~2:1 (panel is 1.92:1) at gen/crop time.
                                add Transform(_art_path, size=(_inner_w - 4, _art_h - 4)) xpos 2 ypos 2 xoffset -6
                            else:
                                text _art_glyph:
                                    xalign 0.5
                                    yalign 0.5
                                    color _accent_c
                                    size _glyph_sz
                                    outlines [(2, "#000000", 0, 0)]
                            add Solid(_border_c + ("99" if playable else "55")) xysize (_inner_w, 2) xpos -6 ypos 0
                            add Solid(_border_c + ("99" if playable else "55")) xysize (2, _art_h) xpos -6 ypos 0
                            add Solid(_border_c + ("99" if playable else "55")) xysize (_inner_w, 2) xpos -6 ypos (_art_h - 2)
                            add Solid(_border_c + ("99" if playable else "55")) xysize (2, _art_h) xpos (_inner_w - 8) ypos 0

                        ## (c) Type tab — centered dark banner with type label.
                        frame:
                            xalign 0.5
                            ysize _tab_h
                            background Frame("#1a1a1aee", 4, 4)
                            padding (14, 1)
                            text _type_label:
                                color "#e0e0e0"
                                size _tab_sz
                                bold True
                                xalign 0.5
                                yalign 0.5
                                font "fonts/RobotoMono-Regular.ttf"

                        ## (d) Description panel — parchment tone, keyword-highlighted text.
                        frame:
                            xfill True
                            yfill True
                            background Frame("#241d15ee", 4, 4)
                            padding (6, 6)
                            text _desc:
                                color _desc_color
                                size _desc_sz
                                xalign 0.5
                                yalign 0.5
                                xmaximum (_inner_w - 16)
                                text_align 0.5
                                line_spacing 2

        ## L5: combo glow — only when a bonus is LIVE right now. Pulses.
        if _combo_live:
            add Solid("#ffcc3344") xpos 0 ypos 0 xysize (_W, _H) at card_glow_pulse
            add Solid("#ffcc3377") xpos 4 ypos 4 xysize (_W - 8, _H - 8) at card_glow_pulse

        ## L6: cost gem — beveled diamond stack overlapping top-left corner.
        ## Two rotated solids (dark outer + orange inner) give the StS-gem
        ## bevel look without needing a circle asset.
        fixed:
            xpos _gem_xpos
            ypos _gem_ypos
            xysize (_gem_outer + 8, _gem_outer + 8)
            add Transform(Solid(GEM_ORANGE_DARK if playable else "#2a1a10"), size=(_gem_outer, _gem_outer), rotate=45) xalign 0.5 yalign 0.5
            add Transform(Solid(GEM_ORANGE if playable else "#553322"), size=(_gem_inner, _gem_inner), rotate=45) xalign 0.5 yalign 0.5
            text _cost_text:
                xalign 0.5
                yalign 0.5
                color _cost_color
                size _gem_sz
                bold True
                font "fonts/RobotoMono-Regular.ttf"
                outlines [(2, "#000000", 0, 0)]

        ## L7: exhaust badge (conditional).
        if _card.get("exhaust"):
            frame:
                xpos _exhaust_xpos
                ypos _exhaust_y
                xysize (_exhaust_w, _exhaust_h)
                background Frame("#5a0000ee", 4, 4)
                text "EXHAUST":
                    color "#ff8866"
                    size _exhaust_sz
                    bold True
                    xalign 0.5
                    yalign 0.5
                    font "fonts/RobotoMono-Regular.ttf"


screen battle_screen():
    modal True
    zorder 600

    python:
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

    ## Relic tray — owned gear, top-left (StS convention). Tooltips surface
    ## via the GetTooltip() consumer below the hand. Empty = renders nothing.
    frame:
        xpos 24
        ypos 24
        background None
        use relic_tray(size=88)

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
                    else:
                        text "■ 0":
                            color "#445566"
                            size 18

                    ## Permanent Strength badge — flags the ramp boss intent.
                    ## Reads "STR +N" in red-orange, only visible when stacked.
                    if bs.enemy_strength > 0:
                        text "STR +[bs.enemy_strength]":
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
                        textbutton "† RAGE":
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
                        textbutton "↑ BUY-IN [_buyin]":
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
                ##   attack       † <dmg>             red       (+N if bonus queued)
                ##   compound     † <val>×<hits>      red
                ##   block        ◆ <block>          blue
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
                    ## Mirror battle_resolve_enemy damage math so the intent
                    ## badge shows the REAL incoming hit, not just the base
                    ## value. The player should never have to add Strength +
                    ## drawer-stack + crew-rage in their head.
                    ##
                    ## _atk_flat_bonus: applies to any single-attack peek.
                    ## _cmp_per_hit_bonus: applies per hit on compound peeks.
                    ## Current-intent-only bonuses (sprejeri tag spend, vlk
                    ## margin, paragraph cite, one-shot enemy_attack_bonus) are
                    ## applied at the use-site below, gated on _is_current.
                    _atk_flat_bonus = bs.enemy_strength
                    _cmp_per_hit_bonus = bs.enemy_strength
                    if bs.enemy_id == "fanousek":
                        _fwd = ENEMY_LIBRARY.get("fanousek", {}).get("wrinkle_data", {})
                        _fthr = _fwd.get("hp_threshold", 0.5)
                        if bs.enemy_hp <= int(bs.enemy_max_hp * _fthr):
                            _fbonus = _fwd.get("bonus_dmg", 4)
                            _atk_flat_bonus += _fbonus
                            _cmp_per_hit_bonus += _fbonus
                    if bs.enemy_id == "rvac" and bs.enemy_hp <= bs.enemy_max_hp // 2:
                        _atk_flat_bonus += 3
                    if bs.enemy_id == "garda" and bs.enemy_hp > bs.enemy_max_hp // 2:
                        _atk_flat_bonus += 3
                    if bs.enemy_id == "estebak":
                        _atk_flat_bonus += bs.buffs.get("estebak_drawers", 0)
                    _atk_current_bonus = bs.buffs.get("enemy_attack_bonus", 0)
                    _lawyer_cite_bonus = 0
                    if bs.enemy_id == "lawyer":
                        _lwd = ENEMY_LIBRARY.get("lawyer", {}).get("wrinkle_data", {})
                        _cad = _lwd.get("cadence", 3)
                        if bs.turn > 0 and bs.turn % _cad == 0:
                            _lawyer_cite_bonus = _lwd.get("bonus_dmg", 6)

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
                                        _icon = "†"
                                        _ic_color = "#ff4422"
                                        ## Engine: base - next_attack_reduction (floor 1)
                                        ## then + flat bonuses. Mirror exactly so a
                                        ## just-played Breath Test visibly drops the
                                        ## displayed hit on the current intent.
                                        _raw = _intent.get("value", 0)
                                        _red = bs.buffs.get("next_attack_reduction", 0) if _is_current else 0
                                        _base = max(1 if _raw > 0 else 0, _raw - _red) + _atk_flat_bonus
                                        if _is_current:
                                            _base += _atk_current_bonus
                                            _base += _lawyer_cite_bonus
                                            if bs.enemy_id == "sprejeri":
                                                _tags = bs.buffs.get("sprejeri_tags", 0)
                                                _thr = 1 if bs.enemy_hp <= bs.enemy_max_hp // 2 else 3
                                                if _tags >= _thr:
                                                    _base += _tags
                                            if bs.enemy_id == "vlk" and _intent.get("id") == "vlk_margin_call":
                                                _mc_per = ENEMY_LIBRARY.get("vlk", {}).get("wrinkle_data", {}).get("margin_per_buyin", 5)
                                                _base += _mc_per * bs.buffs.get("vlk_buyin", 0)
                                        _val_text = "{}".format(_base)
                                        _dmg_for_threat = _base
                                    elif _itype == "compound":
                                        _icon = "†"
                                        _ic_color = "#ff6644"
                                        _raw = _intent.get("value", 0)
                                        _hits = _intent.get("value2", 1)
                                        ## Engine spreads damage_reduction across hits.
                                        _red = (bs.buffs.get("next_attack_reduction", 0) // max(1, _hits)) if _is_current else 0
                                        _per_hit = max(1 if _raw > 0 else 0, _raw - _red) + _cmp_per_hit_bonus
                                        if _is_current and _lawyer_cite_bonus > 0:
                                            _per_hit += max(1, _lawyer_cite_bonus // max(1, _hits))
                                        _val_text = "{}×{}".format(_per_hit, _hits)
                                        _dmg_for_threat = _per_hit * _hits
                                    elif _itype == "block":
                                        _icon = "◆"
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
                                        _icon = "↑"
                                        _ic_color = "#ff8822"
                                        _val_text = "+{} STR".format(_intent.get("value", 0))
                                        _dmg_for_threat = 0
                                    elif _itype == "restrict":
                                        ## Card-play cap on your next turn — purple, sharp glyph.
                                        _icon = "◊"
                                        _ic_color = "#cc44cc"
                                        _val_text = "Max {} card(s)".format(_intent.get("value", 1))
                                        _dmg_for_threat = 0
                                    elif _itype == "debuff":
                                        _ic_color = "#aa44cc"
                                        _dkey = _intent.get("debuff_key", "player_draw_penalty")
                                        if _dkey == "max_energy_penalty_next_turn":
                                            _icon = "↓"
                                            _val_text = "-{} energy".format(_intent.get("value", 1))
                                        else:
                                            _icon = "↓"
                                            _val_text = "-{} draw".format(_intent.get("value", 1))
                                        _dmg_for_threat = 0
                                    elif _itype == "moneydrain":
                                        ## Vlk Buy-In — drains run money, not HP.
                                        _icon = "↓"
                                        _ic_color = "#cc66cc"
                                        _val_text = "-{} Kč".format(_intent.get("value", 0))
                                        _dmg_for_threat = 0
                                    elif _itype == "dividend":
                                        ## Vlk Dividend — heals you. The bait.
                                        _icon = "↑"
                                        _ic_color = "#66cc88"
                                        _val_text = "+{} HP".format(_intent.get("value", 0))
                                        _dmg_for_threat = 0
                                    else:
                                        _icon = "?"
                                        _ic_color = "#888888"
                                        _val_text = "?"
                                        _dmg_for_threat = 0

                                    ## Threat tier — current intent only. Damage value
                                    ## is the primary readout (huge, bold, color-coded);
                                    ## icon stays smaller as a label; name is flavour.
                                    ## Numeric-damage intents (attack/compound) get the
                                    ## big ramp; non-attack labels are long strings and
                                    ## blow out the chip at 40-56px, so they get a
                                    ## moderate bump only.
                                    _is_numeric = _itype in ("attack", "compound")
                                    if _is_current and _is_numeric and _dmg_for_threat >= 15:
                                        _val_size = 56
                                        _val_color = "#ff2222"
                                        _panel_bg = "#3a0000ee"
                                        _icon_size = 34
                                        _name_size = 13
                                        _panel_pad = (22, 12)
                                        _icon_spacing = 12
                                        _val_outlines = [(2, "#000000", 0, 0)]
                                    elif _is_current and _is_numeric and _dmg_for_threat >= 8:
                                        _val_size = 48
                                        _val_color = "#ffcc44"
                                        _panel_bg = "#2a1a00dd"
                                        _icon_size = 30
                                        _name_size = 12
                                        _panel_pad = (20, 10)
                                        _icon_spacing = 10
                                        _val_outlines = [(2, "#000000", 0, 0)]
                                    elif _is_current and _is_numeric:
                                        _val_size = 40
                                        _val_color = "#ffffff"
                                        _panel_bg = "#1a1a1add"
                                        _icon_size = 26
                                        _name_size = 12
                                        _panel_pad = (16, 8)
                                        _icon_spacing = 10
                                        _val_outlines = [(2, "#000000", 0, 0)]
                                    elif _is_current:
                                        ## Non-attack current intent: label is a string,
                                        ## not a number. Moderate bump only so e.g.
                                        ## "Max 1 card(s)" or "+8 HP" fits the chip.
                                        _val_size = 24
                                        _val_color = _ic_color
                                        _panel_bg = "#1a1a1add"
                                        _icon_size = 26
                                        _name_size = 12
                                        _panel_pad = (16, 8)
                                        _icon_spacing = 8
                                        _val_outlines = [(2, "#000000", 0, 0)]
                                    else:
                                        _val_size = 18
                                        _val_color = "#888888"
                                        _panel_bg = "#1a1a1add"
                                        _icon_size = 18
                                        _name_size = 10
                                        _panel_pad = (10, 6)
                                        _icon_spacing = 6
                                        _val_outlines = []

                                frame:
                                    background Frame(_panel_bg, 4, 4)
                                    padding _panel_pad
                                    vbox:
                                        spacing 2
                                        xalign 0.5
                                        hbox:
                                            spacing _icon_spacing
                                            xalign 0.5
                                            yalign 0.5
                                            text _icon:
                                                color _ic_color
                                                size _icon_size
                                                yalign 0.5
                                            text "[_val_text]":
                                                color _val_color
                                                size _val_size
                                                bold _is_current
                                                yalign 0.5
                                                font "fonts/RobotoMono-Regular.ttf"
                                                outlines _val_outlines
                                        text "[_label]":
                                            color "#888888"
                                            size _name_size
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
                    text "■ [bs.player_block]":
                        color "#88aaff"
                        size 18
                        bold True
                        at block_gain_pulse
                else:
                    text "■ 0":
                        color "#445566"
                        size 18
                        bold True

                ## Card-play restriction banner — appears when a 'restrict'
                ## intent has capped the player's plays this turn. Shows the
                ## remaining budget so the player can plan the one card that
                ## matters most.
                if bs.current_turn_max_cards is not None:
                    $ _restrict_left = max(0, bs.current_turn_max_cards - bs.cards_played_this_turn)
                    text "× RESTRICTED: [_restrict_left]/[bs.current_turn_max_cards] cards":
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
                        "rvac_double_total",
                        "colonel_phase2",
                        "grundza_detonated",
                        "mirror_armed_for_counter",
                        "paragraph_4b_armed",
                        "job_offer_armed",
                        "took_the_heat_armed",
                        "sprejeri_tags",
                        "thick_skull_used",
                    }
                    ## Glyphs are restricted to the safe set RobotoMono actually
                    ## ships (verified against its cmap): ◆ ◊ ↑ ↓ † + × · ○ ▼ —
                    ## NO astral-plane emoji (they render as tofu/'?' in-game per
                    ## the recurring render bug). Visual grammar:
                    ##   ◆ block/defense   ◊ damage-reduction/reflect/special
                    ##   † offense/retaliate/bleed   ↑ rising   ↓ falling
                    ##   + heal/draw   × restriction   · transient counter/timer
                    _BUFF_ICONS = {
                        "starting_block_+1":           "◆",
                        "stoic_anchor_block":          "◆",
                        "stoic_anchor_heal":           "+",
                        "soma_starting_block":         "◆",
                        "presence_charges":            "◆",
                        "read_charges":                "○",
                        "kick_charges":                "+",
                        "mental_dr_50":                "◊",
                        "special_dr_50":               "◊",
                        "iron_stance_active":          "†",
                        "single_retaliate_dmg":        "†",
                        "vigil_next_turn_block":       "◆",
                        "insight_block":               "◆",
                        "insight_turns_left":          "·",
                        "block_next_turn":             "◆",
                        "mirror_next":                 "◊",
                        "mirror_cooldown":             "·",
                        "reframe_next":                "◊",
                        "next_attack_reduction":       "◊",
                        "bleed_dmg":                   "†",
                        "bleed_turns":                 "·",
                        "crash_next_turn":             "▼",
                        "max_energy_penalty_next_turn":"▼",
                        "skip_next_turn":              "▼",
                        "cards_cap_next_turn":         "×",
                        "enemy_attack_bonus":          "↑",
                        "player_draw_penalty":         "↓",
                        "see_red":                     "↑",
                        "thick_skull":                 "◆",
                        "iron_posture":                "◆",
                        "roid_rage":                   "†",
                    }
                    ## Enemy-applied debuffs ON the player — rendered red so the
                    ## player can tell at a glance what's hurting them vs their
                    ## own (gold) buffs.
                    _BUFF_BAD = {
                        "crash_next_turn", "max_energy_penalty_next_turn",
                        "skip_next_turn", "cards_cap_next_turn",
                        "enemy_attack_bonus", "player_draw_penalty",
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
                        "single_retaliate_dmg":"Bouncer Door",
                        "vigil_next_turn_block":"Vigil",
                        "insight_block":       "Insight",
                        "insight_turns_left":  "Insight (turns)",
                        "block_next_turn":     "Procedural Defense",
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
                        "single_retaliate_dmg": "Bouncer Door: when the enemy's next attack arrives, retaliate for {v} damage (one use, fires even if your block soaks the hit).",
                        "vigil_next_turn_block":"Vigil: gain +{v} block at the start of your next turn.",
                        "insight_block":        "Insight: gain bonus block at the start of your turn.",
                        "insight_turns_left":   "Insight: {v} more turn(s) of bonus block.",
                        "block_next_turn":      "Procedural Defense: block ALL damage on your next turn.",
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
                        _icon  = _BUFF_ICONS.get(_k, "•")
                        _count = _v if (isinstance(_v, int) and not isinstance(_v, bool) and _v > 1) else None
                        _chip  = "{} {}".format(_icon, _count) if _count is not None else _icon
                        _chip_color = "#ff6655" if _k in _BUFF_BAD else "#ffdd44"
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
                        _active_buffs.append((_chip, _tip, _chip_color))
                if _active_buffs:
                    hbox:
                        spacing 4
                        box_wrap True
                        xmaximum 330
                        for _chip, _bt, _bc in _active_buffs:
                            textbutton _chip:
                                action NullAction()
                                tooltip _bt
                                text_color _bc
                                text_hover_color "#ffffff"
                                text_size 18
                                text_bold True
                                text_font "fonts/RobotoMono-Regular.ttf"
                                background Frame("#1a1410cc", 3, 3)
                                hover_background Frame("#332b00ee", 3, 3)
                                padding (6, 3)

        ## ── ENERGY (right side) ───────────────────────────────────────────────
        ## Cracked-badge icon (REFACTOR/game/images/ui/ui_energy_badge.png) with
        ## the energy number rendered over the central empty inset. The whole
        ## fixed pulses on card-spend via energy_pulse (zoom 1.0 -> 1.25 -> 1.0
        ## over 0.35s) so badge and number bounce together. Stack: badge 180×180
        ## sits ABOVE the END TURN button at ypos 700; number offset slightly
        ## down because the inset isn't dead-center vertically in the artwork.
        fixed:
            xpos 1710
            ypos 510
            xysize (180, 180)
            at energy_pulse

            add "images/ui/ui_energy_badge.png" xalign 0.5 yalign 0.5 size (180, 180)

            text "[bs.energy]/[bs.max_energy]":
                color "#ffffff"
                size 32
                bold True
                xalign 0.5
                yalign 0.5
                yoffset 4
                outlines [(3, "#000000", 0, 0)]

        ## ── END TURN BUTTON — pulses yellow when energy is unspent so the
        ## playtester stops ending the turn with cards still playable.
        python:
            _et_has_energy = bs.energy > 0
            _et_label = "[[ END TURN ]"
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

        ## Click the pile counter to open a peek modal. Round count rides
        ## along here (used to float mid-right, but it's meta-info and groups
        ## better with the other pile readouts at the bottom-left).
        textbutton "Round [bs.turn]   ·   Draw: [_draw_n]   Discard: [_disc_n]   Exhaust: [_exh_n]":
            xpos 30
            ypos 1010
            action Show("battle_pile_peek")
            text_color "#888888"
            text_hover_color "#ffffff"
            text_size 14
            text_font "fonts/RobotoMono-Regular.ttf"
            background Frame("#1a1a1add", 4, 4)
            hover_background Frame("#2a2a2add", 4, 4)
            padding (10, 6)

        ## ── HAND ──────────────────────────────────────────────────────────────
        ## Each card slot delegates to `battle_card_view(cid, mode="hand", ...)`
        ## — the single source of truth for card visuals (also used by the
        ## hover-inspect overlay below in mode="inspect"). The button wrapper
        ## keeps Ren'Py focus/click semantics and pipes hover events into
        ## `_hover_card_cid` so the overlay knows what to draw.
        ## xmaximum 1880 + spacing 2 supports hands of up to 8 cards
        ## (8×220 + 7×2 = 1774) within the 1920px screen.
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
                    $ _ok, _reason = bs.hand_playable(_cid)

                    button:
                        xsize 220
                        ysize 316
                        background None
                        hover_background None
                        sensitive _ok
                        action [Function(battle_play_card, _cid), Function(renpy.restart_interaction)]
                        at card_hover_lift

                        use battle_card_view(cid=_cid, mode="hand", playable=_ok)

        ## ── Active tooltip text — buff chips. Placed here (after
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
