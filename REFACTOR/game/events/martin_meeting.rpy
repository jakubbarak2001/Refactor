################################################################################
## REFACTOR - Arc II: The Martin Meeting (Day 24)
## Ported verbatim from martin_meeting_event.py — all 8 phases
################################################################################

## Affection points tracked as a screen-level variable
default martin_affection = 0
## MM outfit picked in Phase 1 — drives JB sprite in Phase 2+
default mm_outfit = "hoodie"

label martin_meeting:

    ## Autosave: before Martin meeting (Day 25)
    $ renpy.save("auto-day25-martin", "Day 25 — The Martin Meeting")

    python:
        store._phone_notifications.append("Martin: 'Cafe. 11:30. Don't be late.'")

    $ martin_affection = 0
    $ mm_outfit = "hoodie"

    play music "audio/martin_meeting_event_the_arrival.mp3" fadein 1.0

    call screen arc_title_card("II", "THE AWAKENING") with arc_fade
    scene black
    scene bg_cafe with fade_from_black
    "DAY 25 — 11:30 AM"

    show screen mm_affection_panel

    ## First-time affection tutorial — early-returns if already seen.
    call tutorial_affection_first_seen from _call_tutorial_affection_first_seen

    ## DE bonuses are now earned inline (in P2 Listen branch + P4 read-Martin
    ## narration block) — no more unconditional auto-stack from the orchestrator.

    ## Phase 1: Preparation
    call martin_phase1_preparation from _call_martin_phase1_preparation

    ## Phase 2: Meeting
    call martin_phase2_meeting from _call_martin_phase2_meeting

    ## Phase 3: Drop the Bomb
    call martin_phase3_bomb from _call_martin_phase3_bomb

    ## Phase 4: Coding Reality Check
    call martin_phase4_coding_check from _call_martin_phase4_coding_check

    ## Phase 5: Financial Reality Check
    call martin_phase5_money_check from _call_martin_phase5_money_check

    ## Phase 6: Hatred Motivation Check
    call martin_phase6_hatred_check from _call_martin_phase6_hatred_check

    ## Phase 6.5: The Dark Question (the swing — biggest single point swing)
    call martin_phase_dark_question from _call_martin_phase_dark_question

    ## Phase 6.75: The Price
    call martin_phase_the_price from _call_martin_phase_the_price

    ## Phase 7: Timing Decision
    call martin_phase7_timing from _call_martin_phase7_timing

    ## Phase 8: Ending / Parting Gift
    call martin_phase8_ending from _call_martin_phase8_ending

    hide screen mm_affection_panel

    return


## ---------------------------------------------------------------------------
## Phase 1: Preparation and clothing choice
## ---------------------------------------------------------------------------

label martin_phase1_preparation:

    scene bg_cafe

    "Martin quit the force nine months ago. Everyone said he was crazy. He's doing great."
    "Lunch at a decent restaurant. He always cared about image. You don't, much."

    menu:
        "Splurge — designer fit. (-12,500 CZK, +1 AFFECTION)":
            python:
                _polo_cost = adjusted_cost(12500)
                if stats.try_spend_money(_polo_cost):
                    martin_affection += 1
                    mm_outfit = "polo"
                    _p1text  = "Polo, watch, the works. You look like a civilian."
                    _p1outcome = "- {:,} CZK, +1 AFFECTION.".format(_polo_cost)
                else:
                    _p1text  = "Card declined. You go in your old clothes."
                    _p1outcome = "NO CHANGE (Insufficient funds)."

            "[_p1text]"
            window hide
            show screen outcome_panel(_p1outcome)
            pause
            hide screen outcome_panel

        "Modest — cut and a sharp shirt. (-2,500 CZK)":
            python:
                _cut_cost = adjusted_cost(2500)
                if stats.try_spend_money(_cut_cost):
                    mm_outfit = "collar"
                    _p1text  = "Fresh cut. New shirt. You look like you tried."
                    _p1outcome = "- {:,} CZK.".format(_cut_cost)
                else:
                    _p1text  = "Card declined. You go in your old clothes."
                    _p1outcome = "NO CHANGE (Insufficient funds)."

            "[_p1text]"
            window hide
            show screen outcome_panel(_p1outcome)
            pause
            hide screen outcome_panel

        "Free. (-1 AFFECTION)":
            python:
                martin_affection -= 1
            "You go in the hoodie. Martin will notice."
            window hide
            show screen outcome_panel("-1 AFFECTION.")
            pause
            hide screen outcome_panel

        "{color=#ff6633}{b}[[BODYBUILDER]{/b}{/color} Hit the gym first. (+1 AFFECTION, free)" if stats.player_class == "bodybuilder" and (getattr(store, 'gym_sessions', 0) >= 5 or getattr(store, 'bb_soma', 0) >= 5):
            python:
                martin_affection += 1
                mm_outfit = "collar"
            "You hit the gym before lunch."
            window hide
            show screen outcome_panel("+1 AFFECTION [BODYBUILDER].")
            pause
            hide screen outcome_panel

        "[[BIOHACKER] Dose [bh_protocol] first. (+1 AFFECTION, free)" if stats.player_class == "biohacker" and bh_protocol is not None:
            python:
                martin_affection += 1
                mm_outfit = "collar"
            "Pattern-recognition sharp. Anxiety metabolized into clarity. He notices the focus."
            window hide
            show screen outcome_panel("+1 AFFECTION [BIOHACKER].")
            pause
            hide screen outcome_panel
    return


