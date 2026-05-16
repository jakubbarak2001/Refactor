################################################################################
## REFACTOR — Enemy Library (Battle Ladder)
##
## ENEMY_LIBRARY is the registry of every enemy the battle engine can fight.
## The Colonel lives here as a metadata entry only; his deck is still built by
## build_colonel_deck() in colonel_deck.rpy because his difficulty-scaling
## predates the ladder. build_enemy_deck(enemy_id) dispatches: Colonel goes
## through the legacy path, ladder enemies use ENEMY_LIBRARY[id]["deck_template"].
##
## Entry schema:
##   id            stable string key
##   display_name  shown in the battle header (e.g. "Grundza")
##   sprite_id     base image-name; battle_screen falls back to
##                 "<sprite_id> neutral" if no emotional state matches
##   log_name      short name for "{} takes {} damage." log lines
##   tier          'easy' / 'medium' / 'hard' / 'capstone'
##   max_hp        int or None — None defers to the engine's deck-size table
##                 (Colonel only)
##   deck_template list[enemy_card_id] or None — None defers to build_colonel_deck()
##   wrinkle       per-enemy mechanic key resolved inside battle_engine.rpy
##                 (None for Colonel)
##   wrinkle_data  dict of params for the wrinkle (turn timers, stack thresholds…)
##   detour_lines  forced-detour narration on loss (empty for Colonel — his loss
##                 routes to reunion_ending, not the shared detour label)
################################################################################

