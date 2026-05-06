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
        flavor     = "Damage scales with your hatred.",
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
        flavor     = "Peek next 3 intents and draw 1. Knowing what's coming buys time.",
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
        flavor  = "Convert the colonel's next attack into block for you.",
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
        flavor  = "Cancel the colonel's next attack.",
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
        type    = "Power",
        color   = "Police",
        cost    = 2,
        rarity  = "uncommon",
        effect  = "procedural_defense",
        flavor  = "Block all damage from one full colonel turn.",
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
        flavor     = "Return the colonel's next attack at double damage. (2-turn cooldown.)",
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
        flavor  = "Skip the colonel's next 2 attacks.",
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
        flavor  = "Reveal his deck. Three turns of foreknowledge.",
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
        flavor  = "Instant-disable one colonel attack. He buried his own resignation 10 years ago.",
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
        flavor  = "Take 50% damage from emotional (Mental-typed) colonel attacks.",
    )

    register_card(
        "stoic_anchor",
        name    = "Stoic Anchor",
        type    = "Power",
        color   = "Mental",
        cost    = 1,
        rarity  = "uncommon",
        effect  = "stoic_anchor",
        flavor  = "Start each turn with +3 block. Heal 3 HP after every colonel attack.",
    )

    ## ---------------------------------------------------------------------------
    ## ADDITIONAL CARDS — broader pool granted via random events / opportunities
    ## ---------------------------------------------------------------------------

    register_card(
        "quick_jab",
        name   = "Quick Jab",
        type   = "Attack",
        color  = "Physical",
        cost   = 0,
        rarity = "common",
        effect = "quick_jab",
        flavor = "Deal 4 and draw 1. Free pressure.",
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

    register_card(
        "empaths_insight",
        name       = "Empath's Insight",
        type       = "Power",
        color      = "Mental",
        cost       = 1,
        rarity     = "rare",
        effect     = "empaths_insight",
        class_lock = "dark_empath",
        flavor     = "Peek 5 intents at battle start. +1 starting block per turn for 3 turns.",
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
        flavor     = "Gain 6 block. Retaliate 4 dmg the next time the colonel hits you.",
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
        flavor     = "Peek 1 intent. Gain 3 block. Free.",
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
        flavor     = "Reduce the colonel's next attack by 8 (minimum 1). Set the trap before he speaks.",
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
        "vladeks_form",
        name       = "Vladek's Form",
        type       = "Power",
        color      = "Physical",
        cost       = 2,
        rarity     = "boss",
        effect     = "vladeks_form",
        class_lock = "bodybuilder",
        flavor     = "Power: +2 SOMA-equivalent block per turn. Retaliate scales doubled. The competition is over.",
    )

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
        flavor     = "Disable one colonel attack tagged 'emotional' or 'guilt'. Deal 25 damage. He knows you have it.",
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
