################################################################################
## REFACTOR - Arc II: The Martin Meeting (Day 24)
## Ported verbatim from martin_meeting_event.py — all 8 phases
################################################################################

## Affection points tracked as a screen-level variable
default martin_affection = 0

label martin_meeting:

    $ martin_affection = 0

    play music "audio/martin_meeting_event_the_arrival.mp3" fadein 1.0

    call screen arc_title_card("II", "THE AWAKENING") with arc_fade
    scene bg_cafe with compile_flash
    "DAY 24 — 11:30 AM"

    ## Phase 1: Preparation
    call martin_phase1_preparation
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 2: Meeting
    call martin_phase2_meeting
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 3: Drop the Bomb
    call martin_phase3_bomb
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 4: Coding Reality Check
    call martin_phase4_coding_check
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 5: Financial Reality Check
    call martin_phase5_money_check
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 6: Hatred Motivation Check
    call martin_phase6_hatred_check
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 6.5: The Dark Question (NEW)
    call martin_phase_dark_question
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 6.75: The Price (NEW)
    call martin_phase_the_price
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 7: Timing Decision
    call martin_phase7_timing
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    ## Phase 8: Ending / Parting Gift
    call martin_phase8_ending
    python:
        if stats.player_class == "dark_empath":
            martin_affection += 1

    python:
        if stats.player_class == "dark_empath":
            renpy.say(None, "[[DARK EMPATH PERK]]: Your empathy gave you +10 bonus Affection Points across all phases.")

    return


## ---------------------------------------------------------------------------
## Phase 1: Preparation and clothing choice
## ---------------------------------------------------------------------------

label martin_phase1_preparation:

    scene bg_cafe

    "You decided to call your friend Martin. It's been almost 9 months since you saw him last."
    "He quit the force abruptly. Everyone said he was crazy. Now, rumors say he's doing great."
    "You agreed to meet for lunch at a decent restaurant in the city center."
    "You look at yourself in the mirror. You look like a mess. Bags under your eyes, pale skin, post-shift exhaustion vibrating in your hands."
    "He always cared about image. High-end fashion, perfumes, good posture."
    "You could stop by the mall and buy something sharp to show him you aren't completely dead inside yet."

    menu:
        "PAY 12,500 CZK — Original Fit MASH polo shirt + Tobacco Honey Guerlain EDP. (+2 AFFECTION POINTS)":
            python:
                if stats.try_spend_money(12500):
                    martin_affection += 2
                    _p1text  = "You look at yourself in the mirror and question whether you actually work at Police or Prada."
                    _p1text2 = "'Impressive. Very nice.'\n'Let's see Martin's style.'"
                    _p1outcome = "- 12,500 CZK, +2 AFFECTION POINTS (He will love the effort you put into your outfit)."
                else:
                    _p1text  = "You check your card balance... declined. Embarrassing."
                    _p1text2 = "You go in your old clothes anyway."
                    _p1outcome = "NO CHANGE (Insufficient funds)."

            "[_p1text]"
            "[_p1text2]"
            show screen outcome_panel(_p1outcome)
            pause
            hide screen outcome_panel

        "PAY 2,500 CZK — Get a new cut and buy a new cool shirt. (+1 AFFECTION POINT)":
            python:
                if stats.try_spend_money(2500):
                    martin_affection += 1
                    _p1text  = "The barber played his part really well, you also buy a new sharp shirt. You look in the mirror."
                    _p1text2 = "For a second, you don't look like a tired cop. You look like a civilian."
                    _p1outcome = "- 2,500 CZK, +1 AFFECTION POINT (He will appreciate the effort)."
                else:
                    _p1text  = "You check your card balance... declined. Embarrassing."
                    _p1text2 = "You go in your old clothes anyway."
                    _p1outcome = "NO CHANGE (Insufficient funds)."

            "[_p1text]"
            "[_p1text2]"
            show screen outcome_panel(_p1outcome)
            pause
            hide screen outcome_panel

        "FREE — Go as is. Sweatpants and a hoodie. You don't have energy to pretend.":
            "You splash some cold water on your face. This is who you are right now."
            "If he's really your friend, he won't care about the hoodie."
            show screen outcome_panel("NO CHANGE.")
            pause
            hide screen outcome_panel

        "[[BODYBUILDER]] GYM FIRST — Show up at your physical best. Your presence says everything. (+1 Affection, free)" if stats.player_class == "bodybuilder" and getattr(store, 'gym_streak', 0) >= 5:
            python:
                martin_affection += 1
            "You hit the gym before the meeting."
            "When you walk into the restaurant, Martin clocks it immediately."
            "The posture. The frame. The calm that only comes from a body used to real physical stress."
            martin "'JB... you look different. Good different.'"
            "He says it with genuine respect. You didn't buy that. You built it."
            show screen outcome_panel("+1 AFFECTION POINT [BODYBUILDER: physical transformation is visible].")
            pause
            hide screen outcome_panel

        "[[BIOHACKER]] STACK UP — Take your cognitive supplement before the meeting. (+1 Affection, free)" if stats.player_class == "biohacker" and nootropic_tier_max >= 2:
            python:
                martin_affection += 1
            "You take your stack an hour before the meeting. T[nootropic_tier_max] protocol."
            "By the time you sit down, your pattern-recognition is sharp. Your anxiety is metabolized into clarity."
            "You make eye contact without effort. You speak without filler words."
            "Martin notices something different about your affect — a focused calm he can't quite name."
            show screen outcome_panel("+1 AFFECTION POINT [BIOHACKER: optimized state for high-stakes social interaction].")
            pause
            hide screen outcome_panel

    "AFFECTION POINTS: [martin_affection] / 12"

    return


