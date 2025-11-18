"""Module for starting message and especially for selecting the difficulty level, gaming mechanics, checks and limits."""
from random import randint

from jb_dev_stats import JBStats
from jb_dev_day_cycle import DayCycle
from jb_dev_decision import Decision


class Game:
    """Sets the basic gaming mechanics, rules, win/loose conditions, difficulty levels."""

    def __init__(self, stats:
    JBStats, day_cycle: DayCycle):
        """Initialise self based on JB Stats class."""
        self.stats = stats
        self.day_cycle = day_cycle
        self.activity_selected = False

    def loose_condition(self):
        """Loose condition that runs endlessly in the background."""
        if self.stats.available_money <= 0:
            print(
                "\nYou ran out all of your money...you won't be able to move out or buy study material for becoming "
                "a developer, you are forced to stay in a work you hate FOREVER...GAME OVER.")

        if self.stats.pcr_hatred >= 100:
            print(
                "\nDue to the latest events, your hatred of PCR has grown to the point, that you cannot think "
                "of any other solution...\nOn one of the night shifts, you lock yourself on the toilet at the station."
                "\nFew minutes later, only thing your colleagues hear is the characteristic sound of your gun...GAME OVER."
            )

    @staticmethod
    def start_game_message():
        """Gives a neatly formatted welcoming message, for whenever you start a game."""
        print("\nWelcome to JB - the game! \n\nIn this game, you will be playing as a young and perspective police "
              "officer in northern part of Bohemia, where sun never rises and criminality is growing rapidly. "
              "\nThe game begins in 1.7.2025, at start you love your job, but that is soon to change, due to the "
              "unforeseen consequences. \nSoon, you will realise your path lies elsewhere - in software development. "
              "Your time and resources are limited though and you have to end your job as police officer soon!"
              "\n\nYou will have to balance between 3 main stats: \n1. Money, \n2. Coding skills, \n3. Hatred of Police "
              "\n\nThe most important rule for you is always have more than 0 money and to keep your "
              "hatred of police under 100."
              "\nIn the following section, you will be able to choose your difficulty level, good luck and have fun!")

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
                    continue
                else:
                    print("\nEASY mode selected: - 85.000,- CZK, Coding Skills 10, PCR Hatred 10.")
                    self.stats.available_money = 85000
                    self.stats.coding_experience = 10
                    self.stats.pcr_hatred = 10
            elif select_game_difficulty == "2":
                confirm_select = input("\nYou selected 'MEDIUM', is that correct? (y/n): ")
                if confirm_select != "y":
                    continue
                else:
                    print("\nMEDIUM mode selected: - 65.000,- CZK, Coding Skills 5, PCR Hatred 15.")
                    self.stats.available_money = 65000
                    self.stats.coding_experience = 5
                    self.stats.pcr_hatred = 15
            elif select_game_difficulty == "3":
                confirm_select = input("\nYou selected 'HARD', is that correct? (y/n): ")
                if confirm_select != "y":
                    continue
                else:
                    print("\nHARD mode selected: - 35.000,- CZK, Coding Skills 0, PCR Hatred 25.")
                    self.stats.available_money = 35000
                    self.stats.coding_experience = 0
                    self.stats.pcr_hatred = 25
            elif select_game_difficulty == "4":
                confirm_select = input("\nYou selected 'INSANE', is that correct? (y/n): ")
                if confirm_select != "y":
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
            Decision.create_decision_variable(menu_select_decision)

            if menu_select_decision.decision_variable_name == "1":
                # CALL METHOD ON JBStats INSTANCE
                print(f"\nCurrent day: #{self.day_cycle.current_day}/30.")
                self.stats.get_stats_command()

            elif menu_select_decision.decision_variable_name == "2":
                self.select_activity()


            elif menu_select_decision.decision_variable_name == "3":
                print(
                    "\nYou open up your phone list, to see following contacts:"
                    "\n1.MM"
                    "\n2.MK"
                    "\n3.PS"
                    "\n4.PAUL GOODMAN"
                    "\n5.COLONEL"
                    "\n6.RETURN TO MENU"
                    "\nSELECT YOUR OPTION (1-6): "
                )  # later: self.show_contacts()

            elif menu_select_decision.decision_variable_name == "4":
                # CALL METHOD ON DayCycle INSTANCE
                print(f"\nEnding day #{self.day_cycle.current_day}...")
                self.day_cycle.next_day()
                print(f"\nStarting day #{self.day_cycle.current_day}/30")
                self.activity_selected = False
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
            Decision.create_decision_variable(menu_select_decision_activity)

            #GYM

            if menu_select_decision_activity.decision_variable_name == "1":
                print("\nYou've selected to go to the gym with your trainer."
                      "\nTraining will help you to relax, but it will cost you some money."
                      "\n1. [33/33/33%] WE GO GYM!"
                      "\n2. RETURN TO MENU"
                      "\nSELECT YOUR OPTION (1-2):")
                menu_select_decision_activity_bouncer = (
                    Decision('', ("1", "2")))
                Decision.create_decision_variable(menu_select_decision_activity_bouncer)

                if menu_select_decision_activity_bouncer.decision_variable_name == "1":
                    activity_roll = randint(1, 3)
                    if activity_roll == 1:
                        self.stats.increment_stats_value_money(-400)
                        self.stats.increment_stats_pcr_hatred(-20)
                        print("\nDude the pump you had was EPIC, you even hit a new PR!"
                              "\nYou feel strong and unstoppable, this was a great training."
                              "\n[OUTCOME]: -400 CZK, -20 PCR HATRED")
                    elif activity_roll == 2:
                        self.stats.increment_stats_value_money(-400)
                        self.stats.increment_stats_pcr_hatred(-10)
                        print("\nYou feel great after this workout, it's awesome that"
                              "\nyou can come to better thoughts in the gym and relax."
                              "\n[OUTCOME]: -400 CZK, -10 PCR HATRED")
                    elif activity_roll == 3:
                        self.stats.increment_stats_value_money(-400)
                        self.stats.increment_stats_pcr_hatred(-5)
                        print("\nYou had better trainings in the past, but you still enjoyed this one."
                              "\n[OUTCOME]: -400 CZK, -5 PCR HATRED")
                    self.stats.get_stats_command()
                    input("\nCONTINUE...")
                    self.activity_selected = True
                elif menu_select_decision_activity_bouncer.decision_variable_name == "2":
                    self.main_menu()

            #MEDITATE

            elif menu_select_decision_activity.decision_variable_name == "2":
                print("\nYou've selected to meditate quietly in your room."
                      "\nTraining will help you to reduce stress, and is completely free."
                      "\n1. [90/10%] BREATHE IN, BREATHE OUT..."
                      "\n2. RETURN TO MENU"
                      "\nSELECT YOUR OPTION (1-2):")
                menu_select_decision_activity_bouncer = (
                    Decision('', ("1", "2")))
                Decision.create_decision_variable(menu_select_decision_activity_bouncer)

                if menu_select_decision_activity_bouncer.decision_variable_name == "1":
                    activity_roll = randint(1, 10)
                    if activity_roll <= 9:
                        self.stats.increment_stats_pcr_hatred(-5)
                        print("\nYou feel somewhat calmer after your meditation."
                              "\n[OUTCOME]: -5 PCR HATRED")
                    elif activity_roll == 10:
                        self.stats.increment_stats_pcr_hatred(-30)
                        print("\nThis meditation went really well! "
                              "\nYou felt as if most of the hatred evaporated into thin air."
                              "\n[OUTCOME]: -30 PCR HATRED")
                    self.stats.get_stats_command()
                    input("\nCONTINUE...")
                    self.activity_selected = True
                elif menu_select_decision_activity_bouncer.decision_variable_name == "2":
                    self.main_menu()

            #BOUNCER NIGHT SHIFT

            elif menu_select_decision_activity.decision_variable_name == "3":
                print("\nYou were offered to work as a bouncer in either a local night club or a strip bar."
                      "\nShifts in night club are generally safe, but there is still some risk attached to it."
                      "\nDoing a bouncer at a strip bar is VERY RISKY, but the reward is also VERY HIGH."
                      "\n1. [70/20/10%] WORK AS A BOUNCER AT A NIGHT CLUB"
                      "\n2. [5/20/50/20/5%]WORK AS A BOUNCER AT A STRIP BAR"
                      "\n3. RETURN TO MENU"
                      "\nSELECT YOUR OPTION (1-3):")
                menu_select_decision_activity_bouncer = (
                    Decision('', ("1", "2", "3")))
                Decision.create_decision_variable(menu_select_decision_activity_bouncer)

                #BOUNCER NIGHT CLUB
                if menu_select_decision_activity_bouncer.decision_variable_name == "1":
                    activity_roll = randint(1, 100)
                    if activity_roll <= 70:
                        self.stats.increment_stats_pcr_hatred(5)
                        self.stats.increment_stats_value_money(4000)
                        print("\nNight shift was really calm, nothing happened and you got your usual rate."
                              "\nYou got angrier at PCR today, because the only reason why you work here,"
                              "\nis the salary you get from them."
                              "\n[OUTCOME]: +3.000 CZK, +5 PCR HATRED")
                    elif activity_roll <= 90:
                        self.stats.increment_stats_value_money(7500)
                        self.stats.increment_stats_pcr_hatred(-5)
                        print("\nThe night shift was great! You gained extra tip from your boss today."
                              "\nThis made you feel so good, that you even forgot about the PCR at all."
                              "\n[OUTCOME]: +7.500 CZK, -5 PCR HATRED")
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

                #BOUNCER STRIP BAR
                elif menu_select_decision_activity_bouncer.decision_variable_name == "2":
                    activity_roll = randint(1, 100)
                    if activity_roll <= 5:
                        self.stats.increment_stats_value_money(25000)
                        self.stats.increment_stats_pcr_hatred(-5)
                        print(
                            "\nA famous regular shows up drunk and paranoid. Two guys try to drag him outside, but you"
                            "\nintervene with textbook precision — one hand block, one arm-bar, clean de-escalation."
                            "\nThe CCTV shows you prevented something ugly."
                            "\nAt the end of the night your boss calls you to the office,"
                            "\npraises your calm judgment, and slides an envelope across the table."
                            "\n'Not many can do what you did tonight.'"
                            "\n[OUTCOME]: +25.000 CZK, -5 PCR HATRED"
                        )
                    elif activity_roll <= 25:
                        self.stats.increment_stats_value_money(8500)
                        self.stats.increment_stats_coding_skill(2)
                        print(
                            "\nSteady crowds, few arguments, no real threats. You handle everything with routine precision."
                            "\nYou even use downtime at the door to mentally rehearse OOP concepts "
                            "\nand class hierarchies — weirdly effective."
                            "\nBoss gives you the standard payout, nods at you, no drama.."
                            "\n[OUTCOME]: +8.500 CZK, +2 CODING SKILLS"
                        )

                    elif activity_roll <= 75:
                        self.stats.increment_stats_value_money(6500)
                        print(
                            "\nStandard calm shift, where nothing of great importance happens."
                            "\nYou find this shift pretty boring today."
                            "\nYou keep on wondering, how long it's going to take you to actually start coding."
                            "\nand doing something more meaningful then standing an entire night at a door."
                            "\nAt-least - the money they pay here is really something else."
                            "\n[OUTCOME]: +6.500 CZK"
                        )


                    elif activity_roll <= 95:
                        self.stats.increment_stats_value_money(1000)
                        self.stats.increment_stats_pcr_hatred(15)
                        print(
                            "\nA fight breaks out inside. "
                            "\nYou break it up, but one participant recognizes your face from the force. "
                            "\n“Ty vole, to je polda!”"
                            "\nWhen the responding patrol arrives, the looks they give you are suffocating. "
                            "\nTwo colleagues whisper. One smirks."
                            "\nYour boss isn’t thrilled about the chaos either and gives you only a partial payout."
                            "\n[OUTCOME]: +1.000CZK, +15 PCR HATRED"
                        )

                    elif activity_roll <= 100:
                        self.stats.increment_stats_value_money(-12500)
                        self.stats.increment_stats_pcr_hatred(25)
                        self.stats.increment_stats_coding_skill(-5)
                        print(
                            "\nYou turn your back for one second — enough for a coked-up idiot"
                            "\nto drive a vodka bottle into your skull."
                            "\nSecurity drags him out, but you’re bleeding, dizzy, and confused."
                            "\nPolice arrives, and when they run your ID, the truth spills: "
                            "\nyou’re a full-time officer moonlighting illegally."
                            "\nYour boss is furious. You get fined by your colleagues."
                            "\nYou stagger home with a headache powerful enough to knock your IQ back several points."
                            "\n[OUTCOME]: -12.500 CZK, +25 PCR HATRED, -5 CODING SKILLS"
                        )

                    self.stats.get_stats_command()
                    input("\nCONTINUE...")
                    self.activity_selected = True


                elif menu_select_decision_activity_bouncer.decision_variable_name == "3":
                    self.main_menu()

            # STUDY PYTHON
            elif menu_select_decision_activity.decision_variable_name == "4":
                print("\nThere are multiple ways for you how to study Python."
                      "\nPython is now your Dojo, coding is your life, you need to master coding, there is no other way!"
                      "\nYou can learn on your own, or pay a tutor."
                      "\nStudying on your own is free, but less effective."
                      "\nPaying a tutor is costly but highly effective."
                      "\n1. [FREE] STUDY ON YOUR OWN"
                      "\n2. [1.500CZK] BUY A STUDY SESSION ON FIVERR"
                      "\n3. [50.000CZK] JOIN AN ON-LINE BOOTCAMP (GAIN BUFF FOR THE REST OF THE GAME)"
                      "\n4. RETURN TO MENU"
                      "\nSELECT YOUR OPTION (1-4):")
                menu_select_decision_activity_bouncer = (
                    Decision('', ("1", "2", "3", "4")))
                Decision.create_decision_variable(menu_select_decision_activity_bouncer)

                # 1) FREE STUDY – 80% +5, 20% +10
                if menu_select_decision_activity_bouncer.decision_variable_name == "1":
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
                elif menu_select_decision_activity_bouncer.decision_variable_name == "2":
                    # Pay for the session
                    self.stats.increment_stats_value_money(-1500)
                    activity_roll = randint(1, 100)

                    if activity_roll <= 60:
                        self.stats.increment_stats_coding_skill(10)
                        print(
                            "\nYou jump on a call with a mid-level developer from Fiverr."
                            "\nHe’s not a genius, but he is practical. He shows you how to structure your files,"
                            "\nexplains why your functions are a mess, and fixes a few key bad habits."
                            "\nYou leave the session with clearer thinking and a to-do list."
                            "\n[OUTCOME]: -1.500 CZK, +10 CODING SKILLS"
                        )
                    elif activity_roll <= 90:
                        self.stats.increment_stats_coding_skill(15)
                        print(
                            "\nYou luck out. Your tutor is actually sharp as hell."
                            "\nThey share their screen, walk you through refactoring, and explain OOP in a way "
                            "\nthat finally clicks with your brain."
                            "\nYou end the session tired but energized, with a feeling that you’ve leveled up."
                            "\n[OUTCOME]: -1.500 CZK, +15 CODING SKILLS"
                        )
                    elif activity_roll <= 100:
                        self.stats.increment_stats_coding_skill(25)
                        print(
                            "\nYou accidentally booked a beast. Senior dev, ten years in the field."
                            "\nHe doesn’t waste a second: code review, patterns, mental models, how to think like an engineer."
                            "\nYou fill pages of notes, your brain is fried, but something inside you has shifted."
                            "\nThis wasn’t just tutoring – this was a paradigm shift."
                            "\n[OUTCOME]: -1.500 CZK, +25 CODING SKILLS"
                        )

                    self.stats.get_stats_command()
                    input("\nCONTINUE...")
                    self.activity_selected = True

                # 3) ONLINE BOOTCAMP – PLACEHOLDER FOR PERMANENT BUFF
                elif menu_select_decision_activity_bouncer.decision_variable_name == "3":
                    self.stats.increment_stats_value_money(-50000)
                    print(
                        "\nYou sign a contract and pay for an on-line Python bootcamp."
                        "\nDeadlines, assignments, code reviews, community, mentors – the full package."
                        "\nFrom now on, every single day in this game, your coding skills will grow if you keep showing up."
                        "\nThis is no longer a hobby. This is a commitment."
                        "\n[OUTCOME]: -50.000 CZK, [BOOTCAMP BUFF ACTIVATED – PLACEHOLDER]"
                    )

                    # TODO: Implement permanent buff:
                    # Every in-game day: self.stats.increment_stats_coding_skill(+2)

                    self.stats.get_stats_command()
                    input("\nCONTINUE...")
                    self.activity_selected = True

                # 4) RETURN TO MAIN MENU
                elif menu_select_decision_activity_bouncer.decision_variable_name == "4":
                    self.main_menu()






            elif menu_select_decision_activity.decision_variable_name == "2":
                print("N/A")
            elif menu_select_decision_activity.decision_variable_name == "3":
                print("N/A")
            elif menu_select_decision_activity.decision_variable_name == "4":
                print("N/A")
            elif menu_select_decision_activity.decision_variable_name == "5":
                print("N/A")


            elif menu_select_decision_activity.decision_variable_name == "2":
                print("N/A")
            elif menu_select_decision_activity.decision_variable_name == "3":
                print("N/A")
            elif menu_select_decision_activity.decision_variable_name == "4":
                print("N/A")
            elif menu_select_decision_activity.decision_variable_name == "5":
                print("N/A")
        else:
            print("\nYou already did your daily activity today.")
