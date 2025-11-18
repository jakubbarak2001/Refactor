"""Module used for representing the first major decision branch at the start of the game, regarding the car accident."""
from random import randint
from jb_dev_stats import JBStats
from jb_dev_decision import Decision

class CarIncident(JBStats):
    """Initialises the event of car incident, initialised by JBStats class."""
    def __init__(self, available_money, coding_experience, pcr_hatred):
        """Initialise self."""
        super().__init__(available_money, coding_experience, pcr_hatred)


def car_incident(stats: JBStats):
    """First introduction to the game, with multiple choices."""
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
    Decision.create_decision_variable(report_incident_decision)

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
                choose_lawyer_first_choice = (
                    Decision('', ("1", "2")))
                Decision.create_decision_variable(choose_lawyer_first_choice)

                if choose_lawyer_first_choice.decision_variable_name == "1":
                    better_call_paul(stats)
                elif choose_lawyer_first_choice.decision_variable_name == "2":
                    car_incident_punishment_roll(stats)

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
                choose_lawyer_first_choice = (
                    Decision('', ("1", "2")))
                Decision.create_decision_variable(choose_lawyer_first_choice)

                if choose_lawyer_first_choice.decision_variable_name == "1":
                    better_call_paul(stats)

                elif choose_lawyer_first_choice.decision_variable_name == "2":
                    car_incident_punishment_roll(stats)

    car_incident_final_message()

def car_incident_final_message():
    """Message for whenever you reach the end of this event."""
    car_incident_final_message_variable= (
        "\n\nIt has been a very long day indeed. No matter what the outcome of this incident"
        "has been,\nyou started to notice something much darker, something that was lurking there all along. "
        "\nYou begin to understand, that no one will help you \nAfter what"
        "happened, you feel as if this was supposed to be a warning for you.\nWarning, that bad "
        "things will most likely happen here in the future and no one from your colleagues will be "
        "here to defend you.\nBut it's just a thought that occurred in your mind and you don't really give it that much "
        "attention as it would probably deserve.")
    input("\n(CONTINUE...)")
    print(car_incident_final_message_variable)

def car_incident_punishment_roll(stats):
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
    stats.increment_stats_value_money(- car_incident_money_punishment_roll)
    input("\nYou tell your boss that you are sorry, that you did a mistake and you will accept"
          "whatever punishment to come.\nYour apology is accepted but, your resentment towards "
          "this organization has grown rapidly. \nYou were charged with abandoning a traffic incident "
          "(that happened on a parking lot) and not reporting it. \nBecause you admitted your guilt "
          "only after the crime was reported by someone else, \nIt doesn't shine a really good light on you."
          "\nAt least that is what "
          "they told you...\nOn the other hand, the punishment will be resolved swiftly and most likely "
          "it won't hurt you that "
          "much over the long term. \nDespite all of that, you feel great deal of anger, coming in."
          "\n\n(CONTINUE...)")
    # ACCEPT THE PUNISHMENT FIRST CHOICE
    print(f"\n\nOUTCOME: \nMONEY - {car_incident_money_punishment_roll}, "
          f"\nPCR HATRED + {car_incident_pcr_hate}")
    print(f"\n\nYou have {stats.available_money},- CZK money left."
          f"\nYour PCR Hatred is: {stats.pcr_hatred}.")

