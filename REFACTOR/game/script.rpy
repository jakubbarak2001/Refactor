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

    ## Title card
    "REFACTOR"
    "A game about a Czech police officer who wants to quit the force and become a developer."
    "You have 30 days. Code or break."

    pause 1.0

    ## Difficulty selection
    call difficulty_selection

    ## Character class selection
    call character_class_selection

    ## Arc I - Car Incident (Day 1)
    call car_incident

    ## Main 30-day loop
    call main_loop

    return


## ---------------------------------------------------------------------------
## DIFFICULTY SELECTION
## ---------------------------------------------------------------------------

label difficulty_selection:

    scene bg_black

    "SELECT DIFFICULTY"
    "Your starting stats depend on this choice."

    menu:
        "EASY — Money: 55,000 CZK | Coding: 10 | Hatred: 15":
            $ init_game("easy")
            "EASY mode selected.\nYou have a solid start. Don't waste it."

        "HARD — Money: 35,000 CZK | Coding: 5 | Hatred: 25":
            $ init_game("hard")
            "HARD mode selected.\nThe margins are tighter. Every decision matters."

        "INSANE — Money: 20,000 CZK | Coding: 0 | Hatred: 35":
            $ init_game("insane")
            "INSANE mode selected.\nYou have nothing. Absolute nothing. Good luck."

    "Starting Stats:"
    "[stats.available_money] CZK | Coding: [stats.coding_skill] | Hatred: [stats.pcr_hatred]/100"

    return


## ---------------------------------------------------------------------------
## CHARACTER CLASS SELECTION
## ---------------------------------------------------------------------------

label character_class_selection:

    scene bg_black

    "Before the grind begins — who are you, JB?"
    "Your class is permanent. Choose carefully."

    call screen class_selection_screen

    ## Apply starting bonuses based on class choice
    python:
        apply_class_bonuses(stats)

    python:
        if stats.player_class == "bodybuilder":
            _class_msg = "BODYBUILDER selected.\nEvery rep is a rep closer to freedom.\n[-5 Coding Skill applied as starting passive]"
        elif stats.player_class == "dark_empath":
            _class_msg = "DARK EMPATH selected.\nYou see through people. That is both your weapon and your curse.\n[-10 Police Hatred applied as starting passive]"
        elif stats.player_class == "biohacker":
            _class_msg = "BIOHACKER selected.\nYour body is a machine. Let's see how far you can push it.\n[+10 Coding Skill | +500 CZK/night BTC income applied]"
        else:
            _class_msg = "Class selected."

    "[_class_msg]"

    return


## ---------------------------------------------------------------------------
## MAIN 30-DAY LOOP
## ---------------------------------------------------------------------------

label main_loop:

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
            if current_day >= 25:
                renpy.jump("burnout_ending")
            else:
                renpy.jump("mental_breakdown_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")
        # Perfect ending check — Escape Artist
        if current_day >= 29 and stats.coding_skill >= 150 and stats.available_money >= 150000 and stats.pcr_hatred <= 30:
            renpy.jump("escape_artist_ending")

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
            if day_cycle.current_day >= 25:
                renpy.jump("burnout_ending")
            else:
                renpy.jump("mental_breakdown_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")

    show screen stats_bar

    ## Two different menus depending on whether the day's activity is done
    python:
        if activity_selected:
            renpy.jump("daily_menu_activity_done")
        else:
            renpy.jump("daily_menu_activity_pending")


label daily_menu_activity_done:
    menu:
        "Show Stats":
            jump show_stats
        "Achievements":
            jump show_achievements
        "Show Contacts":
            jump show_contacts
        "End the Day":
            jump end_day


label daily_menu_activity_pending:
    menu:
        "Show Stats":
            jump show_stats
        "Achievements":
            jump show_achievements
        "Select Activity":
            jump select_activity
        "Show Contacts":
            jump show_contacts
        "End the Day":
            jump end_day


label show_stats:
    call screen full_stats_screen
    jump daily_menu


