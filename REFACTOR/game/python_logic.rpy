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

    ## ── Stale module-ref scrubber ─────────────────────────────────────────
    ## Old code did `import random as _bh_grant_rand` inside a label python
    ## block, which left the random MODULE bound in the store. The store is
    ## pickled on every save, and modules can't be pickled — instant crash.
    ## The bug is fixed (we use `__import__('random').choice(...)` inline now)
    ## but older saves still carry the leaked binding. Scrub on every load
    ## so existing saves don't keep crashing.
    def _bh_scrub_stale_module_refs():
        import types as _types
        for _name in ("_bh_grant_rand", "_noot_rng", "_daily_music_rand",
                      "_battle_rand", "_rage_rand", "_bh_rand", "_juice_math",
                      "_kw_re_mod"):
            if hasattr(store, _name):
                try:
                    delattr(store, _name)
                except Exception:
                    pass
        ## Defensive sweep — any leaked module-typed store attr is unrenderable
        ## and unsave-able. Scrub anything that snuck through.
        for _name in list(vars(store).keys()):
            try:
                if isinstance(getattr(store, _name), _types.ModuleType) and _name.startswith("_"):
                    delattr(store, _name)
            except Exception:
                pass

    config.after_load_callbacks.append(_bh_scrub_stale_module_refs)
    config.start_callbacks.append(_bh_scrub_stale_module_refs)

    ## ── Misclassed-Rage scrubber ─────────────────────────────────────────
    ## Rage cards (Outburst / Tunnel Vision / Snap) are Bodybuilder-exclusive
    ## as of the class-gating fix. Saves made BEFORE the gate may carry
    ## injected Rage cards on a Biohacker or Dark Empath deck. Purge them on
    ## load + start so existing runs aren't permanently corrupted by a fix
    ## they predate.
    ##
    ## Also resets _rage_thresholds_triggered to {} for non-BB so the
    ## tutorial popup / threshold tracking doesn't think the player already
    ## "saw" 40/60/80 — they didn't, the system just shouldn't have fired.
    def _scrub_misclassed_rage():
        try:
            _pc = stats.player_class if stats is not None else None
        except Exception:
            return
        if _pc == "bodybuilder" or _pc is None:
            return
        _pd = globals().get("player_deck")
        if _pd is None:
            return
        _rage_ids = {"outburst", "tunnel_vision", "snap",
                     "outburst_plus", "tunnel_vision_plus", "snap_plus"}
        _pd.cards = [c for c in _pd.cards if c not in _rage_ids]
        ## Reset trigger-set so non-BB doesn't show "already triggered" if
        ## they ever class-switch in a dev/test scenario.
        try:
            store._rage_thresholds_triggered = set()
        except Exception:
            pass

    config.after_load_callbacks.append(_scrub_misclassed_rage)
    config.start_callbacks.append(_scrub_misclassed_rage)

    ## ── Stale run_hp_max scrubber ────────────────────────────────────────
    ## Saves made before the BH HP buff (80 → 90) carry a persisted
    ## store.run_hp_max = 80 + gym_bonus. The lazy-init paths early-return
    ## when the field isn't None, so Recovery / event_heal silently no-op'd
    ## because the clamp was below the new class base. On load, if the
    ## stored cap is below the canonical class_max_hp(), raise it AND lift
    ## current run_hp by the same delta (so the player sees the heal
    ## headroom they're entitled to). Never lowers — gym +max-HP modalities
    ## stack legitimately above the base.
    def _scrub_stale_run_hp_max():
        try:
            if stats is None:
                return
            ## Helper not necessarily resolved here yet (init order); guard.
            _fn = globals().get("class_max_hp")
            if _fn is None:
                return
            _canonical = _fn()
            _stored    = getattr(store, 'run_hp_max', None)
            if _stored is None:
                return
            if _stored < _canonical:
                _delta = _canonical - _stored
                store.run_hp_max = _canonical
                _cur = getattr(store, 'run_hp', None)
                if _cur is not None:
                    store.run_hp = min(_canonical, _cur + _delta)
        except Exception:
            pass

    config.after_load_callbacks.append(_scrub_stale_run_hp_max)
    config.start_callbacks.append(_scrub_stale_run_hp_max)


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
            ## Hatred corrupts (vision §1 pillar 2). Each threshold crossing
            ## jams a permanent Rage card into the deck. One-shot per threshold
            ## — dipping below and back up does NOT re-grant.
            _check_rage_injection()

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

    ## ── Single source of truth for class HP caps ─────────────────────────
    ## Multiple sites used to inline `115 if bb else 75 if de else 80` —
    ## when the BH base bumped to 90, the inline copies went stale and
    ## Recovery / event_heal silently no-op'd because their lazy-init
    ## clamped run_hp_max at the old 80. Every site that needs a class HP
    ## must now call this helper.
    CLASS_BASE_HP = {
        "bodybuilder": 115,
        "dark_empath": 75,
        "biohacker":   90,
    }

    def class_max_hp(player_class=None, include_gym_bonus=True):
        """Canonical max HP for a class. Adds gym_max_hp_bonus by default
        (the Recovery / gym +max-HP modalities stack here). Pass
        include_gym_bonus=False for the raw class base."""
        if player_class is None and stats is not None:
            player_class = stats.player_class
        base = CLASS_BASE_HP.get(player_class, 80)
        if include_gym_bonus:
            base += getattr(store, 'gym_max_hp_bonus', 0)
        return base

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

    def hatred_cap():
        """Police-hatred breakdown threshold. Bodybuilder runs hotter — the
        Hatred archetype is theirs, so BB gets 25 more headroom (125) before
        the breakdown ending fires. Every other class breaks down at 100."""
        if stats is not None and stats.player_class == "bodybuilder":
            return 125
        return 100

    def add_soma(n):
        """BB-only SOMA grant. Clamps to 0..10 and unlocks the cap achievement."""
        if not stats or stats.player_class != "bodybuilder":
            return
        store.bb_soma = max(0, min(10, getattr(store, 'bb_soma', 0) + n))
        if store.bb_soma >= 10:
            unlock_achievement("maximum_stack")

    ## ---------------------------------------------------------------------------
    ## Hatred corruption — vision §1 pillar 2.
    ## Each threshold (40 / 60 / 80) jams a permanent Rage card into the deck
    ## on first crossing. The deck IS the 30 days; bad weeks stick.
    ## Fired from increment_stats_pcr_hatred after the mutation lands.
    ##
    ## CLASS GATING: Rage is BODYBUILDER-EXCLUSIVE. BB's fantasy is "the bar
    ## tells the truth and the body holds the grudge" — Rage cards are the
    ## physical manifestation of that grudge. Biohacker's corruption is
    ## CHEMICAL (dependency, tolerance, crash) and lives in the Nootropics
    ## protocol rather than the deck. Dark Empath's corruption is RELATIONAL
    ## and lives in the cold-read tracker. Non-BB classes still accumulate
    ## Hatred — it still feeds the collapse cap — but no Rage cards land.
    ## ---------------------------------------------------------------------------
    RAGE_THRESHOLDS = [
        (40, "outburst"),
        (60, "tunnel_vision"),
        (80, "snap"),
    ]

    def _check_rage_injection():
        if stats is None:
            return
        ## BB-exclusive. Hatred still ticks for everyone (collapse cap still
        ## ends the run), but no permanent Rage cards land in non-BB decks.
        if stats.player_class != "bodybuilder":
            return
        triggered = getattr(store, '_rage_thresholds_triggered', None)
        if triggered is None:
            store._rage_thresholds_triggered = set()
            triggered = store._rage_thresholds_triggered
        ## grant_card lives in card_data.rpy; reference via globals() so this
        ## file doesn't need to know the registration order at init time.
        _grant = globals().get("grant_card")
        if _grant is None:
            return
        for threshold, card_id in RAGE_THRESHOLDS:
            if threshold in triggered:
                continue
            if stats.pcr_hatred >= threshold:
                if _grant(card_id, silent=False):
                    triggered.add(threshold)

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
    # Coding daily income — Biohacker freelance fantasy. Coding-tier-scaled
    # CZK paid passively at start of every day. The smart class's loop closure:
    # dose → +Coding → tier-up → bigger daily income → fund bigger doses.
    # Over a 30-day run, T5-capped BH earns 75k passive — material in late game.
    # Other classes get nothing — this is BH's identity. BB earns via Bouncer,
    # DE via cold-read pacing; BH earns by being smart.
    # ---------------------------------------------------------------------------
    def coding_daily_income():
        """Per-day CZK from coding skill, biohacker-only. Pays out at the
        start of each day in do_end_day. Tier brackets mirror the existing
        get_coding_tier_info ladder. Returns 0 for non-BH or below T2."""
        if stats is None or stats.player_class != "biohacker":
            return 0
        s = stats.coding_skill
        if s < 35:
            return 0       # Still Learning — nobody pays you yet
        if s < 100:
            return 200     # T2 Junior — a small recurring gig
        if s < 150:
            return 600     # T3 Solid — steady freelance
        if s < 200:
            return 1200    # T4 Senior — pricing your hours properly
        return 2500        # T5 God-tier — pick your clients

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
        ## Battle ladder state — drainable pool + skip-tomorrow penalty flag.
        ## Lazy-inited by roll_ladder_or_event on first call; reset here so a
        ## new run gets a fresh pool of 10 enemies.
        store.battle_ladder_pool = None
        store._ladder_skip_tomorrow = False
        ## Overtime "?" pity counter for the enemy roll (resets to the 10%
        ## floor on a fight). See _roll_overtime in events/overtime_events.rpy.
        store.overtime_enemy_chance = 10
        ## Shared StS-event pool — drained by the daily random-event slot AND
        ## the Overtime activity (no repeats across either). None here so
        ## _ensure_random_event_pool refills it fresh each run.
        store.random_event_pool = None
        ## Event hook — taking the KEEP branch of ev_colonel_regards leaves
        ## the Colonel +50 max HP at the day-30 fight. Run-permanent.
        store._colonel_gift_taken = False
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
        ## Hatred-corruption tracker — set of thresholds (40/60/80) already
        ## crossed this run. See _check_rage_injection / RAGE_THRESHOLDS.
        store._rage_thresholds_triggered = set()
        ## Battle-loss counter — incremented in forced_detour. Drives the
        ## Compromise card injection on the 2nd+ loss and (eventually) the
        ## Colonel deck scaling. Reset per run.
        store._battle_losses = 0
        ## Fixer-removal counter — drives escalating removal price. Each
        ## successful shred bumps the next removal's CZK cost. See
        ## fixer_current_price() in cards/card_data.rpy.
        store._fixer_removals = 0
        ## Per-day Fixer gate — one shred per day. Reset in do_end_day.
        ## Fixer visits don't consume the daily activity, but they're
        ## rate-limited so you can't bulk-shred a whole deck with cash.
        store._fixer_shredded_today = False

        ## --- Class progression state ---
        ## BB: SOMA stack (each gym session +1, max 10). 5+ unlocks Iron Body buff in fight.
        store.bb_soma = 0
        ## One-shot flag — the SOMA 10/10 capstone reward (soma_ten_reward) fires once.
        store._soma_reward_given = False
        ## DE: PROFILES (npc_id -> read_count). 3 reads on same NPC unlocks their event.
        store.de_profiles = {"rookie": 0, "veteran": 0, "lieutenant": 0, "clerk": 0}
        ## BH: PROTOCOL (current active compound profile, set by last nootropic taken).
        store.bh_protocol = None
        ## One-shot flag — the Protocol 10/10 capstone (protocol_ten_reward) fires once.
        store._protocol_reward_given = False
        ## ACD856 FAKE outcome leaves the player with a one-shot Diarrhea status
        ## card injected into the next battle. Read + consumed in battle_init.
        store.bh_pending_diarrhea = False
        ## Per-day Nootropics Lab gate — one dose OR one research session per day.
        ## Reset in do_end_day, blocks re-entry in activity_nootropics.
        store.nootropics_done_today = False
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
            "passive": "Built for the long fight. Persistent HP scales with gym attendance; bouncer bonus turns physical work into capital. Coding caps at 100 — you can buy your way to Junior Dev, not Senior.",
            "coding_modifier":   0,
            "hatred_modifier":   0,
            "coding_ceiling":  100,
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
                "Two unique daily activities — Nootropics Lab (dose for combat edge) and Recovery (4 modalities for HP + Hatred relief).",
                "Today's PROTOCOL drives the next fight's bonus — Legal: +1 starting block; Shady: +1 max energy; Lab: +1 max energy AND first-turn perks.",
                "Fastest Coding ramp of any class (T1/T2/T3 doses grant +3/+6/+10 Coding).",
                "10 nootropic BUYs unlock a choose-1-of-3 rare capstone Power.",
                "ACD856 random event — 10k CZK gamble for +20 max HP and a rare regen Power.",
                "Starts with +5 Coding Skill (analytical edge from baseline).",
            ],
            "passive": "Starts with +5 Coding. Daily protocol decides the per-fight bonus. Three deck archetypes — Stimulant (energy ramp), Neurochem (draw / replay), Wetware (HP regen).",
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
        ## --- Class arc achievements ---
        "bring_the_lt":     {"category": "Story",      "name": "Bring The Lieutenant",    "desc": "Expose Kovář's flagged report to journalists.",                  "hint": "Dark Empath only — choose to expose, not leverage or comply."},
        "subject_zero":     {"category": "Story",      "name": "Subject Zero",            "desc": "Become the trial. Document everything. Lose your baseline.",     "hint": "Biohacker only — agree to the 21-day compound trial."},
        "profile_master":   {"category": "Collection", "name": "Profile Master",          "desc": "Cold-read all four station targets at least three times each.",  "hint": "Dark Empath only — read every target deeply."},
        "maximum_stack":    {"category": "Collection", "name": "Maximum Stack",           "desc": "Reach SOMA 10/10. The body is the answer.",                      "hint": "Bodybuilder only — go to the gym 10 times."},
        "compound_knowledge":{"category":"Collection", "name": "Compound Knowledge",       "desc": "Learn synthesis instead of taking the vial.",                    "hint": "Biohacker only — pick the lesson over the contraband."},
        "wake_up_call":     {"category": "Secret",     "name": "Wake Up Call",            "desc": "Break the Colonel's bureaucracy loop. Step out of the script.","hint": "???"},
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

    ## REFACTORED to a 3-user-tier model (Legal/Shady/Lab) mapped onto the
    ## 5-tier array slots 1/3/5. Slots 2 and 4 are kept as data (older systems
    ## — martin_meeting, class_arcs, colonel_event — index into NOOTROPIC_TIERS
    ## directly) but never surfaced in the submenu (_NOOT_VIS hides them).
    ## User-visible tier names: T1 LEGAL eshop, T3 SHADY source, T5 LAB grade.
    ## Cost curve: 2k / 5k / 10k. Coding ramp: +3 / +6 / +10. Hatred:
    ## -3 / -2 net / +5 (lab grade is paranoia + cost + body strain).
    ## Coding numbers — second tuning pass (2026-05-25, post-playthrough).
    ## First pass tripled gains (+3/+6/+10 → +8/+15/+25) which made dosing
    ## the dominant strategy: 3× more XP per slot than STUDY, AND a card,
    ## AND a protocol bonus. Player feedback: "spam nootropics, ignore
    ## everything else." Cut ~40% so STUDY (+18 XP/day after companion
    ## buff) is a real competing lane:
    ##   T1 LEGAL:  +8  → +5
    ##   T3 SHADY:  +15 → +9
    ##   T5 LAB:    +25 → +15
    ##   T6 BLACK MARKET: +30 → +20
    ## Hatred costs unchanged — Hatred is still the brake on dose spam.
    NOOTROPIC_TIERS = {
        1: {
            "name":          "Legal Supplements",
            "compounds":     "Omega-3, Creatine, Magnesium, Vitamin D — eshop next-day.",
            "cost":          2000,
            "coding":        5,
            "hatred":        -3,
            "flavor":        "Boring. Legal. The foundation any serious protocol starts from.",
        },
        2: {
            "name":          "Cognitive Stack",
            "compounds":     "L-Theanine + Caffeine, Alpha-GPC, Bacopa Monnieri",
            "cost":          750,
            "coding":        12,
            "hatred":        -5,
            "flavor":        "[DEPRECATED visible tier — kept as data for legacy references.]",
        },
        3: {
            "name":          "Shady Source",
            "compounds":     "Modafinil, racetams — Telegram dealer, brown envelope.",
            "cost":          5000,
            "coding":        9,
            "hatred":        -5,
            "flavor":        "The dealer answers on the third ring. He doesn't say his name.",
        },
        4: {
            "name":          "Peptides",
            "compounds":     "Noopept, Semax, Selank",
            "cost":          2000,
            "coding":        18,
            "hatred":        -12,
            "flavor":        "[DEPRECATED visible tier — kept as data for legacy references.]",
        },
        5: {
            "name":          "Lab Grade",
            "compounds":     "DIHEXA, FLModafinil, custom peptides — gray-market lab.",
            "cost":          10000,
            "coding":        15,
            "hatred":        5,
            "flavor":        "The vial is plain. The labelling is wrong on purpose.",
        },
        ## TIER 6 — BLACK MARKET. Pure money-to-power; gated behind 100 Coding
        ## (you have to BE somebody to know somebody). Adds the "I've made it
        ## and I'm escalating" tier to BH's money sink. Surfaced as a 4th
        ## option in activity_nootropics when stats.coding_skill >= 100.
        6: {
            "name":          "Black Market Procurement",
            "compounds":     "Bespoke synthesis. The chemist works on referral only.",
            "cost":          25000,
            "coding":        20,
            "hatred":        10,
            "flavor":        "Cash up front. Address sent fifteen minutes before pickup. He doesn't shake your hand.",
        },
    }

    ## ── BH escalation flavor ─────────────────────────────────────────────
    ## The user explicitly asked for the Nootropics Lab to read "more like a
    ## protocol or some kind of shit. Or make it progressively worse." Voice
    ## drifts from cautious-clinical (early) to obsessive-clinical (mid) to
    ## post-clinical (late) as cumulative doses pile up. The cabinet stops
    ## being something you visit and starts being the room.
    ##
    ## Stages (cumulative across all tiers):
    ##   1: ≤2  uses — methodical, optimistic, "the protocol"
    ##   2: 3-6 uses — daily routine, instrumented, sticky notes
    ##   3: 7-9 uses — handwriting not entirely yours, baseline drift
    ##   4: 10+ uses — cabinet IS the room, dose IS the language
    def bh_stage():
        n = sum(nootropic_uses) if nootropic_uses else 0
        ## Black market doses count toward the rabbit-hole stage too.
        n += getattr(store, 'bh_blackmarket_uses', 0)
        if n <= 2:
            return 1
        if n <= 6:
            return 2
        if n <= 9:
            return 3
        return 4

    _BH_OPEN_LINES = [
        "You open the cabinet. The protocol is specific. Every compound has a purpose.",
        "Cabinet open. Today's protocol is on the second sticky note from the left. Three weeks of data behind it.",
        "You open the cabinet without looking. The protocol changed again last night — your handwriting, not entirely your decision.",
        "There is no closing the cabinet anymore. The protocol is just what the next hour looks like.",
    ]
    _BH_SUBTITLES = [
        "Exact compound. Exact dose. Exact timing.",
        "Compound. Dose. Timing. HRV in, HRV out, clarity 1-10.",
        "Inputs in. Outputs trending. The baseline is the variable now.",
        "There is no baseline. There is the dose.",
    ]
    _BH_RESEARCH_FLAVORS = [
        "Late-night dive. Three open tabs of papers and forum threads.",
        "Twelve tabs. Two PDFs you've already cited to yourself.",
        "PubMed. Reddit. A Korean preprint server. Sleep is for control groups.",
        "The papers stopped being other people's a while ago. You're just confirming.",
    ]
    _BH_TIER_FLAVORS = {
        1: [
            "Omega-3, creatine, magnesium, vitamin D. Next-day delivery.",
            "The base stack. Boring. Necessary. Spreadsheet column A.",
            "Foundational. You haven't bought magnesium and creatine on different days in months.",
            "Floor. The thing the rest of the protocol sits on. You take it without reading the bottle.",
        ],
        3: [
            "Modafinil, racetams. Brown envelope from a Telegram contact.",
            "The Telegram contact has a name now. 'Tom.' Tom is reliable.",
            "Tom doesn't ask what you do. You don't ask where the racetams cross the border.",
            "You stopped reading the labels. Tom is reliable. The labels are a formality.",
        ],
        5: [
            "DIHEXA, FLModafinil, custom peptides. Gray-market lab.",
            "Subcutaneous. The site rotates. You log the angle.",
            "You haven't called what's in the vials by its chemical name in weeks.",
            "The dose is the language. The vial is a sentence. Today's sentence is short.",
        ],
    }
    ## Post-dose flavor — fires AFTER the dose lands as in-character reflection.
    ## Per tier, four escalating lines. Indexed by per-tier use count, not stage.
    _BH_POSTDOSE_FLAVORS = {
        1: [
            "Boring. Legal. The foundation any serious protocol starts from.",
            "Predictable curve. The baseline you compare everything else against.",
            "You barely notice it land. Which is the point. Floor stays floor.",
            "It's not a dose anymore. It's part of breakfast.",
        ],
        3: [
            "The dealer answers on the third ring. He doesn't say his name.",
            "Tom answered second ring today. The envelope is a little heavier.",
            "Tom said 'be careful' and meant it. You're not sure with what.",
            "Tom didn't say anything. Tom just nodded. The room felt smaller after.",
        ],
        5: [
            "The vial is plain. The labelling is wrong on purpose.",
            "Second dose hits faster than the first. You note the delta. You don't fix it.",
            "You can feel the membrane uptake now. That's not supposed to be a thing you can feel.",
            "The Colonel's face is very clear today. Useful. The dose is doing its job.",
        ],
        ## Black market — premium one-off, escalation tracked separately on
        ## store.bh_blackmarket_uses (NOT nootropic_uses[5] which is T5).
        6: [
            "Cash up front, address fifteen minutes ahead. He doesn't shake your hand.",
            "Second time he texts you the address from a different number. You don't ask.",
            "The chemist starts a conversation. Halfway through, you realise it's a job interview.",
            "He calls you by your first name now. You never told him.",
        ],
    }

    def bh_open_line():
        return _BH_OPEN_LINES[bh_stage() - 1]

    def bh_subtitle():
        return _BH_SUBTITLES[bh_stage() - 1]

    def bh_research_flavor():
        return _BH_RESEARCH_FLAVORS[bh_stage() - 1]

    def bh_tier_flavor(tier):
        ## Per-tier flavor in the picker — escalates with how many times THIS
        ## tier has been bought (not cumulative). Caps at the last index.
        idx = nootropic_uses[tier - 1] if 0 <= tier - 1 < len(nootropic_uses) else 0
        pool = _BH_TIER_FLAVORS.get(tier, [])
        if not pool:
            return ""
        return pool[min(idx, len(pool) - 1)]

    def bh_postdose_flavor(tier):
        ## Fires AFTER a dose lands. Counter has just been incremented at
        ## this point, so dose #1 → idx 0 in the flavor list (subtract 1).
        ## Tier 6 (Black Market) tracks separately on store.bh_blackmarket_uses
        ## since nootropic_uses is a fixed 5-length T1-T5 array.
        if tier == 6:
            used = getattr(store, 'bh_blackmarket_uses', 0)
        else:
            used = nootropic_uses[tier - 1] if 0 <= tier - 1 < len(nootropic_uses) else 0
        idx = max(0, used - 1)
        pool = _BH_POSTDOSE_FLAVORS.get(tier, [])
        if not pool:
            return NOOTROPIC_TIERS.get(tier, {}).get("flavor", "")
        return pool[min(idx, len(pool) - 1)]


    def apply_nootropic_morning_effects():
        """
        Called at the start of each new day before the daily menu.
        Reads nootropic_last_tier, applies crash/withdrawal, resets the tracker.
        Returns a tuple (tag, flavor_text) or None if nothing to report.
        Tags: 'crash', 'withdrawal', 'dependency_triggered', 'soft_dependency',
              'dependency_cleared'

        Dependency model (rebalanced 2026-05-25):
          - Lock-in threshold raised 2 → 5 T5 LAB doses. The old 2-dose
            trigger was a trap once T5 was buffed to +25 Coding/dose —
            hitting it was inevitable for any BH using the class identity.
          - Withdrawal penalty halved (-20/+20 → -8/+10) so a missed day
            stings but doesn't cripple.
          - 3 consecutive no-dose days clears the latch. The body adapts;
            the player can break free if they're disciplined.
        """
        global nootropic_last_tier, nootropic_dependency

        tier = nootropic_last_tier
        nootropic_last_tier = 0  # consume — reset for today

        if tier == 0:
            # Nothing taken yesterday
            if nootropic_dependency:
                stats.increment_stats_coding_skill(-8)
                stats.increment_stats_pcr_hatred(10)
                ## Track consecutive no-dose days. After 3 in a row the
                ## body adapts and the dependency latch clears — gives the
                ## disciplined player a path out instead of a forever-tax.
                _streak = getattr(store, '_bh_nodose_streak', 0) + 1
                store._bh_nodose_streak = _streak
                if _streak >= 3:
                    nootropic_dependency = False
                    store._bh_nodose_streak = 0
                    return ("dependency_cleared",
                            "Day three off. The shake in your hands is gone.\n"
                            "Your body found a new baseline. The dependency is broken.\n"
                            "(Dependency cleared. You can resume on your own terms.)")
                return ("withdrawal",
                        "Your body misses the compound.\n"
                        "Thinking is slower. Patience is shorter.\n"
                        "(-8 Coding Skill, +10 Police Hatred)\n"
                        "({} more no-dose day(s) to break the dependency.)".format(3 - _streak))
            return None

        ## A dose landed → reset the no-dose streak.
        store._bh_nodose_streak = 0

        # T5 hard dependency trigger — raised 2 → 5 doses (see docstring).
        if tier == 5 and nootropic_uses[4] >= 5 and not nootropic_dependency:
            nootropic_dependency = True
            return ("dependency_triggered",
                    "Five doses. You crossed the line.\n"
                    "FLModafinil (CRL-40,940) has rewritten your baseline.\n"
                    "You will feel its absence now.")

        # T4 soft dependency (extra penalty after 4 uses, no hard lock)
        if tier == 4 and nootropic_uses[3] >= 4:
            stats.increment_stats_coding_skill(-3)
            stats.increment_stats_pcr_hatred(5)
            return ("soft_dependency",
                    "The edge is dulling. Your body is adapting.\n"
                    "This is what tolerance looks like.")

        return None

    def check_nootropic_unlocks():
        """
        Check if usage thresholds unlock the next tier under the 3-user-tier
        model (Legal / Shady / Lab → slots 1 / 3 / 5).
        T1x3 (Legal) -> T3 (Shady) — jumps tier_max straight to 3.
        T3x3 (Shady) -> T5 (Lab)  — jumps tier_max straight to 5.
        T5 can also be unlocked via the Israeli Developer event flag.
        """
        global nootropic_tier_max
        ## Legal x3 unlocks Shady — jump past the dead slot 2 to keep
        ## downstream `tier_max >= 2` checks (martin_meeting etc.) satisfied.
        if nootropic_tier_max < 3 and nootropic_uses[0] >= 3:
            nootropic_tier_max = 3
            return "SHADY_UNLOCKED"
        ## Shady x3 unlocks Lab — jump past the dead slot 4.
        if nootropic_tier_max < 5 and nootropic_uses[2] >= 3:
            nootropic_tier_max = 5
            return "LAB_UNLOCKED"
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

    ## Do NOT bind `random` to a store name here (e.g. `import random as
    ## _daily_music_rand`). The store gets pickled on save and modules can't
    ## be pickled — and even when the import is at init-python level (not a
    ## label block) the binding only survives if the running process never
    ## scrubs it. Use `__import__('random').choice(...)` inline below.
    ## Same lesson as `_bh_grant_rand` / `_noot_rng` (see scrubber above).

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
        chosen = __import__('random').choice(choices)

        renpy.music.play(chosen, fadein=fadein, channel="music")
        store._last_daily_track = chosen
