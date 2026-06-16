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

    ## Difficulty selection — easy / hard / insane. Reaches the 2.5x / 5x score
    ## multipliers and 7/9-card Colonel decks that were previously dead content.
    call difficulty_selection from _call_difficulty_selection

    ## Character class selection
    call character_class_selection from _call_character_class_selection

    ## Arc I - Car Incident (Day 1)
    call car_incident from _call_car_incident

    ## Main 30-day loop
    call main_loop from _call_main_loop

    return


## ---------------------------------------------------------------------------
## DIFFICULTY SELECTION
## ---------------------------------------------------------------------------

label difficulty_selection:

    scene bg_black

    $ store._chosen_difficulty = None
    call screen difficulty_selection_screen

    $ init_game(store._chosen_difficulty or "easy")


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

    if _noot_tag == "dependency_cleared":
        scene bg_jb_flat
        "[[DEPENDENCY CLEARED]"
        "[_noot_flavor]"

    ## Special events. Top-level `call ... from _xxx` (NOT renpy.call inside a
    ## python block) so saves taken mid-call survive future line-shifting edits
    ## to script.rpy — the `from` clause creates a named return label that's
    ## looked up by name, not by line number.
    if current_day == 14:
        call salary_day from _call_salary_day_daystart

    ## Day 16 — THE MIDNIGHT CALL. The ARC II Colonel interlude (a 2AM phone
    ## call): a second Colonel touchpoint before day 30. On day 16 (not a
    ## LADDER_EVENT_DAY) so a battle/event slot can't swallow it.
    if current_day == 16:
        call midnight_call from _call_midnight_call_daystart

    ## BB "The Trainer" arc (Iron Garden) — additive day_start interludes on
    ## days 7/13/19, gated to the bodybuilder class + the prior arc stage, so
    ## they layer on top of the day WITHOUT consuming the random-event battle
    ## slots. class_arc_pre_colonel_check flushes any stage still pending.
    if stats.player_class == "bodybuilder":
        if current_day == 7 and getattr(store, 'bb_arc_stage', 0) == 0:
            call bb_trainer_eye from _call_bb_trainer_eye
        elif current_day == 13 and getattr(store, 'bb_arc_stage', 0) == 1:
            call bb_trainer_meet from _call_bb_trainer_meet
        elif current_day == 19 and getattr(store, 'bb_arc_stage', 0) == 2:
            call bb_trainer_platform from _call_bb_trainer_platform

    ## Battle ladder / random events:
    ## - Regular cadence: days 3, 6, 9, 12, 15, 18, 21
    ## - Plus day 27 — a Hard-tier slot for players who deferred the Colonel
    ##   to day 30 (the day-25 Colonel path ends the game before reaching 27).
    if current_day in LADDER_EVENT_DAYS:
        call random_event_check from _call_random_event_check_daystart

    ## Day 24 — the Colonel's Guard. A fixed-day elite (no longer a floating
    ## day-20+ boss): his crew intercepts JB the day before the Martin meeting.
    ## Fires like a story beat — the fight resolves and the day rolls over the
    ## normal way (do_end_day), so the Day-25 Martin meeting isn't swallowed by
    ## a day-advancing battle branch. Skipped if Act II was already cleared.
    if current_day == 24 and 2 not in (getattr(store, '_act_bosses_done', None) or set()):
        call battle_with("garda", "hard") from _call_garda_day24
        python:
            if getattr(store, '_act_bosses_done', None) is None:
                store._act_bosses_done = set()
            store._act_bosses_done.add(2)

    if current_day == 25:
        call martin_meeting from _call_martin_meeting_daystart

    ## Self-heal poisoned saves: stats.colonel_day must be 25 (Martin's
    ## "brave" path) or 30 (default / "reasonable"). Any other value is
    ## stale state from an older build or a dev-console tweak — left
    ## alone it would trigger the final boss mid-run on load.
    python:
        if stats.colonel_day not in (26, 30):
            stats.colonel_day = 30

    if current_day == stats.colonel_day and current_day >= 26:
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

    ## Fixer arrival — every 5th day he sets up shop. Announced here in
    ## daily_menu (not day_start) so it fires on the day the hub actually
    ## renders, regardless of whether a battle advanced the clock first; the
    ## per-day guard keeps it to once per visit, not every hub re-entry.
    if fixer_visits_today(current_day) and getattr(store, '_fixer_arrival_shown_day', None) != current_day:
        $ store._fixer_arrival_shown_day = current_day
        "Your phone buzzes once. A number with no name. You know the number."
        "'I'm in town. Third floor, same as always. Today only — after that I'm a ghost again.'"
        window hide

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

    "You head to the gym with your trainer.\nTraining will help you relax."

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
                store.gym_sessions = getattr(store, 'gym_sessions', 0) + 1
                ## BB-only common: spotter granted on the 3rd session of the run.
                if store.gym_sessions == 3 and stats.player_class == "bodybuilder":
                    grant_card("hold_the_line", silent=True)
                if store.gym_sessions >= 5:
                    _newly_unlocked = unlock_achievement("gym_rat")
                    if _newly_unlocked and stats.player_class == "bodybuilder":
                        grant_card("iron_stance", silent=True)
                ## Base relief is 33% of the hatred cap (was a 10/15/25 roll —
                ## the roll now only picks the narration). The BB bonus rides
                ## on top. Consecutive gym days (regular OR heavy — they
                ## share the key) bleed the whole payout 25% per repeat day.
                _gym_mult = activity_repeat_tick("gym")
                _gym_base_red = int(round(hatred_cap() * 0.33))
                _total_red = int(round((_gym_base_red + _bb_bonus) * _gym_mult))
                if _roll == 1:
                    _gym_text = "Personal record. The bar tells the truth. The Colonel doesn't exist for 90 minutes."
                elif _roll == 2:
                    _gym_text = "Solid session. Head's quieter than this morning."
                else:
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
                    ## Canonical helper — was inlined here with stale 80 for
                    ## BH, missed in the 80→90 buff. class_max_hp() includes
                    ## the gym bonus by default.
                    store.run_hp_max = class_max_hp()
                    store.run_hp = store.run_hp_max
                _heal_max_future = store.run_hp_max + _gym_max_bump
                _gym_heal = int(round(_heal_max_future * 0.33 * _gym_mult))
                _heal_parts = []
                if _gym_max_bump > 0:
                    _heal_parts.append("{{color=#00cc88}}+{} MAX HP{{/color}}".format(_gym_max_bump))
                else:
                    _heal_parts.append("MAX HP capped")
                _heal_parts.append("{{color=#00cc88}}+{} HP{{/color}}".format(_gym_heal))
                if _gym_mult < 1.0:
                    _heal_parts.append("REPEAT -{}%".format(int(round((1.0 - _gym_mult) * 100))))
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

    "The owner meets you at the door. Doesn't say hello. Looks at your shoulders, then your eyes, then nods once."
    "'Heavy day. We go until you can't grip the bar.'"
    "Two hours later your forearms feel like wet rope and your back is one long ache."
    "You drive home with the windows down. The wind is loud. Your head is finally quiet."

    python:
        ## Always-apply progression — you completed the session.
        store.gym_sessions = getattr(store, 'gym_sessions', 0) + 1
        add_soma(1)
        if store.gym_sessions == 3 and stats.player_class == "bodybuilder":
            grant_card("hold_the_line", silent=True)
        if store.gym_sessions >= 5:
            _newly_unlocked = unlock_achievement("gym_rat")
            if _newly_unlocked and stats.player_class == "bodybuilder":
                grant_card("iron_stance", silent=True)
        ## Pre-compute heavy-session HEAL payload (heavier than regular gym:
        ## -30 hatred + +15 HP, but no Max HP bump — that's the regular gym's
        ## job). Numbers only applied if the player picks HEAL. Shares the
        ## "gym" diminishing-returns key with regular gym, so alternating
        ## the two doesn't dodge the consecutive-day penalty.
        _heavy_mult = activity_repeat_tick("gym")
        _heavy_heal = int(round(15 * _heavy_mult))
        _heavy_relief = int(round(30 * _heavy_mult))
        _heavy_heal_text = "- {:,} CZK, -{} PCR HATRED, +1 SOMA, +{} HP{}".format(_heavy_cost, _heavy_relief, _heavy_heal, activity_repeat_tag(_heavy_mult))

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
            stats.increment_stats_pcr_hatred(-_heavy_relief)
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

    ## Pick a modality. Each one is a different combat-prep buff for the
    ## next fight — sauna for heal builds, meditation for energy, cold
    ## plunge for tank fights, red light for regen. Random rolling here
    ## stopped making sense once the buffs became build-defining (player
    ## reported "you said I choose, but it's random — what?").
    python:
        _bh_accent = class_accent_color("biohacker")
        _rec_options = [
            {
                "label_name":     "_apply_rec_sauna",
                "title":          "SAUNA",
                "accent":         _bh_accent,
                "cost_text":      "FREE",
                "class_relevant": True,
                "art":            "images/backgrounds/bh_recovery_sauna.jpg",
                "art_glyph":      "~",
                "stat_lines": [
                    ("BATTLE BONUS", "All heals +100%"),
                    ("HP",           "+25 (max +5)"),
                    ("HATRED",       "-10"),
                ],
            },
            {
                "label_name":     "_apply_rec_meditation",
                "title":          "MEDITATION",
                "accent":         _bh_accent,
                "cost_text":      "FREE",
                "class_relevant": True,
                "art":            "images/backgrounds/bh_recovery_meditation.jpg",
                "art_glyph":      "○",
                "stat_lines": [
                    ("BATTLE BONUS", "+2 energy (turn 1)"),
                    ("HP",           "+15"),
                    ("HATRED",       "-30"),
                ],
            },
            {
                "label_name":     "_apply_rec_coldplunge",
                "title":          "COLD PLUNGE",
                "accent":         _bh_accent,
                "cost_text":      "FREE",
                "class_relevant": True,
                "art":            "images/backgrounds/bh_recovery_coldplunge.jpg",
                "art_glyph":      "*",
                "stat_lines": [
                    ("BATTLE BONUS", "+25 starting block"),
                    ("HP",           "+30 (max +10)"),
                    ("HATRED",       "—"),
                ],
            },
            {
                "label_name":     "_apply_rec_redlight",
                "title":          "RED LIGHT",
                "accent":         _bh_accent,
                "cost_text":      "FREE",
                "class_relevant": True,
                "art":            "images/backgrounds/bh_recovery_redlight.jpg",
                "art_glyph":      "●",
                "stat_lines": [
                    ("BATTLE BONUS", "+5 HP/turn regen"),
                    ("HP",           "+20 (max +5)"),
                    ("HATRED",       "-15"),
                ],
            },
        ]

    call screen activity_submenu(
        title       = "RECOVERY — PICK A PROTOCOL",
        subtitle    = "Each modality preps a different combat edge for the next fight.",
        options     = _rec_options,
        back_label  = "select_activity",
    )


