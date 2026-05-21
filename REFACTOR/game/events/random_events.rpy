################################################################################
## REFACTOR — Random Events (distilled v2)
##
## Each random event is now a Slay-the-Spire-style 2-option choice:
##   1 setup banner, 2-3 lines of context, 2 options with cost/reward visible
##   inline, 1-2 lines of resolution per branch.
################################################################################

## ---------------------------------------------------------------------------
## EVENT 1: Tel Aviv Professor
## Coding-skill check (≥35) or Biohacker auto-pass. Pass unlocks FLMod for BH.
## ---------------------------------------------------------------------------

label re_israeli_developer:

    scene bg_random_event
    play sound "audio/police_siren.mp3"
    play music "audio/random_event_bed.wav" fadein 1.5

    "TEL AVIV PROFESSOR"

    "A fender-bender. The professor steps out of the damaged Mercedes, ignoring the chaos."
    "He looks at you, ignoring the uniform entirely."
    "'You have intelligent eyes. Tell me — do you write code?'"

    python:
        _can_code = stats.coding_skill >= 35 or stats.player_class == "biohacker"

    menu:
        "Talk code. [[+30 Coding, BH: FLMod source]" if _can_code:
            python:
                stats.increment_stats_coding_skill(30)
                _bh = (stats.player_class == "biohacker")
                if _bh:
                    flmodafinil_unlocked = True

            "Twenty minutes of pointers, GIL, scaling. He nods. Hands you his GitHub on a folded card."

            if stats.player_class == "biohacker":
                "Then, quieter: 'I notice things. You optimise everything — including yourself.'"
                "He slips you a Telegram handle. CRL-40,940 source. You pocket it."
                window hide
                show screen outcome_panel("+30 CODING  |  [CRL-40,940 SOURCE UNLOCKED]  [BIOHACKER]")
            else:
                window hide
                show screen outcome_panel("+30 CODING SKILL.")
            pause
            hide screen outcome_panel

        "Stay silent. [[+10 Coding]":
            $ stats.increment_stats_coding_skill(10)
            "He shrugs. Gives you sixty seconds on abstraction layers anyway."
            "You learn something. The fear chokes the rest."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    $ store._nightmare_wolf_triggered = True

    "THE NIGHTMARE"

    "04:00 AM. A dream of body bags moving. A black husky pressing its nose to glass."
    "You wake up choking. The room is silent. The dream had teeth."

    menu:
        "Shake it off. [[+5 Hatred]":
            $ stats.increment_stats_pcr_hatred(5)
            "You don't forget."
            window hide
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Analyze it.":
            python:
                if stats.player_class == "dark_empath":
                    stats.increment_stats_pcr_hatred(-10)
                    stats.increment_stats_coding_skill(5)
                    _nw_msg = "[DARK EMPATH] You map the symbolism. The bag is the job. The wolf is the part of you that already left."
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
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

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
                window hide
                show screen outcome_panel("{} PCR HATRED{}".format(_ct_amt, _ct_tag))
            else:
                "You botch the rhythm of the conversation. She walks off. You feel worse than before."
                window hide
                show screen outcome_panel("+{} PCR HATRED (awkward).".format(_ct_amt))
            pause
            hide screen outcome_panel

        "Professional nod. [[no change]":
            "You move on. So does she."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE PAPERWORK"

    "Sergeant: 'JB. This report has your name on it. Stop signature, search authorization, evidence chain. It shouldn't.'"
    "You've never seen this case before."

    menu:
        "Fix it quietly. [[-5 Hatred, +1 Coding]":
            python:
                stats.increment_stats_pcr_hatred(-5)
                stats.increment_stats_coding_skill(1)
            "Forty-five minutes of database forensics. You find the bug. You file a quiet correction."
            "Your name comes off the doc. Nobody else finds out."
            window hide
            show screen outcome_panel("-5 PCR HATRED, +1 CODING SKILL.")
            pause
            hide screen outcome_panel

        "Escalate. [[+10 Hatred]":
            $ stats.increment_stats_pcr_hatred(10)
            "Internal Review opens an inquiry. Three colleagues are interviewed."
            "By Friday everyone knows you ratted. The atmosphere does not improve."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE OVERTIME"

    "Dispatch needs a double tonight. Cash bonus, no questions. The shift supervisor is already walking away."

    menu:
        "Take it. (+6,000 CZK) (BB: 0 Hatred. Other: +15 Hatred.)":
            python:
                stats.increment_stats_value_money(6000)
                if stats.player_class == "bodybuilder":
                    _ot_hat = 0
                    _ot_msg = "[BB] You sleep four hours and look fresh. The sergeant is suspicious."
                else:
                    stats.increment_stats_pcr_hatred(15)
                    _ot_hat = 15
                    _ot_msg = "Sixteen hours straight. By hour twelve you stop being a person and start being a function."
            "[_ot_msg]"
            window hide
            show screen outcome_panel("+6,000 CZK, +{} PCR HATRED.".format(_ot_hat))
            pause
            hide screen outcome_panel

        "Pass. [[no change]":
            "He blinks. Nobody says no. He shrugs and walks off."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

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
            window hide
            show screen outcome_panel("+5,000 CZK, +15 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Refuse. [[-5 Hatred]":
            $ stats.increment_stats_pcr_hatred(-5)
            "He looks at you for a long moment. Then nods. 'Fair enough.'"
            "Your spine straightens slightly."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE NOTE"

    "A care home. An elderly woman. The smell. The note on the bedside table."
    "'Sorry for the trouble.'"

    menu:
        "Process professionally. [[+15 Hatred, +1 Coding]":
            python:
                stats.increment_stats_pcr_hatred(15)
                stats.increment_stats_coding_skill(1)
            "You document everything correctly. The paperwork is clean. You sleep poorly for three days."
            window hide
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
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

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
                    _usb_out = "+20 CODING SKILL [FLAG: usb_evidence]"
                else:
                    _usb_msg = "A folder of badly-organized scripts and a corrupted Excel. You learn from the chaos."
                    _usb_out = "+10 CODING SKILL."
            "[_usb_msg]"
            window hide
            show screen outcome_panel(_usb_out)
            pause
            hide screen outcome_panel

        "Turn it in. [[+5 Hatred]":
            $ stats.increment_stats_pcr_hatred(5)
            "Lieutenant Kovář takes it without making eye contact. You never see it again."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE CALL"

    "An older man at the front desk: 'Pane policisto, my Turkish neighbor — he keeps asking my bank details.'"
    "'I think he's running a scam. Or maybe I'm paranoid.'"

    menu:
        "Follow up. [[+10 Coding]":
            $ stats.increment_stats_coding_skill(10)
            "An empty Airbnb. Three burner phones in a drawer. You run the IPs."
            "You find a fraud ring you can't dismantle alone — but you understand the topology now."
            window hide
            show screen outcome_panel("+10 CODING SKILL (system mapping).")
            pause
            hide screen outcome_panel

        "Dismiss. [[+5 Hatred]":
            $ stats.increment_stats_pcr_hatred(5)
            "He leaves. He looks smaller than when he came in."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE PRINTER"

    "The printer eats your incident report. You have ten minutes to get it to the prosecutor."

    menu:
        "Slam it.":
            python:
                if stats.player_class == "bodybuilder":
                    stats.increment_stats_coding_skill(5)
                    _pr_msg = "[BB] One palm strike. The drum unjams. The page emerges. Sergeant slow-claps. You bow."
                    _pr_out = "+5 CODING (you fixed it by being correct about the world). [BB]"
                else:
                    stats.increment_stats_pcr_hatred(15)
                    _pr_msg = "You break the front panel. The printer makes a sound it shouldn't. You owe IT 4,000 CZK."
                    _pr_out = "+15 PCR HATRED."
            "[_pr_msg]"
            window hide
            show screen outcome_panel(_pr_out)
            pause
            hide screen outcome_panel

        "Debug it. [[+5 Coding]":
            $ stats.increment_stats_coding_skill(5)
            "You find the rolled paper. You release it. The printer respects you, briefly."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE OLD MAN"

    "An old man at a tram stop, talking about how things were better in 1985."
    "He sees the uniform. He locks onto you. 'Officer. You have a minute?'"

    menu:
        "Listen. [[-10 Hatred]":
            $ stats.increment_stats_pcr_hatred(-10)
            "He talks for six minutes. Beer was 1.20 Kčs. The trams ran on time. His wife died in 2003."
            "You don't say much. He doesn't need you to."
            window hide
            show screen outcome_panel("-10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Move him along. [[+10 Hatred]":
            $ stats.increment_stats_pcr_hatred(10)
            "He shuffles off. He doesn't look back."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE STACK"

    "200 incident reports, due tomorrow. Half are duplicates. The form fields are inconsistent."

    menu:
        "Stack up.":
            python:
                if stats.player_class == "biohacker":
                    stats.increment_stats_coding_skill(20)
                    _st_msg = "[BH] You drop into deep work. Four hours feels like forty minutes. Done."
                    _st_out = "+20 CODING SKILL [BH: hyperfocus]"
                else:
                    stats.increment_stats_pcr_hatred(15)
                    _st_msg = "You dial in. The system breaks twice. Your back hurts. You finish at 3 AM."
                    _st_out = "+15 PCR HATRED."
            "[_st_msg]"
            window hide
            show screen outcome_panel(_st_out)
            pause
            hide screen outcome_panel

        "Manual grind. [[+10 Hatred, +1 Coding]":
            python:
                stats.increment_stats_pcr_hatred(10)
                stats.increment_stats_coding_skill(1)
            "You finish at 4 AM. You learn the schema by accident."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE OUTAGE"

    "'Dispatch is offline.' The room freezes. Three patrols are mid-pursuit. The radio works. The terminal doesn't."

    menu:
        "Reboot it. [[+10 Coding]":
            $ stats.increment_stats_coding_skill(10)
            "You restart the service. You clear the lock file. You re-establish the database connection."
            "Dispatch is back online in eleven minutes. The unit chief looks at you for the first time in three years."
            window hide
            show screen outcome_panel("+10 CODING SKILL.")
            pause
            hide screen outcome_panel

        "Use the radio. [[-5 Hatred]":
            $ stats.increment_stats_pcr_hatred(-5)
            "Voice channel only, like the 90s. Things move slower. Nobody dies. You like it."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE TESLA"

    "Tesla Model S. 220 km/h. The driver is in his thirties, AirPods in, no panic at all."
    "He hands you a business card before he hands you his license. CTO. Fintech. Smug."

    menu:
        "Take the card.":
            python:
                stats.increment_stats_coding_skill(5)
                if stats.player_class == "biohacker":
                    stats.increment_stats_coding_skill(3)
                    _tb_msg = "[BH] You ask three sharp questions about his stack. He's impressed enough to follow up."
                    _tb_out = "+8 CODING SKILL [BH: networking]"
                else:
                    _tb_msg = "You bookmark him in your head. You'll Google the company later."
                    _tb_out = "+5 CODING SKILL (networking flag)."
            "[_tb_msg]"
            window hide
            show screen outcome_panel(_tb_out)
            pause
            hide screen outcome_panel

        "Write the ticket. [[+1,500 CZK]":
            $ stats.increment_stats_value_money(1500)
            "He pays without arguing. He drives at exactly 130 km/h afterwards."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE WHISPER"

    "A colleague you barely know corners you by the coffee machine."
    "'I've got something on Lieutenant Kovář. Expense reports. Doctored. Want to know?'"

    menu:
        "Listen. [[CARD: STACK TRACE]":
            "He talks for twelve minutes. Dates, amounts, account numbers. You memorize them."
            "You walk away with information that has weight."
            python:
                offer_card("stack_trace", "INFORMANT")
            window hide
            show screen outcome_panel("[STACK TRACE offered]")
            pause
            hide screen outcome_panel

        "Pass. [[+5 Hatred]":
            $ stats.increment_stats_pcr_hatred(5)
            "He nods. He walks away. Now you wonder."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE EVAL"

    "Mandatory department psych eval. The therapist is in her forties, kind eyes, a clipboard."
    "'How are you feeling about the work, JB?'"

    menu:
        "Be honest. [[-10 Hatred]":
            $ stats.increment_stats_pcr_hatred(-10)
            "She nods slowly. Doesn't write it down. Says: 'I'm not your enemy. I'll mark you fit. Take care of yourself.'"
            window hide
            show screen outcome_panel("-10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Perform sanity. [[+5 Hatred]":
            $ stats.increment_stats_pcr_hatred(5)
            "You hear yourself say things the academy taught you to say. She marks you fit."
            "The lie taxes you on the drive home."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

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
                    _sc_extra = " [DARK EMPATH: read his pauses, +5 extra Coding]"
            "Forty-seven minutes. He stays. By the time the ambulance gets there, he's sitting on the curb crying."
            window hide
            show screen outcome_panel("-15 PCR HATRED, +5 CODING SKILL.{}".format(_sc_extra))
            pause
            hide screen outcome_panel

        "Transfer it. [[+10 Hatred]":
            $ stats.increment_stats_pcr_hatred(10)
            "You patch him to the suicide hotline. The call drops during the transfer."
            "You don't know what happened. The shift continues."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

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
            window hide
            show screen outcome_panel("-1,500 CZK, -10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Skip it. [[+5 Hatred]":
            $ stats.increment_stats_pcr_hatred(5)
            "You see the photos on Monday. He looks happy. You look at your reflection."
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

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
                    _ci_out = "+20 CODING, -15 PCR HATRED [INTERVIEW PASSED]"
                else:
                    stats.increment_stats_coding_skill(5)
                    stats.increment_stats_pcr_hatred(15)
                    _ci_msg = "Async Python catches you. You hear yourself say 'callback hell' and mean something else. Dispatch interrupts the call."
                    _ci_out = "+5 CODING (you learned), +15 PCR HATRED."

            "[_ci_msg]"
            window hide
            show screen outcome_panel(_ci_out)
            pause
            hide screen outcome_panel

        "Reschedule. [[+3 Coding, +10 Hatred]":
            python:
                stats.increment_stats_coding_skill(3)
                stats.increment_stats_pcr_hatred(10)
            "They reply: 'Sure! Friday at 14:00.' Friday is your 12-hour shift."
            "You stare at the calendar. You reply: 'Perfect.'"
            window hide
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
    play music "audio/random_event_bed.wav" fadein 1.5

    "THE UPDATE"

    "IT pushed an update at 06:00. By 07:30 nothing works."
    "Error: 'RuntimeError: Database migration failed.' You actually understand what that means."

    python:
        _su_chance = min((stats.coding_skill * 100) // 60, 100)

    menu:
        "[[BH] KNOWN FAILURE MODE — You've seen this exact error on a dev forum at 2 AM." if stats.player_class == "biohacker":
            python:
                stats.increment_stats_coding_skill(15)
                stats.increment_stats_pcr_hatred(-20)
                stats.increment_stats_value_money(2500)
            "Three commands in a terminal. The screen turns green. Silence. Sergeant: 'JB. How did you—'"
            "You leave before he can take the bonus back."
            window hide
            show screen outcome_panel("+15 CODING, -20 PCR HATRED, +2,500 CZK [BH: known fix]")
            pause
            hide screen outcome_panel

        "[[DE] FIND HORA — Constable Hora isn't panicking. He knows something." if stats.player_class == "dark_empath":
            python:
                stats.increment_stats_pcr_hatred(-10)
                stats.increment_stats_coding_skill(5)
            "Hora: 'The v1.4.2 rollback re-enables the legacy ODBC connector. Run the old client on desktop four.'"
            "You do. It works. You give Hora the coffee meant for the sergeant."
            window hide
            show screen outcome_panel("-10 PCR HATRED, +5 CODING [DE: extracted the workaround]")
            pause
            hide screen outcome_panel

        "Fix it. [[CODING CHECK: [_su_chance]%%]":
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
            window hide
            show screen outcome_panel(_su_out)
            pause
            hide screen outcome_panel

        "Walk out. [[+10 Hatred, +2 Coding]":
            python:
                stats.increment_stats_pcr_hatred(10)
                stats.increment_stats_coding_skill(2)
            "You spend patrol thinking about the error message. Better communication than most humans you know."
            window hide
            show screen outcome_panel("+10 PCR HATRED, +2 CODING (ambient learning).")
            pause
            hide screen outcome_panel

    return

