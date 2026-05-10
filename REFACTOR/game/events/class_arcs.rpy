################################################################################
## REFACTOR — Class-Specific Multi-Stage Arcs (GOTY v2)
##
## Each class has a 3-stage NPC relationship arc:
##   BB → THE TRAINER (gym mentor → competition slot → competition day)
##   DE → THE KOVÁŘ AFFAIR (notice → confrontation → choice)
##   BH → THE TELEGRAM SOURCE (online contact → lab visit → test subject)
##
## Stages fire on day-windowed checks during random-event rolls. Player class
## must match. Stage advances via store.{bb|de|bh}_arc_stage.
##
## Each stage is Slay-the-Spire-distilled: setup hook + 2-3 options.
################################################################################


## ---------------------------------------------------------------------------
## BB ARC — THE TRAINER
## ---------------------------------------------------------------------------

label re_bb_trainer_intro:
    scene bg_random_event
    play sound "audio/police_siren.mp3"

    python:
        store._phone_notifications.append("Vladek: 'Talk after your set. — V'")

    "[[Vladek — Stage 1]"
    "THE TRAINER"

    "Vladek wipes his forehead after your last set. Looks at you a long second."
    "'JB. I've been watching you. You have the frame, the discipline. You're wasting it on uniformed bullshit.'"
    "'I run a private programme. I'd take you on. Free of charge.'"

    menu:
        "Take the offer. [[+1 SOMA, -10 Hatred, arc continues]":
            python:
                store.bb_arc_stage = 1
                add_soma(1)
                stats.increment_stats_pcr_hatred(-10)
            "He nods. 'Tomorrow. 5 AM. Don't be late.'"
            "You haven't trained in front of someone who actually believes in you in three years."
            show screen outcome_panel("+1 SOMA, -10 PCR HATRED  ·  [Vladek's programme opened]")
            pause
            hide screen outcome_panel

        "Decline. [[arc closes]":
            python:
                store.bb_arc_stage = -1
            "He shrugs. 'Suit yourself. The body keeps score either way.'"
            "He doesn't make the offer twice."
            show screen outcome_panel("ARC CLOSED. Vladek won't ask again.")
            pause
            hide screen outcome_panel

    return


label re_bb_competition_offer:
    scene bg_random_event
    play sound "audio/police_siren.mp3"

    python:
        _bb_entry_cost = adjusted_cost(8000)

    "[[Vladek — Stage 2]"
    "COMPETITION SLOT"

    "Vladek's voice on the phone: 'JB. I have a slot. National amateur strongman, three weeks out. Entry's [_bb_entry_cost] CZK. You'd pay it back in winnings or in pride.'"
    "'You'd be the only cop in the field. They'd remember you.'"

    menu:
        "Register. [[-[_bb_entry_cost] CZK, arc continues]" if stats.available_money >= _bb_entry_cost:
            python:
                stats.try_spend_money(_bb_entry_cost)
                store.bb_arc_stage = 2
                add_soma(2)
            "You wire the entry. Vladek answers in three minutes: 'Good. Now we work.'"
            "Three weeks of doubled volume. Your back hurts in places you didn't know existed."
            show screen outcome_panel("-{} CZK, +2 SOMA  ·  [Competition day approaching]".format(_bb_entry_cost))
            pause
            hide screen outcome_panel

        "Pass. [[arc closes]":
            python:
                store.bb_arc_stage = -1
            "He doesn't argue. He doesn't call again."
            show screen outcome_panel("ARC CLOSED. Vladek won't ask twice.")
            pause
            hide screen outcome_panel

    return