label _apply_rec_sauna:
    scene bg_bh_rec_sauna with Dissolve(0.4)
    "Eight minutes at 90°C. You finish on the cold tile, condensation everywhere, lungs still wide. Heat-shock proteins do the work."
    python:
        store.gym_max_hp_bonus = getattr(store, 'gym_max_hp_bonus', 0) + 5
        if getattr(store, 'run_hp_max', None) is None:
            store.run_hp_max = class_max_hp()
            store.run_hp = store.run_hp_max
        else:
            store.run_hp_max += 5
            store.run_hp = min(store.run_hp_max, store.run_hp + 5)
        _restored = event_heal(25)
        stats.increment_stats_pcr_hatred(-10)
        store.pending_recovery_buff = {"type": "heal_boost", "value": 2.0}
        _rec_out = "SAUNA  |  +{} HP  |  +5 MAX HP  |  -10 Hatred  |  NEXT FIGHT: heals +100%".format(_restored)
    jump _recovery_finish


label _apply_rec_meditation:
    scene bg_bh_rec_meditation with Dissolve(0.4)
    "Twenty minutes on the cushion. The Colonel-loop unhooks somewhere around minute eight. You don't notice until minute fifteen."
    python:
        _restored = event_heal(15)
        stats.increment_stats_pcr_hatred(-30)
        store.pending_recovery_buff = {"type": "turn1_energy", "value": 2}
        _rec_out = "MEDITATION  |  +{} HP  |  -30 Hatred  |  NEXT FIGHT: +2 energy (turn 1)".format(_restored)
    jump _recovery_finish