init -1 python:

    ENEMY_LIBRARY = {}

    def register_enemy(enemy_id, **fields):
        defaults = {
            "id":            enemy_id,
            "display_name":  enemy_id.title(),
            "sprite_id":     enemy_id,
            "bg_id":         None,
            "log_name":      enemy_id.title(),
            "tier":          "easy",
            "max_hp":        None,
            "deck_template": None,
            "wrinkle":       None,
            "wrinkle_data":  {},
            "detour_lines":  [],
        }
        defaults.update(fields)
        defaults["id"] = enemy_id
        ENEMY_LIBRARY[enemy_id] = defaults
        return defaults

    def build_enemy_deck(enemy_id, prev_card_id=None):
        """Returns a shuffled list of enemy-card-ids for this enemy. Colonel
        delegates to build_colonel_deck() so his difficulty-scaling path stays
        intact. Ladder enemies read deck_template from ENEMY_LIBRARY.

        Anti-adjacency: enemy block resets each turn, so two consecutive blocks
        are pure waste (only the second one matters). After shuffling we (1) make
        sure no two adjacent cards are both 'block' within the deck, and (2) if
        the previous resolved card was 'block', swap the first card off-block so
        reshuffles don't chain into another block."""
        if enemy_id == "colonel":
            return build_colonel_deck()
        e = ENEMY_LIBRARY.get(enemy_id)
        if not e or not e.get("deck_template"):
            return []
        deck = list(e["deck_template"])
        __import__('random').shuffle(deck)

        def _intent_of(cid):
            c = ENEMY_DECK_LIBRARY.get(cid)
            return c.get("intent") if c else None

        prev_intent = _intent_of(prev_card_id) if prev_card_id else None
        if prev_intent == "block" and deck and _intent_of(deck[0]) == "block":
            for j in range(1, len(deck)):
                if _intent_of(deck[j]) != "block":
                    deck[0], deck[j] = deck[j], deck[0]
                    break

        for i in range(len(deck) - 1):
            if _intent_of(deck[i]) == "block" and _intent_of(deck[i + 1]) == "block":
                for j in range(i + 2, len(deck)):
                    if _intent_of(deck[j]) != "block":
                        deck[i + 1], deck[j] = deck[j], deck[i + 1]
                        break

        return deck


    register_enemy(
        "colonel",
        display_name = "Colonel",
        sprite_id    = "colonel",
        log_name     = "Colonel",
        tier         = "capstone",
    )

    ## ---------------------------------------------------------------------------
    ## EASY tier (days 3-9)
    ## ---------------------------------------------------------------------------

    register_enemy(
        "rvac",
        display_name = "Bar Brawler",
        sprite_id    = "rvac",
        log_name     = "Brawler",
        tier         = "easy",
        max_hp       = 65,
        deck_template = ["rvac_swing", "rvac_haymaker", "rvac_drink"],
        wrinkle      = "drunken_double",
        detour_lines = [
            "The brawler clocks you. You wake up in the alley behind the bar with a split lip.",
            "The watch commander writes it up wrong on purpose. The bar gets a warning. You get the blame.",
        ],
    )

    register_enemy(
        "sprejeri",
        display_name = "Taggers",
        sprite_id    = "sprejeri",
        log_name     = "Taggers",
        tier         = "easy",
        max_hp       = 70,
        deck_template = ["tag_quick", "tag_team", "spray_blind", "vandal_block"],
        wrinkle      = "tag_stack",
        detour_lines = [
            "They scatter through the panelák stairwells. You chase one to the third floor. He vanishes through a corridor that was never on the plan.",
            "Three more tags appear by morning. One of them looks like your face.",
        ],
    )

    register_enemy(
        "fanousek",
        display_name = "Hooligan",
        sprite_id    = "fanousek",
        log_name     = "Hooligan",
        tier         = "easy",
        max_hp       = 70,
        deck_template = ["chant", "flare_throw", "pile_in"],
        wrinkle      = "crew_rage",
        wrinkle_data = {"hp_threshold": 0.5, "bonus_dmg": 3},
        detour_lines = [
            "His crew finds you behind the bus station. They take turns on your kidneys.",
            "You file the report from the ER. The match was a draw, they tell each other.",
        ],
    )

    register_enemy(
        "spis",
        display_name = "Case File",
        sprite_id    = "spis",
        log_name     = "Case File",
        tier         = "easy",
        max_hp       = 65,
        deck_template = ["dossier_flick", "read_aloud", "paper_wall", "file_swap"],
        wrinkle      = "paper_clog",
        detour_lines = [
            "The file folds itself shut. The kid in it walks at 4 PM.",
            "Your name ends up on the cover. Misfiled. They don't fix it.",
        ],
    )

    ## ---------------------------------------------------------------------------
    ## MEDIUM tier (days 9-18)
    ## ---------------------------------------------------------------------------

    register_enemy(
        "nguyen",
        display_name = "Mr. Nguyen",
        sprite_id    = "nguyen",
        log_name     = "Nguyen",
        tier         = "medium",
        max_hp       = 110,
        deck_template = ["knockoff_swing", "stall_swarm", "haggle", "lockup", "markdown"],
        wrinkle      = "counterfeit_drop",
        detour_lines = [
            "He smiles. The stánkaři close ranks. You're walked back to the parking lot.",
            "The next morning the warehouse is empty. The case files itself as 'no evidence'.",
        ],
    )

    register_enemy(
        "grundza",
        display_name = "Grundza",
        sprite_id    = "grundza",
        bg_id        = "varic",
        log_name     = "Grundza",
        tier         = "medium",
        max_hp       = 125,
        deck_template = ["fume_swipe", "chem_burn", "chem_stoke", "lab_check", "gas_release"],
        wrinkle      = "lab_timer",
        wrinkle_data = {"detonation_turn": 7, "detonation_dmg": 20},
        detour_lines = [
            "The lab door slams. Half the squad's gear comes back contaminated.",
            "Internal Affairs pencils your name in the column marked 'incident'.",
        ],
    )

    register_enemy(
        "lawyer",
        display_name = "Mgr. Procházka",
        sprite_id    = "lawyer",
        bg_id        = "courtroom",
        log_name     = "Counsel",
        tier         = "medium",
        max_hp       = 120,
        deck_template = ["objection", "cross_examine", "paragraph_5_2", "procedural_shield", "build_argument", "intimidate"],
        wrinkle      = "paragraph_cite",
        wrinkle_data = {"cadence": 3, "bonus_dmg": 6},
        detour_lines = [
            "The judge nods at his closing. Your statement gets read back to you in his voice, two octaves lower. You sign whatever's slid across the bench.",
            "He shakes your lieutenant's hand on the way out. The case is dismissed before the door closes.",
        ],
    )

    register_enemy(
        "dispatcher",
        display_name = "Dispatch Officer",
        sprite_id    = "dispatcher",
        log_name     = "Dispatch",
        tier         = "medium",
        max_hp       = 110,
        deck_template = ["priority_call", "all_units", "false_alarm", "silence", "frequency_jam"],
        wrinkle      = "priority_change",
        detour_lines = [
            "Your case is reassigned to someone who won't read it. Three priority changes before lunch.",
            "The radio goes quiet for two hours. You sit in the car, looking at the wrong street.",
        ],
    )

    ## ---------------------------------------------------------------------------
    ## HARD tier (days 19-28)
    ## ---------------------------------------------------------------------------

    register_enemy(
        "inspekce",
        display_name = "Internal Affairs",
        sprite_id    = "inspekce",
        log_name     = "Internal Affairs",
        tier         = "hard",
        max_hp       = 150,
        deck_template = [
            "interview", "audit", "quote_regulation",
            "formal_warning", "case_review", "wire_check", "transfer_pending",
        ],
        wrinkle      = "paperwork_injection",
        detour_lines = [
            "She doesn't raise her voice. She slides three forms across the table. Sign here. Initial. Here.",
            "You're at a desk job by Monday. The badge stays in your drawer for now.",
        ],
    )

    register_enemy(
        "garda",
        display_name = "Colonel's Guard",
        sprite_id    = "garda",
        log_name     = "Guard",
        tier         = "hard",
        max_hp       = 180,
        deck_template = [
            "breach_swing", "kettle", "shield_wall", "gas_throw",
            "baton_combo", "formation_buff", "phalanx_block", "clear_room",
        ],
        wrinkle      = "formation_strength",
        detour_lines = [
            "The breach team puts you face-down on the parking-lot asphalt. They were never your team.",
            "You sign whatever paperwork they slide under you. The Colonel doesn't have to be in the room.",
        ],
    )
