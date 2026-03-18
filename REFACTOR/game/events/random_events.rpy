################################################################################
## REFACTOR - Random Events (14 total)
## Ported verbatim from random_events.py
## Each event is its own label: re_<name>
################################################################################

## ---------------------------------------------------------------------------
## EVENT: Israeli Developer
## ---------------------------------------------------------------------------

label re_israeli_developer:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "You are standing at a small intersection somewhere in the middle of your district."
    "A light car crash happened — nothing serious, just enough to annoy you and create paperwork."
    "You're managing the traffic with your glowing baton like a depressed Jedi when suddenly a man approaches you from the damaged vehicle."
    "He looks completely calm, almost amused by the chaos around him."
    "He has an accent you can't quite place at first, until he says:"
    "'You know, in Tel Aviv, traffic is much worse.'"
    "He laughs. You don't."

    "You raise an eyebrow. 'Tel Aviv?'"
    "'Yes! I teach computer science there. Twenty-two years now. Came here for holiday… and someone forgot to use his brakes,' he says, pointing at the Czech driver."
    "You ask him what he teaches."
    "'Algorithms. Systems architecture. Low-level optimization. And recently — machine learning basics.'"
    "'Students only want AI now. Nobody wants to understand pointers anymore.'"

    "He looks at you with a sharp, analyzing gaze, ignoring your uniform entirely."
    "'You have intelligent eyes. You are not just a traffic cone stand. Tell me... do you write code?'"

    python:
        _can_code = stats.coding_skill >= 35
        ## BIOHACKER perk: always gets full coding reward regardless of skill check
        if stats.player_class == "biohacker":
            _can_code = True

    menu:
        "'Actually, I am something of a developer myself.' [[SKILL CHECK >= 35: PASSED]]" if _can_code:
            python:
                stats.increment_stats_coding_skill(30)
                _isr_biohacker = stats.player_class == "biohacker"
                if _isr_biohacker:
                    flmodafinil_unlocked = True

            "You adjust your belt, look around to make sure your colleague isn't listening, and reply:"
            jb "'I work with Python. Backend mostly. Trying to get into AI integration.'"
            "The Professor's eyes light up. 'Python? Good for prototyping. But tell me, how do you handle memory management when you scale? Do you understand what the Global Interpreter Lock actually does?'"
            "You spend the next 20 minutes in a deep technical debate. He quizzes you, challenges you, and eventually nods in approval."
            "'Not bad,' he says. 'Actually, quite good. You have the mind for it. Why are you wearing this costume?'"
            "He writes an email address on a piece of paper. 'Send me your GitHub. We always look for talent.'"

            if _isr_biohacker:
                "He pauses before leaving. Lowers his voice just below the ambient traffic noise."
                "'I notice things. You have the eyes of someone who optimises everything — including himself.'"
                "'I know a contact. Research compounds. Cognitive enhancement. Not recreational. Functional.'"
                "He slips you a second piece of paper. No name. No address. Just a Telegram handle."
                "'Don't abuse it,' he says. 'Tools are only as smart as the person holding them.'"
                "You pocket it. You know exactly what it is."
                show screen outcome_panel("+30 CODING SKILLS  |  [[CRL-40,940 SOURCE UNLOCKED]]  [BIOHACKER]")
                pause
                hide screen outcome_panel
            else:
                "You walk away feeling validated for the first time in years."
                show screen outcome_panel("+30 CODING SKILLS.")
                pause
                hide screen outcome_panel

        "Stay silent. 'Me? No. I just... work here.' [[IMPOSTER SYNDROME]]":
            python:
                stats.increment_stats_coding_skill(10)

            "You feel the words forming in your throat — 'I study Python', 'I want to build apps' — but the fear chokes them down."
            jb "'Me? No. I just follow orders.'"
            "The Professor looks disappointed for a split second, then shrugs."
            "'Pity. You have the look. Well, let me tell you something anyway...'"
            "He gives you a short, precise monologue about problem-solving and abstraction layers."
            "'If you ever get tired of this job — and trust me, you will — learn to build things. Police officers preserve the status quo. Developers build the future.'"
            "You listen. You learn something. But it hurts that you didn't speak up."
            show screen outcome_panel("+10 CODING SKILLS.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Nightmare Wolf
## ---------------------------------------------------------------------------

label re_nightmare_wolf:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "04:00 AM. You are on patrol. The world is grey and cold."
    "Dispatch sends you to an accident nearby. Routine procedure."
    "Your colleague drives. He doesn't say a word."

    "Arrival. There are too many flashing lights for a simple crash."
    "You see the body bags lined up on the wet asphalt. Small ones."
    "You look away, but you swear one of the bags moves."
    "Just a twitch. A hand pressing against the black plastic."
    "You look at the paramedic. He lights a cigarette and looks right through you."
    "You get back in the car. We are leaving."

    "Back at the station. You walk into the main room."
    "She is sitting there."
    "The woman from the briefing. The murderer. Black hair, calm hands."
    "She is sitting on the bench, un-cuffed, watching you."

    jb "'That's her. That's the fugitive.'"
    "Your colleagues stop drinking coffee. They look at you, then at the empty bench."
    "Then they start laughing."
    "'JB, you look like hell. Go wash your face.'"

    jb "'LOOK.'"
    "Standing outside, pressing its nose against the glass, is a Husky."
    "But it's wrong. It's too big. It's staring directly at you."

    "'Enough,' your colleague says. His voice is dead serious."
    "Before you can react, they grab you."
    "You struggle, but they force you into a chair. Duct tape over your mouth."
    "They aren't angry. They look... bored. Disappointed."

    "You try to scream through the tape."
    "CRASH."
    "The window shatters. The Husky is inside."
    "It doesn't bark. It just tears the first officer's throat out."
    "Blood sprays on the wall. The others don't even reach for their guns."
    "They just stand there and die."

    "The Wolf turns to you. It walks over the bodies. It puts its face right next to yours."
    "You can smell its breath. Hot. Metallic."

    "You wake up."
    "You are tangled in your sheets, soaking wet. Your heart is hammering against your ribs."
    "The room is silent. But you can still feel the phantom pressure of the tape on your mouth."

    python:
        _nw_de = (stats.player_class == "dark_empath")

    if _nw_de:
        "[[DARK EMPATH]]: Even mid-nightmare, part of your mind stays cold and analytical."
        "The wolf's body language. The colleagues' passive compliance. The timing of the tape."
        "You've processed this unconsciously before. You know what it means."
        menu:
            "[[DARK EMPATH]] READ IT — Hold eye contact. Project stillness. Don't give fear an audience.":
                python:
                    stats.increment_stats_pcr_hatred(3)
                "In the dream, you go completely still."
                "The wolf stops. Tilts its head. Confusion. Not fear — it has never met something that didn't flinch."
                "You wake up. Heart loud, but something in you is quieter than before."
                "You've seen behind the threat. You won't forget it."
                show screen outcome_panel("+3 PCR HATRED [DARK EMPATH: nightmare analyzed, not survived].")
                pause
                hide screen outcome_panel
    else:
        python:
            stats.increment_stats_pcr_hatred(10)
        show screen outcome_panel("+10 PCR HATRED (Night terror).")
        pause
        hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Civilian Small Talk
## ---------------------------------------------------------------------------

label re_civilian_small_talk:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "You are standing next to your marked car, somewhere in the middle of nowhere."
    "Cold wind, grey sky, nothing happening for the last 40 minutes."
    "Your colleague is scrolling his phone like a true professional, defending the homeland by liking memes."
    "From the nearby panel house, an older man slowly approaches you. Jacket from 1987, slippers, eyes full of boredom and curiosity."
    "He asks the usual nonsense: 'What are you guarding here?' 'Is something happening?' 'Is it dangerous here?'"
    "You answer politely, mechanically. You would rather be anywhere else, even filling out forms."
    "After a while, he gets bolder and asks the one question you didn't want to hear:"
    "'Tell me honestly, young man... do you like this job? What do you really think about it?'"

    menu:
        "VENT OUT AND TELL HIM THE TRUTH. (80%% success chance)":
            python:
                ## DARK EMPATH perk: always reads the old man correctly, guaranteed success
                if stats.player_class == "dark_empath":
                    _roll = 1
                else:
                    _roll = __import__('random').randint(1, 100)
                if _roll <= 80:
                    stats.increment_stats_pcr_hatred(-25)
                    _cst_text = "You look him straight in the eyes and something inside you finally snaps.\nYou start slowly, but your words gain momentum.\nYou describe the leadership that has never seen the street, but writes rules for those who live on it.\nThe old man just nods, listening. No phone, no recording, just a human being who actually hears you.\nWhen you finish, he smiles sadly and says: 'I thought so... you can see it in your eyes.'\nYou feel strangely lighter. Nothing changed... but at least you said it out loud."
                    _cst_outcome = "-25 PCR HATRED.{}".format(" [DARK EMPATH: guaranteed success]" if stats.player_class == "dark_empath" else "")
                else:
                    stats.increment_stats_pcr_hatred(25)
                    stats.increment_stats_value_money(-2500)
                    _cst_text = "You look around, see no one, and decide to finally let it all out.\nThe next day, your boss calls you in. On his desk lies a phone, screen turned towards you.\nThe old man sent the recording to the city hall, 'out of concern for the state of the police'.\nYou receive a written reprimand and a nice little financial penalty."
                    _cst_outcome = "+25 PCR HATRED, -2500 CZK."

            "[_cst_text]"
            show screen outcome_panel(_cst_outcome)
            pause
            hide screen outcome_panel

        "KEEP IT INSIDE AND SAY GENERAL INFORMATION. [[SAFE OPTION]]":
            python:
                stats.increment_stats_pcr_hatred(10)

            "You feel the words crawling up your throat, but you swallow them back down."
            "You put on your standard-issue smile and say something about 'stable job, helping people, good team, interesting work'."
            "You hear yourself and want to throw up, but the old man seems satisfied."
            "'Well, at least someone still does this work, right?'"
            jb "'Yes, someone.'"
            "He walks away and the silence returns. Only now it feels heavier."
            show screen outcome_panel("+10 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Admin Mistake After Shift
## ---------------------------------------------------------------------------

label re_admin_mistake:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "It's 07:00 in the morning. Your night shift is finally over… at least on paper."
    "You feel like a ghost in uniform. Eyes burning, head heavy, body running only on caffeine and spite."
    "You walk towards the exit. As you pass the office corridor, you hear laughter."
    "Day shift has just arrived. Fresh, rested, smelling like showers and normal life."
    "Then you hear it: 'JB, come here for a moment.'"
    "Your boss is sitting behind his desk with a stack of papers."
    "'You made a mistake here. This is done wrong. You need to fix it. Today. Now.'"
    "You've been here all night. You still have an hour of travel home ahead of you."

    menu:
        "TELL HIM YOU'RE DONE AND GO HOME. Pay the penalty later. (-2500 CZK, -10 PCR HATRED)":
            python:
                stats.increment_stats_value_money(-2500)
                stats.increment_stats_pcr_hatred(-10)

            "You look at the papers. Then at your boss. Then back at the papers."
            "Something inside you just… snaps, but in a quiet way. Not dramatic. Just final."
            jb "'No. I'm done for today. If there's a penalty, I'll pay it.'"
            "Your boss stares at you, surprised. He expected begging, excuses, submissive guilt."
            "He exhales through his nose, annoyed. 'Fine. I warned you.'"
            "You walk past the day shift, like a ghost leaving a party he was never invited to."
            "Outside, the air is cold, but it feels… real."
            show screen outcome_panel("-2500 CZK, -10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "STAY, FIX THE MISTAKE AND DESTROY WHAT'S LEFT OF YOUR SOUL. (+20 PCR HATRED)":
            python:
                stats.increment_stats_pcr_hatred(20)

            "You swallow your pride, sit down and take the report."
            "Your hands feel heavy. Your brain feels like wet concrete. But you start rewriting."
            "Your boss corrects you twice more, just to make sure you understand who's in control here."
            "Finally, you finish. Your boss glances at the report, nods once and says:"
            "'Now it's correct. You can go.' No thank you. No appreciation. Just a checkbox ticked."
            show screen outcome_panel("+20 PCR HATRED.")
            pause
            hide screen outcome_panel

        "[[DARK EMPATH]] REDIRECT — The mistake was the system's. Let him feel that. (0 penalty)" if stats.player_class == "dark_empath":
            "You look at the report. Then at your boss. Then back at him."
            "He's not angry. He's performing authority. There is a difference."
            "He needs the hierarchy acknowledged. He doesn't actually care about the form."
            jb "'You're right, Sergeant. I flagged this to the shift admin three days ago and it got lost in the handover queue. I'll close the loop today and make sure it doesn't happen again.'"
            "You are referring to an email sent to a shared inbox that nobody monitors."
            "He pauses. He nods slowly."
            "'Good. Don't let it happen again.'"
            "You fix the report in 20 minutes. The power structure got its performance. You paid nothing for it."
            show screen outcome_panel("0 CZK, 0 PCR HATRED [DARK EMPATH: the system took the blame, not you].")
            pause
            hide screen outcome_panel

        "[[BODYBUILDER]] STAND UP — Some meetings end because you get to your feet. (+5 Hatred)" if stats.player_class == "bodybuilder":
            python:
                stats.increment_stats_pcr_hatred(5)
            "You are very tired."
            "You are also very large."
            "You stand up. Slowly. All of you stands up."
            "Your boss — who has not played a sport since 1998 — looks up at you from behind his desk."
            "He looks at the papers. He looks at you."
            "He looks at the papers again."
            jb "'I'll sort it today.'"
            "You walk out."
            "He does not call you back."
            "He probably could have pushed harder. He made a choice."
            "You fix the report in your car, over coffee, in 25 minutes."
            show screen outcome_panel("0 CZK, +5 PCR HATRED [BODYBUILDER: presence shortened the confrontation significantly].")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Overtime Offer
## ---------------------------------------------------------------------------

label re_overtime_offer:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "06:43 AM. Your day off. You were asleep."
    "Your phone rings. Work number."
    "You stare at it for four seconds. It doesn't stop."

    jb "'...Hello.'"
    "'JB. Novák called in sick. Horáček too. I need someone.'"
    "There's no question mark at the end of that sentence. There never is."
    "You look at your ceiling. Your laptop is open on the desk. Python tutorial, paused at chapter 7."
    "One path leads to the station. The other leads to chapter 8."

    menu:
        "[[BODYBUILDER]] DOUBLE SHIFT — Your body can handle it. (+15,000 CZK, 0 Hatred)" if stats.player_class == "bodybuilder":
            python:
                stats.increment_stats_value_money(15000)
            jb "'I'll take it.'"
            "Zero hesitation. You shower, eat a protein bar, and walk back in."
            "Your body is a machine. You let it run."
            "You outlast everyone on the shift. You are earning your escape, one hour at a time."
            show screen outcome_panel("+15,000 CZK [BODYBUILDER: physical endurance pays off].")
            pause
            hide screen outcome_panel

        "DO OVERTIME. [[GAIN RANDOM AMOUNT OF MONEY]]":
            python:
                _earned = __import__('random').randint(3500, 12500)
                stats.increment_stats_value_money(_earned)

            jb "'Fine. Give me 30 minutes.'"
            "You close the laptop."
            "The shift is long and unremarkable. Paperwork, a domestic dispute that resolved itself, one confused tourist."
            "But the pay lands in your account at midnight and you do the math in your head — that's {n} CZK closer to getting out."
            "You fall asleep with your uniform still half on."
            show screen outcome_panel("+{} CZK.".format(_earned))
            pause
            hide screen outcome_panel

        "STAY AT HOME AND CODE. [[GAIN RANDOM AMOUNT OF CODING SKILLS]]":
            python:
                _gained = __import__('random').randint(15, 40)
                stats.increment_stats_coding_skill(_gained)

            jb "'I can't make it in today. I'm sick.'"
            "Silence."
            "'You don't sound sick.'"
            jb "'Stomach thing. Sudden onset.'"
            "More silence. Then a click."
            "You put the phone face-down and open the laptop."
            "Six hours later you understand decorators. Really understand them, not just copy-paste understand them."
            "It was worth it."
            show screen outcome_panel("+{} CODING SKILLS.".format(_gained))
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Birthday Gift
## ---------------------------------------------------------------------------

label re_birthday_gift:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "You're at the station. The depressive atmosphere is omnipresent, your mind is wandering, your eyes staring at the ceiling."
    "Until your middle-aged secretary arrives with her fake smile — the one even tiny children would see through."
    "You put on your mask again and force a smile on your face. With utter joy, she announces that two of your colleagues are celebrating their birthdays this week and asks if you want to contribute to their gifts."
    "You pause for a moment and think: 'Why should I contribute? I am gonna quit anyway... but if I won't give anything, they will hate me here even more.'"

    menu:
        "PAY FOR THE GIFTS. [[-1000 CZK, +5 PCR HATRED]]":
            python:
                stats.increment_stats_pcr_hatred(5)
                stats.increment_stats_value_money(-1000)

            jb "'Sure, buy them something nice.'"
            "You don't even look in her eyes as you torment yourself with those words you've just said."
            "She is satisfied, but you are still obliged to listen to her rantings about her children for another 15 minutes."
            "'What have I done to deserve this...' you think for yourself."
            show screen outcome_panel("-1000 CZK, +5 PCR HATRED.")
            pause
            hide screen outcome_panel

        "DON'T PAY ANYTHING. [[+15 PCR HATRED]]":
            python:
                stats.increment_stats_pcr_hatred(15)

            jb "'No... I don't want to contribute.'"
            "She pauses, her mouth opens, she stares at you. You always thought she was around her 40s, but as she started to glare at you without saying anything for a few seconds, you think she looks more close to her 70s."
            "You don't react and hold your cold-hearted expression towards her."
            "After a short moment, she puts her hands on her hips and says with an imitation of a motherly tone: '...JB...'"
            "Another moment of silence. You respond only by staring directly into her soul."
            "Suddenly, she recognizes that something is really wrong with you. In a last ditch attempt, she says that 'it's not really nice from you.'"
            jb "'I don't care.'"
            "After that she finally lets you be. 'Fuck them all...' you think for yourself."
            show screen outcome_panel("+15 PCR HATRED.")
            pause
            hide screen outcome_panel

        "[[DARK EMPATH]] REDIRECT — 'I'll handle the gift coordination personally.' (0 CZK, +2 Hatred)" if stats.player_class == "dark_empath":
            python:
                stats.increment_stats_pcr_hatred(2)
            "You read her in an instant. She doesn't want money. She wants to feel important."
            jb "'Actually — I'd like to choose the gifts myself this time. Something personal. Can you tell me what they like?'"
            "She beams. She talks for 10 minutes about their favourite chocolates."
            "You made her feel heard. You gave her nothing."
            "She leaves satisfied. You've lost nothing but 10 minutes."
            show screen outcome_panel("+2 PCR HATRED [DARK EMPATH: redirected without cost].")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Corpse in Care Home
## ---------------------------------------------------------------------------

label re_corpse_in_care_home:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "You enter the old-age care home. The moment the automatic doors open, a wall of warm, thick air hits you in the face. It smells like mould, old carpet, urine, and something underneath it… something sweet and rotten."
    "A nurse approaches you immediately. Pale, shaking. 'He's upstairs. Second floor. Room 214.'"
    "You and your colleague walk up the narrow staircase, each step worse than the previous one. The smell intensifies rapidly."
    "You haven't even opened the door yet, and you already feel your PCR hatred rising."

    python:
        stats.increment_stats_pcr_hatred(10)

    show screen outcome_panel("+10 PCR HATRED (just for being here).")
    pause
    hide screen outcome_panel

    "Your colleague opens the door to Room 214."
    "The smell almost knocks you backward."
    "There he is. A man in his 60s. Or what used to be him. He is lying in his bed, bloated, swollen beyond recognition, easily between 160 and 180 kilos of decomposing mass. His skin is greyish-green and pulled tight like an overfilled balloon."
    "Your older colleague — bald, dead inside, veteran of 1000 night shifts — looks at you and grins."
    "'This one's yours, JB. I carried worse ones.' He throws you a pair of thin latex gloves as if that would help."

    python:
        _base_chance   = 35
        _hate_bonus    = stats.pcr_hatred // 4
        _avoid_chance  = min(_base_chance + _hate_bonus, 100)

    menu:
        "[[DARK EMPATH]] LEVERAGE — Use his retirement instinct against him. (Guaranteed avoidance)" if stats.player_class == "dark_empath":
            python:
                renpy.jump("re_corpse_avoided")
            "You study his face. 17 years on the force. One pension photo on his desk."
            "He's not heartless. He's tired. He just needs permission to not care."
            jb "'Genuine question — is THIS the memory you want right before you retire?'"
            "His jaw tightens. He looks at the door. Back at you."
            "A long exhale. He walks to the hallway."
            "'I'll get two from downstairs. Wait here.'"
            "You step into the hallway and breathe clean air."
            "[[DARK EMPATH PERK]]: Avoidance guaranteed through psychological leverage."

        "OBJECT — Refuse to drag him. ([_avoid_chance]%% success chance)":
            python:
                _refusal_roll = __import__('random').randint(1, 100)
                if _refusal_roll <= _avoid_chance:
                    _avoid_success = True
                else:
                    _avoid_success = False

            python:
                if _avoid_success:
                    renpy.say(jb, "'No. I'm not dragging him. I'm not doing this.'")
                    renpy.say(None, "Your colleague stares at you for a long moment. His face doesn't move — not a muscle, not a twitch — but something in his eyes softens.")
                    renpy.say(None, "He finally sighs, long and exhausted, like a man who has seen too much.")
                    renpy.say(None, "'Fine… I'll get someone else. Just… wait outside.'")
                    renpy.say(None, "You step back into the hallway, breathing through your mouth until your lungs stop screaming.")
                    renpy.jump("re_corpse_avoided")
                else:
                    stats.increment_stats_pcr_hatred(5)
                    renpy.say(None, "You take a step back and shake your head again. 'No, seriously. I can't do this.'")
                    renpy.say(None, "Your colleague turns slowly and looks at you with an expression of disappointment mixed with superiority.")
                    renpy.say(None, "'That's cute, JB. Really cute. But you're doing it anyway.'")
                    renpy.say(None, "He taps your shoulder with the latex gloves, like he's knighting you with a sword made of rubber.")
                    renpy.say(None, "[[+5 PCR HATRED — your refusal was ignored and mocked.]]")

        "ACCEPT AND DRAG HIM. (95%% success)":
            pass

    ## Dragging outcome (reached if refusal failed or accepted)
    python:
        _drag_roll = __import__('random').randint(1, 100)
        if _drag_roll <= 5:
            stats.increment_stats_pcr_hatred(30)
            _drag_text = "You lift him and the worst happens. A wet tearing sound.\nHis abdomen ruptures. Warm, thick fluids splash over your shoes and pants.\nYou freeze completely. Shock overrides everything.\nYour colleague coughs a laugh: 'Yep… seen that before.'"
            _drag_outcome = "+30 PCR HATRED (CRITICAL WORST CASE)."
        elif _drag_roll <= 80:
            stats.increment_stats_pcr_hatred(15)
            _drag_text = "You and the team lift him. He's heavy — unbelievably heavy — but he doesn't rupture.\nThe smell, the warmth, the texture of the room… it will stay in your mind forever.\nBut at least nothing spilled."
            _drag_outcome = "+15 PCR HATRED."
        else:
            stats.increment_stats_pcr_hatred(15)
            _drag_text = "You lift him carefully. Everything stays intact. Still a nightmare — but survivable."
            _drag_outcome = "+15 PCR HATRED."

    "[_drag_text]"
    show screen outcome_panel(_drag_outcome)
    pause
    hide screen outcome_panel

    return

## Jump target when the player successfully avoids dragging
label re_corpse_avoided:
    return


## ---------------------------------------------------------------------------
## EVENT: Forgotten USB
## ---------------------------------------------------------------------------

label re_forgotten_usb:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "You are patting down a suspect's jacket in the evidence locker."
    "You feel a lump. It's a black USB drive with a taped label: 'DO NOT TOUCH'."
    "Curiosity kills the cat... but satisfaction brought it back."

    menu:
        "[[BIOHACKER]] SANDBOX FIRST — Analyze in isolation. No risk, guaranteed learning. (+10 Coding)" if stats.player_class == "biohacker":
            python:
                stats.increment_stats_coding_skill(10)
            "You don't plug it in blind. You boot a sandboxed environment on your personal device."
            "You mount the USB in read-only mode."
            "The payload detonates inside the sandbox. You watch it propagate in real time."
            "Ransomware. Crypto-locker variant. Novel obfuscation layer you haven't seen before."
            "You document everything. The behavior tree. The evasion logic. The dead-drop C2 address."
            "The knowledge is worth more than anything on the drive."
            show screen outcome_panel("+10 CODING SKILL [BIOHACKER: analyzed safely, learned from it].")
            pause
            hide screen outcome_panel

        "Plug it into your own personal laptop. [[50%% RISK]]":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= 50:
                    stats.increment_stats_coding_skill(-25)
                    _usb_text = "SCREEEECH! Your speakers blast noise.\nA skull appears on your screen. All your Python projects are being encrypted.\nIt's a nasty ransomware. You have to format everything."
                    _usb_outcome = "-25 CODING SKILL (You lost your projects)."
                else:
                    stats.increment_stats_value_money(25000)
                    _usb_text = "It opens. A text file contains a private key.\nYou check the wallet... there is some leftover Ethereum!\nYou quickly transfer it to your account."
                    _usb_outcome = "+25,000 CZK."

            "[_usb_text]"
            show screen outcome_panel(_usb_outcome)
            pause
            hide screen outcome_panel

        "Don't touch it. [[SAFE]]":
            "You leave it in the evidence room. Probably for the best."

    return


## ---------------------------------------------------------------------------
## EVENT: Turkish Fraud
## ---------------------------------------------------------------------------

label re_turkish_fraud:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "An old man comes to the station, shaking and crying."
    "'They stole my money! My uncle died in Turkey! He was a billionaire!'"
    "You listen to the story. It's the classic 'Prince Heritage' scam."
    "The victim sent 100,000 CZK to an account in Istanbul to 'release the funds'."
    "Usually, you would just file a report and file it into the trash."
    "But you look at the email headers the victim printed out. You recognize the IP masking. It's lazy."

    python:
        _tf_success = stats.coding_skill * 2
        if _tf_success >= 100:
            _tf_success = 100

    menu:
        "Track the scammer and turn the tables. [[CODING]] [[Roll chance: [_tf_success]%%] Current skill: [stats.coding_skill]":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _tf_success:
                    stats.daily_btc_income += 2500
                    stats.increment_stats_pcr_hatred(-20)
                    _tf_text = "You tell the old man to wait. You open your laptop.\nYou trace the packet route, bypass their cheap VPN, and find their real server.\nYou access their webcam. You take a screenshot of the scammer.\nYou send them one email: 'I know who you are. Send me 5k CZK a day in BTC, or I send this to the Turkish police.'\nFive minutes later, your wallet pings."
                    _tf_outcome = "+2,500 CZK DAILY PASSIVE INCOME, -20 PCR HATRED."
                else:
                    stats.increment_stats_pcr_hatred(10)
                    stats.increment_stats_value_money(-2500)
                    stats.increment_stats_coding_skill(-10)
                    _tf_text = "You try to track them, but their encryption is too good.\nOn top of that, the fraudster noticed you are trying to hack him.\nSo he returned the favor — he broke into your bank account and stole some of your money.\nYou have to tell the old man the truth that his money is lost — just as yours."
                    _tf_outcome = "+10 PCR HATRED, -10 CODING SKILLS, -2500 CZK."

            "[_tf_text]"
            show screen outcome_panel(_tf_outcome)
            pause
            hide screen outcome_panel

        "'I'm sorry sir, the money is gone.' [[GENERIC]]":
            python:
                stats.increment_stats_pcr_hatred(10)

            "You explain to him that the billionaire uncle doesn't exist."
            "He cries. You watch. It's just another Tuesday."
            show screen outcome_panel("+10 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Printer Incident
## ---------------------------------------------------------------------------

label re_printer_incident:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "The station's only printer — a relic from 2004 — has jammed again."
    "There is a queue of 3 angry colleagues waiting to print their reports."
    "The 'IT Guy' is on vacation in Croatia for the next 2 weeks."
    "You look at the error code: 'PC LOAD LETTER'."

    python:
        _print_chance = min(stats.coding_skill * 2, 100)

    menu:
        "Try to fix the driver logic and spooler. [[CODING CHECK: [_print_chance]%%]":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _print_chance:
                    stats.increment_stats_coding_skill(10)
                    _pt = "You open the terminal interface. You bypass the spooler, clear the cache manually, and restart the daemon. The printer roars to life.\nYour colleagues look at you like you just performed a miracle."
                    _po = "+10 CODING SKILL (Real-world application)."
                else:
                    stats.increment_stats_value_money(-2000)
                    stats.increment_stats_pcr_hatred(15)
                    _pt = "You try to mess with the settings... and smoke starts coming out.\nIt's hardlocked. Dead. Brick.\nThe Commander comes out. 'JB, did you break government property?'"
                    _po = "-2000 CZK, +15 PCR HATRED."

            "[_pt]"
            show screen outcome_panel(_po)
            pause
            hide screen outcome_panel

        "[[BODYBUILDER]] SLAM IT — Sometimes brute force IS the solution. (60%% success)" if stats.player_class == "bodybuilder":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= 60:
                    stats.increment_stats_pcr_hatred(-5)
                    _pt = "You lift the printer slightly — just enough — and you slam it back onto the desk.\nA sound like a dying whale.\nThen it whirrs.\nAnd prints.\nYour colleagues stare. Nobody says anything.\nYou walk away."
                    _po = "-5 PCR HATRED [BODYBUILDER: percussive maintenance — successful]."
                else:
                    stats.increment_stats_pcr_hatred(10)
                    stats.increment_stats_value_money(-3000)
                    _pt = "You slam it. The chassis cracks.\nThe screen goes dark. The drum assembly falls out.\nYour colleagues stare in silence.\nYour Commander appears at the door.\n'JB. That was government property.'"
                    _po = "+10 PCR HATRED, -3,000 CZK [BODYBUILDER: it didn't survive]."

            "[_pt]"
            show screen outcome_panel(_po)
            pause
            hide screen outcome_panel

        "Walk away. Not your problem. [[IGNORE]]":
            python:
                stats.increment_stats_pcr_hatred(5)

            "You decide not to risk it. You hand write your report."
            "It takes 45 minutes longer."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Citizen of Czechoslovakia
## ---------------------------------------------------------------------------

label re_citizen_czechoslovakia:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "You pull over a beat-up Felicia for a broken taillight. Routine stop."
    "As you approach the window, a phone is shoved into your face."
    "'AM I BEING DETAINED? AM I BEING DETAINED?' screams a teenager with a cracking voice."
    "'I am a free citizen of the Federal Republic of Czechoslovakia! The Czech Republic is a corporation!'"
    "He is live-streaming to 12 viewers. He refuses to show ID because 'ID is a slave contract'."

    menu:
        "Walk away. It's not worth the paperwork or the YouTube comments. [[IGNORE]]":
            python:
                stats.increment_stats_pcr_hatred(15)

            "You sigh, turn off your body cam for a second to rub your eyes, and get back in your car."
            "The kid screams 'VICTORY!' as you drive away."
            "You saved 3 hours of paperwork, but you lost a piece of your soul."
            show screen outcome_panel("+15 PCR HATRED (Humiliation).")
            pause
            hide screen outcome_panel

        "Smash the window, drag him out. Law is Law. [[ARREST]]":
            python:
                stats.increment_stats_pcr_hatred(5)
                stats.increment_stats_value_money(-1000)

            "You've had enough. You break the window. He screams like a banshee."
            "You arrest him for obstruction."
            "Later, you find out his parents are lawyers. The paperwork takes 6 hours."
            "Your boss fines you for the 'unnecessary property damage' to the Felicia."
            show screen outcome_panel("-1000 CZK (Fine), +5 PCR HATRED (At least you silenced him).")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Paperwork Overload
## ---------------------------------------------------------------------------

label re_paperwork_overload:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "You walk into the office. Your desk is gone."
    "It has been replaced by a literal tower of files. Theft reports, accidents, lost dogs."
    "The admin lady smirks. 'Boss wants this done by tomorrow morning.'"
    "It looks like 12 hours of manual data entry. A nightmare."

    python:
        _pw_locked = stats.coding_skill < 40

    menu:
        "'Fuck it.' Write a Python script to automate the forms. [[CODING]] [[REQ: 40 SKILL]] Current: [stats.coding_skill]":
            python:
                if stats.coding_skill >= 40:
                    stats.ai_paperwork_buff = True
                    stats.increment_stats_coding_skill(5)
                    _pw_text = "You lock the door. You open your laptop.\nYou write a scraper using Selenium and a text-filler script.\nYou hit ENTER. The computer starts doing the work for you.\nYou spend the rest of the shift drinking coffee and watching the progress bar."
                    _pw_outcome = "[[CRITICAL SUCCESS]]: AI AUTOMATION UNLOCKED! -5 Hatred daily for the rest of the game. +5 CODING SKILL."
                else:
                    stats.increment_stats_pcr_hatred(20)
                    _pw_text = "You try to automate it, but you mess up the regex.\nThe script fills every form with 'NULL'.\nYou have to redo EVERYTHING by hand. It takes all night."
                    _pw_outcome = "+20 PCR HATRED (Insufficient skill)."

            "[_pw_text]"
            show screen outcome_panel(_pw_outcome)
            pause
            hide screen outcome_panel

        "[[BIOHACKER]] STACK UP AND GRIND — Take a supplement early, optimize the queue. (Req: T2+)" if stats.player_class == "biohacker" and nootropic_tier_max >= 2:
            python:
                stats.increment_stats_pcr_hatred(8)
                stats.increment_stats_coding_skill(3)
            "You check your kit. T2 stack. Earlier than planned."
            "You take it."
            "Within 40 minutes, your pattern-recognition sharpens. The pile becomes a sorting problem."
            "You optimize the sequence. Batch similar entries. Copy-paste where the format allows."
            "By 2 AM, it's done. You're wired, but it's done. You learned something from the structure."
            show screen outcome_panel("+8 PCR HATRED, +3 CODING SKILL [BIOHACKER: cognitive stack cuts the grind].")
            pause
            hide screen outcome_panel

        "Grind through it. Suffering is part of the job. [[MANUAL]]":
            python:
                stats.increment_stats_pcr_hatred(20)

            "You sit down. You pick up a pen."
            "Name. Date. Incident. Signature."
            "Name. Date. Incident. Signature."
            "By 4 AM, you forgot your own name."
            show screen outcome_panel("+20 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Dispatch Blue Screen
## ---------------------------------------------------------------------------

label re_dispatch_blue_screen:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "It is Friday night. The radio is screaming. Total chaos."
    "Suddenly, the main dispatch monitor flickers and dies."
    "BSOD. 'CRITICAL_PROCESS_DIED'."
    "The Commander starts hitting the monitor with his baton."
    "'IT SUPPORT IS CLOSED! WE ARE BLIND!'"

    menu:
        "Push him aside and fix it via PowerShell. [[CODING]] [[REQ: 30 SKILL]] Current: [stats.coding_skill]":
            python:
                if stats.coding_skill >= 30:
                    stats.increment_stats_pcr_hatred(-10)
                    stats.increment_stats_coding_skill(5)
                    _dbs_text = "You type `Restart-Service DispatchCore -Force`.\nThe screen flickers back to life. The map reloads.\nThe Commander stares at you. 'Good work, JB.'\nFor a moment, you feel useful."
                    _dbs_outcome = "-10 PCR HATRED, +5 CODING SKILL."
                else:
                    stats.increment_stats_pcr_hatred(10)
                    _dbs_text = "You try to open the terminal, but your hands are shaking.\nThe Commander yells: 'GET OUT OF THE WAY!'\nYou failed to help. Now you just look like an idiot."
                    _dbs_outcome = "+10 PCR HATRED (Failed skill check)."

            "[_dbs_text]"
            show screen outcome_panel(_dbs_outcome)
            pause
            hide screen outcome_panel

        "Watch it burn. Enjoy the silence. [[CHAOS]]":
            python:
                stats.increment_stats_pcr_hatred(-5)

            "You sip your coffee."
            "Without the dispatch software, no one can send you anywhere."
            "For 20 minutes, there is peace."
            show screen outcome_panel("-5 PCR HATRED (Schadenfreude).")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: Tech Bro Speeding
## ---------------------------------------------------------------------------

label re_tech_bro_speeding:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "You notice a Porsche Taycan doing 150 km/h in a 90 zone."
    "You pull him over — it's a dude in his early 20s, wearing a Patagonia vest with a Matcha Latte in his cup holder."
    "On the seat next to him is a MacBook Pro with an open development environment."
    "This guy is clearly a Developer."
    "'Can you hurry up? I have to push this into production, else my CTO will kill me.'"
    "He shoves a laptop in your face. It's a terminal. Red text everywhere."

    python:
        _tbs_chance = min((stats.coding_skill * 100) // 70, 100)

    menu:
        "'I can help you with that.' [[CODING]] [[Roll chance: [_tbs_chance]%%] Current skill: [stats.coding_skill]":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _tbs_chance:
                    stats.increment_stats_coding_skill(15)
                    _tbs_text = "'It's a SyntaxError on line 84 but I can't see it!' he yells, tearing his hair out.\nYou lean in, squinting at the glowing code.\n'There,' you point with a gloved finger. 'The if statement.'\n'The logic is fine. You missed the colon at the end. Typical speeding mistake.'\nYou tap the ':' key once. The red error text turns green. The build passes.\n'...Dude... who are you?'\n'I'm just a guy who likes his syntax clean. Drive safe.'"
                    _tbs_outcome = "+15 CODING SKILL (Syntax Sniper)."
                else:
                    stats.increment_stats_pcr_hatred(5)
                    stats.increment_stats_coding_skill(-5)
                    _tbs_text = "'Let me handle this,' you say with confidence, channeling 'The Matrix'.\nYou start typing furiously, mashing keys to look professional.\n'I'm just bypassing the firewall algorithms...' you mumble.\n'Dude, what are you doing? Stop! That's my delete key!'\nThe screen goes blank. A single message appears: [[REPOSITORY DELETED]].\n'DID YOU JUST DELETE MY ENTIRE STARTUP??'\n'Technically,' you shrug, 'The bug is gone.'"
                    _tbs_outcome = "+5 PCR HATRED, -5 CODING SKILL (You are not the guy yet)."

            "[_tbs_text]"
            show screen outcome_panel(_tbs_outcome)
            pause
            hide screen outcome_panel

        "[[BIOHACKER]] STACK TALK — You see the Matcha. You recognize the mindset. (+20 Coding, -5 Hatred)" if stats.player_class == "biohacker":
            python:
                stats.increment_stats_coding_skill(20)
                stats.increment_stats_pcr_hatred(-5)
            "You notice the Matcha. The minimal-UI development environment. The posture of someone who optimizes everything."
            jb "'What's your current stack?'"
            "He blinks. The panic in his eyes recedes."
            "'...Golang, gRPC, Kubernetes. Why?'"
            jb "'Your goroutine is leaking. Line 91 — you're spawning context without cancellation. It never terminates.'"
            "Complete silence."
            "He fixes it in three keystrokes."
            "He stares at the green build indicator. Then at you."
            "'Who ARE you?'"
            jb "'Just someone who likes his concurrency clean. Drive safe.'"
            "He hands you his card before he leaves."
            show screen outcome_panel("+20 CODING SKILL, -5 PCR HATRED [BIOHACKER: found your tribe].")
            pause
            hide screen outcome_panel

        "'License and registration. Now.' [[DUTY]]":
            python:
                stats.increment_stats_pcr_hatred(5)

            "You ignore his laptop and write him a ticket for 2000 CZK."
            "'Typical,' he mutters, scanning the payment QR code."
            "His hourly rate is probably your monthly salary."
            "He zooms off."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: The Informant
## ---------------------------------------------------------------------------

label re_the_informant:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIORITY ALERT"

    "It's after midnight. You're doing a solitary patrol near the industrial district when a man steps out of the shadows."
    "He's thin, nervous, wearing a hood despite the heat."
    "You know the type. You've arrested the type. But right now he's holding an envelope, not a weapon."
    "'Officer JB, right? I know who you are. I know you want out of this force.'"
    "You freeze. How does he know your name?"
    "'I have information on your station's commander. Corruption, real corruption. I'll give it to you — but I need 3 days to disappear first. Just... don't file the report until Thursday.'"
    "He drops the envelope at your feet. Inside: 8,000 CZK cash and a USB drive."

    menu:
        "TAKE THE DEAL — Keep the money, delay the report 3 days. [[+8,000 CZK, +20 HATRED]":
            python:
                stats.increment_stats_value_money(8000)
                stats.increment_stats_pcr_hatred(20)

            "You pocket the envelope."
            "The man disappears."
            "For three days, every time you see your commander, your gut twists."
            "On Thursday you file the report. It goes nowhere — the commander has friends."
            "You kept the money but gained nothing but paranoia."
            show screen outcome_panel("+8,000 CZK, +20 PCR HATRED (Guilty conscience).")
            pause
            hide screen outcome_panel

        "REJECT AND ARREST — Do your job. Take him in.":
            python:
                stats.increment_stats_pcr_hatred(15)
                stats.increment_stats_value_money(-500)

            "You snap the cuffs on. By the book."
            "It takes 5 hours of paperwork to process him."
            "He lawyers up immediately and is released by morning."
            "The USB was blank."
            "Your commander gives you a very stiff nod in the hallway."
            "You are either a hero or a sucker. You can't tell which."
            show screen outcome_panel("-500 CZK (overtime costs), +15 PCR HATRED (pointless bureaucracy).")
            pause
            hide screen outcome_panel

        "SCARE HIM OFF — Keep the USB, let him walk, don't report anything.":
            python:
                stats.increment_stats_pcr_hatred(5)
                stats.increment_stats_coding_skill(5)

            "You take the USB. You let him run."
            "Later, alone at your desk, you plug it in."
            "It contains a zip file of leaked internal software — badly written Python scripts managing the station's scheduling system."
            "You spend two hours reverse-engineering it. You find three critical bugs."
            "Nobody sent you this. Nobody will ever know."
            show screen outcome_panel("+5 CODING SKILL (self-taught reverse engineering), +5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: The Evaluation
## ---------------------------------------------------------------------------

label re_the_evaluation:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PERFORMANCE REVIEW"

    "Your direct superior, Sergeant Novak, calls you into a side office."
    "He has a printed form. Quarterly Performance Review. KPIs. Objectives. Feedback boxes."
    "He looks almost apologetic."
    "'This is required. I need you to self-assess your... engagement with the role.'"
    "He slides the form across the desk."
    "You stare at it. It has checkboxes."
    "Choices like: 'HIGH MOTIVATION', 'TEAM PLAYER', 'COMMITTED TO DEPARTMENT VALUES'."
    "You have a pen. You have a decision to make."

    menu:
        "LIE MAGNIFICENTLY — Check every positive box. Smile. Get rated 'Outstanding'.":
            python:
                stats.increment_stats_pcr_hatred(15)
                stats.increment_stats_value_money(2000)

            "You perform. Oscar-worthy."
            "'JB, I have to say, this attitude is refreshing,' Novak says, genuinely pleased."
            "'I'm putting you forward for the Q3 performance bonus.'"
            "Two thousand CZK lands in your account two weeks later."
            "Every single CZK feels like a small piece of your soul being purchased."
            show screen outcome_panel("+2,000 CZK, +15 PCR HATRED (You lied. You got paid. You feel sick).")
            pause
            hide screen outcome_panel

        "TELL THE PARTIAL TRUTH — Neutral answers. Professional distance.":
            python:
                stats.increment_stats_pcr_hatred(5)

            "You check the middle options. 'MEETS EXPECTATIONS'. 'ADEQUATE PERFORMANCE'."
            "Novak sighs. He was hoping for more enthusiasm."
            "'Honest, I suppose. Keep your head down, JB.'"
            "You walk out feeling neither good nor bad."
            "Just... transparent."
            show screen outcome_panel("+5 PCR HATRED (The performance review industrial complex claims another victim).")
            pause
            hide screen outcome_panel

        "SABOTAGE THE FORM — Write exactly what you think. All of it.":
            python:
                stats.increment_stats_pcr_hatred(-20)
                stats.increment_stats_value_money(-1500)

            "You write it all."
            "The broken printers. The overtime. The political appointments. The lying."
            "Novak reads it slowly. His face goes through several colors."
            "He puts the form in a drawer. Never to be seen again."
            "'That's... noted, JB. You're dismissed.'"
            "A week later, your shift is extended by 3 hours 'due to staffing requirements'."
            "It cost you time and money. But you feel lighter than you have in months."
            show screen outcome_panel("-1,500 CZK (penalty shift), -20 PCR HATRED (catharsis is free).")
            pause
            hide screen outcome_panel

        "[[DARK EMPATH]] READ HIM — Give Novak exactly the narrative he needs. (0 Hatred, +2,500 CZK)" if stats.player_class == "dark_empath":
            python:
                stats.increment_stats_value_money(2500)
            "You study his face for exactly two seconds."
            "The hopeful pen tap. The slight forward lean. The way the word 'engagement' made him sit straighter."
            "He doesn't want honest feedback. He wants to feel like a good manager."
            "That costs you nothing to give."
            jb "'Sergeant, I have to say — this format actually encourages real self-reflection. Can I add a note at the bottom?'"
            "You write three sentences of measured, completely fictional positive feedback."
            "Novak reads it twice."
            "He sits back. He is genuinely moved."
            "'JB, this is exactly the kind of attitude we need right now.'"
            "'I'm putting you forward for a discretionary bonus.'"
            show screen outcome_panel("+2,500 CZK, 0 PCR HATRED [DARK EMPATH: gave him the narrative he was already writing].")
            pause
            hide screen outcome_panel

        "[[BODYBUILDER]] BRUTE SINCERITY — I do the job. The form is not the job." if stats.player_class == "bodybuilder":
            python:
                if stats.pcr_hatred >= 50:
                    stats.increment_stats_value_money(1500)
                    stats.increment_stats_pcr_hatred(-5)
                    _bb_ev_text = "Novak puts the pen down. There is something in your delivery — the flat certainty of a man who has never thought to embellish — that lands."
                    _bb_ev_text2 = "'Fair enough, JB. I'll note it as... operational focus.'"
                    _bb_ev_outcome = "+1,500 CZK, -5 PCR HATRED [BODYBUILDER: brute sincerity landed]."
                else:
                    stats.increment_stats_pcr_hatred(10)
                    _bb_ev_text = "Novak looks at you with the expression of a man whose form now has a blank where the answer should be."
                    _bb_ev_text2 = "'Right. I'll just... put MEETS EXPECTATIONS then, shall I.'"
                    _bb_ev_outcome = "+10 PCR HATRED [BODYBUILDER: the sincerity was too blunt for the room]."
            jb "'Sergeant. I show up. I do the work. You want to put that in a box — fine. But if you go out there right now and ask anyone who they want next to them on a bad call, they'll say my name.'"
            "Novak looks at the blank form. Then at you."
            "[_bb_ev_text]"
            "[_bb_ev_text2]"
            show screen outcome_panel(_bb_ev_outcome)
            pause
            hide screen outcome_panel

        "[[BIOHACKER]] SUBMIT DATA — Your actual metrics. Incident response times. Coding progression curve." if stats.player_class == "biohacker":
            python:
                stats.increment_stats_value_money(3000)
                stats.increment_stats_pcr_hatred(-5)
            jb "'Actually, Sergeant — I prepared a self-assessment.'"
            "You pull out your phone. A spreadsheet."
            "Incident response times by quarter. Coding hours logged. Skill progression. Efficiency deltas."
            "It is extremely clear that Novak has never seen anything like this in 22 years of performance reviews."
            "He stares at it for a long time."
            "Then he writes 'EXCEPTIONAL — DATA-DRIVEN CANDIDATE' in the feedback box."
            "Three days later, an unofficial bonus lands in your account. He doesn't know how else to process you."
            show screen outcome_panel("+3,000 CZK, -5 PCR HATRED [BIOHACKER: the data confused and impressed him simultaneously].")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: The Suicide Call
## ---------------------------------------------------------------------------

label re_suicide_call:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — CODE RED"

    "The radio crackles. A call comes through — welfare check, residential building, third floor."
    "An anonymous tip. 'Someone's on the ledge.'"
    "You are the closest unit."
    "You arrive in 4 minutes. There's a man. Young. Maybe 25. Sitting on the window ledge, legs dangling."
    "He sees you and doesn't move."
    "Nobody else is there yet. Just you."

    python:
        _de_available = (stats.player_class == "dark_empath")

    menu:
        "TALK — Stay calm. Keep him talking. Try to connect.":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= 60:
                    stats.increment_stats_pcr_hatred(-15)
                    stats.increment_stats_coding_skill(3)
                    _sc_text = "'What's your name?' you ask.\nHe tells you.\nYou keep talking. About nothing at first. Then about something real.\nFifteen minutes later, he's inside. Wrapped in a blanket. Talking to a paramedic.\nYou sit in your car afterward and don't move for ten minutes.\nSometimes this job is exactly what it needs to be."
                    _sc_outcome = "-15 PCR HATRED, +3 CODING SKILL (clarity of mind)."
                else:
                    stats.increment_stats_pcr_hatred(20)
                    _sc_text = "You try. You say the right words — the training words.\nBut he sees your uniform before he sees you.\nHe screams at you to leave.\nCrisis team arrives fifteen minutes later and handles it.\nYou file a report. You don't sleep well that night."
                    _sc_outcome = "+20 PCR HATRED (You weren't enough. Not this time)."

            "[_sc_text]"
            show screen outcome_panel(_sc_outcome)
            pause
            hide screen outcome_panel

        "CALL FOR BACKUP — Don't escalate. Wait for the specialists.":
            python:
                stats.increment_stats_pcr_hatred(10)

            "You call it in. Negotiation team. Ambulance. By the book."
            "They arrive in 22 minutes."
            "He's still there. They handle it in another 40."
            "Later, your report is praised as 'proper escalation procedure'."
            "You were praised for doing nothing."
            "That feels about right."
            show screen outcome_panel("+10 PCR HATRED (You followed protocol. Somehow that feels worse).")
            pause
            hide screen outcome_panel

        "[[DARK EMPATH]] MIRROR HIM — Tell him the truth about yourself. Break the wall." if _de_available:
            python:
                stats.increment_stats_pcr_hatred(-30)
                stats.increment_stats_value_money(3000)

            "You take off your hat."
            "You sit on the ground, below him, so he has to look down at you."
            jb "'I'm going to be honest with you. I hate my job. I'm planning to leave it. I don't know what comes next.'"
            jb "'I'm terrified too. But I'm not on that ledge.'"
            "He stares at you for a long time."
            "'Why are you telling me this?'"
            jb "'Because you look like someone who's sick of being lied to. So am I.'"
            "He comes down."
            "You find out later he's a programmer who burned out. Ironic."
            "He sends you a GitHub link from the hospital. 'Start here,' the message says."
            show screen outcome_panel("-30 PCR HATRED, +3,000 CZK (mental health fund donation). [[DARK EMPATH PERK]]")
            pause 2.5
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: The Retirement Party
## ---------------------------------------------------------------------------

label re_retirement_party:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — MANDATORY SOCIAL EVENT"

    "Lieutenant Kovarik is retiring today. 35 years on the force."
    "There's a mandatory gathering in the break room. Someone ordered a supermarket cake."
    "There's a printed banner that says 'CONGRATULATIONS LIEUTENANT' with slightly off-center alignment."
    "You have been cornered by three different colleagues already asking if you'll attend."
    "It's mandatory. Of course you'll attend."
    "You stand there with a plastic cup of warm sparkling wine and consider your options."

    menu:
        "MAKE A TOAST — Say something real. Honor the man.":
            python:
                stats.increment_stats_pcr_hatred(-10)

            "You raise your cup."
            jb "'35 years. Most of us couldn't do 35 months. Lieutenant Kovarik, I don't know if you loved every day of this job. But you showed up every single one of them.'"
            jb "'That means something.'"
            "Silence. Then applause."
            "Kovarik looks at you with wet eyes."
            "You meant it."
            "For about 15 minutes, you remember why you joined."
            show screen outcome_panel("-10 PCR HATRED (A moment of genuine human connection. Cherish it).")
            pause
            hide screen outcome_panel

        "SURVIVE AND ESCAPE — Attend for exactly 9 minutes. Leave.":
            python:
                stats.increment_stats_pcr_hatred(5)

            "You stand near the door. You eat one piece of cake."
            "You nod at appropriate moments."
            "After 9 minutes you check your watch, look troubled, and say: 'Radio. Sorry.'"
            "Nobody stops you."
            "Outside, you breathe deeply."
            "Freedom in the small rebellions."
            show screen outcome_panel("+5 PCR HATRED (The cake was dry anyway).")
            pause
            hide screen outcome_panel

        "[[DARK EMPATH]] SEE HIM — A real tribute. Not a performance. (-25 Hatred)" if stats.player_class == "dark_empath":
            python:
                stats.increment_stats_pcr_hatred(-25)
            "You watch Kovarik from across the room."
            "The way he holds his cup with both hands. The smile that reaches his eyes when a rookie says his name."
            "He's not waiting for the speech. He's waiting to be seen."
            "You walk over. You don't raise your cup."
            jb "'You made this place survivable, Lieutenant. That's not a small thing.'"
            "He doesn't respond immediately."
            "His jaw tightens once — the way it does when someone's trying not to cry."
            "'How did you know exactly what to—'"
            "You shrug."
            "He grips your forearm with both hands and doesn't let go for a moment."
            "For 30 seconds, you feel something at work you haven't felt in months."
            "You file it carefully. You'll need to remember this is possible."
            show screen outcome_panel("-25 PCR HATRED [DARK EMPATH: real connection found you both].")
            pause
            hide screen outcome_panel

        "[[BODYBUILDER]] RAISE YOUR VOICE — The toast lands hardest from the biggest man in the room. (-20 Hatred)" if stats.player_class == "bodybuilder":
            python:
                stats.increment_stats_pcr_hatred(-20)
            "You raise your cup."
            "Your voice is not subtle. You were not built for indoor volumes."
            jb "'THIRTY-FIVE YEARS. Most of you couldn't do thirty-five minutes of paperwork without crying into your coffee!'"
            "Laughter. Real laughter."
            jb "'Kovarik — you are the last reason I haven't burnt this building down. I mean that.'"
            "More laughter. His wife covers her mouth."
            "Kovarik is laughing and crying at the same time, and everyone in the room is watching him and feeling something real for the first time this year."
            "For one evening, you are not a number on a rota."
            "You are a person at a party."
            "That's more than you expected."
            show screen outcome_panel("-20 PCR HATRED [BODYBUILDER: blunt force honesty — most effective tribute in the room].")
            pause
            hide screen outcome_panel

        "[[BIOHACKER]] OBSERVE — Calculate the social ROI. Stay. Document. Learn. (-15 Hatred)" if stats.player_class == "biohacker":
            python:
                stats.increment_stats_pcr_hatred(-15)
            "You run the calculation. Ninety minutes. Cake quality: four out of ten. Social cost of leaving: three weeks of frosty hallway energy."
            "You stay."
            "You watch Kovarik cry twice. His wife holds his hand. Three separate colleagues say almost identical things without realising it."
            "You document the social architecture of a retirement party. The need for public witness. The way relief and grief occupy the same face."
            "On the way out, Kovarik catches your arm."
            "'I know you're planning to leave too, JB.'"
            "You say nothing."
            "'Do it before it's too late to enjoy it.'"
            "He nods at the banner — the slightly off-centre alignment."
            "'Whoever printed that gave up a long time ago. Don't be that person.'"
            "You leave with something you didn't expect: certainty."
            show screen outcome_panel("-15 PCR HATRED [BIOHACKER: the data confirmed what you already knew].")
            pause
            hide screen outcome_panel

        "DRINK EVERYTHING — Use the open bar to process your feelings.":
            python:
                stats.increment_stats_pcr_hatred(25)
                stats.increment_stats_value_money(-800)

            "You take the sparkling wine. Then the beer. Then whatever is left."
            "You tell three colleagues your honest opinion of the department."
            "One of them nods. One of them writes something down."
            "You are very slightly reprimanded the next morning."
            "You remember approximately 60%% of what you said."
            "The remaining 40%% is probably better left forgotten."
            show screen outcome_panel("-800 CZK, +25 PCR HATRED (Wet brain, hot opinions).")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: The Coding Interview
## ---------------------------------------------------------------------------

label re_coding_interview:

    scene bg_random_event
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — PRIVATE PRIORITY"

    "You parked the patrol car in a side street and told dispatch you were 'on a welfare check'."
    "You're not."
    "You have your phone in your lap. A tech startup emailed you back. Three days ago."
    "'We'd love to do a quick technical screen. 30 minutes. Python basics.'"
    "This is your chance. Right now. In uniform. In a police car."
    "Your hands are shaking."

    python:
        _bh_bonus = (stats.player_class == "biohacker")
        _ci_base  = min((stats.coding_skill * 100) // 80, 100)
        _ci_final = min(_ci_base + (20 if _bh_bonus else 0), 100)

    "Your current coding skill: [stats.coding_skill] | Success chance: [_ci_final]%%"

    menu:
        "TAKE THE INTERVIEW — Do it right now, in the car. [[CODING CHECK: [_ci_final]%%]]":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _ci_final:
                    stats.increment_stats_coding_skill(20)
                    stats.increment_stats_pcr_hatred(-15)
                    store.coding_interview_passed = True
                    _ci_text = "You answer the questions. Calmly. Clearly.\nFizzBuzz? Done. List comprehension? Done. Explain decorators? You actually explain it.\nThe interviewer goes quiet for a second.\n'Very good. Can you come in next week for a technical round?'\nYou are sitting in a police car in full uniform.\n'Yes,' you say. 'I'll be there.'"
                    _ci_outcome = "+20 CODING SKILL, -15 PCR HATRED (You just proved it to yourself). [[CODING INTERVIEW PASSED]]"
                else:
                    stats.increment_stats_coding_skill(5)
                    stats.increment_stats_pcr_hatred(15)
                    _ci_text = "It starts fine. Then they ask about async Python.\nYour brain goes blank. The words come out wrong. You hear yourself say 'callback hell' and mean something else.\nThe interviewer says 'we'll be in touch' in a tone that means the opposite.\nDispatch calls at exactly the worst moment and you have to hang up mid-apology."
                    _ci_outcome = "+5 CODING SKILL, +15 PCR HATRED (Not yet. But closer)."

            "[_ci_text]"
            show screen outcome_panel(_ci_outcome)
            pause
            hide screen outcome_panel

        "RESCHEDULE — You're not ready. Better to wait.":
            python:
                stats.increment_stats_pcr_hatred(10)
                stats.increment_stats_coding_skill(3)

            "You type a careful email. 'Due to work commitments, could we reschedule for next week?'"
            "They reply: 'Of course! Friday at 14:00?'"
            "You stare at the calendar."
            "Friday is your 12-hour shift."
            "You stare harder."
            "You reply: 'Perfect.'"
            show screen outcome_panel("+3 CODING SKILL (research done while waiting), +10 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


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
                store.corrupt_chain_1 = True  ## Money was pocketed — chain opens
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

        "TAKE IT AND DOUBLE DOWN — Accept the bribe then report him anonymously.":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= 40:
                    stats.increment_stats_value_money(5000)
                    stats.increment_stats_pcr_hatred(10)
                    store.corrupt_chain_1 = True  ## Got away with it — chain opens
                    _br_text = "You take the money. Then you file an anonymous tip about a suspicious BMW.\nInternal affairs investigates. They find nothing on you.\nThe driver gets a visit and a fine anyway.\nYou bought yourself 5000 CZK and a clean conscience. Somehow."
                    _br_outcome = "+5,000 CZK, +10 PCR HATRED (Morally complex but financially positive)."
                else:
                    stats.increment_stats_value_money(-3000)
                    stats.increment_stats_pcr_hatred(35)
                    store.corrupt_chain_1 = False  ## Caught — chain burned, driver knows your face
                    _br_text = "The driver's 'secretary' works in internal affairs.\nThree days later you are called in for a 'routine audit'.\nYou pay the money back plus a penalty.\nThe driver sends you a LinkedIn request. You decline."
                    _br_outcome = "-3,000 CZK, +35 PCR HATRED (The plan had a flaw)."

            "[_br_text]"
            show screen outcome_panel(_br_outcome)
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## EVENT: The System Update
## ---------------------------------------------------------------------------

label re_system_update:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "RANDOM EVENT — TECHNICAL INCIDENT"

    "IT Department pushed an update to the station's case management software at 06:00 AM."
    "By 07:30, nothing works."
    "Printers are printing garbage. The database is returning results from 2011."
    "Your sergeant is on the phone with IT helpdesk, shouting, slowly dying inside."
    "You watch the chaos unfold. You look at the error message on the nearest screen:"
    "'RuntimeError: Database migration failed. Rolling back to v1.4.2. Contact your administrator.'"
    "You actually understand what that means."

    python:
        _su_chance = min((stats.coding_skill * 100) // 60, 100)

    "Your coding skill: [stats.coding_skill] | Fix chance: [_su_chance]%%"

    menu:
        "[[BIOHACKER]] KNOWN FAILURE MODE — You've read the migration docs. This is a three-command fix." if stats.player_class == "biohacker":
            python:
                stats.increment_stats_coding_skill(15)
                stats.increment_stats_pcr_hatred(-20)
                stats.increment_stats_value_money(2500)
            "You push past the sergeant without a word."
            "You open a terminal."
            "You type three commands. You have seen this exact error before, on a dev forum, at 2 AM."
            "The screen turns green."
            "The database unlocks. The migration flag is cleared. Every monitor in the room reboots cleanly."
            "Absolute silence."
            "Your sergeant stares at you."
            "'JB. How did you—'"
            jb "'Stack Overflow.'"
            "He gives you the rest of the shift off and an unofficial bonus."
            "You leave before he can think of a reason to take it back."
            show screen outcome_panel("+15 CODING SKILL, -20 PCR HATRED, +2,500 CZK [BIOHACKER: no roll needed — you already knew the fix].")
            pause
            hide screen outcome_panel

        "[[DARK EMPATH]] FIND HORA — Somebody in this room isn't panicking. Find them." if stats.player_class == "dark_empath":
            python:
                stats.increment_stats_pcr_hatred(-10)
                stats.increment_stats_coding_skill(5)
            "You scan the room."
            "Everyone is panicking. Except Constable Hora, who is quietly completing paper forms as if nothing happened."
            "He's not panicking because he already knows the workaround."
            "He has been working around IT failures for eleven years."
            "You sidle up beside him."
            jb "'Hora. You know something.'"
            "He doesn't look up from the paper."
            "'The v1.4.2 rollback re-enables the legacy ODBC connector. Run the old client on desktop four.'"
            "You run the old client on desktop four."
            "Everything works."
            "You give Hora the coffee that was meant for your sergeant."
            "Some social debts are worth more than money."
            show screen outcome_panel("-10 PCR HATRED, +5 CODING SKILL [DARK EMPATH: extracted the workaround — no chaos required].")
            pause
            hide screen outcome_panel

        "FIX IT — Open a terminal and attempt the rollback manually. [[CODING CHECK: [_su_chance]%%]]":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _su_chance:
                    stats.increment_stats_coding_skill(15)
                    stats.increment_stats_pcr_hatred(-20)
                    stats.increment_stats_value_money(2500)
                    _su_text = "You push past the sergeant. You open a command prompt.\nYou type three commands.\nThe screen turns green.\nEverything works.\nAbsolute silence from every person in the room.\nYour sergeant stares at you.\n'JB. How did you—'\n'Stack Overflow,' you lie.\nHe gives you the rest of the shift off and an unofficial bonus."
                    _su_outcome = "+15 CODING SKILL, -20 PCR HATRED, +2,500 CZK (Legendary fix). [[CODE GOD]]"
                else:
                    stats.increment_stats_coding_skill(5)
                    stats.increment_stats_pcr_hatred(20)
                    _su_text = "You open the terminal and type something that looks correct.\nIt is not correct.\nThe database migration re-runs.\nNow the system is printing 2019 crime reports as today's incidents.\nA very old arrest warrant gets automatically re-activated.\nThe suspect was released 4 years ago.\nSomebody is now being very confused on a street in Brno."
                    _su_outcome = "+5 CODING SKILL (negative reinforcement), +20 PCR HATRED."

            "[_su_text]"
            show screen outcome_panel(_su_outcome)
            pause
            hide screen outcome_panel

        "DO NOTHING — This isn't your problem. Go on patrol.":
            python:
                stats.increment_stats_pcr_hatred(10)
                stats.increment_stats_coding_skill(2)

            "You leave while your colleagues argue with an automated IT ticket system."
            "You spend the shift thinking about the error message."
            "'Database migration failed.' Clean. Specific. Honest."
            "Better communication than most humans you know."
            "You look up migration patterns in your phone later. On patrol. While technically driving."
            show screen outcome_panel("+10 PCR HATRED, +2 CODING SKILL (ambient learning).")
            pause
            hide screen outcome_panel

        "DOCUMENT THE CHAOS — Write down every error, every system call. Learn from it.":
            python:
                stats.increment_stats_coding_skill(8)
                stats.increment_stats_pcr_hatred(5)

            "You sit in the corner and fill three pages of your notebook with error logs, stack traces, and observations."
            "You sketch the system architecture as you understand it."
            "You write three questions to Google later."
            "By the end of the shift, IT has fixed it remotely — but you've learned more from this disaster than two Fiverr lessons."
            show screen outcome_panel("+8 CODING SKILL (field research), +5 PCR HATRED (witnessing the chaos).")
            pause
            hide screen outcome_panel

    return