label _apply_rec_coldplunge:
    scene bg_bh_rec_coldplunge with Dissolve(0.4)
    "Two minutes at 4°C. Your nervous system does the math and reboots without asking. HRV up six points by tomorrow."
    python:
        store.gym_max_hp_bonus = getattr(store, 'gym_max_hp_bonus', 0) + 10
        if getattr(store, 'run_hp_max', None) is None:
            store.run_hp_max = class_max_hp()
            store.run_hp = store.run_hp_max
        else:
            store.run_hp_max += 10
            store.run_hp = min(store.run_hp_max, store.run_hp + 10)
        _restored = event_heal(30)
        store.pending_recovery_buff = {"type": "starting_block", "value": 25}
        _rec_out = "COLD PLUNGE  |  +{} HP  |  +10 MAX HP  |  NEXT FIGHT: +25 starting block".format(_restored)
    jump _recovery_finish


label _apply_rec_redlight:
    scene bg_bh_rec_redlight with Dissolve(0.4)
    "Twenty minutes under the panel. You log the wavelength. You log the duration. Mitochondria warm up."
    python:
        store.gym_max_hp_bonus = getattr(store, 'gym_max_hp_bonus', 0) + 5
        if getattr(store, 'run_hp_max', None) is None:
            store.run_hp_max = class_max_hp()
            store.run_hp = store.run_hp_max
        else:
            store.run_hp_max += 5
            store.run_hp = min(store.run_hp_max, store.run_hp + 5)
        _restored = event_heal(20)
        stats.increment_stats_pcr_hatred(-15)
        store.pending_recovery_buff = {"type": "regen", "value": 5}
        _rec_out = "RED LIGHT  |  +{} HP  |  +5 MAX HP  |  -15 Hatred  |  NEXT FIGHT: +5 HP/turn regen".format(_restored)
    jump _recovery_finish


label _recovery_finish:
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
## BOUNCER — the money lane. One venue, no card-shop side hustle (cards are the
## Coding lane's job). Rolls a rarity-tiered payout: common / uncommon / rare.
## Base 12.5k / 17.5k / 22.5k + the +2,500 BB bonus = ~15k / 20k / 25k profit
## for the Bodybuilder. The grind costs Hatred on a common night; a jackpot
## night relieves it.
## ---------------------------------------------------------------------------

