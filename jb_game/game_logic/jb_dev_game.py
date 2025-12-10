"""Module for starting message and especially for selecting the difficulty level, gaming mechanics, checks and limits."""
from random import randint

from jb_game.game_logic.jb_dev_stats import JBStats
from jb_game.game_logic.jb_dev_day_cycle import DayCycle
from jb_game.game_logic.jb_dev_decision import Decision
from jb_game.game_logic.jb_dev_random_events import RandomEvents


class Game:
    """Sets the basic gaming mechanics, rules, win/loose conditions, difficulty levels."""

    DIFFICULTY_SETTINGS = {
        "1": {"name": "EASY", "money": 85000, "coding": 10, "hatred": 10},
        "2": {"name": "MEDIUM", "money": 65000, "coding": 5, "hatred": 15},
        "3": {"name": "HARD", "money": 35000, "coding": 0, "hatred": 25},
        "4": {"name": "INSANE", "money": 20000, "coding": 0, "hatred": 50},
        # 5 NIGHTMARE difficulty placeholder
    }

    def __init__(self, stats: JBStats, day_cycle: DayCycle, events_list: RandomEvents):
        """Initialise self based on JB Stats class."""
        self.stats = stats
        self.day_cycle = day_cycle
        self.events_list = events_list
        self.selected_difficulty = None
        self.activity_selected = False
        self.python_bootcamp = False
        self.car_incident_stress = True

    def set_difficulty_level(self):
        """Lets user choose what difficulty level he wants using the dictionary."""
        while True:
            print("\nPlease, select the game's difficulty:")

            for key, setting in self.DIFFICULTY_SETTINGS.items():
                print(
                    f"{key}. {setting['name']} - {setting['money']},- CZK, Coding Skills {setting['coding']}, PCR Hatred {setting['hatred']}")

            print("\n(Enter a number from the list above): ")

            # SELECTION LOGIC:
            choice = input("> ").strip()

            if choice in self.DIFFICULTY_SETTINGS:
                settings = self.DIFFICULTY_SETTINGS[choice]

                # Double check with the user
                confirm_select = input(f"\nYou selected '{settings['name']}', is that correct? (y/n): ")
                if confirm_select.lower() != "y":
                    continue

                # Apply the settings
                print(f"\n{settings['name']} mode selected.")
                self.selected_difficulty = settings['name'].lower()
                self.stats.available_money = settings['money']
                self.stats.coding_experience = settings['coding']
                self.stats.pcr_hatred = settings['hatred']

                # Show the stats and exit loop
                self.stats.get_stats_command()
                input("\n(PRESS ANY KEY TO CONTINUE.)")
                break
            else:
                print("\nWrong input, try again.")

    def main_menu(self):
        """Basic UI, containing selectable options."""
        while True:
            print(
                "\nMAIN MENU:"
                "\n1.SHOW STATS"
                "\n2.SELECT ACTIVITY"
                "\n3.SHOW CONTACTS"
                "\n4.END THE DAY."
                "\nSELECT YOUR OPTION (1-4): "
            )

            # REFACTOR: One line decision
            choice = Decision.ask(("1", "2", "3", "4"))

            if choice == "1":
                print(f"\nCurrent day: #{self.day_cycle.current_day}/30.")
                self.stats.get_stats_command()

            elif choice == "2":
                self.select_activity()

            elif choice == "3":
                print(
                    "\nYou open up your phone list, to see following contacts(DOESNT WORK IN THIS VERSION):"
                    "\n1.MM"
                    "\n2.MK"
                    "\n3.PS"
                    "\n4.PAUL GOODMAN"
                    "\n5.COLONEL"
                    "\n6.RETURN TO MENU"
                    "\nSELECT YOUR OPTION (1-6): "
                )  # later: self.show_contacts()

            elif choice == "4":
                # LOGIC: If activity not done, ask for confirmation
                if not self.activity_selected:
                    print("\nYou haven't selected your daily activity.")
                    confirm = input("Are you sure you want to end the day? (y/n): ").strip().lower()

                    if confirm != "y":
                        continue  # <--- This jumps back to the main menu loop safely!

                # End of Day Logic
                print(f"\nEnding day #{self.day_cycle.current_day}...")
                self.day_cycle.next_day()

                # Random Event Trigger (Every 3 days)
                if self.day_cycle.current_day % 3 == 0:
                    print(f"\nStarting day #{self.day_cycle.current_day}/30")
                    self.events_list.select_random_event(self.stats)
                    # Note: You might not need next_day() again here unless events consume a day
                else:
                    print(f"\nStarting day #{self.day_cycle.current_day}/30")

                # Reset Daily Flags
                self.activity_selected = False

                # Apply Daily Effects
                self.stats.increment_stats_pcr_hatred(5)
                if self.python_bootcamp:
                    self.stats.increment_stats_coding_skill(5)


    def select_activity(self):
        """Lets you select a daily activity once per day, through the game's menu."""
        if not self.activity_selected:
            print(
                "\nYou think about what activity to do today (You can select only one per day):"
                "\n1.GYM"
                "\n2.MEDITATE"
                "\n3.BOUNCER NIGHT SHIFT"
                "\n4.LEARN PYTHON"
                "\n5.RETURN TO MENU"
                "\nSELECT YOUR OPTION (1-5):"
            )

            # REFACTOR: One line decision
            choice = Decision.ask(("1", "2", "3", "4", "5"))

            if choice == "1":
                self.activity_gym()
            elif choice == "2":
                self.activity_meditate()
            elif choice == "3":
                self.activity_bouncer()
            elif choice == "4":
                self.activity_python()
            elif choice == "5":
                self.main_menu()

        else:
            print("\nYou've already done your daily activity today!")

    def activity_gym(self):
        """Daily activity accessible from menu, allows you to go to gym and lowers PCR Hatred, costs money."""
        print("\nYou've selected to go to the gym with your trainer."
              "\nTraining will help you to relax, but it will cost you some money."
              "\n1. [33/33/33%] WE GO GYM!"
              "\n2. RETURN TO MENU"
              "\nSELECT YOUR OPTION (1-2):")

        # REFACTOR: One line decision
        choice = Decision.ask(("1", "2"))

        if choice == "1":
            activity_roll = randint(1, 3)
            if activity_roll == 1:
                self.stats.increment_stats_value_money(-400)
                self.stats.increment_stats_pcr_hatred(-25)
                print("\nDude the pump you had was EPIC, you even hit a new PR!"
                      "\nYou feel strong and unstoppable, this was a great training."
                      "\n[OUTCOME]: -400 CZK, -25 PCR HATRED")
            elif activity_roll == 2:
                self.stats.increment_stats_value_money(-400)
                self.stats.increment_stats_pcr_hatred(-15)
                print("\nYou feel great after this workout, it's awesome that"
                      "\nyou can come to better thoughts in the gym and relax."
                      "\n[OUTCOME]: -400 CZK, -15 PCR HATRED")
            elif activity_roll == 3:
                self.stats.increment_stats_value_money(-400)
                self.stats.increment_stats_pcr_hatred(-10)
                print("\nYou had better trainings in the past, but you still enjoyed this one."
                      "\n[OUTCOME]: -400 CZK, -10 PCR HATRED")
            self.stats.get_stats_command()
            input("\nCONTINUE...")
            self.activity_selected = True
        elif choice == "2":
            self.main_menu()

    def activity_meditate(self):
        """Daily activity accessible from menu, allows you to meditate and lowers PCR Hatred for free."""
        print("\nYou've selected to meditate quietly in your room."
              "\nTraining will help you to reduce stress, and is completely free."
              "\n1. [90/10%] BREATHE IN, BREATHE OUT..."
              "\n2. RETURN TO MENU"
              "\nSELECT YOUR OPTION (1-2):")

        # REFACTOR: One line decision
        choice = Decision.ask(("1", "2"))

        if choice == "1":
            activity_roll = randint(1, 10)
            if activity_roll <= 9:
                self.stats.increment_stats_pcr_hatred(-15)
                print("\nYou feel somewhat calmer after your meditation."
                      "\n[OUTCOME]: -5 PCR HATRED")
            elif activity_roll == 10:
                self.stats.increment_stats_pcr_hatred(-35)
                print("\nThis meditation went really well! "
                      "\nYou felt as if most of the hatred evaporated into thin air."
                      "\n[OUTCOME]: -35 PCR HATRED")
            self.stats.get_stats_command()
            input("\nCONTINUE...")
            self.activity_selected = True
        elif choice == "2":
            self.main_menu()

    def activity_bouncer(self):
        """Daily activity accessible from menu, allows you to work at a nightclub/strip club, multiple outcomes."""
        print("\nYou were offered to work as a bouncer in either a local night club or a strip bar."
              "\nShifts in night club are generally safe, but there is still some risk attached to it."
              "\nDoing a bouncer at a strip bar is VERY RISKY, but the reward is also VERY HIGH."
              "\n1. [70/20/10%] WORK AS A BOUNCER AT A NIGHT CLUB"
              "\n2. [5/20/50/20/5%]WORK AS A BOUNCER AT A STRIP BAR"
              "\n3. RETURN TO MENU"
              "\nSELECT YOUR OPTION (1-3):")

        # REFACTOR: One line decision
        choice = Decision.ask(("1", "2", "3"))

        if choice == "1":
            activity_roll = randint(1, 100)
            if activity_roll <= 70:
                self.stats.increment_stats_pcr_hatred(10)
                self.stats.increment_stats_value_money(4000)
                print("\nNight shift was really calm, nothing happened and you got your usual rate."
                      "\nYou got angrier at PCR today, because the only reason why you work here,"
                      "\nis the salary you get from them."
                      "\n[OUTCOME]: +3.000 CZK, +10 PCR HATRED")
            elif activity_roll <= 90:
                self.stats.increment_stats_value_money(7500)
                self.stats.increment_stats_pcr_hatred(-10)
                print("\nThe night shift was great! You gained extra tip from your boss today."
                      "\nThis made you feel so good, that you even forgot about completely about PCR."
                      "\n[OUTCOME]: +7.500 CZK, -10 PCR HATRED")
            elif activity_roll <= 100:
                self.stats.increment_stats_pcr_hatred(20)
                self.stats.increment_stats_value_money(4000)
                print("\nThere was an incident... some guys fought over one chick at the club, "
                      "\nThe police was called and your colleagues recognised you and made fun of you."
                      "\nYou were the talk of the following days, there will be no disciplinary action "
                      "\ntaken against you, yet this made you completely mad."
                      "\n[OUTCOME]: +4.000 CZK, +20 PCR HATRED!")

            self.stats.get_stats_command()
            input("\nCONTINUE...")
            self.activity_selected = True

        elif choice == "2":
            activity_roll = randint(1, 100)
            if activity_roll <= 5:
                self.stats.increment_stats_value_money(35000)
                self.stats.increment_stats_pcr_hatred(-15)
                print(
                    "\nA famous regular shows up drunk and paranoid. Two guys try to drag him outside, but you"
                    "\nintervene with textbook precision — one hand block, one arm-bar, clean de-escalation."
                    "\nThe CCTV shows you prevented something ugly."
                    "\nAt the end of the night your boss calls you to the office,"
                    "\npraises your calm judgment, and slides an envelope across the table."
                    "\n'Not many can do what you did tonight.'"
                    "\n[OUTCOME]: +25.000 CZK, -15 PCR HATRED"
                )
            elif activity_roll <= 25:
                self.stats.increment_stats_value_money(12500)
                self.stats.increment_stats_coding_skill(2)
                print(
                    "\nSteady crowds, few arguments, no real threats. You handle everything with routine precision."
                    "\nYou even use downtime at the door to mentally rehearse OOP concepts "
                    "\nand class hierarchies — weirdly effective."
                    "\nBoss gives you something extra for showing up, nods at you, no drama.."
                    "\n[OUTCOME]: +12.500 CZK, +2 CODING SKILLS"
                )

            elif activity_roll <= 75:
                self.stats.increment_stats_value_money(6500)
                self.stats.increment_stats_pcr_hatred(5)
                print(
                    "\nStandard calm shift, where nothing of great importance happens."
                    "\nYou find this shift pretty boring today."
                    "\nYou keep on wondering, how long it's going to take you to actually start coding."
                    "\nand doing something more meaningful then standing an entire night at a door."
                    "\nAt-least - the money they pay here is really something else."
                    "\n[OUTCOME]: +4.500 CZK, +5 PCR HATRED"
                )


            elif activity_roll <= 95:
                self.stats.increment_stats_value_money(1000)
                self.stats.increment_stats_pcr_hatred(25)
                print(
                    "\nA fight breaks out inside. "
                    "\nYou break it up, but one participant recognizes your face from the force. "
                    "\n“Ty vole, to je POLDA!”"
                    "\nWhen the responding patrol arrives, the looks they give you are suffocating. "
                    "\nTwo colleagues whisper. One smirks."
                    "\nYour boss isn’t thrilled about the chaos either and gives you only a partial payout."
                    "\n[OUTCOME]: +1.000CZK, +25 PCR HATRED"
                )

            elif activity_roll <= 100:
                self.stats.increment_stats_value_money(-12500)
                self.stats.increment_stats_pcr_hatred(35)
                self.stats.increment_stats_coding_skill(-5)
                print(
                    "\nYou turn your back for one second — enough for a coked-up idiot"
                    "\nto drive a vodka bottle into your skull."
                    "\nSecurity drags him out, but you’re bleeding, dizzy, and confused."
                    "\nPolice arrives, and when they run your ID, the truth spills: "
                    "\nyou’re a full-time officer moonlighting illegally."
                    "\nYour boss is furious. You get fined by your colleagues."
                    "\nYou stagger home with a headache powerful enough to knock your IQ back several points."
                    "\n[OUTCOME]: -12.500 CZK, +35 PCR HATRED, -5 CODING SKILLS"
                )

            self.stats.get_stats_command()
            input("\nCONTINUE...")
            self.activity_selected = True


        elif choice == "3":
            self.main_menu()

    def activity_python(self):
        """Daily activity accessible from menu, allows you to code and gain coding experience."""
        print("\nThere are multiple ways for you how to study Python."
              "\nPython is now your Dojo, coding is your life, you need to master coding, there is no other way!"
              "\nYou can learn on your own, or pay a tutor."
              "\nStudying on your own is free, but less effective."
              "\nPaying a tutor is costly but highly effective."
              "\n1. [FREE - 80/20%] STUDY ON YOUR OWN"
              "\n2. [2.500CZK - 65/25/10%] BUY A STUDY SESSION ON FIVERR"
              "\n3. [50.000CZK] JOIN AN ON-LINE BOOTCAMP (GAIN BUFF FOR THE REST OF THE GAME)"
              "\n4. RETURN TO MENU"
              "\nSELECT YOUR OPTION (1-4):")

        # REFACTOR: One line decision
        choice = Decision.ask(("1", "2", "3", "4"))

        # 1) FREE STUDY – 80% +5, 20% +10
        if choice == "1":
            activity_roll = randint(1, 100)
            if activity_roll <= 80:
                self.stats.increment_stats_coding_skill(5)
                print(
                    "\nYou sit at your cheap desk with a cup of instant coffee and a worn-out Python book."
                    "\nNo guidance, no mentor, just you and the code."
                    "\nYou grind through a couple of chapters, debug a few silly mistakes and slowly connect concepts."
                    "\nIt's not glamorous, but it works."
                    "\n[OUTCOME]: +5 CODING SKILLS"
                )
            elif activity_roll <= 100:
                self.stats.increment_stats_coding_skill(10)
                print(
                    "\nYou decide to go full monk mode: phone on airplane mode, browser closed, notebook open."
                    "\nYou re-write examples by hand, experiment with your own functions"
                    "\nand finally understand something that confused you for days."
                    "\nThe dopamine hit from that 'I GET IT' moment is unreal."
                    "\n[OUTCOME]: +10 CODING SKILLS"
                )

            self.stats.get_stats_command()
            input("\nCONTINUE...")
            self.activity_selected = True

        # 2) PAID TUTOR – 60% +10, 30% +15, 10% +25
        elif choice == "2":
            # Pay for the session
            self.stats.increment_stats_value_money(-1500)
            activity_roll = randint(1, 100)

            if activity_roll <= 65:
                self.stats.increment_stats_coding_skill(10)
                print(
                    "\nYou jump on a call with a mid-level developer from Fiverr."
                    "\nHe’s not a genius, but he is practical. He shows you how to structure your files,"
                    "\nexplains why your functions are a mess, and fixes a few key bad habits."
                    "\nYou leave the session with clearer thinking and a to-do list."
                    "\n[OUTCOME]: -2.500 CZK, +10 CODING SKILLS"
                )
            elif activity_roll <= 90:
                self.stats.increment_stats_coding_skill(15)
                print(
                    "\nYou luck out. Your tutor is actually sharp as hell."
                    "\nThey share their screen, walk you through refactoring, and explain OOP in a way "
                    "\nthat finally clicks with your brain."
                    "\nYou end the session tired but energized, with a feeling that you’ve leveled up."
                    "\n[OUTCOME]: -2.500 CZK, +15 CODING SKILLS"
                )
            elif activity_roll <= 100:
                self.stats.increment_stats_coding_skill(25)
                print(
                    "\nYou accidentally booked a beast. Senior dev, ten years in the field."
                    "\nHe doesn’t waste a second: code review, patterns, mental models, how to think like an engineer."
                    "\nYou fill pages of notes, your brain is fried, but something inside you has shifted."
                    "\nThis wasn’t just tutoring – this was a paradigm shift."
                    "\n[OUTCOME]: -2.500 CZK, +25 CODING SKILLS"
                )

            self.stats.get_stats_command()
            input("\nCONTINUE...")
            self.activity_selected = True

        # 3) ONLINE BOOTCAMP – PLACEHOLDER FOR PERMANENT BUFF
        elif choice == "3":
            self.stats.increment_stats_value_money(-50000)
            print(
                "\nYou sign a contract and pay for an on-line Python bootcamp."
                "\nDeadlines, assignments, code reviews, community, mentors – the full package."
                "\nFrom now on, every single day in this game, your coding skills will grow if you keep showing up."
                "\nThis is no longer a hobby. This is a commitment."
                "\n[OUTCOME]: -50.000 CZK, [BOOTCAMP BUFF ACTIVATED +5 CODING SKILL EVERYDAY]"
            )

            self.python_bootcamp = True

            self.stats.get_stats_command()
            input("\nCONTINUE...")
            self.activity_selected = True

        # 4) RETURN TO MAIN MENU
        elif choice == "4":
            self.main_menu()

        else:
            print("\nYou already did your daily activity today.")