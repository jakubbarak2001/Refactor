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
        "easy":   3000,
        "medium": 5000,
        "hard":   7500,
    }

    def _battle_ladder_band(day):
        if day <= 9:
            return "easy"
        if day <= 17:
            return "medium"
        return "hard"

    ## Walking away lowers the death clock. The relief scales with the weight
    ## of the case you're refusing — a back-alley tagger barely registers; an
    ## act boss is a reckoning, so denying it drops a real chunk of Hatred.
    ## This is the whole point of the deny system: a legible trade — relief now
    ## vs. the cards / cash / gear you forfeit. A run that flees EVERYTHING
    ## reaches the Colonel low-Hatred but near-starter-deck — the Pacifist line.
    FLEE_HATRED_RELIEF = {"easy": 15, "medium": 25, "hard": 35}

    def flee_hatred_relief(tier, is_boss=False, enemy_id=None):
        ## A per-enemy flee_relief override (set in the enemy def) wins over the
        ## tier table — lets a specific case carry its own deny weight.
        if enemy_id is not None:
            _ov = ENEMY_LIBRARY.get(enemy_id, {}).get("flee_relief")
            if _ov is not None:
                return _ov
        return FLEE_HATRED_RELIEF.get(tier, 25) + (10 if is_boss else 0)

    def flee_czk_penalty(enemy_id):
        ## The Colonel docks your pay for letting a case slide. 0 (no penalty)
        ## for everyone unless the enemy def sets flee_czk_penalty.
        return ENEMY_LIBRARY.get(enemy_id, {}).get("flee_czk_penalty", 0)

    ## Act bosses — fixed-day reckonings that cap each act, fired with priority
    ## over the random ladder/event roll. Each is an existing, fully-arted enemy
    ## promoted to boss (higher HP, no_flee, guaranteed relic). Returns
    ## (enemy_id, reward_tier, act) or (None, None, None). reward_tier feeds the
    ## existing money/card-reward tables (no "boss" tier needed downstream).
    ##   Act I  (day 10+): Grundza        — the meth lab, the first real wall.
    ##   Act II (day 20+): Colonel's Guard — his elite intercepts you.
    ##   Act III (day 30): the Colonel (own event).
    def boss_check(day):
        done = getattr(store, "_act_bosses_done", None) or set()
        if 1 not in done and day >= 10:
            return ("grundza", "medium", 1)
        if 2 not in done and day >= 20:
            return ("garda", "hard", 2)
        return (None, None, None)

    def _ladder_init_pool():
        """Lazy-init the per-run drainable ladder pool."""
        if not hasattr(store, 'battle_ladder_pool') or store.battle_ladder_pool is None:
            ## grundza (Act I) and garda (Act II) are pulled from the random
            ## pool — they fire as fixed-day act bosses via boss_check(), not
            ## as drainable ladder rungs.
            store.battle_ladder_pool = {
                "easy":   ["rvac", "sprejeri", "fanousek", "spis"],
                "medium": ["nguyen", "lawyer", "dispatcher", "vlk"],
                "hard":   ["inspekce", "lifer", "estebak"],
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
## FIGHT (engage → rewards + risk) or LET THEM GO (Hatred relief, walk away,
## forfeit all rewards). The relief valve is the cop choosing not to escalate;
## the cost is the cards/cash/gear you don't get. Every battle_with fight is
## deniable (only the Colonel can't be, and he doesn't route through here) so a
## pure Pacifist run is reachable.
##
## The decision-relevant stats (HP / Hatred / Wallet / Deck) AND a concrete
## preview of each choice's payoff sit right on the panel — the player should
## never have to guess what they're trading. Returns "fight" or "flee".
## ---------------------------------------------------------------------------

screen encounter_choice(enemy_id, tier="medium", can_flee=True):
    modal True
    zorder 550

    python:
        _enc_e      = ENEMY_LIBRARY.get(enemy_id, {}) or {}
        _enc_name   = _enc_e.get("display_name", enemy_id)
        _enc_spr    = "{} neutral".format(_enc_e.get("sprite_id") or enemy_id)
        _enc_bg_id  = _enc_e.get("bg_id") or _enc_e.get("sprite_id") or enemy_id
        _enc_bg     = "images/backgrounds/bg_{}.jpg".format(_enc_bg_id)
        _enc_is_boss = _enc_e.get("is_boss", False)

        ## Contemplative JB — hand-on-chin "do I take this one?" sprite. Falls
        ## back to the mood sprites until that art lands, so this never breaks.
        _enc_jb_path = "images/sprites/jb_contemplative.png"
        if renpy.loadable(_enc_jb_path):
            _enc_jb = im.Scale(_enc_jb_path, 600, 900)
        elif stats and stats.pcr_hatred >= 60:
            _enc_jb = "jb angry"
        else:
            _enc_jb = "jb determined"

        ## ── What FIGHT pays out (kept in sync with battle_with's reward path).
        _enc_cash = BATTLE_MONEY_REWARD.get(tier, 0)
        if _enc_is_boss or tier == "hard":
            _enc_gear_txt = " · guaranteed gear"
        elif tier == "medium":
            _enc_gear_txt = " · gear (coin-flip)"
        else:
            _enc_gear_txt = ""
        _enc_fight_sub = "+{:,} CZK · draft a card{}".format(_enc_cash, _enc_gear_txt)

        ## ── What WALK AWAY pays out.
        _enc_relief = flee_hatred_relief(tier, _enc_is_boss, enemy_id)
        _enc_penalty = flee_czk_penalty(enemy_id)
        _enc_flee_label = _enc_e.get("flee_label") or ("WALK AWAY" if _enc_is_boss else "LET THEM GO")
        if _enc_penalty > 0:
            _enc_flee_sub = "-{} Hatred · -{:,} CZK · forfeit the rewards".format(_enc_relief, _enc_penalty)
        else:
            _enc_flee_sub = "-{} Hatred · forfeit the rewards".format(_enc_relief)

    add "#0a0a0a"
    if renpy.loadable(_enc_bg):
        add Transform(_enc_bg, size=(config.screen_width, config.screen_height))
    ## Dim the bg so the two figures + choices read (mockup: "lower opacity").
    add Solid("#000000bb")
    use class_color_frame(thickness=6)

    ## Run stat readout (money / coding / hatred / day) — the hub bar up top.
    use stats_bar

    ## JB on the left, the enemy on the right — a face-off at matched scale.
    ## Both sprites are 600x900 (im.Scale) shown at zoom 0.98; the enemy mirrors
    ## JB's 40px edge margin and clears the choice buttons (which end at x~1250).
    add _enc_jb xpos 40 yalign 1.0 zoom 0.98
    if renpy.has_image(_enc_spr, exact=True):
        add _enc_spr xpos 1292 yalign 1.0 zoom 0.98

    ## Name + subtitle sit below the stat bar (54px) with headroom.
    text "[_enc_name!u]":
        xalign 0.5
        ypos 150
        color "#ff2a2a"
        size 46
        bold True
        font "fonts/RobotoMono-Regular.ttf"
        outlines [ (3, "#000000", 0, 0) ]

    text "The case is in front of you. What it costs you is right here.":
        xalign 0.5
        ypos 218
        color "#cdbd97"
        size 20
        italic True
        font "fonts/RobotoMono-Regular.ttf"

    vbox:
        xpos 690
        yalign 0.5
        spacing 26

        button:
            xysize (560, 96)
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
                text "[_enc_fight_sub]":
                    xalign 0.5
                    color "#e0b0a0"
                    size 16
                    font "fonts/RobotoMono-Regular.ttf"

        if can_flee:
            button:
                xysize (560, 96)
                background Frame(Solid("#102a18"), 4, 4)
                hover_background Frame(Solid("#1d5230"), 4, 4)
                action Return("flee")
                vbox:
                    yalign 0.5
                    xfill True
                    text "[_enc_flee_label]":
                        xalign 0.5
                        color "#6fdd92"
                        size 32
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"
                    text "[_enc_flee_sub]":
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

    ## Pre-battle standoff — engage or walk away. The encounter honours the
    ## enemy's no_flee flag; the act bosses now leave it False so a flee-
    ## everything Pacifist run stays reachable (the Colonel, the one fight you
    ## truly can't refuse, never routes through here). no_flee stays a live
    ## lever for any future genuinely-mandatory ladder fight.
    $ _enc_data    = ENEMY_LIBRARY.get(enemy_id, {})
    $ _enc_is_boss = _enc_data.get("is_boss", False)
    call screen encounter_choice(enemy_id, tier, not _enc_data.get("no_flee", False))

    if _return == "flee":
        python:
            _flee_relief = flee_hatred_relief(tier, _enc_is_boss, enemy_id)
            _flee_penalty = flee_czk_penalty(enemy_id)
            stats.increment_stats_pcr_hatred(-_flee_relief)
            ## Fleeing once disqualifies the "Peace was never an option" run.
            store._run_fled = getattr(store, '_run_fled', 0) + 1
            if _flee_penalty > 0:
                stats.increment_stats_value_money(-_flee_penalty)
                _flee_outcome = "- {} Hatred   - {:,} CZK".format(_flee_relief, _flee_penalty)
            else:
                _flee_outcome = "- {} Hatred".format(_flee_relief)
        if _enc_is_boss:
            "You weigh it — the guns, the gold, the long fall if it goes wrong."
            "Not this one. You step back into the dark before he's sure you were ever there."
        else:
            "You look at them. You look at the paperwork it would become."
            "Not tonight. You let it go — and the pressure behind your eyes drops a notch."
        if _flee_penalty > 0:
            "A case left open is a number that doesn't add up. The Colonel's people find the gap by morning — [_flee_penalty:,] crowns, docked, no conversation."
        window hide
        show screen outcome_panel(_flee_outcome)
        pause
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

    ## Victory — this enemy is down. Counts as a kill (breaks Pacifist). The
    ## Colonel doesn't pass through here, so beating him with _run_kills still 0
    ## is the achievement.
    $ store._run_kills = getattr(store, '_run_kills', 0) + 1

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
        _is_boss = ENEMY_LIBRARY.get(enemy_id, {}).get("is_boss", False)
        ## Bosses ALWAYS drop a relic; hard wins always; medium 50%; easy none.
        _relic_roll = _is_boss or (tier == "hard") or (tier == "medium" and __import__("random").random() < 0.5)
        if _relic_roll:
            _relic_drop = random_unowned_relic(relic_drop_weights(tier, _is_boss))
            if _relic_drop:
                grant_relic(_relic_drop, silent=True)
                _relic_meta = RELIC_LIBRARY.get(_relic_drop, {})
                _relic_name = _relic_meta.get("name", _relic_drop)
                _relic_hook = _relic_meta.get("hook", "")

    if _relic_drop:
        "You pocket something from the scene: [_relic_name]."
        "[_relic_hook]"

    return
