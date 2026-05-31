################################################################################
## REFACTOR — Battle Ladder
##
## Slot rotation: random_event_check (script.rpy) consults
## roll_ladder_or_event(day) to decide between a ladder fight and the
## narrative random-event pool. Ladder pool drains as battles fire
## (no repeats per run) and is keyed by day band:
##     easy (d3-9)    = rvac / sprejeri / fanousek / spis
##     medium (d10-17)= nguyen / grundza / lawyer / dispatcher / vlk
##     hard (d18-28)  = inspekce / garda / lifer / estebak
## The Colonel (Day 30) stays on his own colonel_event label — his
## multi-phase resolution and ending-jump logic are NOT routed through
## the wrapper.
##
## battle_with(enemy_id, tier) is the wrapper label:
##     init  -> screen -> outcome -> (forced_detour OR card_reward_trio)
################################################################################

default _ladder_skip_tomorrow = False


init python:

    ## Cash on ladder victory. Closes the post-battle reward loop — card draft
    ## remains the strategic reward; CZK is the sim-feel reward. Sized to sit
    ## under Day-14 minimum salary (20k): three hard wins ≈ one salary day.
    BATTLE_MONEY_REWARD = {
        "easy":   2500,
        "medium": 5000,
        "hard":   7500,
    }

    def _battle_ladder_band(day):
        if day <= 9:
            return "easy"
        if day <= 17:
            return "medium"
        return "hard"

    def _ladder_init_pool():
        """Lazy-init the per-run drainable ladder pool."""
        if not hasattr(store, 'battle_ladder_pool') or store.battle_ladder_pool is None:
            store.battle_ladder_pool = {
                "easy":   ["rvac", "sprejeri", "fanousek", "spis"],
                "medium": ["nguyen", "grundza", "lawyer", "dispatcher", "vlk"],
                "hard":   ["inspekce", "garda", "lifer", "estebak"],
            }

    def roll_ladder_or_event(day):
        """Decide what fires this random-event slot.

        Returns:
            ('battle', enemy_id, tier)  fire battle_with(enemy_id, tier)
            ('event',  None, None)      fall through to narrative pool
            (None,     None, None)      silent slot (Easy-loss penalty)

        Battles STRICTLY take priority over narrative events: as long as the
        current tier's battle pool has enemies, the slot is a battle. Events
        only fire on a tier where the pool is drained. This was a player
        request — random events felt like dead air between fights.
        """
        import random as _r
        _ladder_init_pool()

        if getattr(store, '_ladder_skip_tomorrow', False):
            store._ladder_skip_tomorrow = False
            return (None, None, None)

        tier = _battle_ladder_band(day)
        battle_pool = store.battle_ladder_pool.get(tier, [])

        if battle_pool:
            eid = _r.choice(battle_pool)
            battle_pool.remove(eid)
            return ("battle", eid, tier)

        event_pool = getattr(store, 'random_event_pool', []) or []
        if event_pool:
            return ("event", None, None)

        return (None, None, None)


## ---------------------------------------------------------------------------
## battle_intro — multi-slide pre-fight cinematic.
##   Slide 1: location background + "why you're here" narration.
##   Slide 2: the enemy sprite rises into frame + reveal narration.
##   Slides 3+ (optional): extra reveal beats over the same sprite/bg, used
##                         when a single reveal slide would overflow the
##                         text-box (lifer, estebak).
## Reads intro_lines / bg_id / sprite_id from ENEMY_LIBRARY. Enemies with
## fewer than two intro_lines (Colonel — own event) are skipped: the fight
## begins at once.
## ---------------------------------------------------------------------------

transform battle_intro_enemy_enter:
    xalign 0.5
    yalign 1.0
    zoom 0.82
    alpha 0.0
    yoffset 80
    easein 0.55 alpha 1.0 yoffset 0


