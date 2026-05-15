################################################################################
## REFACTOR — Colonel Deck (Phase 1.5)
##
## The Colonel's deck consists of "intent cards" the boss plays each turn.
## Each entry has:
##   id        — stable string key
##   name      — display name (shown above intent indicator)
##   intent    — "attack" / "buff" / "block" / "compound" / "debuff"
##   value     — primary numeric value (dmg / block / hits-of-X)
##   value2    — secondary value (for compound: hits)
##   counter   — dict of conditions -> effect modifications (resolved by engine)
##   immunity  — list of player_class strings that bypass this attack
##   tags      — list of tags ("emotional", "physical", "money") for card-counter logic
##   dialogue  — line to display when this intent resolves
##   threat    — for AI ordering: 1=low, 2=med, 3=high (affects deck ordering)
################################################################################

init python:

    ENEMY_DECK_LIBRARY = {}

    def register_enemy_card(card_id, **fields):
        defaults = {
            "id":       card_id,
            "name":     card_id,
            "intent":   "attack",
            "value":    10,
            "value2":   0,
            "counter":  {},
            "immunity": [],
            "tags":     [],
            "dialogue": "",
            "threat":   2,
        }
        defaults.update(fields)
        defaults["id"] = card_id
        ENEMY_DECK_LIBRARY[card_id] = defaults
        return defaults

    ## ---------------------------------------------------------------------------
    ## The 7 core attacks (mapped from the original colonel_event)
    ## ---------------------------------------------------------------------------

    register_enemy_card(
        "training_debt",
        name     = "Training Debt",
        intent   = "attack",
        value    = 25,
        tags     = ["money"],
        dialogue = "'You know you have to return the money for your training, JB?'",
        threat   = 3,
        counter  = {
            "buff_paragraph_4b_armed": {"damage_to_self": 10, "negate": True},
            "money_gte_200000":        {"reduce_damage": 10},
        },
    )

    register_enemy_card(
        "why_quit",
        name     = "Why Quit",
        intent   = "attack",
        value    = 22,
        tags     = ["emotional", "mental"],
        dialogue = "'Why, JB? After everything I did for you. Why are you quitting?'",
        threat   = 2,
    )

    register_enemy_card(
        "civilian_void",
        name     = "Civilian Void",
        intent   = "attack",
        value    = 28,
        tags     = ["emotional", "mental"],
        dialogue = "'Without the badge, you are nobody. Out there you are just another civilian.'",
        threat   = 3,
        counter  = {
            "buff_mirror_armed_for_counter": {"damage_to_self": 56, "negate": True},
            "coding_skill_gte_100":          {"reduce_damage": 14},
        },
    )

    register_enemy_card(
        "brotherhood",
        name     = "Brotherhood",
        intent   = "attack",
        value    = 18,
        tags     = ["emotional", "guilt", "mental"],
        dialogue = "'And what about your team? Lieutenant? The rookies?'",
        immunity = ["bodybuilder"],
        threat   = 2,
        counter  = {
            ## stoic_anchor power writes stoic_anchor_block/_heal (not the
            ## bare key); stoic_refactor power writes mental_dr_50. Counter
            ## keys must match the actual buff names — earlier versions
            ## checked buff_stoic_anchor / buff_stoic_refactor and silently
            ## did nothing.
            "buff_stoic_anchor_block": {"reduce_damage": 12},
            "buff_mental_dr_50":       {"reduce_damage": 9},
        },
    )

    register_enemy_card(
        "safety_net",
        name     = "Safety Net",
        intent   = "attack",
        value    = 24,
        tags     = ["money", "fear"],
        dialogue = "'You are throwing away a guaranteed future for... what? Coding scripts?'",
        immunity = ["biohacker"],
        threat   = 2,
        counter  = {
            "money_gte_150000": {"reduce_damage": 12},
        },
    )

    register_enemy_card(
        "debt_of_honor",
        name     = "Debt of Honor",
        intent   = "attack",
        value    = 22,
        tags     = ["emotional", "guilt", "mental"],
        dialogue = "'Have you forgotten the car accident, JB? I buried that for you.'",
        threat   = 2,
        counter  = {
            ## Repointed from card_ghost_secret (now unobtainable post-Phase 4
            ## Martin trim) to took_the_heat (always granted on Day 1).
            ## Owning the receipt for the OG car incident counters his guilt.
            ## Buff-based so the counter survives subsequent card plays and
            ## upgrade to took_the_heat_plus.
            "buff_took_the_heat_armed": {"damage_to_self": 25, "negate": True},
        },
    )

    register_enemy_card(
        "blacklist",
        name     = "Blacklist",
        intent   = "attack",
        value    = 26,
        tags     = ["fear"],
        dialogue = "'I will make calls. I will ruin you. You will never work in this town again.'",
        threat   = 3,
        counter  = {
            ## job_offer is a Power, auto-fired at battle_init — that path
            ## doesn't update last_card_played, so the old card_-prefixed
            ## check never matched. Buff is set inside _eff_job_offer/_plus.
            "buff_job_offer_armed": {"damage_to_self": 15, "negate": True},
            "coding_skill_gte_50":  {"reduce_damage": 10},
        },
    )

    ## ---------------------------------------------------------------------------
    ## Filler / pressure cards (Insane and Ultra get these mixed in)
    ## ---------------------------------------------------------------------------

    register_enemy_card(
        "cold_stare",
        name     = "Cold Stare",
        intent   = "strength",
        value    = 2,
        dialogue = "He stares at you. He sips his coffee. He says nothing. The room cools by two degrees.",
        threat   = 2,
    )

    register_enemy_card(
        "the_doctrine",
        name     = "The Doctrine",
        intent   = "attack",
        value    = 15,
        tags     = ["mental"],
        dialogue = "'There is a rule, JB. One word per topic. The room enforces it.'",
        threat   = 3,
    )

    register_enemy_card(
        "coffee_pour",
        name     = "Coffee Pour",
        intent   = "block",
        value    = 12,
        dialogue = "'Black? Two sugars?' He pours another cup. The pause is deliberate.",
        threat   = 1,
    )

    register_enemy_card(
        "authority_display",
        name     = "Authority Display",
        intent   = "debuff",
        value    = 1,        ## reduce player draw next turn by N
        dialogue = "He stands up. The room shrinks. He has been doing this for 32 years.",
        threat   = 2,
    )

    register_enemy_card(
        "compounding_pressure",
        name     = "Compounding Pressure",
        intent   = "compound",
        value    = 7,        ## damage per hit
        value2   = 3,        ## number of hits
        tags     = ["physical"],
        dialogue = "He doesn't stop. Every sentence is a small cut. Every cut is the same shape.",
        threat   = 3,
    )

    register_enemy_card(
        "final_threat",
        name     = "Final Threat",
        intent   = "attack",
        value    = 40,
        tags     = ["fear"],
        dialogue = "'JB. Last chance. Sit back down.'",
        threat   = 3,
    )


    ## ---------------------------------------------------------------------------
    ## Deck builder — assembles the colonel's deck for the current difficulty
    ## ---------------------------------------------------------------------------

    ## ---------------------------------------------------------------------------
    ## Battle ladder — Easy tier intents
    ## ---------------------------------------------------------------------------

    register_enemy_card(
        "rvac_swing",
        name     = "Roundhouse",
        intent   = "attack",
        value    = 12,
        dialogue = "He winds up. Right at your jaw.",
        threat   = 2,
    )
    register_enemy_card(
        "rvac_haymaker",
        name     = "Haymaker",
        intent   = "attack",
        value    = 18,
        dialogue = "He throws his whole bar tab into it.",
        threat   = 3,
    )
    register_enemy_card(
        "rvac_drink",
        name     = "Pull from the Bottle",
        intent   = "block",
        value    = 4,
        dialogue = "He swigs. The bottle empties. The fist gets heavier.",
        threat   = 1,
    )

    register_enemy_card(
        "tag_quick",
        name     = "Quick Tag",
        intent   = "attack",
        value    = 9,
        dialogue = "One darts in. Paints across your jacket. Darts out.",
        threat   = 2,
    )
    register_enemy_card(
        "tag_team",
        name     = "Tag Team",
        intent   = "compound",
        value    = 5,
        value2   = 3,
        dialogue = "All three move at once. Three quick hits.",
        threat   = 3,
    )
    register_enemy_card(
        "spray_blind",
        name     = "Aerosol Cloud",
        intent   = "debuff",
        value    = 1,
        dialogue = "A cloud goes off in your face. You'll draw one card short.",
        threat   = 2,
    )
    register_enemy_card(
        "vandal_block",
        name     = "Tagged Van",
        intent   = "block",
        value    = 6,
        dialogue = "They duck behind a sprayed-over Trabant.",
        threat   = 1,
    )

    register_enemy_card(
        "chant",
        name     = "Chant",
        intent   = "buff",
        value    = 3,
        dialogue = "He starts a chant. Others join. The next hit lands harder.",
        threat   = 2,
    )
    register_enemy_card(
        "flare_throw",
        name     = "Flare Throw",
        intent   = "attack",
        value    = 14,
        dialogue = "A flare arcs past your ear. You feel the heat.",
        threat   = 2,
    )
    register_enemy_card(
        "pile_in",
        name     = "Pile In",
        intent   = "compound",
        value    = 3,
        value2   = 4,
        dialogue = "The pack rushes. Six fast knocks.",
        threat   = 3,
    )

    register_enemy_card(
        "dossier_flick",
        name     = "Dossier Flick",
        intent   = "attack",
        value    = 10,
        dialogue = "A page slaps you across the temple. Paper cuts add up.",
        threat   = 1,
    )
    register_enemy_card(
        "read_aloud",
        name     = "Read Aloud",
        intent   = "attack",
        value    = 13,
        dialogue = "It reads a witness statement aloud. Each word lands.",
        threat   = 2,
    )
    register_enemy_card(
        "paper_wall",
        name     = "Paper Wall",
        intent   = "block",
        value    = 14,
        dialogue = "It folds itself into a wall of forms.",
        threat   = 1,
    )
    register_enemy_card(
        "file_swap",
        name     = "File Swap",
        intent   = "debuff",
        value    = 1,
        dialogue = "A blank form drops into your draw pile.",
        threat   = 2,
    )

    ## ---------------------------------------------------------------------------
    ## Medium tier intents
    ## ---------------------------------------------------------------------------

    register_enemy_card(
        "knockoff_swing",
        name     = "Knockoff Swing",
        intent   = "attack",
        value    = 16,
        dialogue = "He swings a counterfeit Rolex across your cheek.",
        threat   = 2,
    )
    register_enemy_card(
        "stall_swarm",
        name     = "Stánek Swarm",
        intent   = "compound",
        value    = 4,
        value2   = 4,
        dialogue = "Three stánkaři close in. Hands everywhere.",
        threat   = 3,
    )
    register_enemy_card(
        "haggle",
        name       = "Haggle",
        intent     = "debuff",
        value      = 1,
        debuff_key = "max_energy_penalty_next_turn",
        dialogue   = "'Discount for cash, mister policeman.' He talks your energy down.",
        threat     = 2,
    )
    register_enemy_card(
        "lockup",
        name     = "Lockup",
        intent   = "block",
        value    = 10,
        dialogue = "Roll-down shutter slams. He waits behind it.",
        threat   = 1,
    )
    register_enemy_card(
        "markdown",
        name     = "Markdown",
        intent   = "attack",
        value    = 12,
        dialogue = "A price tag rakes your knuckles. Sticker glue stays for days.",
        threat   = 1,
    )

    register_enemy_card(
        "fume_swipe",
        name     = "Fume Swipe",
        intent   = "attack",
        value    = 15,
        dialogue = "He swings, and the mask trails chemical mist.",
        threat   = 2,
    )
    register_enemy_card(
        "chem_burn",
        name     = "Chem Burn",
        intent   = "attack",
        value    = 13,
        dialogue = "Acid splash. The jacket is ruined.",
        threat   = 2,
    )
    register_enemy_card(
        "chem_stoke",
        name     = "Time to Cook",
        intent   = "buff",
        value    = 2,
        dialogue = "He turns the burner up. The next strike will hit harder.",
        threat   = 1,
    )
    register_enemy_card(
        "lab_check",
        name     = "Lab Check",
        intent   = "block",
        value    = 12,
        dialogue = "He ducks behind the rig. Glassware between you.",
        threat   = 1,
    )
    register_enemy_card(
        "gas_release",
        name     = "Gas Release",
        intent   = "debuff",
        value    = 1,
        dialogue = "A valve hisses. Eyes water. You'll be a card short.",
        threat   = 2,
    )

    register_enemy_card(
        "paragraph_5_2",
        name     = "Paragraf 5(2)",
        intent   = "attack",
        value    = 18,
        dialogue = "He pushes the glasses up the bridge of his nose. The lenses catch the light. 'Paragraf 5, odstavec 2. Pane policisto, that one you should know by heart.'",
        threat   = 3,
    )
    register_enemy_card(
        "cross_examine",
        name     = "Cross-Examination",
        intent   = "compound",
        value    = 5,
        value2   = 4,
        dialogue = "'Where exactly. When exactly. With whom. Repeat the answer.' Four questions, no pauses.",
        threat   = 3,
    )
    register_enemy_card(
        "intimidate",
        name       = "Look Over the Rim",
        intent     = "debuff",
        value      = 1,
        debuff_key = "max_energy_penalty_next_turn",
        dialogue   = "He drops his chin and looks at you over the top of his glasses. The room shrinks by a foot.",
        threat     = 2,
    )
    register_enemy_card(
        "procedural_shield",
        name     = "Presumption of Innocence",
        intent   = "block",
        value    = 20,
        dialogue = "He flips the case folder shut and rests his palm on the cover. 'Bez důkazu žádné obvinění.'",
        threat   = 1,
    )
    register_enemy_card(
        "objection",
        name     = "Námitka",
        intent   = "attack",
        value    = 13,
        dialogue = "'Námitka!' The word lands like a rubber stamp on your forehead.",
        threat   = 2,
    )
    register_enemy_card(
        "build_argument",
        name     = "Build the Argument",
        intent   = "buff",
        value    = 6,
        dialogue = "He stacks three precedent cards on the desk in a row. The next strike will land sharper.",
        threat   = 2,
    )

    register_enemy_card(
        "priority_call",
        name     = "Priority Call",
        intent   = "attack",
        value    = 15,
        dialogue = "The radio crackles. 'All units, your location.'",
        threat   = 2,
    )
    register_enemy_card(
        "radio_static",
        name     = "Static Burst",
        intent   = "debuff",
        value    = 1,
        dialogue = "Static fills the channel. You miss the next dispatch.",
        threat   = 2,
    )
    register_enemy_card(
        "false_alarm",
        name     = "False Alarm",
        intent   = "attack",
        value    = 14,
        dialogue = "A false call routes you across town. Wasted breath.",
        threat   = 1,
    )
    register_enemy_card(
        "silence",
        name     = "Comms Silence",
        intent   = "block",
        value    = 14,
        dialogue = "Channel goes dead. You can't reach him.",
        threat   = 1,
    )
    register_enemy_card(
        "frequency_jam",
        name       = "Frequency Jam",
        intent     = "debuff",
        value      = 1,
        debuff_key = "max_energy_penalty_next_turn",
        dialogue   = "He overlays your channel. Your next move costs more.",
        threat     = 2,
    )

    ## ---------------------------------------------------------------------------
    ## Hard tier intents
    ## ---------------------------------------------------------------------------

    register_enemy_card(
        "interview",
        name     = "Interview",
        intent   = "attack",
        value    = 18,
        dialogue = "'Where exactly were you on the eighteenth?' She's read it three times.",
        threat   = 3,
    )
    register_enemy_card(
        "audit",
        name     = "Audit",
        intent   = "debuff",
        value    = 1,
        dialogue = "She turns the page. Slowly. Your next move is short a card.",
        threat   = 2,
    )
    register_enemy_card(
        "quote_regulation",
        name     = "Quote Regulation",
        intent   = "strength",
        value    = 2,
        dialogue = "She names the paragraph. Each citation makes the next argument hit harder. +2 STR.",
        threat   = 2,
    )
    register_enemy_card(
        "formal_warning",
        name     = "Formal Warning",
        intent   = "attack",
        value    = 20,
        dialogue = "A signature line slides under your hand. You sign.",
        threat   = 3,
    )
    register_enemy_card(
        "case_review",
        name     = "Case Review",
        intent   = "block",
        value    = 18,
        dialogue = "She closes the folder. You can't see what's inside anymore.",
        threat   = 1,
    )
    register_enemy_card(
        "wire_check",
        name     = "Wire Check",
        intent   = "attack",
        value    = 16,
        dialogue = "She plays back your own radio traffic. The tone gives you away.",
        threat   = 2,
    )
    register_enemy_card(
        "transfer_pending",
        name     = "Transfer Pending",
        intent   = "compound",
        value    = 7,
        value2   = 3,
        dialogue = "Three forms. Three signatures. Three different offices.",
        threat   = 3,
    )

    register_enemy_card(
        "breach_swing",
        name     = "Breach Swing",
        intent   = "attack",
        value    = 20,
        dialogue = "The lead operator swings the ram, then the baton.",
        threat   = 3,
    )
    register_enemy_card(
        "kettle",
        name     = "Kettle",
        intent   = "debuff",
        value    = 1,
        dialogue = "They form up around you. Less room. Less options.",
        threat   = 2,
    )
    register_enemy_card(
        "shield_wall",
        name     = "Shield Wall",
        intent   = "block",
        value    = 22,
        dialogue = "The phalanx locks polycarbonate. Nothing comes through.",
        threat   = 1,
    )
    register_enemy_card(
        "gas_throw",
        name     = "Gas Throw",
        intent   = "compound",
        value    = 4,
        value2   = 5,
        dialogue = "The canister bounces twice. Tear gas blooms.",
        threat   = 3,
    )
    register_enemy_card(
        "baton_combo",
        name     = "Baton Combo",
        intent   = "compound",
        value    = 3,
        value2   = 7,
        dialogue = "Ten short strikes. Trained. Identical.",
        threat   = 3,
    )
    register_enemy_card(
        "formation_buff",
        name     = "Hold Formation",
        intent   = "buff",
        value    = 4,
        dialogue = "Three operators step forward in unison. The next strike will land harder.",
        threat   = 2,
    )
    register_enemy_card(
        "phalanx_block",
        name     = "Phalanx",
        intent   = "block",
        value    = 26,
        dialogue = "Shields overlap. Shins braced. No daylight between them.",
        threat   = 1,
    )
    register_enemy_card(
        "clear_room",
        name     = "Clear Room",
        intent   = "attack",
        value    = 26,
        dialogue = "'Clear left. Clear right.' The corner finds you.",
        threat   = 3,
    )


    COLONEL_DECK_TEMPLATES = {
        ## Every difficulty includes cold_stare (permanent +2 STR ramp) AND
        ## the_doctrine (card-play restriction) — the boss has to bring more
        ## than raw damage to feel like a capstone. Damage cards get cycled
        ## into harder tiers.
        ## Easy: 5 cards — 3 attacks + ramp + restrict.
        5:  ["training_debt", "why_quit", "civilian_void", "cold_stare", "the_doctrine"],
        ## Hard: 7 cards — full base set + new mechanics.
        7:  ["training_debt", "why_quit", "civilian_void", "safety_net", "blacklist", "cold_stare", "the_doctrine"],
        ## Insane: 9 cards — adds guilt-tier attacks + compound.
        9:  ["training_debt", "why_quit", "civilian_void", "brotherhood", "safety_net", "debt_of_honor", "blacklist", "cold_stare", "the_doctrine"],
    }

    def build_colonel_deck():
        """Return the colonel's deck for the current difficulty as a shuffled list of card-ids.

        Loss-stacking: every 2 ladder losses promotes the Colonel by one
        template tier (5 → 7 → 9, capped). The vision wants stalled runs
        to compound into a harder boss, not just degrade stats."""
        size = diff_setting("colonel_deck_size", 7)
        _tiers = [5, 7, 9]
        _losses = getattr(store, '_battle_losses', 0)
        _bumps = _losses // 2
        if size in _tiers and _bumps > 0:
            _idx = min(len(_tiers) - 1, _tiers.index(size) + _bumps)
            size = _tiers[_idx]
        template = COLONEL_DECK_TEMPLATES.get(size, COLONEL_DECK_TEMPLATES[7])
        deck = list(template)
        __import__('random').shuffle(deck)
        return deck
