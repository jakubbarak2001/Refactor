import sys
import time
import os
import pygame
from jb_game.game_logic.jb_dev_stats import JBStats
from jb_game.game_logic.jb_dev_decision import Decision


def resource_path(relative_path):
    """ Get absolute path to resource (Works for Dev & EXE) """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


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

    def _play_music(self, track_name):
        """Helper to play music tracks smoothly."""
        try:
            music_path = resource_path(track_name)
            pygame.mixer.init()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            pygame.mixer.music.set_volume(0.3)
        except Exception as e:
            print(f"\n[SYSTEM] Audio Warning: Could not play music '{track_name}' ({e})")

    def trigger_event(self, stats: JBStats):
        """Main entry point for the Day 24 event."""

        # --- MUSIC START: THE ARRIVAL ---
        self._play_music("mm_event_the_arrival.mp3")

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
        self._timing_decision_phase(stats)
        self._ending_phase(stats)

        return

    def _preparation_phase(self, stats: JBStats):
        """Phase 1: Preparation and clothing choice."""
        self._slow_print("\nYou decided to call MM. It's been almost 9 months since you saw him last.", delay=0.03)
        self._slow_print("He quit the force abruptly. Everyone said he was crazy. Now, rumors say he's doing great.", delay=0.03)
        self._slow_print("\nYou agreed to meet for lunch at a decent restaurant in the city center.", delay=0.03)
        self._slow_print("You look at yourself in the mirror. You look like a mess. Bags under your eyes, pale skin,", delay=0.03)
        self._slow_print("post-shift exhaustion vibrating in your hands.", delay=0.03)
        self._slow_print("\nMM always cared about image. High-end fashion, perfumes, good posture.", delay=0.03)
        self._slow_print("You could stop by the mall and buy something sharp to show him you aren't completely dead inside yet.\n", delay=0.03)

        self._slow_print("1. [PAY 12.500 CZK] ORIGINAL FIT MASH POLO SHIRT + TOBACCO HONEY GUERLAIN EDP, he has no idea what is coming... ", delay=0.02)
        self._slow_print("2. [PAY 2.500 CZK] GET A NEW CUT AND BUY NEW COOL SHIRT", delay=0.02)
        self._slow_print("3. [FREE] GO AS IS. Sweatpants and a hoodie. You don't have energy to pretend.", delay=0.02)

        choice = Decision.ask(("1", "2" "3"))

        if choice == "1":
            if stats.try_spend_money(12500):
                self.mm_points += 2
                self._slow_print("\nYou look at yourself in the mirror and question whether you actually really work at Police or Prada.", delay=0.05)
                time.sleep(1)
                self._slow_print("'Impressive. Very nice.'", delay=0.03)
                time.sleep(1)
                self._slow_print("'Let's see MM's style.'", delay=0.03)
                self._slow_print("\n[OUTCOME]: -12.500 CZK, +MM AFFECTION (He will love the effort you put into your outfit).", delay=0.01)
            else:
                self._slow_print("\nYou check your card balance... declined. Embarrassing.", delay=0.05)
                self._slow_print("You go in your old clothes anyway.", delay=0.03)
        elif choice == "2":
            if stats.try_spend_money(2500):
                self.mm_points += 1
                self._slow_print("\nThe barber played his part really well, you also buy a new sharp shirt. You look in the mirror.", delay=0.05)
                self._slow_print("For a second, you don't look like a tired cop. You look like a civilian.", delay=0.03)
                self._slow_print("\n[OUTCOME]: -2.500 CZK, +MM AFFECTION (He will appreciate the effort).", delay=0.01)
            else:
                self._slow_print("\nYou check your card balance... declined. Embarrassing.", delay=0.05)
                self._slow_print("You go in your old clothes anyway.", delay=0.05)
        elif choice == "3":
            self._slow_print("\nYou splash some cold water on your face. This is who you are right now.", delay=0.05)
            time.sleep(1)
            self._slow_print("If he's really your friend, he won't care about the hoodie.", delay=0.03)
            self._slow_print("\n[OUTCOME]: NO CHANGE.", delay=0.01)

        print(f"\nCurrent MM points [{self.mm_points}/12]")
        input("\n(PRESS ENTER)")

    def _meeting_phase(self, stats: JBStats):
        """Phase 2: The Meeting and conversation topic."""
        self._slow_print("\nYou arrive at the restaurant. You see him in the distance.", delay=0.05)
        self._slow_print("It's a shock. He looks... different. Bigger. Buffed.", delay=0.02)
        self._slow_print("His skin has color. He is smiling at the waitress.", delay=0.02)
        self._slow_print("He looks like a totally different person compared to the wreck you remember from the service.", delay=0.02)
        time.sleep(1)
        self._slow_print("\nYou sit down. Your brain is running on cheap caffeine and 2 hours of sleep after a 24hr shift.", delay=0.03)
        self._slow_print("He orders a steak. You order a coffee.", delay=0.02)
        self._slow_print("\nBefore the food arrives, you need to break the ice. What do you talk about?", delay=0.02)
        time.sleep(1)
        self._slow_print("\n1. [VENT OUT] Complain about the police, the Colonel, and the bureaucracy.", delay=0.01)
        self._slow_print("2. [BRAG] Talk about your Python projects and how much you've learned.", delay=0.01)
        self._slow_print("3. [LISTEN] Let him talk. Ask him how he did it.", delay=0.01)

        choice = Decision.ask(("1", "2", "3"))

        if choice == "1":
            stats.increment_stats_pcr_hatred(-50)
            self._slow_print("\nYou unload everything. The broken printers, the bodies, the admin mistakes.", delay=0.03)
            self._slow_print("It feels good to say it to someone who understands.", delay=0.02)
            self._slow_print("\n[OUTCOME]: -50 PCR HATRED.", delay=0.01)

        elif choice == "2":
            stats.increment_stats_coding_skill(25)
            self._slow_print("\nYou start talking about OOP, classes, and the automation script you wrote.", delay=0.03)
            self._slow_print("You try to sound professional, to show you are ready.", delay=0.02)
            self._slow_print("\n[OUTCOME]: +25 CODING SKILL.", delay=0.01)

        elif choice == "3":
            self.mm_points += 2
            self._slow_print("\nYou stay quiet. You ask him about his life.", delay=0.03)
            self._slow_print("He talks about his freedom. About sleeping 8 hours a day. About respect.", delay=0.02)
            self._slow_print("He appreciates that you actually listen.", delay=0.02)
            self._slow_print("\n[OUTCOME]: +MM AFFECTION.", delay=0.01)

        print(f"\nCurrent MM points [{self.mm_points}/12]")
        input("\n(PRESS ENTER)")

    def _drop_the_bomb_phase(self, stats: JBStats):
        """Phase 3: The realization and interruption."""
        red = "\033[91m"
        bold = "\033[1m"
        reset = "\033[0m"

        self._slow_print("\nThe food arrives. The smell of steak fills the air, but your stomach is tied in a knot.", delay=0.05)
        self._slow_print("You put down your fork. It's time.", delay=0.02)
        self._slow_print("\n'You know, MM,' you start, your voice cracking slightly. 'It was really inspiring when you left.'", delay=0.02)
        self._slow_print("'I don't really know what to do next, I'm kind of lost, and...'", delay=0.01)
        time.sleep(1)
        self._slow_print("\nHe puts his hand up. He stops you mid-sentence.", delay=0.03)
        self._slow_print("He looks you dead in the eye. The restaurant noise fades away.", delay=0.02)
        input("\n(PRESS ENTER)")

        self._slow_print(f"\n{bold}'Stop lying to yourself, JB.'{reset}", delay=0.08)
        time.sleep(1.5)
        self._slow_print(f"\n{bold}'You exactly know what to do.'{reset}", delay=0.08)
        time.sleep(1.5)
        self._slow_print(f"\n{bold}'You are just too scared to admit it.'{reset}", delay=0.08)

        print("\n(Press any key to let that sink in...)")
        input()

        self._slow_print("Silence. Absolute silence.", delay=0.10)

        # --- MUSIC SWITCH: THE AWAKENING ---
        self._play_music("mm_event_the_awakening.mp3")

        self._slow_print(f"{bold}The truth hits you like a physical blow.{reset}", delay=0.05)
        self._slow_print(f"{bold}You look down at the table. You whisper it.{reset}", delay=0.05)
        time.sleep(0.5)
        self._slow_print(f"\n{bold}{red}'You are right...'{reset}", delay=0.15)
        time.sleep(0.5)
        self._slow_print(f"{bold}{red}'I... I want to quit.'{reset}", delay=0.20)

        self._slow_print("\nAs you say those words, the reality of your debt and the Colonel's face flash before your eyes.", delay=0.05)
        if stats.pcr_hatred >= 60:
            self._slow_print(f"\n{red}[RELIEF]: -15 PCR HATRED (It feels so good to say aloud what you already knew).{reset}", delay=0.01)
        else:
            stats.increment_stats_pcr_hatred(15)
            self._slow_print(f"\n{red}[CRITICAL EFFECT]: +15 PCR HATRED (The Fear of leaving is now real). {reset}", delay=0.01)

        self._slow_print(f"\nYour current hatred is: {stats.pcr_hatred}.", delay=0.01)
        print(f"\nCurrent MM points [{self.mm_points}/12]")
        input("\n(PRESS ENTER)")


    def _coding_reality_check(self, stats: JBStats):
        """Phase 4: The Skill Check based on coding experience."""
        self._slow_print("\nMM leans back. 'Okay. You said it. Now, can you actually do it?'", delay=0.02)
        self._slow_print("'Do you have the skills? If you leave tomorrow, can you feed yourself?'", delay=0.02)

        self._slow_print(f"\n[REALITY CHECK] Current Coding Experience: {stats.coding_skill}", delay=0.01)
        input("\n(PRESS ENTER TO EVALUATE)")

        if stats.coding_skill >= 200:
            self.mm_points += 2
            stats.increment_stats_pcr_hatred(-20)
            self._slow_print("\nYou smile. You don't just know syntax. You dream in code.", delay=0.02)
            self._slow_print("You are a God Tier developer trapped in a uniform.", delay=0.02)
            self._slow_print("'I am ready,' you say. And you mean it.", delay=0.02)
            self._slow_print("\n[OUTCOME]: +MM AFFECTION, -20 PCR HATRED (Confidence).", delay=0.01)

        elif stats.coding_skill >= 150:
            self.mm_points += 1
            stats.increment_stats_pcr_hatred(-10)
            self._slow_print("\nYou are solid. You can build apps. You understand the backend.", delay=0.02)
            self._slow_print("You aren't a genius, but you are hireable. Today.", delay=0.02)
            self._slow_print("'I can do this,' you nod.", delay=0.02)
            self._slow_print("\n[OUTCOME]: +MM AFFECTION, -10 PCR HATRED.", delay=0.01)

        elif stats.coding_skill >= 100:
            self._slow_print("\nYou are a Junior. You know enough to get into trouble, maybe enough to get an internship.", delay=0.02)
            self._slow_print("It's going to be hard. But not impossible.", delay=0.02)
            self._slow_print("'I think I have a shot,' you say, hesitating slightly.", delay=0.02)
            self._slow_print("\n[OUTCOME]: NEUTRAL. (It's not great, not terrible).", delay=0.01)

        elif stats.coding_skill >= 50:
            self.mm_points -= 1
            stats.increment_stats_pcr_hatred(10)
            self._slow_print("\nYou know the basics. Loops, functions, some libraries.", delay=0.02)
            self._slow_print("But a job? Real software? You are miles away.", delay=0.02)
            self._slow_print("You look away. 'I... I'm still learning.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: -MM AFFECTION, +10 PCR HATRED (Doubt creeps in).", delay=0.01)

        else:
            self.mm_points -= 2
            stats.increment_stats_pcr_hatred(20)
            self._slow_print("\nYou have nothing. You spent your time drinking beer instead of studying.", delay=0.02)
            self._slow_print("You are just a cop with a dream and zero skills.", delay=0.02)
            self._slow_print("MM sees it. He sighs. It's a sigh of pity.", delay=0.02)
            self._slow_print("'Jesus, JB. You have nothing prepared, do you?'", delay=0.02)
            self._slow_print("\n[OUTCOME]: -MM AFFECTION, +20 PCR HATRED (Shame).", delay=0.01)

        print(f"\nCurrent MM points [{self.mm_points}/12]")
        input("\n(PRESS ENTER)")

    def _financial_reality_check(self, stats: JBStats):
        """Phase 5: Money Check. Can you afford the exit fee?"""
        self._slow_print("\nMM takes a sip of his drink. 'Skills are one thing. But freedom isn't free.'", delay=0.02)
        self._slow_print("'They are going to make you pay for your uniform, your training, every single koruna.'", delay=0.02)
        self._slow_print("'Do you have the cash? Or are you going to be in debt the moment you walk out?'", delay=0.02)

        self._slow_print(f"\n[REALITY CHECK] Current Savings: {stats.available_money} CZK", delay=0.01)
        input("\n(PRESS ENTER TO EVALUATE)")

        if stats.available_money >= 200000:
            self.mm_points += 2
            self._slow_print("\nYou nod confidently. You have been saving aggressively.", delay=0.02)
            self._slow_print("You have a war chest. You can buy your freedom twice over.", delay=0.02)
            self._slow_print("MM looks impressed. 'Smart man.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: +MM AFFECTION (Financial Freedom).", delay=0.01)

        elif stats.available_money >= 150000:
            self.mm_points += 1
            self._slow_print("\nYou have enough. It will hurt, but you won't starve.", delay=0.02)
            self._slow_print("You can pay the exit fee and still have a buffer for a few months.", delay=0.02)
            self._slow_print("'I'm covered,' you say.", delay=0.02)
            self._slow_print("\n[OUTCOME]: +MM AFFECTION (Secure).", delay=0.01)

        elif stats.available_money >= 100000:
            self._slow_print("\nYou do the math in your head. It's going to be extremely tight.", delay=0.02)
            self._slow_print("If you pay them off, you'll be eating instant noodles for weeks.", delay=0.02)
            self._slow_print("'I can scrape it together,' you admit.", delay=0.02)
            self._slow_print("\n[OUTCOME]: NEUTRAL (Survival Mode).", delay=0.01)

        elif stats.available_money >= 50000:
            self.mm_points -= 1
            self._slow_print("\nYou sweat a little. You don't have enough for the full fee.", delay=0.02)
            self._slow_print("You'll need a loan, or help from parents. It's messy.", delay=0.02)
            self._slow_print("MM shakes his head. 'That's dangerous ground, JB.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: -MM AFFECTION (Financial Risk).", delay=0.01)

        else:
            self.mm_points -= 2
            self._slow_print("\nYou are broke. You have nothing.", delay=0.02)
            self._slow_print("If you quit, you will be in immediate debt with no income.", delay=0.02)
            self._slow_print("You are trapped.", delay=0.02)
            self._slow_print("MM looks at you like you are a child. 'So you want to quit but you can't afford it?'", delay=0.02)
            self._slow_print("\n[OUTCOME]: -MM AFFECTION (Total Disaster).", delay=0.01)

        print(f"\nCurrent MM points [{self.mm_points}/12]")
        input("\n(PRESS ENTER)")

    def _hatred_motivation_check(self, stats: JBStats):
        """Phase 6: The Motivation. How much do you hate the system?"""
        self._slow_print("\nMM finishes his steak. He wipes his mouth.", delay=0.02)
        self._slow_print("'One last thing. The system. The Colonel. The meaningless orders.'", delay=0.02)
        self._slow_print("'What do you really feel about them? Is this just burnout, or is it personal?'", delay=0.02)
        self._slow_print(f"\n[REALITY CHECK] Current PCR HATRED: {stats.pcr_hatred}/100", delay=0.01)

        self._slow_print("\n1. [PURE RAGE] 'I hate them. I want to watch the station burn.'", delay=0.005)
        self._slow_print("2. [HATRED] 'I'm done. I despise what I've become here.'", delay=0.005)
        self._slow_print("3. [NEUTRAL] 'It's just a job. It didn't work out.'", delay=0.005)
        self._slow_print("4. [SOFT] 'I don't have hard feelings. Maybe it's me who is the problem.'", delay=0.005)
        self._slow_print("5. [COPING] 'Actually, the police is vital for society! The Colonel is just misunderstood!'", delay=0.005)

        choice = Decision.ask(("1", "2", "3", "4", "5"))

        if choice == "1":
            stats.increment_stats_pcr_hatred(25)
            self.mm_points += 2
            self._slow_print("\nYour eyes flash with anger. You practically spit the words out.", delay=0.02)
            self._slow_print("'I hate them so much it hurts. Every second in that uniform is torture.'", delay=0.02)
            self._slow_print("MM smiles. A genuine, shark-like smile. 'Good. Use that anger.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: +MM AFFECTION, +25 PCR HATRED (Fuel for the fire).", delay=0.01)

        elif choice == "2":
            stats.increment_stats_pcr_hatred(10)
            self.mm_points += 1
            self._slow_print("\nYou sigh. 'I hate it. I hate the politics, the lies. I need out.'", delay=0.02)
            self._slow_print("MM nods. 'That's the spirit.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: +MM AFFECTION, +10 PCR HATRED.", delay=0.01)

        elif choice == "3":
            self._slow_print("\nYou shrug. 'It's business. We just aren't a good fit.'", delay=0.02)
            self._slow_print("MM looks bored. 'Diplomatic answer. Boring, but safe.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: NEUTRAL.", delay=0.01)

        elif choice == "4":
            stats.increment_stats_pcr_hatred(-25)
            self.mm_points -= 1
            self._slow_print("\n'They gave me a chance. Maybe I'm just weak.'", delay=0.02)
            self._slow_print("MM frowns. 'Don't do that. Don't blame yourself for their toxicity.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: -MM AFFECTION, -25 PCR HATRED.", delay=0.01)

        elif choice == "5":
            stats.increment_stats_pcr_hatred(-50)
            self.mm_points -= 2
            self._slow_print("\nYou start rambling.", delay=0.02)
            self._slow_print("'I mean, the Thin Blue Line... hierarchy is important... order... discipline...'", delay=0.02)
            self._slow_print("You sound like a brainwashed cadet.", delay=0.02)
            self._slow_print("MM stares at you in disbelief. He almost laughs.", delay=0.02)
            self._slow_print("'Wow. Stockholm Syndrome much? You are defending the cage you are trapped in.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: -MM AFFECTION, -50 PCR HATRED (The mental gymnastics you do are just insane).", delay=0.01)

        print(f"\nCurrent MM points [{self.mm_points}/12]")
        input("\n(PRESS ENTER)")

    def _timing_decision_phase(self, stats: JBStats):
        """Phase 7: The Decision. When do you face the Final Boss?"""
        red = "\033[91m"
        bold = "\033[1m"
        reset = "\033[0m"

        self._slow_print("\nMM's expression darkens. The nostalgia is gone.", delay=0.02)
        time.sleep(1)
        self._slow_print(f"\n'One last thing, JB. {bold}The Colonel.{reset}'", delay=0.02)
        time.sleep(2.0)

        self._slow_print("'I know you think he is just a bureaucrat. But don't underestimate him.'", delay=0.02)
        self._slow_print(f"'He is the one who hired you, remember? He personally admitted you to the academy.'", delay=0.02)
        time.sleep(2.0)

        self._slow_print(f"'He sees you as his project. His success story. His {bold}'Good Soldier'{reset}.'", delay=0.02)
        time.sleep(1.5)

        self._slow_print(f"\n'When you hand him that resignation... he won't see it as paperwork.'", delay=0.02)
        time.sleep(0.5)
        self._slow_print(f"{bold}{red}'He will take it as a betrayal.'{reset}", delay=0.10)
        time.sleep(1.0)

        self._slow_print(f"\n'He will come at you with everything. Guilt, threats, regulations, maybe even empathy.'", delay=0.02)
        self._slow_print(f"'It won't be an easy fight. It might be the hardest thing you've ever done.'", delay=0.08)

        self._slow_print("\nHe looks at you intently.", delay=0.02)
        time.sleep(1.0)
        self._slow_print(f"{bold}'Are you ready to face him? Do you want to rip the band-aid off now?'{reset}", delay=0.02)
        self._slow_print("'Or do you need time to prepare your mind and your wallet?'", delay=0.02)

        self._slow_print("\n1. [BRAVE] 'I'm doing it tomorrow. I want it over with.' (Trigger Event Day 25, GAIN MM AFFECTION)", delay=0.005)
        self._slow_print("2. [REASONABLE] 'I need more time. I'll wait until the last moment.' (Trigger Event Day 30, NEUTRAL)", delay=0.005)

        choice = Decision.ask(("1", "2"))

        if choice == "1":
            self.mm_points += 2
            # Add dynamic attribute to stats for Game class to read later
            stats.colonel_day = 25
            self._slow_print("\nYou clench your fist. 'Tomorrow. I'm not waiting.'", delay=0.02)
            self._slow_print("MM nods, impressed. 'Good. Strike while the iron is hot. Don't let the fear settle.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: +2 MM POINTS, FINAL BOSS SET FOR DAY 25.", delay=0.01)

        elif choice == "2":
            stats.colonel_day = 30
            self._slow_print("\nYou take a deep breath. 'I need to be sure. I'll wait... I have to do it till the end of this month.'", delay=0.02)
            self._slow_print("MM nods understandingly. 'Smart. Don't rush into a war you aren't ready for.'", delay=0.02)
            self._slow_print("'Use the time wisely. Save money. Code. Prepare.'", delay=0.02)
            self._slow_print("\n[OUTCOME]: FINAL BOSS SET FOR DAY 30.", delay=0.01)

    def _ending_phase(self, stats: JBStats):
        """
        Phase 8: The Parting Gift.
        Based on MM_Points, determines what 'Weapon' or 'Status' you take to the final boss.
        """
        red = "\033[91m"
        bold = "\033[1m"
        reset = "\033[0m"

        self._slow_print("\nThe lunch is over. You pay the bill.", delay=0.02)
        self._slow_print("You walk out into the cold street. The wind hits your face.", delay=0.02)

        if self.mm_points >= 8:
            self._slow_print(f"\n{bold}MM stops you before you leave.{reset}", delay=0.02)
            self._slow_print("'Wait, JB. I have a good feeling about this. You are actually ready.'", delay=0.02)
            self._slow_print("'I want to help you. I can't fight him for you, but I can give you an edge.'", delay=0.02)
            self._slow_print("'What do you need the most? Information? Security? Or a weapon?'", delay=0.02)

            self._good_ending_selection(stats)

        elif self.mm_points >= 5:
            self._slow_print(f"\nMM shakes your hand. His grip is firm.", delay=0.02)
            self._slow_print("'It’s going to be hell, JB. He will try to break you.'", delay=0.02)
            self._slow_print("'But if you get overwhelmed, just remember that I made it.'", delay=0.02)
            self._slow_print("'I'm waiting on the other side. Don't let him win.'", delay=0.02)

            stats.final_boss_buff = "STOIC_ANCHOR"
            self._slow_print(f"\n{bold}[STATUS ACQUIRED]: STOIC ANCHOR{reset}", delay=0.04)
            self._slow_print("(Passive: You are more resistant to Colonel's attacks.)", delay=0.01)

        else:
            self._slow_print(f"\nMM looks at you with pity. He doesn't shake your hand.", delay=0.02)
            self._slow_print("'JB, you remind me of that one dude from HS,'", delay=0.02)
            self._slow_print("who saw Fast and Furious and had that dream of opening a car tuning shop, but never actually did...'", delay=0.02)
            self._slow_print("'If you go in there like this, he's going to eat you alive.'", delay=0.02)
            self._slow_print("'Good luck. You are going to need it.'", delay=0.02)

            stats.final_boss_buff = "IMPOSTER_SYNDROME"
            self._slow_print(f"\n{red}[STATUS ACQUIRED]: IMPOSTER SYNDROME{reset}", delay=0.04)
            self._slow_print("(Debuff: You start the boss fight with a DEBUFF.)", delay=0.01)

    def _good_ending_selection(self, stats: JBStats):
        """The 5-choice menu for the Good Ending."""
        green = "\033[92m"
        bold = "\033[1m"
        reset = "\033[0m"

        print(f"\n{green}CHOOSE YOUR FINAL BOSS ADVANTAGE:{reset}")

        self._slow_print(f"\n1. {bold}[THE LEGAL NUKE]{reset}", delay=0.01)
        self._slow_print("   MM gives you a file proving the 80k debt is void via 'Paragraph 4B'.", delay=0.01)
        self._slow_print("   (Effect: Instantly deals 35 HP DMG + Disables Money Threats)", delay=0.01)

        self._slow_print(f"\n2. {bold}[GHOST OF THE PAST]{reset}", delay=0.01)
        self._slow_print("   MM reveals the Colonel tried to quit 10 years ago and failed.", delay=0.01)
        self._slow_print("   (Effect: Unlocks 'Pity' Dialogue. Bleed Damage to Colonel's Ego)", delay=0.01)

        self._slow_print(f"\n3. {bold}[PRODUCTION READY SHIELD]{reset}", delay=0.01)
        self._slow_print("   MM vouches for you and writes a salary figure on a napkin.", delay=0.01)
        self._slow_print("   (Effect: -50% DMG from Anxiety/Fear attacks. You have a future.)", delay=0.01)

        self._slow_print(f"\n4. {bold}[STOIC REFACTOR]{reset}", delay=0.01)
        self._slow_print("   MM teaches you the 'Grey Rock' method to emotionally debug the Colonel.", delay=0.01)
        self._slow_print("   (Effect: Ability to Heal +40 Sanity once per fight)", delay=0.01)

        self._slow_print(f"\n5. {bold}[AGGRESSIVE OPENING]{reset}", delay=0.01)
        self._slow_print("   MM hypes you up to take the initiative and strike first.", delay=0.01)
        self._slow_print("   (Effect: Colonel starts with -20 HP. Skip the intimidation intro.)", delay=0.01)

        choice = Decision.ask(("1", "2", "3", "4", "5"))

        if choice == "1":
            self._slow_print("\nMM hands you a crumpled digital file printout.", delay=0.02)
            self._slow_print("'He lies about the contract. Quote this paragraph. Watch him choke.'", delay=0.02)
            stats.final_boss_buff = "LEGAL_NUKE"

        elif choice == "2":
            self._slow_print("\nMM leans in and whispers the Colonel's dirty secret.", delay=0.02)
            self._slow_print("You smile. suddenly, the Colonel doesn't look like a monster. He looks like a failure.", delay=0.02)
            stats.final_boss_buff = "GHOST_SECRET"

        elif choice == "3":
            self._slow_print("\nMM makes a call. He hands you a napkin with a number on it.", delay=0.02)
            self._slow_print("'That's your starting salary. He can't threaten a man who has options.'", delay=0.02)
            stats.final_boss_buff = "JOB_OFFER"

        elif choice == "4":
            self._slow_print("\nMM grabs your shoulders. He teaches you to breathe. To detach.", delay=0.02)
            self._slow_print("'He is just broken code, JB. Don't get angry. Just debug him.'", delay=0.02)
            stats.final_boss_buff = "STOIC_HEAL"

        elif choice == "5":
            self._slow_print("\nMM slaps your back hard. The adrenaline hits.", delay=0.02)
            self._slow_print("'Don't let him speak. Throw the badge on the table. Be the alpha.'", delay=0.02)
            stats.final_boss_buff = "FIRST_STRIKE"

        self._slow_print(f"\n{green}{bold}[ACE IN THE HOLE ACQUIRED]{reset}", delay=0.04)