label activity_bouncer:

    scene bg_havana_club

    python:
        _bb_cash = 2500 if stats.player_class == "bodybuilder" else 0
        _bb_tag = " [BODYBUILDER BONUS]" if _bb_cash else ""
        ## Flat 20k base — always, on a fresh night. Consecutive bouncer
        ## nights bleed it 25% per repeat day (resets after a day off) AND
        ## escalate the night itself: the longer the same cop stands in the
        ## same doorway, the more the city notices him standing in it.
        _bnc_mult = activity_repeat_tick("bouncer")
        _bnc_n = store._activity_streaks.get("bouncer", {}).get("count", 1)
        _pending_money = int(round(20000 * _bnc_mult)) + _bb_cash
        _bnc_tag = activity_repeat_tag(_bnc_mult)
        if _bnc_n <= 1:
            ## Fresh night — full pay, no heat.
            _pending_hatred = 0
            _btext = "A quiet shift. IDs, nods, one umbrella handed back at two in the morning. The envelope is full and nobody asked what you do during the day."
        elif _bnc_n == 2:
            _pending_hatred = 5
            _btext = "Same doorway, same playlist. A drunk regular won't leave at closing, so you walk him out by the collar while he explains he knows his rights. He doesn't know the half of it."
        elif _bnc_n == 3:
            _pending_hatred = 10
            _btext = "Third night straight. Somebody calls the police on a fight you already broke up — the patrol takes one look at you and grins. 'Moonlighting, kolego?' By morning the whole precinct knows."
        else:
            _pending_hatred = 15
            _btext = "Fourth night running. The drunk from Tuesday is back with two friends and a phone already filming. By sunrise you're a clip with subtitles, and the Colonel has seen it twice."
        if _pending_hatred > 0:
            _boutcome = "+ {:,} CZK, +{} PCR HATRED{}{}".format(stats.money_gain_preview(_pending_money), _pending_hatred, _bb_tag, _bnc_tag)
        else:
            _boutcome = "+ {:,} CZK{}{}".format(stats.money_gain_preview(_pending_money), _bb_tag, _bnc_tag)

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
        _bc_flavor = "Six weeks. Study days roll high-tier cards after. Enrolling doesn't spend the hour."
        if _is_de:
            _bc_flavor = "Six weeks. You'll read the instructor for a discount. Study days roll high-tier cards after. Enrolling doesn't spend the hour."
        _bh_accent = class_accent_color("biohacker")

        ## ── BH gets a SPLIT coding picker ──────────────────────────────
        ## STUDY = invest (+Coding XP, no card, no money). FREELANCE CODE
        ## = cash out (CZK scaled by tier, no XP, no card). Lane separation
        ## clarifies the decision: long game vs immediate cash. Nootropic
        ## doses remain the only path to new cards.
        if _is_bh:
            ## Freelance hireability + payout by current Coding tier.
            _fc_skill   = stats.coding_skill
            _fc_payout  = 0
            _fc_locked  = False
            _fc_lock_t  = ""
            if _fc_skill >= 200:   _fc_payout = 22000
            elif _fc_skill >= 150: _fc_payout = 13000
            elif _fc_skill >= 100: _fc_payout = 7500
            elif _fc_skill >=  35: _fc_payout = 3500
            else:
                _fc_locked = True
                _fc_lock_t = "Need 35+ Coding. Nobody hires Tier 1 yet."

            _coding_options = [
                {
                    "label_name":     "coding_study",
                    "title":          "STUDY",
                    "accent":         _bh_accent,
                    "cost_text":      "FREE",
                    "art":            "images/pictures/act_coding.png",
                    "art_xoff":       -60,
                    "effect_text":    "+15 Coding XP",
                    "flavor_text":    "Documentation tabs. A side project. No paycheck — pure investment.",
                    "class_relevant": True,
                },
                {
                    "label_name":     "coding_freelance",
                    "title":          "FREELANCE",
                    "accent":         _bh_accent,
                    "cost_text":      "FREE",
                    "effect_text":    ("+{:,} CZK".format(_fc_payout) if not _fc_locked else "Need 35+ Coding"),
                    "flavor_text":    ("An hour of billable work. Coding tier sets the rate." if not _fc_locked else "Tier 1 can't price an hour yet. Study first."),
                    "class_relevant": True,
                    "locked":         _fc_locked,
                    "lock_text":      _fc_lock_t,
                },
                {
                    "label_name":     "coding_bootcamp",
                    "title":          "JOIN BOOTCAMP",
                    "accent":         _bh_accent,
                    "cost_text":      _bc_cost_text,
                    "effect_text":    "+25 Coding now  ·  +5 Coding/night",
                    "flavor_text":    "Six weeks of deadlines and code reviews. The fastest way to tier up the protocol. Enrolling doesn't spend the hour.",
                    "class_relevant": True,
                    "locked":         _bc_done,
                    "lock_text":      "Already enrolled. The buff is live.",
                },
            ]
        else:
            ## Other classes — STUDY keeps the card-trio behaviour; bootcamp
            ## option still available (BH skipped because their tier ramp
            ## happens via the top-level Nootropics Lab).
            ## REFACTOR — coding's combat payoff for a non-BH (BB) run: spend
            ## the slot to upgrade a card to its '+' form. Budget = current
            ## Coding tier (1-5); a higher coder refactors more of the deck.
            _rf_tier      = _coding_tier_int()
            _rf_used      = getattr(store, "_refactors_used", 0)
            _rf_left      = max(0, _rf_tier - _rf_used)
            _rf_has_upg   = (player_deck is not None) and any(is_upgradeable(_c) for _c in player_deck.cards)
            _rf_locked    = (_rf_left <= 0) or (not _rf_has_upg)
            if _rf_left <= 0:
                _rf_lock_t = "Refactor budget spent. Raise Coding a tier for another."
            elif not _rf_has_upg:
                _rf_lock_t = "Nothing left to refactor — every card's already at its best."
            else:
                _rf_lock_t = ""
            _coding_options = [
                {
                    "label_name":     "coding_study",
                    "title":          "STUDY",
                    "accent":         _bh_accent,
                    "cost_text":      "FREE",
                    "art":            "images/pictures/act_coding.png",
                    "art_xoff":       -60,
                    "effect_text":    ("Pick a card  ·  +15 Coding" if stats.player_class == "bodybuilder" else "Pick from a 3-card offer"),
                    "flavor_text":    ("Bootcamp tier: high-rarity offers." if _bc_done else "An hour at the keyboard. A card to keep — and the skill sticks."),
                    "class_relevant": False,
                },
                {
                    "label_name":     "coding_refactor",
                    "title":          "REFACTOR",
                    "accent":         _bh_accent,
                    "cost_text":      "FREE",
                    "art":            "images/pictures/act_refactor.png",
                    "effect_text":    ("Upgrade a card  ·  +15 Coding  ({} left)".format(_rf_left) if not _rf_locked else "Upgrade a card  ·  +15 Coding"),
                    "flavor_text":    "Rewrite what you've already got. Cleaner, meaner. Coding tier sets how many.",
                    "class_relevant": True,
                    "locked":         _rf_locked,
                    "lock_text":      _rf_lock_t,
                },
                {
                    "label_name":     _bc_label,
                    "title":          "JOIN BOOTCAMP",
                    "accent":         _bh_accent,
                    "cost_text":      _bc_cost_text,
                    "art":            "images/pictures/act_bootcamp.png",
                    "effect_text":    "Study days roll rare cards",
                    "flavor_text":    _bc_flavor,
                    "class_relevant": False,
                    "locked":         _bc_done,
                    "lock_text":      "Already enrolled. The buff is live.",
                },
            ]

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

    ## BH path: pure +Coding XP, no card, no money. Cards come from doses;
    ## money comes from the FREELANCE tile. Lane split keeps each action
    ## with one clear purpose.
    ## XP at 12 (2026-06-03): an 18 here let study-spam ALONE cap Coding (T5)
    ## by ~day 12-16, making doses / overtime / research feel skippable. At 12,
    ## study is a strong contributor but the +8/win, doses and bootcamp also
    ## matter — multi-system engagement to reach T5, not a one-button ramp.
    if stats.player_class == "biohacker":
        "An hour at the keyboard. No client, no deadline. You're paying yourself in skill."
        python:
            _bh_study_xp = 12
            stats.increment_stats_coding_skill(_bh_study_xp)
            _study_outcome = "+{} CODING SKILL.".format(_bh_study_xp)
        window hide
        show screen outcome_panel(_study_outcome)
        pause
        hide screen outcome_panel
        python:
            activity_selected = True
        jump end_day

    ## Other classes — original card-trio behaviour, scaled by day band
    ## (or hard tier after Bootcamp).
    python:
        _study_tier = "hard" if bool(python_bootcamp) else _battle_ladder_band(day_cycle.current_day)
        _study_trio = pick_battle_rewards(_study_tier)

    "An hour at the keyboard. Documentation tabs open. You build something small that works, and it earns you something worth keeping."

    call screen card_reward_trio_screen(_study_trio)

    python:
        _study_card = _return
        if _study_card and _study_card != "skip":
            grant_card(_study_card, silent=True)
            _study_outcome = "+ Card."
        else:
            _study_outcome = "Passed on the offer."
        ## BB has no BH-style daily Coding lane (BH STUDY = +18 XP, no card). A
        ## modest +Coding on top of the card makes the tech build reachable
        ## without the 35k bootcamp wall. Delta read back so the panel matches
        ## the ceiling clamp at the cap.
        if stats.player_class == "bodybuilder":
            _cs_before = stats.coding_skill
            stats.increment_stats_coding_skill(15)
            _cs_gain = stats.coding_skill - _cs_before
            if _cs_gain > 0:
                _study_outcome += "  + {} CODING SKILL.".format(_cs_gain)

    window hide
    show screen outcome_panel(_study_outcome)
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump end_day


