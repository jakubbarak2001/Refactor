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

        ## Grant a representative deck of acquired cards — spans all 3 archetypes.
        for _cid in ["provoke", "knuckle_down", "see_red", "breaking_point",
                      "bracing", "iron_posture", "counterweight", "stack_trace",
                      "hotfix", "crunch_time", "gut_punch", "killing_blow"]:
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
            ("vlk",        "medium"),
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

        for _cid in ["provoke", "knuckle_down", "bracing", "gut_punch",
                      "stack_trace", "backup", "see_red"]:
            grant_card(_cid, silent=True)

        day_cycle.current_day = {"easy": 6, "medium": 12, "hard": 21}.get(_picked_tier, 6)

        _ladder_summary = "DEV LADDER: {} ({}) | day {} | deck {} cards".format(
            _picked_enemy, _picked_tier, day_cycle.current_day, len(player_deck.cards),
        )

    "[_ladder_summary]"

    call battle_with(_picked_enemy, _picked_tier) from _call_battle_with

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
    elif stats.player_class == "biohacker":
        scene bg_bh_supplier with Dissolve(0.6)

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
        scene bg_bh_supplier with Dissolve(0.6)
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
        if stats.pcr_hatred >= hatred_cap():
            renpy.jump("hatred_collapse_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")

    ## Crisis event — fires once per run when Hatred reaches 85. Top-level
    ## `call expression ... from _xxx` so the named return label survives
    ## script edits (save stability — see the comment near salary_day above).
    python:
        ## BB excluded — its crisis event was cut (Hatred is the Bodybuilder's
        ## fantasy, not a mid-run "lose your shit" liability beat).
        _should_crisis = (
            stats.pcr_hatred >= 85
            and stats.player_class != "bodybuilder"
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
        if stats.pcr_hatred >= hatred_cap():
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
## SOMA 10/10 capstone — choose 1 of 3 rare cards. Called from both gym
## activities right after add_soma. Gated so a re-call is a safe no-op.
## ---------------------------------------------------------------------------

label soma_ten_reward:
    if stats is None or stats.player_class != "bodybuilder":
        return
    if getattr(store, 'bb_soma', 0) < 10 or getattr(store, '_soma_reward_given', False):
        return
    $ store._soma_reward_given = True

    "Ten sessions. Ten. The man in the mirror is not the man who walked in on Day 1."
    "Your trainer doesn't say anything. He looks at the rack, then at you, then steps back."
    "Something the body earned. Pick what it becomes."

    window hide
    call screen card_reward_trio_screen(cards=["roid_rage", "synthol", "pre_workout"])
    python:
        if _return and _return not in ("skip", None):
            grant_card(_return, silent=False)
    return


## ---------------------------------------------------------------------------
## PROTOCOL 10/10 capstone — choose 1 of 3 rare BH cards. Fires when the
## total nootropic BUY count (sum of nootropic_uses) hits 10. Research
## sessions are the upgrade lane and don't increment the counter. Gated
## with a one-shot flag so re-call is a safe no-op.
## ---------------------------------------------------------------------------

label protocol_ten_reward:
    if stats is None or stats.player_class != "biohacker":
        return
    if sum(getattr(store, 'nootropic_uses', [0,0,0,0,0])) < 10 or getattr(store, '_protocol_reward_given', False):
        return
    $ store._protocol_reward_given = True

    "Ten compounds. Ten experiments. The body that walked in on Day 1 is not the body running this protocol."
    "Your notebook is full of dose-response curves. You know your own physiology better than any doctor."
    "Something the body learned. Pick what it becomes."

    window hide
    call screen card_reward_trio_screen(cards=["peak_state", "total_recall", "telomere_reset"])
    python:
        if _return and _return not in ("skip", None):
            grant_card(_return, silent=False)
    return


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

    "You head to the gym with your trainer.\nTraining will help you relax."
    python:
        _streak_msg = ""
        if store.gym_streak >= 1:
            _streak_msg = "\n[STREAK: {} days in a row — extra -{} Hatred bonus]".format(store.gym_streak, _streak_bonus)
    "Gym attendance: [store.gym_streak] day streak.[_streak_msg]"

    menu:
        "We go gym!":
            ## Same workout SFX as the BB hover preview on the class-select
            ## screen (audio/sfx/gym_plates.mp3) — clicking "we go gym" should
            ## sound like clanging plates.
            play sound "audio/sfx/gym_plates.mp3"
            python:
                _roll = __import__('random').randint(1, 3)

            python:
                _bb_bonus = 5 if stats.player_class == "bodybuilder" else 0
                ## Always-apply progression (you completed the session — UPGRADE or HEAL):
                store.gym_streak += 1
                ## BB-only common: spotter granted at the 3-day streak.
                if store.gym_streak == 3 and stats.player_class == "bodybuilder":
                    grant_card("hold_the_line", silent=True)
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
            call soma_ten_reward from _call_soma_ten_reward_gym

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
                _heal_parts = []
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
                call _run_card_upgrade_flow from _call__run_card_upgrade_flow
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
            grant_card("hold_the_line", silent=True)
        if store.gym_streak >= 5:
            _newly_unlocked = unlock_achievement("gym_rat")
            if _newly_unlocked and stats.player_class == "bodybuilder":
                grant_card("iron_stance", silent=True)
        ## Pre-compute heavy-session HEAL payload (heavier than regular gym:
        ## -30 hatred + +15 HP, but no Max HP bump — that's the regular gym's
        ## job). Numbers only applied if the player picks HEAL.
        _heavy_heal = 15
        _heavy_heal_text = "- {:,} CZK, -30 PCR HATRED, +1 SOMA, +{} HP".format(_heavy_cost, _heavy_heal)

    call soma_ten_reward from _call_soma_ten_reward_heavy

    label .choice_loop:
        pass

    window hide
    call screen gym_choice_screen(heal_stats_text=_heavy_heal_text)
    $ _heavy_choice = _return

    if _heavy_choice == "upgrade":
        call _run_card_upgrade_flow from _call__run_card_upgrade_flow_1
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
## Random 1-of-4 modality: Sauna, Meditation, Cold Plunge, Red Light. Each
## has its own image and stat profile. Daily mystery — same activity, can't
## pre-pick the modality. Free, eats the daily slot.
## Max HP bumps share the gym_max_hp_bonus store var so battle_init picks them
## up (BH branch already adds _gym_b to player_max_hp).
## ---------------------------------------------------------------------------

label activity_recovery:

    python:
        _rec_mod = __import__('random').choice(["sauna", "meditation", "coldplunge", "redlight"])

    if _rec_mod == "sauna":
        scene bg_bh_rec_sauna with Dissolve(0.4)
        "Eight minutes at 90°C. You finish on the cold tile, condensation everywhere, lungs still wide. Heat-shock proteins do the work."
        python:
            store.gym_max_hp_bonus = getattr(store, 'gym_max_hp_bonus', 0) + 5
            _restored = event_heal(20)
            stats.increment_stats_pcr_hatred(-10)
            _rec_out = "SAUNA  |  +{} HP  |  +5 MAX HP  |  -10 Hatred".format(_restored)

    elif _rec_mod == "meditation":
        scene bg_bh_rec_meditation with Dissolve(0.4)
        "Twenty minutes on the cushion. The Colonel-loop unhooks somewhere around minute eight. You don't notice until minute fifteen."
        python:
            _restored = event_heal(10)
            stats.increment_stats_pcr_hatred(-30)
            _rec_out = "MEDITATION  |  +{} HP  |  -30 Hatred".format(_restored)

    elif _rec_mod == "coldplunge":
        scene bg_bh_rec_coldplunge with Dissolve(0.4)
        "Two minutes at 4°C. Your nervous system does the math and reboots without asking. HRV up six points by tomorrow."
        python:
            store.gym_max_hp_bonus = getattr(store, 'gym_max_hp_bonus', 0) + 10
            _restored = event_heal(25)
            _rec_out = "COLD PLUNGE  |  +{} HP  |  +10 MAX HP".format(_restored)

    else:  # redlight
        scene bg_bh_rec_redlight with Dissolve(0.4)
        "Twenty minutes under the panel. You log the wavelength. You log the duration. Mitochondria warm up."
        python:
            store.gym_max_hp_bonus = getattr(store, 'gym_max_hp_bonus', 0) + 5
            _restored = event_heal(15)
            stats.increment_stats_pcr_hatred(-15)
            _rec_out = "RED LIGHT  |  +{} HP  |  +5 MAX HP  |  -15 Hatred".format(_restored)

    window hide
    show screen outcome_panel(_rec_out)
    pause
    hide screen outcome_panel

    python:
        activity_selected = True
    jump end_day


## ---------------------------------------------------------------------------
## ACTIVITY: BOUNCER
## ---------------------------------------------------------------------------

## ---------------------------------------------------------------------------
## BOUNCER — the flat money lane. One venue, no card-shop side hustle. Cards
## are the Coding lane's job. Payouts tuned ~65% above the legacy night-club
## EV (5k -> 8.3k) since Bouncer is now the only dedicated money activity.
## BB bonus +2,500 CZK still applies.
## ---------------------------------------------------------------------------

label activity_bouncer:

    scene bg_havana_club

    python:
        _roll = __import__('random').randint(1, 100)
        _bb_cash = 2500 if stats.player_class == "bodybuilder" else 0
        _bb_tag = " [BODYBUILDER BONUS]" if _bb_cash else ""
        if _roll <= 70:
            _pending_money = 7000 + _bb_cash
            _pending_hatred = 10
            _btext = "Uneventful. Six hours in a doorway, nodding at people happier than you.\nBy 3 AM you're calculating how many more shifts like this to quit forever. The number is getting smaller."
            _boutcome = "+ {} CZK, +10 PCR HATRED{}".format(7000 + _bb_cash, _bb_tag)
        elif _roll <= 90:
            _pending_money = 14000 + _bb_cash
            _pending_hatred = -10
            _btext = "Rare night. Regulars tip heavy, the manager notices your work, and nobody throws up on anyone.\nDriving home at 4 AM, windows down: 'If this was my real job I would hate it slightly less.' Closest thing to joy you've felt all week."
            _boutcome = "+ {} CZK, -10 PCR HATRED{}".format(14000 + _bb_cash, _bb_tag)
        else:
            _pending_money = 6000 + _bb_cash
            _pending_hatred = 20
            _btext = "Two drunks fight over a woman interested in neither. You step in — one recognizes you. 'TO JE PŘECE POLDA!'\nPhone out. The group chat hasn't stopped since. You want to die."
            _boutcome = "+ {} CZK, +20 PCR HATRED{}".format(6000 + _bb_cash, _bb_tag)

    "[_btext]"

    python:
        stats.increment_stats_value_money(_pending_money)
        stats.increment_stats_pcr_hatred(_pending_hatred)

    window hide
    show screen outcome_panel(_boutcome)
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
        _is_bh = (stats.player_class == "biohacker")
        _is_de = (stats.player_class == "dark_empath")
        _bc_done = bool(python_bootcamp)
        _bc_label = "coding_bootcamp_de" if _is_de else "coding_bootcamp"
        _bc_cost = adjusted_cost(28000) if _is_de else adjusted_cost(35000)
        _bc_cost_text = "{:,} CZK".format(_bc_cost)
        _bc_flavor = "Six weeks. Study days roll high-tier cards after."
        if _is_de:
            _bc_flavor = "Six weeks. You'll read the instructor for a discount. Study days roll high-tier cards after."
        _bh_accent = class_accent_color("biohacker")
        _coding_options = [
            {
                "label_name":     "coding_study",
                "title":          "STUDY",
                "accent":         _bh_accent,
                "cost_text":      "FREE",
                "effect_text":    "Pick from a 3-card offer",
                "flavor_text":    ("Bootcamp tier: high-rarity offers." if _bc_done else "An hour at the keyboard. The keyboard pays in cards."),
                "class_relevant": _is_bh,
            },
        ]
        ## Bootcamp option — BH skips this lane (their Coding ramps via the
        ## top-level Nootropics Lab instead). Other classes see the bootcamp
        ## purchase tile, DE-discounted.
        if not _is_bh:
            _coding_options.append({
                "label_name":     _bc_label,
                "title":          "JOIN BOOTCAMP",
                "accent":         _bh_accent,
                "cost_text":      _bc_cost_text,
                "effect_text":    "Study days roll rare cards",
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


## ---------------------------------------------------------------------------
## STUDY — the card lane. An hour of focused work; the day pays in a card.
## Tier band scales with the current day-band, OR jumps to "hard" tier once
## the player has graduated Bootcamp (the deck-defining purchase that turns
## every future Study day into a rare-biased card offer).
## ---------------------------------------------------------------------------

label coding_study:

    python:
        _study_tier = "hard" if bool(python_bootcamp) else _battle_ladder_band(day_cycle.current_day)
        _study_trio = pick_battle_rewards(_study_tier)

        ## BH FREELANCE PAYOUT — coding-tier-scaled CZK on top of the card.
        ## The "intelligent class" amplifier: studying isn't just for the
        ## card, it's also a billable hour. Tier brackets mirror
        ## get_coding_tier_info / coding_daily_income for consistency.
        ##   T1 (0-34)    →     0 CZK    (you're not hireable yet)
        ##   T2 (35-99)   → 1,500 CZK    (junior contract work)
        ##   T3 (100-149) → 4,000 CZK    (solid mid-market freelance)
        ##   T4 (150-199) → 8,000 CZK    (senior hourly rate)
        ##   T5 (200+)    →15,000 CZK    (god-tier picks the project)
        _study_bh_payout = 0
        if stats.player_class == "biohacker":
            _scs = stats.coding_skill
            if _scs >= 200:   _study_bh_payout = 15000
            elif _scs >= 150: _study_bh_payout = 8000
            elif _scs >= 100: _study_bh_payout = 4000
            elif _scs >=  35: _study_bh_payout = 1500

    if _study_bh_payout > 0:
        "An hour at the keyboard. A repo PR. An invoice. The skill ladder pays."
    else:
        "An hour at the keyboard. Documentation tabs open. You build something small that works, and it earns you something worth keeping."

    call screen card_reward_trio_screen(_study_trio)

    python:
        _study_card = _return
        if _study_bh_payout > 0:
            stats.increment_stats_value_money(_study_bh_payout)
        if _study_card and _study_card != "skip":
            grant_card(_study_card, silent=True)
            if _study_bh_payout > 0:
                _study_outcome = "+ Card.  + {:,} CZK [FREELANCE].".format(_study_bh_payout)
            else:
                _study_outcome = "+ Card."
        else:
            if _study_bh_payout > 0:
                _study_outcome = "Passed on the offer.  + {:,} CZK [FREELANCE].".format(_study_bh_payout)
            else:
                _study_outcome = "Passed on the offer."

    window hide
    show screen outcome_panel(_study_outcome)
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump end_day


label coding_bootcamp:

    python:
        _bc_cost = adjusted_cost(35000)
        if not stats.try_spend_money(_bc_cost):
            renpy.say(None, "[[INSUFFICIENT FUNDS] You need {:,} CZK. Current: {:,} CZK.".format(_bc_cost, stats.available_money))
            renpy.jump("activity_coding")

    "Six weeks of deadlines, code reviews, and one Friday capstone that ships a working REST API in a single sitting. The instructor pings you: 'You're ready to push to production.'"

    $ python_bootcamp = True

    python:
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


label coding_bootcamp_de:

    python:
        _bc_cost = adjusted_cost(28000)
        if not stats.try_spend_money(_bc_cost):
            renpy.say(None, "[[INSUFFICIENT FUNDS] You need {:,} CZK. Current: {:,} CZK.".format(_bc_cost, stats.available_money))
            renpy.jump("activity_coding")

    "You read the instructor on the call and price yourself a 20%% discount. Six weeks later you ship the capstone REST API ahead of the cohort. 'You're ready to push to production.'"

    $ python_bootcamp = True

    python:
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


## ---------------------------------------------------------------------------
## ACTIVITY: OVERTIME
##
## Volunteer for the extra shift. Flat +5,000 CZK / +15 Hatred, then
## _roll_overtime() (events/overtime_events.rpy) resolves the night: a
## pity-ramped battle-ladder fight, an overtime event, or the flat night roll.
## ---------------------------------------------------------------------------

label activity_overtime:

    scene bg_police_interior

    "You sign on for the extra shift. 5,000 CZK and eight more hours under the fluorescents."

    python:
        stats.increment_stats_value_money(5000)
        stats.increment_stats_pcr_hatred(15)
        _ot_kind, _ot_eid, _ot_tier = _roll_overtime()

    if _ot_kind == "battle":
        call battle_with(_ot_eid, _ot_tier) from _call_overtime_battle
        python:
            if stats.pcr_hatred >= 75:
                renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
            else:
                play_daily_music(fadein=1.5)
            activity_selected = True
        jump end_day

    if _ot_kind == "event":
        call expression _ot_eid from _call_overtime_event
        $ activity_selected = True
        jump end_day

    python:
        _ns_roll = __import__('random').randint(1, 100)
        if _ns_roll <= 20:
            stats.increment_stats_coding_skill(8)
            stats.increment_stats_pcr_hatred(-5)
            _ns_bonus = "\n[NIGHT BONUS]: Dead quiet shift. You studied Python for 4 hours. +8 Coding, -5 Hatred."
        elif _ns_roll <= 40:
            stats.increment_stats_value_money(1500)
            _ns_bonus = "\n[NIGHT BONUS]: Helped with an accident. Extra callout pay. +1,500 CZK."
        elif _ns_roll <= 60:
            stats.increment_stats_pcr_hatred(10)
            _ns_bonus = "\n[NIGHT PENALTY]: Paperwork from an arrest took until 6AM. +10 PCR HATRED."
        else:
            _ns_bonus = ""

    "You work through the night. The city is different after midnight — quieter, stranger, more honest."
    "[_ns_bonus]"
    window hide
    show screen outcome_panel("+5,000 CZK, +15 PCR HATRED.{}".format(_ns_bonus))
    pause
    hide screen outcome_panel

    $ activity_selected = True
    jump end_day


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
    ## still pick an activity (gym, bouncer, coding, overtime).
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

    ## Apply nightly stat changes FIRST, then compute + display the BH
    ## freelance paycheck so the preview line matches the actual payout.
    ## (Bug noted by refactor-judge: bootcamp +5 Coding crossing a tier
    ## boundary made the preview undercount the real amount.)
    python:
        # Base nightly hatred scales with difficulty (Easy 4, Hard 5, Insane 6, Ultra 7-8)
        _nightly_base = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
        stats.increment_stats_pcr_hatred(_nightly_base)
        if python_bootcamp:
            stats.increment_stats_coding_skill(5) # bootcamp buff

        ## BH freelance income — paid overnight, scaled by current (POST-
        ## bootcamp-bump) coding tier. No-op for non-BH classes.
        _coding_paycheck = coding_daily_income()
        if _coding_paycheck > 0:
            stats.increment_stats_value_money(_coding_paycheck)

    if _coding_paycheck > 0:
        "[[FREELANCE] A client paid out overnight — [_coding_paycheck:,] CZK in the account by morning."

    python:
        # Advance day
        day_cycle.next_day()
        activity_selected = False
        # Per-day Fixer gate — new day, one new shred available.
        store._fixer_shredded_today = False
        # Per-day Nootropics Lab gate — one dose OR one research session per day.
        store.nootropics_done_today = False
        # Defensive: scrub any stale module refs from older saves so the
        # next quicksave doesn't crash pickle.
        _bh_scrub_stale_module_refs()
        # Reset gym streak if player didn't go to gym today
        if not getattr(store, 'gym_day', False):
            store.gym_streak = 0
        store.gym_day = False

    python:
        # Check loss conditions after passives
        if stats.pcr_hatred >= hatred_cap():
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

    ## One nootropic action per day — applies to BOTH dose buys and Research
    ## PubMed. Reset in do_end_day. Bounce back to the coding hub if already used.
    if getattr(store, 'nootropics_done_today', False):
        "You've already run today's protocol. The body needs a beat before the next dose."
        jump activity_coding

    scene bg_bh_supplier

    python:
        _dep_warning = ""
        if nootropic_dependency:
            _dep_warning = "\n\n[DEPENDENCY ACTIVE] — Skipping a dose costs -20 Coding, +20 Hatred."

        ## 4-tile lineup: T1 LEGAL / T2 SHADY / T3 LAB / T4 BLACK MARKET.
        ## (Slots 2 and 4 in NOOTROPIC_TIERS remain as legacy data for
        ## martin_meeting / class_arcs / colonel_event references but are
        ## never surfaced.) BLACK MARKET unlocks at 100 Coding — you have
        ## to BE somebody to know somebody. Pure money-to-power; the
        ## endgame sink that lets a flush BH skip the slow Lab grind.
        _NOOT_TITLES = {
            1: "T1 — LEGAL ESHOP",
            3: "T2 — SHADY SOURCE",
            5: "T3 — LAB GRADE",
            6: "T4 — BLACK MARKET",
        }
        ## Per-tier flavor escalates with how many times THIS tier has been
        ## bought — see bh_tier_flavor() in python_logic.rpy. Voice goes from
        ## "next-day delivery" → "Tom is reliable" → "labels are a formality".
        ## Tier 6 (black market) has its own static flavor since it's a
        ## premium one-off, not a habit.
        _NOOT_FLAVORS = {
            1: bh_tier_flavor(1),
            3: bh_tier_flavor(3),
            5: bh_tier_flavor(5),
            6: NOOTROPIC_TIERS[6]["flavor"],
        }
        _NOOT_VIS = {
            1: True,
            3: nootropic_tier_max >= 3,
            5: flmodafinil_unlocked or nootropic_tier_max >= 5,
            ## Black market shows up once your reputation is real.
            ## 100 Coding = T3 "Solid Developer" — the chemist takes you seriously.
            6: stats.coding_skill >= 100,
        }
        _noot_options = []
        for _tn in (1, 3, 5, 6):
            _ti = NOOTROPIC_TIERS[_tn]
            _hatred_sign = "+" if _ti["hatred"] >= 0 else ""
            _eff = "+{} Coding, {}{} Hatred, 1-of-3 card".format(
                _ti["coding"], _hatred_sign, _ti["hatred"])
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
        ## RESEARCH PUBMED — free upgrade lane. Always visible. Routes to the
        ## deck upgrade picker (deck breadth vs deck quality is the BH axis).
        _noot_options.append({
            "label_name":     "_apply_research",
            "title":          "RESEARCH PUBMED",
            "accent":         class_accent_color("biohacker"),
            "cost_text":      "FREE",
            "effect_text":    "Upgrade 1 card",
            "flavor_text":    bh_research_flavor(),
            "class_relevant": True,
            "visible":        True,
        })

        _noot_open_line = bh_open_line()
        _noot_subtitle  = bh_subtitle()

    "[_noot_open_line][_dep_warning]"

    call screen activity_submenu(
        title       = "NOOTROPICS — PICK A PATH",
        subtitle    = _noot_subtitle,
        options     = _noot_options,
        back_label  = "select_activity",
    )


label _apply_noot_t1:
    $ _tier = 1
    jump _apply_nootropic_tier

label _apply_noot_t3:
    $ _tier = 3
    jump _apply_nootropic_tier

label _apply_noot_t5:
    $ _tier = 5
    jump _apply_nootropic_tier

label _apply_noot_t6:
    $ _tier = 6
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

        # Track usage. nootropic_uses is a 5-length array (one slot per
        # legacy T1-T5). Tier 6 (Black Market) is tracked separately on
        # store.bh_blackmarket_uses so it doesn't index out of bounds.
        if _tier <= 5:
            nootropic_uses[_tier - 1] += 1
        else:
            store.bh_blackmarket_uses = getattr(store, 'bh_blackmarket_uses', 0) + 1
        nootropic_last_tier = _tier
        ## BH PROTOCOL — current active stack maps to a name shown in HUD/log
        ## and read by battle_engine to drive the per-fight bonus (Legal: +1
        ## starting block; Shady: +1 max energy; Lab: +1 max energy + 1
        ## opening hand). Slot 1/3/5 = Legal/Shady/Lab.
        _PROTOCOL_NAMES = {1: "Legal", 3: "Shady", 5: "Lab", 6: "Black Market"}
        store.bh_protocol = _PROTOCOL_NAMES.get(_tier, None)

        # Check for new tier unlocks
        _unlock = check_nootropic_unlocks()

        ## Card-grant trio for this tier. One card per archetype (stimulant /
        ## neurochem / wetware), randomised within each archetype's pool at
        ## the tier's rarity so repeated doses don't show the same trio.
        ## Use __import__('random') inline — `import random as X` in a label's
        ## python block leaves the module bound as a local that the next save
        ## tries to pickle and crashes on. Same pattern as ev_pills uses.
        _BH_GRANT_POOLS = {
            1: {  # commons
                "stimulant": ["microdose", "hrv_spike"],
                "neurochem": ["pattern_match", "n_of_one"],
                "wetware":   ["mitochondrial"],
            },
            3: {  # uncommons
                "stimulant": ["stack_up", "adrenal_burst", "racetam"],
                "neurochem": ["cognitive_stack", "recall_protocol"],
                "wetware":   ["telomere", "hyper_if"],
            },
            5: {  # rares (event/boss cards excluded; ladder pool is the
                  # standard rare draft)
                "stimulant": ["megadose", "burnout", "catecholamine_spike", "flmodafinil", "override"],
                "neurochem": ["lucid_window"],
                "wetware":   ["pain_threshold"],
            },
            ## Black market draws from the rare T5 pool with one upgrade
            ## promotion roll baked in — buying at 25k should feel like the
            ## money chose for you. Same pools as T5, evaluated identically.
            6: {
                "stimulant": ["megadose", "burnout", "catecholamine_spike", "flmodafinil", "override"],
                "neurochem": ["lucid_window"],
                "wetware":   ["pain_threshold"],
            },
        }
        _pools = _BH_GRANT_POOLS.get(_tier, {})
        _noot_trio = [
            __import__('random').choice(_pools["stimulant"]),
            __import__('random').choice(_pools["neurochem"]),
            __import__('random').choice(_pools["wetware"]),
        ]

        _outcome_str = "- {:,} CZK  |  +{} Coding  |  {} Hatred".format(
            _cost, _coding_gain,
            "{}".format(_t["hatred"]) if _t["hatred"] < 0 else "+{}".format(_t["hatred"]))
        if nootropic_dependency and _tier == 5:
            _outcome_str += "  [TOLERANCE — reduced effect]"

        ## Post-dose reflection escalates with per-tier use count. See
        ## bh_postdose_flavor() — voice drifts from "next-day delivery" to
        ## "Tom didn't say anything" to "Colonel's face is very clear today".
        _postdose = bh_postdose_flavor(_tier)

    "[_postdose]"
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

    ## Tier unlock announcement (3-user-tier model)
    if _unlock == "SHADY_UNLOCKED":
        "\nThe forums whispered a name. You added him on Telegram. He answers on the third ring.\n[[NEW TIER UNLOCKED: Shady Source]"

    if _unlock == "LAB_UNLOCKED":
        "\nThree months of forum credibility paid off. You have an address. The vials are plain. The labelling is wrong on purpose.\n[[NEW TIER UNLOCKED: Lab Grade]"

    ## Card grant — 1-of-3 trio per the tier's rarity pool, one card per archetype.
    window hide
    call screen card_reward_trio_screen(cards=_noot_trio)
    python:
        if _return and _return not in ("skip", None):
            grant_card(_return, silent=False)
        ## Lock the day — one nootropic action per day. Set even on skip;
        ## the dose was paid for and committed regardless of card pick.
        store.nootropics_done_today = True

    ## Protocol 10/10 capstone — fires once when total nootropic BUYs hits 10.
    ## Mirrors soma_ten_reward. Research (READ UP) is the upgrade lane and does
    ## NOT increment nootropic_uses — only buys count toward the capstone.
    if sum(getattr(store, 'nootropic_uses', [0,0,0,0,0])) >= 10:
        call protocol_ten_reward

    ## Dependency warning — preserved at slot 5 (Lab). Old gate was "1 dose
    ## before threshold" so warning fires after first Lab dose. Kept compatible
    ## with the 3-user-tier model where slot 5 == Lab.
    python:
        _dep_warn = nootropic_uses[4] == 1 and _tier == 5

    if _dep_warn:
        "[[WARNING] One more Lab-grade dose and your baseline changes permanently.\nHard dependency triggers at 2 total Lab doses."

    ## Nootropics is a top-level daily activity now — consumes the slot.
    python:
        activity_selected = True
    jump end_day


## ---------------------------------------------------------------------------
## RESEARCH PUBMED — PubMed / forum deep-dive. The BH upgrade lane. Free in
## cash; consumes the per-day nootropic action only on commit (cancel out of
## the picker = no slot consumed, retry allowed). No stat bumps — pure card
## upgrade is the entire payoff.
## ---------------------------------------------------------------------------

label _apply_research:

    scene bg_bh_supplier

    python:
        _stg = bh_stage()
        _research_lines = [
            "You skip the cabinet. Three open tabs of papers. Two forum threads. A notebook with bad handwriting.",
            "Cabinet stays open in the background. Twelve tabs. A spreadsheet you keep meaning to clean up.",
            "The cabinet is in your peripheral vision. So is the dose schedule. You're reading anyway.",
            "You don't bother closing the cabinet. The notebook has stopped being notes — it's a second baseline.",
        ]
        _research_close = [
            "You close the tabs. You'll come back to it tomorrow.",
            "Tabs minimised. Not closed. You'll be back inside an hour.",
            "You leave the tabs open. The browser remembers things you don't anymore.",
            "There's no closing it. The reading is the protocol now.",
        ]
        _research_open_line = _research_lines[_stg - 1]
        _research_close_line = _research_close[_stg - 1]

    "[_research_open_line]"

    call _run_card_upgrade_flow
    $ _research_result = _return

    if _research_result is None:
        "[_research_close_line]"
        jump activity_coding

    python:
        store.nootropics_done_today = True
    show screen outcome_panel("Card upgraded.")
    pause
    hide screen outcome_panel

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
        _cr_card = "breath_test"
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

    ## StS-style choice events — drained per run (no repeats), shared with the
    ## Overtime activity, which pulls from the same pool. Each ev_* label drives
    ## an event_screen / event_outcome flow (events/event_screen.rpy +
    ## event_engine.rpy). Battles take priority; an event fills this daily slot
    ## only when the day-band ladder pool is dry.
    python:
        _ensure_random_event_pool()
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
        call battle_with(_slot_eid, _slot_tier) from _call_battle_with_1
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