## ---------------------------------------------------------------------------
## Phase 2: The Meeting and conversation topic
## ---------------------------------------------------------------------------

label martin_phase2_meeting:

    scene bg_cafe
    show martin default at char_center

    "You arrive at the restaurant. You see him in the distance."
    "It's a shock. He looks... different. Bigger. Buffed."
    "His skin has color. He is smiling at the waitress."
    "He looks like a totally different person compared to the wreck you remember from the service."

    "You sit down. Your brain is running on cheap caffeine and 2 hours of sleep after a 24hr shift."
    "He orders a steak. You order a coffee."
    "Before the food arrives, you need to break the ice. What do you talk about?"

    menu:
        "VENT OUT — Complain about the police, the Colonel, and the bureaucracy. (-50 PCR HATRED)":
            python:
                stats.increment_stats_pcr_hatred(-50)

            "You unload everything. The broken printers, the bodies, the admin mistakes."
            "It feels good to say it to someone who understands."
            show screen outcome_panel("-50 PCR HATRED.")
            pause
            hide screen outcome_panel

        "BRAG — Talk about your Python projects and how much you've learned. (+25 CODING SKILLS)":
            python:
                stats.increment_stats_coding_skill(25)

            "You start talking about your projects, classes, and the automation script you wrote."
            "You try to sound professional, to show you are ready."
            show screen outcome_panel("+25 CODING SKILL.")
            pause
            hide screen outcome_panel

        "LISTEN — Let him talk. Ask him how he did it. (+2 AFFECTION POINTS)":
            python:
                martin_affection += 2

            "You stay quiet. You ask him about his life."
            "He talks about his freedom. About sleeping 8 hours a day. About respect."
            "He appreciates that you actually listen."
            show screen outcome_panel("+2 AFFECTION POINTS.")
            pause
            hide screen outcome_panel

    "AFFECTION POINTS: [martin_affection] / 12"

    return


## ---------------------------------------------------------------------------
## Phase 3: Drop the Bomb
## ---------------------------------------------------------------------------

label martin_phase3_bomb:

    scene bg_cafe
    show martin serious at char_center

    "The food arrives. The smell of steak fills the air, but your stomach is tied in a knot."
    "You put down your fork. It's time."
    "'Bro you know...,' you start, your voice cracking slightly. 'It was really inspiring when you left.'"
    "'I don't really know what to do next, I'm kind of lost, and...'"

    "He puts his hand up. He stops you mid-sentence."
    "He looks you dead in the eye. The restaurant noise fades away."

    martin "'Stop lying to yourself, JB.'"
    martin "'You know exactly what to do.'"
    martin "'You are just too scared to admit it.'"

    "Silence. Absolute silence."

    play music "audio/martin_meeting_event_the_awakening.mp3" fadein 1.0

    "The truth hits you like a physical blow."
    "You look down at the table. You whisper it."

    jb "'You are right...'"
    jb "'I... I want to quit.'"

    "As you say those words, the reality of your debt and the Colonel's face flash before your eyes."

    python:
        if stats.pcr_hatred >= 60:
            stats.increment_stats_pcr_hatred(-15)
            _bomb_outcome = "[[RELIEF]]: -15 PCR HATRED (It feels so good to say aloud what you already knew)."
        else:
            stats.increment_stats_pcr_hatred(15)
            _bomb_outcome = "[[CRITICAL EFFECT]]: +15 PCR HATRED (The Fear of leaving is now real)."

    show screen outcome_panel(_bomb_outcome)
    pause
    hide screen outcome_panel

    "Your current hatred is: [stats.pcr_hatred]."
    "AFFECTION POINTS: [martin_affection] / 12"

    return


