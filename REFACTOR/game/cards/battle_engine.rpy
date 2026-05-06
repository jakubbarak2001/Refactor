################################################################################
## REFACTOR — Battle Engine (Phase 1.6)
##
## BattleState owns all combat state for the Colonel deck-fight.
## Turn structure:
##   Player turn:
##     - Reset player_block to 0 (block doesn't carry between turns)
##     - Apply start-of-turn buffs (block_next_turn etc)
##     - Refill energy to max_energy
##     - Reveal upcoming colonel intent
##     - Draw 5 cards
##     - Player plays cards (interactive — battle_screen)
##     - Player ends turn
##   Enemy turn:
##     - Resolve current intent (deal damage / gain block / etc)
##     - Apply player counter-cards (paragraph_4b auto-counters training_debt, etc)
##     - Advance intent index
##   Loop until is_over()
##
## State is a singleton stored in `battle_state` at module scope, so the
## battle screen can read it and the card-effect functions can mutate it.
################################################################################

init python:

    import random as _battle_rand

    class BattleState(object):
        """Singleton-style state for the deck-based Colonel fight."""

        def __init__(self):
            self.player_hp = 80
            self.player_max_hp = 80
            self.player_block = 0

            self.enemy_hp = 100
            self.enemy_max_hp = 100
            self.enemy_block = 0

            self.energy = 3
            self.max_energy = 3
            self.starting_block = 0  ## job_offer power adds to this

            self.hand = []
            self.draw_pile = []
            self.discard_pile = []
            self.exhaust_pile = []

            self.intent_queue = []        ## list[colonel_card_id]
            self.intent_index = 0          ## current intent the colonel will play
            self.intent_revealed = 1       ## how many ahead the player can see

            self.cancel_next_attack = False
            self.skip_attack_count = 0
            self.buffs = {}                ## key -> True or numeric

            self.turn = 0
            self.log = []
            self.over = None               ## None / "victory" / "defeat"

            ## Animation hooks for the screen (set by play_card / end_turn)
            self.last_card_played = None
            self.last_intent_resolved = None
            self.last_damage_to_player = 0
            self.last_damage_to_enemy = 0

        ## ---------------- LOG ----------------
        def add_log(self, msg):
            self.log.append(msg)
            ## Keep log capped to last 12 entries to bound memory and screen size
            if len(self.log) > 12:
                self.log = self.log[-12:]

        ## ---------------- DAMAGE / BLOCK ----------------
        def deal_damage(self, target, amount):
            """target: 'player' | 'enemy' (or string aliases)"""
            if amount <= 0:
                return
            if target == "enemy":
                ## Apply enemy block first
                absorbed = min(self.enemy_block, amount)
                self.enemy_block -= absorbed
                actual = amount - absorbed
                self.enemy_hp -= actual
                self.last_damage_to_enemy = actual
                self.add_log("Colonel takes {} damage.".format(actual))
                if self.enemy_hp <= 0:
                    self.enemy_hp = 0
                    self.over = "victory"
            elif target == "player":
                ## Apply mental damage reduction if buff active
                if self.buffs.get("mental_dr_50") and self._intent_has_tag("mental"):
                    amount = max(1, amount // 2)
                absorbed = min(self.player_block, amount)
                self.player_block -= absorbed
                actual = amount - absorbed
                self.player_hp -= actual
                self.last_damage_to_player = actual
                self.add_log("JB takes {} damage.".format(actual))
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.over = "defeat"

        def gain_block(self, target, amount):
            if target == "enemy":
                self.enemy_block += amount
                self.add_log("Colonel gains {} block.".format(amount))
            else:
                self.player_block += amount
                self.add_log("JB gains {} block.".format(amount))

        def heal(self, target, amount):
            if target == "enemy":
                self.enemy_hp = min(self.enemy_max_hp, self.enemy_hp + amount)
            else:
                self.player_hp = min(self.player_max_hp, self.player_hp + amount)
                self.add_log("JB heals {} HP.".format(amount))

        ## ---------------- DECK MECHANICS ----------------
        def draw_cards(self, n):
            for _ in range(n):
                if not self.draw_pile:
                    if not self.discard_pile:
                        return  ## empty everywhere
                    self.draw_pile = list(self.discard_pile)
                    _battle_rand.shuffle(self.draw_pile)
                    self.discard_pile = []
                if self.draw_pile:
                    self.hand.append(self.draw_pile.pop())

        def discard(self, card_id):
            if card_id in self.hand:
                self.hand.remove(card_id)
            self.discard_pile.append(card_id)

        def exhaust(self, card_id):
            if card_id in self.hand:
                self.hand.remove(card_id)
            self.exhaust_pile.append(card_id)

        def discard_hand(self):
            self.discard_pile.extend(self.hand)
            self.hand = []

        ## ---------------- ENERGY ----------------
        def gain_energy(self, n):
            self.energy += n

        def spend_energy(self, n):
            self.energy = max(0, self.energy - n)

        ## ---------------- INTENT MANAGEMENT ----------------
        def current_intent(self):
            if self.intent_index >= len(self.intent_queue):
                return None
            return ENEMY_DECK_LIBRARY.get(self.intent_queue[self.intent_index])

        def peek_intents(self, n):
            self.intent_revealed = max(self.intent_revealed, n)

        def cancel_next_attack_set(self):
            self.cancel_next_attack = True

        def skip_attacks(self, n):
            self.skip_attack_count += n

        def buff(self, target, key, value):
            ## Single-side buff dict — target is 'player' or 'enemy'.
            ## We currently only track player-side buffs.
            if isinstance(value, bool):
                self.buffs[key] = value
            else:
                self.buffs[key] = self.buffs.get(key, 0) + value

        def _intent_has_tag(self, tag):
            ic = self.current_intent()
            return ic is not None and tag in ic.get("tags", [])

        ## ---------------- STATE PROBES ----------------
        def is_over(self):
            return self.over

        def hand_playable(self, card_id):
            """Returns (True, '') or (False, reason)."""
            c = CARD_LIBRARY.get(card_id)
            if c is None:
                return False, "Unknown card."
            cost = c.get("cost", 0)
            if isinstance(cost, int) and cost > self.energy:
                return False, "Not enough energy."
            ## Mirror has a per-fight cooldown after each use
            if card_id == "mirror" and self.buffs.get("mirror_cooldown", 0) > 0:
                return False, "Mirror on cooldown ({} turns).".format(self.buffs["mirror_cooldown"])
            return True, ""


    ## Module-level singleton (None when no battle in progress)
    battle_state = None


    ## ---------------- ENGINE FUNCTIONS ----------------

    def battle_init():
        """Build a fresh BattleState for the colonel fight. Reads stats / player_deck / difficulty."""
        global battle_state
        bs = BattleState()

        ## Player HP by class
        if stats and stats.player_class == "bodybuilder":
            bs.player_max_hp = 115
            bs.player_hp = 115
            ## SOMA bonus: +1 starting block per turn for every 2 SOMA stacks
            _soma = getattr(store, 'bb_soma', 0)
            if _soma >= 2:
                bs.buffs["stoic_anchor_block"] = bs.buffs.get("stoic_anchor_block", 0) + (_soma // 2)
                bs.add_log("[[SOMA x{}]]: +{} starting block per turn.".format(_soma, _soma // 2))
            bs.buffs["presence_charges"] = 3
            bs.add_log("[[PRESENCE x3]]: Block you don't have to play for. The room is smaller now. He has to plan around you.")
        elif stats and stats.player_class == "dark_empath":
            bs.player_max_hp = 75
            bs.player_hp = 75
            ## READ baseline: peek 2 intents at fight start; PROFILES adds further depth.
            bs.peek_intents(2)
            ## PROFILES bonus: +1 intent peek per profile read 2+ times.
            ## Threshold 2 (was 3) is reachable in a 30-day run with 8 cold reads.
            _de_deep_profiles = sum(1 for n, c in getattr(store, 'de_profiles', {}).items() if c >= 2)
            if _de_deep_profiles > 0:
                bs.peek_intents(1 + _de_deep_profiles)
                bs.add_log("[[PROFILES x{}]]: peek depth {}.".format(_de_deep_profiles, 1 + _de_deep_profiles))
            bs.buffs["read_charges"] = 3
            bs.add_log("[[READ x3]]: One free look at what he's about to do. He has tells. He's never had to hide them from you before.")
        elif stats and stats.player_class == "biohacker":
            bs.player_max_hp = 80
            bs.player_hp = 80
            ## BH max-energy gate: dose-counter check (3+ total nootropic uses across all tiers).
            if sum(getattr(store, 'nootropic_uses', [0,0,0,0,0])) >= 3:
                bs.max_energy = 4
                bs.add_log("[[STACK]]: dose count >= 3. +1 max energy.")
            bs.buffs["kick_charges"] = 3
            bs.add_log("[[KICK x3]]: The compound kicking in. Each turn it's running, you draw one extra card. He's still finishing the sentence; you've already chosen.")
        else:
            ## No class set (shouldn't happen in normal play) — safe defaults.
            bs.player_max_hp = 80
            bs.player_hp = 80

        ## Build draw pile from collected deck (full deck shuffled)
        if player_deck and player_deck.cards:
            bs.draw_pile = list(player_deck.cards)
            _battle_rand.shuffle(bs.draw_pile)

        ## Apply Power-card pre-fight buffs from collected deck
        ## (job_offer, stoic_refactor are Powers — they activate at battle start)
        for cid in list(bs.draw_pile):
            c = CARD_LIBRARY.get(cid, {})
            if c.get("type") == "Power":
                ## Power cards activate immediately and are removed from the deck
                eff_id = c.get("effect")
                if eff_id and eff_id in card_effects:
                    try:
                        card_effects[eff_id](bs, "player", "enemy")
                    except Exception:
                        pass
                bs.exhaust_pile.append(cid)
                bs.draw_pile.remove(cid)

        ## Build colonel deck per difficulty
        bs.intent_queue = build_colonel_deck()

        ## Colonel HP scales with deck size (Easy/Hard/Insane/Ultra → 80/100/130/160)
        deck_size = len(bs.intent_queue)
        if deck_size <= 5:
            bs.enemy_max_hp = 80
        elif deck_size <= 7:
            bs.enemy_max_hp = 100
        elif deck_size <= 9:
            bs.enemy_max_hp = 130
        else:
            bs.enemy_max_hp = 160
        bs.enemy_hp = bs.enemy_max_hp

        bs.add_log("[[INIT]]: HP {}/{}  Enemy {}/{}  deck {}  hand 0".format(
            bs.player_hp, bs.player_max_hp, bs.enemy_hp, bs.enemy_max_hp, len(bs.draw_pile)))

        battle_state = bs
        return bs


    def battle_start_player_turn():
        """Begin a player turn — reset block, refill energy, draw 5 cards."""
        bs = battle_state
        if bs is None or bs.is_over():
            return
        bs.turn += 1
        bs.player_block = bs.starting_block

        ## Apply start-of-turn buffs
        if bs.buffs.get("starting_block_+1"):
            bs.player_block += 1
        if bs.buffs.get("stoic_anchor_block"):
            bs.player_block += bs.buffs["stoic_anchor_block"]
        if bs.buffs.get("presence_charges", 0) > 0:
            bs.player_block += 3
            bs.buffs["presence_charges"] -= 1
        if bs.buffs.get("read_charges", 0) > 0:
            bs.peek_intents(bs.intent_revealed + 1)
            bs.buffs["read_charges"] -= 1
        if bs.buffs.get("vigil_next_turn_block"):
            bs.player_block += bs.buffs["vigil_next_turn_block"]
            bs.buffs["vigil_next_turn_block"] = 0  ## consume
        if bs.buffs.get("insight_turns_left", 0) > 0:
            bs.player_block += bs.buffs.get("insight_block", 0)
            bs.buffs["insight_turns_left"] -= 1
        if bs.buffs.get("block_next_turn"):
            bs.player_block += 999  ## flagged: full block this turn
            bs.buffs["block_next_turn"] = False  ## consume

        ## Tick down the mirror cooldown each turn (Mirror = DE-only rare).
        if bs.buffs.get("mirror_cooldown", 0) > 0:
            bs.buffs["mirror_cooldown"] -= 1
        if bs.buffs.get("skip_next_turn"):
            ## Player loses this turn — go straight to enemy
            bs.buffs["skip_next_turn"] = False
            bs.add_log("[[FLMod crash]]: you lose this turn.")
            battle_end_player_turn()
            return

        ## Refill energy (BH gets +1 if they took FLMod yesterday — already in player_max_hp logic)
        bs.energy = bs.max_energy

        ## FLModafinil ebb — peak passes, max energy reduced this turn only
        if bs.buffs.get("max_energy_penalty_next_turn", 0) > 0:
            _pen = bs.buffs["max_energy_penalty_next_turn"]
            bs.energy = max(0, bs.energy - _pen)
            bs.buffs["max_energy_penalty_next_turn"] = 0
            bs.add_log("[[FLMod ebb]]: -{} max energy this turn.".format(_pen))

        ## Stack-up crash — Biohacker pays for last turn's energy spike
        if bs.buffs.get("crash_next_turn"):
            bs.energy = max(0, bs.energy - 2)
            bs.buffs["crash_next_turn"] = False
            bs.add_log("[[Stack crash]]: the spike wears off. -2 energy this turn.")

        ## Draw 5 cards
        bs.draw_cards(5)

        if bs.buffs.get("kick_charges", 0) > 0:
            bs.draw_cards(1)
            bs.buffs["kick_charges"] -= 1

        bs.add_log("--- Turn {} ---".format(bs.turn))


    def battle_play_card(card_id):
        """Play a card from hand. Returns True if played, False if not playable."""
        bs = battle_state
        if bs is None or bs.is_over():
            return False
        if card_id not in bs.hand:
            return False
        ok, reason = bs.hand_playable(card_id)
        if not ok:
            bs.add_log("Cannot play: " + reason)
            return False

        c = CARD_LIBRARY.get(card_id, {})
        cost = c.get("cost", 0)
        if isinstance(cost, int):
            bs.spend_energy(cost)

        ## Resolve effect
        eff_id = c.get("effect")
        if eff_id and eff_id in card_effects:
            try:
                card_effects[eff_id](bs, "player", "enemy")
            except Exception as e:
                bs.add_log("Effect error: {}".format(e))

        bs.last_card_played = card_id

        ## Move to discard or exhaust
        if c.get("exhaust"):
            bs.exhaust(card_id)
        else:
            bs.discard(card_id)

        ## Apply double_next_attack buff (Personal Record)
        if c.get("type") == "Attack" and bs.buffs.get("double_next_attack"):
            bs.buffs["double_next_attack"] = False
            ## The attack already resolved at base damage; apply the doubling as bonus
            eff_id = c.get("effect")
            if eff_id and eff_id in card_effects:
                try:
                    card_effects[eff_id](bs, "player", "enemy")
                except Exception:
                    pass
            bs.add_log("Personal Record: doubled.")

        return True


    def battle_end_player_turn():
        """Player ends their turn — discard hand, resolve enemy intent."""
        bs = battle_state
        if bs is None or bs.is_over():
            return

        ## Discard remaining hand
        bs.discard_hand()

        ## Enemy phase — resolve current intent
        battle_resolve_enemy()
        if bs.is_over():
            return

        ## Start next player turn
        battle_start_player_turn()


    def battle_resolve_enemy():
        """Resolve the colonel's current intent and advance the queue."""
        bs = battle_state

        ## Reset damage trackers — fresh intent, fresh accounting
        bs.last_damage_to_player = 0
        bs.last_damage_to_enemy = 0

        ## Brawl bleed — applied at the START of each colonel intent if active
        if bs.buffs.get("bleed_turns", 0) > 0:
            _bleed = bs.buffs.get("bleed_dmg", 0)
            if _bleed > 0:
                bs.deal_damage("enemy", _bleed)
                bs.add_log("[[Bleed]]: colonel takes {} dmg from open wound.".format(_bleed))
            bs.buffs["bleed_turns"] -= 1
            if bs.buffs["bleed_turns"] <= 0:
                bs.buffs["bleed_dmg"] = 0
            if bs.is_over():
                return

        ## Skip attacks if "Algorithm" was played
        if bs.skip_attack_count > 0:
            bs.skip_attack_count -= 1
            ic = bs.current_intent()
            if ic:
                bs.add_log("[[Algorithm]]: skipped colonel's '{}'.".format(ic.get("name", "?")))
            bs.intent_index += 1
            return

        ic = bs.current_intent()
        if ic is None:
            ## Out of cards — colonel is exhausted, treat as victory if HP <= 25
            if bs.enemy_hp <= 25:
                bs.over = "victory"
                bs.add_log("Colonel runs out of arguments. You win.")
            else:
                ## Reshuffle: rebuild deck and continue
                bs.intent_queue = build_colonel_deck()
                bs.intent_index = 0
                ic = bs.current_intent()
                if ic is None:
                    return

        ## Cancellation check
        if bs.cancel_next_attack:
            bs.cancel_next_attack = False
            bs.add_log("[[Refactor]]: cancelled colonel's '{}'.".format(ic.get("name", "?")))
            bs.intent_index += 1
            return

        ## Class immunity
        if stats and stats.player_class in ic.get("immunity", []):
            bs.add_log("[[{}]]: '{}' bounces off you.".format(stats.player_class.upper(), ic.get("name", "?")))
            bs.intent_index += 1
            return

        ## Conditional counters (player-side buffs and stat thresholds)
        damage_reduction = 0
        for cond, mod in ic.get("counter", {}).items():
            if _check_battle_condition(bs, cond):
                if mod.get("negate"):
                    bs.add_log("[[{}]]: '{}' is negated.".format(cond.upper(), ic.get("name", "?")))
                    if mod.get("damage_to_self"):
                        bs.deal_damage("enemy", mod["damage_to_self"])
                    bs.intent_index += 1
                    return
                damage_reduction += mod.get("reduce_damage", 0)

        ## Mirror buff — return next attack at double damage instead of taking it
        if bs.buffs.get("mirror_next") and ic.get("intent") in ("attack", "compound"):
            bs.buffs["mirror_next"] = False
            ## Set cooldown so Mirror can't fire again for 2 player turns
            bs.buffs["mirror_cooldown"] = 2
            base = ic.get("value", 0) * (ic.get("value2", 1) if ic.get("intent") == "compound" else 1)
            bs.deal_damage("enemy", base * 2)
            bs.add_log("[[Mirror]]: '{}' bounced for {} dmg. (2-turn cooldown.)".format(ic.get("name", "?"), base * 2))
            bs.intent_index += 1
            return

        ## Reframe buff — convert next attack into block
        if bs.buffs.get("reframe_next") and ic.get("intent") in ("attack", "compound"):
            bs.buffs["reframe_next"] = False
            base = ic.get("value", 0)
            bs.gain_block("player", base)
            bs.add_log("[[Reframe]]: '{}' reframed into +{} block.".format(ic.get("name", "?"), base))
            bs.intent_index += 1
            return

        ## Frame Trap (DE) — additional one-shot damage reduction on the next attack
        if bs.buffs.get("next_attack_reduction", 0) > 0:
            damage_reduction += bs.buffs["next_attack_reduction"]
            bs.buffs["next_attack_reduction"] = 0
            bs.add_log("[[Frame Trap]]: attack softened.")

        ## Resolve intent by type
        intent_type = ic.get("intent", "attack")
        bs.last_intent_resolved = ic["id"]

        if intent_type == "attack":
            dmg = max(1 if ic.get("value", 0) > 0 else 0, ic.get("value", 0) - damage_reduction)
            bs.deal_damage("player", dmg)
        elif intent_type == "compound":
            hits = ic.get("value2", 1)
            per_hit = max(1 if ic.get("value", 0) > 0 else 0, ic.get("value", 0) - (damage_reduction // max(1, hits)))
            for _i in range(hits):
                if bs.is_over():
                    break
                bs.deal_damage("player", per_hit)
        elif intent_type == "block":
            bs.gain_block("enemy", ic.get("value", 0))
        elif intent_type == "buff":
            ## Cold Stare — add to a self-attack-bonus stack
            bs.buffs["enemy_attack_bonus"] = bs.buffs.get("enemy_attack_bonus", 0) + ic.get("value", 0)
        elif intent_type == "debuff":
            bs.buffs["player_draw_penalty"] = bs.buffs.get("player_draw_penalty", 0) + ic.get("value", 1)

        ## Apply enemy_attack_bonus to attacks
        if intent_type == "attack" and bs.buffs.get("enemy_attack_bonus"):
            bonus = bs.buffs["enemy_attack_bonus"]
            bs.buffs["enemy_attack_bonus"] = 0
            bs.deal_damage("player", bonus)
            bs.add_log("Pressure bonus: +{} damage.".format(bonus))

        ## Stoic Anchor heal-on-hit
        if bs.buffs.get("stoic_anchor_heal") and bs.last_damage_to_player > 0:
            bs.heal("player", bs.buffs["stoic_anchor_heal"])

        ## Iron Stance retaliate-on-hit (BB) — scales with turn count.
        ## Turn 1: 4 dmg. Turn 5: 12. Turn 10: 22. Rewards surviving longer.
        ## Vladek's Form (BB arc reward) doubles the retaliate value.
        if bs.buffs.get("iron_stance_active") and bs.last_damage_to_player > 0:
            _retaliate = 4 + (max(1, bs.turn) - 1) * 2
            if bs.buffs.get("vladeks_active"):
                _retaliate *= 2
            bs.deal_damage("enemy", _retaliate)
            _suffix = " [[Vladek's Form: doubled]]" if bs.buffs.get("vladeks_active") else ""
            bs.add_log("[[Iron Stance]]: retaliated for {} dmg (turn {}).{}".format(_retaliate, bs.turn, _suffix))

        ## Iron Body single-shot retaliate (BB common) — fires once on next hit
        if bs.buffs.get("single_retaliate_dmg", 0) > 0 and bs.last_damage_to_player > 0:
            _sr = bs.buffs["single_retaliate_dmg"]
            bs.buffs["single_retaliate_dmg"] = 0
            bs.deal_damage("enemy", _sr)
            bs.add_log("[[Iron Body]]: retaliated for {} dmg.".format(_sr))

        bs.intent_index += 1


    def _check_battle_condition(bs, cond):
        """Resolve a counter condition like 'card_paragraph_4b', 'money_gte_200000'."""
        if cond.startswith("card_"):
            ## Was this card played this turn? Use last_card_played.
            return bs.last_card_played == cond[5:]
        if cond.startswith("buff_"):
            return bool(bs.buffs.get(cond[5:]))
        if cond.startswith("money_gte_"):
            try:
                threshold = int(cond[len("money_gte_"):])
                return stats is not None and stats.available_money >= threshold
            except ValueError:
                return False
        if cond.startswith("coding_skill_gte_"):
            try:
                threshold = int(cond[len("coding_skill_gte_"):])
                return stats is not None and stats.coding_skill >= threshold
            except ValueError:
                return False
        return False


    def battle_finish():
        """Tear down — clear singleton."""
        global battle_state
        battle_state = None


    ## ---------------- BATTLE OUTCOME ----------------

    def battle_outcome():
        """Returns 'victory_perfect' / 'victory_pyrrhic' / 'victory_close' / 'defeat'."""
        bs = battle_state
        if bs is None:
            return "defeat"
        if bs.over == "defeat":
            return "defeat"
        if bs.over == "victory":
            ratio = bs.player_hp / float(max(1, bs.player_max_hp))
            if ratio >= 0.7:
                return "victory_perfect"
            elif ratio >= 0.3:
                return "victory_pyrrhic"
            else:
                return "victory_close"
        return "defeat"
