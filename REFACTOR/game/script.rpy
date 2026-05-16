################################################################################
## REFACTOR - Main Script
## Full 30-day game loop with all three arcs
################################################################################

## ---------------------------------------------------------------------------
## GAME START
## ---------------------------------------------------------------------------

label start:

    scene bg_black
    $ play_daily_music(fadein=2.0)

    ## Difficulty selection — hidden for now; default to Easy
    $ init_game("easy")

    ## Character class selection
    call character_class_selection from _call_character_class_selection

    ## Arc I - Car Incident (Day 1)
    call car_incident from _call_car_incident

    ## Main 30-day loop
    call main_loop from _call_main_loop

    return


## ---------------------------------------------------------------------------
## DEV — Skip straight to the Colonel deck-fight
## Configured for fast iteration: bootstraps stats + a representative deck,
## skips the 30-day loop entirely. Dev-only entry point on the main menu.
## ---------------------------------------------------------------------------

label dev_skip_to_colonel:

    scene bg_black
    play music "audio/tension_theme.mp3" fadein 1.0

    python:
        ## Pick a class — cycle via store flag so successive presses test all three
        _classes = ["bodybuilder", "dark_empath", "biohacker"]
        _idx = getattr(store, '_dev_class_idx', 0) % 3
        store._dev_class_idx = _idx + 1
        _picked_class = _classes[_idx]

        ## Init game on Hard
        init_game("hard")
        stats.player_class = _picked_class
        apply_class_bonuses(stats)
        init_player_deck()

        ## Mid-late stats (representative of a real run reaching colonel).
        ## Coding clamped to the class ceiling so BB (cap 100) tests at its
        ## actual maximum instead of an impossible 110.
        _dev_ceiling = CLASS_DATA.get(_picked_class, {}).get("coding_ceiling", 250)
        stats.coding_skill    = min(110, _dev_ceiling)
        stats.available_money = 60000
        stats.pcr_hatred      = 50

        ## Grant a representative deck of acquired cards
        for _cid in ["iron_will", "iron_will", "boundary", "compile", "compile",
                      "refactor", "side_income", "backup", "backup", "vigil"]:
            grant_card(_cid, silent=True)

        ## Cycle Martin gift across runs to test all four
        _gifts = ["paragraph_4b", "ghost_secret", "job_offer", "stoic_refactor"]
        _gift_idx = getattr(store, '_dev_gift_idx', 0) % 4
        store._dev_gift_idx = _gift_idx + 1
        _picked_gift = _gifts[_gift_idx]
        grant_card(_picked_gift, silent=True)
        stats.final_boss_buff = _picked_gift.upper()

        ## BB also gets iron_stance to test class symmetry
        if _picked_class == "bodybuilder":
            grant_card("iron_stance", silent=True)

        day_cycle.current_day = 25
        stats.colonel_day = 25

        ## Pre-compose a single status line — avoids nested-bracket interpolation
        _dev_summary = "DEV BOOT: {} | gift {} | Coding {} | Money {} CZK | Hatred {} | Deck {} cards".format(
            _picked_class.upper(),
            _picked_gift,
            stats.coding_skill,
            stats.available_money,
            stats.pcr_hatred,
            len(player_deck.cards),
        )

    "[_dev_summary]"

    jump colonel_event


## ---------------------------------------------------------------------------
## DEV — Ladder battle direct entry. Cycles through the 10-enemy roster on
## successive presses so the wrinkles/decks/decks-vs-rewards can be sanity-
## checked without playing through 30 days. Dev-only; no menu hookup yet.
## ---------------------------------------------------------------------------

label dev_ladder_test:

    scene bg_black
    play music "audio/tension_theme.mp3" fadein 0.8

    python:
        _ladder_roster = [
            ("rvac",       "easy"),
            ("sprejeri",   "easy"),
            ("fanousek",   "easy"),
            ("spis",       "easy"),
            ("nguyen",     "medium"),
            ("grundza",    "medium"),
            ("lawyer",     "medium"),
            ("dispatcher", "medium"),
            ("inspekce",   "hard"),
            ("garda",      "hard"),
        ]
        _idx = getattr(store, '_dev_ladder_idx', 0) % len(_ladder_roster)
        store._dev_ladder_idx = _idx + 1
        _picked_enemy, _picked_tier = _ladder_roster[_idx]

        ## Boot BB on Hard with a representative mid-run kit so the fight
        ## isn't trivial. Mirrors dev_skip_to_colonel's prep.
        init_game("hard")
        stats.player_class = "bodybuilder"
        apply_class_bonuses(stats)
        init_player_deck()
        stats.coding_skill    = 80
        stats.available_money = 40000
        stats.pcr_hatred      = 30

        for _cid in ["iron_will", "bracing", "gut_punch", "compile",
                      "radio_call", "backup", "quick_jab"]:
            grant_card(_cid, silent=True)

        day_cycle.current_day = {"easy": 6, "medium": 12, "hard": 21}.get(_picked_tier, 6)

        _ladder_summary = "DEV LADDER: {} ({}) | day {} | deck {} cards".format(
            _picked_enemy, _picked_tier, day_cycle.current_day, len(player_deck.cards),
        )

    "[_ladder_summary]"

    call battle_with(_picked_enemy, _picked_tier)

    return


## ---------------------------------------------------------------------------
## DIFFICULTY SELECTION
## ---------------------------------------------------------------------------

label difficulty_selection:

    scene bg_black

    $ store._chosen_difficulty = None
    call screen difficulty_selection_screen

    $ init_game(store._chosen_difficulty)


    return


## ---------------------------------------------------------------------------
## CHARACTER CLASS SELECTION
## ---------------------------------------------------------------------------

label character_class_selection:

    ## Suppress the Ren'Py quick_menu so it doesn't flash during the fade
    ## transition between the (modal) difficulty screen and this intro.
    $ quick_menu = False

    scene bg_class_intro with fade

    "Before the grind begins — who are you, JB?"
    "Your class is permanent. Choose carefully."

    scene bg_black with fade

    $ quick_menu = True

    call screen class_selection_screen

    ## Apply starting bonuses based on class choice
    python:
        apply_class_bonuses(stats)
        init_player_deck()

    python:
        _cls_accent  = class_accent_color(stats.player_class)
        _hdr_open    = "{cps=12}{size=+14}{b}{color=" + _cls_accent + "}"
        _hdr_mid     = "{/color}"
        _hdr_close   = "{/b}{/size}{/cps}"
        if stats.player_class == "bodybuilder":
            _flv = "Every rep is a rep closer to your freedom."
            _hdr = _hdr_open + "BODYBUILDER" + _hdr_mid + " SELECTED." + _hdr_close
        elif stats.player_class == "dark_empath":
            _flv = "You see through people. That is both your weapon and your curse."
            _hdr = _hdr_open + "DARK EMPATH" + _hdr_mid + " SELECTED." + _hdr_close
        elif stats.player_class == "biohacker":
            _flv = "Your body is a machine. Let's see how far you can push it."
            _hdr = _hdr_open + "BIOHACKER" + _hdr_mid + " SELECTED." + _hdr_close
        else:
            _flv = ""
            _hdr = "Class selected."
        if _flv:
            _flv_cps  = max(1, int(round(len(_flv) / 0.5)))
            _class_msg = _hdr + "{w=0.5}\n{cps=" + str(_flv_cps) + "}{i}{color=#e0c060}" + _flv + "{/color}{/i}{/cps}"
        else:
            _class_msg = _hdr

    ## Class-defining background under the "X selected" beat
    if stats.player_class == "bodybuilder":
        scene bg_bb_gym with Dissolve(0.6)

    "[_class_msg]"

    stop sound fadeout 0.4

    ## --- Class intro vignette: 3 lines establishing JB's lifestyle for this class ---
    if stats.player_class == "bodybuilder":
        scene bg_jb_flat with Dissolve(0.6)
        "05:14 AM. The mirror in the bathroom doesn't lie."
        "You knock out fifty push-ups before the kettle boils. Black coffee. Two raw eggs. A sticky note on the fridge: 'PROGRESSIVE OVERLOAD.'"
        "You drive to the station. Your forearms ache the right way."
    elif stats.player_class == "dark_empath":
        scene bg_police_interior with Dissolve(0.6)
        "07:02 AM. Coffee black. Two minutes of stillness in the kitchen, watching the radiator condensation drift."
        "You catalogue your colleagues in the morning briefing — who slept, who didn't, who is thinking about leaving but hasn't said it yet."
        "You don't speak unless asked. Speaking gives away too much."
    elif stats.player_class == "biohacker":
        scene bg_police_interior with Dissolve(0.6)
        "06:03 AM. HRV reading: 67ms. Sleep score: 8.2."
        "You stack the morning compounds — magnesium glycinate, L-theanine, modafinil — into a small glass tray. You photograph the dose. You log it."
        "You drink a litre of structured water before the first email arrives."

    return


## ---------------------------------------------------------------------------
## MAIN 30-DAY LOOP
## ---------------------------------------------------------------------------

label main_loop:

    ## Self-heal: if the player saved mid-intro while quick_menu was suppressed
    ## (character_class_selection wraps two narrative lines with quick_menu=False),
    ## any reload past that point should re-enable it.
    $ quick_menu = True

    python:
        # Ensure state is initialised (fallback in case jump used directly)
        if stats is None:
            init_game("easy")

    jump day_start