## ---------------------------------------------------------------------------
## Phase 4: Coding Reality Check
## ---------------------------------------------------------------------------

label martin_phase4_coding_check:

    scene bg_cafe
    show martin serious at char_center

    martin "Okay. You said it. Now, can you actually do it?"
    martin "Do you have the skills? If you leave tomorrow, can you feed yourself?"

    "REALITY CHECK — Current Coding Experience: [stats.coding_skill]"

    python:
        if stats.coding_skill >= 200:
            martin_affection += 2
            stats.increment_stats_pcr_hatred(-20)
            _code_text    = "You smile. You don't just know syntax. You dream in code.\nYou are a God Tier developer trapped in a uniform."
            _code_jb      = "'I am ready,' you say. And you mean it."
            _code_outcome = "+2 AFFECTION POINTS, -20 PCR HATRED (Confidence)."
        elif stats.coding_skill >= 150:
            martin_affection += 1
            stats.increment_stats_pcr_hatred(-10)
            _code_text    = "You are solid. You can build apps. You understand the backend.\nYou aren't a genius, but you are hireable. Today."
            _code_jb      = "'I can do this,' you nod."
            _code_outcome = "+1 AFFECTION POINT, -10 PCR HATRED."
        elif stats.coding_skill >= 100:
            _code_text    = "You are a Junior. You know enough to get into trouble, maybe enough to get an internship.\nIt's going to be hard. But not impossible."
            _code_jb      = "'I think I have a shot,' you say, hesitating slightly."
            _code_outcome = "NEUTRAL. (It's not great, not terrible)."
        elif stats.coding_skill >= 50:
            martin_affection -= 1
            stats.increment_stats_pcr_hatred(10)
            _code_text    = "You know the basics. Loops, functions, some libraries.\nBut a job? Real software? You are miles away."
            _code_jb      = "'I... I'm still learning.'"
            _code_outcome = "-1 AFFECTION POINT, +10 PCR HATRED (Doubt creeps in)."
        else:
            martin_affection -= 2
            stats.increment_stats_pcr_hatred(20)
            _code_text    = "You have nothing. You spent your time drinking beer instead of studying.\nYou are just a cop with a dream and zero skills."
            _code_jb      = "Martin sees it. He sighs. It's a sigh of pity."
            _code_outcome = "-2 AFFECTION POINTS, +20 PCR HATRED (Shame)."

    "[_code_text]"
    jb "[_code_jb]"
    show screen outcome_panel(_code_outcome)
    pause
    hide screen outcome_panel

    ## Class bonus checks after the coding reality check
    python:
        _bh_t3_bonus = (stats.player_class == "biohacker" and nootropic_tier_max >= 3)
        _de_read_bonus = (stats.player_class == "dark_empath")

    if _bh_t3_bonus:
        "You mention that you've been running a Racetam stack to accelerate your study retention."
        "Martin stops. His fork goes down."
        martin "'...Wait. You're using nootropics to code?'"
        jb "'T3 protocol. Tracked my retention rate. I'm learning 40%% faster than baseline.'"
        "He stares at you."
        martin "'That is either insane or brilliant.'"
        martin "'I genuinely can't tell yet. But it's very you.'"
        python:
            martin_affection += 1
        show screen outcome_panel("+1 AFFECTION [BIOHACKER: T3+ compound protocol impresses Martin's analytical side].")
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
        show screen outcome_panel("+1 AFFECTION [DARK EMPATH: read Martin's real-time feedback and adapted].")
        pause
        hide screen outcome_panel

    "AFFECTION POINTS: [martin_affection] / 12"

    return


## ---------------------------------------------------------------------------
## Phase 5: Financial Reality Check
## ---------------------------------------------------------------------------

