################################################################################
## REFACTOR - Python Logic
## Ported from stats.py and day_cycle.py
################################################################################

init python:

    ## --- StS-style highlight tag: {stshl=word} → inline gold-bold word ---
    ## Why: random-event flavor highlight, mirrors Slay the Spire's
    ## colored event-text words. Implemented as inline color+bold tokens
    ## (NOT an embedded Text displayable) so the highlighted word flows
    ## inline with surrounding dialogue. An earlier displayable-based
    ## version added a gentle bob but introduced a ~100px horizontal gap
    ## around the word — inline tokens trade the bob for clean layout.
    def _stshl_tag(tag, argument, contents):
        return [
            (renpy.TEXT_TAG, "b"),
            (renpy.TEXT_TAG, "color=#f5b042"),
            (renpy.TEXT_TEXT, argument),
            (renpy.TEXT_TAG, "/color"),
            (renpy.TEXT_TAG, "/b"),
        ]

    config.custom_text_tags["stshl"] = _stshl_tag


    class Stats:
        """Core stat container for JB. Ported from stats.py."""

        def __init__(self, available_money=0, coding_experience=0, pcr_hatred=0):
            self.available_money = available_money
            self.coding_skill = coding_experience
            self.pcr_hatred = pcr_hatred
            self.colonel_day = 30
            self.final_boss_buff = None
            self.difficulty = None
            self.player_class = None
            self.colonel_attitude = None

        def try_spend_money(self, amount):
            """Attempt to spend money. Returns True on success."""
            if self.available_money >= amount:
                self.available_money -= amount
                return True
            return False

        def increment_stats_value_money(self, amount):
            self.available_money += amount
            if self.available_money < 0:
                self.available_money = 0

        def increment_stats_coding_skill(self, amount):
            ## Per-class hard ceiling. BB physically cannot become a senior
            ## engineer through study — to win the Colonel he must buy his way
            ## past the skill gate. Default ceiling 250 for classes that
            ## don't set one.
            ceiling = 250
            cls = getattr(self, "player_class", None)
            if cls and cls in CLASS_DATA:
                ceiling = CLASS_DATA[cls].get("coding_ceiling", 250)
            self.coding_skill += amount
            if self.coding_skill >= ceiling:
                self.coding_skill = ceiling
            if self.coding_skill >= 250:
                unlock_achievement("hackerman")

        def increment_stats_pcr_hatred(self, amount):
            self.pcr_hatred += amount
            if self.pcr_hatred < 0:
                self.pcr_hatred = 0

        def stats_description_money(self):
            money_levels = [
                (1000000, "YOU ARE A MILLIONAIRE! Why are you still working at the police?!"),
                (500000,  "Half a million... you could actually buy a small garage in your city now."),
                (200000,  "Your reserves are INSANE! You feel safer than you ever did carrying a gun."),
                (150000,  "This is serious money. You breathe a little easier knowing you have this cushion."),
                (100000,  "If you don't spend unwisely, you can survive for months without a salary."),
                (85000,   "You have a solid financial foundation. Not rich, but not desperate."),
                (65000,   "You have some savings, but a broken car or a lawyer could wipe it out."),
                (45000,   "You are treading water. One big expense and you are in trouble."),
                (30000,   "Your situation is getting tense. You're calculating the price of cheese in the supermarket."),
                (20000,   "You are running out of money! The stress is starting to affect your sleep."),
                (10000,   "DANGER ZONE. You have enough for rent, but not much else."),
                (5000,    "SOON YOU WILL HAVE NO MONEY LEFT! Instant noodles are your new best friend."),
                (1000,    "You are basically broke. You check your pockets for loose change."),
                (0,       "YOU HAVE NO MONEY LEFT. You are one crisis away from homelessness."),
            ]
            for limit, desc in money_levels:
                if self.available_money >= limit:
                    return desc
            return "YOU HAVE NO MONEY LEFT."

        def stats_description_coding_experience(self):
            if self.coding_skill == -100:
                return "Why even learn to code, when you can be a police officer?"
            coding_levels = [
                (250, "SCHIZO CODER. 01010101 'I am the Compiler.'"),
                (225, "SINGULARITY. You no longer type. You stare at the screen and the code writes itself."),
                (200, "GOD TIER. You see the Matrix. You don't write code, you manifest logic."),
                (175, "Principal Engineer. You spend more time drawing boxes on whiteboards than typing."),
                (150, "Senior Developer. You delete more code than you write, and the system runs faster."),
                (125, "Medior Developer. You can build entire systems from scratch without tutorials."),
                (100, "HIREABLE (Junior Dev). You know enough to get paid. Escape is finally possible!"),
                (85,  "Competent. You understand OOP, APIs, and databases. You are dangerous."),
                (65,  "Advanced Learner. You can make simple websites and text games without crashing."),
                (45,  "Intermediate. You finally understand what 'self' actually means."),
                (30,  "Beginner. You spend 90% of your time debugging syntax errors."),
                (15,  "Script Kiddie. You copy-paste from Stack Overflow and pray it works."),
                (5,   "Hello World. You made the computer print text. You feel like a hacker."),
                (0,   "Non-Existent. You think 'Python' is just a snake in the zoo."),
            ]
            for limit, desc in coding_levels:
                if self.coding_skill > limit:
                    return desc
            return "You are just starting. Ideally, keep the computer turned on."

        def stats_description_police_hatred(self):
            if self.pcr_hatred == -100:
                return "Colonel was right. You are nothing without this uniform."
            hatred_levels = [
                (95, "PSYCHOTIC BREAK. HAHAHAHDAHHAHAHAHA! The siren sounds like music! The paperwork is confetti!"),
                (85, "CRITICAL MASS. You are physically shaking. One more stupid order and you will scream."),
                (75, "TOXIC. You look at civilians and wonder if they know how good they have it. You hate them for it."),
                (65, "BURNOUT. You don't patrol anymore; you just drive aimlessly to avoid the radio."),
                (50, "HOLLOW. The coffee tastes like bureaucracy and despair. You are only here for the money."),
                (40, "RESENTMENT. You stopped polishing your boots weeks ago. Why bother?"),
                (25, "The cracks are showing. You check the time every 5 minutes hoping the shift is over."),
                (15, "Skepticism. You realize the 'Protect and Serve' motto is mostly just branding."),
                (5,  "Routine. There are things you dislike, but overall, it's a stable job."),
                (0,  "FRESH MEAT. You love your job! You are going to save the world! (You fool)."),
            ]
            for limit, desc in hatred_levels:
                if self.pcr_hatred > limit:
                    return desc
            return "You are suspiciously happy. Are you sure you work here?"


    class DayCycle:
        """Simple day counter. Ported from day_cycle.py."""

        def __init__(self, current_day=1):
            self.current_day = current_day

        def next_day(self):
            self.current_day += 1


    # ---------------------------------------------------------------------------
    # Difficulty settings — starting stats AND rule modifiers per tier.
    # Fields:
    #   money / coding / hatred — starting values (Phase 0)
    #   nightly_hatred_mult     — multiplier on base nightly hatred tick (do_end_day)
    #   salary_mult             — multiplier on Day-14 salary
    #   purchase_mult           — multiplier on activity costs (use adjusted_cost helper)
    #   score_mult              — final ending score multiplier
    #   opp_rate                — % chance of opportunity event on non-event days (Phase 1+)
    #   minigame_retries        — coding mini-game retries permitted (Phase 2+)
    #   colonel_deck_size       — Colonel boss deck size (Phase 1+)
    # ---------------------------------------------------------------------------
    DIFFICULTY_SETTINGS = {
        "easy":   {"money": 55000, "coding": 10,  "hatred": 15,
                   "nightly_hatred_mult": 0.8, "salary_mult": 1.10, "purchase_mult": 1.0,  "score_mult": 1.0,
                   "opp_rate": 50, "minigame_retries": 2, "colonel_deck_size": 5},
        "hard":   {"money": 35000, "coding":  5,  "hatred": 25,
                   "nightly_hatred_mult": 1.0, "salary_mult": 1.00, "purchase_mult": 1.0,  "score_mult": 2.5,
                   "opp_rate": 30, "minigame_retries": 1, "colonel_deck_size": 7},
        "insane": {"money": 20000, "coding":  0,  "hatred": 35,
                   "nightly_hatred_mult": 1.2, "salary_mult": 0.85, "purchase_mult": 1.10, "score_mult": 5.0,
                   "opp_rate": 20, "minigame_retries": 0, "colonel_deck_size": 9},
    }

    def diff_setting(key, default=None):
        """Read a difficulty rule field. Safe before init_game runs."""
        if stats is None or stats.difficulty is None:
            return default
        return DIFFICULTY_SETTINGS.get(stats.difficulty, {}).get(key, default)

    def class_accent_color(player_class=None):
        """Return the class accent color hex string. Falls back to neutral grey
        if class is unset (e.g. before character_class_selection runs)."""
        if player_class is None and stats is not None:
            player_class = stats.player_class
        return {
            "bodybuilder": "#ff6633",
            "dark_empath": "#9944cc",
            "biohacker":   "#33cc66",
        }.get(player_class, "#888888")

    def adjusted_cost(base):
        """Apply the active difficulty's purchase multiplier to a base cost."""
        return int(base * diff_setting("purchase_mult", 1.0))

    def add_soma(n):
        """BB-only SOMA grant. Clamps to 0..10 and unlocks the cap achievement."""
        if not stats or stats.player_class != "bodybuilder":
            return
        store.bb_soma = max(0, min(10, getattr(store, 'bb_soma', 0) + n))
        if store.bb_soma >= 10:
            unlock_achievement("maximum_stack")

    def get_key_event_days():
        """Return dict[day -> (label, color)] for calendar markers."""
        if stats is None:
            return {}
        marks = {
            14: ("SALARY",   "#ffd700"),
            15: ("CALL",     "#9944cc"),
            24: ("MARTIN",   "#33aacc"),
        }
        ## Colonel day depends on Martin Meeting timing choice
        marks[stats.colonel_day] = ("COLONEL", "#cc2200")
        return marks

    # ---------------------------------------------------------------------------
    # Coding tier helper (mirroring game_rules.py get_coding_tier_info)
    # ---------------------------------------------------------------------------
    def get_coding_tier_info(coding_skill):
        tiers = {
            "TIER 1": {"range": "0-34",   "standard": 0,     "hourly": 0,   "label": "Still Learning"},
            "TIER 2": {"range": "35-99",  "standard": 2500,  "hourly": 25,  "label": "Junior Scripter"},
            "TIER 3": {"range": "100-149","standard": 5000,  "hourly": 50,  "label": "Solid Developer"},
            "TIER 4": {"range": "150-199","standard": 7500,  "hourly": 75,  "label": "Senior Engineer"},
            "TIER 5": {"range": "200+",   "standard": 10000, "hourly": 100, "label": "God-Tier Dev"},
        }
        if coding_skill < 35:
            return "TIER 1", tiers["TIER 1"]
        elif coding_skill < 100:
            return "TIER 2", tiers["TIER 2"]
        elif coding_skill < 150:
            return "TIER 3", tiers["TIER 3"]
        elif coding_skill < 200:
            return "TIER 4", tiers["TIER 4"]
        else:
            return "TIER 5", tiers["TIER 5"]

    # ---------------------------------------------------------------------------
    # Global game-state objects – initialised in label start via init_game()
    # ---------------------------------------------------------------------------
    stats     = None
    day_cycle = None
    python_bootcamp   = False
    activity_selected = False

    # Nootropic system state (Biohacker class only)
    nootropic_tier_max   = 1            # highest unlocked tier (1–5)
    nootropic_uses       = [0,0,0,0,0]  # total uses per tier index
    nootropic_dependency = False        # hard dependency triggered (T5 x3)
    nootropic_last_tier  = 0            # tier taken yesterday; 0 = none
    flmodafinil_unlocked = False        # T5 requires special event unlock

    # Dark Empath Cold Read state
    cold_read_index = 0                 # rotates through 4 targets

    def init_game(difficulty):
        """
        Initialise global game state for the chosen difficulty string
        ('easy', 'hard', 'insane').
        """
        global stats, day_cycle, python_bootcamp, activity_selected
        global nootropic_tier_max, nootropic_uses, nootropic_dependency
        global nootropic_last_tier, flmodafinil_unlocked, cold_read_index
        settings = DIFFICULTY_SETTINGS[difficulty]
        stats = Stats(
            available_money   = settings["money"],
            coding_experience = settings["coding"],
            pcr_hatred        = settings["hatred"],
        )
        stats.difficulty  = difficulty
        day_cycle         = DayCycle(current_day=1)
        python_bootcamp   = False
        activity_selected = False
        nootropic_tier_max   = 1
        nootropic_uses       = [0, 0, 0, 0, 0]
        nootropic_dependency = False
        nootropic_last_tier  = 0
        flmodafinil_unlocked = False
        cold_read_index      = 0
        store._crisis_triggered = False
        store._nightmare_wolf_triggered = False
        store._reunion_via_defeat = False
        ## Battle ladder state — drainable pool + skip-tomorrow penalty flag.
        ## Lazy-inited by roll_ladder_or_event on first call; reset here so a
        ## new run gets a fresh pool of 10 enemies.
        store.battle_ladder_pool = None
        store._ladder_skip_tomorrow = False
        ## Persistent run HP — carries across ladder battles + into the Colonel.
        ## None = first battle hasn't fired yet (battle_init will lazy-init to
        ## the class max). After each victory, battle_finish writes the
        ## post-fight HP here. forced_detour subtracts on defeat. End-of-day
        ## nightly cycle slowly regens. Healing activities (gym) bump it up.
        store.run_hp = None
        store.run_hp_max = None
        ## Permanent max-HP bonus accrued from gym sessions (+5 per regular gym).
        ## Added on top of class baseline in battle_init. Resets on new run.
        store.gym_max_hp_bonus = 0

        ## --- Class progression state ---
        ## BB: SOMA stack (each gym session +1, max 10). 5+ unlocks Iron Body buff in fight.
        store.bb_soma = 0
        ## DE: PROFILES (npc_id -> read_count). 3 reads on same NPC unlocks their event.
        store.de_profiles = {"rookie": 0, "veteran": 0, "lieutenant": 0, "clerk": 0}
        ## BH: PROTOCOL (current active compound profile, set by last nootropic taken).
        store.bh_protocol = None
        ## Class-arc multi-stage flags (Kovář / Telegram)
        store.de_arc_stage = 0
        store.bh_arc_stage = 0
        ## Phone notification queue — set-pieces append strings here, PHONE button
        ## in the hub appears only when non-empty (cleared on user view).
        store._phone_notifications = []
        ## Israeli unlock for BH telegram arc (set by re_israeli_developer if BH path taken)
        ## (flmodafinil_unlocked already gates this; bh_arc_stage starts when that flag flips)

    # ---------------------------------------------------------------------------
    # Character Class data and perk helpers
    # ---------------------------------------------------------------------------
    CLASS_DATA = {
        "bodybuilder": {
            "name":    "BODYBUILDER",
            "tagline": "Iron body. Iron will. Limited vocabulary.",
            "color":   class_accent_color("bodybuilder"),
            "perks": [
                "Bouncer shifts pay +2,500 CZK on every outcome.",
                "Gym sessions deal -5 extra Hatred on all outcomes.",
                "Permanent +5 max HP per gym session, persistent across the run.",
                "Immune to Colonel's Brotherhood guilt trip.",
                "Extra brute-force option if caught at car incident.",
            ],
            "passive": "Built for the long fight. Persistent HP scales with gym attendance; bouncer bonus turns physical work into capital.",
            "coding_modifier":   0,
            "hatred_modifier":   0,
            "coding_ceiling":  250,
        },
        "dark_empath": {
            "name":    "DARK EMPATH",
            "tagline": "You feel everything. You weaponize it.",
            "color":   class_accent_color("dark_empath"),
            "perks": [
                "Auto +1 Affection per Martin Meeting phase.",
                "COLD READ — free relief; OBSERVATION HOUR branch goes deeper, no card.",
                "Colonel's Why Quit / Civilian Void deal 50%% less damage.",
                "Secret FATAL STRIKE option on Civilian Void attack.",
                "civilian_small_talk always succeeds (-25 Hatred guaranteed).",
            ],
            "passive": "Starts with -5 Police Hatred (already numb to the madness).",
            "coding_modifier":   0,
            "hatred_modifier":  -5,
            "coding_ceiling":  250,
        },
        "biohacker": {
            "name":    "BIOHACKER",
            "tagline": "Optimized. Caffeinated. Slightly illegal.",
            "color":   class_accent_color("biohacker"),
            "perks": [
                "Starts with +5 Coding Skill (analytical edge from baseline).",
                "Israeli Developer event always grants max coding reward.",
                "Coding coach always grants +25 Coding (top-tier tutor).",
                "Colonel's Safety Net attack is auto-countered.",
            ],
            "passive": "Starts with +5 Coding Skill (analytical edge from baseline).",
            "coding_modifier":   5,
            "hatred_modifier":   0,
            "coding_ceiling":  250,
        },
    }

    # ---------------------------------------------------------------------------
    # Achievement system
    # category: "Story" / "Combat" / "Collection" / "Secret"
    # hint: shown for locked non-secret achievements; secrets stay obscured until unlocked.
    # ---------------------------------------------------------------------------
    ACHIEVEMENTS = {
        "first_blood":      {"category": "Story",      "name": "First Blood",            "desc": "Lose money for the first time.",                                "hint": "Spend more than you can afford."},
        "gym_rat":          {"category": "Collection", "name": "Gym Rat",                 "desc": "Hit a 5-day gym streak.",                                       "hint": "Hit the gym 5 days in a row."},
        "deep_pockets":     {"category": "Collection", "name": "Deep Pockets",            "desc": "Save over 200,000 CZK.",                                        "hint": "Accumulate 200,000 CZK in savings."},
        "code_god":         {"category": "Collection", "name": "Code God",                "desc": "Reach 200+ Coding Skill.",                                      "hint": "Reach 200 Coding Skill."},
        "dark_night":       {"category": "Story",      "name": "Dark Night of the Soul",  "desc": "Complete The Midnight Call.",                                   "hint": "Take the Day-15 phone call."},
        "dark_empath_win":  {"category": "Combat",     "name": "Mirror Mirror",           "desc": "Use the FATAL STRIKE as Dark Empath.",                          "hint": "Dark Empath only — find the Colonel's hidden vulnerability."},
        "biohacker_win":    {"category": "Combat",     "name": "Optimized",               "desc": "Auto-counter Safety Net as Biohacker.",                         "hint": "Biohacker only — let the Colonel try the safety net argument."},
        "hackerman":        {"category": "Collection", "name": "Hackerman",               "desc": "Max out coding skill to 250. You are the compiler now.",        "hint": "Reach 250 Coding Skill (the cap)."},
        "the_return":       {"category": "Story",      "name": "The Return",              "desc": "Walk out of the station, then walk back six months later.",         "hint": "Leave the Colonel behind without the perfect exit. Six months later you'll find out what that costs."},
        ## --- Class arc achievements ---
        "bring_the_lt":     {"category": "Story",      "name": "Bring The Lieutenant",    "desc": "Expose Kovář's flagged report to journalists.",                  "hint": "Dark Empath only — choose to expose, not leverage or comply."},
        "subject_zero":     {"category": "Story",      "name": "Subject Zero",            "desc": "Become the trial. Document everything. Lose your baseline.",     "hint": "Biohacker only — agree to the 21-day compound trial."},
        "profile_master":   {"category": "Collection", "name": "Profile Master",          "desc": "Cold-read all four station targets at least three times each.",  "hint": "Dark Empath only — read every target deeply."},
        "maximum_stack":    {"category": "Collection", "name": "Maximum Stack",           "desc": "Reach SOMA 10/10. The body is the answer.",                      "hint": "Bodybuilder only — go to the gym 10 times."},
        "compound_knowledge":{"category":"Collection", "name": "Compound Knowledge",       "desc": "Learn synthesis instead of taking the vial.",                    "hint": "Biohacker only — pick the lesson over the contraband."},
        "wake_up_call":     {"category": "Secret",     "name": "Wake Up Call",            "desc": "Type sys.exit() during the colonel's loop. Step out of the script.","hint": "???"},
        "i_dont_need_it":   {"category": "Secret",     "name": "I Don't Need IT",         "desc": "Reach the escape ending without signing the bootcamp contract.",    "hint": "Find another way out of the uniform."},
    }

    def unlock_achievement(key):
        """Unlock an achievement by key. Safe to call multiple times."""
        global _achievements_unlocked
        if not hasattr(store, '_achievements_unlocked'):
            store._achievements_unlocked = set()
        if key not in store._achievements_unlocked:
            store._achievements_unlocked.add(key)
            ach = ACHIEVEMENTS.get(key, {})
            ach_name = ach.get("name", key)
            ach_desc = ach.get("desc", "")
            ## Fade music, play sound, restore music
            current_music = renpy.music.get_playing()
            renpy.music.set_volume(0.15, delay=0.2)
            renpy.sound.play("audio/achivement_unlocked.mp3", channel="sound")
            renpy.show_screen("achievement_toast", ach_name=ach_name, ach_desc=ach_desc)
            ## Restore music volume after sound finishes (~2s typical)
            renpy.music.set_volume(1.0, delay=2.5)
            return True  ## Newly unlocked
        return False  ## Already had it

    def apply_class_bonuses(stats_obj):
        """Apply starting stat modifiers for the chosen player class."""
        cls = stats_obj.player_class
        if cls not in CLASS_DATA:
            return
        data = CLASS_DATA[cls]
        ## Route the coding modifier through the helper so the per-class
        ## ceiling clamp applies (matters when the modifier is positive — BH).
        stats_obj.increment_stats_coding_skill(data["coding_modifier"])
        stats_obj.pcr_hatred = max(0, stats_obj.pcr_hatred + data["hatred_modifier"])

    # Salary amounts keyed by hatred bracket (mirrors receive_salary in game_rules.py)
    def salary_amount(pcr_hatred):
        if pcr_hatred <= 25:
            return 40000
        elif pcr_hatred <= 50:
            return 30000
        else:
            return 20000

    # ---------------------------------------------------------------------------
    # Nootropics System — Biohacker exclusive
    # ---------------------------------------------------------------------------

    NOOTROPIC_TIERS = {
        1: {
            "name":          "Daily Supplements",
            "compounds":     "Omega-3, Creatine, Matcha, Magnesium, Vitamin D",
            "cost":          300,
            "coding":        4,
            "hatred":        -4,
            "crash_coding":  0,
            "crash_hatred":  0,
            "flavor":        "Boring. Effective. The foundation of any serious optimisation protocol.",
            "crash_flavor":  "",
        },
        2: {
            "name":          "Cognitive Stack",
            "compounds":     "L-Theanine + Caffeine, Alpha-GPC, Bacopa Monnieri",
            "cost":          750,
            "coding":        8,
            "hatred":        -5,
            "crash_coding":  0,
            "crash_hatred":  0,
            "flavor":        "The static clears. The cursor blinks faster.",
            "crash_flavor":  "",
        },
        3: {
            "name":          "Racetams",
            "compounds":     "Aniracetam, Oxiracetam, Phenylpiracetam",
            "cost":          1250,
            "coding":        13,
            "hatred":        -8,
            "crash_coding":  -3,
            "crash_hatred":  0,
            "flavor":        "You feel the connections forming. Real ones. Dendrites firing in new configurations.",
            "crash_flavor":  "Mild choline depletion. Your focus is slightly dulled this morning.",
        },
        4: {
            "name":          "Peptides",
            "compounds":     "Noopept, Semax, Selank",
            "cost":          2000,
            "coding":        18,
            "hatred":        -12,
            "crash_coding":  -5,
            "crash_hatred":  8,
            "flavor":        "You are not yourself. You are a better-compiled version of yourself.",
            "crash_flavor":  "Mood flatness. The grey is back. You knew it would come.",
        },
        5: {
            "name":          "FLModafinil (CRL-40,940)",
            "compounds":     "Fluoromodafinil — research chemical, slightly illegal",
            "cost":          3500,
            "coding":        28,
            "hatred":        -20,
            "crash_coding":  -18,
            "crash_hatred":  22,
            "flavor":        "You are the compiler now. Everything else is just source code waiting to be optimised.",
            "crash_flavor":  "The crash hits like a system reboot with corrupted memory. Your hands shake. The Colonel's face is very clear this morning.",
        },
    }

    def apply_nootropic_morning_effects():
        """
        Called at the start of each new day before the daily menu.
        Reads nootropic_last_tier, applies crash/withdrawal, resets the tracker.
        Returns a tuple (tag, flavor_text) or None if nothing to report.
        Tags: 'crash', 'withdrawal', 'dependency_triggered', 'soft_dependency'
        """
        global nootropic_last_tier, nootropic_dependency

        tier = nootropic_last_tier
        nootropic_last_tier = 0  # consume — reset for today

        if tier == 0:
            # Nothing taken yesterday
            if nootropic_dependency:
                stats.increment_stats_coding_skill(-20)
                stats.increment_stats_pcr_hatred(20)
                return ("withdrawal",
                        "Your body revolts without the compound.\n"
                        "Every thought feels like pushing through wet concrete.\n"
                        "(-20 Coding Skill, +20 Police Hatred)")
            return None

        t = NOOTROPIC_TIERS[tier]
        effects = []

        if t["crash_coding"] != 0:
            stats.increment_stats_coding_skill(t["crash_coding"])
            effects.append("{} Coding".format(t["crash_coding"]))
        if t["crash_hatred"] != 0:
            stats.increment_stats_pcr_hatred(t["crash_hatred"])
            effects.append("+{} Hatred".format(t["crash_hatred"]))

        # T5 hard dependency trigger
        if tier == 5 and nootropic_uses[4] >= 2 and not nootropic_dependency:
            nootropic_dependency = True
            return ("dependency_triggered",
                    "Two doses. You crossed the line.\n"
                    "FLModafinil (CRL-40,940) has rewritten your baseline.\n"
                    "You will feel its absence now.\n\n" + t["crash_flavor"])

        # T4 soft dependency (extra penalty after 4 uses, no hard lock)
        if tier == 4 and nootropic_uses[3] >= 4:
            stats.increment_stats_coding_skill(-3)
            stats.increment_stats_pcr_hatred(5)
            return ("soft_dependency",
                    "The edge is dulling. Your body is adapting.\n"
                    "This is what tolerance looks like.\n\n" + t["crash_flavor"])

        if effects:
            return ("crash", t["crash_flavor"])
        return None

    def check_nootropic_unlocks():
        """
        Check if usage thresholds unlock the next tier.
        Returns a tag string if a new tier was unlocked, else None.
        T1x2 -> T2, T2x2 -> T3, T3x2 -> T4, T4x2 -> T5.
        T5 can also be unlocked via the Israeli Developer event flag.
        """
        global nootropic_tier_max
        if nootropic_tier_max < 2 and nootropic_uses[0] >= 2:
            nootropic_tier_max = 2
            return "T2_UNLOCKED"
        if nootropic_tier_max < 3 and nootropic_uses[1] >= 2:
            nootropic_tier_max = 3
            return "T3_UNLOCKED"
        if nootropic_tier_max < 4 and nootropic_uses[2] >= 2:
            nootropic_tier_max = 4
            return "T4_UNLOCKED"
        if nootropic_tier_max < 5 and nootropic_uses[3] >= 2:
            nootropic_tier_max = 5
            return "T5_UNLOCKED"
        return None

    # ---------------------------------------------------------------------------
    # Cold Read Target Pool — Dark Empath exclusive
    # ---------------------------------------------------------------------------

    COLD_READ_TARGETS = [
        {
            "name":      "The Overwhelmed Rookie",
            "text_low":  (
                "He's barely holding it together. Twenty-two years old, "
                "processing things no training prepared him for.\n"
                "You sit next to him in the break room. You don't say much. Neither does he.\n"
                "You listen to the frequency of his breathing, the speed of his blinking.\n"
                "You understand exactly what he's afraid of.\n"
                "For a moment — just a moment — you feel something close to compassion."
            ),
            "text_high": (
                "He's barely holding it together. You catalogue every tell without thinking.\n"
                "Micro-tremble in his left hand. Eyes on the floor when the Sergeant speaks.\n"
                "You feel nothing except pattern recognition.\n"
                "He is a stress variable in a failing system.\n"
                "It is almost peaceful to stop pretending you care."
            ),
        },
        {
            "name":      "The Cynical Veteran",
            "text_low":  (
                "Twenty-eight years on the force. He holds his coffee with both hands "
                "like it's the last warm thing in the world.\n"
                "You watch the way his eyes go flat when the Colonel's name comes up.\n"
                "He's not broken. He's just... resolved.\n"
                "You wonder if that's better or worse.\n"
                "The question takes up less space than hatred does."
            ),
            "text_high": (
                "Twenty-eight years on the force. He's already dead inside and doesn't know it.\n"
                "You watch him perform contentment — the jokes, the coffee ritual, the practiced shrug.\n"
                "All of it maintenance. Keeping a machine running past its end-of-life date.\n"
                "You feel contempt. But also relief.\n"
                "You are not going to become that."
            ),
        },
        {
            "name":      "The Quietly Corrupt Lieutenant",
            "text_low":  (
                "He gets calls that aren't in the logbook. You've noticed.\n"
                "You watch him for 30 minutes — who he avoids, what he does before leaving.\n"
                "You don't know what to do with what you see. But you file it away.\n"
                "Knowledge is the only thing here that nobody can take from you."
            ),
            "text_high": (
                "He gets calls that aren't in the logbook. The new watch appeared three weeks ago.\n"
                "You track his tells with cold efficiency. "
                "The pause before he answers questions about the Novák case.\n"
                "You know exactly what he is.\n"
                "And you know exactly what that information is worth.\n"
                "You feel nothing except a quiet sense of leverage."
            ),
        },
        {
            "name":      "The Civilian Clerk",
            "text_low":  (
                "She processes paperwork and hates every cop in the building. Including you.\n"
                "You watch her operate — the eye rolls, the micro-delays.\n"
                "Somewhere under all that resentment you recognise someone who also feels trapped.\n"
                "You nod at her on the way out. She almost nods back."
            ),
            "text_high": (
                "She processes paperwork and hates every cop in the building. Including you.\n"
                "You watch her with clinical detachment. Surface-level contempt, no real depth.\n"
                "You could make her day terrible with one misplaced complaint. You don't.\n"
                "Not because you're kind. Because it costs you nothing to let her think she's invisible."
            ),
        },
    ]


