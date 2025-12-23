"""Module for starting message and especially for selecting the difficulty level, gaming mechanics, checks and limits."""
from random import randint

from game.game_logic.stats import Stats
from game.game_logic.day_cycle import DayCycle
from game.game_logic.decision_options import Decision
from game.game_logic.random_events import RandomEvents
from game.game_logic.game_endings import GameEndings
from game.game_logic.martin_meeting_event import MartinMeetingEvent
from game.game_logic.colonel_event import ColonelEvent
from game.game_logic.press_enter_to_continue import continue_prompt

class Game:
    """Sets the basic gaming mechanics, rules, win/loose conditions, difficulty levels."""
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    reset = "\033[0m"

    DIFFICULTY_SETTINGS = {
        "1": {"name": f"{green}EASY{reset}", "money": 55000, "coding": 10, "hatred": 15},
        "2": {"name": f"{yellow}HARD{reset}", "money": 35000, "coding": 5, "hatred": 25},
        "3": {"name": f"{red}INSANE{reset}", "money": 20000, "coding": 0, "hatred": 35},
        # 4 NIGHTMARE difficulty placeholder
    }

    def __init__(self, stats: Stats, day_cycle: DayCycle, events_list: RandomEvents):
        """Initialise self based on JB Stats class."""
        self.stats = stats
        self.day_cycle = day_cycle
        self.events_list = events_list
        self.selected_difficulty = None
        self.activity_selected = False
        self.python_bootcamp = False
        self.car_incident_stress = True

    def check_game_status(self):
        """
        Runs automatically to check if the player has lost.
        Also prints warnings if stats are critical.
        """
        red = "\033[91m"
        yellow = "\033[93m"
        reset = "\033[0m"

        if self.stats.pcr_hatred >= 100:
            GameEndings.mental_breakdown_ending(self.stats)

        if self.stats.available_money <= 0:
            GameEndings.homeless_ending(self.stats)

        if self.stats.pcr_hatred >= 65:
            print(f"\n{red}[WARNING] HATRED AT {self.stats.pcr_hatred}%! YOU WILL BREAK DOWN SOON IF YOU DON'T SLOW DOWN. {reset}")

        if self.stats.available_money < 7500:
            print(f"\n{yellow}[WARNING] LOW FUNDS ({self.stats.available_money} CZK). POVERTY IMMINENT.{reset}")

    def set_difficulty_level(self):
        """Lets the user choose difficulty level from the dictionary."""
        while True:
            print("\nSELECT THE DIFFICULTY:")

            for key, setting in self.DIFFICULTY_SETTINGS.items():
                print(f"{key}. {setting['name']}: {setting['money']},- CZK, Coding Skills {setting['coding']}, PCR Hatred {setting['hatred']}")

            print("\n(Enter a number from the list above): ")

            choice = input("> ").strip()

            if choice in self.DIFFICULTY_SETTINGS:
                settings = self.DIFFICULTY_SETTINGS[choice]

                confirm_select = input(f"\nYou selected '{settings['name']}', is that correct? (y/n): ")
                if confirm_select.lower() != "y":
                    continue

                print(f"\n{settings['name']} mode selected.\n")
                self.selected_difficulty = settings['name'].lower()
                self.stats.available_money = settings['money']
                self.stats.coding_skill = settings['coding']
                self.stats.pcr_hatred = settings['hatred']

                self.stats.get_stats_command()
                continue_prompt()
                break
            else:
                print("\nWrong input, try again.")

    def _apply_nightly_passives(self):
        """Calculates and applies overnight stat changes (buffs/debuffs)."""
        self.stats.increment_stats_pcr_hatred(5)

        if self.python_bootcamp:
            self.stats.increment_stats_coding_skill(5)
            print("\n[PYTHON BOOTCAMP] Your investment is starting to pay off! (+5 Coding Skills).")

        if self.stats.ai_paperwork_buff:
            print("\n[AI AUTOMATION] Your script handled the paperwork efficiently. (-5 Hatred)")
            self.stats.increment_stats_pcr_hatred(-5)

        if self.stats.daily_btc_income > 0:
            print(
                f"\n[PASSIVE INCOME] The Turkish fraudster sent his daily tribute: +{self.stats.daily_btc_income} CZK.")
            self.stats.increment_stats_value_money(self.stats.daily_btc_income)

    def _trigger_night_cycle(self):
        """Handles the visual and logical progression of ending a day."""
        self.day_cycle.day_end_message()
        self._apply_nightly_passives()
        self.day_cycle.next_day()

    def _handle_end_of_day_routine(self):
        """
        Orchestrates the complex logic of ending a day, including checking for
        salary, random events, and story progression.
        """
        # 1. Check if player skipped activity
        if not self.activity_selected:
            print("\nYou haven't selected your daily activity.")
            confirm = input("Are you sure you want to end the day? (y/n): ").strip().lower()
            if confirm != "y":
                return  # Return to menu without ending day

        # 2. Process the standard night cycle
        self._trigger_night_cycle()

        # 3. Check for Salary (Day 14)
        if self.day_cycle.current_day == 14:
            self.receive_salary()

        # 4. Check for Random Events (Every 3rd day, before day 22)
        if self.day_cycle.current_day % 3 == 0 and self.day_cycle.current_day < 22:
            event_happened = self.events_list.select_random_event(self.stats)

            # Logic Note: If an event happens, the day ends AGAIN immediately after in original code.
            # Preserved this behavior as it simulates the event taking up time.
            if event_happened:
                self._trigger_night_cycle()

        # 5. Check for MM Event (Day 24)
        if self.day_cycle.current_day == 24:
            self.day_cycle.next_day()
            self.day_cycle.day_start_message()
            mm_event = MartinMeetingEvent()
            mm_event.trigger_event(self.stats)

        # 6. Check for Colonel Event (Final Boss)
        # This checks if the current day matches the scheduled Boss Fight day (25 or 30).
        if self.day_cycle.current_day == self.stats.colonel_day:
            colonel_event = ColonelEvent()
            colonel_event.trigger_event(self.stats)

        # 7. Start the new day
        self.day_cycle.day_start_message()
        self.activity_selected = False

    def main_menu(self):
        """Basic UI, acts as a router for selectable options."""
        while True:
            self.check_game_status()

            print(
                "\nMAIN MENU:"
                "\n1. SHOW STATS"
                "\n2. SELECT ACTIVITY"
                "\n3. SHOW CONTACTS"
                "\n4. END THE DAY"
                "\nSELECT YOUR OPTION (1-4): "
            )

            choice = Decision.ask(("1", "2", "3", "4"))

            if choice == "1":
                print(f"\nDAY: #{self.day_cycle.current_day}/30.")
                self.stats.get_stats_command()

            elif choice == "2":
                self.select_activity()

            elif choice == "3":
                # Placeholder for future implementation
                print(
                    "\nYou open up your phone list (CONTACTS WIP):"
                    "\n1. MM\n2. MK\n3. PS\n4. PAUL GOODMAN\n5. COLONEL"
                    "\n(Press any key to return)"
                )
                input()

            elif choice == "4":
                self._handle_end_of_day_routine()

    def receive_salary(self):
        """Gives the player money based on level of hatred"""
        if self.stats.pcr_hatred <= 25:
            self.stats.available_money += 40000
            print("SALARY DAY")
            print("You have received extra money for you (pretending) being an example of a model police officer, good job!")
            print(f"You've received 40.000 CZK,-")
            continue_prompt()
        elif self.stats.pcr_hatred <= 50:
            self.stats.available_money += 30000
            print("SALARY DAY")
            print("Your bank just send you a notification - it's the salary day.")
            print("Since your recent work attitude diminished quite recently, so did your salary this month.")
            print(f"You've received 30.000 CZK,-")
            continue_prompt()
        else:
            self.stats.available_money += 20000
            print("SALARY DAY")
            print("Your bank just send you a notification - it's the salary day.")
            print("It has became obvious to everyone around you that you hate this job so much.")
            print("Disciplinary actions weren't enough, so the higher-ups decided to do what was 'required', to 'motivate' ")
            print("you towards more representative attitude to your job (which means monetary punishment).")
            print(f"You've received 20.000 CZK,-")
            continue_prompt()


    def select_activity(self):
        """Lets you select a daily activity once per day, through the game's menu."""
        if not self.activity_selected:
            print(
                "\nYou think about what activity to do today (You can select only one per day):"
                "\n1.GYM"
                "\n2.THERAPY"
                "\n3.BOUNCER NIGHT SHIFT"
                "\n4.CODING"
                "\n5.RETURN TO MENU"
                "\nSELECT YOUR OPTION (1-5):"
            )

            choice = Decision.ask(("1", "2", "3", "4", "5"))

            if choice == "1":
                self.activity_gym()
            elif choice == "2":
                self.activity_therapy()
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
              "\n1. [PAY 400CZK: (33/33/33%)] WE GO GYM!"
              "\n2. RETURN TO MENU"
              "\nSELECT YOUR OPTION (1-2):")

        choice = Decision.ask(("1", "2"))

        if choice == "1":
            cost = 400
            if self.stats.try_spend_money(cost):
                activity_roll = randint(1, 3)

                if activity_roll == 1:
                    self.stats.increment_stats_pcr_hatred(-25)
                    print("\nDude the pump you had was EPIC, you even hit a new PR!"
                          "\nYou feel strong and unstoppable, this was a great training."
                          f"\n[OUTCOME]: -{cost} CZK, -25 PCR HATRED")
                elif activity_roll == 2:
                    self.stats.increment_stats_pcr_hatred(-15)
                    print("\nYou feel great after this workout, it's awesome that"
                          "\nyou can come to better thoughts in the gym and relax."
                          f"\n[OUTCOME]: -{cost} CZK, -15 PCR HATRED")
                elif activity_roll == 3:
                    self.stats.increment_stats_pcr_hatred(-10)
                    print("\nYou had better trainings in the past, but you still enjoyed this one."
                          f"\n[OUTCOME]: -{cost} CZK, -10 PCR HATRED")

                self.stats.get_stats_command()
                input("\nCONTINUE...")
                self.activity_selected = True

            else:
                print(
                    f"\n[INSUFFICIENT FUNDS] You check your wallet... you don't even have {cost} CZK for the gym entry.")
                continue_prompt()
                self.activity_gym()

        elif choice == "2":
            self.main_menu()

    def activity_therapy(self):
        """Daily activity accessible from menu, allows you to visit a therapist and lower your PCR hatred for money."""
        print("\nYou've selected to go to a therapy, something that might actually help you lower your stress."
              "\nPaying for a therapist is somewhat expensive, but the results are worth it."
              "\n1. [PAY 1500CZK: -25 PCR HATRED] GET HELP. "
              "\n2. RETURN TO MENU"
              "\nSELECT YOUR OPTION (1-2):")

        choice = Decision.ask(("1", "2"))

        if choice == "1":
            cost = 1500
            if self.stats.try_spend_money(cost):
                self.stats.increment_stats_pcr_hatred(-25)

                print("\nYou call your therapist, you can finally vent out, it's a great relief.")
                print("\nShe listens to you and actually tries to help you.")
                print(
                    "\nShe reminds you that your situation is only temporary and that what job you do doesn't define who you are.")
                print("\nYou feel a great sense of relief after this session.")
                print(f"\n[OUTCOME]: -{cost} CZK, -25 PCR HATRED")

                self.stats.get_stats_command()
                self.activity_selected = True

            else:
                # NEW: Insufficient funds logic
                print(f"\n[INSUFFICIENT FUNDS] Therapy is a luxury you can't afford right now. You need {cost} CZK.")
                continue_prompt()
                self.activity_therapy()

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
        CODING_LEVEL = {
            "TIER 0": {"CODING SKILL": "0-49", "STANDARD RATE": 0, "HOUR RATE": 0},
            "TIER 1": {"CODING SKILL": "50-99", "STANDARD RATE": 2500, "HOUR RATE": 25},
            "TIER 2": {"CODING SKILL": "100-149", "STANDARD RATE": 5000, "HOUR RATE": 50},
            "TIER 3": {"CODING SKILL": "150-199", "STANDARD RATE": 7500, "HOUR RATE": 75},
            "TIER 4": {"CODING SKILL": "200+", "STANDARD RATE": 10000, "HOUR RATE": 100},
        }

        skill = getattr(self.stats, 'coding_skill', 0)
        if skill < 50:
            current_tier = "TIER 0"
        elif skill < 100:
            current_tier = "TIER 1"
        elif skill < 150:
            current_tier = "TIER 2"
        elif skill < 200:
            current_tier = "TIER 3"
        else:
            current_tier = "TIER 4"

        tier_info = CODING_LEVEL[current_tier]
        tier_display = f"{current_tier} | CODING SKILL: {tier_info['CODING SKILL']} | STANDARD RATE: {tier_info['STANDARD RATE']} | HOUR RATE: {tier_info['HOUR RATE']}"

        print("\nThere are multiple ways for you how to study Python."
              "\nPython is now your Dojo, coding is your life, you need to master coding, there is no other way!"
              "\nYou can learn on your own, or pay a tutor."
              "\nStudying on your own is free, but less effective."
              "\nPaying a tutor is costly but highly effective."
              f"\n1. [{tier_display}] CODE FOR MONEY $$$"
              "\n2. [2.500CZK - 65/25/10%] BUY A STUDY SESSION ON FIVERR"
              "\n3. [35.000CZK] JOIN AN ON-LINE BOOTCAMP (GAIN BUFF FOR THE REST OF THE GAME)"
              "\n4. RETURN TO MENU"
              "\n0. VIEW CURRENT TIER DETAILS"
              "\nSELECT YOUR OPTION (0-4):")

        choice = Decision.ask(("0", "1", "2", "3", "4"))

        if choice == "0":
            print(tier_display)
            continue_prompt()
            return self.activity_python()

        if choice == "1":
            # Compute payout using: Total = STANDARD RATE + CODING SKILL * HOUR RATE
            standard = tier_info['STANDARD RATE']
            hour_rate = tier_info['HOUR RATE']
            skill_now = self.stats.coding_skill
            total_money = standard + skill_now * hour_rate

            if current_tier == "TIER 0":
                print("\n[TIER 0] Still learning.")
                print("You can't code for money yet. Keep practicing and building tiny projects.")
                print("Unlock paid work at 50 Coding Skill.")
                continue_prompt()
                return self.activity_python()

            elif current_tier == "TIER 1":
                print("\n[TIER 1] Junior Scripter Online")
                print(f"Your current coding skill is {skill_now}.")
                print("Example work:")
                print("- Basic CLI utilities, CSV/Excel cleaners, simple web-scraper")
                print("- Small bug fixes, wiring helper functions, basic refactors")
                print(f"Calculation: STANDARD RATE ({standard}) + CODING SKILL ({skill_now}) * HOUR RATE ({hour_rate})")
                print(f"You received: {total_money} CZK")
                self.stats.increment_stats_value_money(total_money)
                self.activity_selected = True
                self.stats.get_stats_command()
                continue_prompt()

            elif current_tier == "TIER 2":
                print("\n[TIER 2] Solid Developer")
                print(f"Your current coding skill is {skill_now}.")
                print("Example work:")
                print("- CRUD REST API (Flask/FastAPI), small microservice, integrations")
                print("- Non-trivial automation/data pipeline, refactor modules into packages")
                print(f"Calculation: STANDARD RATE ({standard}) + CODING SKILL ({skill_now}) * HOUR RATE ({hour_rate})")
                print(f"You received: {total_money} CZK")
                self.stats.increment_stats_value_money(total_money)
                self.activity_selected = True
                self.stats.get_stats_command()
                continue_prompt()

            elif current_tier == "TIER 3":
                print("\n[TIER 3] Senior Engineer Mode")
                print(f"Your current coding skill is {skill_now}.")
                print("Example work:")
                print("- Production-ready backend with auth, caching, logging, tests")
                print("- Performance tuning, DB indexing, CI pipelines, containerization")
                print(f"Calculation: STANDARD RATE ({standard}) + CODING SKILL ({skill_now}) * HOUR RATE ({hour_rate})")
                print(f"You received: {total_money} CZK")
                self.stats.increment_stats_value_money(total_money)
                self.activity_selected = True
                self.stats.get_stats_command()
                continue_prompt()

            elif current_tier == "TIER 4":
                print("\n[TIER 4] God-Tier Developer")
                print(f"Your current coding skill is {skill_now}.")
                print("Example work:")
                print("- Highly scalable distributed services with observability and SLOs")
                print("- Complex domain modeling, deep refactors, bulletproof test suites")
                print(f"Calculation: STANDARD RATE ({standard}) + CODING SKILL ({skill_now}) * HOUR RATE ({hour_rate})")
                print(f"You received: {total_money} CZK")
                self.stats.increment_stats_value_money(total_money)
                self.activity_selected = True
                self.stats.get_stats_command()
                continue_prompt()

        elif choice == "2":
            cost = 2500
            if self.stats.try_spend_money(cost):
                activity_roll = randint(1, 100)

                if activity_roll <= 65:
                    self.stats.increment_stats_coding_skill(10)
                    print(
                        "\nYou jump on a call with a mid-level developer from Fiverr."
                        "\nHe’s not a genius, but he is practical. He shows you how to structure your files,"
                        "\nexplains why your functions are a mess, and fixes a few key bad habits."
                        "\nYou leave the session with clearer thinking and a to-do list."
                        f"\n[OUTCOME]: -{cost} CZK, +10 CODING SKILLS"
                    )
                elif activity_roll <= 90:
                    self.stats.increment_stats_coding_skill(15)
                    print(
                        "\nYou luck out. Your tutor is actually sharp as hell."
                        "\nThey share their screen, walk you through refactoring, and explain OOP in a way "
                        "\nthat finally clicks with your brain."
                        "\nYou end the session tired but energized, with a feeling that you’ve leveled up."
                        f"\n[OUTCOME]: -{cost} CZK, +15 CODING SKILLS"
                    )
                elif activity_roll <= 100:
                    self.stats.increment_stats_coding_skill(25)
                    print(
                        "\nYou accidentally booked a beast. Senior dev, ten years in the field."
                        "\nHe doesn’t waste a second: code review, patterns, mental models, how to think like an engineer."
                        "\nYou fill pages of notes, your brain is fried, but something inside you has shifted."
                        "\nThis wasn’t just tutoring – this was a paradigm shift."
                        f"\n[OUTCOME]: -{cost} CZK, +25 CODING SKILLS"
                    )

                self.stats.get_stats_command()
                continue_prompt()
                self.activity_selected = True

            else:
                print(
                    f"\n[INSUFFICIENT FUNDS] You check your bank account. You only have {self.stats.available_money} CZK.")
                print(f"You need {cost} CZK for the tutor.")
                continue_prompt()
                self.activity_python()

        elif choice == "3":
            cost = 35000
            if self.stats.try_spend_money(cost) and not self.python_bootcamp:
                print(
                    "\nYou sign a contract and pay for an on-line Python bootcamp."
                    "\nDeadlines, assignments, code reviews, community, mentors – the full package."
                    "\nFrom now on, your coding skill will keep on growing daily!."
                    "\nThis is no longer a hobby. This is a commitment."
                    f"\n[OUTCOME]: -{cost} CZK, [BOOTCAMP BUFF ACTIVATED +5 CODING SKILL EVERYDAY]"
                )

                self.python_bootcamp = True
                self.stats.get_stats_command()
                continue_prompt()
                self.activity_selected = True

            elif self.python_bootcamp:
                print("\nYou have already joined the bootcamp!")
                continue_prompt()
                self.activity_python()

            else:
                print(f"\n[INSUFFICIENT FUNDS] Transaction Declined. You need {cost} CZK.")
                print("That is a lot of money. Maybe stick to free docs for now?")
                continue_prompt()
                self.activity_python()

        elif choice == "4":
            self.main_menu()

        else:
            print("\nYou already did your daily activity today.")
            self.main_menu()