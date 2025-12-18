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

        print("\n1. [PAY 2.500 CZK] BUY A NEW OUTFIT. Impress him.")
        print("2. [FREE] GO AS IS. Sweatpants and a hoodie. You don't have energy to pretend.")

        choice = Decision.ask(("1", "2"))

        if choice == "1":
            if stats.try_spend_money(2500):
                self.mm_points += 1
                print("\nYou buy a sharp shirt and new chinos. You look in the mirror.")
                print("For a second, you don't look like a tired cop. You look like a civilian.")
                print("\n[OUTCOME]: -2.500 CZK, +MM AFFECTION (He will appreciate the effort).")
            else:
                print("\nYou check your card balance... declined. Embarrassing.")
                print("You go in your old clothes anyway.")
        elif choice == "2":
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
            print("\n[OUTCOME]: +2 MM POINTS, +25 PCR HATRED (Fuel for the fire).")

        elif choice == "2":
            stats.increment_stats_pcr_hatred(10)
            self.mm_points += 1
            print("\nYou sigh. 'I hate it. I hate the politics, the lies. I need out.'")
            print("MM nods. 'That's the spirit.'")
            print("\n[OUTCOME]: +1 MM POINT, +10 PCR HATRED.")

        elif choice == "3":
            print("\nYou shrug. 'It's business. We just aren't a good fit.'")
            print("MM looks bored. 'Diplomatic answer. Boring, but safe.'")
            print("\n[OUTCOME]: NEUTRAL.")

        elif choice == "4":
            stats.increment_stats_pcr_hatred(-10)
            self.mm_points -= 1
            print("\n'They gave me a chance. Maybe I'm just weak.'")
            print("MM frowns. 'Don't do that. Don't blame yourself for their toxicity.'")
            print("\n[OUTCOME]: -1 MM POINT, -10 PCR HATRED.")

        elif choice == "5":
            stats.increment_stats_pcr_hatred(-25)
            self.mm_points -= 2
            print("\nYou start rambling.")
            print("'I mean, the Thin Blue Line... hierarchy is important... order... discipline...'")
            print("You sound like a brainwashed cadet.")
            print("MM stares at you in disbelief. He almost laughs.")
            print("'Wow. Stockholm Syndrome much? You are defending the cage you are trapped in.'")
            print("\n[OUTCOME]: -2 MM POINTS, -25 PCR HATRED (Pathetic).")