## ---------------------------------------------------------------------------
## Daily music pool — randomized rotation
## ---------------------------------------------------------------------------
## Defeats repetition fatigue from a single workhorse track. Tracks in the pool
## should share a sonic lane (all A-minor, Mr-Robot/Cyberpunk/HL2 register) so
## any sequence cohabits.
##
## Behaviour: idempotent. If a pool track is ALREADY on the music channel, the
## call is a no-op — daily-menu to daily-menu transitions don't reshuffle. Only
## fires a fresh pick when the currently-playing track is non-pool (after
## combat, after an event with its own music, at game start). That's the
## "track changes after combat, not every day" behaviour.
##
## Missing files are silently skipped. If the entire pool is missing, falls
## back to `audio/coding_in_snow_theme.mp3` so the game keeps working while
## new tracks are being added.
## ---------------------------------------------------------------------------

init python:

    import random as _daily_music_rand

    ## Add/remove filenames here as new tracks land. Each track lives in the
    ## Mr-Robot / Cyberpunk / HL2 industrial-noir lane (A minor) so any
    ## sequence cohabits cleanly when the pool randomises.
    DAILY_LOOP_POOL = [
        "audio/rust_triage.wav",
        "audio/circuit_mercy_pulse.wav",
        "audio/subfloor_metrics.wav",
        "audio/debug_heartbeats.wav",
    ]

    DAILY_LOOP_FALLBACK = "audio/coding_in_snow_theme.mp3"

    def play_daily_music(fadein=1.5):
        """Resume daily-loop music with rotation. See module docstring above."""
        pool = [t for t in DAILY_LOOP_POOL if renpy.loadable(t)]

        ## No pool tracks on disk — fall back to the single workhorse.
        if not pool:
            if renpy.loadable(DAILY_LOOP_FALLBACK):
                if renpy.music.get_playing(channel="music") != DAILY_LOOP_FALLBACK:
                    renpy.music.play(DAILY_LOOP_FALLBACK, fadein=fadein, channel="music")
            return

        ## A pool track is already playing — leave it alone.
        currently = renpy.music.get_playing(channel="music")
        if currently in pool:
            return

        ## Pick a fresh pool track, avoiding the last one if pool has >1 entry.
        last = getattr(store, '_last_daily_track', None)
        choices = [t for t in pool if t != last] or pool
        chosen = _daily_music_rand.choice(choices)

        renpy.music.play(chosen, fadein=fadein, channel="music")
        store._last_daily_track = chosen
