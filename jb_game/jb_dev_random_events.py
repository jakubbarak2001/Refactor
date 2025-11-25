from jb_game.jb_dev_stats import JBStats
from jb_game.jb_dev_decision import Decision
from random import randint
from random import choice



class RandomEvents:
    """Class containing random events that turn up during the gameplay, every 3 days."""
    def __init__(self) -> None:
        """Initialises itself and the list of events."""
        self.random_events_list = [
            RandomEvents.random_event_israeli_developer,
            RandomEvents.random_event_nightmare_wolf,
            RandomEvents.random_event_civilian_small_talk,
            RandomEvents.random_event_admin_mistake_after_shift,
            RandomEvents.random_event_overtime_offer,
            RandomEvents.random_event_birthday_gift,
            RandomEvents.random_event_corpse_in_care_home
        ]

    def select_random_event(self, stats:JBStats) -> None:
        """Chooses one random event at once, then removes it from the list."""
        if not self.random_events_list:
            return

        else:
            random_event_selection = choice(self.random_events_list)
            self.random_events_list.remove(random_event_selection)
            random_event_selection(stats)

    @staticmethod
    def random_event_overtime_offer(stats: JBStats) -> None:
        """Event with overtime offer."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYour boss calls you very early in the morning, he says he needs you to "
              "\narrive at the police station urgently.\nBoth of your colleagues who were supposed to work today "
              "suddenly became sick.\nYou would get extra money for this overtime.\nOn the other hand, you "
              "don't have to accept this and perhaps you could use the time to code at home."
              "\n\nYou have the following options:"
              "\n1. [GAIN RANDOM AMOUNT OF MONEY] DO OVERTIME."
              "\n2. [GAIN RANDOM AMOUNT OF CODING SKILLS] STAY AT HOME AND CODE."
              "\n\nWHAT IS YOUR DECISION?: ")

        decision = Decision('', ('1', '2'))
        decision.create_decision()

        if decision.decision_variable_name == "1":
            random_event_chance_roll = randint(3500, 12500)
            stats.increment_stats_value_money(random_event_chance_roll)
            input("\nYou've reluctantly agreed to the overtime, at least the shift was calm."
                  "\nThe money is nice, but don't forget that your mission is to leave this job."
                  f"\n[OUTCOME]: +{random_event_chance_roll} MONEY."
                  "\n\n(CONTINUE...)")

        elif decision.decision_variable_name == "2":
            random_event_chance_roll = randint(15, 40)
            stats.increment_stats_coding_skill(random_event_chance_roll)
            input("\nAlthough your boss wasn't happy with your decision, you've decided to stay at home"
                  "\nand to use your time for studying Python. In the end you've earned a great deal of knowledge, "
                  "so this was indeed worth the time."
                  f"\n[OUTCOME]: +{random_event_chance_roll} CODING SKILLS."
                  "\n\n(CONTINUE...)")


    @staticmethod
    def random_event_birthday_gift(stats: JBStats) -> None:
        """Event with your colleagues celebrating their B-day."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou're at the station, it's dark again, "
              "\nno one really cared to even pull the blinds even though its almost 10 AM now. "
              "\nThe depressive atmosphere is omnipresent, your mind is wandering again, your eyes staring completely "
              "\nstill at the ceiling. Until your middle-aged secretary arrives, she puts her fake smile on, "
              "\nThe one, even tiny children would see through. "
              "\nYou put on your mask again and force a smile on your face, with utter joy, she announces "
              "\nthat two of your colleagues you really don't give a shit about are celebrating their "
              "\nbirthdays this week and asks you, if you want to contribute to their gifts."
              "\nYou pause for a moment and think for yourself - 'no I don't give a damm about those two retards' "
              "\nbut if I won't give anything to them, they will hate me here even more. "
              "\nWhat shall I do..."
              "\n1. [-1000,- CZK, PCR HATRED +5] PAY FOR THE GIFTS."
              "\n2. [PCR HATRED + 10] DON't PAY ANYTHING."
              "\n\nWHAT IS YOUR DECISION?: ")

        decision = Decision('', ('1', '2'))
        decision.create_decision()

        if decision.decision_variable_name == "1":
            stats.increment_stats_pcr_hatred(5)
            stats.increment_stats_value_money(-1000)
            input("\n'Sure, buy them something nice'. "
                  "\nYou don't even look in her eyes as you torment yourself with those words you've just said."
                  "\nShe is satisfied, but you are still obliged to to listen to her rantings\nand about "
                  "her children for another 15 minutes, after that, she finally leaves."
                  "\n\n'What have I done to deserve this...' you think for yourself."
                  f"\n[OUTCOME]: - 1000 CZK, +5 PCR HATRED."
                  "\n\n(CONTINUE...)"
                  )

        elif decision.decision_variable_name == "2":
            stats.increment_stats_pcr_hatred(15)
            input("\n'No...I don't want to contribute'"
                  "\nShe pauses, her mouth opens, she stares at you. You always thought that she is around her 40s, "
                  "\nBut as she started to glare at you without saying anything for few seconds, you think she "
                  "\nlooks more close to her 70s. "
                  "\nYou don't react and hold your cold hearted expression towards her, "
                  "\nnot breaking the contact with her even for a mere second."
                  "\nAfter that short moment, that felt to you like eternity. She puts her hands on her hips, and tilts "
                  "\nher head slightly towards, after which she says with a motherly tone 'JB...'"
                  "\nAfter that, another moment of silence occurs, you respond only by staring directly into her soul. "
                  "\nSuddenly, she recognises, that something is really wrong with you."
                  "\nYou are no longer taking anything from anyone. "
                  "\nIn a last ditch attempt, she says that 'it's not really nice from you'."
                  "\nYou pause for a while and reply 'could say the same about that cheap perfume on you'. "
                  "\nAfter that she finally lets you be, as she retreats to her work."
                  "\n'Fuck them all...' you think for yourself."
                  "\n[OUTCOME]: +10 PCR HATRED."
                  "\n\n(CONTINUE...)"
                  )

    @staticmethod
    def random_event_civilian_small_talk(stats: JBStats) -> None:
        """Event where an old civilian tries to make small talk and asks about your job."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou are standing next to your marked car, somewhere in the middle of nowhere."
              "\nCold wind, grey sky, nothing happening for the last 40 minutes."
              "\nYour colleague is scrolling his phone like a true professional, defending the homeland by liking memes."
              "\nYou are guarding some pointless place, because someone at the district HQ decided it looks good on paper."
              "\n\nFrom the nearby panel house, an older man slowly approaches you. Jacket from 1987, slippers, "
              "eyes full of boredom and curiosity."
              "\nAt first, he asks the usual nonsense:"
              "\n'What are you guarding here?'"
              "\n'Is something happening?'"
              "\n'Is it dangerous here?'"
              "\nYou answer politely, mechanically. You would rather be anywhere else, even filling out forms."
              "\n\nAfter a while, he gets bolder and asks the one question you didn't want to hear:"
              "\n'Tell me honestly, young man... do you like this job? What do you really think about it?'"
              "\n\nYou feel something inside you. A familiar pressure in your chest. You could finally say it."
              "\nYou could finally talk about how this job is one big circus, about the money, about the leadership..."
              "\nOr you can put your mask back on and say the neutral PR answer you've said a hundred times before."
              "\n\nYou have the following options:"
              "\n1. [80/20%] VENT OUT AND TELL HIM THE TRUTH."
              "\n2. [PCR HATRED +10] KEEP IT INSIDE AND SAY GENERAL INFORMATION."
              "\n\nWHAT IS YOUR DECISION?: ")

        decision = Decision('', ('1', '2'))
        decision.create_decision()

        if decision.decision_variable_name == "1":
            vent_chance_roll = randint(1, 100)

            if vent_chance_roll <= 80:
                stats.increment_stats_pcr_hatred(-25)
                input("\nYou look him straight in the eyes and something inside you finally snaps."
                      "\nYou start slowly, but your words gain momentum:"
                      "\nYou tell him about the shifts that never end, about the paperwork that eats your soul,"
                      "\nabout the salary that wouldn't even feed a golden retriever with anxiety."
                      "\nYou describe the leadership that has never seen the street, but writes rules for those who live on it."
                      "\nThe old man just nods, listening. No phone, no recording, just a human being who actually hears you."
                      "\nWhen you finish, he smiles sadly and says: 'I thought so... you can see it in your eyes.'"
                      "\nHe wishes you good luck and slowly walks away."
                      "\nYou feel strangely lighter. Nothing changed... but at least you said it out loud."
                      f"\n\n[OUTCOME]: PCR HATRED -25."
                      "\n\n(CONTINUE...)")

            else:
                stats.increment_stats_pcr_hatred(25)
                stats.increment_stats_value_money(-2500)
                input("\nYou look around, see no one, and decide to finally let it all out."
                      "\nYou tell him everything. How they pay you practically nothing for doing other people's dirty work."
                      "\nHow you are the punching bag of the state, how every mistake is yours, but every success disappears "
                      "in the reports."
                      "\nYou describe the leadership that moves only when someone up there needs a good photo for the news."
                      "\nThe old man listens, nods, pretends he understands."
                      "\n\nThe next day, your boss calls you in. On his desk lies a phone, screen turned towards you."
                      "\nYou see yourself on video, hear your own voice verbatim describing your 'dream job'."
                      "\nThe old man sent the recording to the city hall, 'out of concern for the state of the police'."
                      "\nYou listen to every sentence you said, but this time as evidence."
                      "\nBy the end of the week, you receive a written reprimand and a nice little financial penalty."
                      "\nNobody cares why you said it. Only that you said it."
                      f"\n\n[OUTCOME]: PCR HATRED +25, MONEY -2500 CZK."
                      "\n\n(CONTINUE...)")

        elif decision.decision_variable_name == "2":
            stats.increment_stats_pcr_hatred(10)
            input("\nYou feel the words crawling up your throat, but you swallow them back down."
                  "\nYou put on your standard-issue smile and say something about 'stable job, helping people, "
                  "good team, interesting work'."
                  "\nYou hear yourself and want to throw up, but the old man seems satisfied."
                  "\nHe nods and says: 'Well, at least someone still does this work, right?'"
                  "\nYou just answer: 'Yes, someone.'"
                  "\nHe walks away and the silence returns. Only now it feels heavier."
                  "\nYou didn't get punished, nobody recorded anything... but the pressure inside you grew again."
                  f"\n\n[OUTCOME]: PCR HATRED +10."
                  "\n\n(CONTINUE...)")

    @staticmethod
    def random_event_corpse_in_care_home(stats: JBStats) -> None:
        """Event involving a decomposing corpse found in a care home."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou enter the old-age care home. The moment the automatic doors open, "
              "a wall of warm, thick air hits you in the face. It smells like mould, "
              "old carpet, urine, and something underneath it… something sweet and rotten."
              "\n\nA nurse approaches you immediately. Pale, shaking. "
              "'He's upstairs,' she whispers. 'Second floor. Room 214.' "
              "\nShe tries to smile, but her face collapses halfway through the attempt."
              "\n\nYou and your colleague walk up the narrow staircase, each step worse than the previous one. "
              "The smell intensifies rapidly. Something is wrong. Very wrong."
              "\n\nBy the time you reach the hallway of the second floor, "
              "your eyes are watering. You already know what’s waiting for you inside that room."
              "\nYou haven't even opened the door yet, and you already feel your PCR hatred rising."
              "\n\n[OUTCOME]: +10 PCR HATRED (just for being here).")
        stats.increment_stats_pcr_hatred(10)

        print("\nYour colleague opens the door to Room 214. "
              "The smell almost knocks you backward. The air inside looks thick — "
              "as if it gained texture, like a fog made of decay."
              "\n\nThere he is. A man in his 60s. Or what used to be him. "
              "He is lying in his bed, bloated, swollen beyond recognition, "
              "easily between 160 and 180 kilos of decomposing mass. "
              "His skin is greyish-green and pulled tight like an overfilled balloon."
              "\n\nYour older colleague — bald, dead inside, veteran of 1000 night shifts — looks at you and grins."
              "\n'This one’s yours, JB. I carried worse ones,' he says. "
              "He throws you a pair of thin latex gloves as if that would help you survive a chemical disaster."
              "\n\nYou have the following options:"
              "\n1. OBJECT — refuse to drag him. [35% SUCCESS: 0 PCR HATRED]"
              "\n2. ACCEPT AND DRAG HIM. [95% clean | 5% spill]"
              "\n\nWHAT IS YOUR DECISION?: ")

        decision = Decision('', ('1', '2'))
        decision.create_decision()

        if decision.decision_variable_name == "1":
            refusal_roll = randint(1, 100)

            if refusal_roll <= 35:
                input("\nYou shake your head. 'No. I'm not dragging him. I'm not doing this.'"
                      "\nYour colleague stares at you for a long moment. His face doesn't move — "
                      "not a muscle, not a twitch — but something in his eyes softens."
                      "\nHe finally sighs, long and exhausted, like a man who has seen too much."
                      "\n'Fine… I'll get someone else. Just… wait outside.'"
                      "\nYou step back into the hallway, leaning against the peeling wall, "
                      "breathing through your mouth until your lungs stop screaming."
                      f"\n\n[OUTCOME]: 0 PCR HATRED (you avoid dragging him)."
                      "\n\n(CONTINUE...)")
                return

            else:
                # 80% failure → extra hatred + forced to drag anyway
                stats.increment_stats_pcr_hatred(5)
                input("\nYou take a step back and shake your head again. "
                      "'No, seriously. I can’t do this. I can't handle this one.'"
                      "\nYour colleague turns slowly — too slowly — and looks at you with an expression "
                      "you’ve seen on him a hundred times: disappointment mixed with superiority."
                      "\nThen he smirks. A small, cruel smirk."
                      "\n'That’s cute, JB,' he says. 'Really cute. But you're doing it anyway.'"
                      "\nHe taps your shoulder with the latex gloves, like he’s knighting you with a sword made of rubber."
                      "\n'Come on, princess. The sooner you touch him, the sooner we're done.'"
                      "\nThe other two officers in the hallway exchange looks. One of them chuckles. "
                      "You feel something hot rise in your stomach — humiliation, anger, something twisted between them."
                      "\nYou want to scream at them. You want to walk away. But you don’t."
                      "\nYou put on the gloves. They feel thin, useless — like wet paper on your hands."
                      "\nYour colleague mutters as he turns away: 'Unbelievable… I carried worse ones when I was your age.'"
                      "\nEvery word he says is gasoline poured onto the fire inside your chest."
                      f"\n\n[OUTCOME]: +5 PCR HATRED (your refusal was ignored and mocked)."
                      "\n\n(CONTINUE...)")

        drag_roll = randint(1, 100)

        if drag_roll <= 5:
            stats.increment_stats_pcr_hatred(30)
            stats.increment_stats_pcr_hatred_daily_debuff = 5  # trauma placeholder
            input("\nYou lift him and the worst happens. A wet tearing sound."
                  "\nHis abdomen ruptures. Warm, thick fluids splash over your shoes and pants."
                  "\nThe smell becomes a physical force pressing on your lungs."
                  "\nYou freeze completely. Shock overrides everything. "
                  "Your brain shuts down in self-defense."
                  "\nYour colleague coughs a laugh: 'Yep… seen that before.'"
                  "\nYou stare at the mess on your shoes, unable to move."
                  f"\n\n[OUTCOME]: +30 PCR HATRED, TRAUMA DEBUFF (+5 PCR DAILY)."
                  "\n\n(CONTINUE...)")
            return

        elif drag_roll <= 80:
            stats.increment_stats_pcr_hatred(20)
            input("\nYou and the team lift him. He’s heavy — unbelievably heavy — "
                  "but he doesn’t rupture."
                  "\nThe smell, the warmth, the texture of the room… it will stay in your mind forever."
                  "\nBut at least nothing spilled."
                  f"\n\n[OUTCOME]: +20 PCR HATRED."
                  "\n\n(CONTINUE...)")
            return

        else:
            stats.increment_stats_pcr_hatred(20)
            input("\nYou lift him carefully. Everything stays intact. "
                  "Still a nightmare — but survivable."
                  f"\n\n[OUTCOME]: +20 PCR HATRED."
                  "\n\n(CONTINUE...)")

    @staticmethod
    def random_event_admin_mistake_after_shift(stats: JBStats) -> None:
        """Event where you have to stay after night shift to fix an administrative mistake."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nIt’s 07:00 in the morning. Your night shift is finally over… at least on paper."
              "\nYou feel like a ghost in uniform. Eyes burning, head heavy, body running only on caffeine and spite."
              "\nYou’re already imagining the moment you sit in your car, put on some music and just let your brain die "
              "for an hour on the way home."
              "\n\nYou walk towards the exit. As you pass the office corridor, you hear laughter."
              "\nDay shift has just arrived. Fresh, rested, smelling like showers and normal life."
              "\nThey’re cracking jokes about weekend, football, beer, kids. Like nothing is wrong with the world."
              "\nYou look at them and feel like you’re watching another species."
              "\n\nThen you hear it:"
              "\n'JB, come here for a moment.'"
              "\n\nYour boss is sitting behind his desk with a stack of papers. Not a good sign."
              "\nHe points to a report from the night. That horrible call you had at 03:17. "
              "The one you would rather forget completely."
              "\n'You made a mistake here,' he says calmly. 'This is done wrong. If someone from above sees this, "
              "you’ll get a penalty. You need to fix it. Today. Now.'"
              "\n\nYou glance at the clock. You’ve been here all night. "
              "Everyone else is just starting their nice little 7–15 shift. Full of energy. Full of life."
              "\nYou still have an hour of travel home ahead of you. And your brain already left the building."
              "\n\nYou have two options:"
              "\n1. [-2500 CZK, PCR HATRED -10] TELL HIM YOU’RE DONE AND GO HOME (PAY THE PENALTY LATER)."
              "\n2. [PCR HATRED +20] STAY, FIX THE MISTAKE AND DESTROY WHAT’S LEFT OF YOUR SOUL."
              "\n\nWHAT IS YOUR DECISION?: ")

        decision = Decision('', ('1', '2'))
        decision.create_decision()

        if decision.decision_variable_name == "1":
            stats.increment_stats_value_money(-2500)
            stats.increment_stats_pcr_hatred(-10)
            input("\nYou look at the papers. Then at your boss. Then back at the papers."
                  "\nSomething inside you just… snaps, but in a quiet way. Not dramatic. Just final."
                  "\n'No. I’m done for today,' you say. 'If there’s a penalty, I’ll pay it.'"
                  "\nYour boss stares at you, surprised. He expected begging, excuses, submissive guilt."
                  "\nInstead, he gets a calm, dead stare."
                  "\nHe exhales through his nose, annoyed. 'Fine. I warned you. You’ll deal with the consequences.'"
                  "\nYou shrug. There’s nothing left to say."
                  "\nYou walk past the day shift, past their jokes and their fresh faces, like a ghost leaving a party "
                  "he was never invited to."
                  "\nOutside, the air is cold, but it feels… real. You know you’ll lose some money. "
                  "But you also know you just saved at least a piece of your mind."
                  f"\n\n[OUTCOME]: MONEY -2500 CZK, PCR HATRED -10."
                  "\n\n(CONTINUE...)")

        elif decision.decision_variable_name == "2":
            stats.increment_stats_pcr_hatred(20)
            input("\nYou swallow your pride, sit down and take the report."
                  "\nYour hands feel heavy. Your brain feels like wet concrete. But you start rewriting."
                  "\nYou correct forms, rewrite statements, adjust times, reprint attachments. "
                  "Your boss corrects you twice more, just to make sure you understand who’s in control here."
                  "\nIn the background, you can hear the day shift laughing in the dispatch room. "
                  "Someone is talking about a barbecue. Someone else is complaining about getting up at 6 AM."
                  "\nYou look at the clock. 08:30. 09:00. 09:30."
                  "\nEvery minute you stay here feels like someone is scraping sandpaper across your brain."
                  "\nFinally, you finish. Your boss glances at the report, nods once and says:"
                  "\n'Now it’s correct. You can go.' No thank you. No appreciation. Just a checkbox ticked."
                  "\nYou walk out of the office feeling like a battery that someone squeezed dry."
                  "\nThe penalty won't come. But you know you paid with something else."
                  f"\n\n[OUTCOME]: PCR HATRED +20."
                  "\n\n(CONTINUE...)")

    @staticmethod
    def random_event_israeli_developer(stats: JBStats) -> None:
        """Event where you meet an Israeli senior developer who teaches CS at Tel Aviv University."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou are standing at a small intersection somewhere in the middle of your district."
              "\nA light car crash happened — nothing serious, just enough to annoy you and create paperwork."
              "\nYou're managing the traffic with your glowing baton like a depressed Jedi when suddenly a man "
              "approaches you from the damaged vehicle."
              "\nHe looks completely calm, almost amused by the chaos around him."
              "\nHe has an accent you can't quite place at first, until he says:"
              "\n\n'You know, in Tel Aviv, traffic is *much* worse.'"
              "\n\nHe laughs. You don’t.")

        print("\nYou raise an eyebrow. 'Tel Aviv?'"
              "\n'Yes! I teach computer science there. Twenty-two years now. Came here for holiday… and someone "
              "forgot to use his brakes,' he says, pointing at the Czech driver from the second car, who now pretends "
              "he has never seen a steering wheel in his entire life."
              "\n\nYou ask him what he teaches."
              "\n'Algorithms. Systems architecture. Low-level optimization. And recently — machine learning basics.'"
              "\nHe shrugs. 'Students only want AI now. Nobody wants to understand pointers anymore.'"
              "\n\nYou laugh. He doesn’t.")

        print("\nThe traffic keeps flowing slowly. People complain, cars honk, and yet… you find yourself talking "
              "to this guy like he's from another planet. A better planet. A planet where people build things instead "
              "of filling out forms and writing statements at 3 AM.")

        print("\nHe gives you a short, precise monologue about problem-solving, abstraction layers, and how to "
              "think like a developer. Not technical — philosophical. Almost like he's trying to give you a cheat code "
              "for life itself.")

        print("\nFinally, when the tow truck arrives, he shakes your hand and says:"
              "\n\n'If you ever get tired of this job — and trust me, you will — come find me. Developers are always "
              "needed. Police officers? Only when something terrible happens.'"
              "\n\nThen he winks and walks away.")

        stats.increment_stats_coding_skill(10)

        input("\nYou stand there for a moment. Cars pass. The city keeps moving. "
              "\nBut inside your head, something shifted. Something opened."
              f"\n\n[OUTCOME]: CODING SKILLS +10."
              "\n\n(CONTINUE...)")


    @staticmethod
    def random_event_nightmare_wolf(stats: JBStats) -> None:
        """Nightmare event about accident, bodies and wolf-like husky. Increases PCR hatred."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nIt begins like any other day.")
        print("\nThe morning air is cold. You rub your eyes, step outside, and feel that quiet village numbness "
              "that always hits before a long shift. You get into the patrol car with your colleague, "
              "engine humming like an old animal trying to wake up.")
        print("\nDispatch calls you in that monotone voice you’ve heard thousands of times:")
        print("\n'Unit 715, proceed to the nearby village. Possible accident.'")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nYou nod. Nothing unusual. Routine. Another pointless call.")
        print("You drive.")
        print("\nThe early light cuts through the trees like thin blades. Birds. Road. Silence. Everything is normal.")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nUntil it isn’t.")
        print("\nAs you approach the village, you see one ambulance… then two… then a third… "
              "and something else — a massive emergency truck, one of those that only come out when something "
              "catastrophic happens.")
        print("\nYour colleague mutters: 'Jesus… what the hell happened here?'")
        print("You don’t answer.")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nYou don’t need to — because you already saw it.")
        print("Next to the road, lined up like a nightmare parade, are body bags.")
        print("Small ones. Tiny ones.")
        print("\nYou try not to look but your eyes betray you. The bags move slightly — or maybe it’s just the wind — "
              "but it looks like something inside is waving at you, like little limbs pressing against the fabric, "
              "reaching out, trying to escape or ask for help you can’t give.")
        print("\nA paramedic walks past with dead eyes and says nothing. "
              "He knows you saw. You know he won’t explain.")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nYou swallow hard and drive back to the station in silence.")
        print("\nWhen you enter the station, fluorescent lights hit your skull like a hammer.")
        print("You see her.")
        print("\nA woman sitting at the far wall — long black hair, hands on her lap, calm face.")
        print("You recognize her instantly.")
        print("\nYou saw her photo last week. International search. Killed her husband. Ran away. Extremely dangerous.")
        print("You blink and she’s still there.")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nYou tell your colleagues immediately:")
        print("'She’s here. That woman. The murderer. She’s right there.'")
        print("\nThey stare at you.")
        print("Then they laugh. Hard.")
        print("\n'Bro, what the fuck are you talking about?'")
        print("'Are you delusional?'")
        print("'Jesus JB, go get some sleep.'")
        print("\nYou point at the wall. She’s still sitting there. Looking at you.")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nYour colleagues slap your shoulder, laughing harder, telling you to stop making things up.")
        print("One of them taps your temple: 'Anyone home? Hello? Wake up.'")
        print("\nYou look back at the window.")
        print("There’s a giant dog outside. A wolf. No — a husky, but enormous, muscular, glowing eyes staring "
              "directly at you as if it has been waiting all night.")
        print("\nYou freeze.")
        print("'Guys… look outside. Look at the window.'")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nYour colleague smacks the back of your head.")
        print("'Enough. You’re losing it.'")
        print("\nBefore you can respond, he grabs your arms, twists them behind the chair, and ties you to it.")
        print("Another puts tape across your mouth. They don’t even hide the contempt on their faces — "
              "disappointment, disgust, tired amusement.")
        print("\nThree of them stand in front of you. Silent. Arms crossed. "
              "Looking at you as if you don’t belong here. As if you never did.")
        print("Their eyes say: you are the problem.")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nYou breathe fast. You try to talk through the tape but only muffled sounds escape.")
        print("You look back at the window.")
        print("\nThe husky is gone.")
        print("No… No, it’s not.")
        print("\nThe glass fractures. A spiderweb crack spreads across the window.")
        print("\nThen— BOOM.")
        print("The creature bursts through the glass with the force of a grenade, shards raining everywhere.")
        print("\nBefore anyone can even reach for their gun, the wolf is already on top of the first officer, "
              "its jaws tearing into his throat. Blood sprays across the wall.")
        print("The second officer barely raises his arm before the animal leaps again, ripping him open like paper.")
        print("The third doesn’t even get a scream out.")
        print("\nIt is over in seconds.")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nThe room is silent except for your ragged breathing and the sound of your heart pounding "
              "so violently it hurts.")
        print("\nThe wolf turns toward you. Slowly. Deliberately.")
        print("It steps closer, each footstep heavy as thunder. Its eyes burn into yours.")
        print("It leans forward. You feel its breath on your face. Hot. Slow. Alive.")
        print("\nAs it gathers strength to leap at you—")
        input("\n(PRESS ANY KEY TO CONTINUE...)")

        print("\nYou wake up.")
        print("Drenched in sweat. Heart racing. Sheets twisted around you like restraints. Room spinning. Mouth dry.")
        print("\nYou sit up, hands trembling. The dream felt real. Too real.")
        print("You whisper to yourself the only thing that comes out:")
        print("\n'I have to get out.'")
        stats.increment_stats_pcr_hatred(20)
        input("\n[OUTCOME]: PCR HATRED +20."
              "\n\n(CONTINUE...)")