label battle_intro(enemy_id):

    python:
        _e = ENEMY_LIBRARY.get(enemy_id, {}) or {}
        _intro = _e.get("intro_lines", []) or []
        _bg_id = _e.get("bg_id") or _e.get("sprite_id") or enemy_id
        _spr_tag = "{} neutral".format(_e.get("sprite_id") or enemy_id)
        _intro_bg = Transform(
            "images/backgrounds/bg_{}.jpg".format(_bg_id),
            size=(config.screen_width, config.screen_height),
        )

    if len(_intro) < 2:
        return

    $ _intro_line1 = _intro[0]
    $ _intro_line2 = _intro[1]

    ## Slide 1 — the location, and why a cop is standing in it.
    scene bg_black
    scene expression _intro_bg with Dissolve(0.6)
    narrator "[_intro_line1]"

    ## Slide 2 — the enemy is in the room.
    show expression _spr_tag as battle_intro_enemy at battle_intro_enemy_enter
    narrator "[_intro_line2]"

    ## Slides 3+ — extra reveal beats over the same sprite/bg.
    if len(_intro) > 2:
        python:
            for _ln in list(_intro[2:]):
                renpy.say(narrator, _ln)

    return


## ---------------------------------------------------------------------------
## encounter_choice — pre-battle standoff. JB meets the enemy and decides:
## FIGHT (engage → rewards + risk) or LET THEM GO (-25 Hatred, walk away,
## forfeit all rewards). The relief valve is the cop choosing not to escalate;
## the cost is the cards/cash/relic you don't get. Bosses set no_flee so the
## option is hidden — you can't walk away from a reckoning.
## Returns "fight" or "flee".
## ---------------------------------------------------------------------------

screen encounter_choice(enemy_id, can_flee=True):
    modal True
    zorder 550

    python:
        _enc_e      = ENEMY_LIBRARY.get(enemy_id, {}) or {}
        _enc_name   = _enc_e.get("display_name", enemy_id)
        _enc_spr    = "{} neutral".format(_enc_e.get("sprite_id") or enemy_id)
        _enc_bg_id  = _enc_e.get("bg_id") or _enc_e.get("sprite_id") or enemy_id
        _enc_bg     = "images/backgrounds/bg_{}.jpg".format(_enc_bg_id)
        ## JB runs visibly hotter at high Hatred — the standoff reads angrier.
        _enc_jb     = "jb angry" if (stats and stats.pcr_hatred >= 60) else "jb determined"

    add "#0a0a0a"
    if renpy.loadable(_enc_bg):
        add Transform(_enc_bg, size=(config.screen_width, config.screen_height))
    ## Dim the bg so the two figures + choices read (mockup: "lower opacity").
    add Solid("#000000bb")
    use class_color_frame(thickness=6)

    ## JB on the left, the enemy on the right — a face-off.
    add _enc_jb xpos 40 yalign 1.0 zoom 0.98
    if renpy.has_image(_enc_spr, exact=True):
        add _enc_spr xpos 1150 yalign 1.0 zoom 0.62

    text "[_enc_name!u]":
        xalign 0.5
        ypos 70
        color "#ff2a2a"
        size 46
        bold True
        font "fonts/RobotoMono-Regular.ttf"
        outlines [ (3, "#000000", 0, 0) ]

    text "The case is in front of you.":
        xalign 0.5
        ypos 138
        color "#cdbd97"
        size 20
        italic True
        font "fonts/RobotoMono-Regular.ttf"

    vbox:
        xpos 690
        yalign 0.62
        spacing 26

        button:
            xysize (560, 92)
            background Frame(Solid("#3a0e0e"), 4, 4)
            hover_background Frame(Solid("#6a1414"), 4, 4)
            action Return("fight")
            vbox:
                yalign 0.5
                xfill True
                text "FIGHT":
                    xalign 0.5
                    color "#ff5a4a"
                    size 32
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                text "Take the case. Rewards on the table.":
                    xalign 0.5
                    color "#caa"
                    size 16
                    font "fonts/RobotoMono-Regular.ttf"

        if can_flee:
            button:
                xysize (560, 92)
                background Frame(Solid("#102a18"), 4, 4)
                hover_background Frame(Solid("#1d5230"), 4, 4)
                action Return("flee")
                vbox:
                    yalign 0.5
                    xfill True
                    text "LET THEM GO":
                        xalign 0.5
                        color "#6fdd92"
                        size 32
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"
                    text "Walk away.  -25 Hatred.  No rewards.":
                        xalign 0.5
                        color "#9ac0a6"
                        size 16
                        font "fonts/RobotoMono-Regular.ttf"


