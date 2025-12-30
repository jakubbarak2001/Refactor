import os
import sys
import time

import pygame
from rich import print
from rich.panel import Panel

from game.game_logic.interaction import Interaction
from game.game_logic.press_enter_to_continue import continue_prompt
from game.game_logic.stats import Stats


def resource_path(relative_path):
    """ Get absolute path to resource (Works for Dev & EXE) """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class MartinMeetingEvent:
    """
    Second main game event (Day 24).
    Meeting with an old colleague who successfully quit the force.
    This event determines your mental state before the final confrontation with the Colonel.
    """

    def __init__(self):
        """Initialises the event with 0 affection points."""
        self.martin_meeting_affection_points = 0

    def _slow_print(self, text, delay=0.1):
        """
        Prints text one character at a time to create dramatic tension.
        If text contains Rich markup (e.g., [red]text[/red]), it will be rendered properly.
        """
        # Check if text already contains Rich markup tags
        if "[" in text and ("]" in text or "[/" in text):
            # Text contains Rich markup, print it directly with Rich
            print(text)
        else:
            # Plain text, print character-by-character
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
            pygame.mixer.music.set_volume(0.15)  # 50% of original volume
        except Exception as e:
            print(f"\n[SYSTEM] Audio Warning: Could not play music '{track_name}' ({e})")

    def _show_affection_points(self):
        """
        Display current affection points in a Rich Panel with royal purple styling.
        Similar to Interaction.show_outcome but with purple color scheme.
        """
        formatted_text = f"[bright_white]CURRENT AFFECTION POINTS[/bright_white]: [{self.martin_meeting_affection_points}/12] POINTS."
        
        # Display in a Rich Panel with royal purple border (using color(129) for royal purple)
        print(Panel(
            formatted_text,
            border_style="bold color(129)",
            title="[bold white on color(129)] > AFFECTION < [/]",
            padding=(1, 2),
            expand=False
        ))

    def _show_reality_check(self, reality_text: str):
        """
        Display a reality check message in a Rich Panel with yellow styling.
        Similar to Outcome and Affection boxes but smaller and with yellow color scheme.
        No title bar, just the content with border (like "Press enter to continue").
        
        Args:
            reality_text: The reality check message text
                         Example: "Current Coding Experience: 150"
        """
        formatted_text = f"[bright_yellow][REALITY CHECK][/bright_yellow]: {reality_text}"
        
        # Display in a smaller Rich Panel with yellow border (using Panel.fit for compact size)
        # No title, just content with border
        print(Panel.fit(
            formatted_text,
            border_style="bold yellow",
            padding=(1, 2)
        ))

    def trigger_event(self, stats: Stats):
        """Main entry point for the Day 24 event."""

        # --- MUSIC START: THE ARRIVAL ---
        self._play_music("martin_meeting_event_the_arrival.mp3")

        print("\n[red]ARC II. - THE AWAKENING[/red]")
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

    def _preparation_phase(self, stats: Stats):
        """Phase 1: Preparation and clothing choice."""
        self._slow_print("\nYou decided to call your friend Martin. It's been almost 9 months since you saw him last.",
                         delay=0.02)
        self._slow_print("He quit the force abruptly. Everyone said he was crazy. Now, rumors say he's doing great.",
                         delay=0.02)
        self._slow_print("\nYou agreed to meet for lunch at a decent restaurant in the city center.", delay=0.01)
        self._slow_print("You look at yourself in the mirror. You look like a mess. Bags under your eyes, pale skin,",
                         delay=0.01)
        self._slow_print("post-shift exhaustion vibrating in your hands.", delay=0.01)
        self._slow_print("\nHe always cared about image. High-end fashion, perfumes, good posture.", delay=0.01)
        self._slow_print(
            "You could stop by the mall and buy something sharp to show him you aren't completely dead inside yet.\n",
            delay=0.02)

        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "[PAY 12500 CZK, + 2 AFFECTION POINTS] ORIGINAL FIT MASH POLO SHIRT + TOBACCO HONEY GUERLAIN EDP, he has no idea what is coming..."),
            ("2", Interaction.get_difficulty_tag(), "[PAY 2500 CZK] GET A NEW CUT AND BUY NEW COOL SHIRT"),
            ("3", Interaction.get_difficulty_tag(), "[FREE] GO AS IS. Sweatpants and a hoodie. You don't have energy to pretend.")
        ])

        if choice == "1":
            if stats.try_spend_money(12500):
                self.martin_meeting_affection_points += 2
                self._slow_print(
                    "\nYou look at yourself in the mirror and question whether you actually really work at Police or Prada.",
                    delay=0.03)
                time.sleep(1)
                self._slow_print("'Impressive. Very nice.'", delay=0.02)
                time.sleep(1)
                self._slow_print("'Let's see Martin's style.'", delay=0.02)
                Interaction.show_outcome("- 12500 CZK, + 2 AFFECTION POINTS (He will love the effort you put into your outfit).")
            else:
                self._slow_print("\nYou check your card balance... declined. Embarrassing.", delay=0.02)
                self._slow_print("You go in your old clothes anyway.", delay=0.02)
        elif choice == "2":
            if stats.try_spend_money(2500):
                self.martin_meeting_affection_points += 1
                self._slow_print(
                    "\nThe barber played his part really well, you also buy a new sharp shirt. You look in the mirror.",
                    delay=0.02)
                self._slow_print("For a second, you don't look like a tired cop. You look like a civilian.", delay=0.02)
                Interaction.show_outcome("- 2500 CZK, +1 AFFECTION POINT (He will appreciate the effort).")
            else:
                self._slow_print("\nYou check your card balance... declined. Embarrassing.", delay=0.02)
                self._slow_print("You go in your old clothes anyway.", delay=0.02)
        elif choice == "3":
            self._slow_print("\nYou splash some cold water on your face. This is who you are right now.", delay=0.02)
            time.sleep(1)
            self._slow_print("If he's really your friend, he won't care about the hoodie.", delay=0.02)
            Interaction.show_outcome("NO CHANGE.")

        self._show_affection_points()
        continue_prompt()

    def _meeting_phase(self, stats: Stats):
        """Phase 2: The Meeting and conversation topic."""
        self._slow_print("You arrive at the restaurant. You see him in the distance.", delay=0.02)
        self._slow_print("It's a shock. He looks... different. Bigger. Buffed.", delay=0.02)
        self._slow_print("His skin has color. He is smiling at the waitress.", delay=0.02)
        self._slow_print(
            "He looks like a totally different person compared to the wreck you remember from the service.", delay=0.02)
        time.sleep(1)
        self._slow_print(
            "\nYou sit down. Your brain is running on cheap caffeine and 2 hours of sleep after a 24hr shift.",
            delay=0.02)
        self._slow_print("He orders a steak. You order a coffee.", delay=0.02)
        self._slow_print("\nBefore the food arrives, you need to break the ice. What do you talk about?", delay=0.02)
        time.sleep(1)

        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "[VENT OUT - 50 PCR HATRED] Complain about the police, the Colonel, and the bureaucracy."),
            ("2", Interaction.get_difficulty_tag(), "[BRAG + 25 CODING SKILLS] Talk about your Python projects and how much you've learned."),
            ("3", Interaction.get_difficulty_tag(), "[LISTEN + 2 AFFECTION POINTS] Let him talk. Ask him how he did it.")
        ])

        if choice == "1":
            stats.increment_stats_pcr_hatred(-50)
            self._slow_print("\nYou unload everything. The broken printers, the bodies, the admin mistakes.",
                             delay=0.02)
            self._slow_print("It feels good to say it to someone who understands.", delay=0.02)
            Interaction.show_outcome("-50 PCR HATRED.")

        elif choice == "2":
            stats.increment_stats_coding_skill(25)
            self._slow_print("\nYou start talking about your projects, classes, and the automation script you wrote.",
                             delay=0.02)
            self._slow_print("You try to sound professional, to show you are ready.", delay=0.02)
            Interaction.show_outcome("+ 25 CODING SKILL.")

        elif choice == "3":
            self.martin_meeting_affection_points += 2
            self._slow_print("\nYou stay quiet. You ask him about his life.", delay=0.02)
            self._slow_print("He talks about his freedom. About sleeping 8 hours a day. About respect.", delay=0.02)
            self._slow_print("He appreciates that you actually listen.", delay=0.02)
            Interaction.show_outcome("+ 2 AFFECTION POINTS.")

        self._show_affection_points()
        continue_prompt()

    def _drop_the_bomb_phase(self, stats: Stats):
        """Phase 3: The realization and interruption."""
        self._slow_print("The food arrives. The smell of steak fills the air, but your stomach is tied in a knot.",
                         delay=0.03)
        self._slow_print("You put down your fork. It's time.", delay=0.02)
        self._slow_print(
            "\n'Bro you know...,' you start, your voice cracking slightly. 'It was really inspiring when you left.'",
            delay=0.02)
        self._slow_print("'I don't really know what to do next, I'm kind of lost, and...'", delay=0.01)
        time.sleep(1)
        self._slow_print("\nHe puts his hand up. He stops you mid-sentence.", delay=0.02)
        self._slow_print("He looks you dead in the eye. The restaurant noise fades away.", delay=0.02)
        continue_prompt()

        self._slow_print("[bold]'Stop lying to yourself, JB.'[/bold]", delay=0.05)
        time.sleep(1.5)
        self._slow_print("[bold]'You know exactly what to do.'[/bold]", delay=0.05)
        time.sleep(1.5)
        self._slow_print("[bold]'You are just too scared to admit it.'[/bold]", delay=0.05)

        continue_prompt()

        self._slow_print("Silence. Absolute silence.", delay=0.05)
        time.sleep(1.0)

        # --- MUSIC SWITCH: THE AWAKENING ---
        self._play_music("martin_meeting_event_the_awakening.mp3")

        self._slow_print("[bold]The truth hits you like a physical blow.[/bold]", delay=0.05)
        self._slow_print("[bold]You look down at the table. You whisper it.[/bold]", delay=0.05)
        time.sleep(0.5)
        self._slow_print("\n[bold red]'You are right...'[/bold red]", delay=0.10)
        time.sleep(0.5)
        self._slow_print("[bold red]'I... I want to quit.'[/bold red]", delay=0.10)

        self._slow_print(
            "\nAs you say those words, the reality of your debt and the Colonel's face flash before your eyes.",
            delay=0.02)
        if stats.pcr_hatred >= 60:
            self._slow_print(
                "\n[red][RELIEF]: - 15 PCR HATRED (It feels so good to say aloud what you already knew).[/red]",
                delay=0.01)
        else:
            stats.increment_stats_pcr_hatred(15)
            self._slow_print("\n[red][CRITICAL EFFECT]: + 15 PCR HATRED (The Fear of leaving is now real).[/red]",
                             delay=0.01)

        self._slow_print(f"\nYour current hatred is: {stats.pcr_hatred}.", delay=0.01)
        self._show_affection_points()
        continue_prompt()

    def _coding_reality_check(self, stats: Stats):
        """Phase 4: The Skill Check based on coding experience."""
        self._slow_print("Martin leans back. 'Okay. You said it. Now, can you actually do it?'", delay=0.02)
        self._slow_print("'Do you have the skills? If you leave tomorrow, can you feed yourself?'", delay=0.02)

        self._show_reality_check(f"Current Coding Experience: {stats.coding_skill}")
        continue_prompt()

        if stats.coding_skill >= 200:
            self.martin_meeting_affection_points += 2
            stats.increment_stats_pcr_hatred(- 20)
            self._slow_print("You smile. You don't just know syntax. You dream in code.", delay=0.02)
            self._slow_print("You are a God Tier developer trapped in a uniform.", delay=0.02)
            self._slow_print("'I am ready,' you say. And you mean it.", delay=0.02)
            Interaction.show_outcome("+ 2 AFFECTION POINTS, - 20 PCR HATRED (Confidence).")

        elif stats.coding_skill >= 150:
            self.martin_meeting_affection_points += 1
            stats.increment_stats_pcr_hatred(- 10)
            self._slow_print("You are solid. You can build apps. You understand the backend.", delay=0.02)
            self._slow_print("You aren't a genius, but you are hireable. Today.", delay=0.02)
            self._slow_print("'I can do this,' you nod.", delay=0.02)
            Interaction.show_outcome("+ 1 AFFECTION POINT, - 10 PCR HATRED.")

        elif stats.coding_skill >= 100:
            self._slow_print(
                "You are a Junior. You know enough to get into trouble, maybe enough to get an internship.", delay=0.02)
            self._slow_print("It's going to be hard. But not impossible.", delay=0.02)
            self._slow_print("'I think I have a shot,' you say, hesitating slightly.", delay=0.02)
            Interaction.show_outcome("NEUTRAL. (It's not great, not terrible).")

        elif stats.coding_skill >= 50:
            self.martin_meeting_affection_points -= 1
            stats.increment_stats_pcr_hatred(10)
            self._slow_print("You know the basics. Loops, functions, some libraries.", delay=0.02)
            self._slow_print("But a job? Real software? You are miles away.", delay=0.02)
            self._slow_print("You look away. 'I... I'm still learning.'", delay=0.02)
            Interaction.show_outcome("- 1 AFFECTION POINT, - 10 PCR HATRED (Doubt creeps in).")

        else:
            self.martin_meeting_affection_points -= 2
            stats.increment_stats_pcr_hatred(20)
            self._slow_print("You have nothing. You spent your time drinking beer instead of studying.", delay=0.02)
            self._slow_print("You are just a cop with a dream and zero skills.", delay=0.02)
            self._slow_print("Martin sees it. He sighs. It's a sigh of pity.", delay=0.02)
            self._slow_print("'Jesus, JB. You have nothing prepared, do you?'", delay=0.02)
            Interaction.show_outcome("- 2 AFFECTION POINTS, + 20 PCR HATRED (Shame).")

        self._show_affection_points()
        continue_prompt()

    def _financial_reality_check(self, stats: Stats):
        """Phase 5: Money Check. Can you afford the exit fee?"""
        self._slow_print("Your friend takes a sip of his drink. 'Skills are one thing. But freedom isn't free.'",
                         delay=0.02)
        self._slow_print("'They are going to make you pay for your uniform, your training, every single koruna.'",
                         delay=0.02)
        self._slow_print("'Do you have the cash? Or are you going to be in debt the moment you walk out?'", delay=0.02)

        self._show_reality_check(f"Current Savings: {stats.available_money} CZK")
        continue_prompt()

        if stats.available_money >= 200000:
            self.martin_meeting_affection_points += 2
            self._slow_print("You nod confidently. You have been saving aggressively.", delay=0.02)
            self._slow_print("You have a war chest. You can buy your freedom twice over.", delay=0.02)
            self._slow_print("Martin looks impressed. 'Smart man.'", delay=0.02)
            Interaction.show_outcome("+ 2 AFFECTION POINTS (Financial Freedom).")

        elif stats.available_money >= 150000:
            self.martin_meeting_affection_points += 1
            self._slow_print("You have enough. It will hurt, but you won't starve.", delay=0.02)
            self._slow_print("You can pay the exit fee and still have a buffer for a few months.", delay=0.02)
            self._slow_print("'I'm covered,' you say.", delay=0.02)
            Interaction.show_outcome("+ 1 AFFECTION POINT (Secure).")

        elif stats.available_money >= 100000:
            self._slow_print("You do the math in your head. It's going to be extremely tight.", delay=0.02)
            self._slow_print("If you pay them off, you'll be eating instant noodles for weeks.", delay=0.02)
            self._slow_print("'I can scrape it together,' you admit.", delay=0.02)
            Interaction.show_outcome("NEUTRAL (Survival Mode).")

        elif stats.available_money >= 50000:
            self.martin_meeting_affection_points -= 1
            self._slow_print("You sweat a little. You don't have enough for the full fee.", delay=0.02)
            self._slow_print("You'll need a loan, or help from parents. It's messy.", delay=0.02)
            self._slow_print("Martin shakes his head. 'That's dangerous ground, JB.'", delay=0.02)
            Interaction.show_outcome("- 1 AFFECTION POINT (Financial Risk).")

        else:
            self.martin_meeting_affection_points -= 2
            self._slow_print("You are broke. You have nothing.", delay=0.02)
            self._slow_print("If you quit, you will be in immediate debt with no income.", delay=0.02)
            self._slow_print("You are trapped.", delay=0.02)
            self._slow_print("Martin looks at you like you are a child. 'So you want to quit but you can't afford it?'",
                             delay=0.02)
            Interaction.show_outcome("- 2 AFFECTION POINTS (Total Disaster).")

        self._show_affection_points()
        continue_prompt()

    def _hatred_motivation_check(self, stats: Stats):
        """Phase 6: The Motivation. How much do you hate the system?"""
        self._slow_print("Martin finishes his steak. He wipes his mouth.", delay=0.02)
        self._slow_print("'One last thing. The system. The Colonel. The meaningless orders.'", delay=0.02)
        self._slow_print("'What do you really feel about them? Is this just burnout, or is it personal?'", delay=0.02)
        self._show_reality_check(f"Current PCR HATRED: {stats.pcr_hatred}/100")

        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "[PURE RAGE] 'I hate them. I want to watch the station burn.'"),
            ("2", Interaction.get_difficulty_tag(), "[HATRED] 'I'm done. I despise what I've become here.'"),
            ("3", Interaction.get_difficulty_tag(), "[NEUTRAL] 'It's just a job. It didn't work out.'"),
            ("4", Interaction.get_difficulty_tag(), "[SOFT] 'I don't have hard feelings. Maybe it's me who is the problem.'"),
            ("5", Interaction.get_difficulty_tag(), "[COPING] 'Actually, the police is vital for society! The Colonel is just misunderstood!'")
        ])

        if choice == "1":
            stats.increment_stats_pcr_hatred(25)
            self.martin_meeting_affection_points += 2
            self._slow_print("\nYour eyes flash with anger. You practically spit the words out.", delay=0.02)
            self._slow_print("'I hate them so much it hurts. Every second in that uniform is torture.'", delay=0.02)
            self._slow_print("Martin smiles. A genuine, shark-like smile. 'Good. Use that anger.'", delay=0.02)
            Interaction.show_outcome("+ 2 AFFECTION POINTS, + 25 PCR HATRED (Fuel for the fire).")

        elif choice == "2":
            stats.increment_stats_pcr_hatred(10)
            self.martin_meeting_affection_points += 1
            self._slow_print("\nYou sigh. 'I hate it. I hate the politics, the lies. I need out.'", delay=0.02)
            self._slow_print("He nods. 'That's the spirit.'", delay=0.02)
            Interaction.show_outcome("+ 1 AFFECTION POINT, - 10 PCR HATRED.")

        elif choice == "3":
            self._slow_print("\nYou shrug. 'It's business. We just aren't a good fit.'", delay=0.02)
            self._slow_print("Your friend looks bored. 'Diplomatic answer. Boring, but safe.'", delay=0.02)
            Interaction.show_outcome("NEUTRAL.")

        elif choice == "4":
            stats.increment_stats_pcr_hatred(- 25)
            self.martin_meeting_affection_points -= 1
            self._slow_print("\n'They gave me a chance. Maybe I'm just weak.'", delay=0.02)
            self._slow_print(
                "Martin stares at you for a moment and then responds: 'Don't do that. Don't blame yourself for their toxicity.'",
                delay=0.02)
            Interaction.show_outcome("- 1 AFFECTION POINT, - 25 PCR HATRED.")

        elif choice == "5":
            stats.increment_stats_pcr_hatred(- 50)
            self.martin_meeting_affection_points -= 2
            self._slow_print("\nYou start rambling.", delay=0.02)
            self._slow_print(
                "'I mean, the job is stable and hierarchy is important and also that pension after 15 years of service is really good!'",
                delay=0.02)
            self._slow_print("You sound like a brainwashed cadet in training.", delay=0.02)
            self._slow_print("He just stares at you in utter disbelief. The cringe has filled the air completely.",
                             delay=0.02)
            self._slow_print("'Wow. Stockholm Syndrome much? What happened to you dude?'", delay=0.02)
            Interaction.show_outcome("- 2 AFFECTION POINTS, - 50 PCR HATRED (Your mental gymnastics are just insane).")

        self._show_affection_points()
        continue_prompt()

    def _timing_decision_phase(self, stats: Stats):
        """Phase 7: The Decision. When do you face the Final Boss?"""
        self._slow_print("Martin's expression darkens. The nostalgia is gone.", delay=0.02)
        time.sleep(1)
        self._slow_print("\n'One last thing, JB. [bold]The Colonel.[/bold]'", delay=0.02)
        time.sleep(1.0)

        self._slow_print("'I know you think he is just a bureaucrat. But don't underestimate him.'", delay=0.02)
        self._slow_print("'He is the one who hired you, remember? He personally admitted you to the academy.'",
                         delay=0.02)
        time.sleep(1.0)

        self._slow_print("'He sees you as his project. His success story. His [bold]'Good Soldier'[/bold].'",
                         delay=0.02)
        time.sleep(0.5)

        self._slow_print("\n'When you hand him that resignation... he won't see it as paperwork.'", delay=0.02)
        time.sleep(0.5)
        self._slow_print("[bold red]'He will take it as a betrayal.'[/bold red]", delay=0.05)
        time.sleep(1.5)

        self._slow_print(f"\n'He will come at you with everything. Guilt, threats, regulations, maybe even empathy.'",
                         delay=0.02)
        self._slow_print(f"'It won't be an easy fight. It might be the hardest thing you've ever done.'", delay=0.02)

        self._slow_print("\nHe looks at you intently.", delay=0.02)
        time.sleep(1.0)
        self._slow_print("[bold]'Are you ready to face him? Do you want to rip the band-aid off now?'[/bold]",
                         delay=0.02)
        self._slow_print("'Or do you need time to prepare your mind and your wallet?'", delay=0.02)

        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "[BRAVE] 'I'm doing it tomorrow. I want it over with.' (Trigger Event Day 25, GAIN AFFECTION POINT)"),
            ("2", Interaction.get_difficulty_tag(), "[REASONABLE] 'I need more time. I'll wait until the last moment.' (Trigger Event Day 30, NEUTRAL)")
        ])

        if choice == "1":
            self.martin_meeting_affection_points += 2
            # Add dynamic attribute to stats for Game class to read later
            stats.colonel_day = 25
            self._slow_print("\nYou clench your fist. 'Tomorrow. I'm not waiting.'", delay=0.02)
            self._slow_print(
                "He simply nods, impressed. 'Good. Strike while the iron is hot. Don't let the fear settle.'",
                delay=0.02)
            Interaction.show_outcome("+ 2 AFFECTION POINTS, FINAL BOSS SET FOR DAY 25.")

        elif choice == "2":
            stats.colonel_day = 30
            self._slow_print(
                "\nYou take a deep breath. 'I need to be sure. I'll wait... I have to do it till the end of this month.'",
                delay=0.02)
            self._slow_print("Your friend understands as he nods. 'Smart. Don't rush into a war you aren't ready for.'",
                             delay=0.02)
            self._slow_print("'Use the time wisely. Save money. Code. Prepare.'", delay=0.02)
            Interaction.show_outcome("FINAL BOSS SET FOR DAY 30.")

        formatted_text = f"[bright_white]YOUR FINAL AFFECTION SCORE IS[/bright_white]: [{self.martin_meeting_affection_points}/12] POINTS."
        print(Panel(
            formatted_text,
            border_style="bold color(129)",
            title="[bold white on color(129)] > FINAL SCORE < [/]",
            padding=(1, 2),
            expand=False
        ))
        continue_prompt()

    def _ending_phase(self, stats: Stats):
        """
        Phase 8: The Parting Gift.
        Based on Affection points, determines what 'Weapon' or 'Status' you take to the final boss.
        """
        self._slow_print("\nThe lunch is over. You pay the bill.", delay=0.02)
        self._slow_print("You walk out into the cold street. The wind hits your face.", delay=0.02)

        if self.martin_meeting_affection_points >= 8:
            self._slow_print("\n[bold]Martin stops you before you leave.[/bold]", delay=0.02)
            self._slow_print("'Wait, JB. I have a good feeling about this. You are actually ready.'", delay=0.02)
            self._slow_print("'I want to help you. I can't fight him for you, but I can give you an edge.'", delay=0.02)
            self._slow_print("'What do you need the most? Information? Security? Or a weapon?'", delay=0.02)

            self._good_ending_selection(stats)

        elif self.martin_meeting_affection_points >= 5:
            self._slow_print("\nYour friend shakes your hand. His grip is firm.", delay=0.02)
            self._slow_print("'It's going to be hell, JB. He will try to break you.'", delay=0.02)
            self._slow_print("'But if you get overwhelmed, just remember that I made it.'", delay=0.02)
            self._slow_print("'I'm waiting on the other side. Don't let him win.'", delay=0.02)

            stats.final_boss_buff = "STOIC_ANCHOR"
            self._slow_print("\n[bold green][STATUS ACQUIRED]: STOIC ANCHOR[/bold green]", delay=0.04)
            self._slow_print("([bold green]Passive:[/bold green] You are more resistant to Colonel's attacks.)", delay=0.01)

        else:
            self._slow_print("\nMartin looks at you with pity. He doesn't shake your hand.", delay=0.02)
            self._slow_print(
                "'JB, do you remember that one guy from high school,",
                delay=0.02)
            self._slow_print(
                "who always wanted to open a car tuning shop but never did anything about it?'",
                delay=0.02)
            self._slow_print("\n'Well... you kinda remind me of him now - big dreams, but no action at all.'", delay=0.02)
            self._slow_print("'If you go in there like this, he's going to eat you alive.'", delay=0.02)
            self._slow_print("'Good luck kiddo. You are going to need it.'", delay=0.02)

            stats.final_boss_buff = "IMPOSTER_SYNDROME"
            self._slow_print("\n[bold red][STATUS ACQUIRED]: IMPOSTER SYNDROME[/bold red]", delay=0.04)
            self._slow_print("([bold red]Debuff:[/bold red] You start the boss fight with a DEBUFF.)", delay=0.01)

        continue_prompt()

    def _good_ending_selection(self, stats: Stats):
        """The 5-choice menu for the Good Ending."""
        print("\n[green]CHOOSE YOUR FINAL BOSS ADVANTAGE:[/green]")

        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "[THE LEGAL NUKE] Martin gives you a file proving the 80k debt is void via 'Paragraph 4B'. (Effect: Colonel starts - 35 HP. Auto-Counters 'Training Debt' attack for + 15 DMG.)"),
            ("2", Interaction.get_difficulty_tag(), "[GHOST OF THE PAST] Martin reveals Colonel's big secret, that only a handful of people do know. (Effect: Immune to Round 1 Fear. Unlocks - 40 HP FATAL STRIKE on 'Car Incident'.)"),
            ("3", Interaction.get_difficulty_tag(), "[PRODUCTION READY SHIELD] Martin vouches for you and writes a salary figure on a napkin. (Effect: Immune to Round 1 Fear. Auto-Wins 'Blacklist' (- 30 HP) & 'Motivation' (- 20 HP).)"),
            ("4", Interaction.get_difficulty_tag(), "[STOIC REFACTOR] Martin teaches you the 'Grey Rock' method to emotionally debug the Colonel. (Effect: Immune to Round 1 Fear (- 10 HP saved). No other effects in current version.)"),
            ("5", Interaction.get_difficulty_tag(), "[AGGRESSIVE OPENING] Martin hypes you up to take the initiative and strike first. (Effect: Colonel starts - 20 HP. Immune to Round 1 Fear.)")
        ])

        if choice == "1":
            self._slow_print("\nMartin hands you a crumpled digital file printout.", delay=0.02)
            self._slow_print("'He lies about the contract. Quote this paragraph. Watch him choke.'", delay=0.02)
            stats.final_boss_buff = "LEGAL_NUKE"

        elif choice == "2":
            self._slow_print("\nMartin leans in and whispers the Colonel's dirty secret.", delay=0.02)
            self._slow_print("You smile. Suddenly, the Colonel doesn't look like a monster. He looks like a failure.",
                             delay=0.02)
            stats.final_boss_buff = "GHOST_SECRET"

        elif choice == "3":
            self._slow_print("\nMartin makes a call. He hands you a napkin with a number on it.", delay=0.02)
            self._slow_print("'That's your starting salary. He can't threaten a man who has options.'", delay=0.02)
            stats.final_boss_buff = "JOB_OFFER"

        elif choice == "4":
            self._slow_print("\nMartin grabs your shoulders. He teaches you to breathe. To detach.", delay=0.02)
            self._slow_print("'He is just broken code, JB. Don't get angry. Just debug him.'", delay=0.02)
            stats.final_boss_buff = "STOIC_HEAL"

        elif choice == "5":
            self._slow_print("\nMartin slaps your back hard. The adrenaline hits.", delay=0.02)
            self._slow_print("'Don't let him speak. Throw the badge on the table. Be the alpha.'", delay=0.02)
            stats.final_boss_buff = "FIRST_STRIKE"

        print("\n[green][bold][ACE IN THE HOLE ACQUIRED][/green][/bold]")