label show_achievements:
    call screen achievements_screen
    jump daily_menu


label show_contacts:
    "You open your phone contact list."
    "1. Martin (ex-colleague)\n2. Paul Goodman (lawyer)\n3. Colonel (your boss)\n\n(Contacts are not interactive in this version.)"
    jump daily_menu


label select_activity:

    python:
        if activity_selected:
            renpy.jump("daily_menu")

    "What will you do today? Choose wisely — only one activity per day."

    menu:
        "GYM — Lower your stress. Costs 400 CZK.":
            jump activity_gym

        "THERAPY — Reduce hatred by 25. Costs 1,500 CZK." if stats.player_class != "dark_empath":
            jump activity_therapy

        "COLD READ — Process through observation. (-20 Hatred)  [[DARK EMPATH]" if stats.player_class == "dark_empath":
            jump activity_cold_read

        "BOUNCER NIGHT SHIFT — Earn money with risk.":
            jump activity_bouncer

        "CODING — Practice Python and improve your skills.":
            jump activity_coding

        "NIGHT SHIFT PATROL — Work extra hours. Earn 3,000 CZK. Always costs Hatred.":
            jump activity_night_shift

        "Return to menu.":
            jump daily_menu


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

    "You head to the gym with your trainer.\nTraining will help you relax, but it will cost 400 CZK."
    python:
        _streak_msg = ""
        if store.gym_streak >= 1:
            _streak_msg = "\n[STREAK: {} days in a row — extra -{} Hatred bonus]".format(store.gym_streak, _streak_bonus)
    "Gym attendance: [store.gym_streak] day streak.[_streak_msg]"

    menu:
        "PAY 400 CZK — We go gym! (33/33/33%% chance for different outcomes)":
            python:
                if not stats.try_spend_money(400):
                    renpy.say(None, "[[INSUFFICIENT FUNDS]] You check your wallet... you don't even have 400 CZK for the gym entry.")
                    renpy.jump("select_activity")
                else:
                    _roll = __import__('random').randint(1, 3)

            python:
                _bb_bonus = 5 if stats.player_class == "bodybuilder" else 0
                store.gym_streak += 1
                if store.gym_streak >= 5:
                    unlock_achievement("gym_rat")
                _streak_add = min(store.gym_streak * 3, 15)
                if _roll == 1:
                    _total_red = 25 + _bb_bonus + _streak_add
                    stats.increment_stats_pcr_hatred(-_total_red)
                    _gym_text = "Something clicks today.\nYou hit a new personal record and for about 90 minutes the Colonel doesn't exist, the station doesn't exist, the paperwork doesn't exist.\nThere is only the bar, the weight, and the fact that your body does exactly what you tell it to.\nYou drive home in silence but it's the good kind of silence."
                    _gym_outcome = "- 400 CZK, -{} PCR HATRED{}{}".format(_total_red, " [BODYBUILDER]" if _bb_bonus else "", " [STREAK x{}]".format(store.gym_streak) if _streak_add else "")
                elif _roll == 2:
                    _total_red = 15 + _bb_bonus + _streak_add
                    stats.increment_stats_pcr_hatred(-_total_red)
                    _gym_text = "Solid session. Nothing transcendent, but you showed up and that's most of it.\nBy the last set your head is quieter than it was this morning.\nYou eat a chicken breast in your car in the gym parking lot and feel no shame whatsoever."
                    _gym_outcome = "- 400 CZK, -{} PCR HATRED{}{}".format(_total_red, " [BODYBUILDER]" if _bb_bonus else "", " [STREAK x{}]".format(store.gym_streak) if _streak_add else "")
                else:
                    _total_red = 10 + _bb_bonus + _streak_add
                    stats.increment_stats_pcr_hatred(-_total_red)
                    _gym_text = "You go through the motions. Every rep feels like lifting a filing cabinet full of quarterly reports.\nYour trainer gives you a look that says he's seen more motivated people at DMVs.\nBut you finish. You paid 400 CZK. You are slightly less likely to flip a desk today."
                    _gym_outcome = "- 400 CZK, -{} PCR HATRED{}{}".format(_total_red, " [BODYBUILDER]" if _bb_bonus else "", " [STREAK x{}]".format(store.gym_streak) if _streak_add else "")

            "[_gym_text]"
            show screen outcome_panel(_gym_outcome)
            pause
            hide screen outcome_panel
            python:
                activity_selected = True
                store.gym_day = True
            jump daily_menu

        "Return to menu.":
            jump daily_menu


