################################################################################
## REFACTOR - Main Script
## Full 30-day game loop with all three arcs
################################################################################

## ---------------------------------------------------------------------------
## GAME START
## ---------------------------------------------------------------------------

label start:

    scene bg_black
    play music "audio/enter_the_code_theme.mp3" fadein 2.0

    ## Difficulty selection
    call difficulty_selection from _call_difficulty_selection

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

        ## Mid-late stats (representative of a real run reaching colonel)
        stats.coding_skill    = 110
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

    $ quick_menu = True

    call screen class_selection_screen

    ## Apply starting bonuses based on class choice
    python:
        apply_class_bonuses(stats)
        init_player_deck()

    python:
        if stats.player_class == "bodybuilder":
            _class_msg = "BODYBUILDER selected.\nEvery rep is a rep closer to freedom.\n[-5 Coding Skill applied as starting passive]"
        elif stats.player_class == "dark_empath":
            _class_msg = "DARK EMPATH selected.\nYou see through people. That is both your weapon and your curse.\n[-5 Police Hatred applied as starting passive]"
        elif stats.player_class == "biohacker":
            _class_msg = "BIOHACKER selected.\nYour body is a machine. Let's see how far you can push it.\n[+5 Coding Skill applied as starting passive]"
        else:
            _class_msg = "Class selected."

    "[_class_msg]"

    ## --- Class intro vignette: 3 lines establishing JB's lifestyle for this class ---
    if stats.player_class == "bodybuilder":
        scene bg_police_interior with Dissolve(0.6)
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

    ## Dynamic music routing — tension increases with hatred
    python:
        if stats.pcr_hatred >= 75:
            renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
        elif stats.pcr_hatred >= 40:
            renpy.music.play("audio/enter_the_code_theme.mp3", fadein=1.5)
        else:
            renpy.music.play("audio/enter_the_code_theme.mp3", fadein=1.5)

    scene bg_police_interior

    ## Win condition check — coding skill >= 100 at day 30 handled in colonel event
    ## Lose conditions checked each day

    python:
        # Check loss conditions
        if stats.pcr_hatred >= 100:
            renpy.jump("hatred_collapse_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")

    ## Crisis event — fires once per run when Hatred reaches 85
    python:
        if stats.pcr_hatred >= 85 and not getattr(store, '_crisis_triggered', False):
            store._crisis_triggered = True
            renpy.call("crisis_event_" + stats.player_class)

    show screen stats_bar
    call screen day_transition_screen(current_day) with arc_fade

    ## Nootropic morning effects — crash, withdrawal, or dependency notification
    python:
        _noot_result = apply_nootropic_morning_effects()
        _noot_tag    = _noot_result[0] if _noot_result else None
        _noot_flavor = _noot_result[1] if _noot_result else ""

    if _noot_tag == "withdrawal":
        scene bg_police_interior
        "[[WITHDRAWAL]]"
        "[_noot_flavor]"

    if _noot_tag == "dependency_triggered":
        scene bg_police_interior
        "[[DEPENDENCY TRIGGERED]]"
        "[_noot_flavor]"

    if _noot_tag == "soft_dependency":
        scene bg_police_interior
        "[[TOLERANCE WARNING]]"
        "[_noot_flavor]"

    if _noot_tag == "crash":
        scene bg_police_interior
        "[[AFTEREFFECTS]]"
        "[_noot_flavor]"

    ## Special events
    python:
        if current_day == 14:
            renpy.call("salary_day")

        # Midnight Call — Day 15
        if current_day == 15:
            renpy.call("midnight_call")

        # Day 6 — Bribe event always fires (hardcoded, gates corrupt cop chain)
        if current_day == 6:
            renpy.call("re_the_bribe")
        # Day 12 — Corrupt cop chain event 2 (only if bribe was taken on Day 6)
        elif current_day == 12 and getattr(store, 'corrupt_chain_1', False):
            renpy.call("re_corrupt_cop_2")
        # Day 18 — Corrupt cop chain event 3 (only if chain 2 was completed)
        elif current_day == 18 and getattr(store, 'corrupt_chain_2', False):
            renpy.call("re_corrupt_cop_3")
        # Random events every 3rd day, before day 22 (days 9, 15, 21 — or 12/18 if chain inactive)
        elif current_day % 3 == 0 and current_day < 22:
            renpy.call("random_event_check")

        # Martin Meeting — Day 24
        if current_day == 24:
            renpy.call("martin_meeting")

        # Colonel Event — Day 25 or 30 (set during Martin Meeting)
        if current_day == stats.colonel_day:
            renpy.call("colonel_event")

    ## BH-only random spending event — fires on non-event days, ~30% chance.
    ## "The cost of optimizing." Pool reshuffles when exhausted (events recur).
    python:
        _bh_event_day = (
            current_day == 6 or
            current_day == 12 or
            current_day == 14 or
            current_day == 15 or
            current_day == 18 or
            (current_day % 3 == 0 and current_day < 22) or
            current_day == 24 or
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

    scene bg_police_interior

    python:
        # Check loss conditions at start of each menu loop
        if stats.pcr_hatred >= 100:
            renpy.jump("hatred_collapse_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")

    show screen stats_bar
    show screen day_calendar

    ## Custom hub screen — buttons use Jump() actions to route to existing labels.
    call screen daily_hub_screen


label show_deck:
    hide screen day_calendar
    call screen deck_viewer
    show screen day_calendar
    jump daily_menu


label select_activity:
    hide screen day_calendar

    python:
        if activity_selected:
            renpy.jump("daily_menu")

    ## Custom tile-grid screen — buttons Jump() to activity_* labels directly.
    call screen activity_select_screen


## ---------------------------------------------------------------------------
## ACTIVITY: GYM
## ---------------------------------------------------------------------------

label activity_gym:

    scene bg_police_interior

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
            python:
                if not stats.try_spend_money(_gym_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS]] You check your wallet... you don't even have [_gym_cost] CZK for the gym entry.")
                    renpy.jump("select_activity")
                else:
                    _roll = __import__('random').randint(1, 3)

            python:
                _bb_bonus = 5 if stats.player_class == "bodybuilder" else 0
                ## Always-apply progression (you completed the session — TAKE or PASS):
                store.gym_streak += 1
                ## BB-only common: spotter granted at the 3-day streak (intermediate milestone)
                ## Streak-milestone cards are NOT the per-session reward — they're cumulative
                ## attendance unlocks, so they remain unconditional.
                if store.gym_streak == 3 and stats.player_class == "bodybuilder":
                    grant_card("spotter", silent=True)
                if store.gym_streak >= 5:
                    _newly_unlocked = unlock_achievement("gym_rat")
                    ## BB-only rare: iron_stance dropped on first 5-day streak unlock
                    if _newly_unlocked and stats.player_class == "bodybuilder":
                        grant_card("iron_stance", silent=True)
                _streak_add = min(store.gym_streak * 3, 15)
                ## Pending reward — applied only if the player PASSes the card offer.
                if _roll == 1:
                    _total_red = 25 + _bb_bonus + _streak_add
                    _gym_card = "personal_record"
                    _gym_text = "Something clicks today.\nYou hit a new personal record and for about 90 minutes the Colonel doesn't exist, the station doesn't exist, the paperwork doesn't exist.\nThere is only the bar, the weight, and the fact that your body does exactly what you tell it to.\nYou drive home in silence but it's the good kind of silence."
                elif _roll == 2:
                    _total_red = 15 + _bb_bonus + _streak_add
                    _gym_card = "iron_will"
                    _gym_text = "Solid session. Nothing transcendent, but you showed up and that's most of it.\nBy the last set your head is quieter than it was this morning.\nYou eat a chicken breast in your car in the gym parking lot and feel no shame whatsoever."
                else:
                    _total_red = 10 + _bb_bonus + _streak_add
                    _gym_card = "quick_jab"
                    _gym_text = "You go through the motions. Every rep feels like lifting a filing cabinet full of quarterly reports.\nYour trainer gives you a look that says he's seen more motivated people at DMVs.\nBut you finish. You paid the entry fee. You are slightly less likely to flip a desk today."
                _gym_outcome = "- {} CZK, -{} PCR HATRED{}{}".format(_gym_cost, _total_red, " [BODYBUILDER]" if _bb_bonus else "", " [STREAK x{}]".format(store.gym_streak) if _streak_add else "")

            "[_gym_text]"

            python:
                _took_gym = offer_card(_gym_card, "GYM", pass_stats_text=_gym_outcome)
                if not _took_gym:
                    ## PASS branch: hatred relief AND the BB-only SOMA stack.
                    ## SOMA represents "I trained the body" — TAKE means "I trained for the deck instead."
                    stats.increment_stats_pcr_hatred(-_total_red)
                    if stats.player_class == "bodybuilder":
                        store.bb_soma = min(10, getattr(store, 'bb_soma', 0) + 1)
                        if store.bb_soma >= 10:
                            unlock_achievement("maximum_stack")
                show_outcome_panel(_took_gym, _gym_card, _gym_outcome)

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
## Class-specific relief replacing the old universal therapy.
## Deeper hatred drop than regular gym, smaller card-or-stat lottery —
## you train for the body, the body trains you back.
## ---------------------------------------------------------------------------