## ---------------------------------------------------------------------------
## Phase 2: The Meeting and conversation topic
## ---------------------------------------------------------------------------

label martin_phase2_meeting:

    scene bg_cafe

    show martin normal at char_right with Dissolve(0.6)
    show expression "jb " + mm_outfit as jb at char_left with Dissolve(0.6)
    pause 0.4

    "He looks bigger. Healthier. Smiling. Different person."

    if mm_outfit == "polo":
        martin "'Damn, JB. You actually showed up.'"
    elif mm_outfit == "collar":
        martin "'Fresh cut. You made the effort. Good start.'"
    else:
        martin "'A hoodie. To lunch. Okay. Sit down.'"

    "He orders a steak. You order coffee. Break the ice — what do you talk about?"

    menu:
        "Vent. Unload everything. (-50 HATRED)":
            python:
                stats.increment_stats_pcr_hatred(-50)
            "You dump it all. Printers, bodies, admin. Feels good to say it out loud."
            window hide
            show screen outcome_panel("-50 HATRED.")
            pause
            hide screen outcome_panel

        "Brag. Show off the projects. (+25 CODING)":
            python:
                stats.increment_stats_coding_skill(25)
            "You walk him through the automation script. Try to sound like a developer."
            window hide
            show screen outcome_panel("+25 CODING.")
            pause
            hide screen outcome_panel

        "Listen. Ask about his life. (+1 AFFECTION)":
            python:
                martin_affection += 1
                _p2_de_bonus = (stats.player_class == "dark_empath" and
                                sum(getattr(store, 'de_profiles', {}).values()) >= 1)
                if _p2_de_bonus:
                    martin_affection += 1

            "He talks about freedom. Eight hours of sleep. Respect. He notices you actually listened."
            if _p2_de_bonus:
                "You catch the things he's not saying. You ask those instead."
                window hide
                show screen outcome_panel("+1 AFFECTION  ·  +1 [DARK EMPATH].")
            else:
                window hide
                show screen outcome_panel("+1 AFFECTION.")
            pause
            hide screen outcome_panel
    return


## ---------------------------------------------------------------------------
## Phase 3: Drop the Bomb
## ---------------------------------------------------------------------------

label martin_phase3_bomb:

    scene bg_cafe
    show martin serious at char_right
    show expression "jb " + mm_outfit as jb at char_left

    "The food arrives. You put down your fork."
    jb "'Martin, I... I don't really know what to do next, I'm—'"

    martin "'Stop lying to yourself, JB. You know exactly what to do. You're just too scared to say it.'"

    play music "audio/martin_meeting_event_the_awakening.mp3" fadein 1.0

    jb "'You're right. I want to quit.'"

    python:
        if stats.pcr_hatred >= 60:
            stats.increment_stats_pcr_hatred(-15)
            _bomb_outcome = "RELIEF: -15 HATRED."
        else:
            stats.increment_stats_pcr_hatred(15)
            _bomb_outcome = "FEAR: +15 HATRED."

    window hide
    show screen outcome_panel(_bomb_outcome)
    pause
    hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## Phase 4: Coding Reality Check
