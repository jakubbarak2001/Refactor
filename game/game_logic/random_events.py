import os
import sys
from random import choice
from random import randint

from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from game.game_logic.interaction import Interaction
from game.game_logic.press_enter_to_continue import continue_prompt
from game.game_logic.stats import Stats

# Try to import pygame, but don't fail if it's not available
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    pygame = None


def resource_path(relative_path):
    """Get absolute path to resource (Works for Dev & EXE)"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def play_police_siren():
    """Play police siren sound effect when random event occurs."""
    if not PYGAME_AVAILABLE:
        return
    
    try:
        # Check if mixer is initialized, if not try to initialize it
        try:
            mixer_initialized = pygame.mixer.get_init() is not None
        except (pygame.error, AttributeError):
            mixer_initialized = False
        
        if not mixer_initialized:
            try:
                pygame.mixer.init()
            except (pygame.error, Exception):
                # Mixer initialization failed, can't play sound
                return
        
        # Load and play siren sound
        siren_path = resource_path("police_siren.mp3")
        if os.path.exists(siren_path):
            try:
                # Use Sound for one-time effects (not music)
                siren_sound = pygame.mixer.Sound(siren_path)
                siren_sound.set_volume(0.3)  # 30% volume
                siren_sound.play()  # Play once, don't loop
            except (pygame.error, Exception):
                # Sound loading/playing failed, silently continue
                pass
    except Exception:
        # Silently fail if sound can't be played
        pass

# --- SETUP: WINDOWS CONSOLE COMPATIBILITY ---
if os.name == 'nt':
    os.system('mode con: cols=120 lines=40')
    os.system('chcp 65001 > nul')

# Initialize Console once
console = Console(force_terminal=True)


def show_random_event_banner():
    """Display random event banner and play police siren sound."""
    # Play police siren sound effect
    play_police_siren()
    
    # Check if we're in GUI mode
    from game.game_logic.interaction import get_interaction
    from game.game_logic.gui_interaction import GUIInteraction
    from game.game_logic.gui_interaction_v2 import GUIInteractionV2
    
    try:
        interaction = get_interaction()
        is_gui_mode = isinstance(interaction, (GUIInteraction, GUIInteractionV2))
    except:
        is_gui_mode = False
    
    if is_gui_mode:
        # GUI Mode: Display the random_event background only (no text box, no prompt label) and wait for continue
        # Get the interaction instance to call continue_prompt with show_prompt_label=False
        interaction = get_interaction()
        if isinstance(interaction, GUIInteractionV2):
            interaction.continue_prompt(bg="random_event", show_prompt_label=False)
        else:
            Interaction.continue_prompt(bg="random_event")
    else:
        # Terminal Mode: Display ASCII art banner
        # 1. Clean ASCII Art Definition
        # Note: I removed leading newlines inside the string to prevent spacing errors
        art_top_raw = r"""
██████╗  █████╗ ███╗   ██╗██████╗  ██████╗ ███╗   ███╗
██╔══██╗██╔══██╗████╗  ██║██╔══██╗██╔═══██╗████╗ ████║
██████╔╝███████║██╔██╗ ██║██║  ██║██║   ██║██╔████╔██║
██╔══██╗██╔══██║██║╚██╗██║██║  ██║██║   ██║██║╚██╔╝██║
██║  ██║██║  ██║██║ ╚████║██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝
"""

        art_bottom_raw = r"""
