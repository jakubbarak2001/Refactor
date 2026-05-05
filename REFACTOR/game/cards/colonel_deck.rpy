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
            "card_paragraph_4b": {"damage_to_self": 10, "negate": True},
            "money_gte_200000":  {"reduce_damage": 10},
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
            "card_mirror":          {"damage_to_self": 56, "negate": True},
            "coding_skill_gte_100": {"reduce_damage": 14},
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
            "buff_stoic_anchor":   {"reduce_damage": 12},
            "buff_stoic_refactor": {"reduce_damage": 9},
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
            "card_ghost_secret": {"damage_to_self": 25, "negate": True},
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
            "card_job_offer":      {"damage_to_self": 15, "negate": True},
            "coding_skill_gte_50": {"reduce_damage": 10},
        },
    )

    ## ---------------------------------------------------------------------------
    ## Filler / pressure cards (Insane and Ultra get these mixed in)
    ## ---------------------------------------------------------------------------

    register_enemy_card(
        "cold_stare",
        name     = "Cold Stare",
        intent   = "buff",
        value    = 6,
        dialogue = "He stares at you. He sips his coffee. He says nothing.",
        threat   = 1,
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

    COLONEL_DECK_TEMPLATES = {
        ## Easy: 5 cards — drop two of the 7 (Brotherhood, Debt — guilt-heavy ones)
        5:  ["training_debt", "why_quit", "civilian_void", "safety_net", "blacklist"],
        ## Hard: 7 cards — full base set
        7:  ["training_debt", "why_quit", "civilian_void", "brotherhood", "safety_net", "debt_of_honor", "blacklist"],
        ## Insane: 9 cards — base + 2 fillers
        9:  ["training_debt", "why_quit", "civilian_void", "brotherhood", "safety_net", "debt_of_honor", "blacklist", "cold_stare", "compounding_pressure"],
        ## Ultra: 12 cards — base + 5 pressure cards (more compounds, final threat)
        12: ["training_debt", "why_quit", "civilian_void", "brotherhood", "safety_net", "debt_of_honor", "blacklist", "cold_stare", "coffee_pour", "authority_display", "compounding_pressure", "final_threat"],
    }

    def build_colonel_deck():
        """Return the colonel's deck for the current difficulty as a shuffled list of card-ids."""
        size = diff_setting("colonel_deck_size", 7)
        template = COLONEL_DECK_TEMPLATES.get(size, COLONEL_DECK_TEMPLATES[7])
        deck = list(template)
        __import__('random').shuffle(deck)
        return deck