## ---------------------------------------------------------------------------

label martin_phase4_coding_check:

    scene bg_cafe
    show martin serious at char_right
    show expression "jb " + mm_outfit as jb at char_left

    martin "Okay. You said it. Now, can you actually do it?"
    martin "Do you have the skills? If you leave tomorrow, can you feed yourself?"

    "REALITY CHECK — Current Coding Experience: [stats.coding_skill]"

    python:
        if stats.coding_skill >= 200:
            martin_affection += 1
            stats.increment_stats_pcr_hatred(-20)
            _code_text    = "You smile. You don't just know syntax. You dream in code.\nYou are a God Tier developer trapped in a uniform."
            _code_jb      = "'I am ready,' you say. And you mean it."
            _code_outcome = "+1 AFFECTION, -20 PCR HATRED."
        elif stats.coding_skill >= 150:
            martin_affection += 1
            stats.increment_stats_pcr_hatred(-10)
            _code_text    = "You are solid. You can build apps. You understand the backend.\nYou aren't a genius, but you are hireable. Today."
            _code_jb      = "'I can do this,' you nod."
            _code_outcome = "+1 AFFECTION, -10 PCR HATRED."
        elif stats.coding_skill >= 100:
            martin_affection += 1
            stats.increment_stats_pcr_hatred(-10)
            _code_text    = "You walk him through the backend you built. He stops eating.\nFor a self-taught cop with a countdown over his head, this is real work. You are hireable."
            _code_jb      = "'I can do this,' you say. No hesitation."
            _code_outcome = "+1 AFFECTION, -10 PCR HATRED."
        elif stats.coding_skill >= 50:
            martin_affection -= 1
            stats.increment_stats_pcr_hatred(10)
            _code_text    = "You know the basics. Loops, functions, some libraries.\nBut a job? Real software? You are miles away."
            _code_jb      = "'I... I'm still learning.'"
            _code_outcome = "-1 AFFECTION, +10 PCR HATRED."
        else:
            martin_affection -= 1
            stats.increment_stats_pcr_hatred(20)
            _code_text    = "You have nothing. You spent your time drinking beer instead of studying.\nYou are just a cop with a dream and zero skills."
            _code_jb      = "Martin sees it. He sighs. It's a sigh of pity."
            _code_outcome = "-1 AFFECTION, +20 PCR HATRED."

    "[_code_text]"
    jb "[_code_jb]"
    window hide
    show screen outcome_panel(_code_outcome)
    pause
    hide screen outcome_panel

    ## Class bonus checks after the coding reality check
    python:
        _bh_t3_bonus = (stats.player_class == "biohacker" and nootropic_tier_max >= 3)
        _de_read_bonus = (stats.player_class == "dark_empath")

    if _bh_t3_bonus:
        "You mention that you've been running a stack to accelerate your study retention."
        "Martin stops. His fork goes down."
        martin "'...Wait. You're using nootropics to code?'"
        jb "'[bh_protocol] protocol. Tracked my retention rate. I'm learning 40%% faster than baseline.'"
        "He stares at you."
        martin "'That is either insane or brilliant.'"
        martin "'I genuinely can't tell yet. But it's very you.'"
        python:
            martin_affection += 1
        window hide
        show screen outcome_panel("+1 AFFECTION [BIOHACKER: protocol stack impresses Martin's analytical side].")
        pause
        hide screen outcome_panel

    if _de_read_bonus:
        "You watch Martin's face as you talk about your coding progress."
        "You catch the micro-expressions he's hiding. A small tightening around his eyes on certain answers."
        "He doesn't believe everything you're saying — but he's not cynical, he's {i}invested{/i}."
        "You adjust your framing in real time. Less bravado. More specificity."
        "His expression softens. He leans forward slightly."
        python:
            martin_affection += 1
        window hide
        show screen outcome_panel("+1 AFFECTION [DARK EMPATH: read Martin's real-time feedback and adapted].")
        pause
        hide screen outcome_panel
    return


## ---------------------------------------------------------------------------
## Phase 5: Financial Reality Check
## ---------------------------------------------------------------------------

