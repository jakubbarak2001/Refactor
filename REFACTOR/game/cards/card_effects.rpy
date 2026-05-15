################################################################################
## REFACTOR — Card Effects (Phase 1.2 stubs / Phase 1.6 implementation)
##
## Each effect_id maps to a callable: (state, source, target) -> None.
## state is a BattleState instance (defined in battle_engine.rpy, Phase 1.6).
##
## BattleState API contract (will be implemented in Phase 1.6):
##   state.deal_damage(target, amount)        — apply damage, considers block
##   state.gain_block(target, amount)         — add block to target
##   state.heal(target, amount)               — restore HP
##   state.draw_cards(n)                      — draw n cards into hand
##   state.gain_energy(n)                     — increase current-turn energy
##   state.cancel_next_attack_set()           — null out next colonel attack
##   state.skip_attacks(n)                    — skip next n colonel intents
##   state.buff(target, key, value)           — apply named modifier
##   state.add_log(msg)                       — append to battle log
##
## state attributes:
##   player_hp / player_max_hp / player_block
##   enemy_hp / enemy_max_hp / enemy_block
##   energy / max_energy
##   hand / draw_pile / discard_pile / exhaust_pile
##   intent_queue                             — list of upcoming colonel cards
##   buffs / debuffs                          — per-side dicts
##
## In Phase 1.2 these are stubs that route to state.add_log so cards can be
## tested in dry-run mode. Phase 1.6 implements full mechanics.
################################################################################

