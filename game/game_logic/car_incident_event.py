"""
Module representing the Car Incident Event.
Contains ALL logic, text, and outcomes for this specific story arc.
Refactored for High Cohesion, Dark Humor, and Better Balancing.
"""
from random import randint
import time

from rich import print
from rich.panel import Panel
from rich.text import Text

from game.game_logic.interaction import Interaction
from game.game_logic.press_enter_to_continue import continue_prompt
from game.game_logic.stats import Stats
from game.game_logic.story import Arc


class CarIncident:
    """
    Encapsulates the entire Car Incident story arc.
    """
    # Odds for the MacGyver and Paul Goodman choices
    macgyver_odds = 50
    paul_goodman_odds = 50

    @staticmethod
    def car_incident_event(stats: Stats) -> None:
        """The main entry point for this event."""

        Arc.display_arc_title("I", "THE INCIDENT", border_color="red")

        CarIncident._play_intro_scene()

        # Difficulty tag for the MacGyver choice
        difficulty_tag = Interaction.get_difficulty_tag(CarIncident.macgyver_odds)

        print("\nYou stand between the cars. The silence of the parking lot is heavy.")
        print("You have a split second decision to make before a colleague walks out with a cigarette.")
        
        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision([
            ("1", difficulty_tag, "THE 'MACGYVER' MANEUVER. Try to buff out the scratch with spit and your sleeve. If it works, you saw nothing."),
            ("2", Interaction.get_difficulty_tag(), "THE 'GOOD SOLDIER'. Go inside, report it, fill out the forms, and accept the humiliation.")
        ])

        # Handle the choice
        if choice == "1":
            CarIncident._path_cover_up(stats)
        else:
            CarIncident._path_confession(stats)

        # Unified debuff + objective panel
        CarIncident._display_grind_objective()
        continue_prompt()

    @staticmethod
    def _play_intro_scene():
        """Handles the text intro with updated text."""
        print(
            "\nIt is 06:45 AM. The sun is technically rising, but in this part of Bohemia, "
            "it just looks like the sky is slowly bruising purple.\n"
            "You just parked your private car. You are already late for the overtime shift at the other station.\n"
            "Your brain is running on 3 hours of sleep and a protein bar that tasted like chalk."
        )
        continue_prompt()
        print(
            "You rush to the service vehicle—a battered Octavia that smells permanently of wet dog and criminals.\n"
            "You throw it into reverse, trusting your muscle memory more than your eyes.\n"
            "You are a professional driver, right? You did the course."
        )
        continue_prompt()
        print(
            "It wasn't a loud noise. It was a sickeningly polite [bold]*crunch*[/bold].\n"
            "Like stepping on a very large, very expensive beetle.\n"
            "You freeze. You look in the mirror. You see nothing."
            "\n\nYou get out. You look."
            "\n\nYour bumper is intimately kissing the door of the Commandant's brand new Superb."
            "\nIt's not just a scratch. It's a statement."
        )

    @staticmethod
    def _path_confession(stats: Stats):
        """
        The Safe Path. Guaranteed loss of money/pride, but no risk of disaster.
        """
        # Decision moment
        decision_text = Text()
        decision_text.append("You sigh. You are an adult. You take responsibility.\n", style="white")
        decision_text.append("You walk inside, find the shift commander, and tell him.", style="white")
        
        print("\n")
        print(Panel(
            decision_text,
            border_style="bold yellow",
            title="[bold white on yellow] > THE DECISION < [/]",
            padding=(1, 2),
            expand=False
        ))
        time.sleep(1.5)
        continue_prompt()

        # The confrontation
        confrontation_text = Text()
        confrontation_text.append("He looks at you over his glasses. ", style="white")
        confrontation_text.append("Then at the clock. ", style="dim white")
        confrontation_text.append("Then back at you.\n", style="white")
        confrontation_text.append("\n", style="")
        confrontation_text.append("'Great start to the morning, JB. ", style="white")
        confrontation_text.append("Really stellar performance.'", style="bold bright_red")
        
        print("\n")
        print(Panel(
            confrontation_text,
            border_style="bold red",
            padding=(1, 2),
            expand=False
        ))
        time.sleep(1.5)
        
        # The paperwork
        paperwork_text = Text()
        paperwork_text.append("He hands you a stack of papers ", style="white")
        paperwork_text.append("thick enough to kill a rat", style="bold white")
        paperwork_text.append(".\n", style="white")
        paperwork_text.append("\n", style="")
        paperwork_text.append("'Fill these out. Insurance will cover most of it, ", style="white")
        paperwork_text.append("but you're paying the deductible.'\n", style="bold yellow")
        paperwork_text.append("'And don't expect a Christmas bonus.'", style="dim white")
        
        print("\n")
        print(Panel(
            paperwork_text,
            border_style="bold yellow",
            title="[bold white on yellow] > THE COST < [/]",
            padding=(1, 2),
            expand=False
        ))

        stats.increment_stats_pcr_hatred(10)
        stats.increment_stats_value_money(- 2000)

        Interaction.show_outcome("-2.000 CZK (Deductible), - 10 PCR HATRED (Humiliation).")
        
        # Final thought
        final_text = Text()
        final_text.append("At least it's over. ", style="dim white")
        final_text.append("No lawyers. ", style="dim white")
        final_text.append(Interaction.format_colonel_text("No Colonel. "), style="dim white")
        final_text.append("Just pure, unadulterated bureaucracy.", style="dim white")
        
        print("\n")
        print(Panel(
            final_text,
            border_style="dim white",
            padding=(1, 2),
            expand=False
        ))

    @staticmethod
    def _path_cover_up(stats: Stats):
        """
        The Risk Path. 50/50 Chance.
        """
        # Initial attempt - tense moment
        attempt_text = Text()
        attempt_text.append("You look around. The parking lot is empty.\n", style="white")
        attempt_text.append("You lick your thumb and furiously rub the scratch on the Superb.\n", style="white")
        attempt_text.append("It's not working. In fact, you're pretty sure you just made it shinier.", style="dim white")
        
        print(Panel(
            attempt_text,
            border_style="bold yellow",
            title="[bold white on yellow] > THE ATTEMPT < [/]",
            padding=(1, 2),
            expand=False
        ))
        time.sleep(1.5)

        roll = randint(1, 100)

        if roll <= 50:
            # Success - dramatic reveal
            success_text = Text()
            success_text.append("Wait... ", style="white")
            success_text.append("it's just paint transfer!", style="bold bright_green")
            
            print("\n")
            print(Panel(
                success_text,
                border_style="bold bright_green",
                padding=(1, 2),
                expand=False
            ))
            time.sleep(1)
            
            # The fix
            fix_text = Text()
            fix_text.append("You spit on your sleeve and scrub harder.\n", style="white")
            fix_text.append("The white mark ", style="white")
            fix_text.append("disappears", style="bold bright_green")
            fix_text.append(".", style="white")
            fix_text.append("\n\nThere is a tiny dent left, but you'd have to look for it with a microscope.", style="dim white")
            
            print(Panel(
                fix_text,
                border_style="bold green",
                padding=(1, 2),
                expand=False
            ))
            time.sleep(1.5)
            
            # The escape
            escape_text = Text()
            escape_text.append("You jump into your car and drive away, ", style="white")
            escape_text.append("heart pounding", style="bold bright_red")
            escape_text.append(".", style="white")
            escape_text.append("\n\n", style="")
            escape_text.append("You got away with it. ", style="bold white")
            escape_text.append("You magnificent bastard.", style="bold bright_green")
            
            print("\n")
            print(Panel(
                escape_text,
                border_style="bold bright_green",
                title="[bold white on bright_green] > SUCCESS < [/]",
                padding=(1, 2),
                expand=False
            ))

            stats.increment_stats_pcr_hatred(-5)
            Interaction.show_outcome("0 CZK LOST, -5 PCR HATRED (The thrill of crime).")

        else:
            CarIncident._scenario_caught_red_handed(stats)

    @staticmethod
    def _scenario_caught_red_handed(stats: Stats):
        """
        The disaster scenario leading to the Paul Goodman / Colonel choice.
        """

        # Choice 2 uses paul_goodman_odds
        difficulty_tag = Interaction.get_difficulty_tag(CarIncident.paul_goodman_odds)

        # The discovery
        discovery_text = Text()
        discovery_text.append("'HEY! WHAT ARE YOU DOING?!'", style="bold bright_red")
        
        print("\n")
        print(Panel(
            discovery_text,
            border_style="bold bright_red",
            padding=(1, 2),
            expand=False
        ))
        time.sleep(1)
        
        caught_text = Text()
        caught_text.append("You freeze. You turn around.\n", style="white")
        caught_text.append("\n", style="")
        caught_text.append("It's not a colleague. ", style="white")
        caught_text.append("It's the traffic camera you completely forgot about", style="bold bright_red")
        caught_text.append(".\n", style="white")
        caught_text.append("And standing right under it is the Shift Commander, ", style="white")
        caught_text.append("holding his morning coffee, watching you", style="bold bright_red")
        caught_text.append(".", style="white")
        
        print("\n")
        print(Panel(
            caught_text,
            border_style="bold red",
            title="[bold white on red] > CAUGHT < [/]",
            padding=(1, 2),
            expand=False
        ))
        continue_prompt()

        # The Colonel arrives
        colonel_arrival_text = Text()
        colonel_arrival_text.append(Interaction.format_colonel_text("Fast forward 2 hours. The Colonel has arrived at the station and is waiting for you in his office."), style="white")
        
        print("\n")
        print(Panel(
            colonel_arrival_text,
            border_style="bold dark_blue",
            padding=(1, 2),
            expand=False
        ))
        time.sleep(1.5)
        
        # The accusation
        accusation_text = Text()
        accusation_text.append("He is angry. ", style="white")
        accusation_text.append("He is disappointed. ", style="bold bright_red")
        accusation_text.append("He is disappointed in ", style="white")
        accusation_text.append("you", style="bold bright_red")
        accusation_text.append(". It's all your fault.\n", style="white")
        accusation_text.append("\n", style="")
        accusation_text.append("'JB, you are a disgrace to the badge. ", style="white")
        accusation_text.append("You are a disgrace to the department.", style="bold bright_red")
        accusation_text.append(" What were you thinking?.'", style="white")
        
        print("\n")
        print(Panel(
            accusation_text,
            border_style="bold red",
            padding=(1, 2),
            expand=False
        ))
        time.sleep(1.5)
        
        # The charge
        charge_text = Text()
        charge_text.append("They aren't calling it an accident. ", style="white")
        charge_text.append("They are calling it ", style="white")
        charge_text.append("'Leaving the scene of a traffic incident'", style="bold bright_red")
        charge_text.append(".\n", style="white")
        charge_text.append("\n", style="")
        charge_text.append("That's a crime. ", style="bold white")
        charge_text.append("That's 'Lose your badge' territory.", style="bold bright_red")
        
        print("\n")
        print(Panel(
            charge_text,
            border_style="bold bright_red",
            title="[bold white on bright_red] > THE CHARGE < [/]",
            padding=(1, 2),
            expand=False
        ))
        time.sleep(1.5)
        
        # The ultimatum
        ultimatum_text = Text()
        ultimatum_text.append("The Boss slides a piece of paper across the table.\n", style="white")
        ultimatum_text.append("\n", style="")
        ultimatum_text.append("'Sign this admission of guilt. ", style="white")
        ultimatum_text.append("Pay the full damages ", style="bold yellow")
        ultimatum_text.append("and we forget the disciplinary charge.'", style="white")
        
        print("\n")
        print(Panel(
            ultimatum_text,
            border_style="bold yellow",
            title="[bold white on yellow] > THE ULTIMATUM < [/]",
            padding=(1, 2),
            expand=False
        ))

        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "SUBMIT. Pay the money. Eat the dirt. Keep your job."),
            ("2", difficulty_tag, "CALL PAUL GOODMAN. Sue the department. Burn the bridge.")
        ])

        if choice == "1":
            stats.increment_stats_pcr_hatred(25)
            stats.increment_stats_value_money(-8000)
            
            # The submission
            submission_text = Text()
            submission_text.append("You sign the paper. ", style="white")
            submission_text.append("Your hand is shaking", style="bold bright_red")
            submission_text.append(".\n", style="white")
            submission_text.append("\n", style="")
            submission_text.append("You walk out ", style="white")
            submission_text.append("8.000 CZK poorer", style="bold yellow")
            submission_text.append(" and with a hatred for this place that ", style="white")
            submission_text.append("burns like acid", style="bold bright_red")
            submission_text.append(".", style="white")
            
            print("\n")
            print(Panel(
                submission_text,
                border_style="bold red",
                title="[bold white on red] > SUBMISSION < [/]",
                padding=(1, 2),
                expand=False
            ))
            
            Interaction.show_outcome("-8.000 CZK, + 25 PCR HATRED.")

        elif choice == "2":
            CarIncident._scenario_better_call_paul(stats)

    @staticmethod
    def _scenario_better_call_paul(stats: Stats):
        """
        The High Stakes Gambler Path.
        """
        # The defiance
        defiance_text = Text()
        defiance_text.append("You look the Boss in the eye and push the paper back.\n", style="white")
        defiance_text.append("\n", style="")
        defiance_text.append("'No. ", style="bold white")
        defiance_text.append("I'm calling my lawyer.'", style="bold bright_green")
        
        print("\n")
        print(Panel(
            defiance_text,
            border_style="bold bright_green",
            title="[bold white on bright_green] > DEFIANCE < [/]",
            padding=(1, 2),
            expand=False
        ))
        time.sleep(1.5)
        
        boss_response_text = Text()
        boss_response_text.append("The Boss laughs. ", style="white")
        boss_response_text.append("'Lawyer? JB, you can't afford a lawyer.'\n", style="bold bright_red")
        boss_response_text.append("\n", style="")
        boss_response_text.append("'You clearly have not heard of ", style="white")
        boss_response_text.append("Paul Goodman", style="bold bright_green")
        boss_response_text.append(",' you reply.", style="white")
        
        print("\n")
        print(Panel(
            boss_response_text,
            border_style="bold yellow",
            padding=(1, 2),
            expand=False
        ))
        continue_prompt()

        # The call
        call_text = Text()
        call_text.append("You call Paul. ", style="white")
        call_text.append("He answers on the first ring", style="bold bright_green")
        call_text.append(".\n", style="white")
        call_text.append("\n", style="")
        call_text.append("'Did you say Police Department? ", style="white")
        call_text.append("Discrimination? Emotional distress?", style="bold bright_green")
        call_text.append(" Say no more.'\n", style="white")
        call_text.append("\n", style="")
        call_text.append("'I'll take the case Pro Bono. ", style="bold bright_green")
        call_text.append("We go to war.'", style="bold bright_red")
        
        print("\n")
        print(Panel(
            call_text,
            border_style="bold bright_green",
            title="[bold white on bright_green] > THE CALL < [/]",
            padding=(1, 2),
            expand=False
        ))
        continue_prompt()

        win_roll = randint(1, 100)

        if win_roll <= 50:
            # Paul wins
            paul_win_text = Text()
            paul_win_text.append("Paul Goodman is a shark in a cheap suit.\n", style="white")
            paul_win_text.append("He found a loophole in the parking lot regulations.\n", style="bold bright_green")
            paul_win_text.append("\n", style="")
            paul_win_text.append(Interaction.format_colonel_text("He threatened to sue the Colonel for 'Unsafe Workplace Environment'."), style="white")
            paul_win_text.append("\n", style="")
            paul_win_text.append("The Department settled to make him go away.", style="bold bright_green")
            
            print("\n")
            print(Panel(
                paul_win_text,
                border_style="bold bright_green",
                padding=(1, 2),
                expand=False
            ))
            time.sleep(1.5)

            payout = 15000
            stats.increment_stats_value_money(payout)
            stats.increment_stats_pcr_hatred(-30)

            victory_text = Text()
            victory_text.append("[CRITICAL SUCCESS]: ", style="bold bright_green")
            victory_text.append(f"You received a settlement of {payout:,} CZK!", style="bold white")
            victory_text.append("\n\n", style="")
            victory_text.append("Your boss refuses to make eye contact with you.", style="dim white")
            
            print("\n")
            print(Panel(
                victory_text,
                border_style="bold bright_green",
                title="[bold white on bright_green] > VICTORY < [/]",
                padding=(1, 2),
                expand=False
            ))
            
            Interaction.show_outcome("+ 15.000 CZK, -30 PCR HATRED (Justice tastes sweet).")

        else:
            # Paul loses
            paul_loss_text = Text()
            paul_loss_text.append(Interaction.format_colonel_text("The Colonel called in a favor."), style="white")
            paul_loss_text.append("\n", style="")
            paul_loss_text.append("The judge was his old drinking buddy.\n", style="bold bright_red")
            paul_loss_text.append("\n", style="")
            paul_loss_text.append("Paul Goodman got held in contempt of court ", style="white")
            paul_loss_text.append("for wearing a neon tie", style="bold bright_red")
            paul_loss_text.append(".\n", style="white")
            paul_loss_text.append("\n", style="")
            paul_loss_text.append("You lost. ", style="white")
            paul_loss_text.append("Badly.", style="bold bright_red")
            
            print("\n")
            print(Panel(
                paul_loss_text,
                border_style="bold bright_red",
                title="[bold white on bright_red] > DEFEAT < [/]",
                padding=(1, 2),
                expand=False
            ))
            time.sleep(1.5)

            court_fees = 12000
            stats.increment_stats_value_money(-court_fees)
            stats.increment_stats_pcr_hatred(50)

            failure_text = Text()
            failure_text.append("[CRITICAL FAILURE]: ", style="bold bright_red")
            failure_text.append(f"You have to pay court fees of {court_fees:,} CZK.", style="bold white")
            failure_text.append("\n\n", style="")
            failure_text.append(Interaction.format_colonel_text("The entire station is laughing at you. The Colonel sends you a 'Get Well Soon' card."), style="dim white")
            
            print("\n")
            print(Panel(
                failure_text,
                border_style="bold bright_red",
                padding=(1, 2),
                expand=False
            ))
            
            Interaction.show_outcome("-12.000 CZK, +50 PCR HATRED (Maximum Salt).")

    @staticmethod
    def _display_grind_objective():
        """
        Displays a unified panel combining the debuff message and main objective.
        Uses Rich TUI with emojis for visual appeal.
        """
        objective_text = Text()
        objective_text.append("FROM THIS MOMENT, THE GRIND BEGINS\n", style="bold white")
        objective_text.append("\n", style="")
        objective_text.append("⚠️  ", style="bold bright_red")
        objective_text.append("DEBUFF: ", style="bold bright_red")
        objective_text.append("You will gain ", style="white")
        objective_text.append("+5 PCR ", style="bold bright_red")
        objective_text.append("😡 HATRED", style="bold bright_red")
        objective_text.append(" daily.\n", style="white")
        objective_text.append("\n", style="")
        objective_text.append("🎯 ", style="bold bright_green")
        objective_text.append("MAIN OBJECTIVE: ", style="bold bright_green")
        objective_text.append("In the next 30 days, you need to become a ", style="white")
        objective_text.append("💻 FULLSTACK DEVELOPER", style="bold bright_green")
        objective_text.append(".", style="white")
        
        print("\n")
        print(Panel(
            objective_text,
            border_style="bold bright_red",
            title="[bold white on bright_red] > THE GRIND BEGINS < [/]",
            padding=(1, 3),
            expand=False
        ))