## ---------------------------------------------------------------------------
## REFACTOR — the title, made literal. Coding's combat payoff for BB: spend the
## slot to upgrade a card to its '+' form. Budget per run = current Coding tier
## (1-5), tracked in store._refactors_used. Reuses the shared upgrade flow
## (picker -> preview -> reveal); only burns the budget on a confirmed upgrade.
## ---------------------------------------------------------------------------

label coding_refactor:

    scene bg_jb_flat

    "You open the editor on a card you already know by heart. Same fight, fewer wasted lines."

    call _run_card_upgrade_flow from _call_refactor_upgrade_flow
    $ _rf_plus = _return

    if _rf_plus is None:
        ## Cancelled out of the picker — no budget spent, slot not consumed.
        jump activity_coding

    python:
        store._refactors_used = getattr(store, "_refactors_used", 0) + 1
        _rf_card_name = CARD_LIBRARY.get(_rf_plus, {}).get("name", "the card")
        ## Like STUDY, a refactor session also teaches you — +Coding XP.
        _rf_cs_before = stats.coding_skill
        stats.increment_stats_coding_skill(15)
        _rf_cs_gain = stats.coding_skill - _rf_cs_before
    window hide
    show screen outcome_panel("Refactored: {}.{}".format(_rf_card_name, ("   + {} CODING SKILL.".format(_rf_cs_gain) if _rf_cs_gain > 0 else "")))
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump end_day


## ---------------------------------------------------------------------------
## FREELANCE CODE — BH-only cash-out lane. Uses current coding tier to set
## the payout. No card, no XP — pure billable hour. Locked at T1 (nobody
## hires you yet); STUDY is the investment lane that unlocks this.
## ---------------------------------------------------------------------------

label coding_freelance:

    scene bg_jb_flat

    python:
        _fc_skill = stats.coding_skill
        if _fc_skill >= 200:   _fc_payout = 22000
        elif _fc_skill >= 150: _fc_payout = 13000
        elif _fc_skill >= 100: _fc_payout = 7500
        elif _fc_skill >=  35: _fc_payout = 3500
        else:                  _fc_payout = 0

    if _fc_payout <= 0:
        "You open the freelance board. Every post wants someone hireable. You aren't, yet."
        jump activity_coding

    python:
        if _fc_skill >= 200:
            _fc_line = "A six-figure US contract pings you direct. You bill the day at god-tier rates."
        elif _fc_skill >= 150:
            _fc_line = "A senior contractor gig. You quote your real hourly rate without flinching."
        elif _fc_skill >= 100:
            _fc_line = "A solid mid-market freelance ticket. You ship the feature before lunch."
        else:
            _fc_line = "A junior bug-fix on a small repo. The pay is small but it's clean money."

    "[_fc_line]"

    python:
        stats.increment_stats_value_money(_fc_payout)
        _fc_outcome = "+ {:,} CZK [FREELANCE].".format(stats.money_gain_preview(_fc_payout))

    window hide
    show screen outcome_panel(_fc_outcome)
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
        _bc_outcome = "- {:,} CZK, +25 CODING, +5 Coding/night. The hour is still yours.".format(_bc_cost)

    window hide
    call screen card_grant_screen(card_id="production_push")
    show screen outcome_panel(_bc_outcome)
    pause
    hide screen outcome_panel
    ## Enrolment is a purchase, not the day's hour — back to the coding
    ## picker with the slot still unspent (the tile now reads enrolled).
    jump activity_coding


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
        _bc_outcome = "- {:,} CZK [DE DISCOUNT], +25 CODING, +5 Coding/night. The hour is still yours.".format(_bc_cost)

    window hide
    call screen card_grant_screen(card_id="production_push")
    show screen outcome_panel(_bc_outcome)
    pause
    hide screen outcome_panel
    ## Enrolment is a purchase, not the day's hour — back to the coding
    ## picker with the slot still unspent (the tile now reads enrolled).
    jump activity_coding


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
            _ns_bonus = "\n[NIGHT BONUS]: Helped with an accident. Extra callout pay. +{:,} CZK.".format(stats.money_gain_preview(1500))
        elif _ns_roll <= 60:
            stats.increment_stats_pcr_hatred(10)
            _ns_bonus = "\n[NIGHT PENALTY]: Paperwork from an arrest took until 6AM. +10 PCR HATRED."
        else:
            _ns_bonus = ""

    "You work through the night. The city is different after midnight — quieter, stranger, more honest."
    "[_ns_bonus]"
    window hide
    show screen outcome_panel("+{:,} CZK, +15 PCR HATRED.{}".format(stats.money_gain_preview(5000), _ns_bonus))
    pause
    hide screen outcome_panel

    $ activity_selected = True
    jump end_day