label martin_phase5_money_check:

    scene bg_cafe
    show martin serious at char_center

    martin "Skills are one thing. But freedom isn't free."
    martin "They are going to make you pay for your uniform, your training, every single koruna."
    martin "Do you have the cash? Or are you going to be in debt the moment you walk out?"

    "REALITY CHECK — Current Savings: [stats.available_money] CZK"

    python:
        if stats.available_money >= 200000:
            martin_affection += 2
            _mon_text    = "You nod confidently. You have been saving aggressively.\nYou have a war chest. You can buy your freedom twice over."
            _mon_martin  = "'Smart man.'"
            _mon_outcome = "+2 AFFECTION POINTS (Financial Freedom)."
        elif stats.available_money >= 150000:
            martin_affection += 1
            _mon_text    = "You have enough. It will hurt, but you won't starve.\nYou can pay the exit fee and still have a buffer for a few months."
            _mon_martin  = "'I'm covered,' you say."
            _mon_outcome = "+1 AFFECTION POINT (Secure)."
        elif stats.available_money >= 100000:
            _mon_text    = "You do the math in your head. It's going to be extremely tight.\nIf you pay them off, you'll be eating instant noodles for weeks."
            _mon_martin  = "'I can scrape it together,' you admit."
            _mon_outcome = "NEUTRAL (Survival Mode)."
        elif stats.available_money >= 50000:
            martin_affection -= 1
            _mon_text    = "You sweat a little. You don't have enough for the full fee.\nYou'll need a loan, or help from parents. It's messy."
            _mon_martin  = "'That's dangerous ground, JB.'"
            _mon_outcome = "-1 AFFECTION POINT (Financial Risk)."
        else:
            martin_affection -= 2
            _mon_text    = "You are broke. You have nothing.\nIf you quit, you will be in immediate debt with no income.\nYou are trapped."
            _mon_martin  = "'So you want to quit but you can't afford it?'"
            _mon_outcome = "-2 AFFECTION POINTS (Total Disaster)."

    "[_mon_text]"
    martin "[_mon_martin]"
    show screen outcome_panel(_mon_outcome)
    pause
    hide screen outcome_panel

    "AFFECTION POINTS: [martin_affection] / 12"

    return


## ---------------------------------------------------------------------------
## Phase 6: Hatred Motivation Check
## ---------------------------------------------------------------------------

