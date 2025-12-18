import sys
import time
from jb_game.game_logic.jb_dev_stats import JBStats
from jb_game.game_logic.jb_dev_decision import Decision


class MMEvent:
    """
    Second main game event (Day 24).
    Meeting with an old colleague (MM) who successfully quit the force.
    This event determines your mental state before the final confrontation with the Colonel.
    """

    def __init__(self):
        """Initialises the event with 0 affection points."""
        self.mm_points = 0

    def _slow_print(self, text, delay=0.1):
        """
        Prints text one character at a time to create dramatic tension.
        """
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()  # Print a newline at the end

    def trigger_event(self, stats: JBStats):
        """Main entry point for the Day 24 event."""
        red = "\033[91m"
        reset = "\033[0m"

        print(f"\n{red}ARC II. - THE AWAKENING{reset}")
        print("DAY 24 - 11:30 AM")

        self._preparation_phase(stats)
        self._meeting_phase(stats)
        self._drop_the_bomb_phase(stats)
        self._coding_reality_check(stats)
        self._financial_reality_check(stats)
        self._hatred_motivation_check(stats)
        self._ending_phase(stats)

        return

    def _preparation_phase(self, stats: JBStats):
        """Phase 1: Preparation and clothing choice."""
        print("\nYou decided to call MM. It's been almost 9 months since you saw him last.")
        print("He quit the force abruptly. Everyone said he was crazy. Now, rumors say he's doing great.")
        print("\nYou agreed to meet for lunch at a decent restaurant in the city center.")
        print("You look at yourself in the mirror. You look like a mess. Bags under your eyes, pale skin,")
        print("post-shift exhaustion vibrating in your hands.")
        print("\nMM always cared about image. High-end fashion, perfumes, good posture.")
        print("You could stop by the mall and buy something sharp to show him you aren't completely dead inside yet.")

        print("\n1. [PAY 12.500 CZK] ORIGINAL FIT MASH POLO SHIRT + TOBACCO HONEY GUERLAIN EDP, he has no idea what is coming... ")
        print("\n2. [PAY 2.500 CZK] GET A NEW CUT AND BUY NEW COOL SHIRT")
        print("3. [FREE] GO AS IS. Sweatpants and a hoodie. You don't have energy to pretend.")

        choice = Decision.ask(("1", "2" "3"))

        if choice == "1":
            if stats.try_spend_money(12500):
                self.mm_points += 2
                print("\nYou look at yourself in the mirror and question yourself whether you actually really work at Police or Prada.")
                print("Impressive. Very nice.")
                print("Let's see MM's clothes.")
                print("\n[OUTCOME]: -12.500 CZK, +MM AFFECTION (He will love the effort you put into your outfit).")
            else:
                print("\nYou check your card balance... declined. Embarrassing.")
                print("You go in your old clothes anyway.")
        elif choice == "2":
            if stats.try_spend_money(2500):
                self.mm_points += 1
                print("\nThe barber played his part really well, you also buy a new sharp shirt. You look in the mirror.")
                print("For a second, you don't look like a tired cop. You look like a civilian.")
                print("\n[OUTCOME]: -2.500 CZK, +MM AFFECTION (He will appreciate the effort).")
            else:
                print("\nYou check your card balance... declined. Embarrassing.")
                print("You go in your old clothes anyway.")
        elif choice == "3":
            print("\nYou splash some cold water on your face. This is who you are right now.")
            print("If he's really your friend, he won't care about the hoodie.")
            print("\n[OUTCOME]: NO CHANGE.")

    def _meeting_phase(self, stats: JBStats):
        """Phase 2: The Meeting and conversation topic."""
        print("\nYou arrive at the restaurant. You see him in the distance.")
        print("It's a shock. He looks... different. Bigger. Buffed.")
        print("His skin has color. He is smiling at the waitress.")
        print("He looks like a totally different person compared to the wreck you remember from the service.")

        print("\nYou sit down. Your brain is running on cheap caffeine and 2 hours of sleep after a 24hr shift.")
        print("He orders a steak. You order a coffee.")
        print("\nBefore the food arrives, you need to break the ice. What do you talk about?")

        print("\n1. [VENT OUT] Complain about the police, the Colonel, and the bureaucracy.")
        print("2. [BRAG] Talk about your Python projects and how much you've learned.")
        print("3. [LISTEN] Let him talk. Ask him how he did it.")

        choice = Decision.ask(("1", "2", "3"))

        if choice == "1":
            stats.increment_stats_pcr_hatred(-50)
            print("\nYou unload everything. The broken printers, the bodies, the admin mistakes.")
            print("It feels good to say it to someone who understands.")
            print("\n[OUTCOME]: -50 PCR HATRED.")

        elif choice == "2":
            stats.increment_stats_coding_skill(25)
            print("\nYou start talking about OOP, classes, and the automation script you wrote.")
            print("You try to sound professional, to show you are ready.")
            print("\n[OUTCOME]: +25 CODING SKILL.")

        elif choice == "3":
            self.mm_points += 1
            print("\nYou stay quiet. You ask him about his life.")
            print("He talks about his freedom. About sleeping 8 hours a day. About respect.")
            print("He appreciates that you actually listen.")
            print("\n[OUTCOME]: +MM AFFECTION.")

    def _drop_the_bomb_phase(self, stats: JBStats):
        """Phase 3: The realization and interruption."""
        red = "\033[91m"
        bold = "\033[1m"
        reset = "\033[0m"

        print("\nThe food arrives. The smell of steak fills the air, but your stomach is tied in a knot.")
        print("You put down your fork. It's time.")
        print("\n'You know, MM,' you start, your voice cracking slightly. 'It was really inspiring when you left.'")
        print("'I don't really know what to do next, I'm kind of lost, and...'")

        # Dramatic interruption
        print("\nHe puts his hand up. He stops you mid-sentence.")
        print("He looks you dead in the eye. The restaurant noise fades away.")

        # Emphasized Text
        print(f"\n{bold}'Stop lying to yourself, JB.'{reset}")
        time.sleep(1.5)
        print(f"\n{bold}'You exactly know what to do.'{reset}")
        time.sleep(1.5)
        print(f"\n{bold}'You are just too scared to admit it.'{reset}")

        print("\n(Press any key to let that sink in...)")
        input()

        print("Silence. Absolute silence.")
        print("The truth hits you like a physical blow.")
        print("You look down at the table. You whisper it.")
        print()

        # SLOW ROLL REVEAL
        self._slow_print(f"{bold}{red}'You are right...'{reset}", delay=0.15)
        time.sleep(0.5)
        self._slow_print(f"{bold}{red}'I... I want to quit.'{reset}", delay=0.20)

        print("\nAs you say those words, the reality of your debt and the Colonel's face flash before your eyes.")
        stats.increment_stats_pcr_hatred(25)
        print(f"\n{red}[CRITICAL EFFECT]: +25 PCR HATRED (The Fear of leaving is now real).{reset}")

    def _coding_reality_check(self, stats: JBStats):
        """Phase 4: The Skill Check based on coding experience."""
        print("\nMM leans back. 'Okay. You said it. Now, can you actually do it?'")
        print("'Do you have the skills? If you leave tomorrow, can you feed yourself?'")

        print(f"\n[REALITY CHECK] Current Coding Experience: {stats.coding_skill}")

        if stats.coding_skill >= 200:
            self.mm_points += 2
            stats.increment_stats_pcr_hatred(-20)
            print("\nYou smile. You don't just know syntax. You dream in code.")
            print("You are a God Tier developer trapped in a uniform.")
            print("'I am ready,' you say. And you mean it.")
            print("\n[OUTCOME]: +MM AFFECTION, -20 PCR HATRED (Confidence).")

        elif stats.coding_skill >= 150:
            self.mm_points += 1
            stats.increment_stats_pcr_hatred(-10)
            print("\nYou are solid. You can build apps. You understand the backend.")
            print("You aren't a genius, but you are hireable. Today.")
            print("'I can do this,' you nod.")
            print("\n[OUTCOME]: +MM AFFECTION, -10 PCR HATRED.")

        elif stats.coding_skill >= 100:
            print("\nYou are a Junior. You know enough to get into trouble, maybe enough to get an internship.")
            print("It's going to be hard. But not impossible.")
            print("'I think I have a shot,' you say, hesitating slightly.")
            print("\n[OUTCOME]: NEUTRAL. (It's not great, not terrible).")

        elif stats.coding_skill >= 50:
            self.mm_points -= 1
            stats.increment_stats_pcr_hatred(10)
            print("\nYou know the basics. Loops, functions, some libraries.")
            print("But a job? Real software? You are miles away.")
            print("You look away. 'I... I'm still learning.'")
            print("\n[OUTCOME]: -MM AFFECTION, +10 PCR HATRED (Doubt creeps in).")

        else:
            self.mm_points -= 2
            stats.increment_stats_pcr_hatred(20)
            print("\nYou have nothing. You spent your time drinking beer instead of studying.")
            print("You are just a cop with a dream and zero skills.")
            print("MM sees it. He sighs. It's a sigh of pity.")
            print("'Jesus, JB. You have nothing prepared, do you?'")
            print("\n[OUTCOME]: -MM AFFECTION, +20 PCR HATRED (Shame).")

    def _financial_reality_check(self, stats: JBStats):
        """Phase 5: Money Check. Can you afford the exit fee?"""
        print("\nMM takes a sip of his drink. 'Skills are one thing. But freedom isn't free.'")
        print("'They are going to make you pay for your uniform, your training, every single cent.'")
        print("'Do you have the cash? Or are you going to be in debt the moment you walk out?'")

        print(f"\n[REALITY CHECK] Current Savings: {stats.available_money} CZK")

        if stats.available_money >= 200000:
            # RICH
            self.mm_points += 2
            print("\nYou nod confidently. You have been saving aggressively.")
            print("You have a war chest. You can buy your freedom twice over.")
            print("MM looks impressed. 'Smart man.'")
            print("\n[OUTCOME]: +MM AFFECTION (Financial Freedom).")

        elif stats.available_money >= 150000:
            # SOLID
            self.mm_points += 1
            print("\nYou have enough. It will hurt, but you won't starve.")
            print("You can pay the exit fee and still have a buffer for a few months.")
            print("'I'm covered,' you say.")
            print("\n[OUTCOME]: +MM AFFECTION (Secure).")

        elif stats.available_money >= 100000:
            # TIGHT
            print("\nYou do the math in your head. It's going to be extremely tight.")
            print("If you pay them off, you'll be eating instant noodles for weeks.")
            print("'I can scrape it together,' you admit.")
            print("\n[OUTCOME]: NEUTRAL (Survival Mode).")

        elif stats.available_money >= 50000:
            # RISKY
            self.mm_points -= 1
            print("\nYou sweat a little. You don't have enough for the full fee.")
            print("You'll need a loan, or help from parents. It's messy.")
            print("MM shakes his head. 'That's dangerous ground, JB.'")
            print("\n[OUTCOME]: -MM AFFECTION (Financial Risk).")

        else:
            # BROKE (<50k)
            self.mm_points -= 2
            print("\nYou are broke. You have nothing.")
            print("If you quit, you will be in immediate debt with no income.")
            print("You are trapped.")
            print("MM looks at you like you are a child. 'So you want to quit but you can't afford it?'")
            print("\n[OUTCOME]: -MM AFFECTION (Total Disaster).")

    def _hatred_motivation_check(self, stats: JBStats):
        """Phase 6: The Motivation. How much do you hate the system?"""
        print("\nMM finishes his steak. He wipes his mouth.")
        print("'One last thing. The system. The Colonel. The meaningless orders.'")
        print("'What do you really feel about them? Is this just burnout, or is it personal?'")

        print("\n1. [PURE RAGE] 'I hate them. I want to watch the station burn.'")
        print("2. [HATRED] 'I'm done. I despise what I've become here.'")
        print("3. [NEUTRAL] 'It's just a job. It didn't work out.'")
        print("4. [SOFT] 'I don't have hard feelings. Maybe it's me who is the problem.'")
        print("5. [COPING] 'Actually, the police is vital for society! The Colonel is just misunderstood!'")

        choice = Decision.ask(("1", "2", "3", "4", "5"))

        if choice == "1":
            stats.increment_stats_pcr_hatred(25)
            self.mm_points += 2
            print("\nYour eyes flash with anger. You practically spit the words out.")
            print("'I hate them so much it hurts. Every second in that uniform is torture.'")
            print("MM smiles. A genuine, shark-like smile. 'Good. Use that anger.'")
            print("\n[OUTCOME]: +MM AFFECTION, +25 PCR HATRED (Fuel for the fire).")

        elif choice == "2":
            stats.increment_stats_pcr_hatred(10)
            self.mm_points += 1
            print("\nYou sigh. 'I hate it. I hate the politics, the lies. I need out.'")
            print("MM nods. 'That's the spirit.'")
            print("\n[OUTCOME]: +MM AFFECTION, +10 PCR HATRED.")

        elif choice == "3":
            print("\nYou shrug. 'It's business. We just aren't a good fit.'")
            print("MM looks bored. 'Diplomatic answer. Boring, but safe.'")
            print("\n[OUTCOME]: NEUTRAL.")

        elif choice == "4":
            stats.increment_stats_pcr_hatred(-10)
            self.mm_points -= 1
            print("\n'They gave me a chance. Maybe I'm just weak.'")
            print("MM frowns. 'Don't do that. Don't blame yourself for their toxicity.'")
            print("\n[OUTCOME]: -MM AFFECTION, -10 PCR HATRED.")

        elif choice == "5":
            stats.increment_stats_pcr_hatred(-25)
            self.mm_points -= 2
            print("\nYou start rambling.")
            print("'I mean, the Thin Blue Line... hierarchy is important... order... discipline...'")
            print("You sound like a brainwashed cadet.")
            print("MM stares at you in disbelief. He almost laughs.")
            print("'Wow. Stockholm Syndrome much? You are defending the cage you are trapped in.'")
            print("\n[OUTCOME]: -MM AFFECTION, -25 PCR HATRED (Pathetic).")

    def _timing_decision_phase(self, stats: JBStats):
        """Phase 7: The Decision. When do you face the Final Boss?"""
        red = "\033[91m"
        bold = "\033[1m"
        reset = "\033[0m"

        print("\nMM's expression darkens. The nostalgia is gone.")
        time.sleep(1)
        print(f"\n'One last thing, JB. {bold}The Colonel.{reset}'")
        time.sleep(1.5)

        print("'I know you think he is just a bureaucrat. But don't underestimate him.'")
        print(f"'He is the one who hired you, remember? He personally admitted you to the academy.'")
        time.sleep(1.0)

        print(f"'He sees you as his project. His success story. His {bold}'Good Soldier'{reset}.'")
        time.sleep(1.5)

        print(f"\n'When you hand him that resignation... he won't see it as paperwork.'")
        time.sleep(0.5)
        self._slow_print(f"{bold}{red}'He will take it as a betrayal.'{reset}", delay=0.12)
        time.sleep(1.0)

        print(f"\n'He will come at you with everything. Guilt, threats, regulations, maybe even empathy.'")
        self._slow_print(f"'It won't be an easy fight. It might be the hardest thing you've ever done.'", delay=0.08)

        print("\nHe looks at you intently.")
        time.sleep(1.0)
        print(f"{bold}'Are you ready to face him? Do you want to rip the band-aid off now?'{reset}")
        print("'Or do you need time to prepare your mind and your wallet?'")

        print("\n1. [BRAVE] 'I'm doing it tomorrow. I want it over with.' (Trigger Event Day 25, GAIN MM AFFECTION)")
        print("2. [REASONABLE] 'I need more time. I'll wait until the last moment.' (Trigger Event Day 30, NEUTRAL)")

        choice = Decision.ask(("1", "2"))

        if choice == "1":
            self.mm_points += 2
            # Add dynamic attribute to stats for Game class to read later
            stats.colonel_day = 25
            print("\nYou clench your fist. 'Tomorrow. I'm not waiting.'")
            print("MM nods, impressed. 'Good. Strike while the iron is hot. Don't let the fear settle.'")
            print("\n[OUTCOME]: +2 MM POINTS, FINAL BOSS SET FOR DAY 25.")

        elif choice == "2":
            stats.colonel_day = 30
            print("\nYou take a deep breath. 'I need to be sure. I'll wait... I have to do it till the end of this month.'")
            print("MM nods understandingly. 'Smart. Don't rush into a war you aren't ready for.'")
            print("'Use the time wisely. Save money. Code. Prepare.'")
            print("\n[OUTCOME]: FINAL BOSS SET FOR DAY 30.")

    def _ending_phase(self, stats: JBStats):
        """
        Phase 8: The Parting Gift.
        Based on MM_Points, determines what 'Weapon' or 'Status' you take to the final boss.
        """
        red = "\033[91m"
        bold = "\033[1m"
        reset = "\033[0m"

        print("\nThe lunch is over. You pay the bill.")
        print("You walk out into the cold street. The wind hits your face.")

        # High Score: The "Good Ending" with 5 choices
        if self.mm_points > 8:
            print(f"\n{bold}MM stops you before you leave.{reset}")
            print("'Wait, JB. I have a good feeling about this. You are actually ready.'")
            print("'I want to help you. I can't fight him for you, but I can give you an edge.'")
            print("'What do you need the most? Information? Security? Or a weapon?'")

            self._good_ending_selection(stats)

        # Medium Score: Neutral Ending
        elif self.mm_points >= 5:
            print(f"\nMM shakes your hand. His grip is firm.")
            print("'It’s going to be hell, JB. He will try to break you.'")
            print("'But if you get overwhelmed, just remember that I made it.'")
            print("'I'm waiting on the other side. Don't let him win.'")

            stats.final_boss_buff = "STOIC_ANCHOR"
            print(f"\n{bold}[STATUS ACQUIRED]: STOIC ANCHOR{reset}")
            print("(Passive: The Colonel's fear attacks deal 25% less damage to your Mental State.)")

        # Low Score: Bad Ending
        else:
            print(f"\nMM looks at you with pity. He doesn't shake your hand.")
            print("'JB, you remind me of that one dude from HS,'")
            print("who saw Fast and Furious and had that dream of opening a car tuning shop, but never actually did...'")
            print("'If you go in there like this, he's going to eat you alive.'")
            print("'Good luck. You are going to need it.'")

            stats.final_boss_buff = "IMPOSTER_SYNDROME"
            print(f"\n{red}[STATUS ACQUIRED]: IMPOSTER SYNDROME{reset}")
            print("(Debuff: You start the boss fight with a DEBUFF.)")

    def _good_ending_selection(self, stats: JBStats):
        """The 5-choice menu for the Good Ending."""
        green = "\033[92m"
        bold = "\033[1m"
        reset = "\033[0m"

        print(f"\n{green}CHOOSE YOUR FINAL BOSS ADVANTAGE:{reset}")

        print(f"\n1. {bold}[THE LEGAL NUKE]{reset}")
        print("   MM gives you a file proving the 80k debt is void via 'Paragraph 4B'.")
        print("   (Effect: Instantly deals 35 HP DMG + Disables Money Threats)")

        print(f"\n2. {bold}[GHOST OF THE PAST]{reset}")
        print("   MM reveals the Colonel tried to quit 10 years ago and failed.")
        print("   (Effect: Unlocks 'Pity' Dialogue. Bleed Damage to Colonel's Ego)")

        print(f"\n3. {bold}[PRODUCTION READY SHIELD]{reset}")
        print("   MM vouches for you and writes a salary figure on a napkin.")
        print("   (Effect: -50% DMG from Anxiety/Fear attacks. You have a future.)")

        print(f"\n4. {bold}[STOIC REFACTOR]{reset}")
        print("   MM teaches you the 'Grey Rock' method to emotionally debug the Colonel.")
        print("   (Effect: Ability to Heal +40 Sanity once per fight)")

        print(f"\n5. {bold}[AGGRESSIVE OPENING]{reset}")
        print("   MM hypes you up to take the initiative and strike first.")
        print("   (Effect: Colonel starts with -20 HP. Skip the intimidation intro.)")

        choice = Decision.ask(("1", "2", "3", "4", "5"))

        if choice == "1":
            print("\nMM hands you a crumpled digital file printout.")
            print("'He lies about the contract. Quote this paragraph. Watch him choke.'")
            stats.final_boss_buff = "LEGAL_NUKE"

        elif choice == "2":
            print("\nMM leans in and whispers the Colonel's dirty secret.")
            print("You smile. suddenly, the Colonel doesn't look like a monster. He looks like a failure.")
            stats.final_boss_buff = "GHOST_SECRET"

        elif choice == "3":
            print("\nMM makes a call. He hands you a napkin with a number on it.")
            print("'That's your starting salary. He can't threaten a man who has options.'")
            stats.final_boss_buff = "JOB_OFFER"

        elif choice == "4":
            print("\nMM grabs your shoulders. He teaches you to breathe. To detach.")
            print("'He is just broken code, JB. Don't get angry. Just debug him.'")
            stats.final_boss_buff = "STOIC_HEAL"

        elif choice == "5":
            print("\nMM slaps your back hard. The adrenaline hits.")
            print("'Don't let him speak. Throw the badge on the table. Be the alpha.'")
            stats.final_boss_buff = "FIRST_STRIKE"

        print(f"\n{green}{bold}[ACE IN THE HOLE ACQUIRED]{reset}")