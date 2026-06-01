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
##   intro_lines   pre-battle cinematic narration list. Slide 1 is the
##                 location/why-you're-here over the bg; slide 2 is the enemy
##                 reveal (sprite enters); slides 3+ are extra beats over the
##                 same sprite/bg, used when one reveal slide would overflow
##                 the text-box. <2 entries skips the intro (Colonel — own event).
##   detour_lines  forced-detour narration on loss (empty for Colonel — his loss
##                 routes to colonel_defeat_ending, not the shared detour label)
##   victory_lines post-victory narration shown before the cash receipt; each
##                 entry is one narrator say-line. Empty list falls back to the
##                 bare cash payout with no flavor (Colonel — own event)
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
            "intro_lines":   [],
            "detour_lines":  [],
            "victory_lines": [],
            ## Act bosses — fired on fixed days by boss_check(), not the random
            ## pool. is_boss drives the boss banner + guaranteed relic reward.
            ## no_flee hides the "let them go" option — battle_with honours it.
            ## Act bosses leave it False (they ARE deniable: a flee-everything
            ## Pacifist run must be able to walk past them); the flag is kept as
            ## a live lever for any future genuinely-mandatory ladder fight.
            ## act marks which act this boss caps (1/2).
            "is_boss":       False,
            "no_flee":       False,
            ## LET THEM GO overrides — flee_relief replaces the tier Hatred
            ## relief for this enemy; flee_czk_penalty docks cash (the Colonel's
            ## cut for letting a case slide); flee_label overrides the button
            ## text (e.g. "LET HIM GO" for a lone suspect). Defaults: tier
            ## relief, no penalty, the generic label.
            "flee_relief":      None,
            "flee_czk_penalty": 0,
            "flee_label":       None,
            "act":           0,
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

        ## Colonel's Guard — the breach team never strings two passive turns
        ## together. A defend or a buff must be answered by a hit, so the player
        ## always eats an attack at least every other turn (chained attacks are
        ## fine; only block/buff back-to-back is forbidden). Mirrors the block
        ## anti-adjacency above but on the attack / non-attack split, including
        ## the reshuffle boundary via prev_card_id.
        if enemy_id == "garda":
            def _is_atk(cid):
                return _intent_of(cid) in ("attack", "compound")
            if prev_card_id is not None and not _is_atk(prev_card_id) and deck and not _is_atk(deck[0]):
                for j in range(1, len(deck)):
                    if _is_atk(deck[j]):
                        deck[0], deck[j] = deck[j], deck[0]
                        break
            for i in range(len(deck) - 1):
                if not _is_atk(deck[i]) and not _is_atk(deck[i + 1]):
                    for j in range(i + 2, len(deck)):
                        if _is_atk(deck[j]):
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
        max_hp       = 95,
        flee_relief      = 25,
        flee_czk_penalty = 1000,
        deck_template = ["rvac_swing", "rvac_haymaker", "rvac_drink"],
        wrinkle      = "drunken_double",
        intro_lines  = [
            "Dispatch routes you to a bar off Mírové náměstí. Noise complaint — the third tonight, same address.",
            "He's still on his feet when you push through the door. Swaying. Knuckles split. He looks at the badge and decides it changes nothing.",
        ],
        detour_lines = [
            "The brawler clocks you. You wake up in the alley behind the bar with a split lip.",
            "The watch commander writes it up wrong on purpose. The bar gets a warning. You get the blame.",
        ],
        victory_lines = [
            "The brawler goes down on the bar mat. There's a roll in his back pocket — the night's takings he was about to walk out the door with.",
            "The barman watches you find it and decides he never had a register. Three thousand, off the books on the way in, off the books on the way out.",
        ],
    )

    register_enemy(
        "sprejeri",
        display_name = "Taggers",
        sprite_id    = "sprejeri",
        log_name     = "Taggers",
        tier         = "easy",
        max_hp       = 80,
        deck_template = ["tag_quick", "tag_team", "spray_blind", "vandal_block"],
        wrinkle      = "tag_stack",
        intro_lines  = [
            "Another vandalism call — the kind dispatch saves for whoever picks up last. You picked up. Kids, a wall, a tunnel: exactly the job you're trying to code your way out of.",
            "Three of them down the tunnel, in no hurry — they've been chased out of here so often it's basically cardio. One caps a fresh can and asks if you want your name on the wall too.",
        ],
        detour_lines = [
            "They scatter through the panelák stairwells. You chase one to the third floor. He vanishes through a corridor that was never on the plan.",
            "Three more tags appear by morning. One of them looks like your face.",
        ],
        victory_lines = [
            "Two of them you book. The third drops a backpack and runs — twenty cans of Montana inside, fresh from the shop in Liberec that doesn't ask for ID.",
            "The shop in Liberec also doesn't ask where the cans came back from. Three thousand crowns, paid out in fifties, paint still rattling.",
        ],
    )

    register_enemy(
        "fanousek",
        display_name = "Hooligan",
        sprite_id    = "fanousek",
        log_name     = "Hooligan",
        tier         = "easy",
        max_hp       = 85,
        flee_label   = "LET HIM GO",
        deck_template = ["chant", "flare_throw", "pile_in"],
        wrinkle      = "crew_rage",
        wrinkle_data = {"hp_threshold": 0.6, "bonus_dmg": 5},
        intro_lines  = [
            "End of a long match-day shift — twelve hours minding other men's tempers, and you want it done. Dispatch isn't done with you: one supporter never made it onto his bus.",
            "His side lost three-nil and the crowd left without him. He's had two hours alone to stew on it. Then you walk in — the first thing all night he can do something about.",
        ],
        detour_lines = [
            "His crew finds you behind the bus station. They take turns on your kidneys.",
            "You file the report from the ER. The match was a draw, they tell each other.",
        ],
        victory_lines = [
            "You cuff him on the curb. His wallet's still fat with match-day drinking money he never got the chance to spend.",
            "Evidence bag for the flare. Pocket for the cash. Nobody at the station counts it twice.",
        ],
    )

    register_enemy(
        "spis",
        display_name = "Case File",
        sprite_id    = "spis",
        log_name     = "Case File",
        tier         = "easy",
        max_hp       = 75,
        deck_template = ["dossier_flick", "read_aloud", "paper_wall", "file_swap"],
        wrinkle      = "paper_clog",
        intro_lines  = [
            "Back at the station, past midnight. A case you closed last week has reopened itself — wrong form, wrong box, wrong name.",
            "The file waits on your desk, thicker than you left it. Every page you correct breeds two more — and the suspect named inside it is released at four o'clock.",
        ],
        detour_lines = [
            "The file folds itself shut. The kid in it walks at 4 PM.",
            "Your name ends up on the cover. Misfiled. They don't fix it.",
        ],
        victory_lines = [
            "The folder closes itself once you've signed every page in the right column. An envelope was clipped inside — pre-filled, untraceable, the kid's lawyer's way of speeding things along.",
            "The envelope didn't make it into the dossier. The kid still walks at four. Three thousand, processing fee, call it what you like.",
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
        intro_lines  = [
            "The Vietnamese market on the edge of town. Counterfeit goods, the report says. You've walked these aisles before and left empty-handed.",
            "Mr. Nguyen meets you at his stall, already smiling, already negotiating. Behind him the stánkaři stop restocking and start watching.",
        ],
        detour_lines = [
            "He smiles. The stánkaři close ranks. You're walked back to the parking lot.",
            "The next morning the warehouse is empty. The case files itself as 'no evidence'.",
        ],
        victory_lines = [
            "He pays the fine before you've written it — exact change, in fifties, smile unchanged. The receipt he hands you back is in Vietnamese.",
            "You don't ask for a translation. Five thousand crowns; the warehouse stays open another month; everybody got something they wanted.",
        ],
    )

    register_enemy(
        "grundza",
        display_name = "Grundza",
        sprite_id    = "grundza",
        bg_id        = "varic",
        log_name     = "Grundza",
        tier         = "boss",
        is_boss      = True,
        no_flee      = False,
        act          = 1,
        max_hp       = 160,
        deck_template = ["fume_swipe", "chem_burn", "chem_stoke", "lab_check", "gas_release"],
        wrinkle      = "lab_timer",
        wrinkle_data = {"detonation_turn": 6, "detonation_dmg": 32},
        intro_lines  = [
            "A tip, an address, three flights of stairs. You smelled what was up here before you reached the door — and you climbed anyway. Somebody's mother cooked dinner in this kitchen once. Tonight it cooks something else.",
            "Grundza doesn't look up from the rig. He's cooked through two raids in this kitchen and neither one rushed him. He knows to the minute when the batch turns — and when the room stops being a room. You have until then.",
        ],
        detour_lines = [
            "The lab door slams. Half the squad's gear comes back contaminated.",
            "Internal Affairs pencils your name in the column marked 'incident'.",
        ],
        victory_lines = [
            "The rig goes cold. There's a tin taped under the sink — vendor float, five-hundred-crown notes bricked together, the kind of money nobody reports missing from a kitchen that wasn't supposed to exist.",
            "Three notes go into evidence. The rest goes down the stairs with you, before the next shift gets here to inventory the room.",
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
        intro_lines  = [
            "District court, hearing room two. Your case, your evidence, your testimony. All it needs now is for you to hold up under questioning.",
            "Mgr. Procházka rises for the defense. He doesn't look at the jury. He looks at you — and finds the paragraph that turns your report into his.",
        ],
        detour_lines = [
            "The judge nods at his closing. Your statement gets read back to you in his voice, two octaves lower. You sign whatever's slid across the bench.",
            "He shakes your lieutenant's hand on the way out. The case is dismissed before the door closes.",
        ],
        victory_lines = [
            "The judge awards costs against his client. By the time payroll routes it through the right ledgers half of it has evaporated into processing — you get the half the paperwork couldn't catch.",
            "Procházka shakes your hand on the way out anyway. For him this was a Tuesday. Five thousand crowns; he'll make it back before the elevator hits the ground floor.",
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
        intro_lines  = [
            "The calls wouldn't stop — wrong frequencies, jobs never logged, a voice that knew your unit number. You stopped trying to explain it and came to the dispatch hall yourself, long after the last shift clocked out.",
            "There's no one in the chair. There never was. The voice comes through every speaker on the floor at once — flat, unhurried, already reading your call sign back to you. It would like to know your location.",
        ],
        detour_lines = [
            "Your case is reassigned to someone who won't read it. Three priority changes before lunch.",
            "The radio goes quiet for two hours. You sit in the car, looking at the wrong street.",
        ],
        victory_lines = [
            "The speakers cut out mid-sentence. A hazard-pay form is already in the printer when you turn around — wrong code, right amount, signed off by a hand you don't recognise.",
            "You don't ask which voice authorised it. The cheque clears Monday. Five thousand crowns for a shift that, on paper, you were never on.",
        ],
    )

    register_enemy(
        "vlk",
        display_name = "Vlk z Mostu",
        sprite_id    = "vlk",
        log_name     = "Vlk",
        tier         = "medium",
        max_hp       = 105,
        deck_template = ["vlk_buyin", "vlk_dividend", "vlk_referral", "vlk_confidence", "vlk_hard_sell", "vlk_margin_call"],
        wrinkle      = "ponzi",
        wrinkle_data = {"margin_per_buyin": 5, "returns_inject_turn": 2, "bluff_drop": 2, "buyin_cap": 10},
        intro_lines  = [
            "A rented conference room above a shopping centre in Most. Three pensioners filed complaints. Forty more are sure they made money.",
            "Vlk doesn't pause the presentation when you walk in. He pulls out a chair for you. By the time you sit, he's explaining why the badge should invest.",
        ],
        detour_lines = [
            "He shakes your hand on the way out. Your account is lighter and you can't say exactly when that happened.",
            "The case closes itself. He's already three towns over, in another rented room, in front of people who haven't met him yet.",
        ],
        victory_lines = [
            "He's already packing the projector when one of the pensioners catches you at the door. She presses an envelope into your hand — finder's fee, she calls it, for getting her deposit back before he reached the next town.",
            "You try to refuse. She's already gone. Five thousand crowns of her own pension money, handed back to the man who stopped him taking it.",
        ],
    )

    ## ---------------------------------------------------------------------------
    ## HARD tier (days 18-28)
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
        intro_lines  = [
            "Internal Affairs. The summons came on department letterhead, no reason given. You signed in your own weapon to walk into this room.",
            "Your file has been read three times — he could recite it back to you. No raised voice, no threats: just paper sliding across the table, and a man patient enough to wait for the part where you sign.",
        ],
        detour_lines = [
            "He doesn't raise his voice. He slides three forms across the table. Sign here. Initial. Here.",
            "You're at a desk job by Monday. The badge stays in your drawer for now.",
        ],
        victory_lines = [
            "He stacks the signed forms into a neat pile. Three months of suspended overtime get released the same afternoon — the figure was already typed into the slip before you sat down.",
            "Seventy-five hundred crowns of your own money, handed back the moment you agreed to behave. He doesn't call it a bribe. He doesn't have to.",
        ],
    )

    register_enemy(
        "garda",
        display_name = "Colonel's Guard",
        sprite_id    = "garda",
        log_name     = "Guard",
        tier         = "boss",
        is_boss      = True,
        no_flee      = False,
        act          = 2,
        max_hp       = 210,
        deck_template = [
            "breach_swing", "shield_wall", "gas_throw",
            "baton_combo", "formation_buff", "phalanx_block", "clear_room",
        ],
        wrinkle      = "formation_strength",
        intro_lines  = [
            "Past midnight. This is where they keep the Colonel — behind the fence, behind other men. You've had enough of waiting for the day he picked. You came for him tonight.",
            "Three of them come around the van — balaclavas, no names, no faces. Zásahová jednotka: the unit you send once the talking is over. The Colonel didn't send anyone you could reason with — he sent the ones who were never going to ask why.",
        ],
        detour_lines = [
            "The breach team puts you face-down on the parking-lot asphalt. They were never your team.",
            "You sign whatever paperwork they slide under you. The Colonel doesn't have to be in the room.",
        ],
        victory_lines = [
            "The last balaclava goes down on the asphalt. The op-fund envelope is in the lead van's glovebox — cash for informants, fuel, receipts that were never going to be filed.",
            "You take what was always going to disappear. Seventy-five hundred crowns of the Colonel's own operating budget, walking out of the lot in your jacket.",
        ],
    )

    register_enemy(
        "lifer",
        display_name = "The Lifer",
        sprite_id    = "lifer",
        log_name     = "The Lifer",
        tier         = "hard",
        max_hp       = 165,
        deck_template = [
            "lifer_pension", "lifer_what_now", "lifer_the_offer",
            "lifer_settle_in", "lifer_seniority", "lifer_routine", "lifer_quiet_word",
        ],
        wrinkle      = "golden_handcuffs",
        wrinkle_data = {"strength_per_stall": 2},
        intro_lines  = [
            "Past midnight. You came back for the last of your things and stopped at the washroom mirror — the one you've walked past a thousand times without ever looking in.",
            "The reflection doesn't move when you do. Then it puts a hand on the rim of the sink and climbs out through the glass, and you know it before fear has time to catch up — the way you know a voice on the phone.",
            "It holds out a pair of handcuffs your size and waits, patient and kind, for you to stop being silly.",
        ],
        detour_lines = [
            "You put them on yourself. Lighter than expected. Warm, even.",
            "The transfer paperwork goes back in the drawer. The desk was always going to be comfortable.",
        ],
        victory_lines = [
            "The reflection lowers the cuffs and steps back into the mirror. A retirement lump-sum slip is on the counter when you come out — signed in a handwriting almost yours.",
            "You leave the slip on the tile. The money clears anyway. Seventy-five hundred crowns of a pension you haven't earned.",
        ],
    )

    register_enemy(
        "estebak",
        display_name = "The Old Man",
        sprite_id    = "estebak",
        log_name     = "The Old Man",
        tier         = "hard",
        max_hp       = 155,
        deck_template = [
            "estebak_dossier", "estebak_redaction", "estebak_old_tape",
            "estebak_archive", "estebak_surveillance", "estebak_case_open", "estebak_summons",
        ],
        wrinkle      = "the_file",
        wrinkle_data = {"drawer_cap": 6},
        intro_lines  = [
            "You went looking for the file the Colonel keeps over you — the car accident, the thing he buried. The trail led down past the basement, past the boiler room, to an archive door with no number.",
            "The records here run further back than the Republic, and the archive kept someone. He rises from the card-index without hurry, and you feel it the way you feel a draft from a door that shouldn't be open.",
            "He has read you cover to cover, and he'd like, very politely, to close the file.",
        ],
        detour_lines = [
            "A drawer slides shut somewhere in the dark. The part of you that wanted out gets suddenly, quietly hard to remember.",
            "You climb back up the stairs empty-handed. The file stays down there — and so, in a way you can't name, do you.",
        ],
        victory_lines = [
            "He goes down into his own card-index. A drawer falls open on the way and the money lands at your feet — old hundred-crown notes, pre-Republic, somehow still legal tender.",
            "You don't count them in the archive. You count them upstairs, in the boiler-room light, where the air remembers what year it is. Seventy-five hundred crowns the Republic forgot about.",
        ],
    )
