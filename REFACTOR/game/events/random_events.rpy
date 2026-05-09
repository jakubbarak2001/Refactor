################################################################################
## REFACTOR — Random Events (distilled v2)
##
## Each random event is now a Slay-the-Spire-style 2-option choice:
##   1 setup banner, 2-3 lines of context, 2 options with cost/reward visible
##   inline, 1-2 lines of resolution per branch.
##
## Hardcoded story-arc events (re_the_bribe, re_corrupt_cop_2/3) keep their
## long-form treatment at the bottom of the file — they're not random, they
## carry the corruption arc and earn their length.
################################################################################

## ---------------------------------------------------------------------------
## EVENT 1: Tel Aviv Professor
## Coding-skill check (≥35) or Biohacker auto-pass. Pass unlocks FLMod for BH.
## ---------------------------------------------------------------------------

label re_israeli_developer:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "TEL AVIV PROFESSOR"

    "A fender-bender. The professor steps out of the damaged Mercedes, ignoring the chaos."
    "He looks at you, ignoring the uniform entirely."
    "'You have intelligent eyes. Tell me — do you write code?'"

    python:
        _can_code = stats.coding_skill >= 35 or stats.player_class == "biohacker"

    menu:
        "Talk code. [[+30 Coding, BH: FLMod source]]" if _can_code:
            python:
                stats.increment_stats_coding_skill(30)
                _bh = (stats.player_class == "biohacker")
                if _bh:
                    flmodafinil_unlocked = True

            "Twenty minutes of pointers, GIL, scaling. He nods. Hands you his GitHub on a folded card."

            if stats.player_class == "biohacker":
                "Then, quieter: 'I notice things. You optimise everything — including yourself.'"
                "He slips you a Telegram handle. CRL-40,940 source. You pocket it."
                show screen outcome_panel("+30 CODING  |  [[CRL-40,940 SOURCE UNLOCKED]]  [BIOHACKER]")
            else:
                show screen outcome_panel("+30 CODING SKILL.")
            pause
            hide screen outcome_panel

        "Stay silent. [[+10 Coding]]":
            $ stats.increment_stats_coding_skill(10)
            "He shrugs. Gives you sixty seconds on abstraction layers anyway."
            "You learn something. The fear chokes the rest."
            show screen outcome_panel("+10 CODING SKILL.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 2: The Nightmare
## Atmospheric Arc-II beat. Flag retained for save-state continuity, no longer
## gates a hidden ending.
## ---------------------------------------------------------------------------

label re_nightmare_wolf:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    $ store._nightmare_wolf_triggered = True

    "THE NIGHTMARE"

    "04:00 AM. A dream of body bags moving. A black husky pressing its nose to glass."
    "You wake up choking. The room is silent. The dream had teeth."

    menu:
        "Shake it off. [[+5 Hatred]]":
            $ stats.increment_stats_pcr_hatred(5)
            "You don't forget."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Analyze it.":
            python:
                if stats.player_class == "dark_empath":
                    stats.increment_stats_pcr_hatred(-10)
                    stats.increment_stats_coding_skill(5)
                    _nw_msg = "[[DARK EMPATH]] You map the symbolism. The bag is the job. The wolf is the part of you that already left."
                    _nw_out = "-10 PCR HATRED, +5 CODING [DE: insight]."
                else:
                    _roll = __import__('random').randint(1, 100)
                    if _roll <= 50:
                        stats.increment_stats_coding_skill(5)
                        _nw_msg = "You journal it. Some patterns surface. You sleep better the rest of the week."
                        _nw_out = "+5 CODING SKILL."
                    else:
                        stats.increment_stats_pcr_hatred(10)
                        _nw_msg = "You stare at the ceiling and the dream gets worse, not better."
                        _nw_out = "+10 PCR HATRED."
            "[_nw_msg]"
            show screen outcome_panel(_nw_out)
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 3: The Compliment (DE auto-success)
## ---------------------------------------------------------------------------

label re_civilian_small_talk:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE COMPLIMENT"

    "An older woman with a small dog stops at a crosswalk and compliments your uniform."
    "'Just polite,' she says. 'I notice things.'"

    menu:
        "Small talk.":
            python:
                if stats.player_class == "dark_empath":
                    stats.increment_stats_pcr_hatred(-25)
                    _ct_amt = -25
                    _ct_tag = " [DARK EMPATH]"
                else:
                    _roll = __import__('random').randint(1, 100)
                    _ct_tag = ""
                    if _roll <= 60:
                        stats.increment_stats_pcr_hatred(-15)
                        _ct_amt = -15
                    else:
                        stats.increment_stats_pcr_hatred(5)
                        _ct_amt = 5
            if _ct_amt < 0:
                "She tells you about her son abroad. The dog is from a shelter. You leave the corner lighter."
                show screen outcome_panel("{} PCR HATRED{}".format(_ct_amt, _ct_tag))
            else:
                "You botch the rhythm of the conversation. She walks off. You feel worse than before."
                show screen outcome_panel("+{} PCR HATRED (awkward).".format(_ct_amt))
            pause
            hide screen outcome_panel

        "Professional nod. [[no change]]":
            "You move on. So does she."
            show screen outcome_panel("NO CHANGE.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 4: The Paperwork
## ---------------------------------------------------------------------------

label re_admin_mistake:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE PAPERWORK"

    "Sergeant: 'JB. This report has your name on it. Stop signature, search authorization, evidence chain. It shouldn't.'"
    "You've never seen this case before."

    menu:
        "Fix it quietly. [[-5 Hatred, +1 Coding]]":
            python:
                stats.increment_stats_pcr_hatred(-5)
                stats.increment_stats_coding_skill(1)
            "Forty-five minutes of database forensics. You find the bug. You file a quiet correction."
            "Your name comes off the doc. Nobody else finds out."
            show screen outcome_panel("-5 PCR HATRED, +1 CODING SKILL.")
            pause
            hide screen outcome_panel

        "Escalate. [[+10 Hatred]]":
            $ stats.increment_stats_pcr_hatred(10)
            "Internal Review opens an inquiry. Three colleagues are interviewed."
            "By Friday everyone knows you ratted. The atmosphere does not improve."
            show screen outcome_panel("+10 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 5: The Overtime (BB perk: no Hatred)
## ---------------------------------------------------------------------------

label re_overtime_offer:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE OVERTIME"

    "Dispatch needs a double tonight. Cash bonus, no questions. The shift supervisor is already walking away."

    menu:
        "Take it. (+6,000 CZK) (BB: 0 Hatred. Other: +15 Hatred.)":
            python:
                stats.increment_stats_value_money(6000)
                if stats.player_class == "bodybuilder":
                    _ot_hat = 0
                    _ot_msg = "[[BB]] You sleep four hours and look fresh. The sergeant is suspicious."
                else:
                    stats.increment_stats_pcr_hatred(15)
                    _ot_hat = 15
                    _ot_msg = "Sixteen hours straight. By hour twelve you stop being a person and start being a function."
            "[_ot_msg]"
            show screen outcome_panel("+6,000 CZK, +{} PCR HATRED.".format(_ot_hat))
            pause
            hide screen outcome_panel

        "Pass. [[no change]]":
            "He blinks. Nobody says no. He shrugs and walks off."
            show screen outcome_panel("NO CHANGE.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 6: The Birthday Gift
## ---------------------------------------------------------------------------

label re_birthday_gift:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE GIFT"

    "It's your birthday. Lieutenant Kovář puts a hand on your shoulder. 'Don't open it here.'"
    "An envelope. Heavy. You can feel the cash through the paper."

    menu:
        "Accept. (+5,000 CZK, +15 Hatred)":
            python:
                stats.increment_stats_value_money(5000)
                stats.increment_stats_pcr_hatred(15)
            "He squeezes your shoulder. 'You're a good man, JB.'"
            "You're not sure what 'good' means anymore."
            show screen outcome_panel("+5,000 CZK, +15 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Refuse. [[-5 Hatred]]":
            $ stats.increment_stats_pcr_hatred(-5)
            "He looks at you for a long moment. Then nods. 'Fair enough.'"
            "Your spine straightens slightly."
            show screen outcome_panel("-5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 7: The Note (DE: +1 extra Coding)
## ---------------------------------------------------------------------------

label re_corpse_in_care_home:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE NOTE"

    "A care home. An elderly woman. The smell. The note on the bedside table."
    "'Sorry for the trouble.'"

    menu:
        "Process professionally. [[+15 Hatred, +1 Coding]]":
            python:
                stats.increment_stats_pcr_hatred(15)
                stats.increment_stats_coding_skill(1)
            "You document everything correctly. The paperwork is clean. You sleep poorly for three days."
            show screen outcome_panel("+15 PCR HATRED, +1 CODING SKILL (procedure muscle).")
            pause
            hide screen outcome_panel

        "Stay with her.":
            python:
                stats.increment_stats_pcr_hatred(-10)
                stats.increment_stats_coding_skill(5)
                _nt_extra = ""
                if stats.player_class == "dark_empath":
                    stats.increment_stats_coding_skill(1)
                    _nt_extra = " [DARK EMPATH: read between the lines, +1 extra]"
            "She had a granddaughter. The handwriting is firm. She knew what she was doing."
            "You leave the room slower than you entered it."
            show screen outcome_panel("-10 PCR HATRED, +5 CODING SKILL{}.".format(_nt_extra))
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 8: The USB
## ---------------------------------------------------------------------------

label re_forgotten_usb:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE USB"

    "A USB stick on your keyboard. No label. Not yours."

    menu:
        "Plug it in.":
            python:
                _usb_roll = __import__('random').randint(1, 100)
                stats.increment_stats_coding_skill(10)
                if _usb_roll <= 25:
                    stats.increment_stats_coding_skill(10)  ## net +20
                    store._usb_evidence = True
                    _usb_msg = "Internal procurement records. Three names. Six contracts. One name belongs to a colleague."
                    _usb_out = "+20 CODING SKILL [[FLAG: usb_evidence]]"
                else:
                    _usb_msg = "A folder of badly-organized scripts and a corrupted Excel. You learn from the chaos."
                    _usb_out = "+10 CODING SKILL."
            "[_usb_msg]"
            show screen outcome_panel(_usb_out)
            pause
            hide screen outcome_panel

        "Turn it in. [[+5 Hatred]]":
            $ stats.increment_stats_pcr_hatred(5)
            "Lieutenant Kovář takes it without making eye contact. You never see it again."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 9: The Turkish Neighbor
## ---------------------------------------------------------------------------

label re_turkish_fraud:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE CALL"

    "An older man at the front desk: 'Pane policisto, my Turkish neighbor — he keeps asking my bank details.'"
    "'I think he's running a scam. Or maybe I'm paranoid.'"

    menu:
        "Follow up. [[+10 Coding]]":
            $ stats.increment_stats_coding_skill(10)
            "An empty Airbnb. Three burner phones in a drawer. You run the IPs."
            "You find a fraud ring you can't dismantle alone — but you understand the topology now."
            show screen outcome_panel("+10 CODING SKILL (system mapping).")
            pause
            hide screen outcome_panel

        "Dismiss. [[+5 Hatred]]":
            $ stats.increment_stats_pcr_hatred(5)
            "He leaves. He looks smaller than when he came in."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 10: The Printer (BB perk)
## ---------------------------------------------------------------------------

label re_printer_incident:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE PRINTER"

    "The printer eats your incident report. You have ten minutes to get it to the prosecutor."

    menu:
        "Slam it.":
            python:
                if stats.player_class == "bodybuilder":
                    stats.increment_stats_coding_skill(5)
                    _pr_msg = "[[BB]] One palm strike. The drum unjams. The page emerges. Sergeant slow-claps. You bow."
                    _pr_out = "+5 CODING (you fixed it by being correct about the world). [BB]"
                else:
                    stats.increment_stats_pcr_hatred(15)
                    _pr_msg = "You break the front panel. The printer makes a sound it shouldn't. You owe IT 4,000 CZK."
                    _pr_out = "+15 PCR HATRED."
            "[_pr_msg]"
            show screen outcome_panel(_pr_out)
            pause
            hide screen outcome_panel

        "Debug it. [[+5 Coding]]":
            $ stats.increment_stats_coding_skill(5)
            "You find the rolled paper. You release it. The printer respects you, briefly."
            show screen outcome_panel("+5 CODING SKILL.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 11: The Old Man
## ---------------------------------------------------------------------------

label re_citizen_czechoslovakia:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE OLD MAN"

    "An old man at a tram stop, talking about how things were better in 1985."
    "He sees the uniform. He locks onto you. 'Officer. You have a minute?'"

    menu:
        "Listen. [[-10 Hatred]]":
            $ stats.increment_stats_pcr_hatred(-10)
            "He talks for six minutes. Beer was 1.20 Kčs. The trams ran on time. His wife died in 2003."
            "You don't say much. He doesn't need you to."
            show screen outcome_panel("-10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Move him along. [[+10 Hatred]]":
            $ stats.increment_stats_pcr_hatred(10)
            "He shuffles off. He doesn't look back."
            show screen outcome_panel("+10 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 12: The Stack (BH perk)
## ---------------------------------------------------------------------------

label re_paperwork_overload:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE STACK"

    "200 incident reports, due tomorrow. Half are duplicates. The form fields are inconsistent."

    menu:
        "Stack up.":
            python:
                if stats.player_class == "biohacker":
                    stats.increment_stats_coding_skill(20)
                    _st_msg = "[[BH]] You drop into deep work. Four hours feels like forty minutes. Done."
                    _st_out = "+20 CODING SKILL [[BH: hyperfocus]]"
                else:
                    stats.increment_stats_pcr_hatred(15)
                    _st_msg = "You dial in. The system breaks twice. Your back hurts. You finish at 3 AM."
                    _st_out = "+15 PCR HATRED."
            "[_st_msg]"
            show screen outcome_panel(_st_out)
            pause
            hide screen outcome_panel

        "Manual grind. [[+10 Hatred, +1 Coding]]":
            python:
                stats.increment_stats_pcr_hatred(10)
                stats.increment_stats_coding_skill(1)
            "You finish at 4 AM. You learn the schema by accident."
            show screen outcome_panel("+10 PCR HATRED, +1 CODING SKILL.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 13: The Outage
## ---------------------------------------------------------------------------

label re_dispatch_blue_screen:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE OUTAGE"

    "'Dispatch is offline.' The room freezes. Three patrols are mid-pursuit. The radio works. The terminal doesn't."

    menu:
        "Reboot it. [[+10 Coding]]":
            $ stats.increment_stats_coding_skill(10)
            "You restart the service. You clear the lock file. You re-establish the database connection."
            "Dispatch is back online in eleven minutes. The unit chief looks at you for the first time in three years."
            show screen outcome_panel("+10 CODING SKILL.")
            pause
            hide screen outcome_panel

        "Use the radio. [[-5 Hatred]]":
            $ stats.increment_stats_pcr_hatred(-5)
            "Voice channel only, like the 90s. Things move slower. Nobody dies. You like it."
            show screen outcome_panel("-5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 14: The Tesla (BH perk)
## ---------------------------------------------------------------------------

label re_tech_bro_speeding:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE TESLA"

    "Tesla Model S. 220 km/h. The driver is in his thirties, AirPods in, no panic at all."
    "He hands you a business card before he hands you his license. CTO. Fintech. Smug."

    menu:
        "Take the card.":
            python:
                stats.increment_stats_coding_skill(5)
                if stats.player_class == "biohacker":
                    stats.increment_stats_coding_skill(3)
                    _tb_msg = "[[BH]] You ask three sharp questions about his stack. He's impressed enough to follow up."
                    _tb_out = "+8 CODING SKILL [[BH: networking]]"
                else:
                    _tb_msg = "You bookmark him in your head. You'll Google the company later."
                    _tb_out = "+5 CODING SKILL (networking flag)."
            "[_tb_msg]"
            show screen outcome_panel(_tb_out)
            pause
            hide screen outcome_panel

        "Write the ticket. [[+1,500 CZK]]":
            $ stats.increment_stats_value_money(1500)
            "He pays without arguing. He drives at exactly 130 km/h afterwards."
            show screen outcome_panel("+1,500 CZK.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 15: The Whisper (offers snitch_info card)
## ---------------------------------------------------------------------------

label re_the_informant:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE WHISPER"

    "A colleague you barely know corners you by the coffee machine."
    "'I've got something on Lieutenant Kovář. Expense reports. Doctored. Want to know?'"

    menu:
        "Listen. [[CARD: SNITCH INFO]]":
            "He talks for twelve minutes. Dates, amounts, account numbers. You memorize them."
            "You walk away with information that has weight."
            python:
                offer_card("snitch_info", "INFORMANT")
            show screen outcome_panel("[[SNITCH INFO offered]]")
            pause
            hide screen outcome_panel

        "Pass. [[+5 Hatred]]":
            $ stats.increment_stats_pcr_hatred(5)
            "He nods. He walks away. Now you wonder."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 16: The Eval
## ---------------------------------------------------------------------------

label re_the_evaluation:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE EVAL"

    "Mandatory department psych eval. The therapist is in her forties, kind eyes, a clipboard."
    "'How are you feeling about the work, JB?'"

    menu:
        "Be honest. [[-10 Hatred]]":
            $ stats.increment_stats_pcr_hatred(-10)
            "She nods slowly. Doesn't write it down. Says: 'I'm not your enemy. I'll mark you fit. Take care of yourself.'"
            show screen outcome_panel("-10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Perform sanity. [[+5 Hatred]]":
            $ stats.increment_stats_pcr_hatred(5)
            "You hear yourself say things the academy taught you to say. She marks you fit."
            "The lie taxes you on the drive home."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 17: The 03:14 Call (DE bonus)
## ---------------------------------------------------------------------------

label re_suicide_call:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE CALL"

    "03:14 AM. The voice on the line is shaking. Male, mid-twenties, on a bridge."
    "He's not asking for help. He's just talking."

    menu:
        "Stay on the line.":
            python:
                stats.increment_stats_pcr_hatred(-15)
                stats.increment_stats_coding_skill(5)
                _sc_extra = ""
                if stats.player_class == "dark_empath":
                    stats.increment_stats_coding_skill(5)
                    _sc_extra = " [[DARK EMPATH: read his pauses, +5 extra Coding]]"
            "Forty-seven minutes. He stays. By the time the ambulance gets there, he's sitting on the curb crying."
            show screen outcome_panel("-15 PCR HATRED, +5 CODING SKILL.{}".format(_sc_extra))
            pause
            hide screen outcome_panel

        "Transfer it. [[+10 Hatred]]":
            $ stats.increment_stats_pcr_hatred(10)
            "You patch him to the suicide hotline. The call drops during the transfer."
            "You don't know what happened. The shift continues."
            show screen outcome_panel("+10 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 18: The Party
## ---------------------------------------------------------------------------

label re_retirement_party:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE PARTY"

    "Sergeant Novák. 35 years. Retiring with a 28%% pension."
    "Drinks at U Slunce, 7 PM. Half the station will be there."

    menu:
        "Go. (-1,500 CZK)":
            python:
                stats.increment_stats_value_money(-1500)
                stats.increment_stats_pcr_hatred(-10)
            "He cries on you at 11 PM. Forty years of service. He says: 'Don't make my mistakes, kid.'"
            "You don't know which ones he means. All of them, probably."
            show screen outcome_panel("-1,500 CZK, -10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Skip it. [[+5 Hatred]]":
            $ stats.increment_stats_pcr_hatred(5)
            "You see the photos on Monday. He looks happy. You look at your reflection."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 19: The Interview (puzzle gate)
## ---------------------------------------------------------------------------

label re_coding_interview:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "THE INTERVIEW"

    "A startup emailed back. Quick technical screen, 30 minutes, tonight."
    "You're parked in a patrol car. Phone in your lap. They're already on the line."

    menu:
        "Take it.":
            python:
                _ci_solved = getattr(store, '_puzzles_solved', None)
                if _ci_solved is None:
                    store._puzzles_solved = []
                    _ci_solved = store._puzzles_solved
                _ci_pid = pick_puzzle_for_skill(stats.coding_skill, exclude=_ci_solved)
                if _ci_pid is None:
                    _ci_pid = "p_medium_sum_even"
                puzzle_init(_ci_pid, max_attempts=1 + diff_setting("minigame_retries", 1))

            "[PUZZLES[_ci_pid]['spec']]"

            call screen coding_puzzle_screen

            python:
                _ci_pass = (_return == "pass")
                if _ci_pass:
                    stats.increment_stats_coding_skill(20)
                    stats.increment_stats_pcr_hatred(-15)
                    store.coding_interview_passed = True
                    store._puzzles_solved.append(_ci_pid)
                    _ci_msg = "You answer cleanly. The interviewer goes quiet. Then: 'Can you come in next week for a technical round?'"
                    _ci_out = "+20 CODING, -15 PCR HATRED [[INTERVIEW PASSED]]"
                else:
                    stats.increment_stats_coding_skill(5)
                    stats.increment_stats_pcr_hatred(15)
                    _ci_msg = "Async Python catches you. You hear yourself say 'callback hell' and mean something else. Dispatch interrupts the call."
                    _ci_out = "+5 CODING (you learned), +15 PCR HATRED."

            "[_ci_msg]"
            show screen outcome_panel(_ci_out)
            pause
            hide screen outcome_panel

        "Reschedule. [[+3 Coding, +10 Hatred]]":
            python:
                stats.increment_stats_coding_skill(3)
                stats.increment_stats_pcr_hatred(10)
            "They reply: 'Sure! Friday at 14:00.' Friday is your 12-hour shift."
            "You stare at the calendar. You reply: 'Perfect.'"
            show screen outcome_panel("+3 CODING, +10 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT 20: The Update (BH/DE perks + skill check)
## ---------------------------------------------------------------------------

label re_system_update:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "THE UPDATE"

    "IT pushed an update at 06:00. By 07:30 nothing works."
    "Error: 'RuntimeError: Database migration failed.' You actually understand what that means."

    python:
        _su_chance = min((stats.coding_skill * 100) // 60, 100)

    menu:
        "[[BH]] KNOWN FAILURE MODE — You've seen this exact error on a dev forum at 2 AM." if stats.player_class == "biohacker":
            python:
                stats.increment_stats_coding_skill(15)
                stats.increment_stats_pcr_hatred(-20)
                stats.increment_stats_value_money(2500)
            "Three commands in a terminal. The screen turns green. Silence. Sergeant: 'JB. How did you—'"
            "You leave before he can take the bonus back."
            show screen outcome_panel("+15 CODING, -20 PCR HATRED, +2,500 CZK [[BH: known fix]]")
            pause
            hide screen outcome_panel

        "[[DE]] FIND HORA — Constable Hora isn't panicking. He knows something." if stats.player_class == "dark_empath":
            python:
                stats.increment_stats_pcr_hatred(-10)
                stats.increment_stats_coding_skill(5)
            "Hora: 'The v1.4.2 rollback re-enables the legacy ODBC connector. Run the old client on desktop four.'"
            "You do. It works. You give Hora the coffee meant for the sergeant."
            show screen outcome_panel("-10 PCR HATRED, +5 CODING [[DE: extracted the workaround]]")
            pause
            hide screen outcome_panel

        "Fix it. [[CODING CHECK: [_su_chance]%%]]":
            python:
                _su_roll = __import__('random').randint(1, 100)
                if _su_roll <= _su_chance:
                    stats.increment_stats_coding_skill(15)
                    stats.increment_stats_pcr_hatred(-20)
                    stats.increment_stats_value_money(2500)
                    _su_msg = "Three commands. Green screen. Sergeant gives you the rest of the shift off and an unofficial bonus."
                    _su_out = "+15 CODING, -20 PCR HATRED, +2,500 CZK."
                else:
                    stats.increment_stats_coding_skill(5)
                    stats.increment_stats_pcr_hatred(20)
                    _su_msg = "You make it worse. The migration re-runs and a 2019 arrest warrant gets reactivated. Someone in Brno is having a confusing afternoon."
                    _su_out = "+5 CODING (negative reinforcement), +20 PCR HATRED."
            "[_su_msg]"
            show screen outcome_panel(_su_out)
            pause
            hide screen outcome_panel

        "Walk out. [[+10 Hatred, +2 Coding]]":
            python:
                stats.increment_stats_pcr_hatred(10)
                stats.increment_stats_coding_skill(2)
            "You spend patrol thinking about the error message. Better communication than most humans you know."
            show screen outcome_panel("+10 PCR HATRED, +2 CODING (ambient learning).")
            pause
            hide screen outcome_panel

    return


################################################################################
## STORY ARC EVENTS — kept long-form (corruption chain).
## These are NOT random — they're hardcoded to specific days and gate endings.
################################################################################

## ---------------------------------------------------------------------------
## EVENT: The Bribe (Day 6 — Hardcoded. Gates the corrupt cop chain.)
## ---------------------------------------------------------------------------

label re_the_bribe:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "DAY 6 — MORAL CHECKPOINT"

    "Traffic stop. Quiet stretch of road outside the city."
    "You clocked him at 68 in a 50 zone. Standard pull. Routine."
    "The car is a BMW 7 Series. Fresh plates. Washed this morning."
    "The driver is mid-50s. Expensive suit. Real tan — the kind from places that have names, not seasons."
    "He hands you his license without being asked. Clean record. Valid insurance."
    "A 1,200 CZK fine. You've written a hundred of these."
    "Then you see it."
    "Under the license. A folded stack of banknotes. Crisp. Prepared."
    "Not a crumpled emergency fifty. This was ready before he left the house."
    "Seven thousand, five hundred crowns."
    "More than you make in a full week of night shifts."
    "He doesn't look at you. He looks at the road ahead."
    "His hand is completely steady."
    "'There are no cameras on this stretch,' he says. Quietly. Like a forecast."
    "'Your colleague is two hundred metres back. I counted.'"
    "You look down the road. He's right. No cameras. Your colleague is checking his phone."
    "Nobody is watching."
    "The debt sits in the back of your head. The Colonel's car. The eight thousand you still owe."
    "He waits."

    menu:
        "Just for this once... [[+7,500 CZK, -15 PCR HATRED]":
            python:
                stats.increment_stats_value_money(7500)
                stats.increment_stats_pcr_hatred(-15)
                store.corrupt_chain_1 = True

            "Your hand closes around the notes."
            "You hand back his license. You say nothing."
            "He says nothing."
            "He pulls away smoothly. No wheel spin. No rush. He's done this before."
            "You stand on the empty road and watch the BMW disappear around the corner."
            "Seven thousand, five hundred crowns."
            "No report. No ticket. No record."
            "The debt in your head gets a little quieter."
            "You think about the Colonel. The eight thousand. The car."
            "You think about Martin, sitting in some café, free."
            "Nobody saw."
            "You get back in the car."
            show screen outcome_panel("+7,500 CZK, -15 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Write the ticket. Do your job.":
            python:
                stats.increment_stats_pcr_hatred(25)
                store.corrupt_chain_1 = False

            "You slide the banknotes back across the license."
            jb "'Just the fine today, sir. 1,200 CZK.'"
            "Something shifts in his face. Not surprise. Not respect."
            "Contempt. Brief, clean, professional contempt."
            "He taps his card on the reader without a word."
            "Then he looks at you. Really looks at you. For the first time."
            "'You know what I make in a day?'"
            "You don't answer."
            "'More than your monthly salary. Probably more than your annual one.'"
            "He takes his receipt."
            "'Keep the badge. You clearly need it more than I need my money.'"
            "He drives away at exactly the speed limit."
            "You stand there holding a 1,200 CZK citation that goes to the state."
            "Not to you. Not to your debt. Not to the Colonel's car. To them."
            "Your colleague is still on his phone."
            "You get back in the car and say nothing."
            show screen outcome_panel("+25 PCR HATRED. (The right call. The expensive one.)")
            pause
            hide screen outcome_panel

        "[[DARK EMPATH]] READ HIM — Profile the driver before you decide." if stats.player_class == "dark_empath":
            python:
                stats.increment_stats_pcr_hatred(-10)
                stats.increment_stats_coding_skill(5)
            "You look at him. Really look."
            "Real tan, not a booth. The suit is bespoke. His hands are completely still."
            "This man is not nervous. Not performing. Not running anything."
            "He considers bribery a transaction. Clean, bilateral, efficient."
            "He's done this before. He'll do it again. He does not see you as a threat."
            "You can work with that."
            jb "'I'll need your company name. For the report I'm not going to file.'"
            "He meets your eyes for the first time. A small, professional nod."
            "He gives you a card. Name. Address. Registered in Luxembourg."
            "He drives away. No ticket. No bribe taken. No moral residue."
            "You have nothing on you and everything you need."
            "You file the card in your jacket. You'll look it up later."
            show screen outcome_panel("-10 PCR HATRED, +5 CODING SKILL [DARK EMPATH: read him clean, kept your hands clean].")
            pause
            hide screen outcome_panel

        "[[BODYBUILDER]] FLIP THE SCRIPT — Step out of the car. Change the power dynamic." if stats.player_class == "bodybuilder":
            python:
                stats.increment_stats_value_money(2400)
                stats.increment_stats_pcr_hatred(-5)
            "You look at the bill. Then at him."
            "You open your door."
            "You step out."
            "All of you steps out."
            "He watches you walk to his window. He has to look up."
            jb "'Sir. I need you to step outside.'"
            "The bill disappears somewhere in his jacket."
            "His hand is not entirely steady."
            "He steps outside."
            jb "'The fine is 2,400 CZK. Speeding plus failure to cooperate with an officer. Cash or card.'"
            "He pays immediately. He does not negotiate."
            "He gets back in his car and drives at exactly the speed limit for at least 200 metres."
            show screen outcome_panel("+2,400 CZK, -5 PCR HATRED [BODYBUILDER: presence commanded the room].")
            pause
            hide screen outcome_panel

        "[[BIOHACKER]] CALCULATE — Run the expected value before touching anything." if stats.player_class == "biohacker":
            python:
                stats.increment_stats_value_money(5000)
                stats.increment_stats_pcr_hatred(8)
                store.corrupt_chain_1 = True
            "You run the numbers."
            "Five thousand CZK. Camera coverage at this stop: none. Third-party witnesses: zero. Setup probability given the car, the plates, the body language: under two percent."
            "Expected value: positive. Risk-adjusted value: still positive."
            "You pocket the bill."
            "Then you write the ticket anyway."
            "If he escalates, you have the ticket. If he doesn't, you have both."
            "He doesn't escalate. He drives away."
            "You made 5,000 CZK and issued a valid citation."
            "The system is not efficient. You are."
            show screen outcome_panel("+5,000 CZK, +8 PCR HATRED [BIOHACKER: positive expected value, minor guilt tax].")
            pause
            hide screen outcome_panel

        "Take it and double down.":
            python:
                _br_roll = __import__('random').randint(1, 100)
                if _br_roll <= 40:
                    stats.increment_stats_value_money(5000)
                    stats.increment_stats_pcr_hatred(10)
                    store.corrupt_chain_1 = True
                    _br_text = "You take the money. Then you file an anonymous tip about a suspicious BMW.\nInternal affairs investigates. They find nothing on you.\nThe driver gets a visit and a fine anyway.\nYou bought yourself 5000 CZK and a clean conscience. Somehow."
                    _br_outcome = "+5,000 CZK, +10 PCR HATRED (Morally complex but financially positive)."
                else:
                    stats.increment_stats_value_money(-3000)
                    stats.increment_stats_pcr_hatred(35)
                    store.corrupt_chain_1 = False
                    _br_text = "The driver's 'secretary' works in internal affairs.\nThree days later you are called in for a 'routine audit'.\nYou pay the money back plus a penalty.\nThe driver sends you a LinkedIn request. You decline."
                    _br_outcome = "-3,000 CZK, +35 PCR HATRED (The plan had a flaw)."

            "[_br_text]"
            show screen outcome_panel(_br_outcome)
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Corrupt Cop Chain — Part 2 (Day 12)
## THE BLACKMAIL — same BMW driver returns, but now he owns you
## ---------------------------------------------------------------------------

label re_corrupt_cop_2:

    scene bg_random_event

    "DAY 12 — THE RETURN"

    "You're walking to your car after shift when you see it."
    "The BMW 7 Series. Same plates. Parked directly next to yours."
    "He's leaning against the hood. Arms crossed. Not hiding."
    "The tan. The suit. The steady hands. The same man from the Litoměřice stretch."
    "He smiles when he sees your face."
    "'Officer. Good to see you again.'"
    "Your stomach folds in half."
    "'I have a small problem,' he says. 'Drove through a checkpoint last night. Blew 0.9. Not my finest hour.'"
    "He reaches into his jacket. Pulls out a folded paper. A citation."
    "'I need this to disappear. The court date, the points, the record. All of it.'"
    "You look at the paper. DUI citation. Filed two days ago. Already in the system."
    "'I can't do that,' you say. 'It's already filed. There's a digital trail.'"
    "He tilts his head. Like a dog hearing a frequency you can't."
    "'JB. Can I call you JB? I recorded our conversation. The one on the Litoměřice stretch.'"
    "He pulls out his phone. Taps play."
    "Your voice fills the parking lot. Clear as daylight."
    "The sound of banknotes. Your silence. His silence. The car pulling away."
    "He taps pause."
    "'I don't want trouble. I just want the citation to go away. That's all.'"
    "That is not all. You both know that is not all."

    menu:
        "Make the citation disappear. You have no choice. (+25 Hatred)":
            python:
                stats.increment_stats_pcr_hatred(25)
                store.corrupt_chain_2 = True

            "You take the paper."
            "You don't say anything. There's nothing to say."
            "That night you stay late at the station. You access the system. You find the citation."
            "You mark it as 'filed in error — duplicate entry.' You delete the court referral."
            "It takes eleven minutes. Eleven minutes to become someone you don't recognize."
            "He texts you at midnight. One word: 'Thanks.'"
            "You don't respond. You delete the message. You can't delete the eleven minutes."

            show screen outcome_panel("+25 PCR HATRED. You are owned.")
            pause
            hide screen outcome_panel

        "Ask for money. If he wants favors, he pays for them. (50/50: +10,000 CZK or +35 Hatred)":
            python:
                _cc_roll = __import__('random').randint(1, 100)
                if _cc_roll <= 50:
                    stats.increment_stats_value_money(10000)
                    stats.increment_stats_pcr_hatred(15)
                    store.corrupt_chain_2 = True
                    store._corrupt_asked_money = True
                else:
                    stats.increment_stats_pcr_hatred(35)
                    store.corrupt_chain_2 = True
                    store._corrupt_asked_money = False

            if getattr(store, '_corrupt_asked_money', False):
                "'If I'm taking this kind of risk,' you say, 'I need compensation.'"
                "He looks at you. Something shifts behind his eyes. Respect, maybe. Or just recalculation."
                "'Ten thousand. Final.'"
                "You nod."
                "He hands you an envelope. You make the citation disappear that night."
                "You are now a corrupt cop who negotiates rates. Somehow that feels worse than doing it for free."

                show screen outcome_panel("+10,000 CZK, +15 PCR HATRED. You named your price. That makes it real.")
                pause
                hide screen outcome_panel
            else:
                "'If I'm taking this kind of risk,' you say, 'I need compensation.'"
                "His face goes cold. The warmth drains out of the parking lot."
                "'You're not in a position to negotiate, JB. I have the recording. You have nothing.'"
                "'Delete the citation. Tonight. Or I send the audio to your Colonel.'"
                "You delete the citation. For free. At 2 AM. Alone at your desk."
                "He didn't pay. He didn't need to. He has the recording and you have nothing."

                show screen outcome_panel("+35 PCR HATRED. He called your bluff. You folded.")
                pause
                hide screen outcome_panel

        "Turn him in. Report everything. Burn yourself to burn him. (-25,000 CZK, +50 Hatred)":
            python:
                stats.increment_stats_value_money(-25000)
                stats.increment_stats_pcr_hatred(50)
                store.corrupt_chain_2 = False

            "'I'm going to report this,' you say. 'All of it. The bribe. This conversation. Everything.'"
            "For the first time, his composure cracks. Just a flicker."
            "'You'd destroy yourself to get to me?'"
            "'I'd destroy myself to stop being this.'"
            "He stares at you. Then he laughs. One short, dry laugh."
            "'Your funeral, officer.'"
            "He drives away."
            "You walk into the station. You return the 7,500 CZK. You file a report."
            "The next three hours are the longest of your life."
            "Internal affairs takes your statement. Your supervisor won't look at you."
            "The disciplinary board fines you 17,500 CZK. Accepting a bribe, failure to report, conduct unbecoming, damage to the reputation of the force."
            "You sign the papers. You pay every crown."
            "You are now under investigation. But the recording is evidence against him too."
            "25,000 CZK gone. The bribe returned. The fine paid. Your bank account gutted."
            "But the recording can't touch you anymore. And neither can he."

            show screen outcome_panel("-25,000 CZK (-7,500 returned, -17,500 fine), +50 PCR HATRED. The most expensive shower you've ever taken.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Corrupt Cop Chain — Part 3 (Day 18)
## THE VISIT — he walks into YOUR station
## ---------------------------------------------------------------------------

label re_corrupt_cop_3:

    scene bg_police_interior

    "DAY 18 — THE VISIT"

    "You're at your desk when the front door opens."
    "You don't look up. People come in all day. Lost wallets. Noise complaints. Parking disputes."
    "Then you hear the voice."
    "'Good afternoon. I'd like to report a minor traffic incident.'"
    "Your head snaps up."
    "The BMW driver. Standing at the reception desk. In your station. Three metres from your colleagues."
    "He's wearing a different suit. Navy blue. No tie. He looks like a concerned citizen."
    "Lieutenant Kovář takes his statement. A fender bender. Nothing serious. Standard paperwork."
    "He fills out the form politely. He answers every question."
    "Then he looks at you. Directly at you. And smiles."
    "'Excuse me — could I trouble you for a glass of water? I know it's a lot to ask.'"
    "Kovář nods at you. 'JB, grab the man some water.'"
    "You walk to the kitchen. He follows."
    "The moment the door closes, the mask drops."

    "'I need access to the vehicle registration database. One name. One plate. One address.'"
    "He says it the way you'd order coffee."
    "'Who?' you ask."
    "'That's not your concern. The name is on this paper. I need the registered address and the owner's full details.'"
    "He slides a folded note across the counter."
    "'I'm not—'"
    "He holds up his phone. Your voice comes out of it."

    "The recording. Day 6. The Litoměřice stretch. Every word. Every pause. Every silence where a 'no' should have been."
    "He lets it play for fifteen seconds. Then stops."
    "'This is a copy. There are others. On servers you will never find.'"
    "He puts the phone away."
    "'One name. One address. Then I walk out and you never see me again.'"
    "You look at the note. A name you don't recognize. A plate number."
    "Through the kitchen door you can hear Kovář typing. The station is full. Your colleagues are ten steps away."
    "None of them can help you."

    menu:
        "Give him the information.":
            pass

    "You sit down at the terminal."
    "You type the plate number. The system returns a name, an address, a phone number."
    "You write it on the back of the note. You hand it to him."
    "He reads it. Folds it. Puts it in his pocket."
    "'Thank you, officer. You've been very helpful.'"
    "He walks back to the reception desk. He shakes Kovář's hand."
    "'Lovely station. Very professional.'"
    "The door closes behind him."
    "You stand in the kitchen holding an empty glass."
    "You just gave a civilian access to a classified police database."
    "You don't know who the name belongs to. You don't know what he'll do with it."
    "You don't want to know."

    python:
        stats.increment_stats_pcr_hatred(30)
        store.corrupt_chain_3_completed = True

    show screen outcome_panel("+30 PCR HATRED. There is no going back from this.")
    pause
    hide screen outcome_panel

    return
