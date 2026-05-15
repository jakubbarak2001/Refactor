################################################################################
## REFACTOR — Card Library (Phase 1.2+)
##
## Card definitions registered with register_card() at init time.
## Effect callables registered with @register_effect in card_effects.rpy.
##
## To add a card: copy a similar card below, change id/name/cost/effect.
## See docs/REFACTOR_PLAYBOOK.md for the card-design checklist.
################################################################################

init python:

    ## ---------------------------------------------------------------------------
    ## STRIKE / DEFEND — registered so they remain valid card_ids, but no longer
    ## granted by init_player_deck (Phase 3 empty-deck pivot). Reserved for
    ## possible future activity grants.
    ## ---------------------------------------------------------------------------

    register_card(
        "strike",
        name   = "Strike",
        type   = "Attack",
        color  = "Physical",
        cost   = 1,
        rarity = "common",
        effect = "deal_damage_6",
        flavor = "The simplest argument: hit harder.",
    )

    register_card(
        "defend",
        name   = "Defend",
        type   = "Skill",
        color  = "Mental",
        cost   = 1,
        rarity = "common",
        effect = "gain_block_5",
        flavor = "Don't take the bait.",
    )

    ## ---------------------------------------------------------------------------
    ## CLASS STARTERS — one signature card per class
    ## ---------------------------------------------------------------------------

    register_card(
        "heavy_set",
        name       = "Heavy Set",
        type       = "Attack",
        color      = "Physical",
        cost       = 1,
        rarity     = "uncommon",
        effect     = "heavy_set",
        class_lock = "bodybuilder",
        flavor     = "Every plate you've ever loaded. Stacked on the bar. Aimed at him.",
    )

    register_card(
        "read_him",
        name       = "Read Him",
        type       = "Skill",
        color      = "Mental",
        cost       = 1,
        rarity     = "uncommon",
        effect     = "read_him",
        class_lock = "dark_empath",
        flavor     = "You hold for a half-second. He swings where you were.",
    )

    register_card(
        "stack_up",
        name       = "Stack Up",
        type       = "Skill",
        color      = "Special",
        cost       = 0,
        rarity     = "uncommon",
        effect     = "stack_up",
        class_lock = "biohacker",
        flavor     = "+2 energy this turn. Crash next turn.",
    )

    ## ---------------------------------------------------------------------------
    ## ACTIVITY-GRANTED CARDS — added to deck by daily activities (Phase 1.3).
    ## ---------------------------------------------------------------------------

    ## GYM
    register_card(
        "iron_will",
        name   = "Iron Will",
        type   = "Skill",
        color  = "Physical",
        cost   = 1,
        rarity = "common",
        effect = "gain_block_12",
        flavor = "You stop flinching.",
    )
    register_card(
        "personal_record",
        name    = "Personal Record",
        type    = "Attack",
        color   = "Physical",
        cost    = 2,
        rarity  = "rare",
        effect  = "deal_damage_double_next",
        exhaust = True,
        flavor  = "Doubles the damage of your next attack this turn.",
    )

    ## THERAPY
    register_card(
        "boundary",
        name   = "Boundary",
        type   = "Skill",
        color  = "Mental",
        cost   = 1,
        rarity = "common",
        effect = "boundary",
        flavor = "Deal 4 and heal 4. The cost of saying no is less than the cost of saying yes.",
    )
    register_card(
        "reframe",
        name    = "Reframe",
        type    = "Skill",
        color   = "Mental",
        cost    = 1,
        rarity  = "uncommon",
        effect  = "reframe",
        exhaust = True,
        flavor  = "Convert the enemy's next attack into block for you.",
    )

    ## BOUNCER
    register_card(
        "side_income",
        name   = "Side Income",
        type   = "Attack",
        color  = "Money",
        cost   = 1,
        rarity = "common",
        effect = "side_income",
        flavor = "Damage equal to (savings / 10000), rounded down.",
    )
    register_card(
        "vip_treatment",
        name    = "VIP Treatment",
        type    = "Attack",
        color   = "Money",
        cost    = 2,
        rarity  = "rare",
        effect  = "vip_treatment",
        exhaust = True,
        flavor  = "Deal 30. Lose 10 HP. Worth it.",
    )

    ## CODING
    register_card(
        "refactor",
        name    = "Refactor",
        type    = "Skill",
        color   = "Logic",
        cost    = 2,
        rarity  = "uncommon",
        effect  = "refactor",
        exhaust = True,
        flavor  = "Cancel the enemy's next attack.",
    )
    register_card(
        "compile",
        name   = "Compile",
        type   = "Skill",
        color  = "Logic",
        cost   = 1,
        rarity = "common",
        effect = "compile",
        flavor = "Draw 2 cards.",
    )
    ## BOOTCAMP graduation card — substantial reward for the 35k investment.
    ## A versatile rare attack that rewards mixed hands.
    register_card(
        "production_push",
        name   = "Production Push",
        type   = "Attack",
        color  = "Logic",
        cost   = 1,
        rarity = "rare",
        effect = "production_push",
        flavor = "Tests pass. Lint passes. Push to main without flinching.",
    )

    ## NIGHT SHIFT
    register_card(
        "backup",
        name   = "Backup",
        type   = "Skill",
        color  = "Police",
        cost   = 1,
        rarity = "common",
        effect = "gain_block_15",
        flavor = "+15 block. Kovář has your six. Allegedly.",
    )
    register_card(
        "procedural_defense",
        name    = "Procedural Defense",
        type    = "Skill",
        color   = "Police",
        cost    = 2,
        rarity  = "uncommon",
        effect  = "procedural_defense",
        exhaust = True,
        flavor  = "Block all damage from his next attack turn. Exhausts.",
    )

    ## NOOTROPICS — Biohacker
    register_card(
        "racetam",
        name       = "Racetam Burst",
        type       = "Skill",
        color      = "Special",
        cost       = 0,
        rarity     = "uncommon",
        effect     = "racetam_burst",
        class_lock = "biohacker",
        flavor     = "+1 energy. Draw 1.",
    )
    register_card(
        "flmodafinil",
        name       = "FLModafinil Spike",
        type       = "Attack",
        color      = "Special",
        cost       = 2,
        rarity     = "rare",
        effect     = "flmodafinil_spike",
        class_lock = "biohacker",
        exhaust    = True,
        flavor     = "Deal 28. 50% chance: lose self for 1 turn.",
    )

    ## COLD READ — Dark Empath
    register_card(
        "mirror",
        name       = "Mirror",
        type       = "Skill",
        color      = "Mental",
        cost       = 2,
        rarity     = "rare",
        effect     = "mirror",
        class_lock = "dark_empath",
        exhaust    = False,
        flavor     = "Return the enemy's next attack at double damage. (2-turn cooldown.)",
    )

    ## ---------------------------------------------------------------------------
    ## EVENT-GRANTED CARDS — Phase 1.3+ (random events / Martin / Midnight Call)
    ## ---------------------------------------------------------------------------

    register_card(
        "algorithm",
        name    = "Algorithm",
        type    = "Skill",
        color   = "Logic",
        cost    = 2,
        rarity  = "rare",
        effect  = "algorithm",
        exhaust = True,
        flavor  = "Skip the enemy's next 2 attacks.",
    )
    register_card(
        "snitch_info",
        name    = "Snitch Info",
        type    = "Skill",
        color   = "Special",
        cost    = 1,
        rarity  = "uncommon",
        effect  = "snitch_info",
        exhaust = True,
        flavor  = "The voicemail was clean. The next swing isn't.",
    )

    ## MARTIN'S GIFTS — Phase 1.8 will replace final_boss_buff with these
    register_card(
        "paragraph_4b",
        name    = "Paragraph 4B",
        type    = "Attack",
        color   = "Logic",
        cost    = 2,
        rarity  = "boss",
        effect  = "paragraph_4b",
        exhaust = True,
        flavor  = "Deal 40. The 80k debt is void.",
    )
    register_card(
        "ghost_secret",
        name    = "Ghost Secret",
        type    = "Skill",
        color   = "Special",
        cost    = 1,
        rarity  = "boss",
        effect  = "ghost_secret",
        exhaust = True,
        flavor  = "Cancel one incoming attack. Deal 15. Leverage works on anyone with something to hide.",
    )
    register_card(
        "job_offer",
        name    = "Job Offer",
        type    = "Power",
        color   = "Money",
        cost    = 1,
        rarity  = "boss",
        effect  = "job_offer",
        flavor  = "+5 max HP at start. +1 starting block per turn.",
    )
    register_card(
        "stoic_refactor",
        name    = "Stoic Refactor",
        type    = "Power",
        color   = "Mental",
        cost    = 1,
        rarity  = "boss",
        effect  = "stoic_refactor",
        flavor  = "Power: take 50%% damage from Mental-typed attacks.",
    )

    register_card(
        "stoic_anchor",
        name    = "Stoic Anchor",
        type    = "Power",
        color   = "Mental",
        cost    = 1,
        rarity  = "uncommon",
        effect  = "stoic_anchor",
        flavor  = "Power: +2 starting block per turn. Heal 2 HP after each enemy attack.",
    )

    ## ---------------------------------------------------------------------------
    ## ADDITIONAL CARDS — broader pool granted via random events / opportunities
    ## ---------------------------------------------------------------------------

    register_card(
        "quick_jab",
        name   = "Quick Jab",
        type   = "Attack",
        color  = "Physical",
        cost   = 1,
        rarity = "common",
        effect = "quick_jab",
        flavor = "Deal 7. No setup. No follow-through.",
    )

    register_card(
        "loan_sharks",
        name    = "Loan Sharks",
        type    = "Attack",
        color   = "Money",
        cost    = 1,
        rarity  = "uncommon",
        effect  = "loan_sharks",
        exhaust = True,
        flavor  = "Pay 5,000 CZK now to deal 30 damage. (No funds = no damage.)",
    )

    register_card(
        "chain_of_command",
        name   = "Chain of Command",
        type   = "Skill",
        color  = "Police",
        cost   = 1,
        rarity = "uncommon",
        effect = "chain_of_command",
        flavor = "Gain 10 block and draw 1. Procedural calm.",
    )

    register_card(
        "vigil",
        name   = "Vigil",
        type   = "Skill",
        color  = "Mental",
        cost   = 1,
        rarity = "common",
        effect = "vigil",
        flavor = "Gain 4 block now. +4 starting block next turn.",
    )

    register_card(
        "iron_stance",
        name       = "Iron Stance",
        type       = "Power",
        color      = "Physical",
        cost       = 2,
        rarity     = "rare",
        effect     = "iron_stance",
        class_lock = "bodybuilder",
        flavor     = "+20 block. Retaliate scales with turn — early small, late lethal.",
    )

    ## ---------------------------------------------------------------------------
    ## Class-balance v2 additions
    ## ---------------------------------------------------------------------------

    register_card(
        "spotter",
        name       = "Spotter",
        type       = "Skill",
        color      = "Physical",
        cost       = 1,
        rarity     = "common",
        effect     = "spotter",
        class_lock = "bodybuilder",
        flavor     = "Gain 6 block. Draw 1. The trainer counts your reps.",
    )

    register_card(
        "brawl",
        name       = "Brawl",
        type       = "Attack",
        color      = "Physical",
        cost       = 2,
        rarity     = "uncommon",
        effect     = "brawl",
        class_lock = "bodybuilder",
        flavor     = "Deal 10 + apply 3-turn bleed (3 dmg/turn). The Colonel sees this is personal.",
    )

    ## Paid Review — BB's "buy your way past the skill gate" card. JB hits his
    ## coding ceiling at 100; this card lets bouncer cash do the work his
    ## keyboard can't. 10,000 CZK ≈ three solid bouncer nights. No funds → no
    ## effect (matches loan_sharks pattern).
    register_card(
        "paid_review",
        name       = "Paid Review",
        type       = "Skill",
        color      = "Tech",
        cost       = 1,
        rarity     = "rare",
        effect     = "paid_review",
        class_lock = "bodybuilder",
        exhaust    = True,
        flavor     = "You text the senior you met at the club. He's expensive. He's awake. He answers.",
    )

    register_card(
        "empaths_insight",
        name       = "Empath's Insight",
        type       = "Power",
        color      = "Mental",
        cost       = 1,
        rarity     = "rare",
        effect     = "empaths_insight",
        class_lock = "dark_empath",
        flavor     = "Their first move tells you their last. Block stacks.",
    )

    ## ---------------------------------------------------------------------------
    ## GOTY v2 — class identity cards (3 per class)
    ## ---------------------------------------------------------------------------

    ## BODYBUILDER — Iron-color, raw physical
    register_card(
        "iron_body",
        name       = "Iron Body",
        type       = "Skill",
        color      = "Physical",
        cost       = 1,
        rarity     = "common",
        effect     = "iron_body",
        class_lock = "bodybuilder",
        flavor     = "Gain 6 block. Retaliate 4 dmg the next time you're hit.",
    )

    register_card(
        "pump",
        name       = "Pump",
        type       = "Skill",
        color      = "Physical",
        cost       = 1,
        rarity     = "uncommon",
        effect     = "pump",
        class_lock = "bodybuilder",
        flavor     = "Gain 2 energy this turn. +5 Hatred. The veins talk.",
    )

    register_card(
        "strongman",
        name       = "Strongman",
        type       = "Skill",
        color      = "Physical",
        cost       = 3,
        rarity     = "rare",
        effect     = "strongman",
        class_lock = "bodybuilder",
        exhaust    = True,
        flavor     = "Gain 25 block + draw 2. The bar bends. The room watches.",
    )

    ## DARK EMPATH — Mental-color, info warfare
    register_card(
        "tell",
        name       = "Tell",
        type       = "Skill",
        color      = "Mental",
        cost       = 0,
        rarity     = "common",
        effect     = "tell",
        class_lock = "dark_empath",
        flavor     = "You see his shoulders set before the swing.",
    )

    register_card(
        "frame_trap",
        name       = "Frame Trap",
        type       = "Skill",
        color      = "Mental",
        cost       = 1,
        rarity     = "uncommon",
        effect     = "frame_trap",
        class_lock = "dark_empath",
        flavor     = "Reduce the enemy's next attack by 8 (minimum 1). Set the trap before they speak.",
    )

    register_card(
        "charm",
        name       = "Charm",
        type       = "Skill",
        color      = "Mental",
        cost       = 1,
        rarity     = "uncommon",
        effect     = "charm",
        class_lock = "dark_empath",
        flavor     = "Heal 8 HP and gain 3 block. You make the room think you belong.",
    )

    ## BIOHACKER — Special-color, optimization
    register_card(
        "hrv_spike",
        name       = "HRV Spike",
        type       = "Skill",
        color      = "Special",
        cost       = 1,
        rarity     = "common",
        effect     = "hrv_spike",
        class_lock = "biohacker",
        flavor     = "Gain 2 energy. Lose 5 HP. The crash is data.",
    )

    register_card(
        "cognitive_stack",
        name       = "Cognitive Stack",
        type       = "Skill",
        color      = "Special",
        cost       = 1,
        rarity     = "uncommon",
        effect     = "cognitive_stack",
        class_lock = "biohacker",
        exhaust    = True,
        flavor     = "Draw 3 cards. Exhausts. The compound knows what to do.",
    )

    register_card(
        "override",
        name       = "Override",
        type       = "Attack",
        color      = "Special",
        cost       = 2,
        rarity     = "rare",
        effect     = "override",
        class_lock = "biohacker",
        exhaust    = True,
        flavor     = "Deal 40 damage. -2 max energy next turn. The body pays the bill, then keeps moving.",
    )

    ## ---------------------------------------------------------------------------
    ## ARC-REWARD CARDS — only obtainable by completing the class arc
    ## ---------------------------------------------------------------------------

    register_card(
        "the_dossier",
        name       = "The Dossier",
        type       = "Skill",
        color      = "Mental",
        cost       = 2,
        rarity     = "boss",
        effect     = "the_dossier",
        class_lock = "dark_empath",
        exhaust    = True,
        flavor     = "Cancel one incoming attack. Deal 25. They know you have it.",
    )

    register_card(
        "the_compound",
        name       = "The Compound",
        type       = "Attack",
        color      = "Special",
        cost       = 1,
        rarity     = "boss",
        effect     = "the_compound",
        class_lock = "biohacker",
        exhaust    = True,
        flavor     = "Deal damage equal to current energy ×10. Lose 8 HP. The trial paid out.",
    )

    ## ---------------------------------------------------------------------------
    ## STORY-GRANT CARDS — granted by narrative choices, not activities.
    ## Day 1 / Car Incident: Admit → "Took the Heat".
    ## ---------------------------------------------------------------------------

    register_card(
        "took_the_heat",
        name    = "Took the Heat",
        type    = "Skill",
        color   = "Police",
        cost    = 1,
        rarity  = "uncommon",
        effect  = "took_the_heat",
        exhaust = True,
        flavor  = "Gain 10 block. Draw 1. You owned it. The next hit lands soft.",
    )

    ## ---------------------------------------------------------------------------
    ## BATTLE LADDER BASIC POOL — Body / Tech / Authority. No class-lock, no boss
    ## rarity. Composed from existing engine primitives (no new effect machinery).
    ## ---------------------------------------------------------------------------

    ## BODY — block, retaliate, money-scale
    register_card(
        "gut_punch",
        name   = "Gut Punch",
        type   = "Attack",
        color  = "Physical",
        cost   = 1,
        rarity = "common",
        effect = "gut_punch",
        flavor = "Deal 8. Below the ribs. He folds.",
    )
    register_card(
        "bracing",
        name   = "Bracing",
        type   = "Skill",
        color  = "Physical",
        cost   = 1,
        rarity = "common",
        effect = "bracing",
        flavor = "Gain 8 block. Square your stance.",
    )
    register_card(
        "second_wind",
        name   = "Second Wind",
        type   = "Skill",
        color  = "Physical",
        cost   = 2,
        rarity = "uncommon",
        effect = "second_wind",
        flavor = "Heal 6. Gain 8 block. The lungs come back.",
    )
    register_card(
        "body_check",
        name   = "Body Check",
        type   = "Attack",
        color  = "Physical",
        cost   = 2,
        rarity = "uncommon",
        effect = "body_check",
        flavor = "Deal 14. Drop your weight through them.",
    )
    register_card(
        "payday",
        name   = "Payday",
        type   = "Attack",
        color  = "Money",
        cost   = 1,
        rarity = "uncommon",
        effect = "payday",
        flavor = "Deal damage = Money / 5,000, max 20. Cash hits harder.",
    )
    register_card(
        "bouncer_door",
        name   = "Bouncer Door",
        type   = "Skill",
        color  = "Physical",
        cost   = 2,
        rarity = "rare",
        effect = "bouncer_door",
        flavor = "Gain 18 block. Retaliate 8 dmg on the next hit.",
    )

    ## TECH — draw, exhaust, scale
    register_card(
        "quick_compile",
        name   = "Quick Compile",
        type   = "Skill",
        color  = "Logic",
        cost   = 0,
        rarity = "common",
        effect = "quick_compile",
        flavor = "Draw 1. The build is green.",
    )
    register_card(
        "lint_pass",
        name   = "Lint Pass",
        type   = "Skill",
        color  = "Logic",
        cost   = 1,
        rarity = "common",
        effect = "lint_pass",
        flavor = "Exhaust a random card from hand. Draw 1. Strip the noise.",
    )
    register_card(
        "stack_trace",
        name   = "Stack Trace",
        type   = "Skill",
        color  = "Logic",
        cost   = 1,
        rarity = "uncommon",
        effect = "stack_trace",
        flavor = "Walk the call up. Two more swings ready.",
    )
    register_card(
        "unit_test",
        name   = "Unit Test",
        type   = "Skill",
        color  = "Logic",
        cost   = 1,
        rarity = "uncommon",
        effect = "unit_test",
        flavor = "Gain 6 block per Skill in hand. Coverage is armor.",
    )
    register_card(
        "merge_conflict",
        name   = "Merge Conflict",
        type   = "Attack",
        color  = "Logic",
        cost   = 2,
        rarity = "uncommon",
        effect = "merge_conflict",
        flavor = "Deal 10. Draw 1. Resolve theirs by overwriting.",
    )
    register_card(
        "kernel_patch",
        name    = "Kernel Patch",
        type    = "Skill",
        color   = "Logic",
        cost    = 2,
        rarity  = "rare",
        effect  = "kernel_patch",
        exhaust = True,
        flavor  = "Gain 1 energy. Draw 2. Live-patching mid-conversation.",
    )
    register_card(
        "pair_program",
        name   = "Pair Program",
        type   = "Skill",
        color  = "Logic",
        cost   = 0,
        rarity = "uncommon",
        effect = "pair_program",
        flavor = "Two heads on one problem.",
    )

    ## AUTHORITY — peek, cancel, status-friendly
    register_card(
        "radio_call",
        name   = "Radio Call",
        type   = "Skill",
        color  = "Police",
        cost   = 1,
        rarity = "common",
        effect = "radio_call",
        flavor = "Dispatch holds the corridor.",
    )
    register_card(
        "breath_test",
        name   = "Breath Test",
        type   = "Skill",
        color  = "Police",
        cost   = 1,
        rarity = "common",
        effect = "breath_test",
        flavor = "Reduce his next attack by 5 (min 1). 'Blow into the tube.'",
    )
    register_card(
        "procedural_kick",
        name   = "Procedural Kick",
        type   = "Attack",
        color  = "Police",
        cost   = 1,
        rarity = "common",
        effect = "procedural_kick",
        flavor = "Deal 5. Gain 5 block. By the book, with a boot.",
    )
    register_card(
        "riot_shield",
        name   = "Riot Shield",
        type   = "Skill",
        color  = "Police",
        cost   = 2,
        rarity = "uncommon",
        effect = "riot_shield",
        flavor = "Gain 14 block. +4 starting block next turn. Lock the line.",
    )
    register_card(
        "cuff_em",
        name    = "Cuff 'Em",
        type    = "Skill",
        color   = "Police",
        cost    = 2,
        rarity  = "uncommon",
        effect  = "cuff_em",
        exhaust = True,
        flavor  = "Skip his next attack. Steel on the wrist.",
    )
    register_card(
        "internal_review",
        name    = "Internal Review",
        type    = "Skill",
        color   = "Police",
        cost    = 1,
        rarity  = "rare",
        effect  = "internal_review",
        exhaust = True,
        flavor  = "Cancel his next attack. Deal 8. The case is on paper now.",
    )

    ## ---------------------------------------------------------------------------
    ## STATUS / CURSE CARDS — injected into the player's draw pile by enemy
    ## wrinkles. Marked pool_excluded so they never appear as ladder rewards.
    ## ---------------------------------------------------------------------------

    register_card(
        "paperwork",
        name          = "Paperwork",
        type          = "Skill",
        color         = "Special",
        cost          = 1,
        rarity        = "common",
        effect        = "status_paperwork",
        exhaust       = True,
        pool_excluded = True,
        flavor        = "Status. Fills the form. Plays itself out of your hand.",
    )
    register_card(
        "counterfeit",
        name          = "Counterfeit",
        type          = "Attack",
        color         = "Special",
        cost          = 1,
        rarity        = "common",
        effect        = "status_counterfeit",
        exhaust       = True,
        pool_excluded = True,
        flavor        = "Status. Deal 4. Take 8. Looked like a deal.",
    )
    register_card(
        "fumes",
        name          = "Fumes",
        type          = "Skill",
        color         = "Special",
        cost          = 1,
        rarity        = "common",
        effect        = "status_fumes",
        exhaust       = True,
        pool_excluded = True,
        flavor        = "Status. Take 2. The lab leaked.",
    )
    register_card(
        "tear_gas",
        name          = "Tear Gas",
        type          = "Skill",
        color         = "Special",
        cost          = 1,
        rarity        = "common",
        effect        = "status_tear_gas",
        exhaust       = True,
        pool_excluded = True,
        flavor        = "Status. Take 3. Eyes go first.",
    )

    ## ---------------------------------------------------------------------------
    ## RAGE CARDS — corruption injected by hatred thresholds (40/60/80).
    ## Permanent additions to the deck (no exhaust). High raw damage, self-
    ## corrupting side effects. The deck IS the 30 days; bad days stick.
    ## See _check_rage_injection in python_logic.rpy.
    ## ---------------------------------------------------------------------------

    register_card(
        "outburst",
        name          = "Outburst",
        type          = "Attack",
        color         = "Rage",
        cost          = 1,
        rarity        = "uncommon",
        effect        = "outburst",
        is_rage       = True,
        pool_excluded = True,
        flavor        = "You said it. You can't unsay it. The doorframe doesn't survive either.",
    )
    register_card(
        "tunnel_vision",
        name          = "Tunnel Vision",
        type          = "Attack",
        color         = "Rage",
        cost          = 1,
        rarity        = "uncommon",
        effect        = "tunnel_vision",
        is_rage       = True,
        pool_excluded = True,
        flavor        = "All you see is him. The hand forgets what else it was holding.",
    )
    register_card(
        "snap",
        name          = "Snap",
        type          = "Attack",
        color         = "Rage",
        cost          = 0,
        rarity        = "rare",
        effect        = "snap",
        is_rage       = True,
        pool_excluded = True,
        flavor        = "Free swing. A card in your hand burns out for the rest of the fight.",
    )

    ## ---------------------------------------------------------------------------
    ## COMPROMISE — loss-injected dead-weight card (granted by forced_detour
    ## on the 2nd+ ladder loss). Permanent in deck, UNPLAYABLE (occupies a
    ## hand slot and can't be cycled). Removable via the Fixer at a discount.
    ## ---------------------------------------------------------------------------

    register_card(
        "compromise",
        name          = "Compromise",
        type          = "Skill",
        color         = "Compromise",
        cost          = 0,
        rarity        = "common",
        effect        = "compromise",
        is_compromise = True,
        unplayable    = True,
        pool_excluded = True,
        flavor        = "Something you let go that you can't take back.",
    )

    ## ---------------------------------------------------------------------------
    ## COMBAT REWARDS — rare-tier cards designed to drop from ladder fights.
    ## Heavier mechanics than activity-granted commons/uncommons; the ladder
    ## is the path to power. Tier weights in pick_battle_rewards bias toward
    ## these (Hard fights drop rare 70% of the time).
    ## ---------------------------------------------------------------------------

    register_card(
        "killing_blow",
        name    = "Killing Blow",
        type    = "Attack",
        color   = "Physical",
        cost    = 2,
        rarity  = "rare",
        effect  = "killing_blow",
        flavor  = "Deal 14. If they're below half HP: deal 14 more. Finish what you started.",
    )
    register_card(
        "tactical_read",
        name    = "Tactical Read",
        type    = "Skill",
        color   = "Logic",
        cost    = 0,
        rarity  = "rare",
        effect  = "tactical_read",
        exhaust = True,
        flavor  = "One look at the board. You go again.",
    )
    register_card(
        "iron_drill",
        name    = "Iron Drill",
        type    = "Skill",
        color   = "Physical",
        cost    = 2,
        rarity  = "rare",
        effect  = "iron_drill",
        flavor  = "Gain 12 block + 4 block per Skill in hand (cap +12). Reps compound.",
    )
    register_card(
        "last_stand",
        name    = "Last Stand",
        type    = "Attack",
        color   = "Physical",
        cost    = 2,
        rarity  = "rare",
        effect  = "last_stand",
        exhaust = True,
        flavor  = "Deal 16. If you're under half HP, draw 2. Exhausts.",
    )

    ## ---------------------------------------------------------------------------
    ## UPGRADE TABLE — back-fill `_plus` variants for every upgradeable base
    ## card. Status / rage / compromise cards are intentionally absent (they're
    ## dead-weight by design — can't sand off corruption with a gym session).
    ##
    ## Balance philosophy (see plan thread):
    ##   - Commons: tiny bumps (Strike 6→9, Defend 5→8). "Don't upgrade these,
    ##     remove them." The lesson is deck-thinning, not deck-buffing.
    ##   - Uncommons: ~25–30% bump on the main number, or one quality-of-life
    ##     toggle (exhaust off, cost down).
    ##   - Rares: conservative scalar bump. Already strong; don't break them.
    ##   - Powers: small (compounds across turns).
    ##   - Money / stat scalers: tighten the ratio, not the cap.
    ##
    ## Effect-id convention: `<base_id>_plus` for everything, even pure scalar
    ## bumps. Verbose but unambiguous — no shared numeric ids between cards.
    ## ---------------------------------------------------------------------------

    ## Universal starters
    register_upgrade("strike",                effect="strike_plus",                flavor="The simplest argument: hit harder. Then a little harder.")
    register_upgrade("defend",                effect="defend_plus",                flavor="Don't take the bait. Don't take the punch.")

    ## Class starters
    register_upgrade("heavy_set",             effect="heavy_set_plus",             flavor="Every plate you've ever loaded. Aimed at him. Plus one more.")
    register_upgrade("read_him",              effect="read_him_plus",              flavor="You hold for a half-second longer. He swings at empty air.")
    register_upgrade("stack_up",              effect="stack_up_plus",              flavor="+2 energy this turn. Draw a card while the room blurs.")

    ## Gym
    register_upgrade("iron_will",             effect="iron_will_plus",             flavor="You stop flinching. You stop apologizing for not flinching.")
    register_upgrade("personal_record",       effect="personal_record_plus",       exhaust=False, flavor="Doubles your next attack. The bar tells the truth, repeatedly.")

    ## Therapy
    register_upgrade("boundary",              effect="boundary_plus",              flavor="Deal 6 and heal 6. Saying no costs even less than you thought.")
    register_upgrade("reframe",               effect="reframe",                    cost=0, flavor="Convert the enemy's next attack into block for you. Free now.")

    ## Bouncer
    register_upgrade("side_income",           effect="side_income_plus",           flavor="Damage equal to (savings / 8,000). Cash works harder.")
    register_upgrade("vip_treatment",         effect="vip_treatment_plus",         flavor="Deal 34. Lose 10 HP. Still worth it.")

    ## Coding
    register_upgrade("refactor",              effect="refactor",                   cost=1, flavor="Cancel the enemy's next attack. Cheaper now. Exhausts.")
    register_upgrade("compile",               effect="compile_plus",               flavor="Draw 3 cards.")
    register_upgrade("production_push",       effect="production_push_plus",       flavor="Tests pass. Lint passes. Push to main while looking him in the eye.")

    ## Night Shift
    register_upgrade("backup",                effect="backup_plus",                flavor="+14 block. Kovář has your six. For real this time.")
    register_upgrade("procedural_defense",    effect="procedural_defense",         cost=1, flavor="Block all damage from his next attack turn. Cheaper. Exhausts.")

    ## Nootropics (BH)
    register_upgrade("racetam",               effect="racetam_plus",               flavor="+1 energy. Draw 2.")
    register_upgrade("flmodafinil",           effect="flmodafinil_plus",           flavor="Deal 32. 50%%: lose self for 1 turn. Exhausts.")

    ## Cold Read (DE)
    register_upgrade("mirror",                effect="mirror_plus",                flavor="Return the enemy's next attack at 2x. +5 block on play. 2-turn cooldown.")

    ## Event drops
    register_upgrade("algorithm",             effect="algorithm_plus",             flavor="Skip the enemy's next 3 attacks. Exhausts.")
    register_upgrade("snitch_info",           effect="snitch_info_plus",           flavor="The voicemail was clean. The next swings aren't.")
    register_upgrade("paragraph_4b",          effect="paragraph_4b_plus",          flavor="Deal 48. The 80k debt is dust.")
    register_upgrade("ghost_secret",          effect="ghost_secret_plus",          flavor="Cancel one incoming attack. Deal 20. Leverage compounds.")
    register_upgrade("job_offer",             effect="job_offer_plus",             flavor="+8 max HP at start. +1 starting block per turn.")
    register_upgrade("stoic_refactor",        effect="stoic_refactor_plus",        flavor="Power: take 50%% damage from Mental-typed attacks.")
    register_upgrade("stoic_anchor",          effect="stoic_anchor_plus",          flavor="Power: +3 starting block per turn. Heal 2 HP after each enemy attack.")

    ## Additional cards
    register_upgrade("quick_jab",             effect="quick_jab_plus",             flavor="Deal 10. Still no setup. Still no follow-through.")
    register_upgrade("loan_sharks",           effect="loan_sharks_plus",           flavor="Pay 5,000 CZK to deal 36 damage. Exhausts.")
    register_upgrade("chain_of_command",      effect="chain_of_command_plus",      flavor="Gain 13 block and draw 1. The chain is shorter than it was.")
    register_upgrade("vigil",                 effect="vigil_plus",                 flavor="Gain 6 block now. +6 starting block next turn.")
    register_upgrade("iron_stance",           effect="iron_stance_plus",           flavor="+24 block. Retaliate scales with turn — late game is lethal.")
    register_upgrade("spotter",               effect="spotter_plus",               flavor="Gain 9 block. Draw 1. The trainer counts louder.")
    register_upgrade("brawl",                 effect="brawl_plus",                 flavor="Deal 12 + 4-turn bleed (4 dmg/turn). It IS personal.")
    register_upgrade("paid_review",           effect="paid_review_plus",           flavor="The senior charges 8,000 now. He's still awake. He still answers.")
    register_upgrade("empaths_insight",       effect="empaths_insight_plus",       flavor="Their first move tells you their last four. Block stacks.")

    ## GOTY v2 class identity
    register_upgrade("iron_body",             effect="iron_body_plus",             flavor="Gain 8 block. Retaliate 6 dmg the next time you're hit.")
    register_upgrade("pump",                  effect="pump_plus",                  flavor="Gain 2 energy this turn. +3 Hatred. Less roar, more aim.")
    register_upgrade("strongman",             effect="strongman_plus",             flavor="Gain 28 block + draw 2. The bar doesn't survive this one.")
    register_upgrade("tell",                  effect="tell_plus",                  flavor="You see his shoulders set, his eyes flick. Free 11 block.")
    register_upgrade("frame_trap",            effect="frame_trap_plus",            flavor="Reduce the enemy's next attack by 11 (minimum 1).")
    register_upgrade("charm",                 effect="charm_plus",                 flavor="Heal 10 HP and gain 5 block. You own the room now.")
    register_upgrade("hrv_spike",             effect="hrv_spike_plus",             flavor="Gain 2 energy. Lose 3 HP. Smaller crash, same lift.")
    register_upgrade("cognitive_stack",       effect="cognitive_stack_plus",       flavor="Draw 4 cards. Exhausts. The compound is dialed in.")
    register_upgrade("override",              effect="override_plus",              flavor="Deal 44 damage. -2 max energy next turn. Exhausts.")

    ## Arc rewards
    register_upgrade("the_dossier",           effect="the_dossier_plus",           flavor="Cancel one incoming attack. Deal 30. They know what you have.")
    register_upgrade("the_compound",          effect="the_compound_plus",          flavor="Deal damage equal to current energy ×12. Lose 12 HP. Trial doubled.")

    ## Story grants
    register_upgrade("took_the_heat",         effect="took_the_heat_plus",         flavor="Gain 13 block. Draw 1. You owned it, twice.")

    ## Battle ladder basics — Body
    register_upgrade("gut_punch",             effect="gut_punch_plus",             flavor="Deal 11. Below the ribs. He folds harder.")
    register_upgrade("bracing",               effect="bracing_plus",               flavor="Gain 11 block. Square your stance, lower your center.")
    register_upgrade("second_wind",           effect="second_wind_plus",           flavor="Heal 8. Gain 10 block. The lungs come back deeper.")
    register_upgrade("body_check",            effect="body_check_plus",            flavor="Deal 17. Drop your full weight through them.")
    register_upgrade("payday",                effect="payday_plus",                flavor="Deal damage = Money / 4,000, max 20. Cash hits sharper.")
    register_upgrade("bouncer_door",          effect="bouncer_door_plus",          flavor="Gain 22 block. Retaliate 10 dmg on the next hit.")

    ## Battle ladder basics — Tech
    register_upgrade("quick_compile",         effect="quick_compile_plus",         flavor="Draw 2. The build is green.")
    register_upgrade("lint_pass",             effect="lint_pass_plus",             flavor="Exhaust a random card from hand. Draw 2.")
    register_upgrade("stack_trace",           effect="stack_trace_plus",           flavor="Walk the call up. Three more swings ready.")
    register_upgrade("unit_test",             effect="unit_test_plus",             flavor="Gain 8 block per Skill in your hand (cap 32).")
    register_upgrade("merge_conflict",        effect="merge_conflict_plus",        flavor="Deal 13. Draw 1. Resolve theirs harder.")
    register_upgrade("kernel_patch",          effect="kernel_patch_plus",          flavor="Gain 1 energy. Draw 3. Exhausts.")
    register_upgrade("pair_program",          effect="pair_program_plus",          flavor="Gain 5 block. Draw 1. Free.")

    ## Battle ladder basics — Authority
    register_upgrade("radio_call",            effect="radio_call_plus",            flavor="Dispatch holds the whole block.")
    register_upgrade("breath_test",           effect="breath_test_plus",           flavor="Reduce his next attack by 8 (min 1).")
    register_upgrade("procedural_kick",       effect="procedural_kick_plus",       flavor="Deal 7. Gain 7 block. By the book, harder boot.")
    register_upgrade("riot_shield",           effect="riot_shield_plus",           flavor="Gain 17 block. +6 starting block next turn.")
    register_upgrade("cuff_em",               effect="cuff_em",                    cost=1, flavor="Skip his next attack. Cheaper now. Exhausts.")
    register_upgrade("internal_review",       effect="internal_review_plus",       flavor="Cancel his next attack. Deal 12 damage. Exhausts.")

    ## Combat-reward rares
    register_upgrade("killing_blow",          effect="killing_blow_plus",          flavor="Deal 16. If they're below half HP: deal 16 more.")
    register_upgrade("tactical_read",         effect="tactical_read_plus",         flavor="Gain 2 energy AND draw 1. Exhausts.")
    register_upgrade("iron_drill",            effect="iron_drill_plus",            flavor="Gain 15 block + 4 per Skill in hand (cap +16). Reps compound.")
    register_upgrade("last_stand",            effect="last_stand_plus",            flavor="Deal 19. If you're under half HP, draw 2. Exhausts.")