def better_call_paul(stats):
    """Using the lawyer option."""
    # PAUL GOODMAN FIRST CHOICE
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
        "\nYou hear a the sound of your phone again, after 3 years of service, you've learned to "
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
        "to let you breath and prepare for what he is about to say.\n\n(PRESS ANY KEY TO CONTINUE.)"
    )
    print(
        "\n'JB, you know that when I've offered you to work at the station, you are currently at, I did "
        "that with my best intentions, towards you.\nYou can also know that right now I'm talking to you "
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
    car_incident_decision_lawyer_final_choices = (
        Decision('car_incident_decision_lawyer_final_variable', ("1", "2")))
    Decision.create_decision_variable(car_incident_decision_lawyer_final_choices)

    if car_incident_decision_lawyer_final_choices.decision_variable_name == "1":
        # PAUL GOODMAN FINAL CHOICE
        stats.increment_stats_pcr_hatred(stats, 10)
        # ADD POLICE HATRED AFFIX, +1 PCR_HATRED EVERY DAY, +2 IF ON INSANE
        print(
            "\nYou manage to collect your thoughts, and with a single breath, you tell him:\n\n"
            "'Thanks for the offer, but I'll rather stick to my decision.'"
            "\nFor a brief moment, you don't hear any response, colonel wasn't probably prepared for this."
            "'Very well, do as you wish.' He responds calmly.\nFROM NOW ON, COLONEL WILL BE HOSTILE TOWARDS YOU!"
        )
        print("\nOUTCOME: \nPCR HATRED + 10, PAUL GOODMAN ACQUIRED!")
        print(
              f"\nYour PCR Hatred is: {stats.pcr_hatred}."
        )
        input("\n(CONTINUE...)")
        print("\nPaul Goodman contacts you once again. He explains, that suing the police is not going to be easy, "
              "but certainly not impossible.\nSince you haven't accepted any punishment, you will have 30 more days, "
              "to prepare for the case.\nYour attorney mentions, that your cooperation and time will be required, and "
              "in the end, the more evidence you gain, the stronger your case will become.")
    elif car_incident_decision_lawyer_final_choices.decision_variable_name == "2":
        # ACCEPT THE PUNISHMENT FINAL CHOICE
        car_incident_colonel_roll = randint(1, 2)
        input(
            "\nWith the deepest regret, you announced to him: 'I'm sorry and I accept your offer.'"
            "\n'I knew you would make the right decision' came from the phone with a subtle hint of laughter."
            "\nDespite your anger and your resentment... you accept the vague promises that the colonel "
            "has fed you with.\nYou don't know if he will keep up with his words, but you have little hope "
            "left, and even less resolution to fight this system.\nYou obey and put your destiny into "
            "his hands, you decided to go through the path of least resistance..."
            "\n\n(CONTINUE...)"
        )
        if car_incident_colonel_roll == 1:
            stats.increment_stats_pcr_hatred(-10)
            # FINAL CAR INCIDENT EVENT COLONEL HAPPY ENDING
            input("\n[SUCCESS]"
                  "\nNot even one hour passes and your phone rings again, it is the colonel. This time, when you "
                  "accept this call, he tells you that he has great news!\nHe spoke to some lawyers and since the "
                  "accident happened on a parking lot, it is not considered as a part of a road communication,\n"
                  "meaning your incident cannot be even classified as a road accident.\nYou won't have to pay "
                  "anything, since the damage falls under insurance, which you actively pay."
                  "\n\n(CONTINUE...)")
            input(
                "\n\nYou are glad this nightmare that started so quickly, ended even faster."
                "\nNow, you can enjoy your free time however you want...\nNo matter what, you still have "
                "to think about this incident and for some reason you have a feeling,\nthat soon some big "
                "things are going to happen and the consequences will be much larger."
                "\n\n(CONTINUE...)"
            )
            print("\n\nOUTCOME: PCR HATRED -10, COLONEL'S AFFECTION GAINED!")
            print(
                  f"\nYour PCR Hatred is: {stats.pcr_hatred}."
            )
        else:
            # ADD POLICE HATRED AFFIX, +1 PCR_HATRED EVERY DAY, +2 IF ON INSANE
            # FINAL CAR INCIDENT EVENT COLONEL BAD ENDING
            stats.increment_stats_pcr_hatred(20)
            stats.increment_stats_value_money(-3500)
            input("\n[FAILURE]"
                  "\nNot even one hour passes and you start to have a bad feeling about this, you feel as if "
                  "it was really a bad idea to put your fate into Colonel's hand. Then your phone rings.\nIt's him "
                  "again and he sounds more less confident then he did last time. He tells you he was able to only "
                  "reduce the penalty to the lowest possible amount\nhe tells you this information most politely, "
                  "just as if he were announcing a death of someone close to you.\nHe tries to prolong the call a "
                  "multiple times, as if he was expecting you to say 'thank you, I'm Grateful'.\nBuy you are not, "
                  "you are not happy with this.\nThis outcome is not the worst one, but what angers you the most, "
                  "were his false promises."
                  "\n\n(CONTINUE...)")
            print("\n\nOUTCOME: MONEY -3500, PCR HATRED +20.")
            print(
                  f"\nYour PCR Hatred is: {stats.pcr_hatred}."
                  f"\nYour Total money is: {stats.available_money}"
            )