## ---------------------------------------------------------------------------
## ACTIVITY: VISIT FIXER (every 5th day: 5/10/15/20/25 — gate in activity_select_screen)
##
## Vision §1 pillar 3: money is the only shop. The Fixer is the in-fiction
## sim action: BUY a card, BUY gear (a relic), SHRED a card. Browsing is free.
##
## Flow:
##   activity_fixer rolls the day's stock (once, cached), then falls into
##   fixer_shop_loop: a single fixer_shop screen shows cards + gear + the shred
##   service + LEAVE, returning a ("buy_card"|"buy_relic"|"shred"|"leave", arg)
##   tuple. Buys spend money, grant, drop the offer from stock, and re-enter the
##   loop so cash/stock stay live. Shred routes through fixer_removal_screen.
##
## Shred pricing: flat current price for ANY card, escalating each shred. See
## fixer_current_price() / fixer_next_price() in cards/card_data.rpy.
## Curve: 5K, 8K, 11K, 14K, 17K, 20K, 20K, ...
## ---------------------------------------------------------------------------

label activity_fixer:

    ## The Fixer is the in-fiction money shop (problem #4): money buys deck
    ## power. Three counters — BUY a card, BUY gear (a relic), SHRED a card —
    ## plus walk away. Browsing is free; only a purchase costs money. Does NOT
    ## consume the daily activity slot (sidebar action, like before).
    ##
    ## Stock is rolled ONCE per visit-day and cached in store._fixer_stock_day
    ## so re-entering the hub doesn't reroll the shelf (no StS reroll-scumming).
    ## Buying removes that offer from the cached stock so it can't be re-bought.

    ## Lights-on entry: a beat of black, the bulb clicks, the shop fades in.
    scene black with Dissolve(0.2)
    $ renpy.pause(0.3, hard=True)
    play sound "audio/sfx/bulb.mp3"
    scene bg_fixer_shop with Dissolve(0.5)

    python:
        _today = day_cycle.current_day
        if getattr(store, '_fixer_stock_day', None) != _today:
            store._fixer_stock_day   = _today
            store._fixer_card_stock  = build_card_shop_offers(5)
            store._fixer_relic_stock = build_relic_shop_offers(3)

    "A flat on the third floor of a panelák. The doorbell doesn't work; he knew you'd be here."
    "'Cash buys what's on the table. I take notes off nobody.'"

label fixer_shop_loop:

    python:
        ## Re-price the cached stock LIVE so the Fixer's Business Card (25% off)
        ## shows the moment you own it — without re-rolling the offered items.
        _shop_card_stock    = [dict(_o, price=fixer_buy_price(_o["price"])) for _o in (getattr(store, '_fixer_card_stock', None) or [])]
        _shop_relic_stock   = [dict(_o, price=fixer_buy_price(_o["price"])) for _o in (getattr(store, '_fixer_relic_stock', None) or [])]
        _shop_shred_price   = fixer_buy_price(fixer_current_price())
        _shop_can_shred     = (player_deck is not None) and any(
            _c not in CLASS_SIGNATURE_CARDS for _c in player_deck.cards)
        _shop_shred_blocked = getattr(store, '_fixer_shredded_today', False)

    window hide
    call screen fixer_shop(card_offers=_shop_card_stock, relic_offers=_shop_relic_stock, cash=stats.available_money, shred_price=_shop_shred_price, can_shred=_shop_can_shred, shred_blocked=_shop_shred_blocked)

    python:
        _shop_act, _shop_arg = _return if isinstance(_return, tuple) else (_return, None)

    if _shop_act == "leave" or _shop_act is None:
        jump daily_menu

    if _shop_act == "shred":
        jump fixer_shred

    if _shop_act == "buy_card":
        python:
            ## Mark the offer SOLD (don't drop it) — the shop screen keeps the
            ## slot in place with a SOLD stamp, StS-style, instead of reflowing.
            _cbuy_offer = next((o for o in store._fixer_card_stock if o["card_id"] == _shop_arg and not o.get("sold")), None)
            _cbuy_ok = False
            _cbuy_price = 0
            if _cbuy_offer is not None:
                _cbuy_price = fixer_buy_price(_cbuy_offer["price"])
                if stats.try_spend_money(_cbuy_price):
                    grant_card(_cbuy_offer["card_id"], silent=True)
                    _cbuy_offer["sold"] = True
                    _cbuy_name = CARD_LIBRARY.get(_shop_arg, {}).get("name", _shop_arg)
                    _cbuy_ok = True
        if _cbuy_ok:
            play sound "audio/sfx/cash_register.mp3"
            "'Pleasure.' He slides the card across the table."
            window hide
            show screen outcome_panel("- {:,} CZK   + {}".format(_cbuy_price, _cbuy_name))
            pause
            hide screen outcome_panel
        jump fixer_shop_loop

    if _shop_act == "buy_relic":
        python:
            _rbuy_offer = next((o for o in store._fixer_relic_stock if o["relic_id"] == _shop_arg and not o.get("sold")), None)
            _rbuy_ok = False
            _rbuy_price = 0
            if _rbuy_offer is not None and not has_relic(_shop_arg):
                _rbuy_price = fixer_buy_price(_rbuy_offer["price"])
                if stats.try_spend_money(_rbuy_price):
                    grant_relic(_shop_arg, silent=True)
                    _rbuy_offer["sold"] = True
                    _rbuy_meta = RELIC_LIBRARY.get(_shop_arg, {})
                    _rbuy_name = _rbuy_meta.get("name", _shop_arg)
                    _rbuy_hook = _rbuy_meta.get("hook", "")
                    _rbuy_ok = True
        if _rbuy_ok:
            play sound "audio/sfx/cash_register.mp3"
            "Sold."
            window hide
            show screen outcome_panel("- {:,} CZK   + {}".format(_rbuy_price, _rbuy_name))
            pause
            hide screen outcome_panel
        jump fixer_shop_loop

    jump fixer_shop_loop


