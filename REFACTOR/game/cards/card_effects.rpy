################################################################################
## REFACTOR — Card Effects
##
## Each effect_id maps to a callable: (state, source, target) -> None.
## state is a BattleState instance (battle_engine.rpy).
##
## BattleState API used here:
##   state.deal_damage(target, amount, bypass_block=False)
##   state.gain_block(target, amount)   state.heal(target, amount)
##   state.draw_cards(n)                state.gain_energy(n)
##   state.gain_hatred(n)               — Hatred delta; fires See Red / Thick Skull
##   state.cancel_next_attack_set()     state.skip_attacks(n)
##   state.exhaust(card_id)             state.discard(card_id)
##   state.buff(target, key, value)     state.add_log(msg)
##   state.cards_played_this_turn / state.skill_played_this_turn  — per-turn
##   state.player_block / last_damage_to_enemy / enemy_hp ...     — read state
################################################################################

init python:

    ## ---------------------------------------------------------------------------
    ## EFFECT_DESCRIPTIONS — static tooltip text keyed by effect_id. Stat-scaling
    ## cards are resolved dynamically by effect_description() below instead.
    ## ---------------------------------------------------------------------------

    EFFECT_DESCRIPTIONS = {
        ## Basic & signature
        "strike":                  "Deal 7 damage.",
        "defend":                  "Gain 6 block.",
        ## Hatred archetype
        "provoke":                 "Gain 8 Hatred. Draw 1 card.",
        "knuckle_down":            "Deal 14 damage. Gain 6 Hatred.",
        "red_mist":                "Deal 8 damage twice. Gain 4 Hatred.",
        "see_red":                 "Power: each time you gain Hatred this fight, gain 2 block.",
        "thick_skull":             "Power: the first time a Hatred gain would reach 100 this fight, Hatred is held at 80 and you gain 20 block.",
        "adrenaline_dump":         "Lose 10 Hatred. Gain 2 energy.",
        "last_nerve":              "Deal 6 damage. If a Rage card is in your hand, draw 1 card.",
        "embrace_it":              "Exhaust a Rage card in your hand: gain 15 block and draw 2 cards.",
        ## Stoic archetype
        "bracing":                 "Gain 9 block.",
        "backup":                  "Gain 10 block.",
        "chain_of_command":        "Gain 8 block. Draw 1 card.",
        "iron_posture":            "Power: at the start of each turn, keep half your remaining block instead of losing all of it.",
        "hold_the_line":           "Gain 2 block for every Skill in your hand.",
        "brick_wall":              "Deal 8 damage. Gain block equal to the damage dealt.",
        "iron_stance":             "Power: gain 12 block. Retaliate 4 when hit, growing +2 each turn (cap 12).",
        "bouncer_door":            "Gain 18 block. Retaliate 8 damage on the next hit.",
        "stoic_anchor":            "Power: +2 starting block per turn. Heal 2 HP after each enemy attack.",
        "second_wind":             "Heal 6 HP. Gain 10 block.",
        ## Tech archetype
        "quick_compile":           "Draw 1 card. Free.",
        "pair_program":            "Gain 4 block. Draw 1 card. Free.",
        "stack_trace":             "Draw 2 cards.",
        "unit_test":               "Gain 5 block for every other Skill in your hand.",
        "production_push":         "Deal 8 damage. 16 instead if you've played a Skill this turn. Draw 1 card.",
        "refactor":                "Cancel the enemy's next attack. Exhausts.",
        "kernel_patch":            "Gain 2 energy. Draw 2 cards. Exhausts.",
        "hotfix":                  "Deal 5 damage. Draw 1 card. Deal 13 instead if this is the 3rd+ card you've played this turn.",
        "ship_it":                 "Gain 1 energy for each Skill in your hand (max 3). Exhausts.",
        "code_review":             "Exhaust your leftmost other card. Draw 2 cards. Gain 3 block.",
        "crunch_time":             "Deal 4 damage for each card you've played this turn, including this one.",
        ## Neutral
        "gut_punch":               "Deal 9 damage.",
        "body_check":              "Deal 16 damage.",
        "breath_test":             "The enemy's next attack deals 6 less (minimum 1).",
        "killing_blow":            "Deal 14. If the enemy is below half HP: deal 14 more.",
        "last_stand":              "Deal 18. If you're below half HP, draw 2 cards. Exhausts.",
        "cuff_em":                 "Skip the enemy's next attack entirely. Exhausts.",
        ## Corruption / Rage
        "outburst":                "Deal 14.\nLose 6 HP.\n+2 Hatred.",
        "tunnel_vision":           "Deal 16.\nDiscard 1 random card.\n+2 Hatred.",
        "snap":                    "Deal 10.\nExhaust 1 random card from your hand (this fight only).\n+2 Hatred.",
        ## Class starters / event / boss / arc / story (out of scope)
        "read_him":                "Gain 6 block. Draw 2 cards.",
        "stack_up":                "Gain +2 energy this turn. Crash next turn (-2 energy).",
        "racetam_burst":           "Gain +1 energy. Draw 1 card.",
        "flmodafinil_spike":       "Deal 28 damage. 50%: -1 max energy next turn. Exhausts.",
        "mirror":                  "The enemy's next attack hits THEM at 2x damage. 2-turn cooldown.",
        "paragraph_4b":            "Deal 40 damage. Voids 'Training Debt' for the fight. Exhausts.",
        "ghost_secret":            "Cancel the enemy's next attack. Deal 15 damage. Exhausts.",
        "job_offer":               "Power: +5 max HP. +1 starting block per turn.",
        "stoic_refactor":          "Power: take 50% damage from Mental-typed attacks.",
        "empaths_insight":         "Power: +5 starting block per turn for the first 3 turns.",
        "tell":                    "Gain 8 block. Free.",
        "frame_trap":              "Reduce the enemy's next attack by 8 (min 1).",
        "charm":                   "Heal 8 HP. Gain 3 block.",
        "hrv_spike":               "Gain +2 energy. Lose 5 HP.",
        "cognitive_stack":         "Draw 3 cards. Exhausts.",
        "override":                "Deal 40 damage. -2 max energy next turn. Exhausts.",
        "the_dossier":             "Deal 25 damage. Cancel the next attack if it's tagged emotional or guilt. Exhausts.",
        "the_compound":            "Deal (current energy × 10) damage. Lose 8 HP. Exhausts.",
        "took_the_heat":           "Gain 10 block. Draw 1 card. Exhausts.",
        ## Status / curse
        "status_paperwork":        "Status. Fills the form. Exhausts.",
        "status_counterfeit":      "Status. Deal 4. Take 8. Exhausts.",
        "status_fumes":            "Status. Take 2. Exhausts.",
        "status_tear_gas":         "Status. Take 3. Exhausts.",
        ## Compromise
        "compromise":              "Unplayable.\nDead weight in hand.",
        ## ─── Upgraded (`_plus`) variants ───
        "strike_plus":             "Deal 9 damage.",
        "defend_plus":             "Gain 8 block.",
        "bracing_plus":            "Gain 11 block.",
        "backup_plus":             "Gain 14 block.",
        "chain_of_command_plus":   "Gain 11 block. Draw 1 card.",
        "iron_stance_plus":        "Power: gain 16 block. Retaliate 4 when hit, growing +2 each turn (cap 12).",
        "bouncer_door_plus":       "Gain 22 block. Retaliate 10 damage on the next hit.",
        "stoic_anchor_plus":       "Power: +3 starting block per turn. Heal 2 HP after each enemy attack.",
        "second_wind_plus":        "Heal 8 HP. Gain 13 block.",
        "quick_compile_plus":      "Draw 2 cards. Free.",
        "pair_program_plus":       "Gain 6 block. Draw 1 card. Free.",
        "stack_trace_plus":        "Draw 3 cards.",
        "unit_test_plus":          "Gain 8 block for every other Skill in your hand.",
        "production_push_plus":    "Deal 11 damage. 20 instead if you've played a Skill this turn. Draw 1 card.",
        "kernel_patch_plus":       "Gain 2 energy. Draw 3 cards. Exhausts.",
        "gut_punch_plus":          "Deal 11 damage.",
        "body_check_plus":         "Deal 20 damage.",
        "breath_test_plus":        "The enemy's next attack deals 8 less (minimum 1).",
        "killing_blow_plus":       "Deal 16. If the enemy is below half HP: deal 16 more.",
        "last_stand_plus":         "Deal 22. If you're below half HP, draw 2 cards. Exhausts.",
        "read_him_plus":           "Gain 9 block. Draw 2 cards.",
        "stack_up_plus":           "Gain +2 energy this turn. Draw 1. Crash next turn (-2 energy).",
        "racetam_plus":            "Gain +1 energy. Draw 2 cards.",
        "flmodafinil_plus":        "Deal 32 damage. 50%: -1 max energy next turn. Exhausts.",
        "mirror_plus":             "The enemy's next attack hits THEM at 2x damage. Gain 5 block. 2-turn cooldown.",
        "paragraph_4b_plus":       "Deal 48 damage. Voids 'Training Debt' for the fight. Exhausts.",
        "ghost_secret_plus":       "Cancel the enemy's next attack. Deal 20 damage. Exhausts.",
        "job_offer_plus":          "Power: +8 max HP. +1 starting block per turn.",
        "stoic_refactor_plus":     "Power: take 50% damage from Mental-typed attacks.",
        "empaths_insight_plus":    "Power: +6 starting block per turn for the first 4 turns.",
        "tell_plus":               "Gain 11 block. Free.",
        "frame_trap_plus":         "Reduce the enemy's next attack by 11 (min 1).",
        "charm_plus":              "Heal 10 HP. Gain 5 block.",
        "hrv_spike_plus":          "Gain +2 energy. Lose 3 HP.",
        "cognitive_stack_plus":    "Draw 4 cards. Exhausts.",
        "override_plus":           "Deal 44 damage. -2 max energy next turn. Exhausts.",
        "the_dossier_plus":        "Deal 30 damage. Cancel the next attack if it's tagged emotional or guilt. Exhausts.",
        "the_compound_plus":       "Deal (current energy × 12) damage. Lose 12 HP. Exhausts.",
        "took_the_heat_plus":      "Gain 13 block. Draw 1 card. Exhausts.",
        ## New-archetype `_plus` variants (the See Red / Thick Skull / Iron
        ## Posture Powers upgrade to cost 0 and reuse the base effect/text).
        "provoke_plus":            "Gain 8 Hatred. Draw 2 cards.",
        "knuckle_down_plus":       "Deal 18 damage. Gain 6 Hatred.",
        "red_mist_plus":           "Deal 10 damage twice. Gain 4 Hatred.",
        "adrenaline_dump_plus":    "Lose 10 Hatred. Gain 2 energy. Draw 1 card.",
        "last_nerve_plus":         "Deal 9 damage. If a Rage card is in your hand, draw 1 card.",
        "embrace_it_plus":         "Exhaust a Rage card in your hand: gain 20 block and draw 2 cards.",
        "hold_the_line_plus":      "Gain 3 block for every Skill in your hand.",
        "brick_wall_plus":         "Deal 12 damage. Gain block equal to the damage dealt.",
        "hotfix_plus":             "Deal 8 damage. Draw 1 card. Deal 17 instead if this is the 3rd+ card you've played this turn.",
        "ship_it_plus":            "Gain 1 energy for each Skill in your hand (max 3). Draw 1 card. Exhausts.",
        "code_review_plus":        "Exhaust your leftmost other card. Draw 2 cards. Gain 6 block.",
        "crunch_time_plus":        "Deal 5 damage for each card you've played this turn, including this one.",
    }

    ## Counterweight converts the block wall into damage without consuming it,
    ## so the hit is capped — keeps a 1-energy uncommon from out-damaging the
    ## rare Attacks. Tunable.
    COUNTERWEIGHT_CAP = 15

    ## ---------------------------------------------------------------------------
    ## Dynamic description resolution. Stat-scaling cards (Heavy Set / Breaking
    ## Point / Bottled Rage / Snap Decision scale off Hatred; Counterweight off
    ## current block) read better with the live number spelled out. Call this
    ## from every UI site instead of EFFECT_DESCRIPTIONS.get().
    ## ---------------------------------------------------------------------------

    def effect_description(effect_id):
        if not effect_id:
            return ""
        h = stats.pcr_hatred if stats else 0
        if effect_id == "heavy_set":
            return "Deal {} damage.\nScales with Hatred.".format(6 + h // 8)
        if effect_id == "heavy_set_plus":
            return "Deal {} damage.\nScales with Hatred.".format(8 + h // 8)
        if effect_id == "breaking_point":
            return "Deal {} damage.\n10 + 1 per 4 Hatred.".format(10 + h // 4)
        if effect_id == "bottled_rage":
            return "Deal {} damage (Hatred / 2).\nThen lose 25 Hatred.".format(h // 2)
        if effect_id == "snap_decision":
            return "Deal {} damage.\n18 if Hatred is 60 or more.".format(18 if h >= 60 else 9)
        if effect_id == "counterweight":
            if battle_state is not None:
                return "Deal {} damage (your block, max {}).".format(
                    min(battle_state.player_block, COUNTERWEIGHT_CAP), COUNTERWEIGHT_CAP)
            return "Deal damage equal to your current block (max {}).".format(COUNTERWEIGHT_CAP)
        if effect_id == "breaking_point_plus":
            return "Deal {} damage.\n13 + 1 per 3 Hatred.".format(13 + h // 3)
        if effect_id == "bottled_rage_plus":
            return "Deal {} damage (Hatred / 2 + 6).\nThen lose 25 Hatred.".format(h // 2 + 6)
        if effect_id == "snap_decision_plus":
            return "Deal {} damage.\n24 if Hatred is 60 or more.".format(24 if h >= 60 else 12)
        if effect_id == "counterweight_plus":
            if battle_state is not None:
                return "Deal {} damage (your block + 4).".format(
                    min(battle_state.player_block, COUNTERWEIGHT_CAP) + 4)
            return "Deal damage equal to your current block + 4 (max {}).".format(COUNTERWEIGHT_CAP + 4)
        return EFFECT_DESCRIPTIONS.get(effect_id, "")

    ## ---------------------------------------------------------------------------
    ## BASIC & SIGNATURE
    ## ---------------------------------------------------------------------------

    @register_effect("strike")
    def _eff_strike(state, source, target):
        state.deal_damage(target, 7)

    @register_effect("defend")
    def _eff_defend(state, source, target):
        state.gain_block(source, 6)

    @register_effect("heavy_set")
    def _eff_heavy_set(state, source, target):
        ## BB signature — damage scales with the run-stat pcr_hatred.
        dmg = 6 + (stats.pcr_hatred // 8) if stats else 6
        state.deal_damage(target, dmg)
        state.add_log("Heavy Set: {} damage (scaled by Hatred).".format(dmg))

    ## ---------------------------------------------------------------------------
    ## ARCHETYPE: HATRED — generators push Hatred, scalers spend it, See Red /
    ## Thick Skull make running hot survivable. All Hatred deltas route through
    ## state.gain_hatred so See Red / Thick Skull see them.
    ## ---------------------------------------------------------------------------

    @register_effect("provoke")
    def _eff_provoke(state, source, target):
        state.gain_hatred(8)
        state.draw_cards(1)

    @register_effect("knuckle_down")
    def _eff_knuckle_down(state, source, target):
        state.deal_damage(target, 14)
        state.gain_hatred(6)

    @register_effect("snap_decision")
    def _eff_snap_decision(state, source, target):
        _h = stats.pcr_hatred if stats else 0
        _dmg = 18 if _h >= 60 else 9
        state.deal_damage(target, _dmg)
        state.add_log("Snap Decision: {} damage (Hatred {}).".format(_dmg, _h))

    @register_effect("red_mist")
    def _eff_red_mist(state, source, target):
        state.deal_damage(target, 8)
        state.deal_damage(target, 8)
        state.gain_hatred(4)

    @register_effect("breaking_point")
    def _eff_breaking_point(state, source, target):
        _h = stats.pcr_hatred if stats else 0
        _dmg = 10 + _h // 4
        state.deal_damage(target, _dmg)
        state.add_log("Breaking Point: {} damage (10 + Hatred/4).".format(_dmg))

    @register_effect("bottled_rage")
    def _eff_bottled_rage(state, source, target):
        ## Cash out — damage scales off Hatred, then dumps 25 of it. The
        ## archetype's pressure valve: pull back from the breakdown clock.
        _dmg = (stats.pcr_hatred // 2) if stats else 0
        state.deal_damage(target, _dmg)
        state.gain_hatred(-25)
        state.add_log("Bottled Rage: {} damage. -25 Hatred.".format(_dmg))

    @register_effect("see_red")
    def _eff_see_red(state, source, target):
        ## Power — gain_hatred() reads this buff and walls up block per gain.
        state.buff(source, "see_red", True)

    @register_effect("thick_skull")
    def _eff_thick_skull(state, source, target):
        ## Power — gain_hatred() reads this buff and catches the first gain
        ## that would reach 100, pinning Hatred at the floor instead.
        state.buff(source, "thick_skull", True)

    @register_effect("adrenaline_dump")
    def _eff_adrenaline_dump(state, source, target):
        state.gain_hatred(-10)
        state.gain_energy(2)

    @register_effect("last_nerve")
    def _eff_last_nerve(state, source, target):
        state.deal_damage(target, 6)
        if any(CARD_LIBRARY.get(c, {}).get("is_rage") for c in state.hand):
            state.draw_cards(1)
            state.add_log("Last Nerve: a Rage card in hand — draw 1.")

    @register_effect("embrace_it")
    def _eff_embrace_it(state, source, target):
        ## Exhaust the first Rage card in hand for a wall + draw. hand_playable
        ## gates this card unplayable when no Rage card is present.
        _rage = next((c for c in state.hand if CARD_LIBRARY.get(c, {}).get("is_rage")), None)
        if _rage is not None:
            state.exhaust(_rage)
            state.add_log("Embrace It: exhausted {}.".format(CARD_LIBRARY.get(_rage, {}).get("name", _rage)))
        state.gain_block(source, 15)
        state.draw_cards(2)

    ## ---------------------------------------------------------------------------
    ## ARCHETYPE: STOIC WALL
    ## ---------------------------------------------------------------------------

    @register_effect("bracing")
    def _eff_bracing(state, source, target):
        state.gain_block(source, 9)

    @register_effect("backup")
    def _eff_backup(state, source, target):
        state.gain_block(source, 10)

    @register_effect("chain_of_command")
    def _eff_chain_of_command(state, source, target):
        state.gain_block(source, 8)
        state.draw_cards(1)

    @register_effect("iron_posture")
    def _eff_iron_posture(state, source, target):
        ## Power — battle_start_player_turn reads this buff and retains half
        ## the standing block instead of clearing it.
        state.buff(source, "iron_posture", True)

    @register_effect("counterweight")
    def _eff_counterweight(state, source, target):
        ## Deal damage = current block, capped. Damaging the enemy never
        ## touches player_block, so the wall stays up — the cap is what keeps
        ## a 1-energy uncommon from eclipsing the rare Attacks.
        _dmg = min(state.player_block, COUNTERWEIGHT_CAP)
        state.deal_damage(target, _dmg)
        state.add_log("Counterweight: {} damage (block {}, cap {}).".format(
            _dmg, state.player_block, COUNTERWEIGHT_CAP))

    @register_effect("hold_the_line")
    def _eff_hold_the_line(state, source, target):
        _skills = sum(1 for c in state.hand if CARD_LIBRARY.get(c, {}).get("type") == "Skill")
        state.gain_block(source, 2 * _skills)
        state.add_log("Hold the Line: {} Skills in hand -> {} block.".format(_skills, 2 * _skills))

    @register_effect("brick_wall")
    def _eff_brick_wall(state, source, target):
        state.deal_damage(target, 8)
        ## Block = damage actually dealt (enemy block can shave the 8).
        state.gain_block(source, state.last_damage_to_enemy)

    @register_effect("iron_stance")
    def _eff_iron_stance(state, source, target):
        ## Power — 12 block now + retaliate that scales with turn count.
        ## battle_resolve_enemy recomputes the retaliate from iron_stance_active.
        state.gain_block(source, 12)
        state.buff(source, "iron_stance_active", True)

    @register_effect("bouncer_door")
    def _eff_bouncer_door(state, source, target):
        state.gain_block(source, 18)
        ## single_retaliate_dmg — fires once on the next hit (shared slot).
        state.buff(source, "single_retaliate_dmg", 8)

    @register_effect("stoic_anchor")
    def _eff_stoic_anchor(state, source, target):
        ## Power — +2 starting block per turn, heal 2 after each enemy attack.
        state.buff(source, "stoic_anchor_block", 2)
        state.buff(source, "stoic_anchor_heal", 2)

    @register_effect("second_wind")
    def _eff_second_wind(state, source, target):
        state.heal(source, 6)
        state.gain_block(source, 10)

    ## ---------------------------------------------------------------------------
    ## ARCHETYPE: TECH TEMPO
    ## ---------------------------------------------------------------------------

    @register_effect("quick_compile")
    def _eff_quick_compile(state, source, target):
        state.draw_cards(1)

    @register_effect("pair_program")
    def _eff_pair_program(state, source, target):
        state.gain_block(source, 4)
        state.draw_cards(1)

    @register_effect("stack_trace")
    def _eff_stack_trace(state, source, target):
        state.draw_cards(2)

    @register_effect("unit_test")
    def _eff_unit_test(state, source, target):
        ## Block per OTHER Skill in hand, capped at 4 Skills — a build payoff,
        ## not a vanilla Defend. Solo Unit Test = 0 block.
        _skills = sum(
            1 for cid in state.hand
            if cid != "unit_test" and CARD_LIBRARY.get(cid, {}).get("type") == "Skill"
        )
        _skills = min(_skills, 4)
        state.gain_block(source, 5 * _skills)
        state.add_log("Unit Test: {} Skills in hand -> {} block.".format(_skills, 5 * _skills))

    @register_effect("production_push")
    def _eff_production_push(state, source, target):
        ## Combo: doubles up if a Skill was already played this turn.
        _dmg = 16 if state.skill_played_this_turn else 8
        state.deal_damage(target, _dmg)
        state.draw_cards(1)
        state.add_log("Production Push: {} damage + draw.".format(_dmg))

    @register_effect("refactor")
    def _eff_refactor(state, source, target):
        state.cancel_next_attack_set()

    @register_effect("kernel_patch")
    def _eff_kernel_patch(state, source, target):
        state.gain_energy(2)
        state.draw_cards(2)

    @register_effect("hotfix")
    def _eff_hotfix(state, source, target):
        ## cards_played_this_turn is incremented before the effect resolves,
        ## so it already counts Hotfix itself — 3rd card played => >= 3.
        _dmg = 13 if state.cards_played_this_turn >= 3 else 5
        state.deal_damage(target, _dmg)
        state.draw_cards(1)

    @register_effect("ship_it")
    def _eff_ship_it(state, source, target):
        _skills = sum(1 for c in state.hand if CARD_LIBRARY.get(c, {}).get("type") == "Skill")
        _e = min(3, _skills)
        state.gain_energy(_e)
        state.add_log("Ship It: {} Skills in hand -> +{} energy.".format(_skills, _e))

    @register_effect("code_review")
    def _eff_code_review(state, source, target):
        ## Auto-exhaust the leftmost OTHER card (no in-battle selection UI).
        _pool = [c for c in state.hand if c != "code_review"]
        if _pool:
            state.exhaust(_pool[0])
            state.add_log("Code Review: exhausted {}.".format(CARD_LIBRARY.get(_pool[0], {}).get("name", _pool[0])))
        state.draw_cards(2)
        state.gain_block(source, 3)

    @register_effect("crunch_time")
    def _eff_crunch_time(state, source, target):
        ## 4 per card played this turn — counter already includes this card.
        _n = state.cards_played_this_turn
        state.deal_damage(target, 4 * _n)
        state.add_log("Crunch Time: {} cards played -> {} damage.".format(_n, 4 * _n))

    ## ---------------------------------------------------------------------------
    ## NEUTRAL
    ## ---------------------------------------------------------------------------

    @register_effect("gut_punch")
    def _eff_gut_punch(state, source, target):
        state.deal_damage(target, 9)

    @register_effect("body_check")
    def _eff_body_check(state, source, target):
        state.deal_damage(target, 16)

    @register_effect("breath_test")
    def _eff_breath_test(state, source, target):
        state.buff(source, "next_attack_reduction", 6)

    @register_effect("killing_blow")
    def _eff_killing_blow(state, source, target):
        state.deal_damage(target, 14)
        if state.enemy_max_hp > 0 and state.enemy_hp > 0 and state.enemy_hp * 2 < state.enemy_max_hp:
            state.deal_damage(target, 14)
            state.add_log("[[Killing Blow]: execution — second hit lands.")

    @register_effect("last_stand")
    def _eff_last_stand(state, source, target):
        state.deal_damage(target, 18)
        if state.player_max_hp > 0 and state.player_hp * 2 < state.player_max_hp:
            state.draw_cards(2)
            state.add_log("[[Last Stand]: low HP — draw 2.")

    @register_effect("cuff_em")
    def _eff_cuff_em(state, source, target):
        state.skip_attacks(1)

    ## ---------------------------------------------------------------------------
    ## ARCHETYPE: CORRUPTION — Rage cards. Each play deals heavy damage with a
    ## self-corrupting cost AND +2 Hatred (routed through gain_hatred so See Red
    ## fires). Permanent in deck until removed by the Fixer.
    ## ---------------------------------------------------------------------------

    import random as _rage_rand

    def _other_cards_in_hand(state, self_id):
        """Hand cards excluding the card currently resolving (so a Rage card
        never discards/exhausts itself when it triggers from hand)."""
        try:
            return [cid for cid in state.hand if cid != self_id]
        except Exception:
            return []

    @register_effect("outburst")
    def _eff_outburst(state, source, target):
        ## Threshold-40 Rage. Self-damage bypasses block (your guard stops the
        ## enemy, not your own outburst). Floor-clamped to leave 1 HP min.
        state.deal_damage(target, 14)
        state.deal_damage(source, 6, bypass_block=True)
        state.gain_hatred(2)
        state.add_log("Outburst: 14 damage. -6 HP. +2 Hatred.")

    @register_effect("tunnel_vision")
    def _eff_tunnel_vision(state, source, target):
        ## Threshold-60 Rage. One random card from hand OR draw pile is
        ## discarded — rage clouds judgment.
        state.deal_damage(target, 16)
        _candidates = _other_cards_in_hand(state, "tunnel_vision") + list(state.draw_pile)
        if _candidates:
            _victim = _rage_rand.choice(_candidates)
            if _victim in state.hand:
                state.discard(_victim)
            elif _victim in state.draw_pile:
                state.draw_pile.remove(_victim)
                state.discard_pile.append(_victim)
            _name = CARD_LIBRARY.get(_victim, {}).get("name", _victim)
            state.add_log("Tunnel Vision: discarded {}.".format(_name))
        state.gain_hatred(2)

    @register_effect("snap")
    def _eff_snap(state, source, target):
        ## Threshold-80 Rage. Free swing — a random hand card is exhausted FOR
        ## THIS FIGHT only (no run-deck removal).
        state.deal_damage(target, 10)
        _others = _other_cards_in_hand(state, "snap")
        if _others:
            _victim = _rage_rand.choice(_others)
            state.exhaust(_victim)
            _name = CARD_LIBRARY.get(_victim, {}).get("name", _victim)
            state.add_log("Snap: exhausted {} for this fight.".format(_name))
        state.gain_hatred(2)

    @register_effect("compromise")
    def _eff_compromise(state, source, target):
        ## Defense-in-depth no-op — Compromise carries unplayable=True so this
        ## never resolves in normal play.
        state.add_log("Compromise: it's a dead card. It does nothing.")

    ## ---------------------------------------------------------------------------
    ## CLASS STARTERS / EVENT / BOSS / ARC / STORY — out of scope, unchanged.
    ## ---------------------------------------------------------------------------

    @register_effect("read_him")
    def _eff_read_him(state, source, target):
        state.gain_block(source, 6)
        state.draw_cards(2)

    @register_effect("stack_up")
    def _eff_stack_up(state, source, target):
        state.gain_energy(2)
        state.buff(source, "crash_next_turn", True)

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

    @register_effect("mirror")
    def _eff_mirror(state, source, target):
        if state.buffs.get("mirror_cooldown", 0) > 0:
            state.add_log("Mirror is on cooldown ({} turns).".format(state.buffs["mirror_cooldown"]))
            return
        state.buff(source, "mirror_next", True)
        state.buff(source, "mirror_armed_for_counter", True)

    @register_effect("paragraph_4b")
    def _eff_paragraph_4b(state, source, target):
        state.deal_damage(target, 40)
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
        state.buff(source, "job_offer_armed", True)

    @register_effect("stoic_refactor")
    def _eff_stoic_refactor(state, source, target):
        state.buff(source, "mental_dr_50", True)

    @register_effect("empaths_insight")
    def _eff_empaths_insight(state, source, target):
        state.buff(source, "insight_block", 5)
        state.buff(source, "insight_turns_left", 3)

    @register_effect("tell")
    def _eff_tell(state, source, target):
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

    @register_effect("the_dossier")
    def _eff_the_dossier(state, source, target):
        ic = state.current_intent()
        if ic and any(t in ic.get("tags", []) for t in ("emotional", "guilt")):
            state.cancel_next_attack_set()
            state.add_log("[[The Dossier]: 'emotional' attack disabled by leverage.")
        state.deal_damage(target, 25)

    @register_effect("the_compound")
    def _eff_the_compound(state, source, target):
        _e = state.energy + 1
        state.deal_damage(target, _e * 10)
        state.deal_damage(source, 8, bypass_block=True)
        state.add_log("[[The Compound]: {}E spent -> {} dmg, -8 HP.".format(_e, _e * 10))

    @register_effect("took_the_heat")
    def _eff_took_the_heat(state, source, target):
        state.gain_block(source, 10)
        state.draw_cards(1)
        state.buff(source, "took_the_heat_armed", True)

    ## ---------------------------------------------------------------------------
    ## STATUS / CURSE — enemy-injected, all exhaust on play.
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
    ## UPGRADED (`_plus`) EFFECTS — paired with the register_upgrade table in
    ## card_library.rpy. New-archetype cards get their `_plus` effects in a
    ## later pass; status / rage / compromise cards are non-upgradeable.
    ## ---------------------------------------------------------------------------

    @register_effect("strike_plus")
    def _eff_strike_plus(state, source, target):
        state.deal_damage(target, 9)

    @register_effect("defend_plus")
    def _eff_defend_plus(state, source, target):
        state.gain_block(source, 8)

    @register_effect("heavy_set_plus")
    def _eff_heavy_set_plus(state, source, target):
        dmg = 8 + (stats.pcr_hatred // 8) if stats else 8
        state.deal_damage(target, dmg)
        state.add_log("Heavy Set+: {} damage (scaled by Hatred).".format(dmg))

    @register_effect("bracing_plus")
    def _eff_bracing_plus(state, source, target):
        state.gain_block(source, 11)

    @register_effect("backup_plus")
    def _eff_backup_plus(state, source, target):
        state.gain_block(source, 14)

    @register_effect("chain_of_command_plus")
    def _eff_chain_of_command_plus(state, source, target):
        state.gain_block(source, 11)
        state.draw_cards(1)

    @register_effect("iron_stance_plus")
    def _eff_iron_stance_plus(state, source, target):
        state.gain_block(source, 16)
        state.buff(source, "iron_stance_active", True)

    @register_effect("bouncer_door_plus")
    def _eff_bouncer_door_plus(state, source, target):
        state.gain_block(source, 22)
        state.buff(source, "single_retaliate_dmg", 10)

    @register_effect("stoic_anchor_plus")
    def _eff_stoic_anchor_plus(state, source, target):
        state.buff(source, "stoic_anchor_block", 3)
        state.buff(source, "stoic_anchor_heal", 2)

    @register_effect("second_wind_plus")
    def _eff_second_wind_plus(state, source, target):
        state.heal(source, 8)
        state.gain_block(source, 13)

    @register_effect("quick_compile_plus")
    def _eff_quick_compile_plus(state, source, target):
        state.draw_cards(2)

    @register_effect("pair_program_plus")
    def _eff_pair_program_plus(state, source, target):
        state.gain_block(source, 6)
        state.draw_cards(1)

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
        state.add_log("Unit Test+: {} Skills in hand -> {} block.".format(_skills, 8 * _skills))

    @register_effect("production_push_plus")
    def _eff_production_push_plus(state, source, target):
        _dmg = 20 if state.skill_played_this_turn else 11
        state.deal_damage(target, _dmg)
        state.draw_cards(1)
        state.add_log("Production Push+: {} damage + draw.".format(_dmg))

    @register_effect("kernel_patch_plus")
    def _eff_kernel_patch_plus(state, source, target):
        state.gain_energy(2)
        state.draw_cards(3)

    @register_effect("gut_punch_plus")
    def _eff_gut_punch_plus(state, source, target):
        state.deal_damage(target, 11)

    @register_effect("body_check_plus")
    def _eff_body_check_plus(state, source, target):
        state.deal_damage(target, 20)

    @register_effect("breath_test_plus")
    def _eff_breath_test_plus(state, source, target):
        state.buff(source, "next_attack_reduction", 8)

    @register_effect("killing_blow_plus")
    def _eff_killing_blow_plus(state, source, target):
        state.deal_damage(target, 16)
        if state.enemy_max_hp > 0 and state.enemy_hp > 0 and state.enemy_hp * 2 < state.enemy_max_hp:
            state.deal_damage(target, 16)
            state.add_log("[[Killing Blow+]: execution — second hit lands.")

    @register_effect("last_stand_plus")
    def _eff_last_stand_plus(state, source, target):
        state.deal_damage(target, 22)
        if state.player_max_hp > 0 and state.player_hp * 2 < state.player_max_hp:
            state.draw_cards(2)
            state.add_log("[[Last Stand+]: low HP — draw 2.")

    @register_effect("read_him_plus")
    def _eff_read_him_plus(state, source, target):
        state.gain_block(source, 9)
        state.draw_cards(2)

    @register_effect("stack_up_plus")
    def _eff_stack_up_plus(state, source, target):
        state.gain_energy(2)
        state.draw_cards(1)
        state.buff(source, "crash_next_turn", True)

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
        state.buff(source, "mirror_next", True)
        state.buff(source, "mirror_armed_for_counter", True)
        state.gain_block(source, 5)

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
        state.buff(source, "mental_dr_50", True)
        state.buff(source, "special_dr_50", True)

    @register_effect("empaths_insight_plus")
    def _eff_empaths_insight_plus(state, source, target):
        state.buff(source, "insight_block", 6)
        state.buff(source, "insight_turns_left", 4)

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
        _e = state.energy + 1
        state.deal_damage(target, _e * 12)
        state.deal_damage(source, 12, bypass_block=True)
        state.add_log("[[The Compound+]: {}E spent -> {} dmg, -12 HP.".format(_e, _e * 12))

    @register_effect("took_the_heat_plus")
    def _eff_took_the_heat_plus(state, source, target):
        state.gain_block(source, 13)
        state.draw_cards(1)
        state.buff(source, "took_the_heat_armed", True)

    ## ---------------------------------------------------------------------------
    ## NEW-ARCHETYPE `_plus` EFFECTS. See Red / Thick Skull / Iron Posture
    ## upgrade to cost 0 and reuse their base effect — no `_plus` effect needed.
    ## ---------------------------------------------------------------------------

    @register_effect("provoke_plus")
    def _eff_provoke_plus(state, source, target):
        state.gain_hatred(8)
        state.draw_cards(2)

    @register_effect("knuckle_down_plus")
    def _eff_knuckle_down_plus(state, source, target):
        state.deal_damage(target, 18)
        state.gain_hatred(6)

    @register_effect("snap_decision_plus")
    def _eff_snap_decision_plus(state, source, target):
        _h = stats.pcr_hatred if stats else 0
        _dmg = 24 if _h >= 60 else 12
        state.deal_damage(target, _dmg)
        state.add_log("Snap Decision+: {} damage (Hatred {}).".format(_dmg, _h))

    @register_effect("red_mist_plus")
    def _eff_red_mist_plus(state, source, target):
        state.deal_damage(target, 10)
        state.deal_damage(target, 10)
        state.gain_hatred(4)

    @register_effect("breaking_point_plus")
    def _eff_breaking_point_plus(state, source, target):
        _h = stats.pcr_hatred if stats else 0
        _dmg = 13 + _h // 3
        state.deal_damage(target, _dmg)
        state.add_log("Breaking Point+: {} damage (13 + Hatred/3).".format(_dmg))

    @register_effect("bottled_rage_plus")
    def _eff_bottled_rage_plus(state, source, target):
        ## Strict upgrade over base: +6 flat damage, identical 25 Hatred dump.
        _dmg = ((stats.pcr_hatred // 2) if stats else 0) + 6
        state.deal_damage(target, _dmg)
        state.gain_hatred(-25)
        state.add_log("Bottled Rage+: {} damage. -25 Hatred.".format(_dmg))

    @register_effect("adrenaline_dump_plus")
    def _eff_adrenaline_dump_plus(state, source, target):
        state.gain_hatred(-10)
        state.gain_energy(2)
        state.draw_cards(1)

    @register_effect("last_nerve_plus")
    def _eff_last_nerve_plus(state, source, target):
        state.deal_damage(target, 9)
        if any(CARD_LIBRARY.get(c, {}).get("is_rage") for c in state.hand):
            state.draw_cards(1)
            state.add_log("Last Nerve+: a Rage card in hand — draw 1.")

    @register_effect("embrace_it_plus")
    def _eff_embrace_it_plus(state, source, target):
        _rage = next((c for c in state.hand if CARD_LIBRARY.get(c, {}).get("is_rage")), None)
        if _rage is not None:
            state.exhaust(_rage)
            state.add_log("Embrace It+: exhausted {}.".format(CARD_LIBRARY.get(_rage, {}).get("name", _rage)))
        state.gain_block(source, 20)
        state.draw_cards(2)

    @register_effect("counterweight_plus")
    def _eff_counterweight_plus(state, source, target):
        _dmg = min(state.player_block, COUNTERWEIGHT_CAP) + 4
        state.deal_damage(target, _dmg)
        state.add_log("Counterweight+: {} damage (block {} + 4).".format(_dmg, state.player_block))

    @register_effect("hold_the_line_plus")
    def _eff_hold_the_line_plus(state, source, target):
        _skills = sum(1 for c in state.hand if CARD_LIBRARY.get(c, {}).get("type") == "Skill")
        state.gain_block(source, 3 * _skills)
        state.add_log("Hold the Line+: {} Skills in hand -> {} block.".format(_skills, 3 * _skills))

    @register_effect("brick_wall_plus")
    def _eff_brick_wall_plus(state, source, target):
        state.deal_damage(target, 12)
        state.gain_block(source, state.last_damage_to_enemy)

    @register_effect("hotfix_plus")
    def _eff_hotfix_plus(state, source, target):
        _dmg = 17 if state.cards_played_this_turn >= 3 else 8
        state.deal_damage(target, _dmg)
        state.draw_cards(1)

    @register_effect("ship_it_plus")
    def _eff_ship_it_plus(state, source, target):
        _skills = sum(1 for c in state.hand if CARD_LIBRARY.get(c, {}).get("type") == "Skill")
        _e = min(3, _skills)
        state.gain_energy(_e)
        state.draw_cards(1)
        state.add_log("Ship It+: {} Skills in hand -> +{} energy, draw 1.".format(_skills, _e))

    @register_effect("code_review_plus")
    def _eff_code_review_plus(state, source, target):
        _pool = [c for c in state.hand if c != "code_review_plus"]
        if _pool:
            state.exhaust(_pool[0])
            state.add_log("Code Review+: exhausted {}.".format(CARD_LIBRARY.get(_pool[0], {}).get("name", _pool[0])))
        state.draw_cards(2)
        state.gain_block(source, 6)

    @register_effect("crunch_time_plus")
    def _eff_crunch_time_plus(state, source, target):
        _n = state.cards_played_this_turn
        state.deal_damage(target, 5 * _n)
        state.add_log("Crunch Time+: {} cards played -> {} damage.".format(_n, 5 * _n))