label martin_phase5_money_check:

    scene bg_cafe
    show martin serious at char_right
    show expression "jb " + mm_outfit as jb at char_left

    martin "Skills are one thing. But freedom isn't free."
    martin "They are going to make you pay for your uniform, your training, every single koruna."
    martin "Do you have the cash? Or are you going to be in debt the moment you walk out?"

    "REALITY CHECK — Current Savings: [stats.available_money] CZK"

    python:
        if stats.available_money >= 100000:
            martin_affection += 1
            _mon_text    = "You nod. You saved hard and it shows.\nYou can cover the exit fee and still have a runway to land on your feet."
            _mon_martin  = "'Smart man.'"
            _mon_outcome = "+1 AFFECTION."
        elif stats.available_money >= 65000:
            martin_affection += 1
            _mon_text    = "You have enough. It will hurt, but you won't starve.\nYou can pay the exit fee and still breathe for a couple of months."
            _mon_martin  = "'I'm covered,' you say."
            _mon_outcome = "+1 AFFECTION."
        elif stats.available_money >= 40000:
            _mon_text    = "You do the math in your head. It's going to be tight.\nIf you pay them off, you'll be eating instant noodles for a while."
            _mon_martin  = "'I can scrape it together,' you admit."
            _mon_outcome = "NEUTRAL (Survival Mode)."
        elif stats.available_money >= 20000:
            martin_affection -= 1
            _mon_text    = "You sweat a little. You don't have enough for the full fee.\nYou'll need a loan, or help from parents. It's messy."
            _mon_martin  = "'That's dangerous ground, JB.'"
            _mon_outcome = "-1 AFFECTION."
        else:
            martin_affection -= 1
            _mon_text    = "You are broke. You have nothing.\nIf you quit, you will be in immediate debt with no income.\nYou are trapped."
            _mon_martin  = "'So you want to quit but you can't afford it?'"
            _mon_outcome = "-1 AFFECTION."

    "[_mon_text]"
    martin "[_mon_martin]"
    window hide
    show screen outcome_panel(_mon_outcome)
    pause
    hide screen outcome_panel
    return


## ---------------------------------------------------------------------------
## Phase 6: Hatred Motivation Check
## ---------------------------------------------------------------------------

label martin_phase6_hatred_check:

    scene bg_cafe
    show martin serious at char_right
    show expression "jb " + mm_outfit as jb at char_left

    "Martin finishes his steak. He wipes his mouth."
    martin "One last thing. The system. The Colonel. The meaningless orders."
    martin "What do you really feel about them? Is this just burnout, or is it personal?"

    "REALITY CHECK — Current PCR HATRED: [stats.pcr_hatred]/[hatred_cap()]"

    menu:
        "Pure rage. (+2 AFFECTION, +25 HATRED)":
            python:
                stats.increment_stats_pcr_hatred(25)
                martin_affection += 2
            jb "'I hate them so much it hurts. Every second in that uniform is torture.'"
            martin "'Good. Use that anger.'"
            window hide
            show screen outcome_panel("+2 AFFECTION, +25 HATRED.")
            pause
            hide screen outcome_panel

        "Hatred. (+1 AFFECTION, +10 HATRED)":
            python:
                stats.increment_stats_pcr_hatred(10)
                martin_affection += 1
            jb "'I hate the politics, the lies. I need out.'"
            martin "'That's the spirit.'"
            window hide
            show screen outcome_panel("+1 AFFECTION, +10 HATRED.")
            pause
            hide screen outcome_panel

        "Neutral. (no change)":
            jb "'It's business. We just aren't a good fit.'"
            martin "'Diplomatic. Boring.'"
            window hide
            show screen outcome_panel("NEUTRAL.")
            pause
            hide screen outcome_panel

        "Soft. (-1 AFFECTION, -25 HATRED)":
            python:
                stats.increment_stats_pcr_hatred(-25)
                martin_affection -= 1
            jb "'They gave me a chance. Maybe I'm just weak.'"
            martin "'Don't blame yourself for their toxicity.'"
            window hide
            show screen outcome_panel("-1 AFFECTION, -25 HATRED.")
            pause
            hide screen outcome_panel

        "Coping. Defend the job. (-2 AFFECTION, -50 HATRED)":
            python:
                stats.increment_stats_pcr_hatred(-50)
                martin_affection -= 2
            jb "'The job is stable. Hierarchy matters. The pension after 15 years is really good!'"
            martin "'...Stockholm Syndrome much? What happened to you?'"
            window hide
            show screen outcome_panel("-2 AFFECTION, -50 HATRED.")
            pause
            hide screen outcome_panel
    return