## ---------------------------------------------------------------------------
## ACTIVITY: THERAPY
## ---------------------------------------------------------------------------

label activity_therapy:

    scene bg_police_interior

    "You've selected to go to therapy.\nSomething that might actually help you lower your stress.\nPaying for a therapist is expensive, but the results are worth it."

    menu:
        "PAY 1500 CZK — Get help. (-25 PCR HATRED)":
            python:
                if not stats.try_spend_money(1500):
                    renpy.say(None, "[[INSUFFICIENT FUNDS]] Therapy is a luxury you can't afford right now. You need 1500 CZK.")
                    renpy.jump("select_activity")
                else:
                    stats.increment_stats_pcr_hatred(-25)

            "Her office smells like books and mild candles. You sit down and she asks: 'So. How was the week?'"
            "You open your mouth to say 'fine' — the standard reflex — and instead talk for 40 minutes without stopping."
            "She takes notes. She doesn't flinch at the parts you expected her to flinch at."
            "At the end she says: 'You know the job isn't the problem. The job is just where the problem lives right now.'"
            "You sit with that for a moment."
            "You don't feel fixed. But you feel like something was put into words that previously just sat in your chest like a stone."
            python:
                ## Every 2nd therapy session grants the SELF-AWARE buff (ai_paperwork_buff reused)
                if not hasattr(store, 'therapy_count'):
                    store.therapy_count = 0
                store.therapy_count += 1
                _therapy_outcome = "- 1500 CZK, -25 PCR HATRED"
                if store.therapy_count % 2 == 0:
                    stats.ai_paperwork_buff = True
                    _therapy_outcome += " + [[SELF-AWARE BUFF ACTIVATED]] (-5 Hatred/night)"

            show screen outcome_panel(_therapy_outcome)
            pause
            hide screen outcome_panel
            python:
                activity_selected = True
            jump daily_menu

        "Return to menu.":
            jump daily_menu


## ---------------------------------------------------------------------------
## ACTIVITY: BOUNCER
## ---------------------------------------------------------------------------

label activity_bouncer:

    scene bg_police_interior

    "You were offered to work as a bouncer in either a local night club or a strip bar.\n\nNight club: Generally safe, but some risk.\nStrip bar: VERY RISKY, but VERY HIGH reward."

    menu:
        "WORK AT A NIGHT CLUB — [[70/20/10%%] outcomes":
            jump bouncer_night_club

        "WORK AT A STRIP BAR — [[5/20/50/20/5%%] outcomes (RISKY!)":
            jump bouncer_strip_bar

        "Return to menu.":
            jump daily_menu