label re_bb_competition_day:
    scene bg_random_event
    play sound "audio/tension_theme.mp3"

    "[[Vladek — Stage 3]"
    "COMPETITION DAY"

    "Big arena. Atlas stones, log press, deadlift ladder. Sixteen competitors. You're number 14."
    "Your hands are chalked. Vladek is at the rail, arms folded, face unreadable."
    "First stone. 130kg. The bar bends. The crowd watches."

    python:
        ## Performance scales with SOMA accumulated through the arc + class baseline
        _bb_strength = stats.coding_skill // 30 + store.bb_soma + (1 if stats.player_class == "bodybuilder" else 0)
        _bb_chance = min(35 + _bb_strength * 8, 90)
        _bb_all_in_label = "GO ALL IN — Push for the win. [skill check {}%]".format(_bb_chance)

    "Your training, your form, your soma — call it [_bb_strength]. Performance ceiling: [_bb_chance]%%."

    menu:
        "[_bb_all_in_label]":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _bb_chance:
                    stats.increment_stats_value_money(35000)
                    stats.increment_stats_pcr_hatred(-30)
                    add_soma(5)
                    store.bb_arc_stage = 3
                    store._bb_arc_won = True
                    _bb_msg = "You finish 2nd. Prize money: 35,000 CZK. Vladek says one word as you step off the platform: 'Good.'"
                    _bb_out = "+35,000 CZK, -30 PCR HATRED, +5 SOMA. [You left your body on the platform]"
                else:
                    stats.increment_stats_value_money(2000)
                    stats.increment_stats_pcr_hatred(15)
                    store.bb_arc_stage = 3
                    _bb_msg = "Top half but no podium. 2,000 CZK consolation. Vladek nods. 'Next year.'"
                    _bb_out = "+2,000 CZK, +15 PCR HATRED. (Honourable. Not enough.)"
            "[_bb_msg]"
            show screen outcome_panel(_bb_out)
            pause
            hide screen outcome_panel
            ## Podium win → grant Vladek's Form (boss-rarity arc reward) + achievement
            python:
                if getattr(store, '_bb_arc_won', False):
                    unlock_achievement("vladeks_pupil")
                    offer_card_solo("vladeks_form", "VLADEK 3/3 — COMPETITION WON")

        "Play it safe. [[guaranteed +5,000 CZK, no SOMA]":
            python:
                stats.increment_stats_value_money(5000)
                stats.increment_stats_pcr_hatred(-5)
                store.bb_arc_stage = 3
            "You skip the deadlift ladder's top weight. Bottom-half finish. The body intact."
            "Vladek says nothing on the drive home. The silence is heavier than a barbell."
            show screen outcome_panel("+5,000 CZK, -5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## DE ARC — THE KOVÁŘ AFFAIR
## ---------------------------------------------------------------------------

label re_de_kovar_eyes:
    scene bg_random_event
    play sound "audio/police_siren.mp3"

    python:
        store._phone_notifications.append("Internal note: Lt. Kovář — pattern flagged.")

    "[[Kovář — Stage 1]"
    "THE EXPENSE REPORTS"

    "You're at your desk. The break room is empty. Lt. Kovář thinks no one's watching."
    "He's scrolling through his phone — fast, deliberately, his thumb pausing in patterns that aren't social media."
    "Banking app. Then a Signal message. Then the bank app again."
    "His left hand drums on the table in a 4-4 rhythm only nervous men do."

    menu:
        "Read him carefully. [[arc continues, +5 Coding]":
            python:
                store.de_arc_stage = 1
                store.de_profiles["lieutenant"] = store.de_profiles.get("lieutenant", 0) + 1
                stats.increment_stats_coding_skill(5)
            "Three withdrawals today. Same time pattern as last Tuesday. You file the rhythm."
            "He looks up. He sees you not-quite-watching. His drumming stops."
            "The room is quieter than it should be."
            show screen outcome_panel("+5 CODING SKILL, [Kovář profile +1]  ·  [Engagement opened]")
            pause
            hide screen outcome_panel

        "Look away. [[arc closes]":
            python:
                store.de_arc_stage = -1
            "You go back to your screen."
            "Some patterns don't need confirming. Knowing isn't the same as having."
            "You won't notice him again. Even when he wants you to."
            show screen outcome_panel("ARC CLOSED.")
            pause
            hide screen outcome_panel

    return


label re_de_kovar_warning:
    scene bg_random_event
    play sound "audio/tension_theme.mp3"

    "[[Kovář — Stage 2]"
    "THE WARNING"

    "Kovář corners you in the corridor. He smiles. The smile doesn't reach the eyes that have been counting your shifts."
    "'JB. You and I should talk.' He pulls you into an empty interrogation room."
    "'I noticed your noticing.'"
    "He drops a thin folder on the table. 'I have a file on you too. Off-duty bouncer work. Unauthorised. The paragraph fits, you know.'"
    "'So we have an exchange to make.'"

    menu:
        "Defer. [[arc continues, profile deepens]":
            python:
                store.de_arc_stage = 2
                store.de_profiles["lieutenant"] = store.de_profiles.get("lieutenant", 0) + 2
                stats.increment_stats_pcr_hatred(-5)
            "He lays it out. He wants you to delete a flagged report. In exchange he buries the bouncer file forever."
            "You don't say yes. You don't say no. You let him talk."
            "His foot taps three times. He's nervous. He NEEDS this."
            show screen outcome_panel("-5 PCR HATRED, [Kovář profile +2]  ·  [Final stage incoming]")
            pause
            hide screen outcome_panel

        "Walk out. [[+15 Hatred, arc closes]":
            python:
                store.de_arc_stage = -1
                stats.increment_stats_pcr_hatred(15)
            "He blinks. He didn't expect that move. You leave him in the room."
            "Three days later you find his file on your desk. He never escalates it. He never speaks to you again."
            show screen outcome_panel("+15 PCR HATRED. (Arc closed. Kovář is no longer a vector.)")
            pause
            hide screen outcome_panel

    return


label re_de_kovar_choice:
    scene bg_random_event
    play sound "audio/sevirra_lenoloc.mp3"

    "[[Kovář — Stage 3]"
    "THE LIST"

    "Kovář hands you a memory stick on a quiet Tuesday. 'The flagged report is folder 4. Delete it tonight. Then we're square.'"
    "You plug it in on a personal laptop in your apartment."
    "Folder 4 is a single PDF. The flagged report is for an anti-trafficking case. Three girls, ages 14, 15, 17. Kovář is named as the responding officer."
    "He didn't take a kickback. He {i}was{/i} the kickback."

    menu:
        "Delete the report. [[+25,000 CZK, +20 Hatred — arc closes dark]":
            python:
                store.de_arc_stage = 3
                stats.increment_stats_value_money(25000)
                stats.increment_stats_pcr_hatred(20)
                store._de_kovar_complicit = True
            "You delete it. Your hands don't shake. That's the part that scares you most."
            "The 25,000 CZK arrives the next day in an envelope on your driver's seat."
            "You don't sleep for three nights."
            show screen outcome_panel("+25,000 CZK, +20 PCR HATRED. [You're complicit now]")
            pause
            hide screen outcome_panel

        "Expose him. [[-15 Hatred, +30 Coding, arc closes clean]":
            python:
                store.de_arc_stage = 3
                stats.increment_stats_pcr_hatred(-15)
                stats.increment_stats_coding_skill(30)
                store._de_kovar_exposed = True
            "You build a static site overnight. HTML, CSS, one Python script to format the PDF metadata."
            "You email the link to two journalists and one anti-trafficking NGO."
            "Two weeks later Kovář is suspended pending criminal investigation."
            "You never see the news at the station. You don't need to."
            show screen outcome_panel("-15 PCR HATRED, +30 CODING. [KOVÁŘ EXPOSED]")
            pause
            hide screen outcome_panel
            ## Expose path → grant The Dossier card + achievement
            python:
                unlock_achievement("bring_the_lt")
                offer_card("the_dossier", "ARC: KOVÁŘ EXPOSED")

        "Offer a trade. [[-5 Hatred, +10 Coding, leverage]":
            python:
                store.de_arc_stage = 3
                stats.increment_stats_pcr_hatred(-5)
                stats.increment_stats_coding_skill(10)
                store._de_kovar_leveraged = True
            "You meet him in the parking lot. You show him the file's been backed up to three encrypted servers."
            "'You don't take another kickback. Ever. Or this goes to the press in 24 hours.'"
            "His face goes white. He nods once. He gets in his car."
            "You have power now. Power has weight."
            show screen outcome_panel("-5 PCR HATRED, +10 CODING. [KOVÁŘ LEVERAGED — quiet ending]")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## BH ARC — THE TELEGRAM SOURCE
## (Requires re_israeli_developer + Biohacker class — flmodafinil_unlocked flag)
## ---------------------------------------------------------------------------

label re_bh_telegram_meet:
    scene bg_random_event
    play sound "audio/police_siren.mp3"

    python:
        store._phone_notifications.append("Telegram: K-Café, Vinohrady, 14:00. Bring nothing.")

    "[[The Supplier — Stage 1]"
    "THE CONTACT"

    "The Telegram handle the Tel Aviv professor gave you. You finally pinged him."
    "Reply in 4 minutes: 'In Prague Friday. Coffee. K-Café, Vinohrady, 14:00. Bring nothing. Wear nothing identifying.'"

    menu:
        "Go. [[arc continues, +5 Coding]":
            python:
                store.bh_arc_stage = 1
                stats.increment_stats_coding_skill(5)
            "He's mid-30s, thin, glasses, no name. He doesn't shake your hand."
            "'You are JB. I am the supplier. I make compounds. I do not sell them. I {i}share{/i} them with researchers I trust.'"
            "He slides a small envelope across. 'A starter sample. Real CRL-40,940. The kind your government cannot legally buy.'"
            "'Take it. We talk again when I am back in three weeks.'"
            "He leaves. He pays for both coffees in cash."
            show screen outcome_panel("+5 CODING. [Supplier line opened — sample on you]")
            pause
            hide screen outcome_panel

        "Ghost him. [[arc closes]":
            python:
                store.bh_arc_stage = -1
            "You delete the conversation. Then the app."
            "You go back to T4 peptides. They will have to be enough."
            show screen outcome_panel("ARC CLOSED. (You're not built for the gray market.)")
            pause
            hide screen outcome_panel

    return


label re_bh_sketchy_lab:
    scene bg_random_event
    play sound "audio/coding_in_snow_theme.mp3"

    "[[The Supplier — Stage 2]"
    "THE LAB"

    "Three weeks later. He texts an address — a Žižkov basement — and a time."
    "You arrive at midnight. Two doors, an LED panel, a key code."
    "Inside: a twenty-square-metre lab with HPLC equipment that costs more than your apartment."
    "He is wearing safety glasses. He gestures at three vials on a bench."
    "'Three new compounds. I synthesised them last week. They have no name yet. I have no human data.'"
    "'I would like to know what they do.'"

    menu:
        "Take a vial. [[+15 Coding, +10 Hatred]":
            python:
                store.bh_arc_stage = 2
                stats.increment_stats_coding_skill(15)
                stats.increment_stats_pcr_hatred(10)
            "You take vial #2. He nods like a teacher seeing a student finally understand the lesson."
            "'Log everything. HRV, sleep, mood. Send weekly.'"
            "You leave with a glass cylinder of unknown chemistry in your pocket."
            "Some doors only open once."
            show screen outcome_panel("+15 CODING, +10 PCR HATRED. [CRL-40,940 vial in your bag]")
            pause
            hide screen outcome_panel

        "Ask instead. [[+25 Coding, no compound]":
            python:
                store.bh_arc_stage = 2
                stats.increment_stats_coding_skill(25)
                store._bh_taught_synth = True
                unlock_achievement("compound_knowledge")
            "He stops. Looks at you. Then smiles for the first time."
            "'This is the right answer.'"
            "Three hours of organic chemistry. The kind universities don't teach because the precursors are scheduled."
            "You leave with notes. Not compounds. Notes."
            show screen outcome_panel("+25 CODING. [Synthesis notes — no contraband on you]")
            pause
            hide screen outcome_panel

        "Walk out. [[arc closes, -5 Hatred]":
            python:
                store.bh_arc_stage = -1
                stats.increment_stats_pcr_hatred(-5)
            "He doesn't argue. He doesn't follow. The door closes behind you."
            "You drive home with cold hands and clear eyes."
            show screen outcome_panel("-5 PCR HATRED. (You drew the line. Some lines hold.)")
            pause
            hide screen outcome_panel

    return


label re_bh_test_subject:
    scene bg_random_event
    play sound "audio/tension_theme.mp3"

    "[[The Supplier — Stage 3]"
    "THE ASK"

    "He wants follow-up. Not vague. Specific."
    "'Compound #2 is showing promise. I need a structured trial. 21 days. Daily dose. Standardised cognitive battery, sleep tracking, blood draw at day 14.'"
    "'You would be patient zero. The data would be yours and mine.'"

    menu:
        "Agree. [[+30 Coding, +25 Hatred, dependency risk]":
            python:
                store.bh_arc_stage = 3
                stats.increment_stats_coding_skill(30)
                stats.increment_stats_pcr_hatred(25)
                ## Risk: triggers nootropic_dependency permanently
                global nootropic_dependency
                nootropic_dependency = True
                store._bh_trial_subject = True
            "Day 1: HRV up 12%%. Sleep efficiency up. Subjective focus: 'glass-clear'."
            "Day 14: blood draw clean. He calls. 'You are responding well. Continue.'"
            "Day 21: you cannot remember what your baseline felt like."
            "Some optimisations are not reversible."
            show screen outcome_panel("+30 CODING, +25 PCR HATRED. [You're dependent — withdrawal in the fight]")
            pause
            hide screen outcome_panel
            ## Trial subject → grant The Compound card + achievement
            python:
                unlock_achievement("subject_zero")
                offer_card("the_compound", "ARC: TRIAL SUBJECT")

        "Refuse. [[+10 Coding from refusing]":
            python:
                store.bh_arc_stage = 3
                stats.increment_stats_coding_skill(10)
                store._bh_refused_trial = True
            "He nods. 'Understood. The synthesis notes are yours regardless. Don't be a stranger.'"
            "You feel the weight of the decision lift, then settle. Different weight. Familiar shape."
            show screen outcome_panel("+10 CODING. (You bought your nervous system back.)")
            pause
            hide screen outcome_panel

        "Counter. [[risk: 50/50]":
            python:
                _bh_roll = __import__('random').randint(1, 100)
                store.bh_arc_stage = 3
                if _bh_roll <= 50:
                    stats.increment_stats_value_money(40000)
                    stats.increment_stats_coding_skill(20)
                    stats.increment_stats_pcr_hatred(20)
                    store._bh_trial_paid = True
                    _bh_msg = "He pauses. Then nods. 'Cash. Anonymous. 40,000 CZK on completion. Don't ask my name.'"
                    _bh_out = "+40,000 CZK, +20 CODING, +20 PCR HATRED. [Paid trial — anonymous]"
                else:
                    stats.increment_stats_pcr_hatred(15)
                    _bh_msg = "He stares at you for ten seconds. Then he stands. 'You misunderstand who I am. Goodbye, JB.'"
                    _bh_out = "+15 PCR HATRED. (Arc closed. He doesn't reply again.)"
            "[_bh_msg]"
            show screen outcome_panel(_bh_out)
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## ARC GATE — called from random_event_check before normal pool roll.
## Returns a class-arc label name to fire, or None.
## ---------------------------------------------------------------------------

init python:

    def class_arc_check():
        """If the player is class X and the right day window + arc stage matches,
        return the class-arc label to fire. Otherwise None.

        Random events fire only on days 9, 15, 21 (every 3rd day, with special-event
        exclusions). Arcs aim to fire one stage per random-event day.

        Day windows:
          Stage 1: 6-12 (catches day 9)
          Stage 2: 13-18 (catches day 15)
          Stage 3: 19-21 (catches day 21)

        Arc stages: 0 (not started), 1/2/3 (current stage in progress or completed),
                    -1 (player closed the arc).
        """
        if stats is None or day_cycle is None:
            return None

        d = day_cycle.current_day
        cls = stats.player_class
        if cls == "bodybuilder":
            stage = getattr(store, 'bb_arc_stage', 0)
            if stage == 0 and 6 <= d <= 12:
                return "re_bb_trainer_intro"
            if stage == 1 and 13 <= d <= 18:
                return "re_bb_competition_offer"
            if stage == 2 and 19 <= d <= 21:
                return "re_bb_competition_day"
        elif cls == "dark_empath":
            stage = getattr(store, 'de_arc_stage', 0)
            if stage == 0 and 6 <= d <= 12:
                return "re_de_kovar_eyes"
            if stage == 1 and 13 <= d <= 18:
                return "re_de_kovar_warning"
            if stage == 2 and 19 <= d <= 21:
                return "re_de_kovar_choice"
        elif cls == "biohacker":
            stage = getattr(store, 'bh_arc_stage', 0)
            ## BH arc gated by Israeli Developer event firing first (flmod source).
            ## Wider windows so Israeli + arc can both unlock in a single run.
            _flmod = getattr(store, 'flmodafinil_unlocked', False)
            if stage == 0 and 6 <= d <= 15 and _flmod:
                return "re_bh_telegram_meet"
            if stage == 1 and 13 <= d <= 21:
                return "re_bh_sketchy_lab"
            if stage == 2 and 19 <= d <= 23:
                return "re_bh_test_subject"
        return None

    def class_arc_pre_colonel_check():
        """Last-resort firing of any unfinished class arc before the colonel fight.
        Called twice from colonel_event so a player with stages 2 and 3 still pending
        sees both before the deck battle starts. Returns a label name or None.
        """
        if stats is None:
            return None
        cls = stats.player_class
        if cls == "bodybuilder":
            stage = getattr(store, 'bb_arc_stage', 0)
            if stage == 1:
                return "re_bb_competition_offer"
            if stage == 2:
                return "re_bb_competition_day"
        elif cls == "dark_empath":
            stage = getattr(store, 'de_arc_stage', 0)
            if stage == 1:
                return "re_de_kovar_warning"
            if stage == 2:
                return "re_de_kovar_choice"
        elif cls == "biohacker":
            stage = getattr(store, 'bh_arc_stage', 0)
            if stage == 1:
                return "re_bh_sketchy_lab"
            if stage == 2:
                return "re_bh_test_subject"
        return None