label day_start:

    python:
        current_day = day_cycle.current_day

    ## Dynamic music routing — tension increases with hatred. Daily-loop
    ## branch uses the rotating pool (see play_daily_music in python_logic.rpy).
    python:
        if stats.pcr_hatred >= 75:
            renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
        else:
            play_daily_music(fadein=1.5)

    scene bg_jb_flat

    ## Win condition check — coding skill >= 100 at day 30 handled in colonel event
    ## Lose conditions checked each day

    python:
        # Check loss conditions
        if stats.pcr_hatred >= 100:
            renpy.jump("hatred_collapse_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")

    ## Crisis event — fires once per run when Hatred reaches 85. Top-level
    ## `call expression ... from _xxx` so the named return label survives
    ## script edits (save stability — see the comment near salary_day above).
    python:
        _should_crisis = (
            stats.pcr_hatred >= 85
            and not getattr(store, '_crisis_triggered', False)
        )
        if _should_crisis:
            store._crisis_triggered = True
            _crisis_label = "crisis_event_" + stats.player_class
    if _should_crisis:
        call expression _crisis_label from _call_crisis_event_daystart

    show screen stats_bar
    call screen day_transition_screen(current_day) with arc_fade

    ## Nootropic morning effects — crash, withdrawal, or dependency notification
    python:
        _noot_result = apply_nootropic_morning_effects()
        _noot_tag    = _noot_result[0] if _noot_result else None
        _noot_flavor = _noot_result[1] if _noot_result else ""

    if _noot_tag == "withdrawal":
        scene bg_jb_flat
        "[[WITHDRAWAL]"
        "[_noot_flavor]"

    if _noot_tag == "dependency_triggered":
        scene bg_jb_flat
        "[[DEPENDENCY TRIGGERED]"
        "[_noot_flavor]"

    if _noot_tag == "soft_dependency":
        scene bg_jb_flat
        "[[TOLERANCE WARNING]"
        "[_noot_flavor]"

    if _noot_tag == "crash":
        scene bg_jb_flat
        "[[AFTEREFFECTS]"
        "[_noot_flavor]"

    ## Special events. Top-level `call ... from _xxx` (NOT renpy.call inside a
    ## python block) so saves taken mid-call survive future line-shifting edits
    ## to script.rpy — the `from` clause creates a named return label that's
    ## looked up by name, not by line number.
    if current_day == 14:
        call salary_day from _call_salary_day_daystart

    # if current_day == 15:
    #     call midnight_call from _call_midnight_call_daystart

    ## Battle ladder / random events:
    ## - Regular cadence: days 3, 6, 9, 12, 15, 18, 21
    ## - Plus day 27 — a Hard-tier slot for players who deferred the Colonel
    ##   to day 30 (the day-25 Colonel path ends the game before reaching 27).
    if current_day in (3, 6, 9, 12, 15, 18, 21, 27):
        call random_event_check from _call_random_event_check_daystart

    if current_day == 24:
        call martin_meeting from _call_martin_meeting_daystart

    ## Self-heal poisoned saves: stats.colonel_day must be 25 (Martin's
    ## "brave" path) or 30 (default / "reasonable"). Any other value is
    ## stale state from an older build or a dev-console tweak — left
    ## alone it would trigger the final boss mid-run on load.
    python:
        if stats.colonel_day not in (25, 30):
            stats.colonel_day = 30

    if current_day == stats.colonel_day and current_day >= 25:
        call colonel_event from _call_colonel_event_daystart

    ## BH-only random spending event — fires on non-event days, ~30% chance.
    ## "The cost of optimizing." Pool reshuffles when exhausted (events recur).
    python:
        _bh_event_day = (
            current_day in (3, 6, 9, 12, 14, 15, 18, 21, 24, 27) or
            current_day == stats.colonel_day
        )
        _is_bh_player = (stats and stats.player_class == "biohacker")
    if _is_bh_player and not _bh_event_day:
        call bh_spending_check from _call_bh_spending_check

    jump daily_menu


## ---------------------------------------------------------------------------
## DAILY MENU
## ---------------------------------------------------------------------------

label daily_menu:

    python:
        current_day = day_cycle.current_day

    scene bg_jb_flat

    python:
        # Check loss conditions at start of each menu loop
        if stats.pcr_hatred >= 100:
            renpy.jump("hatred_collapse_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")

    # Hatred intro popup — fires once per run at first ≥40 crossing.
    if stats.pcr_hatred >= 40 and not getattr(store, '_hatred_intro_shown', False):
        $ store._hatred_intro_shown = True
        call screen hatred_intro_popup

    show screen stats_bar

    ## Custom hub screen — buttons use Jump() actions to route to existing labels.
    call screen daily_hub_screen


label select_activity:
    python:
        if activity_selected:
            renpy.jump("daily_menu")

    ## Custom tile-grid screen — buttons Jump() to activity_* labels directly.
    call screen activity_select_screen


## ---------------------------------------------------------------------------
## ACTIVITY: GYM
## ---------------------------------------------------------------------------

label activity_gym:

    scene bg_bb_gym

    python:
        ## Gym streak tracking
        if not hasattr(store, 'gym_streak'):
            store.gym_streak = 0
        _streak_bonus = min(store.gym_streak * 3, 15)  ## +3 extra hatred reduction per streak day, max +15
        _gym_cost = adjusted_cost(400)

    "You head to the gym with your trainer.\nTraining will help you relax, but it will cost [_gym_cost] CZK."
    python:
        _streak_msg = ""
        if store.gym_streak >= 1:
            _streak_msg = "\n[STREAK: {} days in a row — extra -{} Hatred bonus]".format(store.gym_streak, _streak_bonus)
    "Gym attendance: [store.gym_streak] day streak.[_streak_msg]"

    menu:
        "PAY [_gym_cost] CZK — We go gym!":
            ## Same workout SFX as the BB hover preview on the class-select
            ## screen (audio/sfx/gym_plates.mp3) — clicking "we go gym" should
            ## sound like clanging plates.
            play sound "audio/sfx/gym_plates.mp3"
            python:
                if not stats.try_spend_money(_gym_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS] You check your wallet... you don't even have [_gym_cost] CZK for the gym entry.")
                    renpy.jump("select_activity")
                else:
                    _roll = __import__('random').randint(1, 3)

            python:
                _bb_bonus = 5 if stats.player_class == "bodybuilder" else 0
                ## Always-apply progression (you completed the session — UPGRADE or HEAL):
                store.gym_streak += 1
                ## BB-only common: spotter granted at the 3-day streak.
                if store.gym_streak == 3 and stats.player_class == "bodybuilder":
                    grant_card("spotter", silent=True)
                if store.gym_streak >= 5:
                    _newly_unlocked = unlock_achievement("gym_rat")
                    if _newly_unlocked and stats.player_class == "bodybuilder":
                        grant_card("iron_stance", silent=True)
                _streak_add = min(store.gym_streak * 3, 15)
                ## Three narrative flavors per session — cosmetic only now that
                ## card grants are gone (replaced by the upgrade choice).
                if _roll == 1:
                    _total_red = 25 + _bb_bonus + _streak_add
                    _gym_text = "Personal record. The bar tells the truth. The Colonel doesn't exist for 90 minutes."
                elif _roll == 2:
                    _total_red = 15 + _bb_bonus + _streak_add
                    _gym_text = "Solid session. Head's quieter than this morning."
                else:
                    _total_red = 10 + _bb_bonus + _streak_add
                    _gym_text = "Heavy day. You finish anyway. Slightly less likely to flip a desk today."

            "[_gym_text]"

            ## SOMA always lands for BB — gym session is "I trained the body."
            $ add_soma(1)

            ## Pre-compute the HEAL payload so the choice screen can preview
            ## the numbers. Apply nothing yet — heal block runs only if the
            ## player picks HEAL.
            python:
                ## Hatred relief is unconditional now — you completed the session,
                ## you get the head-clear whether you bank it as a card upgrade or
                ## a heal. Removed from the choice preview accordingly.
                stats.increment_stats_pcr_hatred(-_total_red)

                _GYM_HP_BONUS_CAP = 30
                _gym_max_bump = max(0, min(5, _GYM_HP_BONUS_CAP - getattr(store, 'gym_max_hp_bonus', 0)))
                ## Lazy-init run_hp_max BEFORE choice so the heal preview is
                ## accurate. The init itself is non-destructive (it doesn't
                ## change current HP unless run_hp_max was None).
                if store.run_hp_max is None:
                    if stats.player_class == "bodybuilder":
                        _class_base = 115
                    elif stats.player_class == "dark_empath":
                        _class_base = 75
                    elif stats.player_class == "biohacker":
                        _class_base = 80
                    else:
                        _class_base = 80
                    store.run_hp_max = _class_base + store.gym_max_hp_bonus
                    store.run_hp = store.run_hp_max
                _heal_max_future = store.run_hp_max + _gym_max_bump
                _gym_heal = int(round(_heal_max_future * 0.25))
                _heal_parts = ["- {:,} CZK".format(_gym_cost)]
                if _gym_max_bump > 0:
                    _heal_parts.append("{{color=#00cc88}}+{} MAX HP{{/color}}".format(_gym_max_bump))
                else:
                    _heal_parts.append("MAX HP capped")
                _heal_parts.append("{{color=#00cc88}}+{} HP{{/color}}".format(_gym_heal))
                if _streak_add:
                    _heal_parts.append("[STREAK x{}]".format(store.gym_streak))
                _gym_heal_text = ", ".join(_heal_parts)

            label .choice_loop:
                pass

            window hide
            call screen gym_choice_screen(heal_stats_text=_gym_heal_text)
            $ _gym_choice = _return

            if _gym_choice == "upgrade":
                call _run_card_upgrade_flow
                if _return:
                    python:
                        _plus_id = _return
                        _c = CARD_LIBRARY.get(_plus_id, {})
                        _soma_suffix = "  ·  +1 SOMA" if stats.player_class == "bodybuilder" else ""
                        _gym_outcome_final = "[CARD UPGRADED] " + _c.get("name", _plus_id) + _soma_suffix
                else:
                    jump activity_gym.choice_loop
            else:
                python:
                    ## HEAL path — apply max HP bump and HP heal. Hatred already
                    ## dropped above (unconditional).
                    store.gym_max_hp_bonus = getattr(store, 'gym_max_hp_bonus', 0) + _gym_max_bump
                    store.run_hp_max += _gym_max_bump
                    store.run_hp = min(store.run_hp_max, store.run_hp + _gym_heal)
                    _soma_suffix = "  ·  +1 SOMA" if stats.player_class == "bodybuilder" else ""
                    _gym_outcome_final = _gym_heal_text + _soma_suffix

            window hide
            show screen outcome_panel(_gym_outcome_final)
            pause
            hide screen outcome_panel

            python:
                activity_selected = True
                store.gym_day = True
            jump end_day

        "Return to menu.":
            jump daily_menu


