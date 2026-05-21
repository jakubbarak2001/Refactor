################################################################################
## REFACTOR — Card Library
##
## Card definitions registered with register_card() at init time.
## Effect callables registered with @register_effect in card_effects.rpy.
##
## Every non-leave-alone card carries an `archetype` tag — one of
## basic / hatred / corruption / stoic / tech / neutral. The tag groups the
## pool into the 3 synergy archetypes for the battle-reward draft and tooling.
##
## The Bodybuilder pool is built around 3 synergistic archetypes:
##   HATRED — push Hatred for scaling damage, cash it out before 100.
##   STOIC  — turn a persistent block wall into offense.
##   TECH   — cycle fast, chain Skills, generate energy, thin the deck.
## Plus deliberate NEUTRAL flex cards and the 3 forced CORRUPTION rage cards.
##
## DE / BH class-locked, event, boss, story, status and Compromise cards are
## left defined and untagged (archetype defaults to None) — out of scope.
################################################################################

init python:

    ## ---------------------------------------------------------------------------
    ## BASIC & SIGNATURE — the starter kit. init_player_deck builds
    ## 4×strike + 4×defend + 1×heavy_set.
    ## ---------------------------------------------------------------------------

    register_card(
        "strike",
        name      = "Strike",
        type      = "Attack",
        color     = "Physical",
        cost      = 1,
        rarity    = "common",
        effect    = "strike",
        archetype = "basic",
        flavor    = "The simplest argument: hit harder.",
    )

    register_card(
        "defend",
        name      = "Defend",
        type      = "Skill",
        color     = "Mental",
        cost      = 1,
        rarity    = "common",
        effect    = "defend",
        archetype = "basic",
        flavor    = "Don't take the bait.",
    )

    register_card(
        "heavy_set",
        name       = "Heavy Set",
        type       = "Attack",
        color      = "Physical",
        cost       = 1,
        rarity     = "uncommon",
        effect     = "heavy_set",
        class_lock = "bodybuilder",
        archetype  = "basic",
        flavor     = "Every plate you've ever loaded. Stacked on the bar. Aimed at him.",
    )

    ## ---------------------------------------------------------------------------
    ## CLASS STARTERS — DE / BH signatures (out of scope, left untouched).
    ## ---------------------------------------------------------------------------

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
    ## ARCHETYPE: HATRED / RAGE — push Hatred up for scaling damage, knowing
    ## Hatred is a death clock (100 = breakdown). Generators feed it, scalers
    ## cash it out, See Red / Thick Skull make running hot survivable.
    ## ---------------------------------------------------------------------------

    register_card(
        "provoke",
        name      = "Provoke",
        type      = "Skill",
        color     = "Physical",
        cost      = 0,
        rarity    = "common",
        effect    = "provoke",
        archetype = "hatred",
        flavor    = "You say the thing. You watch it land. Now he has to answer.",
    )

    register_card(
        "knuckle_down",
        name      = "Knuckle Down",
        type      = "Attack",
        color     = "Physical",
        cost      = 2,
        rarity    = "uncommon",
        effect    = "knuckle_down",
        archetype = "hatred",
        flavor    = "No windup. No speech. Just the decision to plant your feet.",
    )

    register_card(
        "snap_decision",
        name      = "Snap Decision",
        type      = "Attack",
        color     = "Physical",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "snap_decision",
        archetype = "hatred",
        flavor    = "The thought and the fist arrive together.",
    )

    register_card(
        "red_mist",
        name      = "Red Mist",
        type      = "Attack",
        color     = "Physical",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "red_mist",
        archetype = "hatred",
        flavor    = "Two seconds you won't remember. He'll remember them.",
    )

    register_card(
        "breaking_point",
        name      = "Breaking Point",
        type      = "Attack",
        color     = "Physical",
        cost      = 2,
        rarity    = "rare",
        effect    = "breaking_point",
        archetype = "hatred",
        flavor    = "Thirty years of swallowed orders. The hinge finally gives.",
    )

    register_card(
        "bottled_rage",
        name      = "Bottled Rage",
        type      = "Attack",
        color     = "Physical",
        cost      = 1,
        rarity    = "rare",
        effect    = "bottled_rage",
        archetype = "hatred",
        flavor    = "Everything you didn't say at every briefing. Uncapped.",
    )

    register_card(
        "see_red",
        name      = "See Red",
        type      = "Power",
        color     = "Physical",
        cost      = 1,
        rarity    = "rare",
        effect    = "see_red",
        archetype = "hatred",
        flavor    = "Anger isn't the problem. Anger is the armor.",
    )

    register_card(
        "thick_skull",
        name      = "Thick Skull",
        type      = "Power",
        color     = "Physical",
        cost      = 1,
        rarity    = "rare",
        effect    = "thick_skull",
        archetype = "hatred",
        flavor    = "They called it a flaw at the academy. It's the only thing that held.",
    )

    register_card(
        "adrenaline_dump",
        name      = "Adrenaline Dump",
        type      = "Skill",
        color     = "Physical",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "adrenaline_dump",
        archetype = "hatred",
        flavor    = "The shake leaves your hands. The clock in your chest resets.",
    )

    register_card(
        "last_nerve",
        name      = "Last Nerve",
        type      = "Attack",
        color     = "Physical",
        cost      = 1,
        rarity    = "rare",
        effect    = "last_nerve",
        archetype = "hatred",
        flavor    = "He found it weeks ago. He's been standing on it since.",
    )

    register_card(
        "embrace_it",
        name      = "Embrace It",
        type      = "Skill",
        color     = "Physical",
        cost      = 1,
        rarity    = "rare",
        effect    = "embrace_it",
        archetype = "hatred",
        flavor    = "Stop fighting the worst of yourself. Aim it.",
    )

    ## ---------------------------------------------------------------------------
    ## ARCHETYPE: STOIC WALL — low Hatred, patient, turn defense into offense.
    ## ---------------------------------------------------------------------------

    register_card(
        "bracing",
        name      = "Bracing",
        type      = "Skill",
        color     = "Physical",
        cost      = 1,
        rarity    = "common",
        effect    = "bracing",
        archetype = "stoic",
        flavor    = "Square your stance. Lower your center.",
    )

    register_card(
        "backup",
        name      = "Backup",
        type      = "Skill",
        color     = "Police",
        cost      = 1,
        rarity    = "common",
        effect    = "backup",
        archetype = "stoic",
        flavor    = "Kovář has your six. Allegedly.",
    )

    register_card(
        "chain_of_command",
        name      = "Chain of Command",
        type      = "Skill",
        color     = "Police",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "chain_of_command",
        archetype = "stoic",
        flavor    = "Procedural calm. Someone, somewhere, signed off on this.",
    )

    register_card(
        "iron_posture",
        name      = "Iron Posture",
        type      = "Power",
        color     = "Physical",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "iron_posture",
        archetype = "stoic",
        flavor    = "You don't drop your guard between rounds. You never learned how.",
    )

    register_card(
        "counterweight",
        name      = "Counterweight",
        type      = "Attack",
        color     = "Physical",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "counterweight",
        archetype = "stoic",
        flavor    = "The wall isn't just for stopping. Lean into it.",
    )

    register_card(
        "hold_the_line",
        name      = "Hold the Line",
        type      = "Skill",
        color     = "Police",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "hold_the_line",
        archetype = "stoic",
        flavor    = "Doorframe at your back. Nobody steps past without paying.",
    )

    register_card(
        "brick_wall",
        name      = "Brick Wall",
        type      = "Attack",
        color     = "Physical",
        cost      = 2,
        rarity    = "rare",
        effect    = "brick_wall",
        archetype = "stoic",
        flavor    = "Hit him with the thing he couldn't get through.",
    )

    register_card(
        "iron_stance",
        name      = "Iron Stance",
        type      = "Power",
        color     = "Physical",
        cost      = 2,
        rarity    = "rare",
        effect    = "iron_stance",
        archetype = "stoic",
        flavor    = "Plant. Brace. Make every hit he throws cost him.",
    )

    register_card(
        "bouncer_door",
        name      = "Bouncer Door",
        type      = "Skill",
        color     = "Physical",
        cost      = 2,
        rarity    = "rare",
        effect    = "bouncer_door",
        archetype = "stoic",
        flavor    = "The door is you. Nothing comes through that you don't allow.",
    )

    register_card(
        "stoic_anchor",
        name      = "Stoic Anchor",
        type      = "Power",
        color     = "Mental",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "stoic_anchor",
        archetype = "stoic",
        flavor    = "You stop reacting. You just hold.",
    )

    register_card(
        "second_wind",
        name      = "Second Wind",
        type      = "Skill",
        color     = "Physical",
        cost      = 2,
        rarity    = "uncommon",
        effect    = "second_wind",
        archetype = "stoic",
        flavor    = "The lungs come back. The legs remember.",
    )

    ## ---------------------------------------------------------------------------
    ## ARCHETYPE: TECH TEMPO — the developer emerging. Cycle fast, chain Skills,
    ## generate energy, thin the deck. Low per-card numbers, high volume.
    ## ---------------------------------------------------------------------------

    register_card(
        "quick_compile",
        name      = "Quick Compile",
        type      = "Skill",
        color     = "Logic",
        cost      = 0,
        rarity    = "common",
        effect    = "quick_compile",
        archetype = "tech",
        flavor    = "The build is green.",
    )

    register_card(
        "pair_program",
        name      = "Pair Program",
        type      = "Skill",
        color     = "Logic",
        cost      = 0,
        rarity    = "uncommon",
        effect    = "pair_program",
        archetype = "tech",
        flavor    = "Two heads on one problem.",
    )

    register_card(
        "stack_trace",
        name      = "Stack Trace",
        type      = "Skill",
        color     = "Logic",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "stack_trace",
        archetype = "tech",
        flavor    = "Walk the call up. The next moves surface.",
    )

    register_card(
        "unit_test",
        name      = "Unit Test",
        type      = "Skill",
        color     = "Logic",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "unit_test",
        archetype = "tech",
        flavor    = "Coverage is armor.",
    )

    register_card(
        "production_push",
        name      = "Production Push",
        type      = "Attack",
        color     = "Logic",
        cost      = 1,
        rarity    = "rare",
        effect    = "production_push",
        archetype = "tech",
        flavor    = "Tests pass. Lint passes. Push to main without flinching.",
    )

    register_card(
        "refactor",
        name      = "Refactor",
        type      = "Skill",
        color     = "Logic",
        cost      = 2,
        rarity    = "uncommon",
        effect    = "refactor",
        exhaust   = True,
        archetype = "tech",
        flavor    = "Rename the variable. The bug evaporates.",
    )

    register_card(
        "kernel_patch",
        name      = "Kernel Patch",
        type      = "Skill",
        color     = "Logic",
        cost      = 2,
        rarity    = "rare",
        effect    = "kernel_patch",
        exhaust   = True,
        archetype = "tech",
        flavor    = "Live-patching mid-conversation.",
    )

    register_card(
        "hotfix",
        name      = "Hotfix",
        type      = "Attack",
        color     = "Logic",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "hotfix",
        archetype = "tech",
        flavor    = "One commit. Straight to main. The bug never sees it coming.",
    )

    register_card(
        "ship_it",
        name      = "Ship It",
        type      = "Skill",
        color     = "Logic",
        cost      = 1,
        rarity    = "rare",
        effect    = "ship_it",
        exhaust   = True,
        archetype = "tech",
        flavor    = "Good enough compiles. Good enough ships.",
    )

    register_card(
        "code_review",
        name      = "Code Review",
        type      = "Skill",
        color     = "Logic",
        cost      = 1,
        rarity    = "uncommon",
        effect    = "code_review",
        archetype = "tech",
        flavor    = "Delete the dead lines. The diff gets honest.",
    )

    register_card(
        "crunch_time",
        name      = "Crunch Time",
        type      = "Attack",
        color     = "Logic",
        cost      = 2,
        rarity    = "rare",
        effect    = "crunch_time",
        archetype = "tech",
        flavor    = "Every shortcut you took this turn, cashed at once.",
    )

    ## ---------------------------------------------------------------------------
    ## NEUTRAL — flexible cards every build is happy to pick.
    ## ---------------------------------------------------------------------------

    register_card(
        "gut_punch",
        name      = "Gut Punch",
        type      = "Attack",
        color     = "Physical",
        cost      = 1,
        rarity    = "common",
        effect    = "gut_punch",
        archetype = "neutral",
        flavor    = "Below the ribs. He folds.",
    )

    register_card(
        "body_check",
        name      = "Body Check",
        type      = "Attack",
        color     = "Physical",
        cost      = 2,
        rarity    = "uncommon",
        effect    = "body_check",
        archetype = "neutral",
        flavor    = "Drop your full weight through them.",
    )

    register_card(
        "breath_test",
        name      = "Breath Test",
        type      = "Skill",
        color     = "Police",
        cost      = 1,
        rarity    = "common",
        effect    = "breath_test",
        archetype = "neutral",
        flavor    = "'Blow into the tube.' The swing comes slower after.",
    )

    register_card(
        "killing_blow",
        name      = "Killing Blow",
        type      = "Attack",
        color     = "Physical",
        cost      = 2,
        rarity    = "rare",
        effect    = "killing_blow",
        archetype = "neutral",
        flavor    = "Finish what you started.",
    )

    register_card(
        "last_stand",
        name      = "Last Stand",
        type      = "Attack",
        color     = "Physical",
        cost      = 2,
        rarity    = "rare",
        effect    = "last_stand",
        exhaust   = True,
        archetype = "neutral",
        flavor    = "Back to the wall. Swing like it.",
    )

    register_card(
        "cuff_em",
        name      = "Cuff 'Em",
        type      = "Skill",
        color     = "Police",
        cost      = 2,
        rarity    = "uncommon",
        effect    = "cuff_em",
        exhaust   = True,
        archetype = "neutral",
        flavor    = "Steel on the wrist. He's done for the moment.",
    )

    ## ---------------------------------------------------------------------------
    ## EVENT / BOSS / ARC / STORY CARDS — out of scope, left untouched.
    ## ---------------------------------------------------------------------------

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
    ## STATUS / CURSE CARDS — enemy-injected, single-fight. pool_excluded.
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
    ## ARCHETYPE: CORRUPTION — Rage cards forced into the deck on crossing a
    ## Hatred threshold (40 / 60 / 80). Permanent, pool_excluded, non-upgradeable,
    ## Fixer-removable. Each play grants +2 Hatred — corruption snowballs. With
    ## Last Nerve and Embrace It these become usable in a Hatred build; elsewhere
    ## they stay liabilities. See _check_rage_injection in python_logic.rpy.
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
        archetype     = "corruption",
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
        archetype     = "corruption",
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
        archetype     = "corruption",
        flavor        = "Free swing. A card in your hand burns out for the rest of the fight.",
    )

    ## ---------------------------------------------------------------------------
    ## COMPROMISE — loss-injected dead-weight card. Permanent, UNPLAYABLE,
    ## pool_excluded. Removable via the Fixer. (forced_detour, 2nd+ ladder loss.)
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
    ## UPGRADE TABLE — `_plus` variants for every upgradeable base card.
    ## New-archetype cards get their `_plus` variants in a later pass; status /
    ## rage / compromise cards are intentionally non-upgradeable.
    ##
    ## Balance philosophy: commons get a tiny bump, uncommons ~25-30%, rares a
    ## conservative scalar, Powers a small bump (they compound across turns).
    ## ---------------------------------------------------------------------------

    ## Basic & signature
    register_upgrade("strike",                effect="strike_plus",                flavor="The simplest argument: hit harder. Then a little harder.")
    register_upgrade("defend",                effect="defend_plus",                flavor="Don't take the bait. Don't take the punch.")
    register_upgrade("heavy_set",             effect="heavy_set_plus",             flavor="Every plate you've ever loaded. Aimed at him. Plus one more.")

    ## Class starters (out of scope)
    register_upgrade("read_him",              effect="read_him_plus",              flavor="You hold for a half-second longer. He swings at empty air.")
    register_upgrade("stack_up",              effect="stack_up_plus",              flavor="+2 energy this turn. Draw a card while the room blurs.")

    ## Stoic
    register_upgrade("bracing",               effect="bracing_plus",               flavor="Square your stance. Lower your center. Set like stone.")
    register_upgrade("backup",                effect="backup_plus",                flavor="Kovář has your six. For real this time.")
    register_upgrade("chain_of_command",      effect="chain_of_command_plus",      flavor="Procedural calm. The chain is shorter than it was.")
    register_upgrade("iron_stance",           effect="iron_stance_plus",           flavor="Plant harder. Brace longer. Every hit he throws comes back.")
    register_upgrade("bouncer_door",          effect="bouncer_door_plus",          flavor="The door is you. Heavier. Hinged tighter.")
    register_upgrade("stoic_anchor",          effect="stoic_anchor_plus",          flavor="You stop reacting. You just hold, and hold harder.")
    register_upgrade("second_wind",           effect="second_wind_plus",           flavor="The lungs come back deeper. The legs come back first.")

    ## Tech
    register_upgrade("quick_compile",         effect="quick_compile_plus",         flavor="The build is green. Twice as green.")
    register_upgrade("pair_program",          effect="pair_program_plus",          flavor="Two heads on one problem. Both of them yours.")
    register_upgrade("stack_trace",           effect="stack_trace_plus",           flavor="Walk the call up. Three more moves surface.")
    register_upgrade("unit_test",             effect="unit_test_plus",             flavor="Coverage is armor. Full coverage is a wall.")
    register_upgrade("production_push",       effect="production_push_plus",       flavor="Tests pass. Lint passes. Push to main looking him in the eye.")
    register_upgrade("refactor",              effect="refactor",                   cost=1, flavor="Rename the variable. The bug evaporates. Cheaper now.")
    register_upgrade("kernel_patch",          effect="kernel_patch_plus",          flavor="Live-patch the conversation. Twice over.")

    ## Neutral
    register_upgrade("gut_punch",             effect="gut_punch_plus",             flavor="Below the ribs. He folds harder.")
    register_upgrade("body_check",            effect="body_check_plus",            flavor="Drop everything you've got through them.")
    register_upgrade("breath_test",           effect="breath_test_plus",           flavor="'Blow into the tube.' The swing barely lands at all.")
    register_upgrade("killing_blow",          effect="killing_blow_plus",          flavor="Finish what you started. Finish it twice.")
    register_upgrade("last_stand",            effect="last_stand_plus",            flavor="Back to the wall. Swing like the wall isn't there.")
    register_upgrade("cuff_em",               effect="cuff_em",                    cost=1, flavor="Steel on the wrist. Cheaper now. Exhausts.")

    ## Out-of-scope upgrades (event / boss / arc / story)
    register_upgrade("racetam",               effect="racetam_plus",               flavor="+1 energy. Draw 2.")
    register_upgrade("flmodafinil",           effect="flmodafinil_plus",           flavor="Deal 32. 50%%: lose self for 1 turn. Exhausts.")
    register_upgrade("mirror",                effect="mirror_plus",                flavor="Return the enemy's next attack at 2x. +5 block on play. 2-turn cooldown.")
    register_upgrade("paragraph_4b",          effect="paragraph_4b_plus",          flavor="Deal 48. The 80k debt is dust.")
    register_upgrade("ghost_secret",          effect="ghost_secret_plus",          flavor="Cancel one incoming attack. Deal 20. Leverage compounds.")
    register_upgrade("job_offer",             effect="job_offer_plus",             flavor="+8 max HP at start. +1 starting block per turn.")
    register_upgrade("stoic_refactor",        effect="stoic_refactor_plus",        flavor="Power: take 50%% damage from Mental-typed attacks.")
    register_upgrade("empaths_insight",       effect="empaths_insight_plus",       flavor="Their first move tells you their last four. Block stacks.")
    register_upgrade("tell",                  effect="tell_plus",                  flavor="You see his shoulders set, his eyes flick. Free 11 block.")
    register_upgrade("frame_trap",            effect="frame_trap_plus",            flavor="Reduce the enemy's next attack by 11 (minimum 1).")
    register_upgrade("charm",                 effect="charm_plus",                 flavor="Heal 10 HP and gain 5 block. You own the room now.")
    register_upgrade("hrv_spike",             effect="hrv_spike_plus",             flavor="Gain 2 energy. Lose 3 HP. Smaller crash, same lift.")
    register_upgrade("cognitive_stack",       effect="cognitive_stack_plus",       flavor="Draw 4 cards. Exhausts. The compound is dialed in.")
    register_upgrade("override",              effect="override_plus",              flavor="Deal 44 damage. -2 max energy next turn. Exhausts.")
    register_upgrade("the_dossier",           effect="the_dossier_plus",           flavor="Cancel one incoming attack. Deal 30. They know what you have.")
    register_upgrade("the_compound",          effect="the_compound_plus",          flavor="Deal damage equal to current energy ×12. Lose 12 HP. Trial doubled.")
    register_upgrade("took_the_heat",         effect="took_the_heat_plus",         flavor="Gain 13 block. Draw 1. You owned it, twice.")

    ## New-archetype cards — Hatred. The three Powers upgrade by going free
    ## (cost 0, same effect) — the refactor / cuff_em cost-reduction pattern.
    register_upgrade("provoke",               effect="provoke_plus",               flavor="You say the thing. You watch it land twice.")
    register_upgrade("knuckle_down",          effect="knuckle_down_plus",          flavor="No windup, no speech — and your feet were already set.")
    register_upgrade("snap_decision",         effect="snap_decision_plus",         flavor="The thought and the fist arrive together, harder.")
    register_upgrade("red_mist",              effect="red_mist_plus",              flavor="Three seconds you won't remember. He won't forget them.")
    register_upgrade("breaking_point",        effect="breaking_point_plus",        flavor="The hinge gave a long time ago. Now it's just leverage.")
    register_upgrade("bottled_rage",          effect="bottled_rage_plus",          flavor="Uncapped — and you've learned to pour, not spill.")
    register_upgrade("see_red",               effect="see_red",               cost=0, flavor="Anger isn't the problem. Anger is free.")
    register_upgrade("thick_skull",           effect="thick_skull",           cost=0, flavor="The only thing that ever held. Costs you nothing.")
    register_upgrade("adrenaline_dump",       effect="adrenaline_dump_plus",       flavor="The shake leaves your hands. A card finds them.")
    register_upgrade("last_nerve",            effect="last_nerve_plus",            flavor="He's still standing on it. You stopped flinching.")
    register_upgrade("embrace_it",            effect="embrace_it_plus",            flavor="Stop fighting the worst of yourself. Aim it better.")

    ## New-archetype cards — Stoic
    register_upgrade("iron_posture",          effect="iron_posture",          cost=0, flavor="You never learned to drop your guard. Now it's reflex.")
    register_upgrade("counterweight",         effect="counterweight_plus",         flavor="Lean into the wall. Add your shoulder.")
    register_upgrade("hold_the_line",         effect="hold_the_line_plus",         flavor="Doorframe at your back. Nobody gets past, ever.")
    register_upgrade("brick_wall",            effect="brick_wall_plus",            flavor="Hit him with the thing he could never get through.")

    ## New-archetype cards — Tech
    register_upgrade("hotfix",                effect="hotfix_plus",                flavor="One commit. Straight to main. He never sees the diff.")
    register_upgrade("ship_it",               effect="ship_it_plus",               flavor="Good enough ships. And reads itself back to you.")
    register_upgrade("code_review",           effect="code_review_plus",           flavor="Delete the dead lines. The diff gets honest, and lean.")
    register_upgrade("crunch_time",           effect="crunch_time_plus",           flavor="Every shortcut, every corner — all of it, due now.")
