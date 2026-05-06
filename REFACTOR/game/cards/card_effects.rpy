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
##   state.peek_intents(n)                    — reveal next n enemy intents
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
        "read_him":                "Peek the next 3 colonel intents. Draw 1 card.",
        "stack_up":                "Gain +2 energy this turn. Crash next turn (-2 energy).",
        "gain_block_12":           "Gain 12 block.",
        "deal_damage_double_next": "Your next attack this turn fires twice.",
        "boundary":                "Deal 4 damage. Heal 4 HP.",
        "reframe":                 "Convert the colonel's next attack into block for you. Exhausts.",
        "side_income":             "Deal damage equal to (Money / 10,000), rounded down.",
        "vip_treatment":           "Deal 30 damage. Lose 10 HP. Exhausts.",
        "refactor":                "Cancel the colonel's next attack. Exhausts.",
        "compile":                 "Draw 2 cards.",
        "gain_block_15":           "Gain 15 block.",
        "procedural_defense":      "Block all damage from the colonel's next turn.",
        "racetam_burst":           "Gain +1 energy. Draw 1 card.",
        "flmodafinil_spike":       "Deal 28 damage. 50%: -1 max energy next turn. Exhausts.",
        "mirror":                  "The colonel's next attack hits HIM at 2x damage. 2-turn cooldown.",
        "algorithm":               "Skip the colonel's next 2 attacks. Exhausts.",
        "snitch_info":             "Reveal the colonel's full deck for the rest of the fight. Exhausts.",
        "paragraph_4b":            "Deal 40 damage. Auto-counters 'Training Debt'. Exhausts.",
        "ghost_secret":            "Cancel the colonel's next attack. Deal 15 damage. Exhausts.",
        "job_offer":               "Power: +5 max HP. +1 starting block per turn.",
        "stoic_refactor":          "Power: take 50% damage from emotional/mental colonel attacks.",
        "stoic_anchor":            "Power: +3 starting block per turn. Heal 3 HP after each colonel attack.",
        "quick_jab":               "Deal 4 damage. Draw 1 card.",
        "loan_sharks":             "Pay 5,000 CZK to deal 30 damage. (No funds = no damage.) Exhausts.",
        "chain_of_command":        "Gain 10 block. Draw 1 card.",
        "vigil":                   "Gain 4 block now. +4 starting block next turn.",
        "iron_stance":             "Power: +20 block. Retaliate (4 + 2x turn) damage when colonel hits.",
        "spotter":                 "Gain 6 block. Draw 1 card.",
        "brawl":                   "Deal 10 damage. Apply 3-turn bleed (3 dmg/turn) to the colonel.",
        "empaths_insight":         "Power: peek 5 intents. +1 starting block for the first 3 turns.",
        "iron_body":               "Gain 6 block. Retaliate 4 damage on the next colonel hit.",
        "pump":                    "Gain +2 energy this turn. +5 Hatred.",
        "strongman":               "Gain 25 block. Draw 2. Exhausts.",
        "tell":                    "Peek 1 intent. Gain 3 block. Free.",
        "frame_trap":              "Reduce the colonel's next attack by 8 (min 1).",
        "charm":                   "Heal 8 HP. Gain 3 block.",
        "hrv_spike":               "Gain +2 energy. Lose 5 HP.",
        "cognitive_stack":         "Draw 3 cards. Exhausts.",
        "override":                "Deal 40 damage. -2 max energy next turn. Exhausts.",
        "vladeks_form":            "Power: +2 starting block/turn. Iron Stance retaliate doubled.",
        "the_dossier":             "Disable one 'emotional' or 'guilt' colonel attack. Deal 25 damage. Exhausts.",
        "the_compound":            "Deal (current energy × 10) damage. Lose 8 HP. Exhausts.",
    }

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
        ## 14 damage + 1 draw, with a hand-mix bonus that rewards tempo decks.
        dmg = 14
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
        ## DE signature — peek next 3 colonel intents AND draw 1 (tempo + info)
        state.peek_intents(3)
        state.draw_cards(1)

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
        state.gain_block(source, 12)

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
        state.deal_damage(target, 30)
        state.deal_damage(source, 10)

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
        state.gain_block(source, 15)

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

    ## ---------------------------------------------------------------------------
    ## Event drops
    ## ---------------------------------------------------------------------------

    @register_effect("algorithm")
    def _eff_algorithm(state, source, target):
        state.skip_attacks(2)

    @register_effect("snitch_info")
    def _eff_snitch(state, source, target):
        state.peek_intents(99)  ## reveal full deck for the rest of the fight

    @register_effect("paragraph_4b")
    def _eff_paragraph_4b(state, source, target):
        state.deal_damage(target, 40)

    @register_effect("ghost_secret")
    def _eff_ghost_secret(state, source, target):
        state.cancel_next_attack_set()
        state.deal_damage(target, 15)

    @register_effect("job_offer")
    def _eff_job_offer(state, source, target):
        state.player_max_hp += 5
        state.player_hp += 5
        state.buff(source, "starting_block_+1", True)

    @register_effect("stoic_refactor")
    def _eff_stoic_refactor(state, source, target):
        state.buff(source, "mental_dr_50", True)

    @register_effect("stoic_anchor")
    def _eff_stoic_anchor(state, source, target):
        ## Power: persistent buff. Engine applies starting_block_+3 and heal_after_attack at runtime.
        state.buff(source, "stoic_anchor_block", 3)
        state.buff(source, "stoic_anchor_heal", 3)

    ## ---------------------------------------------------------------------------
    ## Additional cards
    ## ---------------------------------------------------------------------------

    @register_effect("quick_jab")
    def _eff_quick_jab(state, source, target):
        state.deal_damage(target, 4)
        state.draw_cards(1)

    @register_effect("loan_sharks")
    def _eff_loan_sharks(state, source, target):
        if stats and stats.try_spend_money(5000):
            state.deal_damage(target, 30)
            state.add_log("Loan Sharks: 5000 CZK spent. 30 damage.")
        else:
            state.add_log("Loan Sharks: card fizzles — no 5,000 CZK on hand.")

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
        ## DE rare power: peek deeper + extra starting block for 3 turns
        state.peek_intents(5)
        state.buff(source, "insight_block", 1)
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
        state.peek_intents(1)
        state.gain_block(source, 3)

    @register_effect("frame_trap")
    def _eff_frame_trap(state, source, target):
        state.buff(source, "next_attack_reduction", 8)

    @register_effect("charm")
    def _eff_charm(state, source, target):
        state.heal(source, 8)
        state.gain_block(source, 3)

    @register_effect("hrv_spike")
    def _eff_hrv_spike(state, source, target):
        state.gain_energy(2)
        state.deal_damage(source, 5)
        state.add_log("HRV Spike: +2 energy, -5 HP. Recorded.")

    @register_effect("cognitive_stack")
    def _eff_cognitive_stack(state, source, target):
        state.draw_cards(3)

    @register_effect("override")
    def _eff_override(state, source, target):
        state.deal_damage(target, 40)
        state.buff(source, "max_energy_penalty_next_turn", state.buffs.get("max_energy_penalty_next_turn", 0) + 2)

    ## ---------------------------------------------------------------------------
    ## Arc-reward effects
    ## ---------------------------------------------------------------------------

    @register_effect("vladeks_form")
    def _eff_vladeks_form(state, source, target):
        ## BB boss power: stacks with iron_stance + adds passive starting block
        state.buff(source, "stoic_anchor_block", state.buffs.get("stoic_anchor_block", 0) + 2)
        state.buff(source, "vladeks_active", True)

    @register_effect("the_dossier")
    def _eff_the_dossier(state, source, target):
        ## Cancel next attack if it's emotional/guilt-tagged. Deal 25 damage either way.
        ic = state.current_intent()
        if ic and any(t in ic.get("tags", []) for t in ("emotional", "guilt")):
            state.cancel_next_attack_set()
            state.add_log("[[The Dossier]]: 'emotional' attack disabled by leverage.")
        state.deal_damage(target, 25)

    @register_effect("the_compound")
    def _eff_the_compound(state, source, target):
        ## Read pre-spend energy by adding back the cost (1E for the_compound).
        ## At 1E in hand, energy at this point is 0 → +1 = 1 → 10 dmg (correct minimum).
        _e = state.energy + 1
        state.deal_damage(target, _e * 10)
        state.deal_damage(source, 8)
        state.add_log("[[The Compound]]: {}E spent → {} dmg, -8 HP.".format(_e, _e * 10))

    @register_effect("iron_stance")
    def _eff_iron_stance(state, source, target):
        ## BB rare power: +20 block now AND retaliate scaling with turn count.
        ## Early game: 4 dmg/hit (turn 1). Late game: scales up (turn N → 4 + (N-1)*2).
        ## Battle engine recomputes the retaliate value each turn from the buff key.
        state.gain_block(source, 20)
        state.buff(source, "iron_stance_active", True)