███████╗██╗   ██╗███████╗███╗   ██╗████████╗           
██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝           
█████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║              
██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║              
███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║              
╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝              
"""

        # 2. Process "RANDOM" (Top - Red)
        # We strip() to remove empty lines from the raw string variable,
        # then justify="left" preserves the ASCII structure.
        text_top = Text(art_top_raw.strip("\n"), style="bold color(196)", justify="left", no_wrap=True)

        # 3. Process "EVENT" (Bottom - Blue)
        text_bottom = Text(art_bottom_raw.strip("\n"), style="bold color(33)", justify="left", no_wrap=True)

        # 4. Group and Align
        # We Align.center the *whole block*, not the internal text logic.
        banner_group = Group(
            Align.center(text_top),
            Align.center(text_bottom)
        )

        # 5. Render
        console.print(
            Panel(
                banner_group,
                border_style="bold white",
                title="[bold white on color(196)] ⚠  PRIORITY ALERT ⚠ [/]",
                subtitle="[bold white on color(33)] DISPATCH INCOMING [/]",
                padding=(1, 2),  # Added vertical padding for "breathing room"
                expand=False  # Keeps the box tight to the content
            ),
            justify="center"  # Centers the Panel itself in the terminal
        )


if __name__ == "__main__":
    show_random_event_banner()
    console.input("[bold grey50](PRESS ENTER TO CONTINUE)[/]")


class RandomEvents:
    """Class containing random events that turn up during the gameplay, every 3 days."""

    def __init__(self) -> None:
        """Initialises itself and the list of events."""
        self.random_events_list = [
            RandomEvents.israeli_developer,
            RandomEvents.nightmare_wolf,
            RandomEvents.civilian_small_talk,
            RandomEvents.admin_mistake_after_shift,
            RandomEvents.overtime_offer,
            RandomEvents.birthday_gift,
            RandomEvents.corpse_in_care_home,
            RandomEvents.forgotten_usb,
            RandomEvents.turkish_fraud,
            RandomEvents.printer_incident,
            RandomEvents.citizen_of_czechoslovakia,
            RandomEvents.paperwork_overload,
            RandomEvents.dispatch_blue_screen,
            RandomEvents.tech_bro_speeding
        ]

    def select_random_event(self, stats: Stats) -> bool:
        """
        Chooses one random event at once, then removes it from the list.
        Returns True if an event ran, False if the list was empty.
        """
        if not self.random_events_list:
            return False

        else:
            random_event_selection = choice(self.random_events_list)
            self.random_events_list.remove(random_event_selection)
            random_event_selection(stats)
            return True

    @staticmethod
    def overtime_offer(stats: Stats) -> None:
        """Event with overtime offer."""
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "Your boss calls you very early in the morning, he says he needs you to "
            "\narrive at the police station urgently.\nBoth of your colleagues who were supposed to work today "
            "suddenly became sick.\nYou would get extra money for this overtime.\nOn the other hand, you "
            "don't have to accept this and perhaps the time would be better used, if you were to code at home."
        )

        # Display decision using Rich Panel with difficulty tags
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "DO OVERTIME. [GAIN RANDOM AMOUNT OF MONEY]"),
            ("2", Interaction.get_difficulty_tag(), "STAY AT HOME AND CODE. [GAIN RANDOM AMOUNT OF CODING SKILLS]")
        ])

        if select_choice == "1":
            random_event_chance_roll = randint(3500, 12500)
            stats.increment_stats_value_money(random_event_chance_roll)
            Interaction.print_text(
                "\nYou've agreed to the overtime, at least the shift was calm."
                "\nThe money is nice, but don't forget that your mission is to leave this job once and for all."
            )
            Interaction.show_outcome(f"+{random_event_chance_roll} MONEY.")

        elif select_choice == "2":
            random_event_chance_roll = randint(15, 40)
            stats.increment_stats_coding_skill(random_event_chance_roll)
            Interaction.print_text(
                "\nAlthough your boss wasn't happy with your decision, you've decided to stay at home"
                "\nand to use your time for studying Python. \nIn the end you've earned a great deal of knowledge."
            )
            Interaction.show_outcome(f"+{random_event_chance_roll} CODING SKILLS.")
        continue_prompt()

    @staticmethod
    def birthday_gift(stats: Stats) -> None:
        """Event with your colleagues celebrating their B-day."""
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "You're at the station, it's dark again, "
            "\nno one really cared to even pull the blinds even though its almost 10 AM now. "
            "\nThe depressive atmosphere is omnipresent, your mind is wandering again, your eyes staring completely "
            "\nstill at the ceiling. Until your middle-aged secretary arrives, she puts her fake smile on, "
            "\nThe one, even tiny children would see through. "
            "\nYou put on your mask again and force a smile on your face, with utter joy, she announces "
            "\nthat two of your colleagues you don't give a damm about are celebrating their "
            "\nbirthdays this week and asks you, if you want to contribute to their gifts."
            "\nYou pause for a moment and think for yourself - 'Why should I contribute? I am gonna quit anyway... "
            "\nbut if I won't give anything to them, they will hate me here even more.' "
            "\n\nWhat shall I do..."
        )

        # Display decision using Rich Panel with difficulty tags
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "PAY FOR THE GIFTS. [- 1000,- CZK, PCR HATRED +5]"),
            ("2", Interaction.get_difficulty_tag(), "DON'T PAY ANYTHING. [PCR HATRED + 15]")
        ])

        if select_choice == "1":
            stats.increment_stats_pcr_hatred(5)
            stats.increment_stats_value_money(- 1000)
            Interaction.print_text(
                "\n'Sure, buy them something nice.' "
                "\nYou don't even look in her eyes as you torment yourself with those words you've just said."
                "\nShe is satisfied, but you are still obliged to to listen to her rantings\nand about "
                "her children for another 15 minutes, after that, she finally leaves."
                "\n\n'What have I done to deserve this...' you think for yourself."
            )
            Interaction.show_outcome("- 1000 CZK, +5 PCR HATRED.")

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(15)
            Interaction.print_text(
                "\n'No...I don't want to contribute'"
                "\nShe pauses, her mouth opens, she stares at you. You always thought that she is around her 40s, "
                "\nBut as she started to glare at you without saying anything for few seconds, you think she "
                "\nlooks more close to her 70s.\n "
                "\nYou don't react and hold your cold hearted expression towards her, "
                "\nnot breaking the contact with her even for a mere second."
                "\nAfter that short moment, that felt to you like eternity. She puts her hands on her hips, and tilts "
                "\nher head slightly towards, after which she says with a imitation of motherly tone '...JB...'\n"
                "\nAfter that, another moment of silence occurs, you respond only by staring directly into her soul. "
                "\nSuddenly, she recognises, that something is really wrong with you."
                "\nYou are no longer taking anything from anyone. "
                "\nIn a last ditch attempt, she says that 'it's not really nice from you'."
                "\n'I don't care'\n"
                "\nAfter that she finally lets you be, as she retreats to her work."
                "\n'Fuck them all...' you think for yourself."
            )
            Interaction.show_outcome("+ 15 PCR HATRED.")
        continue_prompt()

    @staticmethod
    def civilian_small_talk(stats: Stats) -> None:
        """Event where an old civilian tries to make small talk and asks about your job."""
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "You are standing next to your marked car, somewhere in the middle of nowhere."
            "\nCold wind, grey sky, nothing happening for the last 40 minutes."
            "\nYour colleague is scrolling his phone like a true professional, defending the homeland by liking memes."
            "\nYou are guarding some pointless place, because someone at the district HQ decided it looks good on paper."
            "\n\nFrom the nearby panel house, an older man slowly approaches you. Jacket from 1987, slippers, "
            "eyes full of boredom and curiosity."
            "\nAt first, he asks the usual nonsense:"
            "\n'What are you guarding here?'"
            "\n'Is something happening?'"
            "\n'Is it dangerous here?'"
            "\nYou answer politely, mechanically. You would rather be anywhere else, even filling out forms."
            "\n\nAfter a while, he gets bolder and asks the one question you didn't want to hear:"
            "\n'Tell me honestly, young man... do you like this job? What do you really think about it?'"
            "\n\nYou feel something inside you. A familiar pressure in your chest. You could finally say it."
            "\nYou could finally talk about how this job is one big circus, about the money, about the leadership..."
            "\nOr you can put your mask back on and say the neutral PR answer you've said a hundred times before."
            "\n\nYou have the following options:"
        )

        # Display decision using Rich Panel with difficulty tags (80% success chance)
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(80), "VENT OUT AND TELL HIM THE TRUTH."),
            ("2", Interaction.get_difficulty_tag(), "KEEP IT INSIDE AND SAY GENERAL INFORMATION. [SAFE OPTION]")
        ])

        if select_choice == "1":
            vent_chance_roll = randint(1, 100)

            if vent_chance_roll <= 80:
                stats.increment_stats_pcr_hatred(-25)
                Interaction.print_text(
                    "\nYou look him straight in the eyes and something inside you finally snaps."
                    "\nYou start slowly, but your words gain momentum:"
                    "\nYou tell him about the shifts that never end, about the paperwork that eats your soul,"
                    "\nabout the salary that wouldn't even feed a golden retriever with anxiety."
                    "\nYou describe the leadership that has never seen the street, but writes rules for those who live on it."
                    "\nThe old man just nods, listening. No phone, no recording, just a human being who actually hears you."
                    "\nWhen you finish, he smiles sadly and says: 'I thought so... you can see it in your eyes.'"
                    "\nHe wishes you good luck and slowly walks away."
                    "\nYou feel strangely lighter. Nothing changed... but at least you said it out loud."
                )
                Interaction.show_outcome("- 25 PCR HATRED.")
                continue_prompt()

            else:
                stats.increment_stats_pcr_hatred(25)
                stats.increment_stats_value_money(-2500)
                Interaction.print_text(
                    "\nYou look around, see no one, and decide to finally let it all out."
                    "\nYou tell him everything. How they pay you practically nothing for doing other people's dirty work."
                    "\nHow you are the punching bag of the state, how every mistake is yours, but every success disappears "
                    "in the reports."
                    "\nYou describe the leadership that moves only when someone up there needs a good photo for the news."
                    "\nThe old man listens, nods, pretends he understands."
                    "\n\nThe next day, your boss calls you in. On his desk lies a phone, screen turned towards you."
                    "\nYou see yourself on video, hear your own voice describing your 'dream job'."
                    "\nThe old man sent the recording to the city hall, 'out of concern for the state of the police'."
                    "\nYou listen to every sentence you said, but this time as evidence."
                    "\nBy the end of the week, you receive a written reprimand and a nice little financial penalty."
                    "\nNobody cares why you said it. Only that you said it."
                )
                Interaction.show_outcome("+ 25 PCR HATRED, -2500 CZK.")
                continue_prompt()

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(10)
            Interaction.print_text(
                "\nYou feel the words crawling up your throat, but you swallow them back down."
                "\nYou put on your standard-issue smile and say something about 'stable job, helping people, "
                "good team, interesting work'."
                "\nYou hear yourself and want to throw up, but the old man seems satisfied."
                "\nHe nods and says: 'Well, at least someone still does this work, right?'"
                "\nYou just answer: 'Yes, someone.'"
                "\nHe walks away and the silence returns. Only now it feels heavier."
                "\nYou didn't get punished, nobody recorded anything... but the pressure inside you grew again."
            )
            Interaction.show_outcome("- 10 PCR HATRED.")
            continue_prompt()

    @staticmethod  # ADD FLY BUZZING SOUND
    def corpse_in_care_home(stats: Stats) -> None:
        """Event involving a decomposing corpse found in a care home."""
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "You enter the old-age care home. The moment the automatic doors open, "
            "a wall of warm, thick air hits you in the face. It smells like mould, "
            "old carpet, urine, and something underneath it… something sweet and rotten."
            "\n\nA nurse approaches you immediately. Pale, shaking. "
            "'He's upstairs,' she whispers. 'Second floor. Room 214.' "
            "\nShe tries to smile, but her face collapses halfway through the attempt."
            "\n\nYou and your colleague walk up the narrow staircase, each step worse than the previous one. "
            "The smell intensifies rapidly. Something is wrong. Very wrong."
            "\n\nBy the time you reach the hallway of the second floor, "
            "your eyes are watering. You already know what's waiting for you inside that room."
            "\nYou haven't even opened the door yet, and you already feel your PCR hatred rising."
        )
        Interaction.show_outcome("+ 10 PCR HATRED (just for being here).")
        stats.increment_stats_pcr_hatred(10)
        continue_prompt()

        Interaction.print_text(
            "\nYour colleague opens the door to Room 214. "
              "The smell almost knocks you backward. The air inside looks thick — "
              "as if it gained texture, like a fog made of decay."
              "\n\nThere he is. A man in his 60s. Or what used to be him. "
              "He is lying in his bed, bloated, swollen beyond recognition, "
              "easily between 160 and 180 kilos of decomposing mass. "
              "His skin is greyish-green and pulled tight like an overfilled balloon."
              "\n\nYour older colleague — bald, dead inside, veteran of 1000 night shifts — looks at you and grins."
              "\n'This one’s yours, JB. I carried worse ones,' he says. "
              "He throws you a pair of thin latex gloves as if that would help you survive a chemical disaster."
              "\n\nYou have the following options:"
        )

        # Calculate avoidance chance: base 35% + 1% per 4 hatred points
        base_chance = 35
        hatred_bonus = stats.pcr_hatred // 4
        avoidance_chance = min(base_chance + hatred_bonus, 100)  # Cap at 100%
        
        # Display decision using Rich Panel with difficulty tags
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(avoidance_chance), "OBJECT — refuse to drag him."),
            ("2", Interaction.get_difficulty_tag(95), "ACCEPT AND DRAG HIM.")
        ])

        if select_choice == "1":
            refusal_roll = randint(1, 100)

            if refusal_roll <= avoidance_chance:
                Interaction.print_text(
                    "\nYou shake your head. 'No. I'm not dragging him. I'm not doing this.'"
                    "\nYour colleague stares at you for a long moment. His face doesn't move — "
                    "not a muscle, not a twitch — but something in his eyes softens."
                    "\nHe finally sighs, long and exhausted, like a man who has seen too much."
                    "\n'Fine… I'll get someone else. Just… wait outside.'"
                    "\nYou step back into the hallway, leaning against the peeling wall, "
                    "breathing through your mouth until your lungs stop screaming."
                )
                Interaction.show_outcome("you avoid dragging it...")
                continue_prompt()
                return

            else:
                stats.increment_stats_pcr_hatred(5)
                Interaction.print_text(
                    "\nYou take a step back and shake your head again. "
                      "'No, seriously. I can’t do this. I can't handle this one.'"
                      "\nYour colleague turns slowly — too slowly — and looks at you with an expression "
                      "you’ve seen on him a hundred times: disappointment mixed with superiority."
                      "\nThen he smirks. A small, cruel smirk."
                      "\n'That’s cute, JB,' he says. 'Really cute. But you're doing it anyway.'"
                      "\nHe taps your shoulder with the latex gloves, like he’s knighting you with a sword made of rubber."
                      "\n'Come on, princess. The sooner you touch him, the sooner we're done.'"
                      "\nThe other two officers in the hallway exchange looks. One of them chuckles. "
                      "You feel something hot rise in your stomach — humiliation, anger, something twisted between them."
                      "\nYou want to scream at them. You want to walk away. But you don’t."
                      "\nYou put on the gloves. They feel thin, useless — like wet paper on your hands."
                      "\nYour colleague mutters as he turns away: 'Unbelievable… I carried worse ones when I was your age.'"
                      "\nEvery word he says is gasoline poured onto the fire inside your chest."
                )
                Interaction.show_outcome("+5 PCR HATRED (your refusal was ignored and mocked).")
                continue_prompt()

        drag_roll = randint(1, 100)

        if drag_roll <= 5:
            stats.increment_stats_pcr_hatred(30)
            Interaction.print_text(
                "\nYou lift him and the worst happens. A wet tearing sound."
                "\nHis abdomen ruptures. Warm, thick fluids splash over your shoes and pants."
                "\nThe smell becomes a physical force pressing on your lungs."
                "\nYou freeze completely. Shock overrides everything. "
                "Your brain shuts down in self-defense."
                "\nYour colleague coughs a laugh: 'Yep… seen that before.'"
                "\nYou stare at the mess on your shoes, unable to move."
                "\n\nFUCK!!! FUCK!!! FUCK!!! FUCK!!! +30 PCR HATRED."
            )
            continue_prompt()
            return

        elif drag_roll <= 80:
            stats.increment_stats_pcr_hatred(15)
            Interaction.print_text(
                "\nYou and the team lift him. He’s heavy — unbelievably heavy — "
                  "but he doesn’t rupture."
                  "\nThe smell, the warmth, the texture of the room… it will stay in your mind forever."
                  "\nBut at least nothing spilled."
            )
            Interaction.show_outcome("+ 15 PCR HATRED.")
            continue_prompt()
            return

        else:
            stats.increment_stats_pcr_hatred(15)
            Interaction.print_text(
                "\nYou lift him carefully. Everything stays intact. "
                "Still a nightmare — but survivable."
            )
            Interaction.show_outcome("+ 15 PCR HATRED.")
            continue_prompt()

    @staticmethod
    def admin_mistake_after_shift(stats: Stats) -> None:
        """Event where you have to stay after night shift to fix an administrative mistake."""
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "It’s 07:00 in the morning. Your night shift is finally over… at least on paper."
              "\nYou feel like a ghost in uniform. Eyes burning, head heavy, body running only on caffeine and spite."
              "\nYou’re already imagining the moment you sit in your car, put on some music and just let your brain die "
              "for an hour on the way home."
              "\n\nYou walk towards the exit. As you pass the office corridor, you hear laughter."
              "\nDay shift has just arrived. Fresh, rested, smelling like showers and normal life."
              "\nThey’re cracking jokes about weekend, football, beer, kids. Like nothing is wrong with the world."
              "\nYou look at them and feel like you’re watching another species."
              "\n\nThen you hear it:"
              "\n'JB, come here for a moment.'"
              "\n\nYour boss is sitting behind his desk with a stack of papers. Not a good sign."
              "\nHe points to a report from the night. That horrible call you had at 03:17. "
              "The one you would rather forget completely."
              "\n'You made a mistake here,' he says calmly. 'This is done wrong. If someone from above sees this, "
              "you’ll get a penalty. You need to fix it. Today. Now.'"
              "\n\nYou glance at the clock. You’ve been here all night. "
              "Everyone else is just starting their nice little 7–15 shift. Full of energy. Full of life."
              "\nYou still have an hour of travel home ahead of you. And your brain already left the building."
              "\n\nYou have two options:"
        )

        # Display decision using Rich Panel with difficulty tags
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "TELL HIM YOU'RE DONE AND GO HOME (PAY THE PENALTY LATER). [-2500 CZK, PCR HATRED - 10]"),
            ("2", Interaction.get_difficulty_tag(), "STAY, FIX THE MISTAKE AND DESTROY WHAT'S LEFT OF YOUR SOUL. [PCR HATRED + 20]")
        ])

        if select_choice == "1":
            stats.increment_stats_value_money(-2500)
            stats.increment_stats_pcr_hatred(- 10)
            Interaction.print_text(
                "\nYou look at the papers. Then at your boss. Then back at the papers."
                  "\nSomething inside you just… snaps, but in a quiet way. Not dramatic. Just final."
                  "\n'No. I’m done for today,' you say. 'If there’s a penalty, I’ll pay it.'"
                  "\nYour boss stares at you, surprised. He expected begging, excuses, submissive guilt."
                  "\nInstead, he gets a calm, dead stare.\n"
                  "\nHe exhales through his nose, annoyed. 'Fine. I warned you. You’ll deal with the consequences.'"
                  "\nYou shrug. There’s nothing left to say."
                  "\nYou walk past the day shift, past their jokes and their fresh faces, like a ghost leaving a party "
                  "he was never invited to."
                  "\nOutside, the air is cold, but it feels… real. You know you'll lose some money. "
                  "But you also know you just saved at least a piece of your mind."
            )
            Interaction.show_outcome("- 2500 CZK, - 10 PCR HATRED.")
            continue_prompt()

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(20)
            Interaction.print_text(
                "\nYou swallow your pride, sit down and take the report."
                  "\nYour hands feel heavy. Your brain feels like wet concrete. But you start rewriting."
                  "\nYou correct forms, rewrite statements, adjust times, reprint attachments. "
                  "Your boss corrects you twice more, just to make sure you understand who’s in control here."
                  "\nIn the background, you can hear the day shift laughing in the dispatch room. "
                  "Someone is talking about a barbecue. Someone else is complaining about getting up at 6 AM."
                  "\nYou look at the clock. 08:30. 09:00. 09:30."
                  "\nEvery minute you stay here feels like someone is scraping sandpaper across your brain."
                  "\nFinally, you finish. Your boss glances at the report, nods once and says:"
                  "\n'Now it's correct. You can go.' No thank you. No appreciation. Just a checkbox ticked."
                  "\nYou walk out of the office feeling like a battery that someone squeezed dry."
                  "\nThe penalty won't come. But you know you paid with something else."
            )
            Interaction.show_outcome("+ 20 PCR HATRED.")
            continue_prompt()

    @staticmethod
    def israeli_developer(stats: Stats) -> None:
        """Event where you meet an Israeli senior developer who teaches CS at Tel Aviv University."""
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "You are standing at a small intersection somewhere in the middle of your district."
              "\nA light car crash happened — nothing serious, just enough to annoy you and create paperwork."
              "\nYou're managing the traffic with your glowing baton like a depressed Jedi when suddenly a man "
              "approaches you from the damaged vehicle."
              "\nHe looks completely calm, almost amused by the chaos around him."
              "\nHe has an accent you can't quite place at first, until he says:"
              "\n\n'You know, in Tel Aviv, traffic is *much* worse.'"
              "\n\nHe laughs. You don’t."
        )

        Interaction.print_text(
            "\nYou raise an eyebrow. 'Tel Aviv?'"
            "\n'Yes! I teach computer science there. Twenty-two years now. Came here for holiday… and someone "
            "forgot to use his brakes,' he says, pointing at the Czech driver from the second car, who now pretends "
            "he has never seen a steering wheel in his entire life."
            "\n\nYou ask him what he teaches."
            "\n'Algorithms. Systems architecture. Low-level optimization. And recently — machine learning basics.'"
            "\nHe shrugs. 'Students only want AI now. Nobody wants to understand pointers anymore.'"
        )

        Interaction.print_text(
            "\nHe looks at you with a sharp, analyzing gaze, ignoring your uniform entirely."
            "\n'You have intelligent eyes. You are not just a traffic cone stand. Tell me... do you write code?'"
        )

        can_code = stats.coding_skill >= 35

        if can_code:
            # Display decision using Rich Panel - both options available
            select_choice = Interaction.show_decision([
                ("1", Interaction.get_difficulty_tag(), "'Actually, I am something of a developer myself.' [SKILL CHECK >= 35 CODING SKILL: PASSED]"),
                ("2", Interaction.get_difficulty_tag(), "Stay silent. 'Me? No. I just... work here.' [IMPOSTER SYNDROME]")
            ])
        else:
            # Only option 2 available - skill check failed
            Interaction.print_text(f"\n[SKILL CHECK >= 35 CODING SKILL: LOCKED] (Current: {stats.coding_skill})")
            select_choice = Interaction.show_decision([
                ("2", Interaction.get_difficulty_tag(), "'Me? No. I just... work here.'")
            ])

        if select_choice == "1":
            stats.increment_stats_coding_skill(30)
            Interaction.print_text(
                "\nYou adjust your belt, look around to make sure your colleague isn't listening, and reply:"
                "\n'I work with Python. Backend mostly. Trying to get into AI integration.'"
                "\n\nThe Professor's eyes light up. 'Python? Good for prototyping. But tell me, how do you handle "
                "memory management when you scale? Do you understand what the Global Interpreter Lock actually does?'"
                "\n\nYou spend the next 20 minutes in a deep technical debate. He quizzes you, challenges you, "
                "and eventually nods in approval."
                "\n\n'Not bad,' he says. 'Actually, quite good. You have the mind for it. Why are you wearing this costume?'"
                "\nHe writes an email address on a piece of paper. 'Send me your GitHub. We always look for talent.'"
                "\n\nYou walk away feeling validated for the first time in years."
            )
            Interaction.show_outcome("+ 30 CODING SKILLS.")
            continue_prompt()

        elif select_choice == "2":
            stats.increment_stats_coding_skill(10)  # Small reward
            Interaction.print_text(
                "\nYou feel the words forming in your throat—'I study Python', 'I want to build apps'—but "
                "the fear chokes them down."
                "\n'Me? No,' you say, shaking your head. 'I just follow orders.'"
                "\n\nThe Professor looks disappointed for a split second, then shrugs."
                "\n'Pity. You have the look. Well, let me tell you something anyway...'"
                "\n\nHe gives you a short, precise monologue about problem-solving and abstraction layers."
                "\n'If you ever get tired of this job — and trust me, you will — learn to build things. "
                "Police officers preserve the status quo. Developers build the future.'"
                "\n\nYou listen. You learn something. But it hurts that you didn't speak up."
            )
            Interaction.show_outcome("+ 10 CODING SKILLS.")
            continue_prompt()

    @staticmethod
    def nightmare_wolf(stats: Stats) -> None:
        """
        Nightmare event based on a dream.
        """
        show_random_event_banner()
        continue_prompt()

        Interaction.print_text(
            "04:00 AM. You are on patrol. The world is grey and cold."
        )
        Interaction.print_text(
            "Dispatch sends you to an accident nearby. Routine procedure."
        )
        Interaction.print_text(
            "Your colleague drives. He doesn't say a word."
        )

        continue_prompt()

        Interaction.print_text(
            "Arrival. There are too many flashing lights for a simple crash."
        )
        Interaction.print_text(
            "You see the body bags lined up on the wet asphalt. Small ones."
        )
        Interaction.print_text(
            "\nYou look away, but you swear one of the bags moves."
        )
        Interaction.print_text(
            "Just a twitch. A hand pressing against the black plastic."
        )
        Interaction.print_text(
            "You look at the paramedic. He lights a cigarette and looks right through you."
        )
        Interaction.print_text(
            "You get back in the car. We are leaving."
        )

        continue_prompt()

        Interaction.print_text(
            "Back at the station. You walk into the main room."
        )
        Interaction.print_text(
            "She is sitting there."
        )
        Interaction.print_text(
            "\nThe woman from the briefing. The murderer. Black hair, calm hands."
        )
        Interaction.print_text(
            "She is sitting on the bench, un-cuffed, watching you."
        )

        Interaction.print_text(
            "\n'That's her,' you whisper. 'That's the fugitive.'"
        )
        Interaction.print_text(
            "\nYour colleagues stop drinking coffee. They look at you, then at the empty bench."
        )
        Interaction.print_text(
            "Then they start laughing."
        )
        Interaction.print_text(
            "'JB, you look like hell. Go wash your face.'"
        )

        continue_prompt()

        Interaction.print_text(
            "You point at the window. 'LOOK.'"
        )
        Interaction.print_text(
            "Standing outside, pressing its nose against the glass, is a Husky."
        )
        Interaction.print_text(
            "But it's wrong. It's too big. It's staring directly at you."
        )

        Interaction.print_text(
            "\n'Enough,' your colleague says. His voice is dead serious."
        )
        Interaction.print_text(
            "Before you can react, they grab you."
        )
        Interaction.print_text(
            "You struggle, but they force you into a chair. Duct tape over your mouth."
        )
        Interaction.print_text(
            "They aren't angry. They look... bored. Disappointed."
        )

        continue_prompt()

        Interaction.print_text(
            "You try to scream through the tape."
        )
        Interaction.print_text(
            "CRASH."
        )
        Interaction.print_text(
            "The window shatters. The Husky is inside."
        )
        Interaction.print_text(
            "\nIt doesn't bark. It just tears the first officer's throat out."
        )
        Interaction.print_text(
            "Blood sprays on the wall. The others don't even reach for their guns."
        )
        Interaction.print_text(
            "They just stand there and die."
        )

        Interaction.print_text(
            "\nThe Wolf turns to you. It walks over the bodies. It puts its face right next to yours."
        )
        Interaction.print_text(
            "You can smell its breath. Hot. Metallic."
        )

        continue_prompt()

        Interaction.print_text(
            "You wake up."
        )
        Interaction.print_text(
            "You are tangled in your sheets, soaking wet. Your heart is hammering against your ribs."
        )
        Interaction.print_text(
            "The room is silent. But you can still feel the phantom pressure of the tape on your mouth."
        )

        stats.increment_stats_pcr_hatred(10)
        Interaction.show_outcome("+ 10 PCR HATRED (Night terror).")
        continue_prompt()

    @staticmethod
    def citizen_of_czechoslovakia(stats: Stats) -> None:
        """
        Sovereign citizen of Czechoslovakia / Influencer event.
        """
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "You pull over a beat-up Felicia for a broken taillight. Routine stop."
        )
        Interaction.print_text(
            "As you approach the window, a phone is shoved into your face."
        )
        Interaction.print_text(
            "\n'AM I BEING DETAINED? AM I BEING DETAINED?' screams a teenager with a cracking voice."
        )
        Interaction.print_text(
            
            "'I am a free citizen of the Federal Republic of Czechoslovakia! The Czech Republic is a corporation!'"
        )
        Interaction.print_text(
            "\nHe is live-streaming to 12 viewers. He refuses to show ID because 'ID is a slave contract'."
        )

        # Display decision using Rich Panel with difficulty tags
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(), "Walk away. It's not worth the paperwork or the YouTube comments. [IGNORE]"),
            ("2", Interaction.get_difficulty_tag(), "Smash the window, drag him out. Law is Law. [ARREST]")
        ])

        if select_choice == "1":
            stats.increment_stats_pcr_hatred(15)
            Interaction.print_text(
                "\nYou sigh, turn off your body cam for a second to rub your eyes, and get back in your car."
            )
            Interaction.print_text(
                "The kid screams 'VICTORY!' as you drive away."
            )
            Interaction.print_text(
                "You saved 3 hours of paperwork, but you lost a piece of your soul."
            )
            Interaction.show_outcome("+ 15 PCR HATRED (Humiliation).")

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(5)
            stats.increment_stats_value_money(- 1000)
            Interaction.print_text(
                "\nYou've had enough. You break the window. He screams like a banshee."
            )
            Interaction.print_text(
                "You arrest him for obstruction."
            )
            Interaction.print_text(
                "\nLater, you find out his parents are lawyers. The paperwork takes 6 hours."
            )
            Interaction.print_text(
                "Your boss fines you for the 'unnecessary property damage' to the Felicia."
            )
            Interaction.show_outcome("- 1000 CZK (Fine), +5 PCR HATRED (At least you silenced him).")

        continue_prompt()

    @staticmethod
    def printer_incident(stats: Stats) -> None:
        """
        Printer event.
        """
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "The station's only printer—a relic from 2004—has jammed again."
        )
        Interaction.print_text(
            "There is a queue of 3 angry colleagues waiting to print their reports."
        )
        Interaction.print_text(
            "The 'IT Guy' is on vacation in Croatia for the next 2 weeks."
        )
        Interaction.print_text(
            "\nYou look at the error code: 'PC LOAD LETTER'."
        )

        success_chance = stats.coding_skill * 2
        if success_chance > 100: success_chance = 100

        # Display decision using Rich Panel with difficulty tags
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(success_chance), f"Try to fix the driver logic and spooler. [CODING CHECK: {success_chance}%]"),
            ("2", Interaction.get_difficulty_tag(), "Walk away. Not your problem. [IGNORE]")
        ])

        if select_choice == "1":
            roll = randint(1, 100)
            if roll <= success_chance:
                stats.increment_stats_coding_skill(10)
                Interaction.print_text(
                    "\nYou open the terminal interface. You bypass the spooler, clear the cache manually,"
                )
                Interaction.print_text(
                    "and restart the daemon. The printer roars to life."
                )
                Interaction.print_text(
                    "Your colleagues look at you like you just performed a miracle."
                )
                Interaction.print_text(
                    "\n[SUCCESS]: + 10 CODING SKILL (Real-world application)."
                )
            else:
                stats.increment_stats_value_money(- 2000)
                stats.increment_stats_pcr_hatred(15)
                Interaction.print_text(
                    "\nYou try to mess with the settings... and smoke starts coming out."
                )
                Interaction.print_text(
                    "It's hardlocked. Dead. Brick."
                )
                Interaction.print_text(
                    "The Commander comes out. 'JB, did you break government property?'"
                )
                Interaction.print_text(
                    "You have to pay for the repair service."
                )
                Interaction.print_text(
                    "\n[FAILURE]: - 2000 CZK, + 15 PCR HATRED."
                )

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(5)
            Interaction.print_text(
                "\nYou decide not to risk it. You hand write your report."
            )
            Interaction.print_text(
                "It takes 45 minutes longer."
            )
            Interaction.show_outcome("+5 PCR HATRED.")

        continue_prompt()

    @staticmethod
    def forgotten_usb(stats: Stats) -> None:
        """
        USB Stick event
        """
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "You are patting down a suspect's jacket in the evidence locker."
        )
        Interaction.print_text(
            "You feel a lump. It's a black USB drive with a taped label: 'DO NOT TOUCH'."
        )
        Interaction.print_text(
            "Curiosity kills the cat... but satisfaction brought it back."
        )

        # Display decision using Rich Panel with difficulty tags (50% chance for USB risk)
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(50), "Plug it into your own personal laptop. [RISK]"),
            ("2", Interaction.get_difficulty_tag(), "Don't touch it. [SAFE]")
        ])

        if select_choice == "1":
            Interaction.print_text(
                "\nYou boot up your laptop and insert the drive..."
            )
            roll = randint(1, 100)

            if roll <= 50:
                stats.increment_stats_coding_skill(-25)
                Interaction.print_text(
                    "\nSCREEECH! Your speakers blast noise."
                )
                Interaction.print_text(
                    "A skull appears on your screen. All your Python projects are being encrypted."
                )
                Interaction.print_text(
                    "It's a nasty ransomware. You have to format everything."
                )
                Interaction.print_text(
                    "\n[FAILURE]: - 25 CODING SKILL (You lost your projects)."
                )
            else:
                stats.increment_stats_value_money(25000)
                Interaction.print_text(
                    "\nIt opens. A text file contains a private key."
                )
                Interaction.print_text(
                    "You check the wallet... there is some leftover Ethereum!"
                )
                Interaction.print_text(
                    "You quickly transfer it to your account."
                )
                Interaction.print_text(
                    "\n[SUCCESS]: + 25.000 CZK."
                )

        elif select_choice == "2":
            Interaction.print_text(
                "\nYou leave it in the evidence room. Probably for the best."
            )

        continue_prompt()

    @staticmethod
    def turkish_fraud(stats: Stats) -> None:
        """
        Internet Fraud / Heritage scam.
        """
        success_chance = stats.coding_skill * 2
        if success_chance >= 100:
            success_chance = 100
        roll = randint(1, 100)

        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "An old man comes to the station, shaking and crying."
        )
        Interaction.print_text(
            "'They stole my money! My uncle died in Turkey! He was a billionaire!'"
        )
        Interaction.print_text(
            "\nYou listen to the story. It's the classic 'Prince Heritage' scam."
        )
        Interaction.print_text(
            "The victim sent 100.000 CZK to an account in Istanbul to 'release the funds'."
        )
        Interaction.print_text(
            "\nUsually, you would just file a report and file it into the trash."
        )
        Interaction.print_text(
            "But you look at the email headers the victim printed out."
        )
        Interaction.print_text(
            "You recognize the IP masking. It's lazy."
        )

        # Display decision using Rich Panel with difficulty tags
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(success_chance), f"Track the scammer and turn the tables. [CODING] [ROLL CHANCE: {success_chance}%] Current coding skill: {stats.coding_skill}"),
            ("2", Interaction.get_difficulty_tag(), "'I'm sorry sir, the money is gone.' [GENERIC]")
        ])

        if select_choice == "1":
            if success_chance >= roll:
                stats.daily_btc_income += 2500
                stats.increment_stats_pcr_hatred(- 20)
                Interaction.print_text(
                    "\nYou tell the old man to wait. You open your laptop."
                )
                Interaction.print_text(
                    "You trace the packet route, bypass their cheap VPN, and find their real server."
                )
                Interaction.print_text(
                    "You access their webcam. You take a screenshot of the scammer."
                )
                Interaction.print_text(
                    
                    "\nYou send them one email: 'I know who you are. Send me 5k CZK a day in BTC, or I send this to the Turkish police.'"
                )
                Interaction.print_text(
                    "\nFive minutes later, your wallet pings."
                )
                Interaction.print_text(
                    "\n[SUCCESS]: You gained PASSIVE INCOME! (+ 2.500 CZK Daily), - 20 PCR HATRED"
                )
                Interaction.print_text(
                    "You tell the old man you'll 'look into it' and send him home."
                )
            else:
                Interaction.print_text(
                    "\nYou try to track them, but their encryption is too good."
                )
                Interaction.print_text(
                    "On top of that, the fraudster noticed you are trying to hack him,."
                )
                Interaction.print_text(
                    "So he returned the favor - he broke into your bank account and stole some of your money.."
                )
                Interaction.print_text(
                    "This didn't went well."
                )
                Interaction.print_text(
                    "You have to tell the old man the truth that his money is lost - just as yours."
                )
                stats.increment_stats_pcr_hatred(10)
                stats.increment_stats_value_money(-2500)
                stats.increment_stats_coding_skill(- 10)
                Interaction.print_text(
                    "\n[FAILURE]: + 10 PCR HATRED. - 10 CODING SKILLS, - 2500 CZK"
                )

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(10)
            Interaction.print_text(
                "\nYou explain to him that the billionaire uncle doesn't exist."
            )
            Interaction.print_text(
                "He cries. You watch. It's just another Tuesday."
            )
            Interaction.show_outcome("+ 10 PCR HATRED.")

        continue_prompt()

    @staticmethod
    def dispatch_blue_screen(stats: Stats) -> None:
        """
        The Dispatch System Crash.
        """
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "It is Friday night. The radio is screaming. Total chaos."
        )
        Interaction.print_text(
            "Suddenly, the main dispatch monitor flickers and dies."
        )
        Interaction.print_text(
            "\nBSOD. 'CRITICAL_PROCESS_DIED'."
        )
        Interaction.print_text(
            "\nThe Commander starts hitting the monitor with his baton."
        )
        Interaction.print_text(
            "'IT SUPPORT IS CLOSED! WE ARE BLIND!'"
        )

        # Display decision using Rich Panel - show both options (skill check happens in logic)
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag() if stats.coding_skill >= 30 else Interaction.get_difficulty_tag(0), f"Push him aside and fix it via PowerShell. [CODING] [REQ: 30 CODING SKILL] Current: {stats.coding_skill}"),
            ("2", Interaction.get_difficulty_tag(), "Watch it burn. Enjoy the silence. [CHAOS]")
        ])

        if select_choice == "1":
            if stats.coding_skill >= 30:
                stats.increment_stats_pcr_hatred(- 10)
                stats.increment_stats_coding_skill(5)
                Interaction.print_text(
                    "\nYou type `Restart-Service DispatchCore -Force`."
                )
                Interaction.print_text(
                    "The screen flickers back to life. The map reloads."
                )
                Interaction.print_text(
                    "The Commander stares at you. 'Good work, JB.'"
                )
                Interaction.print_text(
                    "For a moment, you feel useful."
                )
                Interaction.print_text(
                    "\n[SUCCESS]: - 10 PCR HATRED, + 5 CODING SKILL."
                )
            else:
                stats.increment_stats_pcr_hatred(10)
                Interaction.print_text(
                    "\nYou try to open the terminal, but your hands are shaking."
                )
                Interaction.print_text(
                    "The Commander yells: 'GET OUT OF THE WAY!'"
                )
                Interaction.print_text(
                    "You failed to help. Now you just look like an idiot."
                )
                Interaction.print_text(
                    "\n[FAILURE]: + 10 PCR HATRED."
                )

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(-5)
            Interaction.print_text(
                "\nYou sip your coffee."
            )
            Interaction.print_text(
                "Without the dispatch software, no one can send you anywhere."
            )
            Interaction.print_text(
                "For 20 minutes, there is peace."
            )
            Interaction.show_outcome("- 5 PCR HATRED (Schadenfreude).")

        continue_prompt()

    @staticmethod
    def tech_bro_speeding(stats: Stats) -> None:
        """
        Event: Help your fellow dev.
        """
        success_chance = (stats.coding_skill * 100) // 70

        if success_chance >= 100:
            success_chance = 100

        roll = randint(1, 100)

        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "You notice a Porsche Taycan doing 150 km/h in a 90 zone."
        )
        Interaction.print_text(
            
            "You pull him over - It's a dude in his early 20s, wearing Patagonia vest and Matcha Latte in his cup holder."
        )
        Interaction.print_text(
            "On a seat next to him is a MacBook Pro with opened interactive development environment."
        )
        Interaction.print_text(
            "This guy is clearly a [bold]Developer[/bold]"
        )
        Interaction.print_text(
            
            "'Can you hurry up? I have to push this into production, else my CTO will kill me.'"
        )
        Interaction.print_text(
            "He shoves a laptop in your face. It's a terminal. Red text everywhere."
        )

        # Display decision using Rich Panel with difficulty tags
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag(success_chance), f"'I can help you with that.' [CODING] [ROLL CHANCE: {success_chance}%] Current coding skill: {stats.coding_skill}"),
            ("2", Interaction.get_difficulty_tag(), "'License and registration. Now.' [DUTY]")
        ])

        if select_choice == "1":
            if success_chance >= roll:
                stats.increment_stats_coding_skill(15)
                Interaction.print_text(
                    "\n'It's a SyntaxError on line 84 but I can't see it!' he yells, tearing his hair out."
                )
                Interaction.print_text(
                    "You lean in, squinting at the glowing code. It's a mess of logic."
                )
                Interaction.print_text(
                    "'There,' you point with a gloved finger. 'The `if` statement.'"
                )
                Interaction.print_text(
                    "'What? The logic is sound!'"
                )
                Interaction.print_text(
                    "'The logic is fine. You missed the colon at the end. Typical speeding mistake.'"
                )
                Interaction.print_text(
                    "\nYou tap the ':' key once. The red error text turns green. The build passes."
                )
                Interaction.print_text(
                    "\nThe driver freezes. He looks at the screen, then at your uniform, then at the screen again."
                )
                Interaction.print_text(
                    "'...Dude...who are you?'"
                )
                Interaction.print_text(
                    "'I'm just a guy who likes his syntax clean. Drive safe.'"
                )
                Interaction.print_text(
                    "He drives away slowly, absolutely terrified of your attention to detail."
                )
                Interaction.print_text(
                    "\n[SUCCESS]: + 15 CODING SKILL (Syntax Sniper)."
                )
            else:
                stats.increment_stats_pcr_hatred(5)
                stats.increment_stats_coding_skill(-5)
                Interaction.print_text(
                    "\n'Let me handle this,' you say with confidence, channeling 'The Matrix'."
                )
                Interaction.print_text(
                    "You start typing furiously, mashing keys to look professional."
                )
                Interaction.print_text(
                    "'I'm just bypassing the firewall algorithms...' you mumble."
                )
                Interaction.print_text(
                    "'Dude, what are you doing? Stop! That's my delete key!'"
                )
                Interaction.print_text(
                    "\nYou hit 'Enter' with a dramatic flourish."
                )
                Interaction.print_text(
                    "The screen goes blank. A single message appears: [REPOSITORY DELETED]."
                )
                Interaction.print_text(
                    "\n'DID YOU JUST DELETE MY ENTIRE STARTUP??'"
                )
                Interaction.print_text(
                    "'Technically,' you shrug, 'The bug is gone.'"
                )
                Interaction.print_text(
                    "'BECAUSE THE CODE IS GONE! You maniac!'"
                )
                Interaction.print_text(
                    "He drifts off, screaming into his matcha latte."
                )
                Interaction.print_text(
                    "\n[FAILURE]: + 5 PCR HATRED, -5 CODING SKILL. (You are not the guy yet)"
                )

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(5)
            Interaction.print_text(
                "\nYou ignore his laptop and write him a ticket for 2000 CZK."
            )
            Interaction.print_text(
                "'Typical,' he mutters, scanning the payment QR code."
            )
            Interaction.print_text(
                "His hourly rate is probably your monthly salary"
            )
            Interaction.print_text(
                "He zooms off."
            )
            Interaction.show_outcome("+ 5 PCR HATRED.")

        continue_prompt()

    @staticmethod
    def paperwork_overload(stats: Stats) -> None:
        """
        Event: The Paperwork Mountain.
        Mechanic: Unlockable Daily Buff (AI Automation).
        """
        show_random_event_banner()
        continue_prompt()
        Interaction.print_text(
            "You walk into the office. Your desk is gone."
        )
        Interaction.print_text(
            "It has been replaced by a literal tower of files. Theft reports, accidents, lost dogs."
        )
        Interaction.print_text(
            "The admin lady smirks. 'Boss wants this done by tomorrow morning.'"
        )
        Interaction.print_text(
            "\nIt looks like 12 hours of manual data entry. A nightmare."
        )

        # Display decision using Rich Panel - show both options (skill check happens in logic)
        select_choice = Interaction.show_decision([
            ("1", Interaction.get_difficulty_tag() if stats.coding_skill >= 40 else Interaction.get_difficulty_tag(0), f"'Fuck it.' Write a Python script to automate the forms. [CODING] [REQ: 40 CODING SKILL] Current: {stats.coding_skill}"),
            ("2", Interaction.get_difficulty_tag(), "Grind through it. Suffering is part of the job. [MANUAL]")
        ])

        if select_choice == "1":
            if stats.coding_skill >= 40:
                stats.ai_paperwork_buff = True
                stats.increment_stats_coding_skill(5)
                Interaction.print_text(
                    "\nYou lock the door. You open your laptop."
                )
                Interaction.print_text(
                    "You write a scraper using Selenium and a text-filler script."
                )
                Interaction.print_text(
                    "You hit ENTER. The computer starts doing the work for you."
                )
                Interaction.print_text(
                    "You spend the rest of the shift drinking coffee and watching the progress bar."
                )
                Interaction.print_text(
                    "\n[CRITICAL SUCCESS]: AI AUTOMATION UNLOCKED!"
                )
                Interaction.print_text(
                    "Your script will now handle reports daily. ( - 5 Hatred daily for the rest of the game)."
                )
            else:
                stats.increment_stats_pcr_hatred(20)
                Interaction.print_text(
                    "\nYou try to automate it, but you mess up the regex."
                )
                Interaction.print_text(
                    "The script fills every form with 'NULL'."
                )
                Interaction.print_text(
                    "You have to redo EVERYTHING by hand. It takes all night."
                )
                Interaction.print_text(
                    "\n[FAILURE]: + 20 PCR HATRED."
                )

        elif select_choice == "2":
            stats.increment_stats_pcr_hatred(20)
            Interaction.print_text(
                "\nYou sit down. You pick up a pen."
            )
            Interaction.print_text(
                "Name. Date. Incident. Signature."
            )
            Interaction.print_text(
                "Name. Date. Incident. Signature."
            )
            Interaction.print_text(
                "By 4 AM, you forgot your own name."
            )
            Interaction.show_outcome("+ 20 PCR HATRED.")

        continue_prompt()