label martin_phase6_hatred_check:

    scene bg_cafe
    show martin serious at char_center

    "Martin finishes his steak. He wipes his mouth."
    martin "One last thing. The system. The Colonel. The meaningless orders."
    martin "What do you really feel about them? Is this just burnout, or is it personal?"

    "REALITY CHECK — Current PCR HATRED: [stats.pcr_hatred]/100"

    menu:
        "PURE RAGE — 'I hate them. I want to watch the station burn.'":
            python:
                stats.increment_stats_pcr_hatred(25)
                martin_affection += 2

            "Your eyes flash with anger. You practically spit the words out."
            jb "'I hate them so much it hurts. Every second in that uniform is torture.'"
            martin "'Good. Use that anger.'"
            show screen outcome_panel("+2 AFFECTION POINTS, +25 PCR HATRED (Fuel for the fire).")
            pause
            hide screen outcome_panel

        "HATRED — 'I'm done. I despise what I've become here.'":
            python:
                stats.increment_stats_pcr_hatred(10)
                martin_affection += 1

            jb "'I hate it. I hate the politics, the lies. I need out.'"
            martin "'That's the spirit.'"
            show screen outcome_panel("+1 AFFECTION POINT, +10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "NEUTRAL — 'It's just a job. It didn't work out.'":
            jb "'It's business. We just aren't a good fit.'"
            martin "'Diplomatic answer. Boring, but safe.'"
            show screen outcome_panel("NEUTRAL.")
            pause
            hide screen outcome_panel

        "SOFT — 'I don't have hard feelings. Maybe it's me who is the problem.'":
            python:
                stats.increment_stats_pcr_hatred(-25)
                martin_affection -= 1

            jb "'They gave me a chance. Maybe I'm just weak.'"
            martin "'Don't do that. Don't blame yourself for their toxicity.'"
            show screen outcome_panel("-1 AFFECTION POINT, -25 PCR HATRED.")
            pause
            hide screen outcome_panel

        "COPING — 'Actually, the police is vital for society! The Colonel is just misunderstood!'":
            python:
                stats.increment_stats_pcr_hatred(-50)
                martin_affection -= 2

            "You start rambling."
            jb "'I mean, the job is stable and hierarchy is important and also that pension after 15 years of service is really good!'"
            "You sound like a brainwashed cadet in training."
            "He just stares at you in utter disbelief. The cringe has filled the air completely."
            martin "'Wow. Stockholm Syndrome much? What happened to you dude?'"
            show screen outcome_panel("-2 AFFECTION POINTS, -50 PCR HATRED (Your mental gymnastics are just insane).")
            pause
            hide screen outcome_panel

    "AFFECTION POINTS: [martin_affection] / 12"

    return


## ---------------------------------------------------------------------------
## Phase 7: Timing Decision
## ---------------------------------------------------------------------------

label martin_phase7_timing:

    scene bg_cafe
    show martin serious at char_center

    "Martin's expression darkens. The nostalgia is gone."
    martin "'One last thing, JB. The Colonel.'"
    martin "'I know you think he is just a bureaucrat. But don't underestimate him.'"
    martin "'He is the one who hired you, remember? He personally admitted you to the academy.'"
    martin "'He sees you as his project. His success story. His Good Soldier.'"
    martin "'When you hand him that resignation... he won't see it as paperwork.'"
    martin "'He will take it as a betrayal.'"

    martin "'He will come at you with everything. Guilt, threats, regulations, maybe even empathy.'"
    martin "'It won't be an easy fight. It might be the hardest thing you've ever done.'"
    martin "'Are you ready to face him? Do you want to rip the band-aid off now?'"
    martin "'Or do you need time to prepare your mind and your wallet?'"

    menu:
        "BRAVE — 'I'm doing it tomorrow. I want it over with.' (Colonel fight Day 25, +2 AFFECTION POINTS)":
            python:
                martin_affection += 2
                stats.colonel_day = 25

            jb "'Tomorrow. I'm not waiting.'"
            martin "'Good. Strike while the iron is hot. Don't let the fear settle.'"
            show screen outcome_panel("+2 AFFECTION POINTS, FINAL BOSS SET FOR DAY 25.")
            pause
            hide screen outcome_panel

        "REASONABLE — 'I need more time. I'll wait until the last moment.' (Colonel fight Day 30)":
            python:
                stats.colonel_day = 30

            jb "'I need to be sure. I'll wait... I have to do it till the end of this month.'"
            martin "'Smart. Don't rush into a war you aren't ready for.'"
            martin "'Use the time wisely. Save money. Code. Prepare.'"
            show screen outcome_panel("FINAL BOSS SET FOR DAY 30.")
            pause
            hide screen outcome_panel

    "FINAL AFFECTION SCORE: [martin_affection] / 12 POINTS"

    return


## ---------------------------------------------------------------------------
## Phase 8: Parting Gift
## ---------------------------------------------------------------------------

label martin_phase8_ending:

    scene bg_cafe

    "The lunch is over. You pay the bill."
    "You walk out into the cold street. The wind hits your face."

    python:
        if martin_affection >= 8:
            renpy.jump("martin_good_ending_selection")
        elif martin_affection >= 5:
            renpy.jump("martin_neutral_ending")
        else:
            renpy.jump("martin_bad_ending")


## ---------------------------------------------------------------------------
## Phase 6.5: The Dark Question
## ---------------------------------------------------------------------------

label martin_phase_dark_question:

    scene bg_cafe
    show martin serious at char_center

    "The restaurant has thinned out. It's just you and Martin and two couples who aren't talking to each other."
    "He refills your coffee without asking."
    martin "'One more question. And I want the honest answer, not the rehearsed one.'"
    martin "'What are you {i}actually{/i} afraid of?'"

    "You pause."

    menu:
        "AFRAID OF FAILURE — 'What if I quit and I can't make it as a developer?'":
            python:
                martin_affection += 1
                stats.increment_stats_pcr_hatred(-5)

            jb "'That I leave... and discover I'm not actually smart enough.'"
            jb "'That the colonel was right.'"
            "Martin is quiet for a moment."
            martin "'That's the most honest thing you've said today.'"
            martin "'Good. Fear of failure means you actually want it.'"
            martin "'Nobody who doesn't care is afraid of failing.'"
            show screen outcome_panel("+1 AFFECTION, -5 PCR HATRED (Honesty is the real armor).")
            pause
            hide screen outcome_panel

        "AFRAID OF IDENTITY — 'Without the badge, who am I?'":
            python:
                martin_affection += 2
                stats.increment_stats_pcr_hatred(-10)

            jb "'The badge is... the only thing some people respect about me.'"
            jb "'Without it I'm just some guy. Thirty-something. No degree. Living in a rented flat.'"
            "Martin stares at you for a long moment."
            martin "'Bro. You just described me three years ago.'"
            martin "'I am not nothing. And you are not nothing. You just haven't built your thing yet.'"
            martin "'The badge was never your identity. It was your cage.'"
            show screen outcome_panel("+2 AFFECTION, -10 PCR HATRED (Martin sees through you. In the good way).")
            pause
            hide screen outcome_panel

        "AFRAID OF NOTHING — 'I'm not afraid. I'm ready.'":
            python:
                stats.increment_stats_pcr_hatred(10)

            jb "'Nothing. I've made my peace with it.'"
            "Martin raises an eyebrow."
            martin "'Sure you have.'"
            "He says it gently, but you both know he doesn't believe you."
            "Lying to Martin is like lying to yourself. He was you, three years ago."
            show screen outcome_panel("+10 PCR HATRED (Supressed fear doesn't disappear, it just goes underground).")
            pause
            hide screen outcome_panel

        "ADMIT THE REAL FEAR — 'I'm afraid of the Colonel finding me after I leave.'":
            python:
                martin_affection += 3
                stats.increment_stats_pcr_hatred(-15)

            jb "'He will ruin me. He has contacts. He will make calls. He will follow my career.'"
            jb "'I'll be applying for dev jobs and they'll Google me and find an official complaint.'"
            "Martin goes very still."
            "Then he smiles. It doesn't reach his eyes."
            martin "'JB. He tried that with me.'"
            martin "'Let me tell you what happened to those calls.'"
            "He leans in. He whispers two sentences."
            "Your jaw drops."
            "The fear drains out of you like water."
            show screen outcome_panel("+3 AFFECTION, -15 PCR HATRED (Martin just neutralized your deepest fear).")
            pause
            hide screen outcome_panel

    "AFFECTION POINTS: [martin_affection] / 12"

    return


## ---------------------------------------------------------------------------
## Phase 6.75: The Price
## ---------------------------------------------------------------------------

label martin_phase_the_price:

    scene bg_cafe
    show martin default at char_center

    "Martin looks down at his steak for a moment. When he looks up, his expression has changed."
    martin "'Before I help you — I need you to understand something.'"
    martin "'Leaving costs. More than money. More than the Colonel.'"
    martin "'It will cost you relationships. Some people will call you selfish.'"
    martin "'Some of your colleagues — the ones you drink with — they will feel judged by your choice.'"
    martin "'Because if you can leave, then so could they. And they chose not to.'"
    martin "'That's uncomfortable for them. So they make it about you.'"

    "He takes a sip of coffee."
    martin "'Can you handle being called a traitor by people you respected?'"

    python:
        _ci_done = getattr(store, 'coding_interview_passed', False)

    menu:
        "YES — 'I've already processed that. I'm ready to be alone in this.'":
            python:
                martin_affection += 2

            jb "'I've thought about this. The ones who matter will understand.'"
            jb "'And if they don't... then they aren't the ones who matter.'"
            martin "'Good answer. That's exactly the mindset.'"
            show screen outcome_panel("+2 AFFECTION POINTS (The right mindset).")
            pause
            hide screen outcome_panel

        "NOT SURE — 'I'll probably still care about what they think. Can't help it.'":
            python:
                martin_affection += 1
                stats.increment_stats_pcr_hatred(-5)

            jb "'Honestly? It's going to hurt. I've known some of these guys for years.'"
            "Martin nods. He respects the honesty more than the bravado."
            martin "'Good. Then do it anyway while it hurts.'"
            martin "'That's what actual courage looks like. Not fearlessness. Doing it scared.'"
            show screen outcome_panel("+1 AFFECTION, -5 PCR HATRED (Courage confirmed).")
            pause
            hide screen outcome_panel

        "[[CODING INTERVIEW PASSED]] 'I have a job offer pending. I don't need their validation anymore.'" if _ci_done:
            python:
                martin_affection += 3
                stats.increment_stats_pcr_hatred(-20)

            jb "'I already have a company interested in me. I passed the technical screen.'"
            "Martin freezes."
            martin "'...You already have an offer?'"
            jb "'Working on it.'"
            "Martin laughs. Genuinely laughs."
            martin "'JB, you madman. You are already out. You just haven't told yourself yet.'"
            show screen outcome_panel("+3 AFFECTION, -20 PCR HATRED [[CODING INTERVIEW PERK — Maximum confidence]].")
            pause 2.5
            hide screen outcome_panel

    "AFFECTION POINTS: [martin_affection] / 12"

    return


## ---------------------------------------------------------------------------
## Martin Ending Labels
## ---------------------------------------------------------------------------

label martin_neutral_ending:

    show martin default at char_center

    "Your friend shakes your hand. His grip is firm."
    martin "'It's going to be hell, JB. He will try to break you.'"
    martin "'But if you get overwhelmed, just remember that I made it.'"
    martin "'I'm waiting on the other side. Don't let him win.'"

    $ stats.final_boss_buff = "STOIC_ANCHOR"
    "[[STATUS ACQUIRED]]: STOIC ANCHOR\n(Passive: You are more resistant to the Colonel's attacks.)"

    return


label martin_bad_ending:

    show martin serious at char_center

    "Martin looks at you with pity. He doesn't shake your hand."
    martin "'JB, do you remember that one guy from high school, who always wanted to open a car tuning shop but never did anything about it?'"
    martin "'Well... you kinda remind me of him now — big dreams, but no action at all.'"
    martin "'If you go in there like this, he's going to eat you alive.'"
    martin "'Good luck kiddo. You are going to need it.'"

    $ stats.final_boss_buff = "IMPOSTER_SYNDROME"
    "[[STATUS ACQUIRED]]: IMPOSTER SYNDROME\n(Debuff: You start the boss fight with a DEBUFF.)"

    return


label martin_good_ending_selection:

    show martin smiling at char_center

    martin "'Wait, JB. I have a good feeling about this. You are actually ready.'"
    martin "'I want to help you. I can't fight him for you, but I can give you an edge.'"
    martin "'What do you need the most? Information? Security? Or a weapon?'"

    "CHOOSE YOUR FINAL BOSS ADVANTAGE:"

    menu:
        "THE LEGAL NUKE — File proving the 80k debt is void via 'Paragraph 4B'. (Colonel -35 HP, auto-counters Training Debt for +15 DMG)":
            "Martin hands you a crumpled digital file printout."
            martin "'He lies about the contract. Quote this paragraph. Watch him choke.'"
            $ stats.final_boss_buff = "LEGAL_NUKE"

        "GHOST OF THE PAST — Martin reveals the Colonel's big secret. (Immune to Round 1 Fear. Unlocks -40 HP FATAL STRIKE on 'Car Incident'.)":
            "Martin leans in and whispers the Colonel's dirty secret."
            "You smile. Suddenly, the Colonel doesn't look like a monster. He looks like a failure."
            $ stats.final_boss_buff = "GHOST_SECRET"

        "PRODUCTION READY SHIELD — Martin vouches for you and writes a salary figure on a napkin. (Immune Round 1 Fear. Auto-Wins 'Blacklist' and 'Motivation'.)":
            "Martin makes a call. He hands you a napkin with a number on it."
            martin "'That's your starting salary. He can't threaten a man who has options.'"
            $ stats.final_boss_buff = "JOB_OFFER"

        "STOIC REFACTOR — Martin teaches you the 'Grey Rock' method. (Immune Round 1 Fear. Reduced damage from emotional attacks.)":
            "Martin grabs your shoulders. He teaches you to breathe. To detach."
            martin "'He is just broken code, JB. Don't get angry. Just debug him.'"
            $ stats.final_boss_buff = "STOIC_HEAL"

        "AGGRESSIVE OPENING — Martin hypes you up to strike first. (Colonel starts -20 HP. Immune to Round 1 Fear.)":
            "Martin slaps your back hard. The adrenaline hits."
            martin "'Don't let him speak. Throw the badge on the table. Be the alpha.'"
            $ stats.final_boss_buff = "FIRST_STRIKE"

    "[[ACE IN THE HOLE ACQUIRED]]: [stats.final_boss_buff]"

    return