init python:

    ## ---------------------------------------------------------------------------
    ## EFFECT_DESCRIPTIONS — human-readable card-effect text for hand tooltips.
    ## Keyed by effect_id (matches CARD_LIBRARY's "effect" field).
    ## Used by battle_screen to render a tooltip on hand-card hover.
    ## ---------------------------------------------------------------------------

    EFFECT_DESCRIPTIONS = {
        "deal_damage_6":           "Deal 6 damage.",
        "gain_block_5":            "Gain 5 block.",
        "heavy_set":               "Deal 4 + (Hatred / 10) damage. Scales with how much you hate this job.",
        "read_him":                "Gain 6 block. Draw 2 cards.",
        "stack_up":                "Gain +2 energy this turn. Crash next turn (-2 energy).",
        "gain_block_12":           "Gain 9 block.",
        "deal_damage_double_next": "Your next attack this turn fires twice.",
        "boundary":                "Deal 4 damage. Heal 4 HP.",
        "reframe":                 "Convert the enemy's next attack into block for you. Exhausts.",
        "side_income":             "Deal damage equal to (Money / 10,000), rounded down.",
        "vip_treatment":           "Deal 30 damage. Lose 10 HP. Exhausts.",
        "refactor":                "Cancel the enemy's next attack. Exhausts.",
        "compile":                 "Draw 2 cards.",
        "production_push":         "Deal 10 damage. Draw 1 card. +6 damage if your hand contains a Skill.",
        "gain_block_15":           "Gain 10 block.",
        "procedural_defense":      "Block all damage from the enemy's next attack turn.",
        "racetam_burst":           "Gain +1 energy. Draw 1 card.",
        "flmodafinil_spike":       "Deal 28 damage. 50%: -1 max energy next turn. Exhausts.",
        "mirror":                  "The enemy's next attack hits THEM at 2x damage. 2-turn cooldown.",
        "algorithm":               "Skip the enemy's next 2 attacks. Exhausts.",
        "snitch_info":             "Deal 18 damage. Exhausts.",
        "paragraph_4b":            "Deal 40 damage. Voids 'Training Debt' for the fight. Exhausts.",
        "ghost_secret":            "Cancel the enemy's next attack. Deal 15 damage. Exhausts.",
        "job_offer":               "Power: +5 max HP. +1 starting block per turn.",
        "stoic_refactor":          "Power: take 50% damage from Mental-typed attacks.",
        "stoic_anchor":            "Power: +2 starting block per turn. Heal 2 HP after each enemy attack.",
        "quick_jab":               "Deal 7 damage.",
        "loan_sharks":             "Pay 5,000 CZK to deal 30 damage. (No funds = no damage.) Exhausts.",
        "paid_review":             "Pay 10,000 CZK to cancel the enemy's next attack and draw 2. (No funds = no effect.) Exhausts.",
        "chain_of_command":        "Gain 10 block. Draw 1 card.",
        "vigil":                   "Gain 4 block now. +4 starting block next turn.",
        "iron_stance":             "Power: +20 block. Retaliate 4 damage on turn 1, +2 per turn after, capped at 12.",
        "spotter":                 "Gain 6 block. Draw 1 card.",
        "brawl":                   "Deal 10 damage. Apply 3-turn bleed (3 dmg/turn) to the enemy.",
        "empaths_insight":         "Power: +5 starting block per turn for the first 3 turns.",
        "iron_body":               "Gain 6 block. Retaliate 4 damage on the next hit.",
        "pump":                    "Gain +2 energy this turn. +5 Hatred.",
        "strongman":               "Gain 25 block. Draw 2. Exhausts.",
        "tell":                    "Gain 8 block. Free.",
        "frame_trap":              "Reduce the enemy's next attack by 8 (min 1).",
        "charm":                   "Heal 8 HP. Gain 3 block.",
        "hrv_spike":               "Gain +2 energy. Lose 5 HP.",
        "cognitive_stack":         "Draw 3 cards. Exhausts.",
        "override":                "Deal 40 damage. -2 max energy next turn. Exhausts.",
        "the_dossier":             "Deal 25 damage. Cancel the next attack if it's tagged emotional or guilt. Exhausts.",
        "the_compound":            "Deal (current energy × 10) damage. Lose 8 HP. Exhausts.",
        ## Battle ladder basic pool — Body / Tech / Authority
        "gut_punch":               "Deal 8 damage.",
        "bracing":                 "Gain 8 block.",
        "second_wind":             "Heal 6 HP. Gain 8 block.",
        "body_check":              "Deal 14 damage.",
        "payday":                  "Deal damage equal to (Money / 5,000), capped at 20.",
        "bouncer_door":            "Gain 18 block. Retaliate 8 damage on the next hit.",
        "quick_compile":           "Draw 1 card. Free.",
        "lint_pass":               "Exhaust a random card from hand. Draw 1.",
        "stack_trace":             "Draw 2 cards.",
        "unit_test":               "Gain 6 block for every Skill in your hand.",
        "merge_conflict":          "Deal 10 damage. Draw 1.",
        "kernel_patch":            "Gain 1 energy. Draw 2. Exhausts.",
        "pair_program":            "Gain 3 block. Draw 1 card. Free.",
        "radio_call":              "Gain 7 block.",
        "breath_test":             "Reduce his next attack by 5 (min 1).",
        "procedural_kick":         "Deal 5 damage. Gain 5 block.",
        "riot_shield":             "Gain 14 block. +4 starting block next turn.",
        "cuff_em":                 "Skip his next attack. Exhausts.",
        "internal_review":         "Cancel his next attack. Deal 8 damage. Exhausts.",
        ## Status / curse cards (injected by enemy wrinkles; auto-exhaust on play)
        "status_paperwork":        "Status. Fills the form. Exhausts.",
        "status_counterfeit":      "Status. Deal 4. Take 8. Exhausts.",
        "status_fumes":            "Status. Take 2. Exhausts.",
        "status_tear_gas":         "Status. Take 3. Exhausts.",
        ## Rage cards (injected at hatred 40/60/80; permanent — not exhaust).
        ## Each Rage play also adds +2 Hatred — corruption snowballs into the
        ## next threshold faster.
        "outburst":                "Deal 12.\nLose 9 HP.\n+2 Hatred.",
        "tunnel_vision":           "Deal 14.\nDiscard 1 random card from hand or draw pile.\n+2 Hatred.",
        "snap":                    "Deal 8.\nExhaust 1 random card from your hand (this fight only).\n+2 Hatred.",
        ## Compromise card (injected by forced_detour on 2nd+ loss; unplayable)
        "compromise":              "Unplayable.\nDead weight in hand.",
        ## Combat-reward rares (ladder-fight drops)
        "killing_blow":            "Deal 14. If enemy is below half HP: deal 14 more.",
        "tactical_read":           "Gain 2 energy this turn. Exhausts.",
        "iron_drill":              "Gain 12 block + 4 per Skill in hand (capped at +12).",
        "last_stand":              "Deal 16. If you're below half HP, draw 2. Exhausts.",
        ## ─── Upgraded variants (`_plus`) — paired with register_upgrade table ───
        "strike_plus":              "Deal 9 damage.",
        "defend_plus":              "Gain 8 block.",
        "heavy_set_plus":           "Deal 6 + (Hatred / 10) damage. Scales with how much you hate this job.",
        "read_him_plus":            "Gain 9 block. Draw 2 cards.",
        "stack_up_plus":            "Gain +2 energy this turn. Draw 1. Crash next turn (-2 energy).",
        "iron_will_plus":           "Gain 13 block.",
        "personal_record_plus":     "Your next attack this turn fires twice.",
        "boundary_plus":            "Deal 6 damage. Heal 6 HP.",
        "side_income_plus":         "Deal damage equal to (Money / 8,000), rounded down.",
        "vip_treatment_plus":       "Deal 34 damage. Lose 10 HP. Exhausts.",
        "compile_plus":             "Draw 3 cards.",
        "production_push_plus":     "Deal 12 damage. Draw 1 card. +8 damage if your hand contains a Skill.",
        "backup_plus":              "Gain 14 block.",
        "racetam_plus":             "Gain +1 energy. Draw 2 cards.",
        "flmodafinil_plus":         "Deal 32 damage. 50%: -1 max energy next turn. Exhausts.",
        "mirror_plus":              "The enemy's next attack hits THEM at 2x damage. Gain 5 block. 2-turn cooldown.",
        "algorithm_plus":           "Skip the enemy's next 3 attacks. Exhausts.",
        "snitch_info_plus":         "Deal 22 damage. Exhausts.",
        "paragraph_4b_plus":        "Deal 48 damage. Voids 'Training Debt' for the fight. Exhausts.",
        "ghost_secret_plus":        "Cancel the enemy's next attack. Deal 20 damage. Exhausts.",
        "job_offer_plus":           "Power: +8 max HP. +1 starting block per turn.",
        "stoic_refactor_plus":      "Power: take 50% damage from Mental-typed attacks.",
        "stoic_anchor_plus":        "Power: +3 starting block per turn. Heal 2 HP after each enemy attack.",
        "quick_jab_plus":           "Deal 10 damage.",
        "loan_sharks_plus":         "Pay 5,000 CZK to deal 36 damage. (No funds = no damage.) Exhausts.",
        "paid_review_plus":         "Pay 8,000 CZK to cancel the enemy's next attack and draw 2. (No funds = no effect.) Exhausts.",
        "chain_of_command_plus":    "Gain 13 block. Draw 1 card.",
        "vigil_plus":               "Gain 6 block now. +6 starting block next turn.",
        "iron_stance_plus":         "Power: +24 block. Retaliate scales with turn — early small, late lethal.",
        "spotter_plus":             "Gain 9 block. Draw 1 card.",
        "brawl_plus":               "Deal 12 damage. Apply 3-turn bleed (4 dmg/turn) to the enemy.",
        "empaths_insight_plus":     "Power: +6 starting block per turn for the first 4 turns.",
        "iron_body_plus":           "Gain 8 block. Retaliate 6 damage on the next hit.",
        "pump_plus":                "Gain +2 energy this turn. +3 Hatred.",
        "strongman_plus":           "Gain 28 block. Draw 2. Exhausts.",
        "tell_plus":                "Gain 11 block. Free.",
        "frame_trap_plus":          "Reduce the enemy's next attack by 11 (min 1).",
        "charm_plus":               "Heal 10 HP. Gain 5 block.",
        "hrv_spike_plus":           "Gain +2 energy. Lose 3 HP.",
        "cognitive_stack_plus":     "Draw 4 cards. Exhausts.",
        "override_plus":            "Deal 44 damage. -2 max energy next turn. Exhausts.",
        "the_dossier_plus":         "Deal 30 damage. Cancel the next attack if it's tagged emotional or guilt. Exhausts.",
        "the_compound_plus":        "Deal (current energy × 12) damage. Lose 12 HP. Exhausts.",
        "took_the_heat_plus":       "Gain 13 block. Draw 1.",
        "gut_punch_plus":           "Deal 11 damage.",
        "bracing_plus":             "Gain 11 block.",
        "second_wind_plus":         "Heal 8 HP. Gain 10 block.",
        "body_check_plus":          "Deal 17 damage.",
        "payday_plus":              "Deal damage equal to (Money / 4,000), capped at 20.",
        "bouncer_door_plus":        "Gain 22 block. Retaliate 10 damage on the next hit.",
        "quick_compile_plus":       "Draw 2 cards. Free.",
        "lint_pass_plus":           "Exhaust a random card from hand. Draw 2.",
        "stack_trace_plus":         "Draw 3 cards.",
        "unit_test_plus":           "Gain 8 block for every Skill in your hand.",
        "merge_conflict_plus":      "Deal 13 damage. Draw 1.",
        "kernel_patch_plus":        "Gain 1 energy. Draw 3. Exhausts.",
        "pair_program_plus":        "Gain 5 block. Draw 1 card. Free.",
        "radio_call_plus":          "Gain 10 block.",
        "breath_test_plus":         "Reduce his next attack by 8 (min 1).",
        "procedural_kick_plus":     "Deal 7 damage. Gain 7 block.",
        "riot_shield_plus":         "Gain 17 block. +6 starting block next turn.",
        "internal_review_plus":     "Cancel his next attack. Deal 12 damage. Exhausts.",
        "killing_blow_plus":        "Deal 16. If enemy is below half HP: deal 16 more.",
        "tactical_read_plus":       "Gain 2 energy this turn. Draw 1. Exhausts.",
        "iron_drill_plus":          "Gain 15 block + 4 per Skill in hand (capped at +16).",
        "last_stand_plus":          "Deal 19. If you're below half HP, draw 2. Exhausts.",
    }

    ## ---------------------------------------------------------------------------
    ## Dynamic description resolution.
    ## Most cards have a static description above. Stat-scaling cards (Heavy Set
    ## scales off Hatred, side_income/payday scale off Money) read better when
    ## the player sees the *current* damage spelled out, not the formula. This
    ## helper returns the dynamic line for those and falls back to the static
    ## dict for everything else. Call this from every UI site that previously
    ## did EFFECT_DESCRIPTIONS.get(effect_id, "").
    ## ---------------------------------------------------------------------------

    def effect_description(effect_id):
        if not effect_id:
            return ""
        h = stats.pcr_hatred if stats else 0
        if effect_id == "heavy_set":
            dmg = 4 + (h // 10)
            return "Deal {} damage.\nScales with Hatred.".format(dmg)
        if effect_id == "heavy_set_plus":
            dmg = 6 + (h // 10)
            return "Deal {} damage.\nScales with Hatred.".format(dmg)
        return EFFECT_DESCRIPTIONS.get(effect_id, "")

    ## ---------------------------------------------------------------------------
    ## Universal starters
    ## ---------------------------------------------------------------------------

    @register_effect("deal_damage_6")
    def _eff_strike(state, source, target):
        state.deal_damage(target, 6)

    @register_effect("gain_block_5")
    def _eff_defend(state, source, target):
        state.gain_block(source, 5)

    ## ---------------------------------------------------------------------------
    ## Class starters
    ## ---------------------------------------------------------------------------

    @register_effect("production_push")
    def _eff_production_push(state, source, target):
        ## Bootcamp graduation reward — versatile rare attack.
        ## 10 base + Skill-in-hand scaling (was 14 base — audit nerf:
        ## 14 base for 1e exceeded rare-tier DPE before the bonus).
        dmg = 10
        ## Bonus: if any Skill is in hand, add +6 (rewards mixed hands, the
        ## "I shipped a feature" feeling — block + attack thinking together).
        try:
            for cid in state.hand:
                c = CARD_LIBRARY.get(cid, {})
                if c.get("type") == "Skill":
                    dmg += 6
                    break
        except Exception:
            pass
        state.deal_damage(target, dmg)
        state.draw_cards(1)
        state.add_log("Production Push: {} damage + draw.".format(dmg))

    @register_effect("heavy_set")
    def _eff_heavy_set(state, source, target):
        ## BB signature — damage scales with player's pcr_hatred
        dmg = 4 + (stats.pcr_hatred // 10) if stats else 4
        state.deal_damage(target, dmg)
        state.add_log("Heavy Set: {} damage (scaled by hatred).".format(dmg))

    @register_effect("read_him")
    def _eff_read_him(state, source, target):
        ## DE signature — info became defense+tempo. Peek mechanic removed
        ## per feedback_no_peek_intent: it doesn't fit the sim feel.
        state.gain_block(source, 6)
        state.draw_cards(2)

    @register_effect("stack_up")
    def _eff_stack_up(state, source, target):
        ## BH signature — +2 energy now, debuff "crash" next turn
        state.gain_energy(2)
        state.buff(source, "crash_next_turn", True)

    ## ---------------------------------------------------------------------------
    ## Gym
    ## ---------------------------------------------------------------------------

    @register_effect("gain_block_12")
    def _eff_iron_will(state, source, target):
        state.gain_block(source, 9)

    @register_effect("deal_damage_double_next")
    def _eff_personal_record(state, source, target):
        state.buff(source, "double_next_attack", True)

    ## ---------------------------------------------------------------------------
    ## Therapy
    ## ---------------------------------------------------------------------------

    @register_effect("boundary")
    def _eff_boundary(state, source, target):
        state.deal_damage(target, 4)
        state.heal(source, 4)

    @register_effect("reframe")
    def _eff_reframe(state, source, target):
        state.buff(source, "reframe_next", True)

    ## ---------------------------------------------------------------------------
    ## Bouncer
    ## ---------------------------------------------------------------------------

    @register_effect("side_income")
    def _eff_side_income(state, source, target):
        dmg = (stats.available_money // 10000) if stats else 0
        state.deal_damage(target, dmg)
        state.add_log("Side Income: {} damage (savings / 10k).".format(dmg))

    @register_effect("vip_treatment")
    def _eff_vip_treatment(state, source, target):
        ## Self-harm leg bypasses block (you slammed your own knee into the
        ## bouncer rail; block stops the drunk, not the rail).
        state.deal_damage(target, 30)
        state.deal_damage(source, 10, bypass_block=True)

    ## ---------------------------------------------------------------------------
    ## Coding
    ## ---------------------------------------------------------------------------

    @register_effect("refactor")
    def _eff_refactor(state, source, target):
        state.cancel_next_attack_set()

    @register_effect("compile")
    def _eff_compile(state, source, target):
        state.draw_cards(2)

    ## ---------------------------------------------------------------------------
    ## Night Shift
    ## ---------------------------------------------------------------------------

    @register_effect("gain_block_15")
    def _eff_backup(state, source, target):
        state.gain_block(source, 10)

    @register_effect("procedural_defense")
    def _eff_procedural_defense(state, source, target):
        state.buff(source, "block_next_turn", True)

    ## ---------------------------------------------------------------------------
    ## Nootropics (BH)
    ## ---------------------------------------------------------------------------

    @register_effect("racetam_burst")
    def _eff_racetam(state, source, target):
        state.gain_energy(1)
        state.draw_cards(1)

    @register_effect("flmodafinil_spike")
    def _eff_flmod(state, source, target):
        state.deal_damage(target, 28)
        if __import__('random').random() < 0.5:
            state.buff(source, "max_energy_penalty_next_turn", 1)
            state.add_log("FLModafinil: peak ebbs — -1 max energy next turn.")

    ## ---------------------------------------------------------------------------
    ## Cold Read (DE)
    ## ---------------------------------------------------------------------------

    @register_effect("mirror")
    def _eff_mirror(state, source, target):
        ## Mirror is no longer one-shot — it has a 2-turn cooldown after each use.
        ## Battle engine consumes mirror_next when the next attack arrives, then
        ## sets mirror_cooldown=2 so the card is unplayable for 2 player turns.
        if state.buffs.get("mirror_cooldown", 0) > 0:
            state.add_log("Mirror is on cooldown ({} turns).".format(state.buffs["mirror_cooldown"]))
            return
        state.buff(source, "mirror_next", True)
        ## Fight-long flag for civilian_void's special counter. Separate from
        ## mirror_next (which gets consumed by the reflect itself) so the
        ## counter survives across multiple mirror plays / cooldowns.
        state.buff(source, "mirror_armed_for_counter", True)

    ## ---------------------------------------------------------------------------
    ## Event drops
    ## ---------------------------------------------------------------------------

    @register_effect("algorithm")
    def _eff_algorithm(state, source, target):
        state.skip_attacks(2)

    @register_effect("snitch_info")
    def _eff_snitch(state, source, target):
        ## Was a full-deck peek; peek mechanic removed. Reframed as "you used
        ## the intel" — one-shot heavy hit, exhausts.
        state.deal_damage(target, 18)

    @register_effect("paragraph_4b")
    def _eff_paragraph_4b(state, source, target):
        state.deal_damage(target, 40)
        ## Arm the fight-long flag that training_debt's counter checks.
        ## Buff-based (not last_card_played) so the counter still fires if
        ## the player plays any card after this one in the same turn, and
        ## still fires on the upgraded variant.
        state.buff(source, "paragraph_4b_armed", True)

    @register_effect("ghost_secret")
    def _eff_ghost_secret(state, source, target):
        state.cancel_next_attack_set()
        state.deal_damage(target, 15)

    @register_effect("job_offer")
    def _eff_job_offer(state, source, target):
        state.player_max_hp += 5
        state.player_hp += 5
        state.buff(source, "starting_block_+1", True)
        ## Fight-long flag for blacklist's counter. Powers auto-fire at
        ## battle_init (which doesn't set last_card_played), so the buff is
        ## the only reliable way to detect "this Power is in play".
        state.buff(source, "job_offer_armed", True)

    @register_effect("stoic_refactor")
    def _eff_stoic_refactor(state, source, target):
        state.buff(source, "mental_dr_50", True)

    @register_effect("stoic_anchor")
    def _eff_stoic_anchor(state, source, target):
        ## Power: persistent buff. Engine applies starting_block_+2 and
        ## heal_after_attack at runtime. Audit nerf: was +3/heal 3 — a power
        ## that paid back its cost in one turn AND kept compounding. Down to
        ## +2/heal 2: still a strong rare-tier engine, no longer free value.
        state.buff(source, "stoic_anchor_block", 2)
        state.buff(source, "stoic_anchor_heal", 2)

    ## ---------------------------------------------------------------------------
    ## Additional cards
    ## ---------------------------------------------------------------------------

    @register_effect("quick_jab")
    def _eff_quick_jab(state, source, target):
        state.deal_damage(target, 7)

    @register_effect("loan_sharks")
    def _eff_loan_sharks(state, source, target):
        if stats and stats.try_spend_money(5000):
            state.deal_damage(target, 30)
            state.add_log("Loan Sharks: 5000 CZK spent. 30 damage.")
        else:
            state.add_log("Loan Sharks: card fizzles — no 5,000 CZK on hand.")

    @register_effect("paid_review")
    def _eff_paid_review(state, source, target):
        ## BB's escape valve for the coding ceiling — cash buys the senior's
        ## hour. 10K CZK → cancel next attack + draw 2. No funds → fizzles
        ## (still exhausts; you texted, you got nothing back).
        if stats and stats.try_spend_money(10000):
            state.cancel_next_attack_set()
            state.draw_cards(2)
            state.add_log("Paid Review: 10000 CZK spent. Attack cancelled. +2 cards.")
        else:
            state.add_log("Paid Review: phone goes to voicemail. No funds.")

    @register_effect("chain_of_command")
    def _eff_chain_of_command(state, source, target):
        state.gain_block(source, 10)
        state.draw_cards(1)

    @register_effect("vigil")
    def _eff_vigil(state, source, target):
        state.gain_block(source, 4)
        state.buff(source, "vigil_next_turn_block", 4)

    ## ---------------------------------------------------------------------------
    ## Class-balance v2 additions
    ## ---------------------------------------------------------------------------

    @register_effect("spotter")
    def _eff_spotter(state, source, target):
        state.gain_block(source, 6)
        state.draw_cards(1)

    @register_effect("brawl")
    def _eff_brawl(state, source, target):
        state.deal_damage(target, 10)
        ## Bleed: 3 damage at start of each enemy turn for 3 turns.
        state.buff(source, "bleed_dmg", 3)
        state.buff(source, "bleed_turns", 3)

    @register_effect("empaths_insight")
    def _eff_empaths_insight(state, source, target):
        ## DE rare power: bumped block-per-turn buff to fully replace the
        ## peek leg of the original effect (peek mechanic removed). +5
        ## starting block per turn for 3 turns instead of +1.
        state.buff(source, "insight_block", 5)
        state.buff(source, "insight_turns_left", 3)

    ## ---------------------------------------------------------------------------
    ## GOTY v2 — class identity card effects
    ## ---------------------------------------------------------------------------

    @register_effect("iron_body")
    def _eff_iron_body(state, source, target):
        state.gain_block(source, 6)
        ## "Retaliate next hit": single-shot retaliate flag separate from iron_stance
        state.buff(source, "single_retaliate_dmg", 4)

    @register_effect("pump")
    def _eff_pump(state, source, target):
        state.gain_energy(2)
        if stats:
            stats.increment_stats_pcr_hatred(5)
        state.add_log("Pump: +2 energy this turn. The room shrinks.")

    @register_effect("strongman")
    def _eff_strongman(state, source, target):
        state.gain_block(source, 25)
        state.draw_cards(2)

    @register_effect("tell")
    def _eff_tell(state, source, target):
        ## 0-cost block — peek mechanic removed; block bumped 3 → 8 to
        ## restore the card's defensive value.
        state.gain_block(source, 8)

    @register_effect("frame_trap")
    def _eff_frame_trap(state, source, target):
        state.buff(source, "next_attack_reduction", 8)

    @register_effect("charm")
    def _eff_charm(state, source, target):
        state.heal(source, 8)
        state.gain_block(source, 3)

    @register_effect("hrv_spike")
    def _eff_hrv_spike(state, source, target):
        ## Syringe doesn't care about your shield. Bypass block.
        state.gain_energy(2)
        state.deal_damage(source, 5, bypass_block=True)
        state.add_log("HRV Spike: +2 energy, -5 HP. Recorded.")

    @register_effect("cognitive_stack")
    def _eff_cognitive_stack(state, source, target):
        state.draw_cards(3)

    @register_effect("override")
    def _eff_override(state, source, target):
        state.deal_damage(target, 40)
        state.buff(source, "max_energy_penalty_next_turn", 2)

    ## ---------------------------------------------------------------------------
    ## Arc-reward effects
    ## ---------------------------------------------------------------------------

    @register_effect("the_dossier")
    def _eff_the_dossier(state, source, target):
        ## Cancel next attack if it's emotional/guilt-tagged. Deal 25 damage either way.
        ic = state.current_intent()
        if ic and any(t in ic.get("tags", []) for t in ("emotional", "guilt")):
            state.cancel_next_attack_set()
            state.add_log("[[The Dossier]: 'emotional' attack disabled by leverage.")
        state.deal_damage(target, 25)

    @register_effect("the_compound")
    def _eff_the_compound(state, source, target):
        ## Read pre-spend energy by adding back the cost (1E for the_compound).
        ## At 1E in hand, energy at this point is 0 → +1 = 1 → 10 dmg (correct minimum).
        _e = state.energy + 1
        state.deal_damage(target, _e * 10)
        ## Self-harm bypasses block — the compound goes through your veins,
        ## not your guard.
        state.deal_damage(source, 8, bypass_block=True)
        state.add_log("[[The Compound]: {}E spent → {} dmg, -8 HP.".format(_e, _e * 10))

    @register_effect("iron_stance")
    def _eff_iron_stance(state, source, target):
        ## BB rare power: +20 block now AND retaliate scaling with turn count.
        ## Early game: 4 dmg/hit (turn 1). Late game: scales up (turn N → 4 + (N-1)*2).
        ## Battle engine recomputes the retaliate value each turn from the buff key.
        state.gain_block(source, 20)
        state.buff(source, "iron_stance_active", True)

    ## ---------------------------------------------------------------------------
    ## Battle ladder basic pool — Body bucket
    ## ---------------------------------------------------------------------------

    @register_effect("gut_punch")
    def _eff_gut_punch(state, source, target):
        state.deal_damage(target, 8)

    @register_effect("bracing")
    def _eff_bracing(state, source, target):
        state.gain_block(source, 8)

    @register_effect("second_wind")
    def _eff_second_wind(state, source, target):
        state.heal(source, 6)
        state.gain_block(source, 8)

    @register_effect("body_check")
    def _eff_body_check(state, source, target):
        state.deal_damage(target, 14)

    @register_effect("payday")
    def _eff_payday(state, source, target):
        dmg = min(20, (stats.available_money // 5000) if stats else 0)
        state.deal_damage(target, dmg)
        state.add_log("Payday: {} damage (savings/5k, cap 20).".format(dmg))

    @register_effect("bouncer_door")
    def _eff_bouncer_door(state, source, target):
        state.gain_block(source, 18)
        ## Reuse the single-shot retaliate slot used by iron_body (BB common).
        ## Iron Body sets dmg=4; bouncer_door is rarer/costlier so dmg=8.
        ## Adding to the existing buff (not overwriting) lets the two stack if
        ## the player has both, which is fine — they're both "next-hit only".
        state.buff(source, "single_retaliate_dmg", 8)

    ## ---------------------------------------------------------------------------
    ## Tech bucket
    ## ---------------------------------------------------------------------------

    @register_effect("quick_compile")
    def _eff_quick_compile(state, source, target):
        state.draw_cards(1)

    @register_effect("lint_pass")
    def _eff_lint_pass(state, source, target):
        ## Exhaust a random card from hand (excluding self — picking self would
        ## double-pile it: state.exhaust then engine.discard both run on the
        ## same id), then draw 1. Useful for dumping a clog status the engine
        ## injected (paperwork / fumes / tear_gas).
        _pool = [c for c in state.hand if c != "lint_pass"]
        if _pool:
            _victim = __import__('random').choice(_pool)
            state.exhaust(_victim)
            state.add_log("Lint Pass: exhausted {}.".format(_victim))
        state.draw_cards(1)

    @register_effect("stack_trace")
    def _eff_stack_trace(state, source, target):
        ## Peek mechanic removed — repurposed as pure cycling.
        state.draw_cards(2)

    @register_effect("unit_test")
    def _eff_unit_test(state, source, target):
        ## Block per OTHER Skill in hand, capped at 4. Excluding self means
        ## solo Unit Test = 0 block — this is a build-payoff card, not a
        ## vanilla Defend. Cap at 4 prevents Skill-flooded hands from
        ## generating 30+ block on a 1E uncommon.
        _skills = sum(
            1 for cid in state.hand
            if cid != "unit_test" and CARD_LIBRARY.get(cid, {}).get("type") == "Skill"
        )
        _skills = min(_skills, 4)
        state.gain_block(source, 6 * _skills)
        state.add_log("Unit Test: {} Skills in hand → {} block.".format(_skills, 6 * _skills))

    @register_effect("merge_conflict")
    def _eff_merge_conflict(state, source, target):
        state.deal_damage(target, 10)
        state.draw_cards(1)

    @register_effect("kernel_patch")
    def _eff_kernel_patch(state, source, target):
        state.gain_energy(1)
        state.draw_cards(2)

    @register_effect("pair_program")
    def _eff_pair_program(state, source, target):
        ## Peek mechanic removed — repurposed as free defensive draw.
        ## Differentiates from quick_compile (pure draw 1) via the block leg.
        state.gain_block(source, 3)
        state.draw_cards(1)

    ## ---------------------------------------------------------------------------
    ## Authority bucket
    ## ---------------------------------------------------------------------------

    @register_effect("radio_call")
    def _eff_radio_call(state, source, target):
        ## Peek mechanic removed (block 6 → 10 was compensation); then
        ## audit-nerfed 10 → 7 since 2× Defend at common is still strong.
        state.gain_block(source, 7)

    @register_effect("breath_test")
    def _eff_breath_test(state, source, target):
        ## Reuses the frame_trap reduction slot.
        state.buff(source, "next_attack_reduction", 5)

    @register_effect("procedural_kick")
    def _eff_procedural_kick(state, source, target):
        state.deal_damage(target, 5)
        state.gain_block(source, 5)

    @register_effect("riot_shield")
    def _eff_riot_shield(state, source, target):
        state.gain_block(source, 14)
        state.buff(source, "vigil_next_turn_block", 4)

    @register_effect("cuff_em")
    def _eff_cuff_em(state, source, target):
        state.skip_attacks(1)

    @register_effect("internal_review")
    def _eff_internal_review(state, source, target):
        state.cancel_next_attack_set()
        state.deal_damage(target, 8)

    ## ---------------------------------------------------------------------------
    ## Status / curse card effects — injected into draw pile by enemy wrinkles.
    ## All exhaust on play; some self-damage. The "use" is to clear them
    ## (or pay the toll if drawn at the wrong time).
    ## ---------------------------------------------------------------------------

    @register_effect("status_paperwork")
    def _eff_status_paperwork(state, source, target):
        state.add_log("[[Paperwork]: form filed. Hand thinner now.")

    @register_effect("status_counterfeit")
    def _eff_status_counterfeit(state, source, target):
        state.deal_damage(target, 4)
        state.deal_damage(source, 8)

    @register_effect("status_fumes")
    def _eff_status_fumes(state, source, target):
        state.deal_damage(source, 2)

    @register_effect("status_tear_gas")
    def _eff_status_tear_gas(state, source, target):
        state.deal_damage(source, 3)

    ## ---------------------------------------------------------------------------
    ## Rage cards — corruption injected by hatred thresholds. High raw damage,
    ## self-corrupting side effects (self-damage, random discard, random
    ## exhaust). Permanent in deck — these recur until removed by a fixer.
    ## ---------------------------------------------------------------------------

    import random as _rage_rand

    def _other_cards_in_hand(state, self_id):
        """Return hand cards excluding the card currently resolving (so a Rage
        card never discards/exhausts itself when it triggers from hand)."""
        try:
            return [cid for cid in state.hand if cid != self_id]
        except Exception:
            return []

    @register_effect("outburst")
    def _eff_outburst(state, source, target):
        ## Threshold-40 Rage. 12 dmg @ 1 energy — paid for in 9 HP AND
        ## +2 hatred (corruption snowballs into the next Rage threshold).
        ## Self-damage bypasses block — your block stops the enemy, not
        ## your own rage. Floor-clamped to leave you at 1 HP min.
        state.deal_damage(target, 12)
        state.deal_damage(source, 9, bypass_block=True)
        if stats:
            stats.increment_stats_pcr_hatred(2)
        state.add_log("Outburst: 12 damage. -9 HP. +2 Hatred.")

    @register_effect("tunnel_vision")
    def _eff_tunnel_vision(state, source, target):
        ## Threshold-60 Rage. 14 dmg @ 1 energy. Rage clouds judgment — one
        ## random card from hand OR draw pile is discarded. Hitting the draw
        ## pile means the victim is a card you haven't even seen yet — could
        ## be your key Strongman that won't show up this turn now.
        state.deal_damage(target, 14)
        _candidates = _other_cards_in_hand(state, "tunnel_vision") + list(state.draw_pile)
        if _candidates:
            _victim = _rage_rand.choice(_candidates)
            ## state.discard handles hand removal. For draw pile we hand-remove
            ## then push to discard_pile (matching discard semantics).
            if _victim in state.hand:
                state.discard(_victim)
            elif _victim in state.draw_pile:
                state.draw_pile.remove(_victim)
                state.discard_pile.append(_victim)
            _name = CARD_LIBRARY.get(_victim, {}).get("name", _victim)
            state.add_log("Tunnel Vision: discarded {}.".format(_name))
        if stats:
            stats.increment_stats_pcr_hatred(2)

    @register_effect("snap")
    def _eff_snap(state, source, target):
        ## Threshold-80 Rage. Free 8 dmg — a random card from hand is
        ## exhausted FOR THIS FIGHT (no run-deck removal). The old version
        ## permanently shredded a card from the player's run-deck and the
        ## designer judged that "felt awful" — losing a Strongman to a Rage
        ## RNG roll could brick a run. Now it's a single-fight exhaust:
        ## still corrupting (a key card gone for this combat) but not
        ## run-ruining. Rage stays in the deck — corruption is sticky, but
        ## it doesn't delete the rest of your kit on its way through.
        state.deal_damage(target, 8)
        _others = _other_cards_in_hand(state, "snap")
        if _others:
            _victim = _rage_rand.choice(_others)
            state.exhaust(_victim)
            _vc = CARD_LIBRARY.get(_victim, {})
            _name = _vc.get("name", _victim)
            state.add_log("Snap: exhausted {} for this fight.".format(_name))
        if stats:
            stats.increment_stats_pcr_hatred(2)

    @register_effect("compromise")
    def _eff_compromise(state, source, target):
        ## Defense-in-depth no-op — Compromise carries unplayable=True, so
        ## hand_playable returns False and battle_play_card never resolves
        ## this effect. If something bypasses the gate (dev tool, future
        ## bug), log and return rather than crash on a missing handler.
        state.add_log("Compromise: it's a dead card. It does nothing.")

    ## ---------------------------------------------------------------------------
    ## Combat-reward rares — ladder-fight drops, heavier mechanics than the
    ## activity-granted common/uncommon pool. Weights in pick_battle_rewards
    ## bias toward these (Hard fights 70% rare).
    ## ---------------------------------------------------------------------------

    @register_effect("killing_blow")
    def _eff_killing_blow(state, source, target):
        state.deal_damage(target, 14)
        ## Execution bonus: if the enemy is now (or was already) below half HP,
        ## deal a second 14-damage hit. Triggers off CURRENT enemy_hp post-first-
        ## hit so the threshold check feels right ("I knocked them low → finish").
        if state.enemy_max_hp > 0 and state.enemy_hp > 0 and state.enemy_hp * 2 < state.enemy_max_hp:
            state.deal_damage(target, 14)
            state.add_log("[[Killing Blow]: execution — second hit lands.")

    @register_effect("tactical_read")
    def _eff_tactical_read(state, source, target):
        ## Peek mechanic removed; energy gain bumped 1 → 2 to compensate.
        ## 0-cost exhaust + 2 energy = a clean one-shot tempo spike.
        state.gain_energy(2)

    @register_effect("iron_drill")
    def _eff_iron_drill(state, source, target):
        ## Base 12 block + 4 per OTHER Skill in hand, capped at +12 (max 24 block).
        ## Excludes self so solo iron_drill = 12 block, not 16.
        _skills = sum(
            1 for cid in state.hand
            if cid != "iron_drill" and CARD_LIBRARY.get(cid, {}).get("type") == "Skill"
        )
        _bonus = min(12, 4 * _skills)
        state.gain_block(source, 12 + _bonus)
        state.add_log("[[Iron Drill]: 12 + {} (per skill) = {} block.".format(_bonus, 12 + _bonus))

    @register_effect("last_stand")
    def _eff_last_stand(state, source, target):
        state.deal_damage(target, 16)
        ## Desperation draw: if HP is below half, the back-against-wall reward
        ## fires. Threshold check uses player_max_hp so it scales per class.
        if state.player_max_hp > 0 and state.player_hp * 2 < state.player_max_hp:
            state.draw_cards(2)
            state.add_log("[[Last Stand]: low HP — draw 2.")

    ## ---------------------------------------------------------------------------
    ## UPGRADED (`_plus`) EFFECTS — paired with `register_upgrade` table at the
    ## end of card_library.rpy. Effect-id convention is `<base>_plus`. Most
    ## upgrades are scalar bumps; a few add a small extra leg (draw, bleed
    ## duration, second-hit threshold). Status / rage / compromise cards are
    ## not upgradeable so they have no _plus effects here.
    ## ---------------------------------------------------------------------------

    @register_effect("strike_plus")
    def _eff_strike_plus(state, source, target):
        state.deal_damage(target, 9)

    @register_effect("defend_plus")
    def _eff_defend_plus(state, source, target):
        state.gain_block(source, 8)

    @register_effect("heavy_set_plus")
    def _eff_heavy_set_plus(state, source, target):
        dmg = 6 + (stats.pcr_hatred // 10) if stats else 6
        state.deal_damage(target, dmg)
        state.add_log("Heavy Set+: {} damage (scaled by hatred).".format(dmg))

    @register_effect("read_him_plus")
    def _eff_read_him_plus(state, source, target):
        state.gain_block(source, 9)
        state.draw_cards(2)

    @register_effect("stack_up_plus")
    def _eff_stack_up_plus(state, source, target):
        state.gain_energy(2)
        state.draw_cards(1)
        state.buff(source, "crash_next_turn", True)

    @register_effect("iron_will_plus")
    def _eff_iron_will_plus(state, source, target):
        state.gain_block(source, 13)

    @register_effect("personal_record_plus")
    def _eff_personal_record_plus(state, source, target):
        ## Same effect as base — the upgrade benefit comes from `exhaust=False`
        ## on the plus card (set via register_upgrade overrides).
        state.buff(source, "double_next_attack", True)

    @register_effect("boundary_plus")
    def _eff_boundary_plus(state, source, target):
        state.deal_damage(target, 6)
        state.heal(source, 6)

    @register_effect("side_income_plus")
    def _eff_side_income_plus(state, source, target):
        dmg = (stats.available_money // 8000) if stats else 0
        state.deal_damage(target, dmg)
        state.add_log("Side Income+: {} damage (savings / 8k).".format(dmg))

    @register_effect("vip_treatment_plus")
    def _eff_vip_treatment_plus(state, source, target):
        state.deal_damage(target, 34)
        state.deal_damage(source, 10, bypass_block=True)

    @register_effect("compile_plus")
    def _eff_compile_plus(state, source, target):
        state.draw_cards(3)

    @register_effect("production_push_plus")
    def _eff_production_push_plus(state, source, target):
        dmg = 12
        try:
            for cid in state.hand:
                c = CARD_LIBRARY.get(cid, {})
                if c.get("type") == "Skill":
                    dmg += 8
                    break
        except Exception:
            pass
        state.deal_damage(target, dmg)
        state.draw_cards(1)
        state.add_log("Production Push+: {} damage + draw.".format(dmg))

    @register_effect("backup_plus")
    def _eff_backup_plus(state, source, target):
        state.gain_block(source, 14)

    @register_effect("racetam_plus")
    def _eff_racetam_plus(state, source, target):
        state.gain_energy(1)
        state.draw_cards(2)

    @register_effect("flmodafinil_plus")
    def _eff_flmodafinil_plus(state, source, target):
        state.deal_damage(target, 32)
        if __import__('random').random() < 0.5:
            state.buff(source, "max_energy_penalty_next_turn", 1)
            state.add_log("FLModafinil+: peak ebbs — -1 max energy next turn.")

    @register_effect("mirror_plus")
    def _eff_mirror_plus(state, source, target):
        ## Mirror+ keeps the 2-turn cooldown (50% uptime change is too strong
        ## for a 2x-bounce card per the balance-judge audit). Upgrade leg is
        ## +5 immediate block — so the card has defensive value on the turn
        ## you play it, not just on the bounce.
        state.buff(source, "mirror_next", True)
        state.buff(source, "mirror_armed_for_counter", True)
        state.gain_block(source, 5)

    @register_effect("algorithm_plus")
    def _eff_algorithm_plus(state, source, target):
        state.skip_attacks(3)

    @register_effect("snitch_info_plus")
    def _eff_snitch_info_plus(state, source, target):
        state.deal_damage(target, 22)

    @register_effect("paragraph_4b_plus")
    def _eff_paragraph_4b_plus(state, source, target):
        state.deal_damage(target, 48)
        state.buff(source, "paragraph_4b_armed", True)

    @register_effect("ghost_secret_plus")
    def _eff_ghost_secret_plus(state, source, target):
        state.cancel_next_attack_set()
        state.deal_damage(target, 20)

    @register_effect("job_offer_plus")
    def _eff_job_offer_plus(state, source, target):
        state.player_max_hp += 8
        state.player_hp += 8
        state.buff(source, "starting_block_+1", True)
        state.buff(source, "job_offer_armed", True)

    @register_effect("stoic_refactor_plus")
    def _eff_stoic_refactor_plus(state, source, target):
        ## Base: 50% DR vs Mental only. Plus: same DR but also Special-typed.
        state.buff(source, "mental_dr_50", True)
        state.buff(source, "special_dr_50", True)

    @register_effect("stoic_anchor_plus")
    def _eff_stoic_anchor_plus(state, source, target):
        state.buff(source, "stoic_anchor_block", 3)
        state.buff(source, "stoic_anchor_heal", 2)

    @register_effect("quick_jab_plus")
    def _eff_quick_jab_plus(state, source, target):
        state.deal_damage(target, 10)

    @register_effect("loan_sharks_plus")
    def _eff_loan_sharks_plus(state, source, target):
        if stats and stats.try_spend_money(5000):
            state.deal_damage(target, 36)
            state.add_log("Loan Sharks+: 5000 CZK spent. 36 damage.")
        else:
            state.add_log("Loan Sharks+: card fizzles — no 5,000 CZK on hand.")

    @register_effect("paid_review_plus")
    def _eff_paid_review_plus(state, source, target):
        if stats and stats.try_spend_money(8000):
            state.cancel_next_attack_set()
            state.draw_cards(2)
            state.add_log("Paid Review+: 8000 CZK spent. Attack cancelled. +2 cards.")
        else:
            state.add_log("Paid Review+: phone goes to voicemail. No funds.")

    @register_effect("chain_of_command_plus")
    def _eff_chain_of_command_plus(state, source, target):
        state.gain_block(source, 13)
        state.draw_cards(1)

    @register_effect("vigil_plus")
    def _eff_vigil_plus(state, source, target):
        state.gain_block(source, 6)
        state.buff(source, "vigil_next_turn_block", 6)

    @register_effect("iron_stance_plus")
    def _eff_iron_stance_plus(state, source, target):
        state.gain_block(source, 24)
        state.buff(source, "iron_stance_active", True)

    @register_effect("spotter_plus")
    def _eff_spotter_plus(state, source, target):
        state.gain_block(source, 9)
        state.draw_cards(1)

    @register_effect("brawl_plus")
    def _eff_brawl_plus(state, source, target):
        state.deal_damage(target, 12)
        state.buff(source, "bleed_dmg", 4)
        state.buff(source, "bleed_turns", 3)

    @register_effect("empaths_insight_plus")
    def _eff_empaths_insight_plus(state, source, target):
        state.buff(source, "insight_block", 6)
        state.buff(source, "insight_turns_left", 4)

    @register_effect("iron_body_plus")
    def _eff_iron_body_plus(state, source, target):
        state.gain_block(source, 8)
        state.buff(source, "single_retaliate_dmg", 6)

    @register_effect("pump_plus")
    def _eff_pump_plus(state, source, target):
        state.gain_energy(2)
        if stats:
            stats.increment_stats_pcr_hatred(3)
        state.add_log("Pump+: +2 energy. The room shrinks. Hatred bumps less.")

    @register_effect("strongman_plus")
    def _eff_strongman_plus(state, source, target):
        state.gain_block(source, 28)
        state.draw_cards(2)

    @register_effect("tell_plus")
    def _eff_tell_plus(state, source, target):
        state.gain_block(source, 11)

    @register_effect("frame_trap_plus")
    def _eff_frame_trap_plus(state, source, target):
        state.buff(source, "next_attack_reduction", 11)

    @register_effect("charm_plus")
    def _eff_charm_plus(state, source, target):
        state.heal(source, 10)
        state.gain_block(source, 5)

    @register_effect("hrv_spike_plus")
    def _eff_hrv_spike_plus(state, source, target):
        state.gain_energy(2)
        state.deal_damage(source, 3, bypass_block=True)
        state.add_log("HRV Spike+: +2 energy, -3 HP. Recorded.")

    @register_effect("cognitive_stack_plus")
    def _eff_cognitive_stack_plus(state, source, target):
        state.draw_cards(4)

    @register_effect("override_plus")
    def _eff_override_plus(state, source, target):
        state.deal_damage(target, 44)
        state.buff(source, "max_energy_penalty_next_turn", 2)

    @register_effect("the_dossier_plus")
    def _eff_the_dossier_plus(state, source, target):
        ic = state.current_intent()
        if ic and any(t in ic.get("tags", []) for t in ("emotional", "guilt")):
            state.cancel_next_attack_set()
            state.add_log("[[The Dossier+]: 'emotional' attack disabled by leverage.")
        state.deal_damage(target, 30)

    @register_effect("the_compound_plus")
    def _eff_the_compound_plus(state, source, target):
        ## Self-cost scaled 8 → 12 to preserve the dmg/self-HP ratio.
        ## Without this, at 4E the card was 60 dmg for 8 HP — ratio doubled
        ## from base. Now 60 dmg for 12 HP keeps the bargain honest.
        _e = state.energy + 1
        state.deal_damage(target, _e * 12)
        state.deal_damage(source, 12, bypass_block=True)
        state.add_log("[[The Compound+]: {}E spent → {} dmg, -12 HP.".format(_e, _e * 12))

    @register_effect("took_the_heat")
    def _eff_took_the_heat(state, source, target):
        ## Dedicated effect (was sharing chain_of_command). The shared
        ## handler couldn't set a took_the_heat-specific flag without also
        ## firing on chain_of_command plays. Arms the fight-long buff that
        ## debt_of_honor's counter checks.
        state.gain_block(source, 10)
        state.draw_cards(1)
        state.buff(source, "took_the_heat_armed", True)

    @register_effect("took_the_heat_plus")
    def _eff_took_the_heat_plus(state, source, target):
        state.gain_block(source, 13)
        state.draw_cards(1)
        state.buff(source, "took_the_heat_armed", True)

    @register_effect("gut_punch_plus")
    def _eff_gut_punch_plus(state, source, target):
        state.deal_damage(target, 11)

    @register_effect("bracing_plus")
    def _eff_bracing_plus(state, source, target):
        state.gain_block(source, 11)

    @register_effect("second_wind_plus")
    def _eff_second_wind_plus(state, source, target):
        state.heal(source, 8)
        state.gain_block(source, 10)

    @register_effect("body_check_plus")
    def _eff_body_check_plus(state, source, target):
        state.deal_damage(target, 17)

    @register_effect("payday_plus")
    def _eff_payday_plus(state, source, target):
        ## Tightens ratio (5k → 4k per damage) instead of raising the cap.
        ## At 80k CZK base capped to 20; plus hits the cap at 80k earlier
        ## (saves ~16k vs. base) but never exceeds 20 — caps the meta.
        dmg = min(20, (stats.available_money // 4000) if stats else 0)
        state.deal_damage(target, dmg)
        state.add_log("Payday+: {} damage (savings/4k, cap 20).".format(dmg))

    @register_effect("bouncer_door_plus")
    def _eff_bouncer_door_plus(state, source, target):
        state.gain_block(source, 22)
        state.buff(source, "single_retaliate_dmg", 10)

    @register_effect("quick_compile_plus")
    def _eff_quick_compile_plus(state, source, target):
        state.draw_cards(2)

    @register_effect("lint_pass_plus")
    def _eff_lint_pass_plus(state, source, target):
        _pool = [c for c in state.hand if c != "lint_pass_plus"]
        if _pool:
            _victim = __import__('random').choice(_pool)
            state.exhaust(_victim)
            state.add_log("Lint Pass+: exhausted {}.".format(_victim))
        state.draw_cards(2)

    @register_effect("stack_trace_plus")
    def _eff_stack_trace_plus(state, source, target):
        state.draw_cards(3)

    @register_effect("unit_test_plus")
    def _eff_unit_test_plus(state, source, target):
        _skills = sum(
            1 for cid in state.hand
            if cid != "unit_test_plus" and CARD_LIBRARY.get(cid, {}).get("type") == "Skill"
        )
        _skills = min(_skills, 4)
        state.gain_block(source, 8 * _skills)
        state.add_log("Unit Test+: {} Skills in hand → {} block.".format(_skills, 8 * _skills))

    @register_effect("merge_conflict_plus")
    def _eff_merge_conflict_plus(state, source, target):
        state.deal_damage(target, 13)
        state.draw_cards(1)

    @register_effect("kernel_patch_plus")
    def _eff_kernel_patch_plus(state, source, target):
        state.gain_energy(1)
        state.draw_cards(3)

    @register_effect("pair_program_plus")
    def _eff_pair_program_plus(state, source, target):
        state.gain_block(source, 5)
        state.draw_cards(1)

    @register_effect("radio_call_plus")
    def _eff_radio_call_plus(state, source, target):
        state.gain_block(source, 10)

    @register_effect("breath_test_plus")
    def _eff_breath_test_plus(state, source, target):
        state.buff(source, "next_attack_reduction", 8)

    @register_effect("procedural_kick_plus")
    def _eff_procedural_kick_plus(state, source, target):
        state.deal_damage(target, 7)
        state.gain_block(source, 7)

    @register_effect("riot_shield_plus")
    def _eff_riot_shield_plus(state, source, target):
        state.gain_block(source, 17)
        state.buff(source, "vigil_next_turn_block", 6)

    @register_effect("internal_review_plus")
    def _eff_internal_review_plus(state, source, target):
        state.cancel_next_attack_set()
        state.deal_damage(target, 12)

    @register_effect("killing_blow_plus")
    def _eff_killing_blow_plus(state, source, target):
        state.deal_damage(target, 16)
        if state.enemy_max_hp > 0 and state.enemy_hp > 0 and state.enemy_hp * 2 < state.enemy_max_hp:
            state.deal_damage(target, 16)
            state.add_log("[[Killing Blow+]: execution — second hit lands.")

    @register_effect("tactical_read_plus")
    def _eff_tactical_read_plus(state, source, target):
        state.gain_energy(2)
        state.draw_cards(1)

    @register_effect("iron_drill_plus")
    def _eff_iron_drill_plus(state, source, target):
        _skills = sum(
            1 for cid in state.hand
            if cid != "iron_drill_plus" and CARD_LIBRARY.get(cid, {}).get("type") == "Skill"
        )
        _bonus = min(16, 4 * _skills)
        state.gain_block(source, 15 + _bonus)
        state.add_log("[[Iron Drill+]: 15 + {} (per skill) = {} block.".format(_bonus, 15 + _bonus))

    @register_effect("last_stand_plus")
    def _eff_last_stand_plus(state, source, target):
        state.deal_damage(target, 19)
        if state.player_max_hp > 0 and state.player_hp * 2 < state.player_max_hp:
            state.draw_cards(2)
            state.add_log("[[Last Stand+]: low HP — draw 2.")