## ---------------------------------------------------------------------------
## battle_with — generalised entry point for any ENEMY_LIBRARY enemy.
## Colonel keeps colonel_event; this wrapper handles ladder rungs only.
## ---------------------------------------------------------------------------

label battle_with(enemy_id, tier):

    if tier == "medium":
        play music "audio/system_knows_better.mp3" fadein 0.8
    elif tier == "hard":
        play music "audio/evidence_locker_pulse.wav" fadein 0.8
    else:
        play music "audio/panelak_nocni_smycka.wav" fadein 0.8
    $ renpy.save("auto-ladder", "Ladder — {}".format(enemy_id))

    call battle_intro(enemy_id) from _call_battle_intro

    ## Pre-battle standoff — engage or walk away. Bosses set no_flee.
    $ _enc_can_flee = not ENEMY_LIBRARY.get(enemy_id, {}).get("no_flee", False)
    call screen encounter_choice(enemy_id, _enc_can_flee)

    if _return == "flee":
        $ stats.increment_stats_pcr_hatred(-25)
        "You look at them. You look at the paperwork it would become."
        "Not tonight. You let it go — and the pressure behind your eyes drops a notch."
        show screen outcome_panel("- 25 Hatred")
        pause 1.0
        hide screen outcome_panel
        return

    python:
        battle_init(enemy_id)
        battle_start_player_turn()

    call screen battle_screen

    python:
        _outcome = battle_outcome()
        battle_finish()

    if _outcome == "defeat":
        call forced_detour(enemy_id, tier) from _call_forced_detour
        return

    python:
        _reward_cash = BATTLE_MONEY_REWARD.get(tier, 0)
        if _reward_cash > 0 and stats is not None:
            stats.increment_stats_value_money(_reward_cash)
        try:
            relic_on_victory()
        except NameError:
            pass
        _victory_lines = ENEMY_LIBRARY.get(enemy_id, {}).get("victory_lines", [])

    if _victory_lines:
        python:
            for _line in _victory_lines:
                renpy.say(None, _line)

    if _reward_cash > 0:
        "[_reward_cash:,] CZK."

    python:
        _rewards = pick_battle_rewards(tier)

    if _rewards:
        call screen card_reward_trio_screen(cards=_rewards)
        python:
            if _return and _return not in ("skip", None):
                grant_card(_return, silent=False)

    ## Hard-tier enemies are the ladder's elites — they drop gear. One relic
    ## per hard win, a random piece JB doesn't already carry. (Act bosses will
    ## grant guaranteed/chosen relics in a later slice; this is the baseline
    ## drip so relics are reachable in a normal run.)
    ## Relic drops — gear off the ladder's tougher cases. Hard wins always
    ## drop (these are the elites); medium wins drop at 50% so the first relic
    ## can land ~day 10-14 and actually SHAPE the back half of the run instead
    ## of arriving as day-18 garnish. Easy tier never drops — a turn-1 relic on
    ## a 10-card starter deck would flatten the early-game decision texture.
    ## (Act bosses will later grant guaranteed/chosen relics on top of this.)
    python:
        _relic_drop = None
        _relic_roll = (tier == "hard") or (tier == "medium" and __import__("random").random() < 0.5)
        if _relic_roll:
            _relic_drop = random_unowned_relic()
            if _relic_drop:
                grant_relic(_relic_drop, silent=True)
                _relic_meta = RELIC_LIBRARY.get(_relic_drop, {})

    if _relic_drop:
        "You pocket something from the scene: [_relic_meta[name]]."
        "[_relic_meta[hook]]"

    return