label bouncer_night_club:

    python:
        _roll = __import__('random').randint(1, 100)
        _bb_cash = 1500 if stats.player_class == "bodybuilder" else 0
        if _roll <= 70:
            stats.increment_stats_pcr_hatred(10)
            stats.increment_stats_value_money(4000 + _bb_cash)
            _btext = "Uneventful. You stand in a doorway for six hours, nodding at people who are happier than you.\nA man in a pink shirt calls you 'big guy'. You do not react.\nAt 3 AM you calculate exactly how many more shifts like this you'd need to quit forever.\nThe number is getting smaller."
            _boutcome = "+ {} CZK, +10 PCR HATRED{}".format(4000 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")
        elif _roll <= 90:
            stats.increment_stats_value_money(7500 + _bb_cash)
            stats.increment_stats_pcr_hatred(-10)
            _btext = "Rare night. A group of regulars tips heavy, the manager actually notices your work, and nobody throws up on anyone.\nDriving home at 4 AM, windows down, you think: 'If this was my real job I would hate it slightly less.'\nThat is the closest thing to joy you have felt all week."
            _boutcome = "+ {} CZK, -10 PCR HATRED{}".format(7500 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")
        else:
            stats.increment_stats_pcr_hatred(20)
            stats.increment_stats_value_money(4000 + _bb_cash)
            _btext = "Two drunk idiots fight over the same woman who is clearly interested in neither of them.\nYou step in. One of them recognizes you — 'TO JE PŘECE POLDA!' — and now his phone is out.\nYour colleagues see the video the next morning. The group chat has not stopped since.\nSergeant Kovář sends you a thumbs up emoji. You want to die."
            _boutcome = "+ {} CZK, +20 PCR HATRED{}".format(4000 + _bb_cash, " [BODYBUILDER BONUS]" if _bb_cash else "")

    "[_btext]"
    show screen outcome_panel(_boutcome)
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump daily_menu


label bouncer_strip_bar:

    python:
        _roll = __import__('random').randint(1, 100)
        _bb_cash = 1500 if stats.player_class == "bodybuilder" else 0
        _bb_tag = " [BODYBUILDER BONUS]" if _bb_cash else ""
        if _roll <= 5:
            stats.increment_stats_value_money(35000 + _bb_cash)
            stats.increment_stats_pcr_hatred(-15)
            _btext = "A famous regular shows up drunk and paranoid. Two guys try to drag him outside, but you intervene with textbook precision.\nYour boss calls you to the office and slides an envelope across the table.\n'Not many can do what you did tonight.'"
            _boutcome = "+{} CZK, -15 PCR HATRED{}".format(35000 + _bb_cash, _bb_tag)
        elif _roll <= 25:
            stats.increment_stats_value_money(12500 + _bb_cash)
            stats.increment_stats_coding_skill(2)
            _btext = "Steady crowds, few arguments, no real threats. You handle everything with routine precision.\nYou even use downtime to mentally rehearse OOP concepts and class hierarchies — weirdly effective."
            _boutcome = "+{} CZK, +2 CODING SKILLS{}".format(12500 + _bb_cash, _bb_tag)
        elif _roll <= 75:
            stats.increment_stats_value_money(6500 + _bb_cash)
            stats.increment_stats_pcr_hatred(5)
            _btext = "You stand in a corridor that smells like vodka Red Bull and bad decisions for four hours.\nNothing interesting happens. One person cries in the bathroom. You pretend not to notice.\nYou pretend not to notice a lot of things in this job.\nAt least the envelope is solid."
            _boutcome = "+{} CZK, +5 PCR HATRED{}".format(6500 + _bb_cash, _bb_tag)
        elif _roll <= 95:
            stats.increment_stats_value_money(1000 + _bb_cash)
            stats.increment_stats_pcr_hatred(25)
            _btext = "A fight breaks out inside. You break it up, but one participant recognizes your face from the force.\n'Ty vole, to je POLDA!' Your boss gives you only a partial payout."
            _boutcome = "+{} CZK, +25 PCR HATRED{}".format(1000 + _bb_cash, _bb_tag)
        else:
            stats.increment_stats_value_money(-12500 + _bb_cash)
            stats.increment_stats_pcr_hatred(35)
            stats.increment_stats_coding_skill(-5)
            _btext = "You turn your back for one second — enough for a coked-up idiot to drive a vodka bottle into your skull.\nPolice arrives and discovers you're moonlighting illegally. Your boss is furious."
            _boutcome = "{} CZK, +35 PCR HATRED, -5 CODING SKILLS{}".format(-12500 + _bb_cash, _bb_tag)

    "[_btext]"
    show screen outcome_panel(_boutcome)
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump daily_menu


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

    "You open the laptop. The apartment is quiet.\nThis is the only hour of the day that belongs entirely to you.\n\nCurrent tier: [_tier_display]"

    menu:
        "CODE FOR MONEY — Earn CZK based on your tier.":
            jump coding_work_for_money

        "FIVERR LESSON — Pay 2,500 CZK for a study session.":
            jump coding_fiverr

        "JOIN ONLINE BOOTCAMP — Pay 28,000 CZK. Unlocks +5 coding/night.  [[DARK EMPATH DISCOUNT]" if not python_bootcamp and stats.player_class == "dark_empath":
            jump coding_bootcamp_de

        "JOIN ONLINE BOOTCAMP — Pay 35,000 CZK. Unlocks +5 coding/night." if not python_bootcamp and stats.player_class not in ["biohacker", "dark_empath"]:
            jump coding_bootcamp

        "NOOTROPICS LAB — Optimise your cognition.  [[BIOHACKER ONLY]" if stats.player_class == "biohacker":
            jump activity_nootropics

        "Return to menu.":
            jump daily_menu


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
    jump daily_menu


label coding_fiverr:

    python:
        if not stats.try_spend_money(2500):
            renpy.say(None, "[[INSUFFICIENT FUNDS]] You need 2500 CZK. Current: {} CZK.".format(stats.available_money))
            renpy.jump("activity_coding")

    python:
        ## BIOHACKER perk: always gets the top-tier tutor
        if stats.player_class == "biohacker":
            _roll = 100
        else:
            _roll = __import__('random').randint(1, 100)
        if _roll <= 65:
            stats.increment_stats_coding_skill(10)
            _ftext = "You jump on a call with a mid-level developer from Fiverr.\nHe's practical. He shows you how to structure your files and fixes bad habits."
            _foutcome = "- 2500 CZK, +10 CODING SKILLS"
        elif _roll <= 90:
            stats.increment_stats_coding_skill(15)
            _ftext = "You luck out. Your tutor is sharp as hell.\nThey explain OOP in a way that finally clicks with your brain."
            _foutcome = "- 2500 CZK, +15 CODING SKILLS"
        else:
            stats.increment_stats_coding_skill(25)
            _ftext = "You accidentally booked a beast. Senior dev, ten years in the field.\nCode review, patterns, mental models. This was a paradigm shift."
            _foutcome = "- 2500 CZK, +25 CODING SKILLS{}".format(" [BIOHACKER PERK]" if stats.player_class == "biohacker" else "")

    "[_ftext]"
    show screen outcome_panel(_foutcome)
    pause
    hide screen outcome_panel
    python:
        activity_selected = True
    jump daily_menu


label coding_bootcamp:

    python:
        if stats.available_money < 35000:
            renpy.say(None, "[[INSUFFICIENT FUNDS]] You need 35000 CZK. That is a lot of money. Maybe stick to free docs for now?")
            renpy.jump("activity_coding")

    "The bootcamp costs 35,000 CZK. This is a massive investment.\nAre you sure you want to sign the contract?"

    menu:
        "YES — Sign the contract.":
            $ stats.try_spend_money(35000)
            "You sign a contract and pay for an on-line Python bootcamp.\nDeadlines, assignments, code reviews. The full package.\nThis is no longer a hobby. This is a commitment."
            show screen outcome_panel("- 35000 CZK, [[BOOTCAMP BUFF ACTIVATED]] +5 Coding/night")
            pause
            hide screen outcome_panel
            $ python_bootcamp = True
            python:
                activity_selected = True
            jump daily_menu

        "NO — I changed my mind.":
            "You step back. It's too much money right now."
            jump activity_coding


label coding_bootcamp_de:

    python:
        if stats.available_money < 28000:
            renpy.say(None, "[[INSUFFICIENT FUNDS]] You need 28,000 CZK. Current: {} CZK.".format(stats.available_money))
            renpy.jump("activity_coding")

    "The bootcamp costs 28,000 CZK. Your emotional intelligence tells you this course is worth more than it costs."
    "You've already mapped the instructor's communication style. You will extract maximum value."

    menu:
        "YES — Sign the contract.":
            $ stats.try_spend_money(28000)
            "You sign the contract."
            "While others grind through the curriculum mechanically, you read your cohort."
            "You know which questions to ask. You know when to stay late and when the instructor is in a generous mood."
            "The bootcamp that costs others 35k costs you 28k. You extracted a 20%% discount through competence."
            show screen outcome_panel("- 28,000 CZK [[DARK EMPATH DISCOUNT]], [[BOOTCAMP BUFF ACTIVATED]] +5 Coding/night")
            pause
            hide screen outcome_panel
            $ python_bootcamp = True
            python:
                activity_selected = True
            jump daily_menu

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
        "TAKE THE SHIFT — +3,000 CZK, certain +15 PCR HATRED.":
            python:
                stats.increment_stats_value_money(3000)
                stats.increment_stats_pcr_hatred(15)

                ## Random chance for a coding opportunity or incident during night shift
                _ns_roll = __import__('random').randint(1, 100)

            python:
                if _ns_roll <= 20:
                    stats.increment_stats_coding_skill(8)
                    stats.increment_stats_pcr_hatred(-5)
                    _ns_bonus = "\n[[NIGHT BONUS]]: Dead quiet shift. You studied Python for 4 hours. +8 Coding, -5 Hatred."
                elif _ns_roll <= 40:
                    stats.increment_stats_value_money(1500)
                    _ns_bonus = "\n[[NIGHT BONUS]]: Helped with an accident. Extra callout pay. +1,500 CZK."
                elif _ns_roll <= 60:
                    stats.increment_stats_pcr_hatred(10)
                    _ns_bonus = "\n[[NIGHT PENALTY]]: Paperwork from an arrest took until 6AM. +10 PCR HATRED."
                else:
                    _ns_bonus = ""

            "You work through the night."
            "The city is different after midnight — quieter, stranger, more honest."
            "You check your watch every hour."
            "[_ns_bonus]"
            show screen outcome_panel("+3,000 CZK, +15 PCR HATRED (Another night traded for money). {}".format(_ns_bonus))
            pause
            hide screen outcome_panel
            python:
                activity_selected = True
            jump daily_menu

        "Return to menu.":
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

    stop music fadeout 1.0

    ## Night cycle
    "END OF DAY [day_cycle.current_day]"

    python:
        # Apply nightly passives
        stats.increment_stats_pcr_hatred(5)       # base +5 hatred per night
        if python_bootcamp:
            stats.increment_stats_coding_skill(5) # bootcamp buff
        if stats.ai_paperwork_buff:
            stats.increment_stats_pcr_hatred(-5)  # AI buff cancels nightly hatred
        if stats.daily_btc_income > 0:
            stats.increment_stats_value_money(stats.daily_btc_income)

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
            if day_cycle.current_day >= 25:
                renpy.jump("burnout_ending")
            else:
                renpy.jump("mental_breakdown_ending")
        if stats.available_money <= 0:
            renpy.jump("homeless_ending")

    jump day_start


## ---------------------------------------------------------------------------
## SALARY DAY (Day 14)
## ---------------------------------------------------------------------------

label salary_day:

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

    scene bg_police_interior

    python:
        _sal = salary_amount(stats.pcr_hatred)
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

    "You open the cabinet. The protocol is specific. Every compound has a purpose.[_dep_warning]"

    menu:
        "TIER 1 — Daily Supplements (300 CZK)\n[NOOTROPIC_TIERS[1]['compounds']]":
            python:
                _tier = 1

        "TIER 2 — Cognitive Stack (750 CZK)\n[NOOTROPIC_TIERS[2]['compounds']]" if nootropic_tier_max >= 2:
            python:
                _tier = 2

        "TIER 3 — Racetams (1,250 CZK)\n[NOOTROPIC_TIERS[3]['compounds']]" if nootropic_tier_max >= 3:
            python:
                _tier = 3

        "TIER 4 — Peptides (2,000 CZK)\n[NOOTROPIC_TIERS[4]['compounds']]" if nootropic_tier_max >= 4:
            python:
                _tier = 4

        "TIER 5 — FLModafinil (CRL-40,940) (3,500 CZK)\n[NOOTROPIC_TIERS[5]['compounds']]" if flmodafinil_unlocked or nootropic_tier_max >= 5:
            python:
                _tier = 5

        "Return to menu.":
            jump activity_coding

    ## --- Process selected tier ---
    python:
        _t     = NOOTROPIC_TIERS[_tier]
        _cost  = _t["cost"]

        # Dependency reduces T5 effectiveness
        _coding_gain = _t["coding"]
        if nootropic_dependency and _tier == 5:
            _coding_gain = int(_coding_gain * 0.65)  # diminishing returns

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

        # Check for new tier unlocks
        _unlock = check_nootropic_unlocks()

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
        _dep_warn = nootropic_uses[4] == 2 and _tier == 5

    if _dep_warn:
        "[[WARNING]] One more dose and your baseline changes permanently.\nFLModafinil (CRL-40,940) dependency triggers at 3 total uses."

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

        # Apply effects
        stats.increment_stats_pcr_hatred(-20)
        _cr_coding_bonus = 0
        if _high_hatred:
            stats.increment_stats_coding_skill(5)
            _cr_coding_bonus = 5

        _cr_outcome = "-20 Police Hatred"
        if _cr_coding_bonus:
            _cr_outcome += ", +5 Coding Skill  [HIGH HATRED — CONTEMPT MODE]"

    "SUBJECT: [_target['name']]"

    "[_cr_text]"

    show screen outcome_panel(_cr_outcome)
    pause
    hide screen outcome_panel

    python:
        activity_selected = True

    jump daily_menu


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

        "LOG AND CONTINUE — Symptoms are data. Biohackers don't panic. (50%% success)":
            python:
                _bh_crisis_roll = __import__('random').randint(1, 100)
                if _bh_crisis_roll <= 50:
                    stats.increment_stats_pcr_hatred(-15)
                    stats.increment_stats_coding_skill(5)
                    _bh_outcome = "-15 PCR HATRED, +5 CODING [BIOHACKER CRISIS: logged and stabilized]."
                    _bh_text = "You open a spreadsheet. HRV. Cortisol proxy. Sleep debt.\nYou adjust the protocol. Reduce T dose, increase magnesium, shift the timing 2 hours.\nWithin 90 minutes your hands are steady.\nYou turned a crisis into a calibration point.\nThat is exactly the kind of person you are becoming."
                else:
                    stats.increment_stats_pcr_hatred(20)
                    stats.increment_stats_coding_skill(-8)
                    _bh_outcome = "+20 PCR HATRED, -8 CODING [BIOHACKER CRISIS: system overload]."
                    _bh_text = "You log everything and keep pushing.\nAt 4 PM your vision goes grey at the edges.\nYou sit on the bathroom floor for 15 minutes.\nA colleague knocks on the door: 'JB, you okay in there?'\nYou are not okay. Your optimization loop had no exit condition.\nYou are the bug."
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
        if store.random_event_pool:
            _chosen = __import__('random').choice(store.random_event_pool)
            store.random_event_pool.remove(_chosen)
            renpy.call(_chosen)
            ## Restore ambient music after random event
            if stats.pcr_hatred >= 75:
                renpy.music.play("audio/tension_theme.mp3", fadein=1.5)
            else:
                renpy.music.play("audio/enter_the_code_theme.mp3", fadein=1.5)
            # After random event, do an extra night cycle
            stats.increment_stats_pcr_hatred(5)
            if python_bootcamp:
                stats.increment_stats_coding_skill(5)
            if stats.ai_paperwork_buff:
                stats.increment_stats_pcr_hatred(-5)
            if stats.daily_btc_income > 0:
                stats.increment_stats_value_money(stats.daily_btc_income)
            day_cycle.next_day()

    return