## ---------------------------------------------------------------------------
## ACTIVITY: HEAVY SESSION (BODYBUILDER ONLY)
## Class-specific relief replacing the old universal therapy. Same post-
## session UPGRADE-vs-HEAL choice as regular gym, but the HEAL side is
## deeper (-30 hatred, +15 HP, no Max HP bump — that's the regular gym's
## job). The UPGRADE side is unchanged from regular gym: pick one card,
## bank +1 SOMA, lose the heal.
## ---------------------------------------------------------------------------

label activity_gym_heavy:

    scene bg_bb_gym

    python:
        _heavy_cost = adjusted_cost(800)
        if not stats.try_spend_money(_heavy_cost):
            renpy.say(None, "[[INSUFFICIENT FUNDS] Heavy session needs {:,} CZK. The good gym isn't free.".format(_heavy_cost))
            renpy.jump("select_activity")
        ## Lazy-init gym_streak — same guard activity_gym uses, since HEAVY SESSION
        ## might be a player's first gym-equivalent activity on Day 1.
        if not hasattr(store, 'gym_streak'):
            store.gym_streak = 0

    "The owner meets you at the door. Doesn't say hello. Looks at your shoulders, then your eyes, then nods once."
    "'Heavy day. We go until you can't grip the bar.'"
    "Two hours later your forearms feel like wet rope and your back is one long ache."
    "You drive home with the windows down. The wind is loud. Your head is finally quiet."

    python:
        ## Always-apply progression — you completed the session.
        store.gym_streak += 1
        add_soma(1)
        if store.gym_streak == 3 and stats.player_class == "bodybuilder":
            grant_card("spotter", silent=True)
        if store.gym_streak >= 5:
            _newly_unlocked = unlock_achievement("gym_rat")
            if _newly_unlocked and stats.player_class == "bodybuilder":
                grant_card("iron_stance", silent=True)
        ## Pre-compute heavy-session HEAL payload (heavier than regular gym:
        ## -30 hatred + +15 HP, but no Max HP bump — that's the regular gym's
        ## job). Numbers only applied if the player picks HEAL.
        _heavy_heal = 15
        _heavy_heal_text = "- {:,} CZK, -30 PCR HATRED, +1 SOMA, +{} HP".format(_heavy_cost, _heavy_heal)

    label .choice_loop:
        pass

    window hide
    call screen gym_choice_screen(heal_stats_text=_heavy_heal_text)
    $ _heavy_choice = _return

    if _heavy_choice == "upgrade":
        call _run_card_upgrade_flow
        if _return:
            python:
                _plus_id = _return
                _c = CARD_LIBRARY.get(_plus_id, {})
                _heavy_outcome = "[CARD UPGRADED] " + _c.get("name", _plus_id) + "  ·  +1 SOMA"
        else:
            jump activity_gym_heavy.choice_loop
    else:
        python:
            ## HEAL path — apply hatred relief + HP heal.
            stats.increment_stats_pcr_hatred(-30)
            _rh = getattr(store, 'run_hp', None)
            _rhm = getattr(store, 'run_hp_max', None)
            if _rh is not None and _rhm is not None:
                store.run_hp = min(_rhm, _rh + _heavy_heal)
            _heavy_outcome = _heavy_heal_text

    window hide
    show screen outcome_panel(_heavy_outcome)
    pause
    hide screen outcome_panel

    python:
        activity_selected = True
        store.gym_day = True
    jump end_day


## ---------------------------------------------------------------------------
## Shared upgrade flow — picker → preview → reveal. Returns the new plus_id
## on confirm, or None if the player cancelled all the way out of the picker
## (caller loops back to gym_choice_screen). Used by activity_gym and
## activity_gym_heavy.
## ---------------------------------------------------------------------------

label _run_card_upgrade_flow:

    label .picker:
        window hide
        call screen deck_upgrade_picker
        $ _ucf_result = _return

        if _ucf_result == "cancel":
            return None

        $ _ucf_base = _ucf_result
        call screen card_upgrade_preview(base_id=_ucf_base)

        if _return == "cancel":
            jump _run_card_upgrade_flow.picker

        $ _ucf_plus = upgrade_card_in_deck(_ucf_base)

        if _ucf_plus is None:
            ## Defensive — shouldn't happen since picker only surfaces upgradeable
            ## cards, but if it does (race / save-load weirdness), bail back to
            ## the picker rather than crash.
            jump _run_card_upgrade_flow.picker

        play sound "audio/achivement_unlocked.mp3"
        call screen upgrade_reveal_screen(plus_id=_ucf_plus)
        return _ucf_plus


## ---------------------------------------------------------------------------
## ACTIVITY: RECOVERY (BIOHACKER ONLY)
## Red light + sauna + cold plunge protocol. Pure relief, no card.
## Doesn't increment the nootropic dose-counter — it's the body's own kit.
## ---------------------------------------------------------------------------

label activity_recovery:

    scene bg_police_interior

    python:
        _recovery_cost = adjusted_cost(500)
        if not stats.try_spend_money(_recovery_cost):
            renpy.say(None, "[[INSUFFICIENT FUNDS] The recovery clinic charges {:,} CZK. You don't have it.".format(_recovery_cost))
            renpy.jump("select_activity")

    "Twenty minutes in the red-light booth. Eight in the sauna. Two in the cold plunge — long enough that your respiratory rate normalizes back to baseline."
    "You log everything. Heart-rate variability up four points. Cortisol curve flatter than yesterday."
    "The data says you're recovering. Whether you {i}feel{/i} recovered is a separate question, but the data is the data."
    "You sleep eleven hours that night. No dreams. The morning is a clean buffer."

    python:
        ## Pure relief — no nootropic dose increment, no card.
        stats.increment_stats_pcr_hatred(-30)
        _recovery_outcome = "- {:,} CZK, -30 PCR HATRED".format(_recovery_cost)

    window hide
    show screen outcome_panel(_recovery_outcome)
    pause
    hide screen outcome_panel

    python:
        activity_selected = True
    jump end_day


## ---------------------------------------------------------------------------
## ACTIVITY: BOUNCER
## ---------------------------------------------------------------------------

label activity_bouncer:

    scene bg_jb_flat

    python:
        _bouncer_options = [
            {
                "label_name":     "bouncer_night_club",
                "title":          "NIGHT CLUB",
                "accent":         "#ffd700",
                "cost_text":      "FREE",
                "effect_text":    "+ CZK · low risk",
                "flavor_text":    "Drunks, mostly handled. The owner pays cash.",
                "class_relevant": False,
            },
            {
                "label_name":     "bouncer_strip_bar",
                "title":          "STRIP BAR",
                "accent":         "#ffd700",
                "cost_text":      "FREE",
                "effect_text":    "+ more CZK · ugly outcomes possible",
                "flavor_text":    "Pays better. You'll see things. You'll do things.",
                "class_relevant": False,
            },
        ]

    call screen activity_submenu(
        title       = "BOUNCER — PICK A VENUE",
        subtitle    = "Two doors. Different math.",
        options     = _bouncer_options,
        back_label  = "select_activity",
    )


