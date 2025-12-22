from game.game_logic.stats import Stats
from game.game_logic.decision_options import Decision
from random import randint
from random import choice

class RandomEvents:
    """Class containing random events that turn up during the gameplay, every 3 days."""
    def __init__(self) -> None:
        """Initialises itself and the list of events."""
        self.random_events_list = [
            RandomEvents.israeli_developer,
            RandomEvents.nightmare_wolf,
            RandomEvents.civilian_small_talk,
            RandomEvents.admin_mistake_after_shift,
            RandomEvents.overtime_offer,
            RandomEvents.birthday_gift,
            RandomEvents.corpse_in_care_home,
            RandomEvents.forgotten_usb,
            RandomEvents.turkish_fraud,
            RandomEvents.printer_incident,
            RandomEvents.citizen_of_czechoslovakia,
            RandomEvents.paperwork_overload,
            RandomEvents.dispatch_blue_screen,
            RandomEvents.tech_bro_speeding
        ]

    def select_random_event(self, stats: Stats) -> bool:
        """
        Chooses one random event at once, then removes it from the list.
        Returns True if an event ran, False if the list was empty.
        """
        if not self.random_events_list:
            return False

        else:
            random_event_selection = choice(self.random_events_list)
            self.random_events_list.remove(random_event_selection)
            random_event_selection(stats)
            return True

    @staticmethod
    def overtime_offer(stats: Stats) -> None:
        """Event with overtime offer."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYour boss calls you very early in the morning, he says he needs you to "
              "\narrive at the police station urgently.\nBoth of your colleagues who were supposed to work today "
              "suddenly became sick.\nYou would get extra money for this overtime.\nOn the other hand, you "
              "don't have to accept this and perhaps the time would be better used, if you were to code at home."
              "\n\nYou have the following options:"
              "\n1. [GAIN RANDOM AMOUNT OF MONEY] DO OVERTIME."
              "\n2. [GAIN RANDOM AMOUNT OF CODING SKILLS] STAY AT HOME AND CODE."
              "\n\nWHAT IS YOUR DECISION?: ")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            random_event_chance_roll = randint(3500, 12500)
            stats.increment_stats_value_money(random_event_chance_roll)
            input("\nYou've agreed to the overtime, at least the shift was calm."
                  "\nThe money is nice, but don't forget that your mission is to leave this job once and for all."
                  f"\n[OUTCOME]: +{random_event_chance_roll} MONEY."
                  "\n\n(CONTINUE...)")

        elif select_choice == "2":
            random_event_chance_roll = randint(15, 40)
            stats.increment_stats_coding_skill(random_event_chance_roll)
            input("\nAlthough your boss wasn't happy with your decision, you've decided to stay at home"
                  "\nand to use your time for studying Python. \nIn the end you've earned a great deal of knowledge."
                  f"\n[OUTCOME]: +{random_event_chance_roll} CODING SKILLS."
                  "\n\n(CONTINUE...)")


    @staticmethod
    def birthday_gift(stats: Stats) -> None:
        """Event with your colleagues celebrating their B-day."""
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou're at the station, it's dark again, "
              "\nno one really cared to even pull the blinds even though its almost 10 AM now. "
              "\nThe depressive atmosphere is omnipresent, your mind is wandering again, your eyes staring completely "
              "\nstill at the ceiling. Until your middle-aged secretary arrives, she puts her fake smile on, "
              "\nThe one, even tiny children would see through. "
              "\nYou put on your mask again and force a smile on your face, with utter joy, she announces "
              "\nthat two of your colleagues you don't give a damm about are celebrating their "
              "\nbirthdays this week and asks you, if you want to contribute to their gifts."
              "\nYou pause for a moment and think for yourself - 'Why should I contribute? I am gonna quit anyway... "
              "\nbut if I won't give anything to them, they will hate me here even more.' "
              "\n\nWhat shall I do..."
              "\n1. [-1000,- CZK, PCR HATRED +5] PAY FOR THE GIFTS."
              "\n2. [PCR HATRED + 10] DON't PAY ANYTHING."
              "\n\nWHAT IS YOUR DECISION?: ")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            stats.increment_stats_pcr_hatred(5)
            stats.increment_stats_value_money(-1000)
            input("\n'Sure, buy them something nice.' "
                  "\nYou don't even look in her eyes as you torment yourself with those words you've just said."
                  "\nShe is satisfied, but you are still obliged to to listen to her rantings\nand about "
                  "her children for another 15 minutes, after that, she finally leaves."
                  "\n\n'What have I done to deserve this...' you think for yourself."
                  f"\n[OUTCOME]: - 1000 CZK, +5 PCR HATRED."
                  "\n\n(CONTINUE...)"
                  )

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(15)
            input("\n'No...I don't want to contribute'"
                  "\nShe pauses, her mouth opens, she stares at you. You always thought that she is around her 40s, "
                  "\nBut as she started to glare at you without saying anything for few seconds, you think she "
                  "\nlooks more close to her 70s.\n "
                  "\nYou don't react and hold your cold hearted expression towards her, "
                  "\nnot breaking the contact with her even for a mere second."
                  "\nAfter that short moment, that felt to you like eternity. She puts her hands on her hips, and tilts "
                  "\nher head slightly towards, after which she says with a imitation of motherly tone '...JB...'\n"
                  "\nAfter that, another moment of silence occurs, you respond only by staring directly into her soul. "
                  "\nSuddenly, she recognises, that something is really wrong with you."
                  "\nYou are no longer taking anything from anyone. "
                  "\nIn a last ditch attempt, she says that 'it's not really nice from you'."
                  "\n'I don't care'\n"
                  "\nAfter that she finally lets you be, as she retreats to her work."
                  "\n'Fuck them all...' you think for yourself."
                  "\n[OUTCOME]: +10 PCR HATRED."
                  "\n\n(CONTINUE...)"
                  )

    @staticmethod
    def civilian_small_talk(stats: Stats) -> None:
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
              "\n2. [SAFE OPTION] KEEP IT INSIDE AND SAY GENERAL INFORMATION."
              "\n\nWHAT IS YOUR DECISION?: ")

        # REFACTOR: One line decision
        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
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
                      "\nYou see yourself on video, hear your own voice describing your 'dream job'."
                      "\nThe old man sent the recording to the city hall, 'out of concern for the state of the police'."
                      "\nYou listen to every sentence you said, but this time as evidence."
                      "\nBy the end of the week, you receive a written reprimand and a nice little financial penalty."
                      "\nNobody cares why you said it. Only that you said it."
                      f"\n\n[OUTCOME]: PCR HATRED +25, MONEY -2500 CZK."
                      "\n\n(CONTINUE...)")

        elif select_choice == "2":
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

    @staticmethod #ADD FLY BUZZING SOUND
    def corpse_in_care_home(stats: Stats) -> None:
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

        # REFACTOR: One line decision
        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            refusal_roll = randint(1, 100)

            if refusal_roll <= 35:
                input("\nYou shake your head. 'No. I'm not dragging him. I'm not doing this.'"
                      "\nYour colleague stares at you for a long moment. His face doesn't move — "
                      "not a muscle, not a twitch — but something in his eyes softens."
                      "\nHe finally sighs, long and exhausted, like a man who has seen too much."
                      "\n'Fine… I'll get someone else. Just… wait outside.'"
                      "\nYou step back into the hallway, leaning against the peeling wall, "
                      "breathing through your mouth until your lungs stop screaming."
                      f"\n\n[OUTCOME]: you avoid dragging it..."
                      "\n\n(CONTINUE...)")
                return

            else:
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
            input("\nYou lift him and the worst happens. A wet tearing sound."
                  "\nHis abdomen ruptures. Warm, thick fluids splash over your shoes and pants."
                  "\nThe smell becomes a physical force pressing on your lungs."
                  "\nYou freeze completely. Shock overrides everything. "
                  "Your brain shuts down in self-defense."
                  "\nYour colleague coughs a laugh: 'Yep… seen that before.'"
                  "\nYou stare at the mess on your shoes, unable to move."
                  f"\n\nFUCK!!! FUCK!!! FUCK!!! FUCK!!! +30 PCR HATRED."
                  "\n\n(CONTINUE...)")
            return

        elif drag_roll <= 80:
            stats.increment_stats_pcr_hatred(15)
            input("\nYou and the team lift him. He’s heavy — unbelievably heavy — "
                  "but he doesn’t rupture."
                  "\nThe smell, the warmth, the texture of the room… it will stay in your mind forever."
                  "\nBut at least nothing spilled."
                  f"\n\n[OUTCOME]: +15 PCR HATRED."
                  "\n\n(CONTINUE...)")
            return

        else:
            stats.increment_stats_pcr_hatred(15)
            input("\nYou lift him carefully. Everything stays intact. "
                  "Still a nightmare — but survivable."
                  f"\n\n[OUTCOME]: +15 PCR HATRED."
                  "\n\n(CONTINUE...)")

    @staticmethod
    def admin_mistake_after_shift(stats: Stats) -> None:
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

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            stats.increment_stats_value_money(-2500)
            stats.increment_stats_pcr_hatred(-10)
            input("\nYou look at the papers. Then at your boss. Then back at the papers."
                  "\nSomething inside you just… snaps, but in a quiet way. Not dramatic. Just final."
                  "\n'No. I’m done for today,' you say. 'If there’s a penalty, I’ll pay it.'"
                  "\nYour boss stares at you, surprised. He expected begging, excuses, submissive guilt."
                  "\nInstead, he gets a calm, dead stare.\n"
                  "\nHe exhales through his nose, annoyed. 'Fine. I warned you. You’ll deal with the consequences.'"
                  "\nYou shrug. There’s nothing left to say."
                  "\nYou walk past the day shift, past their jokes and their fresh faces, like a ghost leaving a party "
                  "he was never invited to."
                  "\nOutside, the air is cold, but it feels… real. You know you’ll lose some money. "
                  "But you also know you just saved at least a piece of your mind."
                  f"\n\n[OUTCOME]: MONEY -2500 CZK, PCR HATRED -10."
                  "\n\n(CONTINUE...)")

        elif select_choice == "2":
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
    def israeli_developer(stats: Stats) -> None:
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
              "\nHe shrugs. 'Students only want AI now. Nobody wants to understand pointers anymore.'")

        print("\nHe looks at you with a sharp, analyzing gaze, ignoring your uniform entirely."
              "\n'You have intelligent eyes. You are not just a traffic cone stand. Tell me... do you write code?'")

        can_code = stats.coding_skill >= 35

        if can_code:
            print("\n1. [SKILL CHECK >= 35 CODING SKILL: PASSED] 'Actually, I am something of a developer myself.'")
            print("2. [IMPOSTER SYNDROME] Stay silent. 'Me? No. I just... work here.'")
            valid_options = ('1', '2')
        else:
            print(f"\n1. [SKILL CHECK >= 35 CODING SKILL: LOCKED] (Current: {stats.coding_skill})")
            print("2. 'Me? No. I just... work here.'")
            valid_options = ('2',)

        print("\nWHAT IS YOUR DECISION?: ")
        select_choice = Decision.ask(valid_options)

        if select_choice == "1":
            stats.increment_stats_coding_skill(30)  # High reward
            input("\nYou adjust your belt, look around to make sure your colleague isn't listening, and reply:"
                  "\n'I work with Python. Backend mostly. Trying to get into AI integration.'"
                  "\n\nThe Professor's eyes light up. 'Python? Good for prototyping. But tell me, how do you handle "
                  "memory management when you scale? Do you understand what the Global Interpreter Lock actually does?'"
                  "\n\nYou spend the next 20 minutes in a deep technical debate. He quizzes you, challenges you, "
                  "and eventually nods in approval."
                  "\n\n'Not bad,' he says. 'Actually, quite good. You have the mind for it. Why are you wearing this costume?'"
                  "\nHe writes an email address on a piece of paper. 'Send me your GitHub. We always look for talent.'"
                  "\n\nYou walk away feeling validated for the first time in years."
                  f"\n\n[OUTCOME]: CODING SKILLS +30."
                  "\n\n(CONTINUE...)")

        elif select_choice == "2":
            stats.increment_stats_coding_skill(10)  # Small reward
            input("\nYou feel the words forming in your throat—'I study Python', 'I want to build apps'—but "
                  "the fear chokes them down."
                  "\n'Me? No,' you say, shaking your head. 'I just follow orders.'"
                  "\n\nThe Professor looks disappointed for a split second, then shrugs."
                  "\n'Pity. You have the look. Well, let me tell you something anyway...'"
                  "\n\nHe gives you a short, precise monologue about problem-solving and abstraction layers."
                  "\n'If you ever get tired of this job — and trust me, you will — learn to build things. "
                  "Police officers preserve the status quo. Developers build the future.'"
                  "\n\nYou listen. You learn something. But it hurts that you didn't speak up."
                  f"\n\n[OUTCOME]: CODING SKILLS +10."
                  "\n\n(CONTINUE...)")

    @staticmethod
    def nightmare_wolf(stats: Stats) -> None:
        """
        Nightmare event based on a dream.
        """
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")

        print("\n04:00 AM. You are on patrol. The world is grey and cold.")
        print("Dispatch sends you to an accident nearby. Routine procedure.")
        print("Your colleague drives. He doesn't say a word.")

        input("\n(PRESS ENTER)")

        print("\nArrival. There are too many flashing lights for a simple crash.")
        print("You see the body bags lined up on the wet asphalt. Small ones.")
        print("\nYou look away, but you swear one of the bags moves.")
        print("Just a twitch. A hand pressing against the black plastic.")
        print("You look at the paramedic. He lights a cigarette and looks right through you.")
        print("You get back in the car. We are leaving.")

        input("\n(PRESS ENTER)")

        print("\nBack at the station. You walk into the main room.")
        print("She is sitting there.")
        print("\nThe woman from the briefing. The murderer. Black hair, calm hands.")
        print("She is sitting on the bench, un-cuffed, watching you.")

        print("\n'That's her,' you whisper. 'That's the fugitive.'")
        print("\nYour colleagues stop drinking coffee. They look at you, then at the empty bench.")
        print("Then they start laughing.")
        print("'JB, you look like hell. Go wash your face.'")

        input("\n(PRESS ENTER)")

        print("\nYou point at the window. 'LOOK.'")
        print("Standing outside, pressing its nose against the glass, is a Husky.")
        print("But it's wrong. It's too big. It's staring directly at you.")

        print("\n'Enough,' your colleague says. His voice is dead serious.")
        print("Before you can react, they grab you.")
        print("You struggle, but they force you into a chair. Duct tape over your mouth.")
        print("They aren't angry. They look... bored. Disappointed.")

        input("\n(PRESS ENTER)")

        print("\nYou try to scream through the tape.")
        print("CRASH.")
        print("The window shatters. The Husky is inside.")
        print("\nIt doesn't bark. It just tears the first officer's throat out.")
        print("Blood sprays on the wall. The others don't even reach for their guns.")
        print("They just stand there and die.")

        print("\nThe Wolf turns to you. It walks over the bodies. It puts its face right next to yours.")
        print("You can smell its breath. Hot. Metallic.")

        input("\n(PRESS ENTER)")

        print("\nYou wake up.")
        print("You are tangled in your sheets, soaking wet. Your heart is hammering against your ribs.")
        print("The room is silent. But you can still feel the phantom pressure of the tape on your mouth.")

        stats.increment_stats_pcr_hatred(10)
        input("\n[OUTCOME]: PCR HATRED +10 (Night terror)."
              "\n\n(CONTINUE...)")

    @staticmethod
    def citizen_of_czechoslovakia(stats: Stats) -> None:
        """
        Sovereign citizen of Czechoslovakia / Influencer event.
        """
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou pull over a beat-up Felicia for a broken taillight. Routine stop.")
        print("As you approach the window, a phone is shoved into your face.")
        print("\n'AM I BEING DETAINED? AM I BEING DETAINED?' screams a teenager with a cracking voice.")
        print(
            "'I am a free citizen of the Federal Republic of Czechoslovakia! The Czech Republic is a corporation!'")
        print("\nHe is live-streaming to 12 viewers. He refuses to show ID because 'ID is a slave contract'.")

        print("\n1. [IGNORE] Walk away. It's not worth the paperwork or the YouTube comments.")
        print("2. [ARREST] Smash the window, drag him out. Law is Law.")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            stats.increment_stats_pcr_hatred(15)
            print("\nYou sigh, turn off your body cam for a second to rub your eyes, and get back in your car.")
            print("The kid screams 'VICTORY!' as you drive away.")
            print("You saved 3 hours of paperwork, but you lost a piece of your soul.")
            print("\n[OUTCOME]: +15 PCR HATRED (Humiliation).")

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(5)
            stats.increment_stats_value_money(-1000)
            print("\nYou've had enough. You break the window. He screams like a banshee.")
            print("You arrest him for obstruction.")
            print("\nLater, you find out his parents are lawyers. The paperwork takes 6 hours.")
            print("Your boss fines you for the 'unnecessary property damage' to the Felicia.")
            print("\n[OUTCOME]: -1000 CZK (Fine), +5 PCR HATRED (At least you silenced him).")

        input("\n(CONTINUE...)")

    @staticmethod
    def printer_incident(stats: Stats) -> None:
        """
        Printer event.
        """
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nThe station's only printer—a relic from 2004—has jammed again.")
        print("There is a queue of 3 angry colleagues waiting to print their reports.")
        print("The 'IT Guy' is on vacation in Croatia for the next 2 weeks.")
        print("\nYou look at the error code: 'PC LOAD LETTER'.")

        success_chance = stats.coding_skill * 2
        if success_chance > 100: success_chance = 100

        print(f"\n1. [CODING CHECK: {success_chance}%] Try to fix the driver logic and spooler.")
        print("2. [IGNORE] Walk away. Not your problem.")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            roll = randint(1, 100)
            if roll <= success_chance:
                stats.increment_stats_coding_skill(10)
                print("\nYou open the terminal interface. You bypass the spooler, clear the cache manually,")
                print("and restart the daemon. The printer roars to life.")
                print("Your colleagues look at you like you just performed a miracle.")
                print("\n[SUCCESS]: +10 CODING SKILL (Real-world application).")
            else:
                stats.increment_stats_value_money(-2000)
                stats.increment_stats_pcr_hatred(15)
                print("\nYou try to mess with the settings... and smoke starts coming out.")
                print("It's hardlocked. Dead. Brick.")
                print("The Commander comes out. 'JB, did you break government property?'")
                print("You have to pay for the repair service.")
                print("\n[FAILURE]: -2000 CZK, +15 PCR HATRED.")

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(5)
            print("\nYou decide not to risk it. You hand write your report.")
            print("It takes 45 minutes longer.")
            print("\n[OUTCOME]: +5 PCR HATRED.")

        input("\n(CONTINUE...)")

    @staticmethod
    def forgotten_usb(stats: Stats) -> None:
        """
        USB Stick event
        """
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou are patting down a suspect's jacket in the evidence locker.")
        print("You feel a lump. It's a black USB drive with a taped label: 'DO NOT TOUCH'.")
        print("Curiosity kills the cat... but satisfaction brought it back.")

        print("\n1. [RISK] Plug it into your own personal laptop.")
        print("2. [SAFE] Don't touch it.")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            print("\nYou boot up your laptop and insert the drive...")
            roll = randint(1, 100)

            if roll <= 50:
                stats.increment_stats_coding_skill(-25)
                print("\nSCREEECH! Your speakers blast noise.")
                print("A skull appears on your screen. All your Python projects are being encrypted.")
                print("It's a nasty ransomware. You have to format everything.")
                print("\n[FAILURE]: -25 CODING SKILL (You lost your projects).")
            else:
                stats.increment_stats_value_money(25000)
                print("\nIt opens. A text file contains a private key.")
                print("You check the wallet... there is some leftover Ethereum!")
                print("You quickly transfer it to your account.")
                print("\n[SUCCESS]: +25.000 CZK.")

        elif select_choice == "2":
            print("\nYou leave it in the evidence room. Probably for the best.")

        input("\n(CONTINUE...)")

    @staticmethod
    def turkish_fraud(stats: Stats) -> None:
        """
        Internet Fraud / Heritage scam.
        """
        success_chance = stats.coding_skill * 2
        if success_chance >= 100:
            success_chance = 100
        roll = randint(1, 100)

        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nAn old man comes to the station, shaking and crying.")
        print("'They stole my money! My uncle died in Turkey! He was a billionaire!'")
        print("\nYou listen to the story. It's the classic 'Prince Heritage' scam.")
        print("The victim sent 100.000 CZK to an account in Istanbul to 'release the funds'.")
        print("\nUsually, you would just file a report and file it into the trash.")
        print("But you look at the email headers the victim printed out.")
        print("You recognize the IP masking. It's lazy.")

        print(f"\n[ROLL CHANCE: {success_chance}%] Current coding skill: {stats.coding_skill}")

        print("1. [CODING] Track the scammer and turn the tables.")
        print("2. [GENERIC] 'I'm sorry sir, the money is gone.'")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            if success_chance >= roll:
                stats.daily_btc_income += 2500
                stats.increment_stats_pcr_hatred(-20)
                print("\nYou tell the old man to wait. You open your laptop.")
                print("You trace the packet route, bypass their cheap VPN, and find their real server.")
                print("You access their webcam. You take a screenshot of the scammer.")
                print(
                    "\nYou send them one email: 'I know who you are. Send me 5k CZK a day in BTC, or I send this to the Turkish police.'")
                print("\nFive minutes later, your wallet pings.")
                print("\n[SUCCESS]: You gained PASSIVE INCOME! (+2.500 CZK Daily), -20 PCR HATRED")
                print("You tell the old man you'll 'look into it' and send him home.")
            else:
                print("\nYou try to track them, but their encryption is too good.")
                print("On top of that, the fraudster noticed you are trying to hack him,.")
                print("So he returned the favor - he broke into your bank account and stole some of your money..")
                print("This didn't went well.")
                print("You have to tell the old man the truth that his money is lost - just as yours.")
                stats.increment_stats_pcr_hatred(10)
                stats.increment_stats_value_money(-2500)
                stats.increment_stats_coding_skill(-10)
                print("\n[FAILURE]: +10 PCR HATRED. -10 CODING SKILLS, -2.500 CZK")

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(10)
            print("\nYou explain to him that the billionaire uncle doesn't exist.")
            print("He cries. You watch. It's just another Tuesday.")
            print("\n[OUTCOME]: +10 PCR HATRED.")

        input("\n(CONTINUE...)")

    @staticmethod
    def dispatch_blue_screen(stats: Stats) -> None:
        """
        The Dispatch System Crash.
        """
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nIt is Friday night. The radio is screaming. Total chaos.")
        print("Suddenly, the main dispatch monitor flickers and dies.")
        print("\nBSOD. 'CRITICAL_PROCESS_DIED'.")
        print("\nThe Commander starts hitting the monitor with his baton.")
        print("'IT SUPPORT IS CLOSED! WE ARE BLIND!'")

        print(f"\n[REQ: 30 CODING SKILL] Current: {stats.coding_skill}")

        print("1. [CODING] Push him aside and fix it via PowerShell.")
        print("2. [CHAOS] Watch it burn. Enjoy the silence.")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            if stats.coding_skill >= 30:
                stats.increment_stats_pcr_hatred(-10)
                stats.increment_stats_coding_skill(5)
                print("\nYou type `Restart-Service DispatchCore -Force`.")
                print("The screen flickers back to life. The map reloads.")
                print("The Commander stares at you. 'Good work, JB.'")
                print("For a moment, you feel useful.")
                print("\n[SUCCESS]: -10 PCR HATRED, +5 CODING SKILL.")
            else:
                stats.increment_stats_pcr_hatred(10)
                print("\nYou try to open the terminal, but your hands are shaking.")
                print("The Commander yells: 'GET OUT OF THE WAY!'")
                print("You failed to help. Now you just look like an idiot.")
                print("\n[FAILURE]: +10 PCR HATRED.")

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(-5)
            print("\nYou sip your coffee.")
            print("Without the dispatch software, no one can send you anywhere.")
            print("For 20 minutes, there is peace.")
            print("\n[OUTCOME]: -5 PCR HATRED (Schadenfreude).")

        input("\n(CONTINUE...)")

    @staticmethod
    def tech_bro_speeding(stats: Stats) -> None:
        """
        Event: The Arch User & The Regex.
        """
        success_chance = (stats.coding_skill * 100) // 70

        if success_chance >= 100:
            success_chance = 100

        roll = randint(1, 100)

        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou clock a Porsche Taycan doing 150 km/h in a 90 zone.")
        print("You pull him over. The driver is shaking, pale, wearing a hoodie.")
        print("He has a faded 'I use Arch btw' sticker on the rear bumper.")
        print("\n'Officer, I wasn't speeding, I'm compiling!' he yells.")
        print("'My regex parser is failing on production logs and the CTO is going to kill me.'")
        print("He shoves a laptop in your face. It's a terminal. Red text everywhere.")

        print(f"\n[ROLL CHANCE: {success_chance}%] Current coding skill: {stats.coding_skill}")

        print("1. [CODING] 'Move over. I know Regex.'")
        print("2. [DUTY] 'License and registration. Now.'")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            if success_chance >= roll:
                stats.increment_stats_coding_skill(15)
                print("\nYou lean in through the window and look at the chaos.")
                print("'You're missing a positive lookahead for the special characters,' you say.")
                print("\nYou reach over, push his hands away, and type from memory:")
                print(">> ^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$")
                print("\nYou hit Enter. The wall of red text turns into a stream of green 'PASS'.")
                print("\nThe driver stares at the screen. Then at you. Then back at the screen.")
                print("'You... you fixed it? In one line? From your head?'")
                print("He is absolutely fucking mind-blown. He looks at you like you are a god.")
                print("'I'm sorry about the speed, Officer. I... I need to rethink my life.'")
                print("He drives away slowly, too in awe to speed.")
                print("\n[SUCCESS]: +15 CODING SKILL (Regex God).")
            else:
                stats.increment_stats_pcr_hatred(5)
                stats.increment_stats_coding_skill(-5)
                print("\nYou try to look cool. 'You just need a backslash here...'")
                print("You type a command. The terminal freezes. The kernel panics.")
                print("\nThe driver screams. 'YOU BRICKED MY BUILD! DO YOU KNOW HOW LONG THIS TAKES?'")
                print("He laughs in your face. 'Stick to writing tickets, cop. Leave the code to the pros.'")
                print("He peels off, leaving you in a cloud of dust and humiliation.")
                print("\n[FAILURE]: +5 PCR HATRED, -5 CODING SKILL.")

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(5)
            print("\nYou ignore his laptop and write him a ticket for 2000 CZK.")
            print("'Typical,' he mutters, scanning the payment QR code.")
            print("'I bet your ticket system runs on Windows Server 2008. Disgusting.'")
            print("He zooms off.")
            print("\n[OUTCOME]: +5 PCR HATRED.")

        input("\n(CONTINUE...)")

    @staticmethod
    def paperwork_overload(stats: Stats) -> None:
        """
        Event: The Paperwork Mountain.
        Mechanic: Unlockable Daily Buff (AI Automation).
        """
        input("\nRANDOM EVENT!"
              "\n\n(CONTINUE...)")
        print("\nYou walk into the office. Your desk is gone.")
        print("It has been replaced by a literal tower of files. Theft reports, accidents, lost dogs.")
        print("The admin lady smirks. 'Boss wants this done by tomorrow morning.'")
        print("\nIt looks like 12 hours of manual data entry. A nightmare.")

        print(f"\n[REQ: 40 CODING SKILL] Current: {stats.coding_skill}")

        print("1. [CODING] 'Fuck it.' Write a Python script to automate the forms.")
        print("2. [MANUAL] Grind through it. Suffering is part of the job.")

        select_choice = Decision.ask(('1', '2'))

        if select_choice == "1":
            if stats.coding_skill >= 40:
                stats.ai_paperwork_buff = True
                stats.increment_stats_coding_skill(5)
                print("\nYou lock the door. You open your laptop.")
                print("You write a scraper using Selenium and a text-filler script.")
                print("You hit ENTER. The computer starts doing the work for you.")
                print("You spend the rest of the shift drinking coffee and watching the progress bar.")
                print("\n[CRITICAL SUCCESS]: AI AUTOMATION UNLOCKED!")
                print("Your script will now handle reports daily. (-5 Hatred per day).")
            else:
                stats.increment_stats_pcr_hatred(20)
                print("\nYou try to automate it, but you mess up the regex.")
                print("The script fills every form with 'NULL'.")
                print("You have to redo EVERYTHING by hand. It takes all night.")
                print("\n[FAILURE]: +20 PCR HATRED.")

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(20)
            print("\nYou sit down. You pick up a pen.")
            print("Name. Date. Incident. Signature.")
            print("Name. Date. Incident. Signature.")
            print("By 4 AM, you forgot your own name.")
            print("\n[OUTCOME]: +20 PCR HATRED.")

        input("\n(CONTINUE...)")