"""Contains everything regarding storytelling."""
from jb_game.jb_dev_stats import JBStats
from random import randint
from jb_dev_decision import Decision

class Story:
    """Contains the most important story elements, mostly text strings."""
    def __init__(self, stats:JBStats):
        """Initialises itself."""
        self.stats = stats
    def start_game_message(self):
        """Gives a neatly formatted welcoming message, for whenever you start a game."""
        print("\nWelcome to JB - the game! \n\nIn this game, you will be playing as a young and perspective police "
              "officer in northern part of Bohemia, where sun never rises and criminality is growing rapidly. "
              "\nThe game begins in 1.7.2025, at start you love your job, but that is soon to change, due to the "
              "unforeseen consequences. \nSoon, you will realise your path lies elsewhere - in software development. "
              "Your time and resources are limited - you have to end your job as police officer soon!"
              "\n\nYou will have to balance between 3 main stats: \n1. Money, \n2. Coding skills, \n3. Hatred of Police "
              "\n\nThe most important rule for you is always have more than 0 money and to keep your "
              "hatred of police under 100."
              "\nIn the following section, you will be able to choose your difficulty level, good luck and have fun!")

    def start_the_car_incident_event(self, stats):
        """Contains the story of first game's event - the famous car incident of JB."""
        print("\nARC I. - J.B. BEGINS")
        print("\nDAY I. - 1.7.2025")
        input(
            "\nIt is very early in the morning, you have just arrived at work and parked "
            "your car outside of the station, \nThe sun is rising slowly and it's sunrays are falling on your forehead, "
            "It looks like any ordinary, routine day to you. "
            "\nYou have overtime shift in other station that is 30 minutes "
            "away, you look on your wrist to check what time is it, to see that you are already being late...\nYou "
            "rush in to the marked police vehicle,waiting for you in front of the station.\nYou notice there is a "
            "one big car, which you usually use whenever someone calls 158."
            "\nIt is obstructing the only way out of the parking lot, "
            "standing in the pathway to the parking lot, behind your car."
            "\nIf that wasn't bad enough, there is another car parked very closely to the right side of your vehicle."
            "\n\n(PRESS ANY KEY TO CONTINUE)"
        )
        print(
            "\nYou believe in your driving skills "
            "and decide to try to manoeuvre your way out of this mess. \nAs you are "
            "trying to leave the parking lot, for a brief moment, you hear a rustling sound "
            "of metal plates hitting each other,\n"
            "when you look at the cars, you can see that the frontal part of the car you were "
            "driving is almost touching the left side back door of another parked car "
            "and there is no space between them. "
            "\nYou immediately abort this operation and return the car back to where is was.\nYou leave your vehicle "
            "to check what happened... after you pause and look at the vehicles, you decide to..."
        )
        print(
            "\n1. [20%] Try to look for the damage by yourself."
            "\n2. [20%] Tell your colleagues about what happened and ask for help."
            "\n\n(What is your decision?): "
        )
        roll_1 = (randint(1, 100))

        report_incident_decision = (
            Decision('', ("1", "2")))
        Decision.create_decision(report_incident_decision)

        if report_incident_decision.decision_variable_name == "1":
            if roll_1 >= 80:
                stats.increment_stats_pcr_hatred(5)
                stats.increment_stats_value_money(-500)
                input("\n[SUCCESS]\nGood job! You found the damage, it's mostly surface, nothing major really..."
                      "\nAfter that you reported the incident and the standard procedures were conducted."
                      "good news for you is that, you will have to pay only small amount for some scratches you"
                      "did on the car and nothing else, since you admitted your guilt.\n\n"
                      "After all the formalities were done, you were told by the traffic police officer, \nthat you "
                      "have nothing to worry about and that you did the right choice by telling the others."
                      "\nAfter that, you go about your business and complete the shift without any other major "
                      "hiccups, \nafter that you return home, completely exhausted, with so many thoughts in your head."
                      "\n\nYou are going to be a black sheep of the department for some time, but people will forget "
                      "soon... \nyou've realised, that there could have been far worse outcome than this."
                      "\n\n(PRESS ANY KEY TO CONTINUE.)")
                print("\n\nOUTCOME:\nMONEY - 500,- CZK, PCR HATRED + 5.")
                print(
                    f"\nYou have {stats.available_money},- CZK money left. \nYour PCR Hatred is: {stats.pcr_hatred}."
                )
            else:
                input(
                    "\n[FAILURE]"
                    "\nYou haven't noticed any damage at all. \nYou believe, that nothing happened and then you drive "
                    "to the other station.\nThe shift is long and really hard, you barely stand on your feet at 7am. "
                    "You've returned to your home station you check the cars briefly again - but see no damage at all."
                    "\nYou get in your car, extremely tired...you don't even pay attention to the road ahead.\n"
                    "After you return home, you fall asleep immediately, you drift away in your dreams,\n"
                    "until a sharp noise cuts you from your one hour of sleep the same way a razor cuts through "
                    "a skin. \nYou hear loud banging on your door, followed by threatening voice almost yelling "
                    "'HEY OPEN UP'.\nYour ears are ringing and your head hurts as if you were experiencing a "
                    "severe hangover, you open the door, only to find 4 police officers, standing tall in-front "
                    "of your door...\n\n(PRESS ANY KEY TO CONTINUE)"
                )
                print(
                    "\n'You probably know why we are here.' says the tallest, but not the smartest, "
                    "who is probably their leader.\n"
                    "With your deep insight, you are capable to connect the dots and realise, that as a matter of "
                    "fact, something happened with the cars, even though you weren't able to detect what.\n"
                    "You realise they are only soldiers, who just follow their orders, there is no reason "
                    "to argue with them, only to listen and hope everything goes well.\n"
                    "'We need to test if you took any alcohol', says their boss with completely still expression."
                    "\nYou comply, and the test result is 0.00%. After that, they finally leave."
                    "\nSuddenly, you hear a buzzing sound of a phone in your pocket. It's your boss, he asks you "
                    "about the details... He tells you that you probably haven't realised yet "
                    "what are the consequences of your actions. \n"
                    "It's possible for you that it can forbidden for you to drive motor vehicles, for up to 2 YEARS! "
                    "and to loose a lot of money on the penalty, going to the range of higher thousands of CZK."
                    "\n\nYou have the following options:"
                    "\n1. [100%] BETTER CALL PAUL! (get a lawyer on this case)."
                    "\n2. [100%] Admit your guilt, be humble, repent your actions and hope for the best."
                    "\n\n(WHAT ARE YOU GOING TO DO?): "
                )
                choose_to_call_a_lawyer = (
                    Decision('', ("1", "2")))
                Decision.create_decision(choose_to_call_a_lawyer)

                from jb_game.jb_dev_car_incident_event import CarIncident

                if choose_to_call_a_lawyer.decision_variable_name == "1":
                    CarIncident.lawyer_paul_goodman_is_called(stats)
                elif choose_to_call_a_lawyer.decision_variable_name == "2":
                    CarIncident.make_a_punishment_roll_for_the_car_incident(stats)

        elif report_incident_decision.decision_variable_name == "2":
            if roll_1 >= 80:
                stats.increment_stats_pcr_hatred(5)
                stats.increment_stats_value_money(-500)
                input("\n[SUCCESS]\nYou weren't able to find any damage by yourself. \nDespite your better judgment, "
                      "you decided to "
                      "go inside the station and explain yourself. Your colleagues rushed out to try and find out "
                      "any damage and they were successful!\nAfter that the standard procedures were conducted, "
                      "good news for you is that, you will have to pay only small amount for some scratches you"
                      "did on the car and nothing else, since you admitted your guilt.\n\n"
                      "After all the formalities were done, you were told by the traffic police officer, \nthat you "
                      "have nothing to worry about and that you did the right choice by telling the others."
                      "\n\nAfter that, you go about your business and complete the shift without any other major "
                      "hiccups afterwards,\nyou return home, completely exhausted, with so many thoughts in your head."
                      "\n\nYou are going to be a black sheep of the department for some time, but people will forget "
                      "soon... \nyou've realised, that there could have been far worse outcome than this."
                      "\n\n(PRESS ANY KEY TO CONTINUE.)")
                print("\n\nOUTCOME:\nMONEY - 500, PCR HATRED + 5.")
                print(
                    f"You have {stats.available_money},- CZK money left. Your PCR Hatred is: {stats.pcr_hatred}."
                )
            else:
                input(
                    "\n[FAILURE]\nDespite your best efforts, you try to look at the car, yet you don't see any "
                    "immediate signs of\n"
                    "damage. For a brief moment you think about sharing this incident to your colleagues, but then\n"
                    "as you wanted to open the door and tell them about it, it occurred to you that this won't be \n"
                    "the best idea, because you can imagine what they would say behind your back after such\n"
                    "stupid mishap... you guess that, nothing happened and with limited time you had, you head out..."
                    "\n\n(PRESS ANY KEY TO CONTINUE.)"
                )
                input(
                    "\nThe night shift was long, and you are tired, when you returned to your station,\nyou checked "
                    "out the car again, but you haven't noticed anything... it really looks as if nothing happened.\n"
                    "You sit in your car, extremely tired...you don't even pay attention to the road ahead.\n"
                    "After you return home, you fall asleep immediately, you drift away in your dreams,\n"
                    "until a sharp noise cuts you from your one hour of sleep the same way a razor cuts through "
                    "a skin. \nYou hear loud banging on your door, followed by threatening voice almost yelling "
                    "'HEY OPEN UP'.\nYour ears are ringing and your head hurts as if you were experiencing a "
                    "severe hangover, you open the door, only to find 4 police officers, standing tall in-front "
                    "of your door...\n\n(PRESS ANY KEY TO CONTINUE)"
                )
                print(
                    "\n'You probably know why we are here.' says the tallest, but not the smartest, "
                    "who is probably their leader.\n"
                    "With your deep insight, you are capable to connect the dots and realise, that as a matter of "
                    "fact, something happened with the cars, even though you weren't able to detect what.\n"
                    "You realise they are only soldiers, who just follow their orders, there is no reason "
                    "to argue with them, only to listen and hope everything goes well.\n"
                    "'We need to test if you took any alcohol', says their boss with completely still expression."
                    "\nYou comply, and the test result is 0.00%. After that, they finally leave."
                    "\nSuddenly, you hear a buzzing sound of a phone in your pocket. It's your boss, he asks you "
                    "about the details... He tells you that you probably haven't realised yet "
                    "what are the consequences of your actions. \n"
                    "It's possible for you that it can forbidden for you to drive motor vehicles, for up to 2 YEARS! "
                    "and to loose a lot of money on the penalty, going to the range of higher thousands of CZK."
                    "\n\nYou have the following options:"
                    "\n1. [100%] BETTER CALL PAUL! (get a lawyer on this case)."
                    "\n2. [100%] Say that you are sorry."
                    "\n\n(WHAT ARE YOU GOING TO DO?): "
                )
                choose_to_call_a_lawyer = (
                    Decision('', ("1", "2")))
                Decision.create_decision(choose_to_call_a_lawyer)

                from jb_game.jb_dev_car_incident_event import CarIncident

                if choose_to_call_a_lawyer.decision_variable_name == "1":
                    CarIncident.lawyer_paul_goodman_is_called(stats)

                elif choose_to_call_a_lawyer.decision_variable_name == "2":
                    CarIncident.make_a_punishment_roll_for_the_car_incident(stats)