label activity_gym_heavy:

    scene bg_police_interior

    python:
        _heavy_cost = adjusted_cost(800)
        if not stats.try_spend_money(_heavy_cost):
            renpy.say(None, "[[INSUFFICIENT FUNDS]] Heavy session needs {:,} CZK. The good gym isn't free.".format(_heavy_cost))
            renpy.jump("select_activity")
        ## Lazy-init gym_streak — same guard activity_gym uses, since HEAVY SESSION
        ## might be a player's first gym-equivalent activity on Day 1.
        if not hasattr(store, 'gym_streak'):
            store.gym_streak = 0

    "Vladek meets you at the door. He doesn't say hello. He looks at your shoulders, then your eyes, then nods once."
    "'Heavy day. We go until you can't grip the bar.'"
    "Two hours later your forearms feel like wet rope and your back is one long ache."
    "You drive home with the windows down. The wind is loud. Your head is finally quiet."

    python:
        ## Always-apply progression — you completed the session.
        store.gym_streak += 1
        if stats.player_class == "bodybuilder":
            store.bb_soma = min(10, getattr(store, 'bb_soma', 0) + 1)
            if store.bb_soma >= 10:
                unlock_achievement("maximum_stack")
        if store.gym_streak == 3 and stats.player_class == "bodybuilder":
            grant_card("spotter", silent=True)
        if store.gym_streak >= 5:
            _newly_unlocked = unlock_achievement("gym_rat")
            if _newly_unlocked and stats.player_class == "bodybuilder":
                grant_card("iron_stance", silent=True)
        ## Pure relief — no card offer here. The trade is "deeper relief instead of card lottery."
        stats.increment_stats_pcr_hatred(-30)
        _heavy_outcome = "- {:,} CZK, -30 PCR HATRED, +1 SOMA".format(_heavy_cost)

    show screen outcome_panel(_heavy_outcome)
    pause
    hide screen outcome_panel

    python:
        activity_selected = True
        store.gym_day = True
    jump end_day


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
            renpy.say(None, "[[INSUFFICIENT FUNDS]] The recovery clinic charges {:,} CZK. You don't have it.".format(_recovery_cost))
            renpy.jump("select_activity")

    "Twenty minutes in the red-light booth. Eight in the sauna. Two in the cold plunge — long enough that your respiratory rate normalizes back to baseline."
    "You log everything. Heart-rate variability up four points. Cortisol curve flatter than yesterday."
    "The data says you're recovering. Whether you {i}feel{/i} recovered is a separate question, but the data is the data."
    "You sleep eleven hours that night. No dreams. The morning is a clean buffer."

    python:
        ## Pure relief — no nootropic dose increment, no card.
        stats.increment_stats_pcr_hatred(-30)
        _recovery_outcome = "- {:,} CZK, -30 PCR HATRED".format(_recovery_cost)

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

    scene bg_police_interior

    "You were offered to work as a bouncer in either a local night club or a strip bar.\n\nNight club: Generally safe, but some risk.\nStrip bar: VERY RISKY, but VERY HIGH reward."

    python:
        _bouncer_options = [
            {
                "label_name":     "bouncer_night_club",
                "title":          "NIGHT CLUB",
                "accent":         "#ffd700",
                "cost_text":      "FREE",
                "effect_text":    "+ CZK · low risk",
                "detail_text":    "RANDOM",
                "card_hint":      "Side Income",
                "flavor_text":    "Drunks, mostly handled. The owner pays cash.",
                "class_relevant": False,
            },
            {
                "label_name":     "bouncer_strip_bar",
                "title":          "STRIP BAR",
                "accent":         "#ffd700",
                "cost_text":      "FREE",
                "effect_text":    "+ more CZK · ugly outcomes possible",
                "detail_text":    "RANDOM · RISKY",
                "card_hint":      "VIP Treatment / Brawl / Loan Sharks",
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

    python:
        _roll = __import__('random').randint(1, 100)
        _bb_cash = 1500 if stats.player_class == "bodybuilder" else 0
        _bouncer_card = None
        ## Pending stat deltas — applied unconditionally if no card to offer,
        ## or only on PASS if there is one.
        _pending_money = 0
        _pending_hatred = 0
        if _roll <= 70:
            _pending_money = 4000 + _bb_cash
            _pending_hatred = 10
            _bouncer_card = "side_income"
            _btext = "Uneventful. You stand in a doorway for six hours, nodding at people who are happier than you.\nA man in a pink shirt calls you 'big guy'. You do not react.\nAt 3 AM you calculate exactly how many more shifts like this you'd need to quit forever.\nThe number is getting smaller."
            _boutcome = "+ {} CZK, +10 PCR HATRED{}".format(4000 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")
        elif _roll <= 90:
            _pending_money = 7500 + _bb_cash
            _pending_hatred = -10
            _bouncer_card = "side_income"
            _btext = "Rare night. A group of regulars tips heavy, the manager actually notices your work, and nobody throws up on anyone.\nDriving home at 4 AM, windows down, you think: 'If this was my real job I would hate it slightly less.'\nThat is the closest thing to joy you have felt all week."
            _boutcome = "+ {} CZK, -10 PCR HATRED{}".format(7500 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")
        else:
            ## Bad outcome — no card offered; stats apply unconditionally below.
            _pending_money = 4000 + _bb_cash
            _pending_hatred = 20
            _btext = "Two drunk idiots fight over the same woman who is clearly interested in neither of them.\nYou step in. One of them recognizes you — 'TO JE PŘECE POLDA!' — and now his phone is out.\nYour colleagues see the video the next morning. The group chat has not stopped since.\nLieutenant Kovář sends you a thumbs up emoji. You want to die."
            _boutcome = "+ {} CZK, +20 PCR HATRED{}".format(4000 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")

    "[_btext]"

    python:
        if _bouncer_card:
            _took_bouncer = offer_card(_bouncer_card, "BOUNCER", pass_stats_text=_boutcome)
        else:
            _took_bouncer = False  ## no card — stats apply
        if not _took_bouncer:
            stats.increment_stats_value_money(_pending_money)
            stats.increment_stats_pcr_hatred(_pending_hatred)
        show_outcome_panel(_took_bouncer, _bouncer_card, _boutcome)

    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump end_day


label bouncer_strip_bar:

    python:
        _roll = __import__('random').randint(1, 100)
        _bb_cash = 1500 if stats.player_class == "bodybuilder" else 0
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
            _btext = "A famous regular shows up drunk and paranoid. Two guys try to drag him outside, but you intervene with textbook precision.\nYour boss calls you to the office and slides an envelope across the table.\n'Not many can do what you did tonight.'"
            _boutcome = "+{} CZK, -15 PCR HATRED{}".format(35000 + _bb_cash, _bb_tag)
        elif _roll <= 25:
            ## No card — stats apply unconditionally.
            _pending_money = 12500 + _bb_cash
            _pending_coding = 2
            _btext = "Steady crowds, few arguments, no real threats. You handle everything with routine precision.\nYou even use downtime to mentally rehearse OOP concepts and class hierarchies — weirdly effective."
            _boutcome = "+{} CZK, +2 CODING SKILLS{}".format(12500 + _bb_cash, _bb_tag)
        elif _roll <= 75:
            _pending_money = 6500 + _bb_cash
            _pending_hatred = 5
            ## BB-only: brawl prompt fires only for bodybuilder (class_lock filter).
            ## Non-BB players: offer_card returns False, stats apply (effectively no choice).
            _strip_card = "brawl"
            _btext = "You stand in a corridor that smells like vodka Red Bull and bad decisions for four hours.\nNothing interesting happens. One person cries in the bathroom. You pretend not to notice.\nYou pretend not to notice a lot of things in this job.\nAt least the envelope is solid."
            _boutcome = "+{} CZK, +5 PCR HATRED{}".format(6500 + _bb_cash, _bb_tag)
        elif _roll <= 95:
            ## No card — stats apply unconditionally.
            _pending_money = 1000 + _bb_cash
            _pending_hatred = 25
            _btext = "A fight breaks out inside. You break it up, but one participant recognizes your face from the force.\n'Ty vole, to je POLDA!' Your boss gives you only a partial payout."
            _boutcome = "+{} CZK, +25 PCR HATRED{}".format(1000 + _bb_cash, _bb_tag)
        else:
            _pending_money = -12500 + _bb_cash
            _pending_hatred = 35
            _pending_coding = -5
            _strip_card = "loan_sharks"
            _btext = "You turn your back for one second — enough for a coked-up idiot to drive a vodka bottle into your skull.\nPolice arrives and discovers you're moonlighting illegally. Your boss is furious."
            _boutcome = "{} CZK, +35 PCR HATRED, -5 CODING SKILLS{}".format(-12500 + _bb_cash, _bb_tag)

    "[_btext]"

    python:
        if _strip_card:
            _took_strip = offer_card(_strip_card, "STRIP-BAR", pass_stats_text=_boutcome)
        else:
            _took_strip = False
        if not _took_strip:
            if _pending_money:
                stats.increment_stats_value_money(_pending_money)
            if _pending_hatred:
                stats.increment_stats_pcr_hatred(_pending_hatred)
            if _pending_coding:
                stats.increment_stats_coding_skill(_pending_coding)
        show_outcome_panel(_took_strip, _strip_card, _boutcome)

    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump end_day


## ---------------------------------------------------------------------------
## ACTIVITY: CODING
## ---------------------------------------------------------------------------

label activity_coding:

    play music "audio/coding_in_snow_theme.mp3" fadein 1.5

    scene bg_police_interior

    python:
        _tier_name, _tier_info = get_coding_tier_info(stats.coding_skill)
        _tier_display = "{} | SKILL: {} | BASE: {} CZK | HOURLY: {}".format(
            _tier_name, _tier_info["range"], _tier_info["standard"], _tier_info["hourly"])
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
                "detail_text":    "FIXED",
                "card_hint":      "",
                "flavor_text":    "Take what your skill's worth right now.",
                "class_relevant": _is_bh,
            },
            {
                "label_name":     "coding_practice_puzzle",
                "title":          "PRACTICE PUZZLE",
                "accent":         _bh_accent,
                "cost_text":      "FREE",
                "effect_text":    "+ Coding",
                "detail_text":    "ROLL",
                "card_hint":      "Compile / Refactor / Algorithm",
                "flavor_text":    "Solve a function. Some stick.",
                "class_relevant": _is_bh,
            },
            {
                "label_name":     "coding_fiverr",
                "title":          "FIVERR LESSON",
                "accent":         _bh_accent,
                "cost_text":      "{:,} CZK".format(adjusted_cost(2500)),
                "effect_text":    "+ Coding",
                "detail_text":    "RANDOM",
                "card_hint":      "Compile / Refactor",
                "flavor_text":    "Someone in Mumbai who knows your stack.",
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
                "detail_text":    "BRANCHED · BIOHACKER",
                "card_hint":      "Racetam / FLModafinil",
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
                "detail_text":    "FIXED · PERMANENT",
                "card_hint":      "Production Push",
                "flavor_text":    _bc_flavor,
                "class_relevant": False,
                "locked":         _bc_done,
                "lock_text":      "Already enrolled. The buff is live.",
            })

    "You open the laptop. The apartment is quiet.\nThis is the only hour of the day that belongs entirely to you.\n\nCurrent tier: [_tier_display]"

    call screen activity_submenu(
        title       = "CODING — PICK A PATH",
        subtitle    = "The hour is yours. The keyboard does what you tell it to.",
        options     = _coding_options,
        back_label  = "select_activity",
    )


label coding_practice_puzzle:

    python:
        ## Pick puzzle by current skill bracket; track played puzzles to avoid repeats this run.
        if not hasattr(store, '_puzzles_solved'):
            store._puzzles_solved = []
        _pid = pick_puzzle_for_skill(stats.coding_skill, exclude=store._puzzles_solved)
        if _pid is None:
            renpy.say(None, "[[NOTHING NEW]] You've solved every puzzle you can find tonight. Get back to work tomorrow.")
            renpy.jump("activity_coding")
        _retries = diff_setting("minigame_retries", 1)
        puzzle_init(_pid, max_attempts=1 + _retries)

    "You open the editor. A coding challenge is waiting in your inbox.\n[PUZZLES[_pid]['spec']]"

    call screen coding_puzzle_screen

    python:
        _result = _return  # screen returned "pass" or "fail"
        _p = PUZZLES.get(_pid, {})

    if _result == "pass":
        python:
            _gain = _p.get("reward_coding", 10)
            ## Always-apply progression — solving the puzzle counts regardless of card choice.
            store._puzzles_solved.append(_pid)
            ## Pick a Logic-color card to OFFER on pass
            _logic_options = ["compile", "refactor", "algorithm"]
            _puzzle_card = __import__('random').choice(_logic_options)
            _outcome_str = "+{} CODING SKILL".format(_gain)

        "[[TESTS PASSED]] The compiler is silent. The function works."
        "You feel something shift. The pattern clicked."

        python:
            _took_puzzle = offer_card(_puzzle_card, "PUZZLE REWARD", pass_stats_text=_outcome_str)
            if not _took_puzzle:
                stats.increment_stats_coding_skill(_gain)
            show_outcome_panel(_took_puzzle, _puzzle_card, _outcome_str)

        pause
        hide screen outcome_panel

        python:
            activity_selected = True
        jump end_day

    else:
        python:
            stats.increment_stats_pcr_hatred(5)

        "[[TESTS FAILED]] The compiler is patient. The compiler is also unimpressed."
        "You stare at the screen. You close the laptop. You open it again. Nothing has changed."
        show screen outcome_panel("+5 PCR HATRED — frustration tax. The puzzle bested you tonight.")
        pause
        hide screen outcome_panel
        python:
            activity_selected = True
        jump end_day


label coding_work_for_money:

    python:
        _tier_name, _tier_info = get_coding_tier_info(stats.coding_skill)
        if _tier_name == "TIER 1":
            renpy.say(None, "[[TIER 1]] Still learning.\nYou can't code for money yet. Keep practicing and building tiny projects.\nUnlock paid work at 50 Coding Skill.")
            renpy.jump("activity_coding")
        else:
            _standard = _tier_info["standard"]
            _hourly   = _tier_info["hourly"]
            _earned   = _standard + (stats.coding_skill * _hourly)
            stats.increment_stats_value_money(_earned)
            activity_selected = True

    "[_tier_name] — [_tier_info['label']]\nYour current coding skill is [stats.coding_skill].\n\nCalculation: [_tier_info['standard']] + [stats.coding_skill] * [_tier_info['hourly']] = [_earned] CZK"
    show screen outcome_panel("+ {} CZK".format(_earned))
    pause
    hide screen outcome_panel
    jump end_day


label coding_fiverr:

    python:
        _fiverr_cost = adjusted_cost(2500)
        if not stats.try_spend_money(_fiverr_cost):
            renpy.say(None, "[[INSUFFICIENT FUNDS]] You need {:,} CZK. Current: {:,} CZK.".format(_fiverr_cost, stats.available_money))
            renpy.jump("activity_coding")

    python:
        ## BIOHACKER perk: always gets the top-tier tutor
        if stats.player_class == "biohacker":
            _roll = 100
        else:
            _roll = __import__('random').randint(1, 100)
        ## Pending coding gain — applied only on PASS.
        if _roll <= 65:
            _fiverr_gain = 10
            _fiverr_card = "compile"
            _ftext = "You jump on a call with a mid-level developer from Fiverr.\nHe's practical. He shows you how to structure your files and fixes bad habits."
            _foutcome = "- {} CZK, +10 CODING SKILLS".format(_fiverr_cost)
        elif _roll <= 90:
            _fiverr_gain = 15
            _fiverr_card = "compile"
            _ftext = "You luck out. Your tutor is sharp as hell.\nThey explain OOP in a way that finally clicks with your brain."
            _foutcome = "- {} CZK, +15 CODING SKILLS".format(_fiverr_cost)
        else:
            _fiverr_gain = 25
            _fiverr_card = "refactor"
            _ftext = "You accidentally booked a beast. Senior dev, ten years in the field.\nCode review, patterns, mental models. This was a paradigm shift."
            _foutcome = "- {} CZK, +25 CODING SKILLS{}".format(_fiverr_cost, " [[BIOHACKER PERK]]" if stats.player_class == "biohacker" else "")

    "[_ftext]"

    python:
        _took_fiverr = offer_card(_fiverr_card, "FIVERR", pass_stats_text=_foutcome)
        if not _took_fiverr:
            stats.increment_stats_coding_skill(_fiverr_gain)
        show_outcome_panel(_took_fiverr, _fiverr_card, _foutcome)

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
        "YES — Sign the contract.":
            python:
                if not stats.try_spend_money(_bc_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS]] You need {:,} CZK. That is a lot of money. Maybe stick to free docs for now?".format(_bc_cost))
                    renpy.jump("activity_coding")
            "You sign a contract and pay for an on-line Python bootcamp.\nDeadlines, assignments, code reviews. The full package.\nThis is no longer a hobby. This is a commitment."
            "Six weeks in, the Friday capstone hits. You ship a working REST API in a single sitting. The instructor pings you privately: 'You're ready to push to production.'"

            $ python_bootcamp = True

            python:
                ## Locked-in reward of paying 35k: the perm buff. The card-or-stats
                ## trade is the BONUS choice on top — a substantive rare card OR
                ## +25 coding skill pumped immediately into the run.
                _bc_outcome = "- {:,} CZK, [[BOOTCAMP BUFF ACTIVATED]] +5 Coding/night, +25 CODING".format(_bc_cost)
                _took_bc = offer_card("production_push", "BOOTCAMP", pass_stats_text=_bc_outcome)
                if not _took_bc:
                    stats.increment_stats_coding_skill(25)
                show_outcome_panel(_took_bc, "production_push", _bc_outcome)

            pause
            hide screen outcome_panel
            python:
                activity_selected = True
            jump end_day

        "NO — I changed my mind.":
            "You step back. It's too much money right now."
            jump activity_coding


label coding_bootcamp_de:

    python:
        _bc_cost = adjusted_cost(28000)
        _bc_cost_str = "{:,}".format(_bc_cost)

    "The bootcamp costs [_bc_cost_str] CZK. Your emotional intelligence tells you this course is worth more than it costs."
    "You've already mapped the instructor's communication style. You will extract maximum value."

    menu:
        "YES — Sign the contract.":
            python:
                if not stats.try_spend_money(_bc_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS]] You need {:,} CZK. Current: {:,} CZK.".format(_bc_cost, stats.available_money))
                    renpy.jump("activity_coding")
            "You sign the contract."
            "While others grind through the curriculum mechanically, you read your cohort."
            "You know which questions to ask. You know when to stay late and when the instructor is in a generous mood."
            "The bootcamp that costs others 35k costs you 28k. You extracted a 20%% discount through competence."
            "Six weeks in, the Friday capstone hits. You ship a clean REST API while the rest of the cohort is still wrestling with imports. The instructor doesn't say it, but you already read it on her face: 'You're ready to push to production.'"

            $ python_bootcamp = True

            python:
                _bc_outcome = "- {:,} CZK [[DARK EMPATH DISCOUNT]], [[BOOTCAMP BUFF ACTIVATED]] +5 Coding/night, +25 CODING".format(_bc_cost)
                _took_bc = offer_card("production_push", "BOOTCAMP", pass_stats_text=_bc_outcome)
                if not _took_bc:
                    stats.increment_stats_coding_skill(25)
                show_outcome_panel(_took_bc, "production_push", _bc_outcome)

            pause
            hide screen outcome_panel
            python:
                activity_selected = True
            jump end_day

        "NO — I changed my mind.":
            "You step back."
            jump activity_coding


## ---------------------------------------------------------------------------
## ACTIVITY: NIGHT SHIFT PATROL
## ---------------------------------------------------------------------------

label activity_night_shift:

    scene bg_police_interior

    "You volunteer for the extra night shift."
    "3,000 CZK for 8 more hours in uniform."
    "You don't need the money. But you do need the distraction."

    menu:
        "TAKE THE SHIFT — +3,000 CZK, certain +15 PCR HATRED. (+ [[CARD]] BACKUP)":
            python:
                stats.increment_stats_value_money(3000)
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
                    _ns_bonus = "\n[[NIGHT BONUS]]: Dead quiet shift. You studied Python for 4 hours. +8 Coding, -5 Hatred."
                elif _ns_roll <= 40:
                    stats.increment_stats_value_money(1500)
                    _ns_bonus = "\n[[NIGHT BONUS]]: Helped with an accident. Extra callout pay. +1,500 CZK."
                elif _ns_roll <= 60:
                    stats.increment_stats_pcr_hatred(10)
                    _ns_extra_card = "chain_of_command"
                    _ns_bonus = "\n[[NIGHT PENALTY]]: Paperwork from an arrest took until 6AM. +10 PCR HATRED."
                else:
                    _ns_bonus = ""

            "You work through the night."
            "The city is different after midnight — quieter, stranger, more honest."
            "You check your watch every hour."
            "[_ns_bonus]"
            show screen outcome_panel("+3,000 CZK, +15 PCR HATRED.{}".format(_ns_bonus))
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
## END DAY
## ---------------------------------------------------------------------------

label end_day:
    hide screen day_calendar

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

    stop music fadeout 1.0

    ## Night cycle
    "END OF DAY [day_cycle.current_day]"

    python:
        # Base nightly hatred scales with difficulty (Easy 4, Hard 5, Insane 6, Ultra 7-8)
        _nightly_base = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
        stats.increment_stats_pcr_hatred(_nightly_base)
        if python_bootcamp:
            stats.increment_stats_coding_skill(5) # bootcamp buff

        # Advance day
        day_cycle.next_day()
        activity_selected = False
        # Reset gym streak if player didn't go to gym today
        if not getattr(store, 'gym_day', False):
            store.gym_streak = 0
        store.gym_day = False

    "Beginning DAY [day_cycle.current_day]..."

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

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

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
    show screen outcome_panel("+ {} CZK".format(_sal))
    pause
    hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## ACTIVITY: NOOTROPICS LAB (Biohacker only)
## ---------------------------------------------------------------------------

label activity_nootropics:

    play music "audio/coding_in_snow_theme.mp3" fadein 1.0
    scene bg_police_interior

    python:
        _dep_warning = ""
        if nootropic_dependency:
            _dep_warning = "\n\n[[DEPENDENCY ACTIVE]] — Skipping a dose costs -20 Coding, +20 Hatred."

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
            _hint = ""
            if _tn >= 5:
                _hint = "FLModafinil"
            elif _tn >= 3:
                _hint = "Racetam"
            _noot_options.append({
                "label_name":     "_apply_noot_t{}".format(_tn),
                "title":          _NOOT_TITLES[_tn],
                "accent":         class_accent_color("biohacker"),
                "cost_text":      "{:,} CZK".format(adjusted_cost(_ti["cost"])),
                "effect_text":    _eff,
                "detail_text":    "FIXED" + (" · CRASH" if _ti.get("crash_coding") or _ti.get("crash_hatred") else ""),
                "card_hint":      _hint,
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
            renpy.say(None, "[[INSUFFICIENT FUNDS]] You need {:,} CZK. Current: {:,} CZK.".format(
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
        "[[NEXT-DAY EFFECT]] [_crash_str]"

    ## Tier unlock announcement
    if _unlock == "T2_UNLOCKED":
        "\nYou've been reading late at night. The forums mention something stronger than supplements.\n[[NEW TIER UNLOCKED: Cognitive Stack]]"

    if _unlock == "T3_UNLOCKED":
        "\nYou've gone deeper. The r/nootropics rabbit hole has no bottom.\n[[NEW TIER UNLOCKED: Racetams]]"

    if _unlock == "T4_UNLOCKED":
        "\nThere's a gray market if you know where to look. You do.\n[[NEW TIER UNLOCKED: Peptides]]"

    if _unlock == "T5_UNLOCKED":
        "\nYou've been deep enough in the forums to find the name. CRL-40,940. Eugeroic. Wakefulness agent.\nThe supplier is three steps removed from anything legal.\n[[NEW TIER UNLOCKED: FLModafinil (CRL-40,940)]]"

    ## Dependency warning at 2 T5 uses (one before threshold)
    python:
        _dep_warn = nootropic_uses[4] == 1 and _tier == 5

    if _dep_warn:
        "[[WARNING]] One more dose and your baseline changes permanently.\nFLModafinil (CRL-40,940) dependency triggers at 2 total uses."

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
                "detail_text":    "FIXED",
                "card_hint":      _cr_card.replace("_", " ").upper(),
                "flavor_text":    "Subtle. The card may stick.",
                "class_relevant": True,
            },
            {
                "label_name":     "cold_read_observe",
                "title":          "OBSERVATION HOUR",
                "accent":         _de_accent,
                "cost_text":      "FREE",
                "effect_text":    "-20 Hatred, +1 PROFILE",
                "detail_text":    "FIXED",
                "card_hint":      "",
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

    python:
        _took_cr = offer_card(_cr_card, "COLD READ", pass_stats_text=_cr_outcome)
        if not _took_cr:
            stats.increment_stats_pcr_hatred(_cr_pending_hatred)
            if _cr_pending_coding:
                stats.increment_stats_coding_skill(_cr_pending_coding)
        show_outcome_panel(_took_cr, _cr_card, _cr_outcome)

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
    show jb worried at char_left

    "[[CRISIS EVENT — BODYBUILDER]]"
    "It happened at the gym."
    "A man in a Levi's jacket made a joke about cops. Something about donuts."
    "You don't remember deciding to react. You just did."
    "You grabbed a 20kg plate off the rack and slammed it into the floor next to him."
    "The crack echoed through the whole building. Everyone froze."
    "He's still standing there, pale as concrete, phone already out."
    "The gym manager has appeared. The word 'police report' has been used."
    "Your hands are still shaking."

    menu:
        "OWN IT — Apologize. Pay for the plate. Leave with your head up. (-2,000 CZK, -20 Hatred)":
            python:
                stats.increment_stats_pcr_hatred(-20)
                stats.increment_stats_value_money(-2000)
            "You uncurl your fists."
            jb "'I'm sorry. I'll pay for the damage. You didn't deserve that.'"
            "The manager nods slowly. The man with the phone doesn't look convinced, but he pockets it."
            "You drive home. The rage is gone."
            "What's left underneath it is quieter. And more honest."
            "Your body was trying to tell you something. It's been trying for weeks."
            show screen outcome_panel("-2,000 CZK, -20 PCR HATRED [BODYBUILDER CRISIS: you faced it].")
            pause
            hide screen outcome_panel

        "STORM OUT — You don't have the words. Just leave before it gets worse. (+5 Hatred)":
            python:
                stats.increment_stats_pcr_hatred(5)
            "You walk to the exit."
            "Nobody stops you."
            "In the car park you sit in your car for 25 minutes with the engine off."
            "The anger has burned itself hollow."
            "Nothing is resolved. But nothing escalated either."
            "You exist in a grey zone between dangerous and fine."
            show screen outcome_panel("+5 PCR HATRED [BODYBUILDER CRISIS: unresolved].")
            pause
            hide screen outcome_panel

    return


label crisis_event_dark_empath:

    play music "audio/tension_theme.mp3" fadein 1.0
    scene bg_police_interior
    show jb bored at char_left

    "[[CRISIS EVENT — DARK EMPATH]]"
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
        "SIT WITH IT — The emptiness is data. Read it.  (-15 Hatred)":
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
            show screen outcome_panel("-15 PCR HATRED, +3 CODING [DARK EMPATH CRISIS: emptiness as clarity].")
            pause
            hide screen outcome_panel

        "DISSOCIATE — Turn the null state into armor. Work the shift like a machine. (+3 Hatred)":
            python:
                stats.increment_stats_pcr_hatred(3)
            "You do exactly what you're supposed to do."
            "You process reports. You respond to calls. You nod at the right moments."
            "Nobody notices. You are performing normalcy from muscle memory."
            "The void persists underneath, but it's insulated now."
            "This is fine. This is sustainable. You've been here before."
            "You haven't."
            show screen outcome_panel("+3 PCR HATRED [DARK EMPATH CRISIS: functional but unresolved].")
            pause
            hide screen outcome_panel

    return


label crisis_event_biohacker:

    play music "audio/tension_theme.mp3" fadein 1.0
    scene bg_police_interior
    show jb worried at char_left

    "[[CRISIS EVENT — BIOHACKER]]"
    "Your resting heart rate is 140 BPM."
    "You know this because you checked. Twice."
    "Your hands have a micro-tremor. Your focus, which is usually a narrow laser, is scattering."
    "You've been running too hot for too long."
    "The stack, the stress, the late-night study sessions, the shift schedules."
    "Your body has quietly filed a formal complaint."
    "You are sitting in the break room pretending to drink coffee."
    "Your biosignals are telling you to stop."

    menu:
        "COLD PROTOCOL — Full system halt. Ice water, no compounds, sleep early. (-25 Hatred, -5 Coding today)":
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
            show screen outcome_panel("-25 PCR HATRED, -5 CODING (rest tax) [BIOHACKER CRISIS: hard reset successful].")
            pause
            hide screen outcome_panel

        "LOG AND CONTINUE — Symptoms are data. Biohackers don't panic.":
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
            show screen outcome_panel(_bh_outcome)
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## RANDOM EVENT GATE
## ---------------------------------------------------------------------------

label random_event_check:

    ## Random event pool — events removed once triggered (using a persistent list)
    python:
        if not hasattr(store, 'random_event_pool'):
            store.random_event_pool = [
                "re_israeli_developer",
                "re_nightmare_wolf",
                "re_civilian_small_talk",
                "re_admin_mistake",
                "re_overtime_offer",
                "re_birthday_gift",
                "re_corpse_in_care_home",
                "re_forgotten_usb",
                "re_turkish_fraud",
                "re_printer_incident",
                "re_citizen_czechoslovakia",
                "re_paperwork_overload",
                "re_dispatch_blue_screen",
                "re_tech_bro_speeding",
                ## New events (PROMPT 3)
                "re_the_informant",
                "re_the_evaluation",
                "re_suicide_call",
                "re_retirement_party",
                "re_coding_interview",
                ## re_the_bribe excluded — hardcoded to Day 6
                "re_system_update",
            ]

    python:
        ## Class arc takes priority over random pool — fires the next stage if
        ## the day window + class match. Returns None otherwise.
        _class_arc = class_arc_check()
        if _class_arc:
            renpy.call(_class_arc)
            ## Restore ambient music after class arc
            if stats.pcr_hatred >= 75:
                renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
            else:
                renpy.music.play("audio/enter_the_code_theme.mp3", fadein=1.5)
            ## Apply nightly cycle and advance day (mirrors random event behaviour)
            _re_nightly = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
            stats.increment_stats_pcr_hatred(_re_nightly)
            if python_bootcamp:
                stats.increment_stats_coding_skill(5)
            day_cycle.next_day()
            renpy.jump("random_event_check_done")

        if store.random_event_pool:
            _chosen = __import__('random').choice(store.random_event_pool)
            store.random_event_pool.remove(_chosen)
            renpy.call(_chosen)
            ## Restore ambient music after random event
            if stats.pcr_hatred >= 75:
                renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
            else:
                renpy.music.play("audio/enter_the_code_theme.mp3", fadein=1.5)
            # Random events consume a day — apply the same nightly cycle as do_end_day.
            _re_nightly = int(round(5 * diff_setting("nightly_hatred_mult", 1.0)))
            stats.increment_stats_pcr_hatred(_re_nightly)
            if python_bootcamp:
                stats.increment_stats_coding_skill(5)
            day_cycle.next_day()

label random_event_check_done:
    return
