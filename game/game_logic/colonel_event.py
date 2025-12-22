import sys
import time
import os
import random
import pygame
from game.game_logic.stats import Stats
from game.game_logic.decision_options import Decision
from game.game_logic.game_endings import GoodEnding


def resource_path(relative_path):
    """ Get absolute path to resource (Works for Dev & EXE) """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class ColonelEvent:
    """
    The Final Boss Event.
    Triggered on Day 25 or Day 30.
    Includes the 'System Glitch' mechanic leading to the Good Ending.
    """

    def __init__(self):
        self.jb_hp = 100
        self.colonel_hp = 100
        self.red = "\033[91m"
        self.green = "\033[92m"
        self.blue = "\033[94m"
        self.bold = "\033[1m"
        self.reset = "\033[0m"

    def _play_music(self, track_name):
        """Helper to play music tracks smoothly."""
        try:
            music_path = resource_path(track_name)
            pygame.mixer.init()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            pygame.mixer.music.set_volume(0.3)
        except Exception as e:
            print(f"\n[SYSTEM] Audio Warning: Could not play music '{track_name}' ({e})")

    def _slow_print(self, text, delay=0.04, bold=False, color=None):
        if color:
            sys.stdout.write(color)
        if bold:
            sys.stdout.write(self.bold)

        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)

        sys.stdout.write(self.reset)
        print()

    def _draw_hp_bar(self, current_hp, max_hp=100):
        blocks = int(current_hp / 10)
        blocks = max(0, min(10, blocks))
        empty_blocks = 10 - blocks
        bar_visual = "■" * blocks + "□" * empty_blocks
        return f"[{bar_visual}] {current_hp}/{max_hp} HP"

    def _print_hud(self, round_name):
        print("\n" + "=" * 50)
        print(f" {self.bold}{round_name.upper()}{self.reset}")
        print("=" * 50)
        print(f"{self.green}JB      {self._draw_hp_bar(self.jb_hp)}{self.reset}")
        print(f"{self.red}COLONEL {self._draw_hp_bar(self.colonel_hp)}{self.reset}")
        print("-" * 50 + "\n")
        time.sleep(1)

    def trigger_event(self, stats: Stats):
        # --- MUSIC START: TENSION THEME ---
        self._play_music("tension_theme.mp3")

        # --- INITIALIZATION PHASE ---
        if stats.final_boss_buff == "LEGAL_NUKE":
            self.colonel_hp -= 35
            print(f"\n{self.green}[PASSIVE]: 'Legal Nuke' applied. Colonel starts with -35 HP.{self.reset}")
        elif stats.final_boss_buff == "FIRST_STRIKE":
            self.colonel_hp -= 20
            print(f"\n{self.green}[PASSIVE]: 'Aggressive Opening' applied. Colonel starts with -20 HP.{self.reset}")
        elif stats.final_boss_buff == "IMPOSTER_SYNDROME":
            print(f"\n{self.red}[WARNING]: You have Imposter Syndrome. You are vulnerable.{self.reset}")

        input("\n(PRESS ENTER TO BEGIN THE END)")

        self._round_one(stats)
        self._round_two(stats)
        self._round_three_logic(stats)

        return

    def _round_one(self, stats):
        self._print_hud("Round 1")
        self._slow_print("It is early morning. You hand your superior the resignation.", delay=0.03)
        self._slow_print("'I need to call the Colonel.'", delay=0.05, color=self.red)
        time.sleep(1)
        self._slow_print("\nThree hours later, the black Superb arrives. He sits inside for 5 minutes.", delay=0.04)

        good_buffs = ["STOIC_ANCHOR", "LEGAL_NUKE", "GHOST_SECRET", "JOB_OFFER", "STOIC_HEAL", "FIRST_STRIKE"]
        if stats.final_boss_buff in good_buffs:
            self._slow_print(f"\n{self.green}[DEFENSE]: You remember MM's advice. You stay calm. (0 DMG){self.reset}",
                             delay=0.02)
        else:
            self.jb_hp -= 10
            self._slow_print(f"\n{self.red}[ANXIETY HIT]: The waiting is torture. (-10 HP){self.reset}", delay=0.02)
        input("\n(PRESS ENTER)")

    def _round_two(self, stats):
        self._print_hud("Round 2")
        self._slow_print("He enters. The room goes silent. Your colleagues look down.", delay=0.03)

        if stats.final_boss_buff == "IMPOSTER_SYNDROME":
            self.jb_hp -= 10
            self._slow_print(f"\n{self.red}[DEBUFF]: You feel like a fraud. (-10 HP){self.reset}", delay=0.02)
        else:
            self._slow_print(f"\n{self.green}[STOIC]: You hold his gaze.{self.reset}", delay=0.02)
        input("\n(PRESS ENTER)")

    def _round_three_logic(self, stats):
        # --- MUSIC SWITCH: ARRIVAL ---
        self._play_music("colonel_arrives.mp3")

        self._slow_print("He invites you upstairs. He makes coffee. The silence is heavy.", delay=0.04)
        self._slow_print("'Black? Two sugars?' he asks.", delay=0.03)
        self._slow_print("Then, he attacks.", delay=0.05, bold=True)
        input("\n(PRESS ENTER)")

        attacks = [
            self._attack_money_check,
            self._attack_why_quit,
            self._attack_civilian_void,
            self._attack_brotherhood,
            self._attack_safety_net,
            self._attack_debt_of_honor,
            self._attack_blacklist
        ]
        random.shuffle(attacks)
        round_counter = 3

        for attack_func in attacks:
            if self.jb_hp <= 0 or self.colonel_hp <= 0:
                break

            self._print_hud(f"Round {round_counter}")
            attack_func(stats)
            round_counter += 1
            input("\n(PRESS ENTER TO CONTINUE)")

        self._check_fight_outcome(stats)

    # -------------------------------------------------------------------------
    # ATTACK METHODS
    # -------------------------------------------------------------------------

    def _attack_money_check(self, stats):
        """Attack 1: The Training Debt."""
        self._slow_print(
            f"\n{self.red}[COLONEL ATTACK]: 'You know you have to return the money for your training, JB?'{self.reset}",
            delay=0.04)

        if stats.final_boss_buff == "LEGAL_NUKE":
            self._slow_print(f"\n{self.green}[AUTO-COUNTER]: You slap the file MM gave you on the table.{self.reset}",
                             delay=0.03)
            self._slow_print("'Paragraph 4B, Colonel. The debt is void.'", delay=0.03)
            self._slow_print("The Colonel chokes on his coffee. He is furious.", delay=0.03)
            self.colonel_hp -= 15
            self._slow_print(f"{self.green}[CRITICAL]: Colonel takes -15 HP DMG!{self.reset}")
            return

        self._slow_print(f"He smiles coldly. '80,000 CZK. Immediately. Or I call the lawyers.'", delay=0.03)
        self._slow_print(f"Your Savings: {stats.available_money} CZK", delay=0.01)

        options = []
        if stats.available_money >= 200000:
            options.append("1. [PAY 80k] 'Here. Keep the change.' (Deals 20 HP DMG)")
            options.append("2. [SHOW BALANCE] 'I have enough to bury you in court.' (Deals 10 HP DMG, Save Money)")

        if not options:
            self._slow_print("\n[PANIC]: You don't have enough to feel safe (Need >200k).", delay=0.02)
            self._slow_print("1. [STAMMER] 'I... I will pay you later.'", delay=0.02)
            choice = Decision.ask(("1",))
            self.jb_hp -= 10
            self._slow_print(f"\n{self.red}[FAILURE]: He sees your fear. You take -10 HP DMG.{self.reset}")
        else:
            for opt in options:
                print(opt)

            choice = Decision.ask(("1", "2"))

            if choice == "1":
                stats.available_money -= 80000
                self.colonel_hp -= 20
                self._slow_print(
                    f"\n{self.green}[DOMINANCE]: You throw the money on the table. He is shocked.{self.reset}")
                self._slow_print(f"{self.green}Colonel takes -20 HP DMG.{self.reset}")
            elif choice == "2":
                self.colonel_hp -= 10
                self._slow_print(
                    f"\n{self.green}[STOIC]: You show him your account app. He realizes he can't threaten you.{self.reset}")
                self._slow_print(f"{self.green}Colonel takes -10 HP DMG.{self.reset}")

    def _attack_why_quit(self, stats):
        """Attack 2: The Motivation Check."""
        self._slow_print(
            f"\n{self.red}[COLONEL ATTACK]: 'Why, JB? After everything I did for you. Why are you quitting?'{self.reset}",
            delay=0.04)

        chance_hatred = int(stats.pcr_hatred * 0.5)
        chance_coding = int(stats.coding_skill / 2)
        chance_money = int(stats.available_money / 3000)

        print(f"\nCHOOSE YOUR DEFENSE:")
        print(f"1. [HATRED] 'I had enough of this sh*t.' (Success Chance: {chance_hatred}%)")
        print(f"2. [CODING] 'I build worlds now. I don't need this.' (Success Chance: {chance_coding}%)")
        print(f"3. [MONEY] 'I can buy my own freedom.' (Success Chance: {chance_money}%)")

        valid_choices = ["1", "2", "3"]
        if stats.final_boss_buff == "JOB_OFFER":
            print(f"4. [MM OFFER] 'MM has a job waiting for me.' (Guaranteed 20 DMG)")
            valid_choices.append("4")

        choice = Decision.ask(tuple(valid_choices))

        if choice == "4":
            self.colonel_hp -= 20
            self._slow_print(
                f"\n{self.green}[PERK]: You mention the job offer. His control over you vanishes.{self.reset}")
            self._slow_print(f"{self.green}Colonel takes -20 HP DMG.{self.reset}")
            return

        roll = random.randint(1, 100)
        success_chance = 0
        dmg_type = ""

        if choice == "1":
            success_chance = chance_hatred
            dmg_type = "Pure Rage"
        elif choice == "2":
            success_chance = chance_coding
            dmg_type = "Logic Bomb"
        elif choice == "3":
            success_chance = chance_money
            dmg_type = "Financial Shield"

        self._slow_print(f"\n[ROLLING]: Rolled: {roll}", delay=0.05)

        if roll <= success_chance:
            bonus_damage = max(0, success_chance - 100)
            damage = 20 + bonus_damage

            self.colonel_hp -= damage
            self._slow_print(f"\n{self.green}[SUCCESS]: Your {dmg_type} hits him hard!{self.reset}")
            self._slow_print(
                f"{self.green}CRITICAL STRIKE: 20 Base + {bonus_damage} Bonus (Excess Chance) = {damage} DMG!{self.reset}")
        else:
            self.jb_hp -= 20
            self._slow_print(f"\n{self.red}[FAILURE]: Your voice cracks. He smells weakness.{self.reset}")
            self._slow_print(f"{self.red}You take -20 HP DMG.{self.reset}")

    def _attack_civilian_void(self, stats):
        """Attack 3: The Fear of Irrelevance."""
        self._slow_print(
            f"\n{self.red}[COLONEL ATTACK]: 'You think you can survive out there? Without the badge, you are nobody.'{self.reset}",
            delay=0.04)
        self._slow_print(
            "'Here, people fear you. Respect you. Out there? You are just another civilian waiting in line.'",
            delay=0.03)

        print("\nCHOOSE YOUR DEFENSE:")
        print("1. [CODING] 'I don't need their fear. I have skills that build the future.'")
        print("2. [HATRED] 'I'd rather be a nobody than a tyrant like you.'")
        print("3. [DOUBT] 'Maybe... maybe I will miss the authority.'")

        choice = Decision.ask(("1", "2", "3"))

        if choice == "1":
            if stats.coding_skill >= 100:
                self.colonel_hp -= 20
                self._slow_print(
                    f"\n{self.green}[SUCCESS]: You laugh. 'I write the logic that runs your world.' He looks confused.{self.reset}")
                self._slow_print(f"{self.green}Colonel takes -20 HP DMG.{self.reset}")
            else:
                self.jb_hp -= 15
                self._slow_print(
                    f"\n{self.red}[FAILURE]: You stutter. You aren't good enough at coding yet to believe it.{self.reset}")
                self._slow_print(f"{self.red}You take -15 HP DMG.{self.reset}")

        elif choice == "2":
            if stats.pcr_hatred >= 60:
                self.colonel_hp -= 15
                self._slow_print(
                    f"\n{self.green}[RAGE]: Your hatred burns brighter than his rank. He steps back.{self.reset}")
                self._slow_print(f"{self.green}Colonel takes -15 HP DMG.{self.reset}")
            else:
                self.jb_hp -= 10
                self._slow_print(
                    f"\n{self.red}[WEAKNESS]: You don't sound convinced. You still crave the power.{self.reset}")
                self._slow_print(f"{self.red}You take -10 HP DMG.{self.reset}")

        elif choice == "3":
            self.jb_hp -= 20
            self._slow_print(f"\n{self.red}[SUBMISSION]: You admit it. He smiles predatorily.{self.reset}")
            self._slow_print(f"{self.red}You take -20 HP DMG.{self.reset}")

    def _attack_brotherhood(self, stats):
        """Attack 4: The Guilt Trip about Colleagues."""
        self._slow_print(
            f"\n{self.red}[COLONEL ATTACK]: 'And what about your team? Lieutenant? The rookies?'{self.reset}",
            delay=0.04)
        self._slow_print("'You are abandoning them in the trenches. They will rot in overtime because YOU left.'",
                         delay=0.03)

        if stats.final_boss_buff == "STOIC_ANCHOR":
            self._slow_print(
                f"\n{self.green}[PASSIVE]: Stoic Anchor active. You realize everyone is responsible for their own life.{self.reset}",
                delay=0.03)
            self._slow_print("'They have the same choice I do, Colonel.'")
            self.colonel_hp -= 10
            self._slow_print(f"{self.green}Colonel takes -10 HP DMG.{self.reset}")
            return

        print("\nCHOOSE YOUR DEFENSE:")
        print("1. [COLD] 'They are colleagues, not family. It's just a job.'")
        print("2. [EMPATHY] 'I... I feel bad for them. But I have to save myself.'")

        choice = Decision.ask(("1", "2"))

        if choice == "1":
            if stats.pcr_hatred >= 50:
                self.colonel_hp -= 15
                self._slow_print(f"\n{self.green}[TRUTH]: 'The system failed them, Colonel. Not me.'{self.reset}")
                self._slow_print(f"{self.green}Colonel takes -15 HP DMG.{self.reset}")
            else:
                self.jb_hp -= 15
                self._slow_print(f"\n{self.red}[GUILT]: You lie. You will miss them. The guilt hits you.{self.reset}")
                self._slow_print(f"{self.red}You take -15 HP DMG.{self.reset}")

        elif choice == "2":
            self.jb_hp -= 10
            self._slow_print(f"\n{self.red}[PAIN]: It hurts to admit. He sees your hesitation.{self.reset}")
            self._slow_print(f"{self.red}You take -10 HP DMG.{self.reset}")

    def _attack_safety_net(self, stats):
        """Attack 5: The Golden Handcuffs (Pension/Benefits)."""
        self._slow_print(
            f"\n{self.red}[COLONEL ATTACK]: 'You are a fool. The pension! The benefits! The stability!'{self.reset}",
            delay=0.04)
        self._slow_print("'You are throwing away a guaranteed future for... what? Coding scripts?'", delay=0.03)

        print("\nCHOOSE YOUR DEFENSE:")
        print("1. [MONEY] 'I have enough savings to be my own pension.'")
        print("2. [FREEDOM] 'I'd rather starve free than eat well in a cage.'")

        choice = Decision.ask(("1", "2"))

        if choice == "1":
            if stats.available_money >= 150000:
                self.colonel_hp -= 25
                self._slow_print(
                    f"\n{self.green}[WEALTH]: You mention your savings. His jaw tightens. He can't buy you.{self.reset}")
                self._slow_print(f"{self.green}CRITICAL HIT: Colonel takes -25 HP DMG.{self.reset}")
            else:
                self.jb_hp -= 15
                self._slow_print(
                    f"\n{self.red}[POOR]: You bluff, but you know you'll be broke in 3 months.{self.reset}")
                self._slow_print(f"{self.red}You take -15 HP DMG.{self.reset}")

        elif choice == "2":
            self.colonel_hp -= 10
            self._slow_print(
                f"\n{self.green}[PHILOSOPHY]: A bit dramatic, but effective. He hates your independence.{self.reset}")
            self._slow_print(f"{self.green}Colonel takes -10 HP DMG.{self.reset}")

    def _attack_debt_of_honor(self, stats):
        """Attack 6: The Personal Debt (Car Incident)."""
        self._slow_print(f"\n{self.red}[COLONEL ATTACK]: 'Have you forgotten the car accident, JB?'{self.reset}",
                         delay=0.05)
        self._slow_print("'I buried the internal investigation. I saved your badge. You OWE me.'", delay=0.04)

        if stats.final_boss_buff == "GHOST_SECRET":
            print(f"\n{self.blue}>> [OPPORTUNITY]: USE 'GHOST OF THE PAST' SECRET <<{self.reset}")
            print("1. [BLACKMAIL] 'Like you buried your resignation 10 years ago?'")
            print("2. [DEFENSIVE] 'I repaid that debt with 3 years of service.'")

            choice = Decision.ask(("1", "2"))

            if choice == "1":
                self.colonel_hp -= 40
                self._slow_print(
                    f"\n{self.green}[DEVASTATION]: You say it. The room drops to absolute zero.{self.reset}")
                self._slow_print("He freezes. His deepest insecurity exposed. He looks old suddenly.")
                self._slow_print(f"{self.green}FATAL STRIKE: Colonel takes -40 HP DMG.{self.reset}")
                return

        else:
            print("\nCHOOSE YOUR DEFENSE:")
            print("1. [DEFENSIVE] 'I repaid that debt with 3 years of flawless service.'")
            print("2. [SUBMIT] 'I know... and I am grateful. But I have to go.'")

            choice = Decision.ask(("1", "2"))

            if choice == "1":
                self.colonel_hp -= 5
                self._slow_print(
                    f"\n{self.green}[NEUTRAL]: He grunts. He knows you worked hard, but he feels cheated.{self.reset}")
                self._slow_print(f"{self.green}Colonel takes -5 HP DMG.{self.reset}")
            elif choice == "2":
                self.jb_hp -= 20
                self._slow_print(f"\n{self.red}[GUILT]: The emotional debt weighs you down.{self.reset}")
                self._slow_print(f"{self.red}You take -20 HP DMG.{self.reset}")

    def _attack_blacklist(self, stats):
        """Attack 7: The Blacklist Threat."""
        self._slow_print(f"\n{self.red}[COLONEL ATTACK]: 'I will make calls. I will ruin you.'{self.reset}", delay=0.04)
        self._slow_print("'No security firm. No state agency. You will never work in this town again.'", delay=0.04)

        if stats.final_boss_buff == "JOB_OFFER":
            self._slow_print(f"\n{self.green}[AUTO-COUNTER]: You smile. 'MM already hired me, Colonel.'{self.reset}",
                             delay=0.03)
            self._slow_print("'Your threats don't work on the private sector.'")
            self.colonel_hp -= 30
            self._slow_print(f"{self.green}CRITICAL HIT: Colonel takes -30 HP DMG.{self.reset}")
            return

        print("\nCHOOSE YOUR DEFENSE:")
        print("1. [CONFIDENCE] 'I'm not looking for security work. I'm a Developer.'")
        print("2. [SCARE] 'Are you threatening a civilian? Careful, Colonel.'")

        choice = Decision.ask(("1", "2"))

        if choice == "1":
            if stats.coding_skill >= 50:
                self.colonel_hp -= 15
                self._slow_print(
                    f"\n{self.green}[PIVOT]: You reject his entire premise. He has no power over IT.{self.reset}")
                self._slow_print(f"{self.green}Colonel takes -15 HP DMG.{self.reset}")
            else:
                self.jb_hp -= 10
                self._slow_print(
                    f"\n{self.red}[DOUBT]: You say it, but you don't fully believe it yourself yet.{self.reset}")
                self._slow_print(f"{self.red}You take -10 HP DMG.{self.reset}")

        elif choice == "2":
            self.colonel_hp -= 10
            self.jb_hp -= 5
            self._slow_print(
                f"\n{self.blue}[CLASH]: A verbal spar. He respects the backbone but hates the tone.{self.reset}")
            self._slow_print(f"{self.green}Both take damage.{self.reset}")

    # -------------------------------------------------------------------------
    # ENDING LOGIC
    # -------------------------------------------------------------------------

    def _check_fight_outcome(self, stats):
        """
        [UPDATED]: Logic for when attacks run out (Stalemate).
        """
        # 1. Player Defeated
        if self.jb_hp <= 0:
            self._slow_print(f"\n{self.red}{self.bold}DEFEAT. You crumble under the pressure.{self.reset}", delay=0.05)
            # In your main game loop, handle the Game Over here
            return

        # 2. Colonel Defeated (Standard)
        if self.colonel_hp <= 0:
            self._glitch_phase(stats)
            return

        # 3. SUDDEN DEATH / ATTACKS EXHAUSTED (Both > 0 HP)
        # This triggers when the loop finishes and no one is at 0 HP.
        print("\n" + "=" * 50)
        self._slow_print(f"{self.bold}THE SILENCE{self.reset}")
        print("=" * 50)

        self._slow_print("\nThe Colonel stops. He has run out of threats.", delay=0.04)
        self._slow_print("He stares at you, breathing heavily. He has nothing left to say.", delay=0.04)

        time.sleep(1)
        print(f"\n{self.green}JB HP: {self.jb_hp}{self.reset}  VS  {self.red}COLONEL HP: {self.colonel_hp}{self.reset}")
        time.sleep(1)

        # LOGIC: If JB_HP >= COLONEL_HP -> WIN
        if self.jb_hp >= self.colonel_hp:
            self._slow_print(f"\n{self.green}VERDICT: YOU ARE STRONGER.{self.reset}", delay=0.05)
            self._slow_print("You withstood the barrage. The Colonel realizes he cannot break you.", delay=0.04)

            # Force Victory
            self.colonel_hp = 0
            self._glitch_phase(stats)

        else:
            # LOGIC: If JB_HP < COLONEL_HP -> LOSS
            self._slow_print(f"\n{self.red}VERDICT: YOU ARE BROKEN.{self.reset}", delay=0.05)
            self._slow_print("You survived the argument, but the stress was too much.", delay=0.04)
            self._slow_print("You don't have the energy to fight anymore. You slowly sit back down.", delay=0.04)
            self._slow_print(f"\n{self.red}{self.bold}DEFEAT.{self.reset}", delay=0.05)

    def _glitch_phase(self, stats):
        """
        [FIXED]: Loop logic for the menu now works correctly.
        """
        # --- MUSIC SWITCH: GLITCH / MATRIX THEME ---
        self._play_music("sevirra_lenoloc.mp3")

        print("\n")
        self._slow_print(f"{self.green}Colonel HP reaches 0.{self.reset}", delay=0.05)
        self._slow_print("He stumbles back. He looks defeated.", delay=0.05)
        self._slow_print("You wait for him to give up.", delay=0.05)

        time.sleep(1.5)
        print("\n" + f"{self.red}ERROR: NPC_STATE_RESET{self.reset}")
        time.sleep(0.5)

        # THE RESET
        self.colonel_hp = 100
        self._print_hud("Round 3 (Wait... again?)")

        self._slow_print("Suddenly, he stands up straight. Like a puppet pulled by strings.", delay=0.04)
        self._slow_print("His face resets to the exact same expression from this morning.", delay=0.04)

        time.sleep(2)
        self._slow_print("\nYour eyes widen.", delay=0.06)
        self._slow_print(f"{self.bold}He is looping.{self.reset}", delay=0.06)
        self._slow_print("He doesn't see you. He CANNOT see you.", delay=0.04)
        self._slow_print("He is just a script running 'police_bureaucracy.exe'.", delay=0.04)

        time.sleep(1.5)
        self._slow_print("\nHe prepares his biggest attack yet. The Final Insult.", delay=0.05)
        self._slow_print(f"{self.red}'You are a COWARD, JB! You were never fit for this force!'{self.reset}",
                         delay=0.04)

        # FIX: Loop properly handles re-displaying options
        while True:
            print("\nCHOOSE YOUR REACTION:")
            print("1. [ARGUE] 'That's not true! I gave you everything!' (Restart the loop)")
            print(f"2. {self.green}[sys.exit()] WAKE UP.{self.reset}")

            choice = input("\n> ")

            if choice == "1":
                self._slow_print("\nYou try to argue, but he just pours another coffee...", delay=0.03)
                self._slow_print("The loop tightens around your neck.", delay=0.03)
                self._slow_print(f"{self.red}You are trapped in the argument forever.{self.reset}")
                self._slow_print("(You realize arguing is pointless. Try again.)\n", delay=0.02)
                time.sleep(1)
                # Loop continues, showing menu again

            elif choice == "2":
                # TRIGGER THE GOOD ENDING MODULE
                good_ending = GoodEnding()
                good_ending.trigger_ending()
                break

            else:
                print("Invalid input.")