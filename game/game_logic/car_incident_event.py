"""
Module representing the Car Incident Event.
Contains ALL logic, text, and outcomes for this specific story arc.
Refactored for High Cohesion, Dark Humor, and Better Balancing.
"""
from random import randint

from rich import print

from game.game_logic.interaction import Interaction
from game.game_logic.press_enter_to_continue import continue_prompt
from game.game_logic.stats import Stats


class CarIncident:
    """
    Encapsulates the entire Car Incident story arc.
    """
    #
    macgyver_odds = 50
    paul_goodman_odds = 50

    @staticmethod
    def car_incident_event(stats: Stats) -> None:
        """The main entry point for this event."""

        print("[red]ARC I - THE INCIDENT[/red]")

        CarIncident._play_intro_scene()

        # Choice 1 uses macgyver_odds
        difficulty_tag = Interaction.get_difficulty_tag(CarIncident.macgyver_odds)

        print("\nYou stand between the cars. The silence of the parking lot is heavy.")
        print("You have a split second decision to make before a colleague walks out with a cigarette.")
        
        # Display decision using Rich Panel
        choice = Interaction.show_decision([
            ("1", difficulty_tag, "THE 'MACGYVER' MANEUVER. Try to buff out the scratch with spit and your sleeve. If it works, you saw nothing."),
            ("2", Interaction.get_difficulty_tag(), "THE 'GOOD SOLDIER'. Go inside, report it, fill out the forms, and accept the humiliation.")
        ])

        if choice == "1":
            CarIncident._path_cover_up(stats)
        else:
            CarIncident._path_confession(stats)

        print("\n[red]FROM THIS MOMENT, THE GRIND BEGINS[/red]: YOU WILL GAIN +5 PCR HATRED DAILY.")
        print("[green]YOUR MAIN OBJECTIVE[/green]: IN NEXT 30 DAYS, YOU NEED TO BECOME A FULLSTACK DEVELOPER.")
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
        print("\nYou sigh. You are an adult. You take responsibility.")
        print("You walk inside, find the shift commander, and tell him.")

        continue_prompt()

        print(
            "He looks at you over his glasses. Then at the clock. Then back at you."
            "\n'Great start to the morning, JB. Really stellar performance.'"
            "\n\nHe hands you a stack of papers thick enough to kill a rat."
            "\n'Fill these out. Insurance will cover most of it, but you're paying the deductible.'"
            "\n'And don't expect a Christmas bonus.'"
        )

        stats.increment_stats_pcr_hatred(10)
        stats.increment_stats_value_money(- 2000)

        print("\n[OUTCOME]: -2.000 CZK (Deductible), - 10 PCR HATRED (Humiliation).")
        print("At least it's over. No lawyers. No Colonel. Just pure, unadulterated bureaucracy.")

    @staticmethod
    def _path_cover_up(stats: Stats):
        """
        The Risk Path. 50/50 Chance.
        """
        print("\nYou look around. The parking lot is empty.")
        print("You lick your thumb and furiously rub the scratch on the Superb.")
        print("It's not working. In fact, you're pretty sure you just made it shinier.")

        roll = randint(1, 100)

        if roll <= 50:
            print("\nWait... it's just paint transfer!")
            print("You spit on your sleeve and scrub harder. The white mark disappears.")
            print("There is a tiny dent left, but you'd have to look for it with a microscope.")
            print("\nYou jump into your car and drive away, heart pounding.")
            print("You got away with it. You magnificent bastard.")

            stats.increment_stats_pcr_hatred(-5)
            print("\n[OUTCOME]: 0 CZK LOST, -5 PCR HATRED (The thrill of crime).")

        else:
            CarIncident._scenario_caught_red_handed(stats)

    @staticmethod
    def _scenario_caught_red_handed(stats: Stats):
        """
        The disaster scenario leading to the Paul Goodman / Colonel choice.
        """

        # Choice 2 uses paul_goodman_odds
        difficulty_tag = Interaction.get_difficulty_tag(CarIncident.paul_goodman_odds)

        print(
            "\n'HEY! WHAT ARE YOU DOING?!'"
            "\n\nYou freeze. You turn around."
            "\nIt's not a colleague. It's the traffic camera you completely forgot about."
            "\nAnd standing right under it is the Shift Commander, holding his morning coffee, watching you."
        )
        continue_prompt()
        print(
            "\nFast forward 2 hours."
            "\nYou are in The Office. The air conditioning is humming."
            "\nThey aren't calling it an accident. They are calling it [bold]'Leaving the scene of a traffic incident'[/bold]."
            "\nThat's a crime. That's 'Lose your badge' territory."
        )
        print(
            "\nThe Boss slides a piece of paper across the table."
            "\n'Sign this admission of guilt. Pay the full damages (8.000 CZK). We forget the disciplinary charge.'"
            "\n'Or... you can fight it.'"
        )

        print(
            f"\n1. {Interaction.get_difficulty_tag()} SUBMIT. Pay the money. Eat the dirt. Keep your job.")
        print(f"2. {difficulty_tag} CALL PAUL GOODMAN. Sue the department. Burn the bridge.")

        choice = Interaction.ask(("1", "2"))

        if choice == "1":
            stats.increment_stats_pcr_hatred(25)
            stats.increment_stats_value_money(-8000)
            print("\nYou sign the paper. Your hand is shaking.")
            print("You walk out 8.000 CZK poorer and with a hatred for this place that burns like acid.")
            print("\n[OUTCOME]: -8.000 CZK, + 25 PCR HATRED.")

        elif choice == "2":
            CarIncident._scenario_better_call_paul(stats)

    @staticmethod
    def _scenario_better_call_paul(stats: Stats):
        """
        The High Stakes Gambler Path.
        """
        print(
            "\nYou look the Boss in the eye and push the paper back."
            "\n'No. Im calling my lawyer.'"
            "\nThe Boss laughs. 'Lawyer? JB, you can't afford a lawyer.'"
            "\nYou clearly have not heard of Paul Goodman,' you reply."
        )
        continue_prompt()

        print("You call Paul. He answers on the first ring.")
        print("'Did you say Police Department? Discrimination? Emotional distress? Say no more.'")
        print("'Ill take the case Pro Bono. We go to war.'")

        continue_prompt()

        win_roll = randint(1, 100)

        if win_roll <= 50:
            print("Paul Goodman is a shark in a cheap suit.")
            print("He found a loophole in the parking lot regulations.")
            print("He threatened to sue the Colonel for 'Unsafe Workplace Environment'.")
            print("The Department settled to make him go away.")

            payout = 15000
            stats.increment_stats_value_money(payout)
            stats.increment_stats_pcr_hatred(-30)

            print(f"\n[CRITICAL SUCCESS]: You received a settlement of {payout} CZK!")
            print("Your boss refuses to make eye contact with you.")
            print("[OUTCOME]: + 15.000 CZK, -30 PCR HATRED (Justice tastes sweet).")

        else:
            print("\nThe Colonel called in a favor.")
            print("The judge was his old drinking buddy.")
            print("Paul Goodman got held in contempt of court for wearing a neon tie.")
            print("You lost. Badly.")

            court_fees = 12000
            stats.increment_stats_value_money(-court_fees)
            stats.increment_stats_pcr_hatred(50)

            print(f"\n[CRITICAL FAILURE]: You have to pay court fees of {court_fees} CZK.")
            print("The entire station is laughing at you. The Colonel sends you a 'Get Well Soon' card.")
            print("[OUTCOME]: -12.000 CZK, +50 PCR HATRED (Maximum Salt).")