## ---------------------------------------------------------------------------
## Phase 7: Timing Decision
## ---------------------------------------------------------------------------

label martin_phase7_timing:

    scene bg_cafe
    show martin serious at char_right
    show expression "jb " + mm_outfit as jb at char_left

    martin "'Last thing. The Colonel hired you. He sees you as his project. He'll take resignation as betrayal.'"
    martin "'Guilt, threats, regulations, empathy — he'll throw all of it. Want to rip it off now, or prepare?'"

    menu:
        "Brave. Tomorrow. (Day 26, +1 AFFECTION)":
            python:
                martin_affection += 1
                stats.colonel_day = 26
            jb "'Tomorrow. I'm not waiting.'"
            martin "'Strike while it's hot.'"
            window hide
            show screen outcome_panel("+1 AFFECTION, FINAL BOSS DAY 26.")
            pause
            hide screen outcome_panel

        "Reasonable. End of the month. (Day 30)":
            python:
                stats.colonel_day = 30
            jb "'End of the month. I need to be ready.'"
            martin "'Smart. Save. Code. Prepare.'"
            window hide
            show screen outcome_panel("FINAL BOSS DAY 30.")
            pause
            hide screen outcome_panel
    return


## ---------------------------------------------------------------------------
## Phase 8: Parting Gift
## ---------------------------------------------------------------------------

label martin_phase8_ending:

    scene bg_cafe
    show martin normal at char_right
    show expression "jb " + mm_outfit as jb at char_left

    "The lunch is over. You pay the bill."
    "You walk out into the cold street. The wind hits your face."

    python:
        ## BFF — close the meeting having banked 10 Affection with Martin.
        if martin_affection >= 10:
            unlock_achievement("bff")
        if martin_affection >= 7:
            renpy.jump("martin_good_ending_selection")
        elif martin_affection >= 3:
            renpy.jump("martin_neutral_ending")
        else:
            renpy.jump("martin_bad_ending")


## ---------------------------------------------------------------------------
## Phase 6.5: The Dark Question
## ---------------------------------------------------------------------------

label martin_phase_dark_question:

    scene bg_cafe
    show martin serious at char_right
    show expression "jb " + mm_outfit as jb at char_left

    martin "'One more question. Honest answer, not the rehearsed one. What are you {i}actually{/i} afraid of?'"

    menu:
        "Afraid of failure. (+1 AFFECTION, -5 HATRED)":
            python:
                martin_affection += 1
                stats.increment_stats_pcr_hatred(-5)
            jb "'That I leave and discover I'm not smart enough. That the Colonel was right.'"
            martin "'Fear of failure means you actually want it.'"
            window hide
            show screen outcome_panel("+1 AFFECTION, -5 HATRED.")
            pause
            hide screen outcome_panel

        "Afraid of identity. (+2 AFFECTION, -10 HATRED)":
            python:
                martin_affection += 2
                stats.increment_stats_pcr_hatred(-10)
                _p65_de_bonus = (stats.player_class == "dark_empath")
                if _p65_de_bonus:
                    martin_affection += 1
            jb "'Without the badge I'm just some guy. Thirty-something. No degree.'"
            martin "'Bro. You just described me three years ago. The badge was never your identity. It was your cage.'"
            if _p65_de_bonus:
                window hide
                show screen outcome_panel("+2 AFFECTION  ·  +1 [DARK EMPATH], -10 HATRED.")
            else:
                window hide
                show screen outcome_panel("+2 AFFECTION, -10 HATRED.")
            pause
            hide screen outcome_panel

        "Afraid of nothing. (-2 AFFECTION, +10 HATRED)":
            python:
                martin_affection -= 2
                stats.increment_stats_pcr_hatred(10)
            jb "'Nothing. Made my peace with it.'"
            martin "'Sure you have.'"
            "He doesn't believe you. Something pulls back behind his eyes."
            window hide
            show screen outcome_panel("-2 AFFECTION, +10 HATRED.")
            pause
            hide screen outcome_panel

        "Admit the real fear. (+2 AFFECTION, -15 HATRED)":
            python:
                martin_affection += 2
                stats.increment_stats_pcr_hatred(-15)
            jb "'He'll ruin me. Make calls. Companies will Google me and find an official complaint.'"
            martin "'JB. He tried that with me. Let me tell you what happened to those calls.'"
            "He leans in. Two sentences. The fear drains out of you."
            window hide
            show screen outcome_panel("+2 AFFECTION, -15 HATRED.")
            pause
            hide screen outcome_panel
    return


