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
        "gain_block_12":           "Gain 12 block.",
        "deal_damage_double_next": "Your next attack this turn fires twice.",
        "boundary":                "Deal 4 damage. Heal 4 HP.",
        "reframe":                 "Convert the enemy's next attack into block for you. Exhausts.",
        "side_income":             "Deal damage equal to (Money / 10,000), rounded down.",
        "vip_treatment":           "Deal 30 damage. Lose 10 HP. Exhausts.",
        "refactor":                "Cancel the enemy's next attack. Exhausts.",
        "compile":                 "Draw 2 cards.",
        "production_push":         "Deal 14 damage. Draw 1 card. +6 damage per other Logic/Tech card in hand.",
        "gain_block_15":           "Gain 15 block.",
        "procedural_defense":      "Block all damage from the enemy's next attack turn.",
        "racetam_burst":           "Gain +1 energy. Draw 1 card.",
        "flmodafinil_spike":       "Deal 28 damage. 50%: -1 max energy next turn. Exhausts.",
        "mirror":                  "The enemy's next attack hits THEM at 2x damage. 2-turn cooldown.",
        "algorithm":               "Skip the enemy's next 2 attacks. Exhausts.",
        "snitch_info":             "Deal 18 damage. Exhausts.",
        "paragraph_4b":            "Deal 40 damage. Auto-counters 'Training Debt'. Exhausts.",
        "ghost_secret":            "Cancel the enemy's next attack. Deal 15 damage. Exhausts.",
        "job_offer":               "Power: +5 max HP. +1 starting block per turn.",
        "stoic_refactor":          "Power: take 50% damage from Mental-typed attacks.",
        "stoic_anchor":            "Power: +3 starting block per turn. Heal 3 HP after each enemy attack.",
        "quick_jab":               "Deal 7 damage.",
        "loan_sharks":             "Pay 5,000 CZK to deal 30 damage. (No funds = no damage.) Exhausts.",
        "paid_review":             "Pay 10,000 CZK to cancel the enemy's next attack and draw 2. (No funds = no effect.) Exhausts.",
        "chain_of_command":        "Gain 10 block. Draw 1 card.",
        "vigil":                   "Gain 4 block now. +4 starting block next turn.",
        "iron_stance":             "Power: +20 block. Retaliate (4 + 2x turn) damage when you're hit.",
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
        "the_dossier":             "Cancel one incoming attack. Deal 25 damage. Exhausts.",
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
        "radio_call":              "Gain 10 block.",
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
        "snap":                    "Deal 8.\nExhaust 1 random hand card — and remove it from your deck.\n+2 Hatred.",
        ## Compromise card (injected by forced_detour on 2nd+ loss; unplayable)
        "compromise":              "Unplayable.\nDead weight in hand.",
        ## Combat-reward rares (ladder-fight drops)
        "killing_blow":            "Deal 14. If enemy is below half HP: deal 14 more.",
        "tactical_read":           "Gain 2 energy this turn. Exhausts.",
        "iron_drill":              "Gain 12 block + 4 per Skill in hand (capped at +12).",
        "last_stand":              "Deal 16. If you're below half HP, draw 2. Exhausts.",
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
        ## Was a full-deck peek; peek mechanic removed. Reframed as "you used
        ## the intel" — one-shot heavy hit, exhausts.
        state.deal_damage(target, 18)

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
        ## Peek mechanic removed; block bumped 6 → 10 to compensate.
        state.gain_block(source, 10)

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
        ## Threshold-80 Rage. Free 8 dmg — but a random hand card is exhausted
        ## for the fight AND removed from the run-deck permanently. Class
        ## signature cards (heavy_set / read_him / stack_up), other Rage cards,
        ## and Compromise cards are NOT permanent-removed (the first because
        ## class identity is sacred; the latter two because removing your own
        ## corruption mid-fight would be a free heal — corruption is sticky).
        state.deal_damage(target, 8)
        _others = _other_cards_in_hand(state, "snap")
        if _others:
            _victim = _rage_rand.choice(_others)
            state.exhaust(_victim)
            _vc = CARD_LIBRARY.get(_victim, {})
            _name = _vc.get("name", _victim)
            _protected = (
                _victim in CLASS_SIGNATURE_CARDS
                or bool(_vc.get("is_rage"))
                or bool(_vc.get("is_compromise"))
            )
            if not _protected and player_deck is not None:
                try:
                    player_deck.remove(_victim)
                    state.add_log("Snap: exhausted {} AND removed from deck.".format(_name))
                except Exception:
                    state.add_log("Snap: exhausted {}.".format(_name))
            else:
                state.add_log("Snap: exhausted {} (protected from deck removal).".format(_name))
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
