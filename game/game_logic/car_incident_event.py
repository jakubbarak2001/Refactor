"""
Module representing the Car Incident Event.
Contains ALL logic, text, and outcomes for this specific story arc.
Refactored for High Cohesion, Dark Humor, and Better Balancing.
"""
from random import randint

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

        CarIncident._play_intro_scene() with dissolve

        # Difficulty tag for the MacGyver choice
        difficulty_tag = Interaction.get_difficulty_tag(CarIncident.macgyver_odds)

        Interaction.print_text(
            "\nYou stand between the cars. The silence of the parking lot is heavy.\n"
            "You have a split second decision to make before a colleague walks out with a cigarette.",
            character="jb",
            expression="worried",
            bg="parking_lot"
        )
        
        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision(
            [
                ("1", difficulty_tag, "THE 'MACGYVER' MANEUVER. Try to buff out the scratch with spit and your sleeve. If it works, you saw nothing."),
                ("2", Interaction.get_difficulty_tag(), "THE 'GOOD SOLDIER'. Go inside, report it, fill out the forms, and accept the humiliation.")
            ],
            character="jb",
            expression="worried",
            bg="parking_lot"
        )

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
        Interaction.print_text(
            "\nIt is 06:45 AM. The sun is technically rising, but in this part of Bohemia, "
            "it just looks like the sky is slowly bruising purple.\n"
            "You just parked your private car. You are already late for the overtime shift at the other station.\n"
            "Your brain is running on 3 hours of sleep and a protein bar that tasted like chalk.",
            character="jb",
            expression="neutral",
            bg="parking_lot",
            wait_for_input=False
        )
        continue_prompt(character="jb", expression="neutral", bg="parking_lot")
        Interaction.print_text(
            "You rush to the service vehicle—a battered Octavia that smells permanently of wet dog and criminals.\n"
            "You throw it into reverse, trusting your muscle memory more than your eyes.\n"
            "You are a professional driver, right? You did the course.",
            character="jb",
            expression="neutral",
            bg="parking_lot",
            wait_for_input=False
        )
        continue_prompt(character="jb", expression="neutral", bg="parking_lot")
        Interaction.print_text(
            "It wasn't a loud noise. It was a sickeningly polite *crunch*.\n"
            "Like stepping on a very large, very expensive beetle.\n"
            "You freeze. You look in the mirror. You see nothing."
            "\n\nYou get out. You look."
            "\n\nYour bumper is intimately kissing the door of the Commandant's brand new Superb."
            "\nIt's not just a scratch. It's a statement.",
            character="jb",
            expression="worried",
            bg="parking_lot",
            animated=True,
            animation_delay=0.03,
            wait_for_input=False
        )
        continue_prompt(character="jb", expression="worried", bg="parking_lot")

    @staticmethod
    def _path_confession(stats: Stats):
        """
        The Safe Path. Guaranteed loss of money/pride, but no risk of disaster.
        """
        # Decision moment
        Interaction.print_text(
            "You sigh. You are an adult. You take responsibility.\n"
            "You walk inside, find the shift commander, and tell him.",
            character="jb",
            expression="bored",
            bg="police_station_interior",
            animated=True,
            animation_delay=0.03,
            wait_for_input=False
        )
        continue_prompt(character="jb", expression="bored", bg="police_station_interior")

        # The confrontation
        Interaction.print_text(
            "He looks at you over his glasses. Then at the clock. Then back at you.\n\n"
            "'Great start to the morning, JB. Really stellar performance.'",
            character="jb",
            expression="bored",
            bg="police_station_interior",
            animated=True,
            animation_delay=0.03
        )
        
        # The paperwork
        Interaction.print_text(
            "He hands you a stack of papers thick enough to kill a rat.\n\n"
            "'Fill these out. Insurance will cover most of it, but you're paying the deductible.'\n"
            "'And don't expect a Christmas bonus.'",
            character="jb",
            expression="bored",
            bg="police_station_interior"
        )

        stats.increment_stats_pcr_hatred(10)
        stats.increment_stats_value_money(- 2000)

        Interaction.show_outcome(
            "-2.000 CZK (Deductible), - 10 PCR HATRED (Humiliation).",
            character="jb",
            expression="bored",
            bg="police_station_interior"
        )
        
        # Final thought
        final_text = "At least it's over. No lawyers. No Colonel. Just pure, unadulterated bureaucracy."
        Interaction.print_text(
            final_text,
            character="jb",
            expression="bored",
            bg="police_station_interior"
        )

    @staticmethod
    def _path_cover_up(stats: Stats):
        """
        The Risk Path. 50/50 Chance.
        """
        # Initial attempt - tense moment
        attempt_text = Text()
        attempt_text.append("You look around. The parking lot is empty.\n", style="white")
        Interaction.print_text(
            "You lick your thumb and furiously rub the scratch on the Superb.\n"
            "It's not working. In fact, you're pretty sure you just made it shinier.",
            character="jb",
            expression="worried",
            bg="parking_lot",
            animated=True,
            animation_delay=0.03
        )

        roll = randint(1, 100)

        if roll <= 50:
            # Success - dramatic reveal
            success_text = Text()
            success_text.append("Wait... ", style="white")
            success_text.append("it's just paint transfer!", style="bold bright_green")
            
            Interaction.print_text(
                "You spit on your sleeve and scrub harder.\n"
                "The white mark disappears.\n\n"
                "There is a tiny dent left, but you'd have to look for it with a microscope.",
                character="jb",
                expression="determined",
                bg="parking_lot",
                animated=True,
                animation_delay=0.03
            )
            
            # The escape
            Interaction.print_text(
                "You jump into your car and drive away, heart pounding.\n\n"
                "You got away with it. You magnificent bastard.",
                character="jb",
                expression="determined",
                bg="parking_lot"
            )

            stats.increment_stats_pcr_hatred(-5)
            Interaction.show_outcome(
                "0 CZK LOST, -5 PCR HATRED (The thrill of crime).",
                character="jb",
                expression="determined",
                bg="parking_lot"
            )

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
        Interaction.print_text(
            "'HEY! WHAT ARE YOU DOING?!'",
            character="jb",
            expression="worried",
            bg="parking_lot",
            animated=True,
            animation_delay=0.02
        )
        
        Interaction.print_text(
            "You freeze. You turn around.\n\n"
            "It's not a colleague. It's the traffic camera you completely forgot about.\n"
            "And standing right under it is the Shift Commander, holding his morning coffee, watching you.",
            character="jb",
            expression="worried",
            bg="parking_lot",
            wait_for_input=False
        )
        continue_prompt(character="jb", expression="worried", bg="parking_lot")

        # The Colonel arrives
        Interaction.print_text(
            "Fast forward 2 hours. The Colonel has arrived at the station and is waiting for you in his office.",
            character="colonel",
            expression="angry",
            bg="police_station_office",
            animated=True,
            animation_delay=0.03
        )
        
        # The accusation
        Interaction.print_text(
            "He is angry. He is disappointed. He is disappointed in you. It's all your fault.\n\n"
            "'JB, you are a disgrace to the badge. You are a disgrace to the department. What were you thinking?'",
            character="colonel",
            expression="angry",
            bg="police_station_office",
            animated=True,
            animation_delay=0.03
        )
        
        # The charge
        Interaction.print_text(
            "They aren't calling it an accident. They are calling it 'Leaving the scene of a traffic incident'.\n\n"
            "That's a crime. That's 'Lose your badge' territory.",
            character="colonel",
            expression="angry",
            bg="police_station_office",
            animated=True,
            animation_delay=0.03
        )
        
        # The ultimatum
        Interaction.print_text(
            "The Boss slides a piece of paper across the table.\n\n"
            "'Sign this admission of guilt. Pay the full damages and we forget the disciplinary charge.'",
            character="colonel",
            expression="angry",
            bg="police_station_office"
        )

        # Display decision using Rich Panel with difficulty tags
        choice = Interaction.show_decision(
            [
                ("1", Interaction.get_difficulty_tag(), "SUBMIT. Pay the money. Eat the dirt. Keep your job."),
                ("2", difficulty_tag, "CALL PAUL GOODMAN. Sue the department. Burn the bridge.")
            ],
            character="colonel",
            expression="angry",
            bg="police_station_office"
        )

        if choice == "1":
            stats.increment_stats_pcr_hatred(25)
            stats.increment_stats_value_money(-8000)
            
            # The submission
            Interaction.print_text(
                "You sign the paper.",
                character="jb",
                expression="bored",
                bg="police_station_office"
            )
            Interaction.print_text(
                "Your hand is shaking.\n\n"
                "You walk out 8.000 CZK poorer and with a hatred for this place that burns like acid.",
                character="jb",
                expression="bored",
                bg="police_station_office"
            )
            
            Interaction.show_outcome(
                "-8.000 CZK, + 25 PCR HATRED.",
                character="jb",
                expression="bored",
                bg="police_station_office"
            )

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
        Interaction.print_text(
            "'No. I'm calling my lawyer.'",
            character="jb",
            expression="determined",
            bg="police_station_office",
            animated=True,
            animation_delay=0.03
        )
        
        Interaction.print_text(
            "The Boss laughs. 'Lawyer? JB, you can't afford a lawyer.'\n\n"
            "'You clearly have not heard of Paul Goodman,' you reply.",
            character="jb",
            expression="determined",
            bg="police_station_office"
        )
        continue_prompt(character="jb", expression="determined", bg="police_station_office")

        # The call
        Interaction.print_text(
            "You call Paul. He answers on the first ring.\n\n"
            "'Did you say Police Department? Discrimination? Emotional distress? Say no more.'\n\n"
            "'I'll take the case Pro Bono. We go to war.'",
            character="jb",
            expression="determined",
            bg="police_station_office",
            wait_for_input=False
        )
        continue_prompt(character="jb", expression="determined", bg="police_station_office")

        win_roll = randint(1, 100)

        if win_roll <= 50:
            # Paul wins
            Interaction.print_text(
                "Paul Goodman is a shark in a cheap suit.\n"
                "He found a loophole in the parking lot regulations.\n\n"
                "He threatened to sue the Colonel for 'Unsafe Workplace Environment'.\n"
                "The Department settled to make him go away.",
                character="jb",
                expression="determined",
                bg="police_station_office",
                animated=True,
                animation_delay=0.03
            )

            payout = 15000
            stats.increment_stats_value_money(payout)
            stats.increment_stats_pcr_hatred(-30)

            Interaction.print_text(
                f"[CRITICAL SUCCESS]: You received a settlement of {payout:,} CZK!\n\n"
                "Your boss refuses to make eye contact with you.",
                character="jb",
                expression="determined",
                bg="police_station_office"
            )
            
            Interaction.show_outcome(
                "+ 15.000 CZK, -30 PCR HATRED (Justice tastes sweet).",
                character="jb",
                expression="determined",
                bg="police_station_office"
            )

        else:
            # Paul loses
            Interaction.print_text(
                "The Colonel called in a favor.\n"
                "The judge was his old drinking buddy.\n\n"
                "Paul Goodman got held in contempt of court for wearing a neon tie.\n\n"
                "You lost. Badly.",
                character="colonel",
                expression="angry",
                bg="police_station_office",
                animated=True,
                animation_delay=0.03
            )

            court_fees = 12000
            stats.increment_stats_value_money(-court_fees)
            stats.increment_stats_pcr_hatred(50)

            Interaction.print_text(
                f"[CRITICAL FAILURE]: You have to pay court fees of {court_fees:,} CZK.\n\n"
                "The entire station is laughing at you. The Colonel sends you a 'Get Well Soon' card.",
                character="colonel",
                expression="angry",
                bg="police_station_office"
            )
            
            Interaction.show_outcome(
                "-12.000 CZK, +50 PCR HATRED (Maximum Salt).",
                character="colonel",
                expression="angry",
                bg="police_station_office"
            )

    @staticmethod
    def _display_grind_objective():
        """
        Displays a unified panel combining the debuff message and main objective.
        Uses Rich TUI with emojis for visual appeal.
        """
        objective_text = Text()
        objective_text = (
            "FROM THIS MOMENT, THE GRIND BEGINS\n\n"
            "⚠️ DEBUFF: You will gain +5 PCR 😡 HATRED daily.\n\n"
            "🎯 MAIN OBJECTIVE: In the next 30 days, you need to become a 💻 FULLSTACK DEVELOPER."
        )
        Interaction.print_text(
            objective_text,
            character="jb",
            expression="determined",
            bg="police_station_interior"
        )
