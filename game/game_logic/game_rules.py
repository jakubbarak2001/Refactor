"""Module for starting message and especially for selecting the difficulty level, gaming mechanics, checks and limits."""
import sys
from random import randint

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from game.game_logic.colonel_event import ColonelEvent
from game.game_logic.day_cycle import DayCycle
from game.game_logic.game_endings import GameEndings
from game.game_logic.interaction import Interaction
from game.game_logic.martin_meeting_event import MartinMeetingEvent
from game.game_logic.press_enter_to_continue import continue_prompt
from game.game_logic.random_events import RandomEvents
from game.game_logic.stats import Stats

console = Console(force_terminal=True, width=None)


class Game:
    """Sets the basic gaming mechanics, rules, win/loose conditions, difficulty levels."""
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    reset = "\033[0m"

    DIFFICULTY_SETTINGS = {
        "1": {"name": "EASY", "color": "bright_green", "money": 55000, "coding": 10, "hatred": 15},
        "2": {"name": "HARD", "color": "yellow", "money": 35000, "coding": 5, "hatred": 25},
        "3": {"name": "INSANE", "color": "bright_red", "money": 20000, "coding": 0, "hatred": 35},
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
        Also prints warnings if stats are critically low.
        """

        if self.stats.pcr_hatred >= 100:
            GameEndings.mental_breakdown_ending(self.stats)

        if self.stats.available_money <= 0:
            GameEndings.homeless_ending(self.stats)

        if self.stats.pcr_hatred >= 65:
            warning_text = Text()
            warning_text.append("⚠️  ", style="bold bright_red")
            warning_text.append(f"HATRED AT {self.stats.pcr_hatred}%!", style="bold bright_red")
            warning_text.append("\nYOU WILL BREAK DOWN SOON IF YOU DON'T SLOW DOWN.", style="bold red")
            
            print("\n")
            print(Panel(
                warning_text,
                border_style="bold bright_red",
                title="[bold white on bright_red] > WARNING < [/]",
                padding=(1, 2),
                expand=False
            ))

        if self.stats.available_money < 7500:
            funds_warning_text = Text()
            funds_warning_text.append("⚠️  ", style="bold bright_yellow")
            funds_warning_text.append(f"LOW FUNDS: {self.stats.available_money:,} CZK", style="bold bright_yellow")
            funds_warning_text.append("\nPOVERTY IMMINENT.", style="bold yellow")
            
            print("\n")
            print(Panel(
                funds_warning_text,
                border_style="bold yellow",
                title="[bold white on yellow] > WARNING < [/]",
                padding=(1, 2),
                expand=False
            ))

    def set_difficulty_level(self):
        """Lets the user choose difficulty level from the dictionary with beautiful Rich TUI."""
        while True:
            print("\n")
            
            # Create difficulty options text with styling
            options_text = Text()
            options_text.append("SELECT YOUR DIFFICULTY\n", style="bold white")
            options_text.append("═" * 50 + "\n", style="dim white")
            
            # Build each difficulty option with styling
            for key in sorted(self.DIFFICULTY_SETTINGS.keys()):
                setting = self.DIFFICULTY_SETTINGS[key]
                color = setting['color']
                
                # Option number with difficulty name
                options_text.append(f"\n[{key}] ", style=f"bold {color}")
                options_text.append(f"{setting['name']}", style=f"bold {color}")
                
                # Stats display
                options_text.append("\n   ", style="")
                options_text.append("💰 Money: ", style="bold cyan")
                options_text.append(f"{setting['money']:,} CZK\n", style="bright_white")
                options_text.append("   ", style="")
                options_text.append("💻 Coding: ", style="bold cyan")
                options_text.append(f"{setting['coding']} points\n", style="bright_white")
                options_text.append("   ", style="")
                options_text.append("😡 Hatred: ", style="bold cyan")
                options_text.append(f"{setting['hatred']}/100\n", style="bright_white")
            
            options_text.append("\n" + "═" * 50, style="dim white")
            
            # Display in a styled panel
            print(Panel(
                options_text,
                border_style="bold yellow",
                title="[bold white on yellow] > DIFFICULTY SELECTION < [/]",
                padding=(1, 3),
                expand=False
            ))
            
            # Get user input
            choice = console.input("\n[bold cyan]Enter your choice[/bold cyan] [dim](1-3)[/dim]: ").strip()

            if choice in self.DIFFICULTY_SETTINGS:
                settings = self.DIFFICULTY_SETTINGS[choice]
                color = settings['color']
                
                # Create confirmation message
                confirm_text = Text()
                confirm_text.append("You selected: ", style="bold white")
                confirm_text.append(f"{settings['name']}", style=f"bold {color}")
                confirm_text.append("\n\n", style="")
                confirm_text.append("Starting Stats:\n", style="bold cyan")
                confirm_text.append(f"  💰 Money: {settings['money']:,} CZK\n", style="bright_white")
                confirm_text.append(f"  💻 Coding: {settings['coding']} points\n", style="bright_white")
                confirm_text.append(f"  😡 Hatred: {settings['hatred']}/100\n", style="bright_white")
                confirm_text.append("\nProceed with this difficulty?", style="italic")
                
                print("\n")
                print(Panel(
                    confirm_text,
                    border_style=f"bold {color}",
                    title=f"[bold white on {color}] > CONFIRM SELECTION < [/]",
                    padding=(1, 3),
                    expand=False
                ))
                
                confirm_select = console.input("\n[bold](y/n)[/bold]: ").strip().lower()
                if confirm_select != "y":
                    continue

                # Apply settings
                self.selected_difficulty = settings['name'].lower()
                self.stats.difficulty = settings['name'].lower()  # Store in stats for access in endings
                self.stats.available_money = settings['money']
                self.stats.coding_skill = settings['coding']
                self.stats.pcr_hatred = settings['hatred']

                # Display confirmation
                print("\n")
                success_text = Text()
                success_text.append(f"{settings['name']}", style=f"bold {color}")
                success_text.append(" mode selected!", style="bold white")
                
                print(Panel(
                    Align.center(success_text),
                    border_style=f"bold {color}",
                    padding=(1, 4),
                    expand=False
                ))
                print()
                
                self.stats.get_stats_command()
                continue_prompt()
                break
            else:
                error_text = Text("Invalid choice! Please enter 1, 2, or 3.", style="bold red")
                print("\n")
                print(Panel(
                    error_text,
                    border_style="bold red",
                    title="[bold white on red] > ERROR < [/]",
                    padding=(1, 2),
                    expand=False
                ))
                print()

    def _show_buffs(self):
        """
        Display current active buffs in a Rich Panel.
        Shows all active passive buffs that affect nightly stats.
        Only displays if there are active buffs.
        """
        active_buffs = []
        
        # Check Python Bootcamp buff
        if self.python_bootcamp:
            active_buffs.append(("💻 Python Bootcamp", "+5 Coding Skills per night", "bright_cyan"))
        
        # Check AI Paperwork Automation buff
        if self.stats.ai_paperwork_buff:
            active_buffs.append(("🤖 AI Automation", "-5 Hatred per night", "bright_green"))
        
        # Check Passive BTC Income
        if self.stats.daily_btc_income > 0:
            active_buffs.append(("💰 Passive Income", f"+{self.stats.daily_btc_income} CZK per night", "bright_yellow"))
        
        # Only display if there are active buffs
        if not active_buffs:
            return
        
        buffs_text = Text()
        buffs_text.append("Active Buffs:\n", style="bold white")
        buffs_text.append("═" * 40 + "\n", style="dim white")
        
        for i, (name, effect, color) in enumerate(active_buffs):
            if i > 0:
                buffs_text.append("\n", style="")
            buffs_text.append(f"• {name}", style=f"bold {color}")
            buffs_text.append(f"\n  {effect}", style="dim white")
        
        buffs_text.append("\n" + "═" * 40, style="dim white")
        
        print("\n")
        print(Panel(
            buffs_text,
            border_style="bold color(129)",
            title="[bold white on color(129)] > BUFFS < [/]",
            padding=(1, 2),
            expand=False
        ))

    def _apply_nightly_passives(self):
        """Calculates and applies overnight stat changes (buffs/debuffs)."""
        self.stats.increment_stats_pcr_hatred(5)

        if self.python_bootcamp:
            self.stats.increment_stats_coding_skill(5)

        if self.stats.ai_paperwork_buff:
            self.stats.increment_stats_pcr_hatred(-5)

        if self.stats.daily_btc_income > 0:
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

        # 3. Show the new day message and buffs (before any events)
        self.day_cycle.day_start_message()
        self._show_buffs()

        # 4. Check for Salary (Day 14)
        if self.day_cycle.current_day == 14:
            self.receive_salary()

        # 5. Check for Random Events (Every 3rd day, before day 22)
        if self.day_cycle.current_day % 3 == 0 and self.day_cycle.current_day < 22:
            event_happened = self.events_list.select_random_event(self.stats)

            # Logic Note: If an event happens, the day ends AGAIN immediately after in original code.
            # Preserved this behavior as it simulates the event taking up time.
            if event_happened:
                self._trigger_night_cycle()
                # Show the new day message again after the event-triggered night cycle
                self.day_cycle.day_start_message()
                self._show_buffs()

        # 6. Check for MM Event (Day 24)
        # Note: Day is already 24 after night cycle from day 23, so don't call next_day() again
        if self.day_cycle.current_day == 24:
            mm_event = MartinMeetingEvent()
            mm_event.trigger_event(self.stats)

        # 7. Check for Colonel Event (Final Boss)
        # This checks if the current day matches the scheduled Boss Fight day (25 or 30).
        if self.day_cycle.current_day == self.stats.colonel_day:
            colonel_event = ColonelEvent()
            colonel_event.trigger_event(self.stats)

        # 8. Reset activity flag for the new day
        self.activity_selected = False

    def main_menu(self):
        """Beautiful Rich TUI main menu that acts as a router for selectable options."""
        while True:
            self.check_game_status()

            # Create menu options with styling
            menu_text = Text()
            menu_text.append("SELECT AN OPTION\n", style="bold white")
            menu_text.append("═" * 40 + "\n", style="dim white")
            
            # Menu options with icons
            menu_text.append("\n[1] ", style="bold cyan")
            menu_text.append("📊 SHOW STATS", style="bold bright_white")
            menu_text.append("\n   View your current stats", style="dim white")
            
            menu_text.append("\n\n[2] ", style="bold cyan")
            menu_text.append("⚙️ SELECT ACTIVITY", style="bold bright_white")
            menu_text.append("\n   Choose your daily activity", style="dim white")
            
            menu_text.append("\n\n[3] ", style="bold cyan")
            menu_text.append("📞 SHOW CONTACTS", style="bold bright_white")
            menu_text.append("\n   View your contact list", style="dim white")
            
            menu_text.append("\n\n[4] ", style="bold cyan")
            menu_text.append("🌙 END THE DAY", style="bold bright_white")
            menu_text.append("\n   Progress to the next day", style="dim white")
            
            menu_text.append("\n\n" + "═" * 40, style="dim white")
            
            # Display day information at the top
            day_info = Text()
            day_info.append(f"DAY ", style="bold white")
            day_info.append(f"#{self.day_cycle.current_day}", style="bold bright_yellow")
            day_info.append(f"/30", style="bold white")
            
            # Create the main menu panel
            print("\n")
            print(Panel(
                menu_text,
                border_style="bold blue",
                title="[bold white on blue] > MAIN MENU < [/]",
                subtitle=day_info,
                padding=(1, 3),
                expand=False
            ))
            
            choice = Interaction.ask(("1", "2", "3", "4"))

            if choice == "1":
                self.stats.get_stats_command()
                continue_prompt()

            elif choice == "2":
                self.select_activity()

            elif choice == "3":
                # Placeholder for future implementation
                contacts_text = Text()
                contacts_text.append("You open up your phone list:\n", style="bold white")
                contacts_text.append("═" * 30 + "\n", style="dim white")
                contacts_text.append("\n1. MM\n", style="bright_white")
                contacts_text.append("2. MK\n", style="bright_white")
                contacts_text.append("3. PS\n", style="bright_white")
                contacts_text.append("4. PAUL GOODMAN\n", style="bright_white")
                contacts_text.append("5. COLONEL\n", style="bright_white")
                contacts_text.append("\n" + "═" * 30, style="dim white")
                
                print("\n")
                print(Panel(
                    contacts_text,
                    border_style="bold cyan",
                    title="[bold white on cyan] > CONTACTS < [/]",
                    subtitle="[dim](WIP - Press ENTER to return)[/dim]",
                    padding=(1, 3),
                    expand=False
                ))
                print()
                continue_prompt()

            elif choice == "4":
                self._handle_end_of_day_routine()

    def receive_salary(self):
        """Beautiful Rich TUI salary day message with money based on level of hatred"""
        if self.stats.pcr_hatred <= 25:
            self.stats.available_money += 40000
            salary_amount = 40000
            
            salary_text = Text()
            salary_text.append("💰 ", style="bold bright_green")
            salary_text.append("SALARY DAY", style="bold bright_green")
            salary_text.append("\n\n", style="")
            salary_text.append("You have received extra money for you (pretending) being\n", style="white")
            salary_text.append("an example of a model police officer, good job!\n\n", style="white")
            salary_text.append("Amount Received: ", style="bold cyan")
            salary_text.append(f"{salary_amount:,} CZK", style="bold bright_green")
            
            print("\n")
            print(Panel(
                salary_text,
                border_style="bold bright_green",
                title="[bold white on bright_green] > SALARY DAY < [/]",
                padding=(1, 3),
                expand=False
            ))
            continue_prompt()
            
        elif self.stats.pcr_hatred <= 50:
            self.stats.available_money += 30000
            salary_amount = 30000
            
            salary_text = Text()
            salary_text.append("💰 ", style="bold yellow")
            salary_text.append("SALARY DAY", style="bold yellow")
            salary_text.append("\n\n", style="")
            salary_text.append("Your bank just sent you a notification - it's the salary day.\n", style="white")
            salary_text.append("Since your recent work attitude diminished quite recently,\n", style="white")
            salary_text.append("so did your salary this month.\n\n", style="white")
            salary_text.append("Amount Received: ", style="bold cyan")
            salary_text.append(f"{salary_amount:,} CZK", style="bold yellow")
            
            print("\n")
            print(Panel(
                salary_text,
                border_style="bold yellow",
                title="[bold white on yellow] > SALARY DAY < [/]",
                padding=(1, 3),
                expand=False
            ))
            continue_prompt()
            
        else:
            self.stats.available_money += 20000
            salary_amount = 20000
            
            salary_text = Text()
            salary_text.append("💰 ", style="bold red")
            salary_text.append("SALARY DAY", style="bold red")
            salary_text.append("\n\n", style="")
            salary_text.append("Your bank just sent you a notification - it's the salary day.\n", style="white")
            salary_text.append("It has become obvious to everyone around you that you hate this job so much.\n", style="white")
            salary_text.append("Disciplinary actions weren't enough, so the higher-ups decided to do\n", style="white")
            salary_text.append("what was 'required', to 'motivate' you towards more representative\n", style="white")
            salary_text.append("attitude to your job (which means monetary punishment).\n\n", style="white")
            salary_text.append("Amount Received: ", style="bold cyan")
            salary_text.append(f"{salary_amount:,} CZK", style="bold red")
            
            print("\n")
            print(Panel(
                salary_text,
                border_style="bold red",
                title="[bold white on red] > SALARY DAY < [/]",
                padding=(1, 3),
                expand=False
            ))
            continue_prompt()

    def select_activity(self):
        """Beautiful Rich TUI activity selection menu."""
        if not self.activity_selected:
            # Create activity options with styling
            activity_text = Text()
            activity_text.append("You think about what activity to do today\n", style="bold white")
            activity_text.append("(You can select only one per day)\n", style="dim white")
            activity_text.append("═" * 40 + "\n", style="dim white")
            
            # Activity options with icons
            activity_text.append("\n[1] ", style="bold cyan")
            activity_text.append("💪 GYM", style="bold bright_white")
            activity_text.append("\n   Lower your stress through exercise", style="dim white")
            
            activity_text.append("\n\n[2] ", style="bold cyan")
            activity_text.append("🧠 THERAPY", style="bold bright_white")
            activity_text.append("\n   Get professional help to reduce hatred", style="dim white")
            
            activity_text.append("\n\n[3] ", style="bold cyan")
            activity_text.append("🌙 BOUNCER NIGHT SHIFT", style="bold bright_white")
            activity_text.append("\n   Earn money with some risk", style="dim white")
            
            activity_text.append("\n\n[4] ", style="bold cyan")
            activity_text.append("💻 CODING", style="bold bright_white")
            activity_text.append("\n   Practice Python and improve your skills", style="dim white")
            
            activity_text.append("\n\n[5] ", style="bold cyan")
            activity_text.append("⬅️  RETURN TO MENU", style="bold bright_white")
            
            activity_text.append("\n\n" + "═" * 40, style="dim white")
            
            # Display in a styled panel
            print("\n")
            print(Panel(
                activity_text,
                border_style="bold green",
                title="[bold white on green] > SELECT ACTIVITY < [/]",
                padding=(1, 3),
                expand=False
            ))
            
            choice = Interaction.ask(("1", "2", "3", "4", "5"))

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
            already_done_text = Text("You've already done your daily activity today!", style="bold yellow")
            print("\n")
            print(Panel(
                already_done_text,
                border_style="bold yellow",
                title="[bold white on yellow] > NOTICE < [/]",
                padding=(1, 2),
                expand=False
            ))
            print()

    def activity_gym(self):
        """Beautiful Rich TUI gym activity menu."""
        gym_text = Text()
        gym_text.append("You've selected to go to the gym with your trainer.\n", style="bold white")
        gym_text.append("Training will help you to relax, but it will cost you some money.\n", style="white")
        gym_text.append("═" * 40 + "\n", style="dim white")
        
        gym_text.append("\n[1] ", style="bold cyan")
        gym_text.append("[PAY 400 CZK] ", style="bold yellow")
        gym_text.append("WE GO GYM!", style="bold bright_white")
        gym_text.append("\n   (33/33/33% chance for different outcomes)", style="dim white")
        
        gym_text.append("\n\n[2] ", style="bold cyan")
        gym_text.append("⬅️  RETURN TO MENU", style="bold bright_white")
        
        gym_text.append("\n\n" + "═" * 40, style="dim white")
        
        print("\n")
        print(Panel(
            gym_text,
            border_style="bold magenta",
            title="[bold white on magenta] > GYM ACTIVITY < [/]",
            padding=(1, 3),
            expand=False
        ))
        
        choice = Interaction.ask(("1", "2"))

        if choice == "1":
            cost = 400
            if self.stats.try_spend_money(cost):
                activity_roll = randint(1, 3)

                if activity_roll == 1:
                    self.stats.increment_stats_pcr_hatred(-25)
                    print("\nDude the pump you had was EPIC, you even hit a new PR!"
                          "\nYou feel strong and unstoppable, this was a great training.")
                    Interaction.show_outcome(f"- {cost} CZK, -25 PCR HATRED")
                elif activity_roll == 2:
                    self.stats.increment_stats_pcr_hatred(- 15)
                    print("\nYou feel great after this workout, it's awesome that"
                          "\nyou can come to better thoughts in the gym and relax.")
                    Interaction.show_outcome(f"- {cost} CZK, - 15 PCR HATRED")
                elif activity_roll == 3:
                    self.stats.increment_stats_pcr_hatred(- 10)
                    print("\nYou had better trainings in the past, but you still enjoyed this one.")
                    Interaction.show_outcome(f"- {cost} CZK, - 10 PCR HATRED")

                self.stats.get_stats_command()
                continue_prompt()
                self.activity_selected = True

            else:
                print(
                    f"\n[INSUFFICIENT FUNDS] You check your wallet... you don't even have {cost} CZK for the gym entry.")
                continue_prompt()
                self.activity_gym()

        elif choice == "2":
            self.main_menu()

    def activity_therapy(self):
        """Beautiful Rich TUI therapy activity menu."""
        therapy_text = Text()
        therapy_text.append("You've selected to go to therapy.\n", style="bold white")
        therapy_text.append("Something that might actually help you lower your stress.\n", style="white")
        therapy_text.append("Paying for a therapist is expensive, but the results are worth it.\n", style="white")
        therapy_text.append("═" * 40 + "\n", style="dim white")
        
        therapy_text.append("\n[1] ", style="bold cyan")
        therapy_text.append("[PAY 1500 CZK] ", style="bold yellow")
        therapy_text.append("GET HELP", style="bold bright_white")
        therapy_text.append("\n   (- 25 PCR HATRED)", style="dim green")
        
        therapy_text.append("\n\n[2] ", style="bold cyan")
        therapy_text.append("⬅️  RETURN TO MENU", style="bold bright_white")
        
        therapy_text.append("\n\n" + "═" * 40, style="dim white")
        
        print("\n")
        print(Panel(
            therapy_text,
            border_style="bold blue",
            title="[bold white on blue] > THERAPY ACTIVITY < [/]",
            padding=(1, 3),
            expand=False
        ))
        
        choice = Interaction.ask(("1", "2"))

        if choice == "1":
            cost = 1500
            if self.stats.try_spend_money(cost):
                self.stats.increment_stats_pcr_hatred(-25)

                print("\nYou call your therapist, you can finally vent out, it's a great relief.")
                print("\nShe listens to you and actually tries to help you.")
                print(
                    "\nShe reminds you that your situation is only temporary and that what job you do doesn't define who you are.")
                print("\nYou feel a great sense of relief after this session.")
                Interaction.show_outcome(f"- {cost} CZK, - 25 PCR HATRED")

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
        """Beautiful Rich TUI bouncer activity menu."""
        bouncer_text = Text()
        bouncer_text.append("You were offered to work as a bouncer\n", style="bold white")
        bouncer_text.append("in either a local night club or a strip bar.\n\n", style="white")
        bouncer_text.append("Night club: Generally safe, but some risk.\n", style="yellow")
        bouncer_text.append("Strip bar: VERY RISKY, but VERY HIGH reward.\n", style="bright_red")
        bouncer_text.append("═" * 40 + "\n", style="dim white")
        
        bouncer_text.append("\n[1] ", style="bold cyan")
        bouncer_text.append("WORK AS A BOUNCER AT A NIGHT CLUB", style="bold bright_white")
        bouncer_text.append("\n   [70/20/10%] outcomes", style="dim yellow")
        
        bouncer_text.append("\n\n[2] ", style="bold cyan")
        bouncer_text.append("WORK AS A BOUNCER AT A STRIP BAR", style="bold bright_white")
        bouncer_text.append("\n   [5/20/50/20/5%] outcomes (RISKY!)", style="dim bright_red")
        
        bouncer_text.append("\n\n[3] ", style="bold cyan")
        bouncer_text.append("⬅️  RETURN TO MENU", style="bold bright_white")
        
        bouncer_text.append("\n\n" + "═" * 40, style="dim white")
        
        print("\n")
        print(Panel(
            bouncer_text,
            border_style="bold red",
            title="[bold white on red] > BOUNCER ACTIVITY < [/]",
            padding=(1, 3),
            expand=False
        ))
        
        choice = Interaction.ask(("1", "2", "3"))

        if choice == "1":
            activity_roll = randint(1, 100)
            if activity_roll <= 70:
                self.stats.increment_stats_pcr_hatred(10)
                self.stats.increment_stats_value_money(4000)
                print("\nNight shift was really calm, nothing happened and you got your usual rate."
                      "\nYou got angrier at PCR today, because the only reason why you work here,"
                      "\nis the salary you get from them.")
                Interaction.show_outcome("+ 3000 CZK, - 10 PCR HATRED")
            elif activity_roll <= 90:
                self.stats.increment_stats_value_money(7500)
                self.stats.increment_stats_pcr_hatred(- 10)
                print("\nThe night shift was great! You gained extra tip from your boss today."
                      "\nThis made you feel so good, that you even forgot about completely about PCR.")
                Interaction.show_outcome("+ 7500 CZK, - 10 PCR HATRED")
            elif activity_roll <= 100:
                self.stats.increment_stats_pcr_hatred(20)
                self.stats.increment_stats_value_money(4000)
                print("\nThere was an incident... some guys fought over one chick at the club, "
                      "\nThe police was called and your colleagues recognised you and made fun of you."
                      "\nYou were the talk of the following days, there will be no disciplinary action "
                      "\ntaken against you, yet this made you completely mad.")
                Interaction.show_outcome("+ 4000 CZK, + 20 PCR HATRED!")

            self.stats.get_stats_command()
            continue_prompt()
            self.activity_selected = True

        elif choice == "2":
            activity_roll = randint(1, 100)
            if activity_roll <= 5:
                self.stats.increment_stats_value_money(35000)
                self.stats.increment_stats_pcr_hatred(- 15)
                print(
                    "\nA famous regular shows up drunk and paranoid. Two guys try to drag him outside, but you"
                    "\nintervene with textbook precision — one hand block, one arm-bar, clean de-escalation."
                    "\nThe CCTV shows you prevented something ugly."
                    "\nAt the end of the night your boss calls you to the office,"
                    "\npraises your calm judgment, and slides an envelope across the table."
                    "\n'Not many can do what you did tonight.'"
                )
                Interaction.show_outcome("+ 25000 CZK, - 15 PCR HATRED")
            elif activity_roll <= 25:
                self.stats.increment_stats_value_money(12500)
                self.stats.increment_stats_coding_skill(2)
                print(
                    "\nSteady crowds, few arguments, no real threats. You handle everything with routine precision."
                    "\nYou even use downtime at the door to mentally rehearse OOP concepts "
                    "\nand class hierarchies — weirdly effective."
                    "\nBoss gives you something extra for showing up, nods at you, no drama.."
                )
                Interaction.show_outcome("+12500 CZK, + 2 CODING SKILLS")

            elif activity_roll <= 75:
                self.stats.increment_stats_value_money(6500)
                self.stats.increment_stats_pcr_hatred(5)
                print(
                    "\nStandard calm shift, where nothing of great importance happens."
                    "\nYou find this shift pretty boring today."
                    "\nYou keep on wondering, how long it's going to take you to actually start coding."
                    "\nand doing something more meaningful then standing an entire night at a door."
                    "\nAt-least - the money they pay here is really something else."
                )
                Interaction.show_outcome("+4500 CZK, +5 PCR HATRED")


            elif activity_roll <= 95:
                self.stats.increment_stats_value_money(1000)
                self.stats.increment_stats_pcr_hatred(25)
                print(
                    "\nA fight breaks out inside. "
                    "\nYou break it up, but one participant recognizes your face from the force. "
                    "\n“Ty vole, to je POLDA!”"
                    "\nWhen the responding patrol arrives, the looks they give you are suffocating. "
                    "\nTwo colleagues whisper. One smirks."
                    "\nYour boss isn't thrilled about the chaos either and gives you only a partial payout."
                )
                Interaction.show_outcome("- 1000CZK, + 25 PCR HATRED")

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
                )
                Interaction.show_outcome("-12500 CZK, +35 PCR HATRED, -5 CODING SKILLS")

            self.stats.get_stats_command()
            continue_prompt()
            self.activity_selected = True


        elif choice == "3":
            self.main_menu()

    def get_coding_tier_info(self):
        """
        Determines the current coding tier based on skill level.
        Returns a tuple: (tier_name, tier_data_dict)
        """
        skill = getattr(self.stats, 'coding_skill', 0)

        CODING_LEVELS = {
            "TIER 1": {"CODING SKILL": "0-49", "STANDARD RATE": 0, "HOUR RATE": 0, "LABEL": "Still Learning"},
            "TIER 2": {"CODING SKILL": "50-99", "STANDARD RATE": 2500, "HOUR RATE": 25, "LABEL": "Junior Scripter"},
            "TIER 3": {"CODING SKILL": "100-149", "STANDARD RATE": 5000, "HOUR RATE": 50, "LABEL": "Solid Developer"},
            "TIER 4": {"CODING SKILL": "150-199", "STANDARD RATE": 7500, "HOUR RATE": 75, "LABEL": "Senior Engineer"},
            "TIER 5": {"CODING SKILL": "200+", "STANDARD RATE": 10000, "HOUR RATE": 100, "LABEL": "God-Tier Dev"},
        }

        if skill < 50:
            return "TIER 1", CODING_LEVELS["TIER 1"]
        elif skill < 100:
            return "TIER 2", CODING_LEVELS["TIER 2"]
        elif skill < 150:
            return "TIER 3", CODING_LEVELS["TIER 3"]
        elif skill < 200:
            return "TIER 4", CODING_LEVELS["TIER 4"]
        else:
            return "TIER 5", CODING_LEVELS["TIER 5"]

    def _perform_coding_work(self):
        """Logic for Option 1: Working for money."""
        current_tier, tier_info = self.get_coding_tier_info()
        skill_now = self.stats.coding_skill

        # Calculate Earnings
        standard = tier_info['STANDARD RATE']
        hour_rate = tier_info['HOUR RATE']
        total_money = standard + (skill_now * hour_rate)

        if current_tier == "TIER 1":
            print("\n[TIER 1] Still learning.")
            print("You can't code for money yet. Keep practicing and building tiny projects.")
            print("Unlock paid work at 50 Coding Skill.")
            continue_prompt()
            return self.activity_python()

        narratives = {
            "TIER 2": [
                "Basic CLI utilities, CSV/Excel cleaners, simple web-scraper",
                "Small bug fixes, wiring helper functions, basic refactors"
            ],
            "TIER 3": [
                "CRUD REST API (Flask/FastAPI), small microservice, integrations",
                "Non-trivial automation/data pipeline, refactor modules into packages"
            ],
            "TIER 4": [
                "Production-ready backend with auth, caching, logging, tests",
                "Performance tuning, DB indexing, CI pipelines, containerization"
            ],
            "TIER 5": [
                "Highly scalable distributed services with observability and SLOs",
                "Complex domain modeling, deep refactors, bulletproof test suites"
            ]
        }

        print(f"\n[{current_tier}] {tier_info['LABEL']}")
        print(f"Your current coding skill is {skill_now}.")
        print("Example work:")
        for example in narratives.get(current_tier, []):
            print(f"- {example}")

        print(f"Calculation: STANDARD RATE ({standard}) + CODING SKILL ({skill_now}) * HOUR RATE ({hour_rate})")
        print(f"You received: {total_money} CZK")

        self.stats.increment_stats_value_money(total_money)
        self.activity_selected = True
        self.stats.get_stats_command()
        continue_prompt()

    def _perform_fiverr_lesson(self):
        """Logic for Option 2: Paying for a mentor."""
        cost = 2500

        if not self.stats.try_spend_money(cost):
            print(f"\n[INSUFFICIENT FUNDS] You need {cost} CZK. Current: {self.stats.available_money} CZK.")
            continue_prompt()
            return self.activity_python()

        activity_roll = randint(1, 100)

        if activity_roll <= 65:
            self.stats.increment_stats_coding_skill(10)
            print("\nYou jump on a call with a mid-level developer from Fiverr.")
            print("He's practical. He shows you how to structure your files and fixes bad habits.")
            Interaction.show_outcome(f"- {cost} CZK, + 10 CODING SKILLS")

        elif activity_roll <= 90:
            self.stats.increment_stats_coding_skill(15)
            print("\nYou luck out. Your tutor is sharp as hell.")
            print("They explain OOP in a way that finally clicks with your brain.")
            Interaction.show_outcome(f"- {cost} CZK, + 15 CODING SKILLS")

        else:
            self.stats.increment_stats_coding_skill(25)
            print("\nYou accidentally booked a beast. Senior dev, ten years in the field.")
            print("Code review, patterns, mental models. This was a paradigm shift.")
            Interaction.show_outcome(f"- {cost} CZK, + 25 CODING SKILLS")

        self.stats.get_stats_command()
        continue_prompt()
        self.activity_selected = True

    def _perform_bootcamp_enrollment(self):
        """Logic for Option 3: Joining Bootcamp."""
        cost = 35000

        # 1. Check funds first.
        # It is annoying to be asked "Do you want to buy?" and then told "You are too poor."
        if self.stats.available_money < cost:
            print(f"\n[INSUFFICIENT FUNDS] You need {cost} CZK. Transaction Declined.")
            print("That is a lot of money. Maybe stick to free docs for now?")
            continue_prompt()
            return self.activity_python()

        # 2. Confirmation Step
        print(f"\n[CONFIRMATION REQUIRED]")
        print(f"The bootcamp costs {cost} CZK. This is a massive investment.")
        print("Do you really want to spend this amount?")
        print("1. YES (Sign the contract)")
        print("2. NO (I changed my mind)")

        confirm = Interaction.ask(("1", "2"))

        if confirm == "2":
            print("\nYou step back. It's too much money right now.")
            continue_prompt()
            return self.activity_python()

        # 3. Process Transaction
        # We already checked funds above, so try_spend_money will return True.
        self.stats.try_spend_money(cost)

        print("\nYou sign a contract and pay for an on-line Python bootcamp.")
        print("Deadlines, assignments, code reviews. The full package.")
        print("This is no longer a hobby. This is a commitment.")
        Interaction.show_outcome(f"- {cost} CZK, [BOOTCAMP BUFF ACTIVATED]")

        self.python_bootcamp = True
        self.stats.get_stats_command()
        continue_prompt()
        self.activity_selected = True

    def activity_python(self):
        """Main Menu for Python Activity."""
        # Check if activity is already done for the day
        if self.activity_selected:
            print("\nYou already did your daily activity today.")
            return self.main_menu()

        current_tier, tier_info = self.get_coding_tier_info()
        tier_display = (f"{current_tier} | SKILL: {tier_info['CODING SKILL']} | "
                        f"BASE: {tier_info['STANDARD RATE']} | HOURLY: {tier_info['HOUR RATE']}")

        # Create coding activity menu with styling
        coding_text = Text()
        coding_text.append("There are multiple ways for you how to study Python.\n", style="bold white")
        coding_text.append("Python is now your Dojo, coding is your life!\n", style="bold bright_cyan")
        coding_text.append("═" * 50 + "\n", style="dim white")
        
        # Option 1: Code for Money
        coding_text.append("\n[1] ", style="bold cyan")
        coding_text.append("CODE FOR MONEY $$$", style="bold bright_white")
        coding_text.append(f"\n   [{tier_display}]", style="dim yellow")
        
        # Option 2: Fiverr
        coding_text.append("\n\n[2] ", style="bold cyan")
        coding_text.append("BUY A STUDY SESSION ON FIVERR", style="bold bright_white")
        coding_text.append("\n   [2500 CZK]", style="dim yellow")
        
        valid_choices = ["0", "1", "2"]
        
        # Dynamic options based on bootcamp status
        if not self.python_bootcamp:
            # Scenario A: Bootcamp NOT bought yet
            coding_text.append("\n\n[3] ", style="bold cyan")
            coding_text.append("JOIN AN ON-LINE BOOTCAMP", style="bold bright_white")
            coding_text.append("\n   [35000 CZK]", style="dim yellow")
            
            coding_text.append("\n\n[4] ", style="bold cyan")
            coding_text.append("⬅️  RETURN TO MENU", style="bold bright_white")
            
            valid_choices.extend(["3", "4"])
        else:
            # Scenario B: Bootcamp ALREADY bought
            coding_text.append("\n\n[3] ", style="bold cyan")
            coding_text.append("⬅️  RETURN TO MENU", style="bold bright_white")
            valid_choices.append("3")
        
        # Option 0: View tier details
        coding_text.append("\n\n[0] ", style="bold cyan")
        coding_text.append("VIEW CURRENT TIER DETAILS", style="bold bright_white")
        
        coding_text.append("\n\n" + "═" * 50, style="dim white")
        
        # Display in a styled panel
        print("\n")
        print(Panel(
            coding_text,
            border_style="bold cyan",
            title="[bold white on cyan] > CODING ACTIVITY < [/]",
            padding=(1, 3),
            expand=False
        ))

        # 4. Handle Input
        choice = Interaction.ask(tuple(valid_choices))

        if choice == "0":
            tier_info_text = Text()
            tier_info_text.append(f"{tier_display}", style="bold bright_white")
            
            print("\n")
            print(Panel(
                tier_info_text,
                border_style="bold cyan",
                title="[bold white on cyan] > CURRENT TIER < [/]",
                padding=(1, 3),
                expand=False
            ))
            print()
            continue_prompt()
            return self.activity_python()  # Reload menu

        elif choice == "1":
            self._perform_coding_work()

        elif choice == "2":
            self._perform_fiverr_lesson()

        elif choice == "3":
            if not self.python_bootcamp:
                # If not bought, 3 is Enroll
                self._perform_bootcamp_enrollment()
            else:
                # If bought, 3 is Return to Menu
                self.main_menu()

        elif choice == "4":
            # Only exists if not bought (Scenario A)
            self.main_menu()
