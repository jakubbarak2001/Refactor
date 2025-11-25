"""Module for starting message and especially for selecting the difficulty level, gaming mechanics, checks and limits."""
from random import randint

from jb_dev_stats import JBStats
from jb_dev_day_cycle import DayCycle
from jb_dev_decision import Decision
from jb_dev_random_events import RandomEvents


class Game:
    """Sets the basic gaming mechanics, rules, win/loose conditions, difficulty levels."""

    def __init__(self, stats:
    JBStats, day_cycle: DayCycle, events_list: RandomEvents):
        """Initialise self based on JB Stats class."""
        self.stats = stats
        self.day_cycle = day_cycle
        self.events_list = events_list
        self.selected_difficulty = None
        self.activity_selected = False
        self.python_bootcamp = False
        self.car_incident_stress = True


    def set_difficulty_level(self):
        """Lets user choose what difficulty level he wants."""
        while True:
            select_game_difficulty = input("\nPlease, select the game's difficulty"
                                           "\n1. Easy - 85.000,- CZK, Coding Skills 10, PCR Hatred 10"
                                           "\n2. Medium - 65.000,- CZK, Coding Skills 5, PCR Hatred 15"
                                           "\n3. Hard - 35.000,- CZK, Coding Skills 0, PCR Hatred 25"
                                           "\n4. Insane - 20.000,- CZK, Coding SKills 0, PCR Hatred 50"
                                           "\n5. NIGHTMARE - (DOESN'T WORK YET)"
                                           "\n\n(Enter any number from 1-4): ")
            if select_game_difficulty == "1":
                confirm_select = input("\nYou selected 'EASY', is that correct? (y/n): ")
                if confirm_select != "y":
                    self.selected_difficulty = 'easy'
                    continue
                else:
                    print("\nEASY mode selected: - 85.000,- CZK, Coding Skills 10, PCR Hatred 10.")
                    self.stats.available_money = 85000
                    self.stats.coding_experience = 10
                    self.stats.pcr_hatred = 10
            elif select_game_difficulty == "2":
                confirm_select = input("\nYou selected 'MEDIUM', is that correct? (y/n): ")
                if confirm_select != "y":
                    self.selected_difficulty = 'medium'
                    continue
                else:
                    print("\nMEDIUM mode selected: - 65.000,- CZK, Coding Skills 5, PCR Hatred 15.")
                    self.stats.available_money = 65000
                    self.stats.coding_experience = 5
                    self.stats.pcr_hatred = 15
            elif select_game_difficulty == "3":
                confirm_select = input("\nYou selected 'HARD', is that correct? (y/n): ")
                if confirm_select != "y":
                    self.selected_difficulty = 'hard'
                    continue
                else:
                    print("\nHARD mode selected: - 35.000,- CZK, Coding Skills 0, PCR Hatred 25.")
                    self.stats.available_money = 35000
                    self.stats.coding_experience = 0
                    self.stats.pcr_hatred = 25
            elif select_game_difficulty == "4":
                confirm_select = input("\nYou selected 'INSANE', is that correct? (y/n): ")
                if confirm_select != "y":
                    self.selected_difficulty = 'insane'
                    continue
                else:
                    print("\nINSANE mode selected: - 20.000,- CZK, Coding Skills 0, PCR Hatred 50.")
                    self.stats.available_money = 20000
                    self.stats.coding_experience = 0
                    self.stats.pcr_hatred = 50
            else:
                print("\nWrong input, try again.")
                continue
            self.stats.get_stats_command()
            input("\n(PRESS ANY KEY TO CONTINUE.)")
            break

    def main_menu(self):
        """Basic UI, containing selectable options."""
        while True:
            (print
                           ("\nMAIN MENU:"
                            "\n1.SHOW STATS"
                            "\n2.SELECT ACTIVITY"
                            "\n3.SHOW CONTACTS"
                            "\n4.END THE DAY."
                            "\nSELECT YOUR OPTION (1-4): ")
                           )
            menu_select_decision = (
                Decision('', ("1", "2", "3", "4")))
            Decision.create_decision(menu_select_decision)

            if menu_select_decision.decision_variable_name == "1":
                print(f"\nCurrent day: #{self.day_cycle.current_day}/30.")
                self.stats.get_stats_command()

            elif menu_select_decision.decision_variable_name == "2":
                self.select_activity()


            elif menu_select_decision.decision_variable_name == "3":
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

            elif menu_select_decision.decision_variable_name == "4":
                while not self.activity_selected:
                    end_day_with_no_activity = (
                        input("\nYou haven't selected your daily activity, are you sure you want to continue?"
                          "\n(y/n): "))
                    if end_day_with_no_activity == "y":
                        break
                    else:
                        Game.main_menu(self)
                print(f"\nEnding day #{self.day_cycle.current_day}...")
                self.day_cycle.next_day()
                print(f"\nStarting day #{self.day_cycle.current_day}/30")
                if self.day_cycle.current_day % 3 == 0:
                    self.events_list.select_random_event(self.stats)
                    print(f"\nStarting day #{self.day_cycle.current_day}/30")
                    self.day_cycle.next_day()
                self.activity_selected = False
                self.stats.increment_stats_pcr_hatred(+5)
                if self.python_bootcamp:
                    self.stats.increment_stats_coding_skill(+5)

            else:
                print("Wrong input, try again.")

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
            menu_select_decision_activity = (
                Decision('', ("1", "2", "3", "4", "5")))
            Decision.create_decision(menu_select_decision_activity)

            choice = menu_select_decision_activity.decision_variable_name

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
        activity_is_selected = (
            Decision('', ("1", "2")))
        Decision.create_decision(activity_is_selected)

        if activity_is_selected.decision_variable_name == "1":
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
        elif activity_is_selected.decision_variable_name == "2":
            self.main_menu()

    def activity_meditate(self):
        """Daily activity accessible from menu, allows you to meditate and lowers PCR Hatred for free."""
        print("\nYou've selected to meditate quietly in your room."
              "\nTraining will help you to reduce stress, and is completely free."
              "\n1. [90/10%] BREATHE IN, BREATHE OUT..."
              "\n2. RETURN TO MENU"
              "\nSELECT YOUR OPTION (1-2):")
        activity_is_selected = (
            Decision('', ("1", "2")))
        Decision.create_decision(activity_is_selected)

        if activity_is_selected.decision_variable_name == "1":
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
        elif activity_is_selected.decision_variable_name == "2":
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
        activity_is_selected = (
            Decision('', ("1", "2", "3")))
        Decision.create_decision(activity_is_selected)

        if activity_is_selected.decision_variable_name == "1":
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

        elif activity_is_selected.decision_variable_name == "2":
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


        elif activity_is_selected.decision_variable_name == "3":
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
        activity_is_selected = (
            Decision('', ("1", "2", "3", "4")))
        Decision.create_decision(activity_is_selected)

        # 1) FREE STUDY – 80% +5, 20% +10
        if activity_is_selected.decision_variable_name == "1":
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
        elif activity_is_selected.decision_variable_name == "2":
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
        elif activity_is_selected.decision_variable_name == "3":
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
        elif activity_is_selected.decision_variable_name == "4":
            self.main_menu()

        else:
            print("\nYou already did your daily activity today.")
