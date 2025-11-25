"""Module used for representing the first major decision branch at the start of the game, regarding the car accident."""
from random import randint
from jb_dev_stats import JBStats
from jb_dev_decision import Decision
import jb_game.jb_dev_story as jb_story_module


class CarIncident:
    """Namespace for all logic of the car incident event."""

    @staticmethod
    def car_incident_event(stats: JBStats) -> None:
        """First introduction event to the game, with multiple choices."""
        story = jb_story_module.Story(stats)
        story.start_the_car_incident_event(stats)
        CarIncident.car_incident_final_message()

    @staticmethod
    def car_incident_final_message() -> None:
        """Message for whenever you reach the end of this event."""
        red = "\033[91m"
        reset = "\033[0m"
        car_incident_end_of_the_event_message = (
            "\n\nIt has been a very long day indeed. No matter what the outcome of this incident "
            "has been,\nyou started to notice something much darker, something that was lurking there all along. "
            "\nYou begin to understand, that no one will help you. \nAfter what "
            "happened, you feel as if this was supposed to be a warning for you.\nWarning, that bad "
            "things will most likely happen here in the future and no one from your colleagues will be "
            "here to defend you.\nBut it's just a thought that occurred in your mind and you don't really give it that much "
            "attention as it would probably deserve."
            f"\n\n{red}FROM THIS MOMENT, YOU WILL GAIN +5 PCR HATRED DAILY.{reset}"
        )
        input("\n(CONTINUE...)")
        print(car_incident_end_of_the_event_message)

    @staticmethod
    def make_a_punishment_roll_for_the_car_incident(stats: JBStats) -> None:
        """Random int roll for deciding the level of player's punishment."""
        car_incident_pcr_hate = 0
        car_incident_money_punishment_roll = randint(2500, 7500)

        if car_incident_money_punishment_roll <= 4500:
            car_incident_pcr_hate = 10
        elif car_incident_money_punishment_roll <= 6500:
            car_incident_pcr_hate = 15
        elif car_incident_money_punishment_roll <= 7500:
            car_incident_pcr_hate = 25

        stats.increment_stats_pcr_hatred(car_incident_pcr_hate)
        stats.increment_stats_value_money(-car_incident_money_punishment_roll)

        input(
            "\nYou tell your boss that you are sorry, that you did a mistake and you will accept "
            "whatever punishment to come.\nYour apology is accepted but, your resentment towards "
            "this organization has grown rapidly. \nYou were charged with abandoning a traffic incident "
            "(that happened on a parking lot) and not reporting it. \nBecause you admitted your guilt "
            "only after the crime was reported by someone else, it doesn't shine a really good light on you."
            "\nAt least that is what they told you...\nOn the other hand, the punishment will be resolved "
            "swiftly and most likely it won't hurt you that much over the long term. \nDespite all of that, "
            "you feel great deal of anger, coming in."
            "\n\n(CONTINUE...)"
        )

        print(
            f"\n\nOUTCOME: \nMONEY - {car_incident_money_punishment_roll}, "
            f"\nPCR HATRED + {car_incident_pcr_hate}"
        )
        print(
            f"\n\nYou have {stats.available_money},- CZK money left."
            f"\nYour PCR Hatred is: {stats.pcr_hatred}."
        )

    @staticmethod
    def lawyer_paul_goodman_is_called(stats: JBStats) -> None:
        """Using the lawyer option."""
        input(
            "\nYou won't let anyone push you around, so you end the boss's call and immediately call "
            "\nThe best lawyer out there, to fight for your cause - PAUL GOODMAN. \nYou explain him what "
            "happened and even though this lawyer is very costly, he finds your case intriguing, so he "
            "offers his services for free!\nAfter that he tells you he will study your case closely and "
            "from now on, you can consider him your ally. \nBefore the call is cancelled, he tells you "
            "one final message: 'no matter what they offer, don't trust them, THEY ONLY LIE.'"
            "\n\n(PRESS ANY KEY TO CONTINUE.)"
        )
        input(
            "\n\nYou take a walk outdoors, to consider your next steps and to clean your head from this "
            "mess, you ask yourself, how could this even happen? How could it go so wrong quickly?"
            "\nYou hear the sound of your phone again, after 3 years of service, you've learned to "
            "anticipate the worst, when you look at the phone display, for a brief moment, you think "
            "your eyes are deceiving you.\nYou can make out the letters, saying only: 'POLICE COLONEL'"
            "\n'FUCK', you could almost hear yourself that, despite you only thought of it in your mind."
            "\n'If he's calling, something is seriously wrong' you think. \nAfter that you reluctantly press "
            "the green button, to accept the call, and put the phone next to your ear..."
            "\n\n(PRESS ANY KEY TO CONTINUE.)"
        )
        input(
            "\n'Hello JB! It has been so long... I have heard about that little ... accident you had, hope "
            "everything is all-right?'\nYou can feel your knees shaking and your heart beating louder, "
            "despite your best efforts to stop this.\nWhy would he call me? What can this mean? "
            "You have so many questions right now and no answers at all..."
            "\n\n'JB, I have heard some disturbing news and I've wanted to know whether my sources are reliable..."
            "\nI've been told that you didn't agree to the way we classified the incident and that you will "
            "try to sue with us.'\nEven though you haven't said a word yet, it didn't stop the colonel "
            "from his monologue.\n'I know, I know, it's been a hard day for you... I just wanted to remind "
            "you of something, that you should keep in mind.' \nHe then pauses for a brief moment, as if "
            "to let you breathe and prepare for what he is about to say.\n\n(PRESS ANY KEY TO CONTINUE.)"
        )
        print(
            "\n'JB, you know that when I've offered you to work at the station you are currently at, I did "
            "that with my best intentions towards you.\nYou can also know that right now I'm talking to you "
            "as if you were my own son and that I really do care about you."
            "\nJB, don't do something you might regret later on.\n\nAs a matter of fact, I like you, I mean that, you "
            "are still young and can achieve great things... but this is a dark path you are heading to.\n"
            "We are still on the good terms...but keep in mind that today's enemies "
            "were yesterday's friends once. \nIf you accept my offer, I can promise you "
            "I will do whatever I can to reduce the punishment to bare minimum or even cancel it completely. "
            "\n\nOn the other hand... if you choose to fight with us, remember that you can win a battle but not a war."
            "\nThat is not a threat, but just a friendly reminder."
            "\nKeep that in mind, before you make your decision.'"
            "\n\nYou have the following options:"
            "\n1. [?%] FIGHT (This will have big consequences!.)"
            "\n2. [50/50%] BACK DOWN (You can still back down and hope for the best.)"
            "\n\nWHAT IS YOUR DECISION?: "
        )

        continue_with_lawyer_or_without_him = Decision('', ("1", "2"))
        Decision.create_decision(continue_with_lawyer_or_without_him)

        if continue_with_lawyer_or_without_him.decision_variable_name == "1":
            stats.increment_stats_pcr_hatred(40)
            print(
                "\nYou manage to collect your thoughts, and with a single breath, you tell him:\n\n"
                "'Thanks for the offer, but I'll rather stick to my decision.'"
                "\nFor a brief moment, you don't hear any response, colonel wasn't probably prepared for this."
                "'Very well, do as you wish.' He responds calmly.\nFROM NOW ON, COLONEL WILL BE HOSTILE TOWARDS YOU!"
            )
            print("\nOUTCOME: \nPCR HATRED + 40, PAUL GOODMAN ACQUIRED!")
            print(f"\nYour PCR Hatred is: {stats.pcr_hatred}.")
            input("\n(CONTINUE...)")
            print(
                "\nPaul Goodman contacts you once again. He explains, that suing the police is not going to be easy, "
                "but certainly not impossible.\nSince you haven't accepted any punishment, you will have 30 more days "
                "to prepare for the case.\nYour attorney mentions that your cooperation and time will be required, and "
                "in the end, the more evidence you gain, the stronger your case will become."
            )

        elif continue_with_lawyer_or_without_him.decision_variable_name == "2":
            colonel_helps_you_chance_roll = randint(1, 2)
            input(
                "\nWith the deepest regret, you announced to him: 'I'm sorry and I accept your offer.'"
                "\n'I knew you would make the right decision' came from the phone with a subtle hint of laughter."
                "\nDespite your anger and your resentment... you accept the vague promises that the colonel "
                "has fed you with.\nYou don't know if he will keep up with his words, but you have little hope "
                "left, and even less resolution to fight this system.\nYou obey and put your destiny into "
                "his hands, you decided to go through the path of least resistance..."
                "\n\n(CONTINUE...)"
            )

            if colonel_helps_you_chance_roll == 1:
                stats.increment_stats_pcr_hatred(-10)
                input(
                    "\n[SUCCESS]"
                    "\nNot even one hour passes and your phone rings again, it is the colonel. This time, when you "
                    "accept this call, he tells you that he has great news!\nHe spoke to some lawyers and since the "
                    "accident happened on a parking lot, it is not considered as a part of a road communication,\n"
                    "meaning your incident cannot be even classified as a road accident.\nYou won't have to pay "
                    "anything, since the damage falls under insurance, which you actively pay."
                    "\n\n(CONTINUE...)"
                )
                input(
                    "\n\nYou are glad this nightmare that started so quickly, ended even faster."
                    "\nNow, you can enjoy your free time however you want...\nNo matter what, you still have "
                    "to think about this incident and for some reason you have a feeling,\nthat soon some big "
                    "things are going to happen and the consequences will be much larger."
                    "\n\n(CONTINUE...)"
                )
                print("\n\nOUTCOME: PCR HATRED -10, COLONEL'S AFFECTION GAINED!")
                print(f"\nYour PCR Hatred is: {stats.pcr_hatred}.")
            else:
                stats.increment_stats_pcr_hatred(20)
                stats.increment_stats_value_money(-3500)
                input(
                    "\n[FAILURE]"
                    "\nNot even one hour passes and you start to have a bad feeling about this, you feel as if "
                    "it was really a bad idea to put your fate into Colonel's hand. Then your phone rings.\nIt's him "
                    "again and he sounds more less confident then he did last time. He tells you he was able to only "
                    "reduce the penalty to the lowest possible amount\nhe tells you this information most politely, "
                    "just as if he were announcing a death of someone close to you.\nHe tries to prolong the call a "
                    "multiple times, as if he was expecting you to say 'thank you, I'm grateful'.\nBut you are not, "
                    "you are not happy with this.\nThis outcome is not the worst one, but what angers you the most, "
                    "were his false promises."
                    "\n\n(CONTINUE...)"
                )
                print("\n\nOUTCOME: MONEY -3500, PCR HATRED +20.")
                print(
                    f"\nYour PCR Hatred is: {stats.pcr_hatred}."
                    f"\nYour Total money is: {stats.available_money}"
                )