## ---------------------------------------------------------------------------
## Phase 6.75: The Price
## ---------------------------------------------------------------------------

label martin_phase_the_price:

    scene bg_cafe
    show martin default at char_right
    show expression "jb " + mm_outfit as jb at char_left

    martin "'One more thing. Leaving costs more than money. Some colleagues will call you a traitor — because if you can leave, so could they.'"
    martin "'Can you handle being called that?'"

    python:
        _ci_done = getattr(store, 'coding_interview_passed', False)

    menu:
        "Yes. (+1 AFFECTION)":
            python:
                martin_affection += 1
            jb "'The ones who matter will understand. The rest aren't the ones who matter.'"
            martin "'Good answer.'"
            window hide
            show screen outcome_panel("+1 AFFECTION.")
            pause
            hide screen outcome_panel

        "Not sure. (+1 AFFECTION, -5 HATRED)":
            python:
                martin_affection += 1
                stats.increment_stats_pcr_hatred(-5)
            jb "'It's going to hurt. Known some of these guys for years.'"
            martin "'Then do it anyway while it hurts. That's what courage looks like.'"
            window hide
            show screen outcome_panel("+1 AFFECTION, -5 HATRED.")
            pause
            hide screen outcome_panel

        "[[CODING INTERVIEW PASSED] 'I have a job offer pending.' (+2 AFFECTION, -20 HATRED)" if _ci_done:
            python:
                martin_affection += 2
                stats.increment_stats_pcr_hatred(-20)
            jb "'A company's interested. I passed the technical screen.'"
            martin "'JB, you madman. You're already out — you just haven't told yourself yet.'"
            window hide
            show screen outcome_panel("+2 AFFECTION, -20 HATRED.")
            pause
            hide screen outcome_panel
    return


## ---------------------------------------------------------------------------
## Martin Ending Labels
## ---------------------------------------------------------------------------

label martin_neutral_ending:

    show martin default at char_right
    show expression "jb " + mm_outfit as jb at char_left

    "Firm handshake."
    martin "'It's going to be hell. If you get overwhelmed, remember that I made it.'"

    python:
        grant_card("stoic_anchor", silent=True)
        stats.final_boss_buff = "STOIC_ANCHOR"
    "[[CARD]: STOIC ANCHOR — +3 starting block/turn. Heal 3 after each colonel attack."

    return


label martin_bad_ending:

    show martin serious at char_right
    show expression "jb " + mm_outfit as jb at char_left

    "He looks at you with pity. No handshake."
    martin "'You remind me of that guy from high school who always wanted to open a tuning shop. Big dreams, no action.'"
    martin "'Take this anyway. You came to lunch.'"

    python:
        grant_card("stoic_anchor", silent=True)
        stats.final_boss_buff = "STOIC_ANCHOR"
    "[[CARD]: STOIC ANCHOR — minimum gift."

    return


label martin_good_ending_selection:

    show martin smiling at char_right
    show expression "jb " + mm_outfit as jb at char_left

    martin "'JB, you're ready. I can't fight him for you, but I can give you an edge.'"
    martin "'He'll lie about your training contract. There's a paragraph that nukes the lie. Quote it and watch him choke.'"

    ## TAKE / PASS via the shared solo offer screen.
    ## On PASS the player still walks away with Stoic Anchor as
    ## the consolation gift — Martin doesn't send him out empty-handed.
    python:
        _took_paragraph = offer_card_solo("paragraph_4b", "MARTIN — THE LEGAL NUKE")
        if _took_paragraph:
            stats.final_boss_buff = "PARAGRAPH_4B"
            _ace_label = "Paragraph 4b"
        else:
            stats.final_boss_buff = "STOIC_ANCHOR"
            grant_card("stoic_anchor", silent=True)
            _ace_label = "Stoic Anchor"

    if _took_paragraph:
        "He slides the printout across the table. You fold it into your jacket."
    else:
        martin "'Stoic Anchor it is. Breathe through what he says.'"

    "[[Ace: [_ace_label]]"

    return