label bouncer_night_club:

    scene bg_havana_club

    python:
        _roll = __import__('random').randint(1, 100)
        _bb_cash = 2500 if stats.player_class == "bodybuilder" else 0
        _bouncer_card = None
        ## Pending stat deltas — applied unconditionally if no card to offer,
        ## or only on PASS if there is one.
        _pending_money = 0
        _pending_hatred = 0
        if _roll <= 70:
            _pending_money = 4000 + _bb_cash
            _pending_hatred = 10
            _bouncer_card = "side_income"
            _btext = "Uneventful. Six hours in a doorway, nodding at people happier than you.\nBy 3 AM you're calculating how many more shifts like this to quit forever. The number is getting smaller."
            _boutcome = "+ {} CZK, +10 PCR HATRED{}".format(4000 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")
        elif _roll <= 90:
            _pending_money = 9000 + _bb_cash
            _pending_hatred = -10
            ## BB on a good night: meets the senior dev who'll review code for cash.
            ## paid_review is a skill-purchase card — still useful even without a
            ## hard coding cap (it's faster than studying). Others: side_income.
            _bouncer_card = "paid_review" if stats.player_class == "bodybuilder" else "side_income"
            _btext = "Rare night. Regulars tip heavy, the manager notices your work, and nobody throws up on anyone.\nDriving home at 4 AM, windows down: 'If this was my real job I would hate it slightly less.' Closest thing to joy you've felt all week."
            _boutcome = "+ {} CZK, -10 PCR HATRED{}".format(9000 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")
        else:
            ## Bad outcome — no card offered; stats apply unconditionally below.
            _pending_money = 4000 + _bb_cash
            _pending_hatred = 20
            _btext = "Two drunks fight over a woman interested in neither. You step in — one recognizes you. 'TO JE PŘECE POLDA!'\nPhone out. The group chat hasn't stopped since. You want to die."
            _boutcome = "+ {} CZK, +20 PCR HATRED{}".format(4000 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")

    "[_btext]"

    $ _bouncer_card_data = can_offer_card(_bouncer_card) if _bouncer_card else None

    if _bouncer_card_data is not None:
        window hide
        call screen card_offer_screen(card=_bouncer_card_data, source_label="BOUNCER", pass_stats_text=_boutcome)
        $ _took_bouncer = commit_card(_bouncer_card, _return == "take")
    else:
        $ _took_bouncer = False

    python:
        if not _took_bouncer:
            stats.increment_stats_value_money(_pending_money)
            stats.increment_stats_pcr_hatred(_pending_hatred)
        _bouncer_panel_text = show_outcome_panel(_took_bouncer, _bouncer_card, _boutcome)

    window hide
    show screen outcome_panel(_bouncer_panel_text)
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump end_day


label bouncer_strip_bar:

    python:
        _roll = __import__('random').randint(1, 100)
        _bb_cash = 2500 if stats.player_class == "bodybuilder" else 0
        _bb_tag = " [BODYBUILDER BONUS]" if _bb_cash else ""
        _strip_card = None
        ## Pending stat deltas — applied unconditionally if no card; only on PASS otherwise.
        _pending_money = 0
        _pending_hatred = 0
        _pending_coding = 0
        if _roll <= 5:
            _pending_money = 35000 + _bb_cash
            _pending_hatred = -15
            _strip_card = "vip_treatment"
            _btext = "A famous regular shows up drunk and paranoid. Two guys try to drag him outside; you intervene with textbook precision.\nYour boss slides an envelope across the table. 'Not many can do what you did tonight.'"
            _boutcome = "+{} CZK, -15 PCR HATRED{}".format(35000 + _bb_cash, _bb_tag)
        elif _roll <= 25:
            ## No card — stats apply unconditionally.
            _pending_money = 12500 + _bb_cash
            _pending_coding = 2
            _btext = "Steady crowds, few arguments, no real threats. Routine precision all night.\nYou use downtime to mentally rehearse OOP and class hierarchies — weirdly effective."
            _boutcome = "+{} CZK, +2 CODING SKILLS{}".format(12500 + _bb_cash, _bb_tag)
        elif _roll <= 75:
            _pending_money = 6500 + _bb_cash
            _pending_hatred = 5
            ## BB-only: brawl prompt fires only for bodybuilder (class_lock filter).
            ## Non-BB players: offer_card returns False, stats apply (effectively no choice).
            _strip_card = "brawl"
            _btext = "Four hours in a corridor that smells like vodka Red Bull and bad decisions. Nothing happens.\nOne person cries in the bathroom; you pretend not to notice. At least the envelope is solid."
            _boutcome = "+{} CZK, +5 PCR HATRED{}".format(6500 + _bb_cash, _bb_tag)
        elif _roll <= 95:
            ## No card — stats apply unconditionally.
            _pending_money = 1000 + _bb_cash
            _pending_hatred = 25
            _btext = "A fight breaks out. You break it up — one participant recognizes you. 'Ty vole, to je POLDA!'\nYour boss only gives you a partial payout."
            _boutcome = "+{} CZK, +25 PCR HATRED{}".format(1000 + _bb_cash, _bb_tag)
        else:
            ## Worst-case strip bar outcome — pure beat-up, no debt. The old
            ## version subtracted 12.5K CZK AND offered loan_sharks card AND
            ## stripped 5 coding. One bad RNG roll could torpedo a run. Now
            ## you just take the hatred hit; the bouncer profession is the
            ## risk, not getting put in actual debt.
            _pending_money = _bb_cash
            _pending_hatred = 30
            _btext = "You turn your back for one second — enough for a coked-up idiot to drive a vodka bottle into your skull.\nThe boss doesn't pay you for the night, but he doesn't fire you either. The headache lasts three days."
            if _bb_cash:
                _boutcome = "+{} CZK [BB BONUS], +30 PCR HATRED".format(_bb_cash)
            else:
                _boutcome = "No pay tonight, +30 PCR HATRED"

    "[_btext]"

    $ _strip_card_data = can_offer_card(_strip_card) if _strip_card else None

    if _strip_card_data is not None:
        window hide
        call screen card_offer_screen(card=_strip_card_data, source_label="STRIP-BAR", pass_stats_text=_boutcome)
        $ _took_strip = commit_card(_strip_card, _return == "take")
    else:
        $ _took_strip = False

    python:
        if not _took_strip:
            if _pending_money:
                stats.increment_stats_value_money(_pending_money)
            if _pending_hatred:
                stats.increment_stats_pcr_hatred(_pending_hatred)
            if _pending_coding:
                stats.increment_stats_coding_skill(_pending_coding)
        _strip_panel_text = show_outcome_panel(_took_strip, _strip_card, _boutcome)

    window hide
    show screen outcome_panel(_strip_panel_text)
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump end_day


## ---------------------------------------------------------------------------
## ACTIVITY: CODING
## ---------------------------------------------------------------------------

label activity_coding:

    scene bg_jb_flat

    python:
        _tier_name, _tier_info = get_coding_tier_info(stats.coding_skill)
        _is_bh = (stats.player_class == "biohacker")
        _is_de = (stats.player_class == "dark_empath")
        _bc_done = bool(python_bootcamp)
        _bc_label = "coding_bootcamp_de" if _is_de else "coding_bootcamp"
        _bc_cost = adjusted_cost(28000) if _is_de else adjusted_cost(35000)
        _bc_cost_text = "{:,} CZK".format(_bc_cost)
        _bc_flavor = "You stop being a guy with a hobby."
        if _is_de:
            _bc_flavor = "You stop being a guy with a hobby. Discount: read the room."
        _bh_accent = class_accent_color("biohacker")
        _coding_options = [
            {
                "label_name":     "coding_work_for_money",
                "title":          "CODE FOR MONEY",
                "accent":         _bh_accent,
                "cost_text":      "FREE",
                "effect_text":    "+ CZK (scales with tier)",
                "flavor_text":    "Take what your skill's worth right now.",
                "class_relevant": _is_bh,
            },
            {
                "label_name":     "coding_fiverr",
                "title":          "BUY A CODING COACH",
                "accent":         _bh_accent,
                "cost_text":      "{:,} CZK".format(adjusted_cost(2500)),
                "effect_text":    "+ Coding",
                "flavor_text":    "Pay someone better to short-cut you up the curve.",
                "class_relevant": _is_bh,
            },
        ]
        ## BH gets a Nootropics Lab tile in this slot (their commitment curve);
        ## every other class gets a Bootcamp tile. The Bootcamp locks (instead
        ## of hiding) once enrolled so players can see the buff is permanent.
        if _is_bh:
            _coding_options.append({
                "label_name":     "activity_nootropics",
                "title":          "NOOTROPICS LAB",
                "accent":         _bh_accent,
                "cost_text":      "VARIES",
                "effect_text":    "+ Coding, +/- Hatred",
                "flavor_text":    "Exact compound. Exact dose. Exact timing.",
                "class_relevant": True,
            })
        else:
            _coding_options.append({
                "label_name":     _bc_label,
                "title":          "JOIN BOOTCAMP",
                "accent":         _bh_accent,
                "cost_text":      _bc_cost_text,
                "effect_text":    "+25 Coding, +5/night",
                "flavor_text":    _bc_flavor,
                "class_relevant": False,
                "locked":         _bc_done,
                "lock_text":      "Already enrolled. The buff is live.",
            })

    call screen activity_submenu(
        title       = "CODING — PICK A PATH",
        subtitle    = "The hour is yours. The keyboard does what you tell it to.",
        options     = _coding_options,
        back_label  = "select_activity",
    )


label coding_work_for_money:

    python:
        _tier_name, _tier_info = get_coding_tier_info(stats.coding_skill)
        if _tier_name == "TIER 1":
            renpy.say(None, "[[TIER 1] Still learning.\nYou can't code for money yet. Keep practicing and building tiny projects.\nUnlock paid work at 50 Coding Skill.")
            renpy.jump("activity_coding")
        else:
            _standard = _tier_info["standard"]
            _hourly   = _tier_info["hourly"]
            _earned   = _standard + (stats.coding_skill * _hourly)
            stats.increment_stats_value_money(_earned)
            activity_selected = True

    "You bill out a day's work. [_tier_name] — [_tier_info['label']]."
    window hide
    show screen outcome_panel("+ {} CZK".format(_earned))
    pause
    hide screen outcome_panel
    jump end_day


label coding_fiverr:

    python:
        _fiverr_cost = adjusted_cost(2500)
        if not stats.try_spend_money(_fiverr_cost):
            renpy.say(None, "[[INSUFFICIENT FUNDS] You need {:,} CZK. Current: {:,} CZK.".format(_fiverr_cost, stats.available_money))
            renpy.jump("activity_coding")

    python:
        _fiverr_gain = 25
        _fiverr_card = "refactor"
        _ftext = "Senior dev. Ten years in. Code review, patterns, mental models. Paradigm shift."
        _foutcome = "- {} CZK, +25 CODING SKILL.".format(_fiverr_cost)

    "[_ftext]"

    $ _fiverr_card_data = can_offer_card(_fiverr_card)

    if _fiverr_card_data is not None:
        window hide
        call screen card_offer_screen(card=_fiverr_card_data, source_label="CODING COACH", pass_stats_text=_foutcome)
        $ _took_fiverr = commit_card(_fiverr_card, _return == "take")
    else:
        $ _took_fiverr = False

    python:
        if not _took_fiverr:
            stats.increment_stats_coding_skill(_fiverr_gain)
        _fiverr_panel_text = show_outcome_panel(_took_fiverr, _fiverr_card, _foutcome)

    window hide
    show screen outcome_panel(_fiverr_panel_text)
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump end_day


label coding_bootcamp:

    python:
        _bc_cost = adjusted_cost(35000)
        _bc_cost_str = "{:,}".format(_bc_cost)

    "The bootcamp costs [_bc_cost_str] CZK. This is a massive investment.\nAre you sure you want to sign the contract?"

    menu:
        "Yes.":
            python:
                if not stats.try_spend_money(_bc_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS] You need {:,} CZK. That is a lot of money. Maybe stick to free docs for now?".format(_bc_cost))
                    renpy.jump("activity_coding")
            "You sign a contract and pay for an on-line Python bootcamp.\nDeadlines, assignments, code reviews. The full package.\nThis is no longer a hobby. This is a commitment."
            "Six weeks in, the Friday capstone hits. You ship a working REST API in a single sitting. The instructor pings you privately: 'You're ready to push to production.'"

            $ python_bootcamp = True

            python:
                ## Bootcamp pays out everything in one go now: +25 coding, the
                ## permanent +5/night buff, and the Production Push card. The
                ## old "take card OR take stats" trade was removed — players
                ## found the extra screen friction-heavy for an already-pricey
                ## activity.
                stats.increment_stats_coding_skill(25)
                grant_card("production_push", silent=True)
                _bc_outcome = "- {:,} CZK   +25 CODING   +5 Coding/night   [+ Production Push]".format(_bc_cost)

            window hide
            show screen outcome_panel(_bc_outcome)
            pause
            hide screen outcome_panel
            python:
                activity_selected = True
            jump end_day

        "No.":
            "You step back. It's too much money right now."
            jump activity_coding


label coding_bootcamp_de:

    python:
        _bc_cost = adjusted_cost(28000)
        _bc_cost_str = "{:,}".format(_bc_cost)

    "The bootcamp costs [_bc_cost_str] CZK. Your emotional intelligence tells you this course is worth more than it costs."
    "You've already mapped the instructor's communication style. You will extract maximum value."

    menu:
        "Yes.":
            python:
                if not stats.try_spend_money(_bc_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS] You need {:,} CZK. Current: {:,} CZK.".format(_bc_cost, stats.available_money))
                    renpy.jump("activity_coding")
            "You sign the contract."
            "While others grind through the curriculum mechanically, you read your cohort."
            "You know which questions to ask. You know when to stay late and when the instructor is in a generous mood."
            "The bootcamp that costs others 35k costs you 28k. You extracted a 20%% discount through competence."
            "Six weeks in, the Friday capstone hits. You ship a clean REST API while the rest of the cohort is still wrestling with imports. The instructor doesn't say it, but you already read it on her face: 'You're ready to push to production.'"

            $ python_bootcamp = True

            python:
                ## Same consolidated reward as the universal bootcamp — see
                ## coding_bootcamp comment. DE discount on price only.
                stats.increment_stats_coding_skill(25)
                grant_card("production_push", silent=True)
                _bc_outcome = "- {:,} CZK [DE DISCOUNT]   +25 CODING   +5 Coding/night   [+ Production Push]".format(_bc_cost)

            window hide
            show screen outcome_panel(_bc_outcome)
            pause
            hide screen outcome_panel
            python:
                activity_selected = True
            jump end_day

        "No.":
            "You step back."
            jump activity_coding


## ---------------------------------------------------------------------------
## ACTIVITY: NIGHT SHIFT PATROL
## ---------------------------------------------------------------------------

label activity_night_shift:

    scene bg_police_interior

    "You volunteer for the extra night shift."
    "5,000 CZK for 8 more hours in uniform."
    "You don't need the money. But you do need the distraction."

    menu:
        "Take the shift. (+5,000 CZK) (+ [[CARD] BACKUP)":
            python:
                stats.increment_stats_value_money(5000)
                stats.increment_stats_pcr_hatred(15)

                ## Random chance for a coding opportunity or incident during night shift
                _ns_roll = __import__('random').randint(1, 100)

            python:
                ## Backup card always offered (you're always with a partner on patrol)
                _ns_extra_card = None
                if _ns_roll <= 20:
                    stats.increment_stats_coding_skill(8)
                    stats.increment_stats_pcr_hatred(-5)
                    _ns_extra_card = "procedural_defense"
                    _ns_bonus = "\n[NIGHT BONUS]: Dead quiet shift. You studied Python for 4 hours. +8 Coding, -5 Hatred."
                elif _ns_roll <= 40:
                    stats.increment_stats_value_money(1500)
                    _ns_bonus = "\n[NIGHT BONUS]: Helped with an accident. Extra callout pay. +1,500 CZK."
                elif _ns_roll <= 60:
                    stats.increment_stats_pcr_hatred(10)
                    _ns_extra_card = "chain_of_command"
                    _ns_bonus = "\n[NIGHT PENALTY]: Paperwork from an arrest took until 6AM. +10 PCR HATRED."
                else:
                    _ns_bonus = ""

            "You work through the night."
            "The city is different after midnight — quieter, stranger, more honest."
            "You check your watch every hour."
            "[_ns_bonus]"
            window hide
            show screen outcome_panel("+5,000 CZK, +15 PCR HATRED.{}".format(_ns_bonus))
            pause
            hide screen outcome_panel

            python:
                offer_card("backup", "NIGHT SHIFT")
                if _ns_extra_card:
                    offer_card(_ns_extra_card, "NIGHT SHIFT BONUS")
                activity_selected = True
            jump end_day

        "Return to menu.":
            jump daily_menu


## ---------------------------------------------------------------------------
## ACTIVITY: VISIT FIXER (day 10+ only — tile gate in activity_select_screen)
##
## Vision §1 pillar 3: money is the only shop. The Fixer is the in-fiction
## sim action for card removal. Removal-only in v1; upgrades deferred.
##
## Flow:
##   1. Compute the current flat removal price (escalates with prior shreds).
##   2. Build the removable-card list (class signatures locked).
##   3. Empty list → free reconnaissance, return to daily_menu.
##   4. fixer_removal_screen → ("remove", card_id) or ("leave", None).
##   5. Leave: free reconnaissance, return to daily_menu.
##   6. Remove: spend money, remove card, bump _fixer_removals, end day.
##
## Pricing: flat current price for ANY card. Escalates each shred. See
## fixer_current_price() / fixer_next_price() in cards/card_data.rpy.
## Curve: 5K, 8K, 11K, 14K, 17K, 20K, 20K, ...
## ---------------------------------------------------------------------------

label activity_fixer:

    ## Per-day gate — one shred per day. Entered from the sidebar button
    ## on the daily hub. Does NOT consume the daily activity slot.
    if getattr(store, '_fixer_shredded_today', False):
        "He doesn't open the door. 'Already did your one tonight. Tomorrow.'"
        jump daily_menu

    scene bg_jb_flat

    python:
        ## Class-signature cards stay locked — you only have one copy of each
        ## and they define the class fantasy. Strike/Defend ARE removable
        ## (thinning basic attacks/blocks is half the point of a card-removal
        ## shop — see Slay-the-Spire). Player starts with 4 of each, so
        ## scrubbing one or two is strategic, not run-ending.
        ## CLASS_SIGNATURE_CARDS (defined in card_data.rpy) is the canonical
        ## set — it includes both base ids AND `_plus` upgraded variants so
        ## upgrading your signature doesn't make it Fixer-eligible.

        ## One flat price per visit — every card costs the same right now.
        ## After a shred, _fixer_removals bumps and the NEXT visit costs more.
        _fixer_current = fixer_current_price()
        _fixer_next    = fixer_next_price()

        ## Build entries — one row per card instance (duplicates render
        ## separately so the player picks WHICH copy disappears).
        _fixer_entries = []
        if player_deck is not None:
            for _cid in player_deck.cards:
                if _cid in CLASS_SIGNATURE_CARDS:
                    continue
                _fixer_entries.append(_cid)

    if not _fixer_entries:
        "The flat smells like old smoke. The fixer doesn't look up from his crossword."
        "'You don't have anything I can scrub yet. Come back when you do.'"
        jump daily_menu

    "A flat on the third floor of a panelák. The doorbell doesn't work; he knew you'd be here."
    "'Pick what disappears. I take cash. I don't take notes.'"

    call screen fixer_removal_screen(entries=_fixer_entries, price=_fixer_current, next_price=_fixer_next)

    python:
        _fixer_action, _fixer_card = _return if isinstance(_return, tuple) else ("leave", None)

    if _fixer_action == "leave":
        ## Free reconnaissance — no shred, no flag. Player just browsed.
        jump daily_menu

    python:
        if not stats.try_spend_money(_fixer_current):
            renpy.say(None, "[[INSUFFICIENT FUNDS] He counts the notes again. 'Come back when you can pay.'")
            renpy.jump("daily_menu")
        player_deck.remove(_fixer_card)
        store._fixer_removals = getattr(store, '_fixer_removals', 0) + 1
        store._fixer_shredded_today = True
        _fixer_name = CARD_LIBRARY.get(_fixer_card, {}).get("name", _fixer_card)
        _fixer_outcome = "- {:,} CZK   - 1 card ({})   ·   Next shred: {:,} CZK".format(
            _fixer_current, _fixer_name, fixer_current_price()
        )

    "He feeds the card into a shredder that's older than you. The teeth are loud."
    "'Done. That's not in your deck anymore. Next one's pricier.'"

    window hide
    show screen outcome_panel(_fixer_outcome)
    pause
    hide screen outcome_panel

    ## Fixer doesn't consume the day. Return to the hub so the player can
    ## still pick an activity (gym, bouncer, coding, night shift).
    jump daily_menu


## ---------------------------------------------------------------------------
## END DAY
## ---------------------------------------------------------------------------

label end_day:
    python:
        if activity_selected:
            renpy.jump("do_end_day")

    ## Activity not selected — ask for confirmation
    "You haven't chosen your daily activity yet. Are you sure you want to end the day?"

    menu:
        "Yes, end the day anyway.":
            jump do_end_day
        "No, let me pick an activity first.":
            jump daily_menu


label do_end_day:

    ## Night cycle — music keeps playing across the day transition for
    ## continuity. play_daily_music in the next daily_menu sees a pool track
    ## already on the channel and no-ops, so the same loop continues.
    "END OF DAY [day_cycle.current_day]"

    python:
        # Base nightly hatred scales with difficulty (Easy 4, Hard 5, Insane 6, Ultra 7-8)
        _nightly_base = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
        stats.increment_stats_pcr_hatred(_nightly_base)
        if python_bootcamp:
            stats.increment_stats_coding_skill(5) # bootcamp buff

        # Persistent-HP nightly regen — +5 HP every night, capped at max.
        # Keeps the run from death-spiraling: ladder fights chip the body,
        # sleep claws a sliver back. Healing-card plays and gym sessions
        # are the bigger valves.
        _run_hp = getattr(store, 'run_hp', None)
        _run_hp_max = getattr(store, 'run_hp_max', None)
        if _run_hp is not None and _run_hp_max is not None and _run_hp < _run_hp_max:
            store.run_hp = min(_run_hp_max, _run_hp + 10)

        # Advance day
        day_cycle.next_day()
        activity_selected = False
        # Per-day Fixer gate — new day, one new shred available.
        store._fixer_shredded_today = False
        # Reset gym streak if player didn't go to gym today
        if not getattr(store, 'gym_day', False):
            store.gym_streak = 0
        store.gym_day = False

    python:
        # Check loss conditions after passives
        if stats.pcr_hatred >= 100:
            renpy.jump("hatred_collapse_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")

    jump day_start


## ---------------------------------------------------------------------------
## SALARY DAY (Day 14)
## ---------------------------------------------------------------------------

label salary_day:

    ## Autosave: start of Day 14 (salary day)
    $ renpy.save("auto-day14-salary", "Day 14 — Salary Day")

    scene bg_police_interior

    python:
        _sal = int(round(salary_amount(stats.pcr_hatred) * diff_setting("salary_mult", 1.0)))
        stats.increment_stats_value_money(_sal)
        if stats.pcr_hatred <= 25:
            _sal_text = "You have received extra money for (pretending) to be an example model police officer, good job!"
        elif stats.pcr_hatred <= 50:
            _sal_text = "Your bank just sent you a notification — it's salary day.\nSince your recent work attitude diminished, so did your salary this month."
        else:
            _sal_text = "Your bank just sent you a notification — it's salary day.\nIt has become obvious to everyone that you hate this job. The higher-ups decided to 'motivate' you with a monetary punishment."

    "SALARY DAY — [_sal_text]"
    window hide
    show screen outcome_panel("+ {} CZK".format(_sal))
    pause
    hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## ACTIVITY: NOOTROPICS LAB (Biohacker only)
## ---------------------------------------------------------------------------

label activity_nootropics:

    scene bg_bh_supplier

    python:
        _dep_warning = ""
        if nootropic_dependency:
            _dep_warning = "\n\n[DEPENDENCY ACTIVE] — Skipping a dose costs -20 Coding, +20 Hatred."

        _NOOT_TITLES = {
            1: "TIER 1 — DAILY",
            2: "TIER 2 — STACK",
            3: "TIER 3 — RACETAMS",
            4: "TIER 4 — PEPTIDES",
            5: "TIER 5 — RESEARCH",
        }
        _NOOT_FLAVORS = {
            1: "Omega-3, creatine, magnesium. The foundation.",
            2: "L-theanine + caffeine. Alpha-GPC. Bacopa.",
            3: "Aniracetam. Oxiracetam. Phenylpiracetam.",
            4: "Noopept. Semax. Selank. Gray-market shelf.",
            5: "FLModafinil. Wakefulness agent. Dose discipline.",
        }
        _NOOT_VIS = {
            1: True,
            2: nootropic_tier_max >= 2,
            3: nootropic_tier_max >= 3,
            4: nootropic_tier_max >= 4,
            5: flmodafinil_unlocked or nootropic_tier_max >= 5,
        }
        _noot_options = []
        for _tn in range(1, 6):
            _ti = NOOTROPIC_TIERS[_tn]
            _hatred_sign = "+" if _ti["hatred"] >= 0 else ""
            _eff = "+{} Coding, {}{} Hatred".format(_ti["coding"], _hatred_sign, _ti["hatred"])
            _noot_options.append({
                "label_name":     "_apply_noot_t{}".format(_tn),
                "title":          _NOOT_TITLES[_tn],
                "accent":         class_accent_color("biohacker"),
                "cost_text":      "{:,} CZK".format(adjusted_cost(_ti["cost"])),
                "effect_text":    _eff,
                "flavor_text":    _NOOT_FLAVORS[_tn],
                "class_relevant": True,
                "visible":        _NOOT_VIS[_tn],
            })

    "You open the cabinet. The protocol is specific. Every compound has a purpose.[_dep_warning]"

    call screen activity_submenu(
        title       = "NOOTROPICS — PICK A TIER",
        subtitle    = "Exact compound. Exact dose. Exact timing.",
        options     = _noot_options,
        back_label  = "activity_coding",
    )


label _apply_noot_t1:
    $ _tier = 1
    jump _apply_nootropic_tier

label _apply_noot_t2:
    $ _tier = 2
    jump _apply_nootropic_tier

label _apply_noot_t3:
    $ _tier = 3
    jump _apply_nootropic_tier

label _apply_noot_t4:
    $ _tier = 4
    jump _apply_nootropic_tier

label _apply_noot_t5:
    $ _tier = 5
    jump _apply_nootropic_tier


label _apply_nootropic_tier:

    ## --- Process selected tier ---
    python:
        _t     = NOOTROPIC_TIERS[_tier]
        _cost  = _t["cost"]

        # Dependency reduces T5 effectiveness
        _coding_gain = _t["coding"]
        if nootropic_dependency and _tier == 5:
            _coding_gain = int(_coding_gain * 0.65)  # diminishing returns

        _cost = adjusted_cost(_cost)
        if not stats.try_spend_money(_cost):
            renpy.say(None, "[[INSUFFICIENT FUNDS] You need {:,} CZK. Current: {:,} CZK.".format(
                _cost, stats.available_money))
            renpy.jump("activity_nootropics")

        # Apply effects
        stats.increment_stats_coding_skill(_coding_gain)
        stats.increment_stats_pcr_hatred(_t["hatred"])

        # Track usage
        nootropic_uses[_tier - 1] += 1
        nootropic_last_tier = _tier
        ## BH PROTOCOL — current active stack maps to a name shown in HUD/log
        _PROTOCOL_NAMES = {1: "Daily", 2: "Cognitive", 3: "Racetam", 4: "Peptide", 5: "Research"}
        store.bh_protocol = _PROTOCOL_NAMES.get(_tier, None)

        # Check for new tier unlocks
        _unlock = check_nootropic_unlocks()

        ## Card grants — T3+ offers Racetam, T5 offers FLModafinil
        _noot_card = None
        if _tier >= 5:
            _noot_card = "flmodafinil"
        elif _tier >= 3:
            _noot_card = "racetam"

        _outcome_str = "- {:,} CZK  |  +{} Coding  |  {} Hatred".format(
            _cost, _coding_gain,
            "{}".format(_t["hatred"]) if _t["hatred"] < 0 else "+{}".format(_t["hatred"]))
        if nootropic_dependency and _tier == 5:
            _outcome_str += "  [TOLERANCE — reduced effect]"

    "[_t['flavor']]"
    window hide
    show screen outcome_panel(_outcome_str)
    pause
    hide screen outcome_panel

    ## Crash/next-day preview
    python:
        _has_crash = _t["crash_coding"] != 0 or _t["crash_hatred"] != 0
        _crash_str = ""
        if _has_crash:
            parts = []
            if _t["crash_coding"] != 0:
                parts.append("{} Coding tomorrow".format(_t["crash_coding"]))
            if _t["crash_hatred"] != 0:
                parts.append("+{} Hatred tomorrow".format(_t["crash_hatred"]))
            _crash_str = "  |  ".join(parts)

    if _has_crash:
        "[[NEXT-DAY EFFECT] [_crash_str]"

    ## Tier unlock announcement
    if _unlock == "T2_UNLOCKED":
        "\nYou've been reading late at night. The forums mention something stronger than supplements.\n[[NEW TIER UNLOCKED: Cognitive Stack]"

    if _unlock == "T3_UNLOCKED":
        "\nYou've gone deeper. The r/nootropics rabbit hole has no bottom.\n[[NEW TIER UNLOCKED: Racetams]"

    if _unlock == "T4_UNLOCKED":
        "\nThere's a gray market if you know where to look. You do.\n[[NEW TIER UNLOCKED: Peptides]"

    if _unlock == "T5_UNLOCKED":
        "\nYou've been deep enough in the forums to find the name. CRL-40,940. Eugeroic. Wakefulness agent.\nThe supplier is three steps removed from anything legal.\n[[NEW TIER UNLOCKED: FLModafinil (CRL-40,940)]"

    ## Dependency warning at 2 T5 uses (one before threshold)
    python:
        _dep_warn = nootropic_uses[4] == 1 and _tier == 5

    if _dep_warn:
        "[[WARNING] One more dose and your baseline changes permanently.\nFLModafinil (CRL-40,940) dependency triggers at 2 total uses."

    ## Nootropics do not consume the daily activity slot — jump back to coding menu
    jump activity_coding


## ---------------------------------------------------------------------------
## ACTIVITY: COLD READ (Dark Empath only)
## ---------------------------------------------------------------------------

label activity_cold_read:

    scene bg_police_interior

    python:
        _target = COLD_READ_TARGETS[cold_read_index % len(COLD_READ_TARGETS)]
        cold_read_index += 1
        _high_hatred = stats.pcr_hatred > 60
        _cr_text = _target["text_high"] if _high_hatred else _target["text_low"]
        ## DE PROFILES tracker — each cold read deepens a specific NPC profile.
        _PROFILE_KEYS = {"The Overwhelmed Rookie": "rookie", "The Cynical Veteran": "veteran",
                          "The Quietly Corrupt Lieutenant": "lieutenant", "The Civilian Clerk": "clerk"}
        _profile_key = _PROFILE_KEYS.get(_target.get("name"), "unknown")
        if _profile_key != "unknown":
            store.de_profiles[_profile_key] = store.de_profiles.get(_profile_key, 0) + 1
        ## Profile Master — all four NPCs at 3+ reads each
        if all(store.de_profiles.get(k, 0) >= 3 for k in ("rookie", "veteran", "lieutenant", "clerk")):
            unlock_achievement("profile_master")

        ## Pending reward — applied only on PASS. Profile-deepening above is progression
        ## (you observed the target — TAKE or PASS) and stays unconditional.
        _cr_pending_hatred = -20
        _cr_pending_coding = 0
        _cr_card = "vigil"
        if _high_hatred:
            _cr_pending_coding = 5
            _cr_card = "mirror"

        ## DE progression milestone: 5th cold read offers Empath's Insight (rare).
        ## Milestone grant is a separate forced offer (no stat trade) — represents
        ## the cumulative achievement, not the per-session reward.
        _cr_milestone = (cold_read_index >= 5 and "empaths_insight" not in player_deck.cards)

        _cr_outcome = "-20 Police Hatred"
        if _cr_pending_coding:
            _cr_outcome += ", +5 Coding Skill  [HIGH HATRED — CONTEMPT MODE]"

    "SUBJECT: [_target['name']]"

    python:
        _de_accent = class_accent_color("dark_empath")
        _cr_options = [
            {
                "label_name":     "cold_read_regular",
                "title":          "REGULAR READ",
                "accent":         _de_accent,
                "cost_text":      "FREE",
                "effect_text":    "-20 Hatred",
                "flavor_text":    "Subtle. The card may stick.",
                "class_relevant": True,
            },
            {
                "label_name":     "cold_read_observe",
                "title":          "OBSERVATION HOUR",
                "accent":         _de_accent,
                "cost_text":      "FREE",
                "effect_text":    "-20 Hatred, +1 PROFILE",
                "flavor_text":    "Sit with them. Read past the surface.",
                "class_relevant": True,
            },
        ]
        _cr_subtitle = "SUBJECT: {}".format(_target.get("name", "?"))

    call screen activity_submenu(
        title       = "COLD READ — PICK YOUR ANGLE",
        subtitle    = _cr_subtitle,
        options     = _cr_options,
        back_label  = "select_activity",
    )


label cold_read_regular:

    "[_cr_text]"

    $ _cr_card_data = can_offer_card(_cr_card)

    if _cr_card_data is not None:
        window hide
        call screen card_offer_screen(card=_cr_card_data, source_label="COLD READ", pass_stats_text=_cr_outcome)
        $ _took_cr = commit_card(_cr_card, _return == "take")
    else:
        $ _took_cr = False

    python:
        if not _took_cr:
            stats.increment_stats_pcr_hatred(_cr_pending_hatred)
            if _cr_pending_coding:
                stats.increment_stats_coding_skill(_cr_pending_coding)
        _cr_panel_text = show_outcome_panel(_took_cr, _cr_card, _cr_outcome)

    window hide
    show screen outcome_panel(_cr_panel_text)
    pause
    hide screen outcome_panel

    python:
        if _cr_milestone:
            offer_card("empaths_insight", "MILESTONE — 5 COLD READS")
        activity_selected = True

    jump end_day


## ---------------------------------------------------------------------------
## OBSERVATION HOUR — DE relief variant. Deeper hatred drop, deeper profile,
## no card offer. Sub-menu of activity_cold_read; the target/profile setup
## from the parent label is already applied (one unconditional read), so
## OBSERVATION HOUR adds a SECOND read on the same target this session.
## ---------------------------------------------------------------------------

label cold_read_observe:

    "[_cr_text]"
    "You don't break the gaze. You don't ask the question that ends the moment."
    "An hour later you walk out of the cafe with a fuller theory. Half their tells, you'd never noticed before. The other half, you'd noticed but never named."

    python:
        ## Deepen the same target an extra step (the parent label's setup already
        ## counted +1; this brings the session total to +2 on this NPC).
        if _profile_key != "unknown":
            store.de_profiles[_profile_key] = store.de_profiles.get(_profile_key, 0) + 1
        ## Re-check Profile Master in case this read tipped the threshold.
        if all(store.de_profiles.get(k, 0) >= 3 for k in ("rookie", "veteran", "lieutenant", "clerk")):
            unlock_achievement("profile_master")
        ## Same hatred relief as the regular path (-20). The trade is profile depth
        ## instead of a card lottery — DE's class-progression contribution.
        stats.increment_stats_pcr_hatred(-20)
        _observe_outcome = "-20 PCR HATRED, +1 PROFILE [{}] (deep)".format(_target.get("name", "?"))

    window hide
    show screen outcome_panel(_observe_outcome)
    pause
    hide screen outcome_panel

    python:
        if _cr_milestone:
            offer_card("empaths_insight", "MILESTONE — 5 COLD READS")
        activity_selected = True

    jump end_day


## ---------------------------------------------------------------------------
## CRISIS EVENTS — fire once per run at >= 85 Hatred
## ---------------------------------------------------------------------------

label crisis_event_bodybuilder:

    play music "audio/tension_theme.mp3" fadein 1.0
    scene bg_police_interior
    show jb angry at char_left

    "[[CRISIS EVENT — BODYBUILDER]"
    "It happened at the gym."
    "A man in a Levi's jacket made a joke about cops. Something about donuts."
    "You don't remember deciding to react. You just did."
    "You grabbed a 20kg plate off the rack and slammed it into the floor next to him."
    "The crack echoed through the whole building. Everyone froze."
    "He's still standing there, pale as concrete, phone already out."
    "The gym manager has appeared. The word 'police report' has been used."
    "Your hands are still shaking."

    menu:
        "Own it. (-2,000 CZK, -20 Hatred)":
            python:
                stats.increment_stats_pcr_hatred(-20)
                stats.increment_stats_value_money(-2000)
            "You uncurl your fists."
            jb "'I'm sorry. I'll pay for the damage. You didn't deserve that.'"
            "The manager nods slowly. The man with the phone doesn't look convinced, but he pockets it."
            "You drive home. The rage is gone."
            "What's left underneath it is quieter. And more honest."
            "Your body was trying to tell you something. It's been trying for weeks."
            window hide
            show screen outcome_panel("-2,000 CZK, -20 PCR HATRED [BODYBUILDER CRISIS: you faced it].")
            pause
            hide screen outcome_panel

        "Storm out. (+5 Hatred)":
            python:
                stats.increment_stats_pcr_hatred(5)
            "You walk to the exit."
            "Nobody stops you."
            "In the car park you sit in your car for 25 minutes with the engine off."
            "The anger has burned itself hollow."
            "Nothing is resolved. But nothing escalated either."
            "You exist in a grey zone between dangerous and fine."
            window hide
            show screen outcome_panel("+5 PCR HATRED [BODYBUILDER CRISIS: unresolved].")
            pause
            hide screen outcome_panel

    return


label crisis_event_dark_empath:

    play music "audio/tension_theme.mp3" fadein 1.0
    scene bg_police_interior
    show jb defeated at char_left

    "[[CRISIS EVENT — DARK EMPATH]"
    "You woke up this morning and something was different."
    "Not wrong. Just... absent."
    "Your colleague said good morning and you opened your mouth."
    "Nothing came out. Not because you didn't know the words."
    "Because you couldn't locate the function that generates them."
    "You stood there for three seconds — which is an eternity in a corridor — before your mouth produced: 'Morning.'"
    "He walked on, none the wiser."
    "You are sitting at your desk now, reading the same line of a report for the seventh time."
    "The emotional switch didn't flip to anger or grief."
    "It flipped to null."

    menu:
        "Sit with it. (-15 Hatred)":
            python:
                stats.increment_stats_pcr_hatred(-15)
                stats.increment_stats_coding_skill(3)
            "You close the report."
            "You put your hands flat on the desk and breathe."
            "Slowly you realize: this isn't breakdown. This is your system refusing to process any more input."
            "You've been running on other people's emotional states for weeks. Reading them. Carrying them."
            "The void is the result of perfect drainage."
            "You are not broken. You are empty. There is a difference."
            "You spend 20 minutes doing nothing. Deliberately."
            "When you return to the report, you read it in 4 minutes. Everything is sharper."
            window hide
            show screen outcome_panel("-15 PCR HATRED, +3 CODING [DARK EMPATH CRISIS: emptiness as clarity].")
            pause
            hide screen outcome_panel

        "Dissociate. (+3 Hatred)":
            python:
                stats.increment_stats_pcr_hatred(3)
            "You do exactly what you're supposed to do."
            "You process reports. You respond to calls. You nod at the right moments."
            "Nobody notices. You are performing normalcy from muscle memory."
            "The void persists underneath, but it's insulated now."
            "This is fine. This is sustainable. You've been here before."
            "You haven't."
            window hide
            show screen outcome_panel("+3 PCR HATRED [DARK EMPATH CRISIS: functional but unresolved].")
            pause
            hide screen outcome_panel

    return


label crisis_event_biohacker:

    play music "audio/tension_theme.mp3" fadein 1.0
    scene bg_police_interior
    show jb worried at char_left

    "[[CRISIS EVENT — BIOHACKER]"
    "Your resting heart rate is 140 BPM."
    "You know this because you checked. Twice."
    "Your hands have a micro-tremor. Your focus, which is usually a narrow laser, is scattering."
    "You've been running too hot for too long."
    "The stack, the stress, the late-night study sessions, the shift schedules."
    "Your body has quietly filed a formal complaint."
    "You are sitting in the break room pretending to drink coffee."
    "Your biosignals are telling you to stop."

    menu:
        "Cold protocol. (-25 Hatred, -5 Coding today)":
            python:
                stats.increment_stats_pcr_hatred(-25)
                stats.increment_stats_coding_skill(-5)
            "You pour the coffee out."
            "You drink a litre of cold water. You eat real food — not protein bars."
            "You go home early and sleep for 10 hours."
            "No stack. No screen. No optimization."
            "You wake up at 6 AM and your hands are steady."
            "Your baseline is restored. The system can be pushed again."
            "But now you know where the red line is."
            window hide
            show screen outcome_panel("-25 PCR HATRED, -5 CODING (rest tax) [BIOHACKER CRISIS: hard reset successful].")
            pause
            hide screen outcome_panel

        "Log and continue.":
            python:
                _bh_crisis_roll = __import__('random').randint(1, 100)
                if _bh_crisis_roll <= 50:
                    stats.increment_stats_pcr_hatred(-20)
                    stats.increment_stats_coding_skill(6)
                    _bh_outcome = "-20 PCR HATRED, +6 CODING [BIOHACKER CRISIS: logged and stabilized]."
                    _bh_text = "You open a spreadsheet. HRV. Cortisol proxy. Sleep debt.\nYou adjust the protocol. Reduce T dose, increase magnesium, shift the timing 2 hours.\nWithin 90 minutes your hands are steady.\nYou turned a crisis into a calibration point.\nThat is exactly the kind of person you are becoming."
                else:
                    stats.increment_stats_pcr_hatred(12)
                    stats.increment_stats_coding_skill(-3)
                    _bh_outcome = "+12 PCR HATRED, -3 CODING [BIOHACKER CRISIS: cost without correction]."
                    _bh_text = "You log everything and keep pushing.\nAt 4 PM your vision goes grey at the edges.\nYou sit on the bathroom floor for 15 minutes.\nA colleague knocks on the door: 'JB, you okay in there?'\nThe data didn't save you this time. But it's still data."
            "[_bh_text]"
            window hide
            show screen outcome_panel(_bh_outcome)
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## RANDOM EVENT GATE
## ---------------------------------------------------------------------------

label random_event_check:

    ## Narrative-event pool — events removed once triggered (drains per run).
    ## Trimmed from 20 to 7 keepers (the "deck IS your 30 days" pivot — fewer
    ## but stronger narrative beats; remaining slots roll battle ladder rungs).
    ## Cut event bodies stay defined in events/random_events.rpy; they're just
    ## unreferenced now.
    python:
        if not hasattr(store, 'random_event_pool'):
            store.random_event_pool = [
                "re_overtime_offer",
                "re_corpse_in_care_home",
                "re_paperwork_overload",
                "re_dispatch_blue_screen",
                "re_tech_bro_speeding",
                "re_suicide_call",
                "re_coding_interview",
            ]
        _ladder_init_pool()

    ## Class arc takes priority over both battle and event pool — fires
    ## the next stage if the day window + class match. Returns None
    ## otherwise (DE/BH only currently; BB has no arc post-f72e84b).
    ## Top-level `call expression ... from _xxx` for save stability.
    python:
        _class_arc = class_arc_check()
    if _class_arc:
        call expression _class_arc from _call_class_arc_random_event_check
        python:
            if stats.pcr_hatred >= 75:
                renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
            else:
                play_daily_music(fadein=1.5)
            _re_nightly = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
            stats.increment_stats_pcr_hatred(_re_nightly)
            if python_bootcamp:
                stats.increment_stats_coding_skill(5)
            day_cycle.next_day()
        jump random_event_check_done

    ## Battle vs event roll. Returns 'battle' / 'event' / None.
    $ _slot_kind, _slot_eid, _slot_tier = roll_ladder_or_event(day_cycle.current_day)

    if _slot_kind == "battle":
        call battle_with(_slot_eid, _slot_tier)
        python:
            if stats.pcr_hatred >= 75:
                renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
            else:
                play_daily_music(fadein=1.5)
            _re_nightly = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
            stats.increment_stats_pcr_hatred(_re_nightly)
            if python_bootcamp:
                stats.increment_stats_coding_skill(5)
            day_cycle.next_day()
        jump random_event_check_done

    python:
        _chosen_event = None
        if _slot_kind == "event" and store.random_event_pool:
            _chosen_event = __import__('random').choice(store.random_event_pool)
            store.random_event_pool.remove(_chosen_event)

    if _chosen_event:
        call expression _chosen_event from _call_random_event_pool_choice
        python:
            if stats.pcr_hatred >= 75:
                renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
            else:
                play_daily_music(fadein=1.5)
            _re_nightly = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
            stats.increment_stats_pcr_hatred(_re_nightly)
            if python_bootcamp:
                stats.increment_stats_coding_skill(5)
            day_cycle.next_day()
    else:
        python:
            ## Silent slot — Easy-loss skip-tomorrow penalty, or both pools
            ## exhausted. Apply nightly cycle so the day still advances cleanly.
            _re_nightly = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
            stats.increment_stats_pcr_hatred(_re_nightly)
            if python_bootcamp:
                stats.increment_stats_coding_skill(5)
            day_cycle.next_day()

label random_event_check_done:
    return