## --- SHRED A CARD (the original removal flow) -----------------------------------
label fixer_shred:

    python:
        _fixer_current = fixer_buy_price(fixer_current_price())
        _fixer_next    = fixer_buy_price(fixer_next_price())
        _fixer_entries = []
        if player_deck is not None:
            for _cid in player_deck.cards:
                if _cid in CLASS_SIGNATURE_CARDS:
                    continue
                _fixer_entries.append(_cid)

    if not _fixer_entries:
        "'Nothing here I'd bother shredding. Save your money.'"
        jump fixer_shop_loop

    call screen fixer_removal_screen(entries=_fixer_entries, price=_fixer_current, next_price=_fixer_next)

    python:
        _fixer_action, _fixer_card = _return if isinstance(_return, tuple) else ("leave", None)

    if _fixer_action == "leave":
        jump fixer_shop_loop

    python:
        _shred_ok = False
        if stats.try_spend_money(_fixer_current):
            player_deck.remove(_fixer_card)
            store._fixer_removals = getattr(store, '_fixer_removals', 0) + 1
            store._fixer_shredded_today = True
            _fixer_name = CARD_LIBRARY.get(_fixer_card, {}).get("name", _fixer_card)
            ## Pawn-Shop Receipt (relic) — the shredded card is worth something
            ## to the right buyer. money_gain_preview keeps the panel honest.
            _pawn_bonus = 0
            if has_relic("pawn_receipt"):
                _pawn_bonus = stats.money_gain_preview(3000)
                stats.increment_stats_value_money(3000)
            _fixer_outcome = "- {:,} CZK   - 1 card ({})   ·   Next shred: {:,} CZK".format(
                _fixer_current, _fixer_name, fixer_buy_price(fixer_current_price())
            )
            if _pawn_bonus:
                _fixer_outcome += "   ·   Pawn slip + {:,} CZK".format(_pawn_bonus)
            _shred_ok = True

    if not _shred_ok:
        "He counts the notes again. 'Come back when you can pay.'"
        jump fixer_shop_loop

    "He feeds the card into a shredder that's older than you. The teeth are loud."
    "'Done. That's not in your deck anymore. Next one's pricier.'"

    window hide
    show screen outcome_panel(_fixer_outcome)
    pause
    hide screen outcome_panel

    jump fixer_shop_loop


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

        ## Passive run income — e.g. the crypto tip from letting Vlk walk. Pays
        ## out every night to the end of the run once granted.
        _passive_income = getattr(store, '_passive_daily_income', 0)
        if _passive_income > 0:
            stats.increment_stats_value_money(_passive_income)
        _coding_paycheck_disp = stats.money_gain_preview(_coding_paycheck)
        _passive_income_disp = stats.money_gain_preview(_passive_income)
        ## Beat Cop's Pension (relic) — a steady morning trickle of the old
        ## salary. Silent credit; the money bar reflects it.
        if has_relic("cop_pension"):
            stats.increment_stats_value_money(2500)

    if _coding_paycheck > 0:
        "[[FREELANCE] A client paid out overnight — [_coding_paycheck_disp:,] CZK in the account by morning."

    if _passive_income > 0:
        "[[CRYPTO] The dog-coin Vlk tipped you ticked over again — [_passive_income_disp:,] CZK in the wallet by morning."

    python:
        # Advance day
        day_cycle.next_day()
        activity_selected = False
        # Per-day Fixer gate — new day, one new shred available.
        store._fixer_shredded_today = False
        # Snapshot whether today's nootropics action was used BEFORE the
        # per-day reset — the bh_random_spending event roll reads this
        # next morning to skip a day after a dose (no double-punishment
        # for using the class identity). Cleared / refreshed each rollover.
        store._bh_dosed_yesterday = bool(getattr(store, 'nootropics_done_today', False))
        # Per-day Nootropics Lab gate — one dose OR one research session per day.
        store.nootropics_done_today = False
        # Defensive: scrub any stale module refs from older saves so the
        # next quicksave doesn't crash pickle.
        _bh_scrub_stale_module_refs()

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
    show screen outcome_panel("+ {} CZK".format(stats.money_gain_preview(_sal)))
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
            _dep_warning = "\n\n[DEPENDENCY ACTIVE] — Skipping a dose costs -8 Coding, +10 Hatred."

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
        ## Tiers open by STORY PROGRESSION (the day) OR by RUSHING (total doses
        ## bought) — a drugs-run player can grind purchases to skip ahead, while
        ## a casual buyer still gets each tier as the connection deepens over the
        ## 30 days. The old buy-3-in-a-row gate was too slow either way.
        _noot_buys = sum(getattr(store, 'nootropic_uses', None) or [])
        _noot_day  = day_cycle.current_day
        _NOOT_VIS = {
            1: True,
            3: (_noot_day >= 5)  or (_noot_buys >= 2),
            5: (_noot_day >= 11) or (_noot_buys >= 5) or flmodafinil_unlocked,
            ## Black market also opens once your reputation is real (100 Coding).
            6: (_noot_day >= 18) or (_noot_buys >= 8) or stats.coding_skill >= 100,
        }
        _NOOT_ART = {
            1: "images/pictures/act_noot_t1.png",
            3: "images/pictures/act_noot_t2.png",
            5: "images/pictures/act_noot_t3.png",
            6: "images/pictures/act_noot_t4.png",
        }
        _noot_options = []
        for _tn in (1, 3, 5, 6):
            _ti = NOOTROPIC_TIERS[_tn]
            _hatred_sign = "+" if _ti["hatred"] >= 0 else ""
            _eff = "+{} Coding, {}{} Hatred, 1-of-3 card".format(
                _ti["coding"], _hatred_sign, _ti["hatred"])
            _noot_cost = adjusted_cost(_ti["cost"])
            _noot_afford = stats.available_money >= _noot_cost
            _noot_options.append({
                "label_name":     "_apply_noot_t{}".format(_tn),
                "title":          _NOOT_TITLES[_tn],
                "accent":         class_accent_color("biohacker"),
                "cost_text":      "{:,} CZK".format(_noot_cost),
                "effect_text":    _eff,
                "flavor_text":    _NOOT_FLAVORS[_tn],
                "class_relevant": True,
                "visible":        _NOOT_VIS[_tn],
                "locked":         not _noot_afford,
                "lock_text":      "Need {:,} CZK.".format(_noot_cost),
                "art":            _NOOT_ART[_tn],
            })
        ## RESEARCH PUBMED — free upgrade lane. Always visible. Routes to the
        ## deck upgrade picker (deck breadth vs deck quality is the BH axis).
        _noot_options.append({
            "label_name":     "_apply_research",
            "title":          "RESEARCH PUBMED",
            "accent":         class_accent_color("biohacker"),
            "cost_text":      "FREE",
            "art":            "images/pictures/act_research.png",
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
        ## Tier-pool retier (2026-05-25):
        ##   - Piracetam (pattern_match) → T2 SHADY. It's a racetam — gray
        ##     market, not eshop-legal.
        ##   - Caffeine added to T1 STIM so every tier has at least one
        ##     attack option (T1 was previously all Skills).
        ##   - Ritalin added to T3 STIM for the same reason — methylphenidate
        ##     fits the SHADY-source flavor.
        ##   - Creatine (renamed mitochondrial) stays at T1 — foundational
        ##     wetware, matches the canonical T1 ingredient list.
        _BH_GRANT_POOLS = {
            1: {  # commons (LEGAL ESHOP — basic supplements)
                "stimulant": ["microdose", "hrv_spike", "caffeine", "tweak", "ice_bath"],
                "neurochem": ["n_of_one"],
                "wetware":   ["mitochondrial"],
            },
            3: {  # uncommons (SHADY — Telegram-tier compounds)
                "stimulant": ["stack_up", "adrenal_burst", "racetam", "ritalin", "theragun", "redline"],
                "neurochem": ["pattern_match", "cognitive_stack", "recall_protocol"],
                "wetware":   ["telomere", "hyper_if", "adrenaline", "red_light_therapy"],
                "coding":    ["decompile", "algorithm"],
            },
            5: {  # rares (LAB GRADE — gray-market exotics)
                "stimulant": ["megadose", "burnout", "catecholamine_spike", "flmodafinil", "override", "the_compound"],
                "neurochem": ["big_tech_offer", "open_source_pr"],
                "wetware":   ["pain_threshold", "homeostasis"],
            },
            ## Black market draws from the rare T5 pool — buying at 25k
            ## should feel like the money chose for you. Same shape as T5.
            6: {
                "stimulant": ["megadose", "burnout", "catecholamine_spike", "flmodafinil", "override", "the_compound"],
                "neurochem": ["big_tech_offer", "open_source_pr"],
                "wetware":   ["pain_threshold", "homeostasis"],
            },
        }
        _pools = _BH_GRANT_POOLS.get(_tier, {})
        ## Draw 3 DISTINCT cards from the WHOLE tier pool (not one rigid card per
        ## archetype — that made low tiers repetitive: the same n_of_one +
        ## mitochondrial every dose). Guarantee at least one Attack so every dose
        ## offers a way to actually hit something. (random inlined — a stored
        ## module ref breaks save pickling, per the note above.)
        _noot_flat = []
        for _noot_lst in _pools.values():
            _noot_flat.extend(_noot_lst)
        _noot_flat = list(dict.fromkeys(_noot_flat))
        __import__('random').shuffle(_noot_flat)
        _noot_trio = []
        _noot_atk = [_c for _c in _noot_flat if CARD_LIBRARY.get(_c, {}).get("type") == "Attack"]
        if _noot_atk:
            _noot_trio.append(_noot_atk[0])
        for _noot_c in _noot_flat:
            if len(_noot_trio) >= 3:
                break
            if _noot_c not in _noot_trio:
                _noot_trio.append(_noot_c)

        _outcome_str = "- {:,} CZK  |  +{} Coding  |  {} Hatred  |  STACK → {}".format(
            _cost, _coding_gain,
            "{}".format(_t["hatred"]) if _t["hatred"] < 0 else "+{}".format(_t["hatred"]),
            store.bh_protocol or "—")
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
        call protocol_ten_reward from _call_protocol_ten_reward

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

    call _run_card_upgrade_flow from _call__run_card_upgrade_flow_2
    $ _research_result = _return

    if _research_result is None:
        "[_research_close_line]"
        jump activity_coding

    python:
        store.nootropics_done_today = True
        ## PubMed research consumes the daily activity slot just like a
        ## dose buy. Cancel path (the `if _research_result is None` branch
        ## above) still bounces back to activity_coding with no slot used.
        activity_selected = True
    show screen outcome_panel("Card upgraded.")
    pause
    hide screen outcome_panel

    jump end_day


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

    ## Act bosses fire first — fixed-day reckonings, priority over the roll.
    ## Each act's boss fires once (boss_check marks the act done after).
    python:
        _boss_eid, _boss_tier, _boss_act = boss_check(day_cycle.current_day)
    if _boss_eid:
        call battle_with(_boss_eid, _boss_tier) from _call_act_boss_fight
        python:
            if getattr(store, '_act_bosses_done', None) is None:
                store._act_bosses_done = set()
            store._act_bosses_done.add(_boss_act)
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
        if _slot_kind == "event":
            ## Prefer an unseen ARC-banded marquee event; if every marquee has
            ## been seen this run, fall back to a recurring texture beat so the
            ## slot is never dead air.
            _chosen_event = _draw_marquee_event(day_cycle.current_day)
            if not _chosen_event:
                _chosen_event = _draw_recurring_event(day_cycle.current_day)

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
