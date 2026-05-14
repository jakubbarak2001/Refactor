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

## Phase 1A diagnostic — toggle in console (`persistent.debug_battle = True`)
## to see [[DBG]: branch=...] traces and [[WARN]: 0-dmg attack] alerts in the
## battle log. Default off — never ships true.
default persistent.debug_battle = False

init python:

    import random as _battle_rand

    def _play_battle_sfx(name):
        """Phase A juice — play a battle SFX from audio/sfx/<name>.<ext>.

        Tries .ogg, then .mp3, then .wav. Silently skips if no matching
        file is present, so the engine works with or without the SFX
        library installed. The user can drop any supported format and
        it'll auto-wire.
        """
        for _ext in (".ogg", ".mp3", ".wav"):
            path = "audio/sfx/{}{}".format(name, _ext)
            if renpy.loadable(path):
                try:
                    renpy.sound.play(path)
                except Exception:
                    pass
                return

    class BattleState(object):
        """Singleton-style state for the deck-based Colonel fight."""

        def __init__(self):
            self.player_hp = 80
            self.player_max_hp = 80
            self.player_block = 0

            self.enemy_hp = 100
            self.enemy_max_hp = 100
            self.enemy_block = 0

            ## Enemy identity — populated by battle_init from ENEMY_LIBRARY.
            ## Defaults preserve Colonel behavior so any code path that builds
            ## a BattleState without going through battle_init still works.
            self.enemy_id = "colonel"
            self.enemy_name = "Colonel"
            self.enemy_sprite_id = "colonel"
            self.enemy_log_name = "Colonel"

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

            ## Phase A juice — per-hit timestamps drive the floating "-N"
            ## damage popups + hit-flash overlays in battle_screen.
            self.last_card_type = None       ## 'Attack' | 'Skill' | 'Power'
            self.last_enemy_hit_time = -1.0  ## game-runtime sec; -1 = never
            self.last_player_hit_time = -1.0

            ## Phase B/C/D juice — additional timestamps for energy pulse,
            ## turn-banner slide-in, victory/defeat fanfare reveal.
            self.last_energy_spend_time = -1.0
            self.last_turn_start_time = -1.0
            self.battle_end_time = -1.0      ## set when bs.over flips to victory/defeat
            self.last_player_block_gain_time = -1.0  ## block-text pulse on gain

            ## Damage-popup tag counters — incremented per hit so every show_screen
            ## call gets a unique _tag and Ren'Py mounts a fresh screen instance
            ## with a fresh ATL. Same-tag show_screen calls get optimized away.
            self._popup_enemy_seq = 0
            self._popup_player_seq = 0

            ## Permanent strength buff for the enemy (StS Strength analog).
            ## Adds to every attack/compound hit. Granted by 'strength' intent
            ## type. Persists for the fight; does NOT decay across turns.
            self.enemy_strength = 0

            ## Card-play restriction. None = no cap (default). When an intent
            ## sets cards_cap_next_turn, the start-of-turn handler latches it
            ## into current_turn_max_cards and resets cards_played_this_turn.
            self.cards_played_this_turn = 0
            self.current_turn_max_cards = None

        def __setstate__(self, state):
            """Restore from pickle. Backfill juice fields if missing so saves
            taken DURING a battle on an older build don't AttributeError
            on the first screen redraw after resume."""
            self.__dict__.update(state)
            if not hasattr(self, 'last_card_type'):
                self.last_card_type = None
            if not hasattr(self, 'last_damage_to_enemy'):
                self.last_damage_to_enemy = 0
            if not hasattr(self, 'last_damage_to_player'):
                self.last_damage_to_player = 0
            if not hasattr(self, 'last_enemy_hit_time'):
                self.last_enemy_hit_time = -1.0
            if not hasattr(self, 'last_player_hit_time'):
                self.last_player_hit_time = -1.0
            if not hasattr(self, 'last_energy_spend_time'):
                self.last_energy_spend_time = -1.0
            if not hasattr(self, 'last_turn_start_time'):
                self.last_turn_start_time = -1.0
            if not hasattr(self, 'battle_end_time'):
                self.battle_end_time = -1.0
            if not hasattr(self, 'last_player_block_gain_time'):
                self.last_player_block_gain_time = -1.0
            if not hasattr(self, 'enemy_id'):
                self.enemy_id = "colonel"
            if not hasattr(self, 'enemy_name'):
                self.enemy_name = "Colonel"
            if not hasattr(self, 'enemy_sprite_id'):
                self.enemy_sprite_id = "colonel"
            if not hasattr(self, 'enemy_log_name'):
                self.enemy_log_name = "Colonel"
            if not hasattr(self, 'enemy_strength'):
                self.enemy_strength = 0
            if not hasattr(self, 'cards_played_this_turn'):
                self.cards_played_this_turn = 0
            if not hasattr(self, 'current_turn_max_cards'):
                self.current_turn_max_cards = None
            if not hasattr(self, '_popup_enemy_seq'):
                self._popup_enemy_seq = 0
            if not hasattr(self, '_popup_player_seq'):
                self._popup_player_seq = 0

        ## ---------------- TIME ----------------
        def _now(self):
            """Current game-runtime seconds (excludes paused time), or 0.0 if
            the runtime isn't available. Used to stamp hit/animation events."""
            try:
                return renpy.get_game_runtime()
            except Exception:
                return 0.0

        ## ---------------- LOG ----------------
        def add_log(self, msg):
            self.log.append(msg)
            ## Keep log capped to last 12 entries to bound memory and screen size
            if len(self.log) > 12:
                self.log = self.log[-12:]

        ## ---------------- DAMAGE / BLOCK ----------------
        def deal_damage(self, target, amount, source_kind="effect", bypass_block=False, popup_delay=0.0):
            """target: 'player' | 'enemy' (or string aliases).

            source_kind: 'effect' (card-played effect) | 'intent' (colonel's
            attack resolving on enemy turn). Player-target damage from
            'effect' sources (i.e., self-damage cards like vip_treatment,
            hrv_spike, the_compound) is FLOOR-CLAMPED to leave at least 1 HP
            so a single card play can never insta-defeat the player. This
            is a fix for the long-standing 'select any card → instantly
            loose' bug — see commit log.

            bypass_block: when True, player block is NOT subtracted from
            the incoming damage. Used by self-harm cards whose text reads
            'Lose N HP' — your block stops enemies, not your own outburst
            or the syringe you just stabbed yourself with.

            popup_delay: seconds to delay the damage-popup render. Multi-hit
            compound attacks pass _i * 0.14 so the -N popups stagger across
            time instead of all collapsing into the last frame. The popup
            screen's transform consumes the delay (renpy.pause from a screen
            action would silently fail).
            """
            if amount <= 0:
                return
            if target == "enemy":
                ## Apply enemy block first
                absorbed = min(self.enemy_block, amount)
                self.enemy_block -= absorbed
                actual = amount - absorbed
                self.enemy_hp -= actual
                self.last_damage_to_enemy = actual
                self.add_log("{} takes {} damage.".format(self.enemy_log_name, actual))
                if self.enemy_hp <= 0:
                    self.enemy_hp = 0
                    self.over = "victory"
                    self.battle_end_time = self._now()
                ## Phase A juice — floating "-N" popup + portrait shake + sfx.
                ## We push the popup IMPERATIVELY via renpy.show_screen rather
                ## than relying on battle_screen to mount it conditionally.
                ## The screen-conditional approach kept failing because the
                ## screen's `$ _ed = bs.last_damage_to_enemy` capture was
                ## stale unless Ren'Py rebuilt the body, and Function actions
                ## returning None don't reliably trigger rebuilds. show_screen
                ## bypasses that entire layer — Ren'Py mounts the popup screen
                ## directly, ATL fires from frame 0, calling show_screen again
                ## with the same name replaces the prior popup so successive
                ## hits each get a fresh animation. Wrapped in try/except for
                ## non-interaction contexts (battle_init, Power auto-fire).
                if actual > 0:
                    self.last_enemy_hit_time = self._now()
                    _play_battle_sfx("hit_thud")
                    try:
                        ## UNIQUE _tag per hit so Ren'Py mounts a brand-new
                        ## screen instance with its own ATL. Multi-hit compounds
                        ## now COEXIST (previously the hide-previous-tag call
                        ## killed earlier popups when several hits resolved in
                        ## the same frame — only the last one ever rendered).
                        ## Lifetime is bounded by the transform's alpha-out at
                        ## ~1.2s; lingering zero-alpha screens don't draw.
                        self._popup_enemy_seq += 1
                        renpy.show_screen(
                            "damage_popup_enemy_inner",
                            damage=actual,
                            delay=popup_delay,
                            _tag="dmg_popup_enemy_{}".format(self._popup_enemy_seq),
                        )
                        renpy.restart_interaction()
                    except Exception:
                        pass
            elif target == "player":
                ## Apply mental damage reduction if buff active
                if self.buffs.get("mental_dr_50") and self._intent_has_tag("mental"):
                    amount = max(1, amount // 2)
                if bypass_block:
                    absorbed = 0
                else:
                    absorbed = min(self.player_block, amount)
                    self.player_block -= absorbed
                actual = amount - absorbed
                ## Insta-loss prevention: card self-damage cannot drop HP below 1.
                ## Only the colonel's actual intent (source_kind='intent') can defeat.
                if source_kind == "effect" and (self.player_hp - actual) <= 0:
                    actual = max(0, self.player_hp - 1)
                    self.add_log("[[Floor]: self-damage clipped — you survive at 1 HP.")
                self.player_hp -= actual
                self.last_damage_to_player = actual
                self.add_log("JB takes {} damage.".format(actual))
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.over = "defeat"
                    self.battle_end_time = self._now()
                ## Phase A juice — floating "-N" popup + flash overlay + sfx.
                ## Same imperative show_screen pattern as the enemy branch.
                ## "enemy_hit" plays the user-provided punch wav (audio/sfx/
                ## enemy_hit.wav) — replaces the no-op hit_thud placeholder
                ## for enemy-attack impact feedback.
                if actual > 0:
                    self.last_player_hit_time = self._now()
                    _play_battle_sfx("enemy_hit")
                    try:
                        ## Same unique-tag pattern as the enemy branch — see
                        ## that comment for the multi-hit coexistence reason.
                        self._popup_player_seq += 1
                        renpy.show_screen(
                            "damage_popup_player_inner",
                            damage=actual,
                            delay=popup_delay,
                            _tag="dmg_popup_player_{}".format(self._popup_player_seq),
                        )
                        renpy.restart_interaction()
                    except Exception:
                        pass

        def gain_block(self, target, amount):
            if target == "enemy":
                self.enemy_block += amount
                self.add_log("{} gains {} block.".format(self.enemy_log_name, amount))
            else:
                self.player_block += amount
                self.add_log("JB gains {} block.".format(amount))
                ## Phase A juice — block-gain sfx
                ## Phase E juice — timestamp drives block-text pulse on screen
                if amount > 0:
                    _play_battle_sfx("block_clang")
                    try:
                        self.last_player_block_gain_time = renpy.get_game_runtime()
                    except Exception:
                        pass

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
            ## Phase B juice — timestamp the spend so the energy counter pulses.
            if n > 0:
                try:
                    self.last_energy_spend_time = renpy.get_game_runtime()
                except Exception:
                    pass
            self.energy = max(0, self.energy - n)

        ## ---------------- INTENT MANAGEMENT ----------------
        def advance_intent(self):
            """Move to the next intent. If the deck is exhausted, reshuffle
            IMMEDIATELY so the next player turn always sees a valid incoming
            intent. Without this, the queue could expire mid-enemy-turn and
            the player would see "no intent → end turn → take damage from
            nowhere" — the reshuffle would happen during enemy resolve and
            the player gets blindsided by an intent they never saw queued.
            """
            self.intent_index += 1
            if self.intent_index >= len(self.intent_queue):
                self.intent_queue = build_enemy_deck(self.enemy_id, prev_card_id=self.last_intent_resolved)
                self.intent_index = 0
                ## Rvac drunken double-down — wrinkle fires on first reshuffle.
                if self.enemy_id == "rvac" and not self.buffs.get("rvac_doubled", False):
                    self.buffs["enemy_attack_bonus"] = self.buffs.get("enemy_attack_bonus", 0) + 3
                    self.buffs["rvac_doubled"] = True
                    self.add_log("[[Drunken double-down]: he's seeing red. +3 to his next swing.")

        def current_intent(self):
            if self.intent_index >= len(self.intent_queue):
                return None
            return ENEMY_DECK_LIBRARY.get(self.intent_queue[self.intent_index])

        ## peek_intents removed per feedback_no_peek_intent — multi-turn
        ## intent reveal doesn't fit the sim. Default intent_revealed=1
        ## keeps StS-style single-turn intent display intact.

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
            ## Compromise cards (loss-injected) carry unplayable=True — they
            ## sit dead in hand, costing a draw slot. Gate before the energy
            ## check so a 0-cost Compromise still reports as unplayable.
            if c.get("unplayable"):
                return False, "Unplayable. Dead weight."
            ## Card-play restriction (boss-style "only N cards this turn").
            ## Gate before energy so it shows even on 0-cost cards.
            if self.current_turn_max_cards is not None:
                if self.cards_played_this_turn >= self.current_turn_max_cards:
                    return False, "Restricted: {} card(s) max this turn.".format(self.current_turn_max_cards)
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

    def battle_init(enemy_id="colonel"):
        """Build a fresh BattleState for a battle against enemy_id. Reads
        stats / player_deck / difficulty. Colonel defaults preserve the
        original entry point (`battle_init()`) used by colonel_event.rpy."""
        global battle_state
        bs = BattleState()

        ## Enemy identity — pull from ENEMY_LIBRARY with Colonel-safe fallbacks.
        _enemy = ENEMY_LIBRARY.get(enemy_id, {})
        bs.enemy_id = enemy_id
        bs.enemy_name = _enemy.get("display_name", "Colonel")
        bs.enemy_sprite_id = _enemy.get("sprite_id", "colonel")
        bs.enemy_log_name = _enemy.get("log_name", "Colonel")

        ## Player HP by class (+ permanent gym-session bonus folded in)
        _gym_b = getattr(store, 'gym_max_hp_bonus', 0)
        if stats and stats.player_class == "bodybuilder":
            bs.player_max_hp = 115 + _gym_b
            bs.player_hp = 115 + _gym_b
            ## SOMA bonus: +1 starting block per turn for every 3 SOMA stacks
            ## (was every 2 — nerfed so ladder fights actually test the player).
            _soma = getattr(store, 'bb_soma', 0)
            if _soma >= 3:
                bs.buffs["stoic_anchor_block"] = bs.buffs.get("stoic_anchor_block", 0) + (_soma // 3)
                bs.add_log("[[SOMA x{}]: +{} starting block per turn.".format(_soma, _soma // 3))
            ## Presence: 1 charge (was 3). One free +3 starting block on turn 1
            ## only, then the player has to play actual block cards.
            bs.buffs["presence_charges"] = 1
            bs.add_log("[[PRESENCE x1]: One free +3 block on your opening turn. After that the room shrinks again.")
        elif stats and stats.player_class == "dark_empath":
            bs.player_max_hp = 75 + _gym_b
            bs.player_hp = 75 + _gym_b
            ## DE init kept minimal — class is locked (BB-only scope per
            ## feedback_bb_only_scope). The original peek-intents perk was
            ## removed per feedback_no_peek_intent; no replacement designed
            ## here since DE isn't currently playable. If/when DE ships,
            ## design a non-peek class identity perk in this slot.
        elif stats and stats.player_class == "biohacker":
            bs.player_max_hp = 80 + _gym_b
            bs.player_hp = 80 + _gym_b
            ## BH max-energy gate: dose-counter check (3+ total nootropic uses across all tiers).
            if sum(getattr(store, 'nootropic_uses', [0,0,0,0,0])) >= 3:
                bs.max_energy = 4
                bs.add_log("[[STACK]: dose count >= 3. +1 max energy.")
            bs.buffs["kick_charges"] = 3
            bs.add_log("[[KICK x3]: The compound kicking in. Each turn it's running, you draw one extra card. He's still finishing the sentence; you've already chosen.")
        else:
            ## No class set (shouldn't happen in normal play) — safe defaults.
            bs.player_max_hp = 80
            bs.player_hp = 80

        ## ── PERSISTENT RUN HP ─────────────────────────────────────────────────
        ## HP carries between ladder battles + into the Colonel — first fight
        ## starts at class max (run_hp=None branch), subsequent fights start at
        ## whatever HP the previous battle ended with (saved by battle_finish on
        ## victory; subtracted by forced_detour on defeat). Lazy-init pattern:
        ## the very first battle in a new run sees run_hp=None and writes the
        ## class max here so future battles have a value to load.
        _run_hp = getattr(store, 'run_hp', None)
        _run_hp_max = getattr(store, 'run_hp_max', None)
        if _run_hp_max is None or _run_hp_max != bs.player_max_hp:
            store.run_hp_max = bs.player_max_hp
        if _run_hp is None:
            store.run_hp = bs.player_max_hp
        else:
            ## Clamp into [1, max] so detour over-shoots or stale state can't
            ## ghost-kill the player on battle entry.
            bs.player_hp = max(1, min(bs.player_max_hp, _run_hp))

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

        ## Build enemy deck — Colonel uses build_colonel_deck() (difficulty-scaled);
        ## ladder enemies use their ENEMY_LIBRARY deck_template.
        bs.intent_queue = build_enemy_deck(enemy_id)

        ## Enemy HP. Colonel = 150 HP — capstone tier, must out-bulk medium
        ## ladder enemies (the boss can't be HP-weaker than the patsies he
        ## sends). Was 100, then 140; bumped again per balance-judge: at 140,
        ## BB-capped (115 + 30 gym cap = 145) still won at ~110 HP remaining.
        ## 150 forces real preparation — Colonel matches or exceeds player max.
        ## Ladder enemies use ENEMY_LIBRARY max_hp.
        if enemy_id == "colonel":
            bs.enemy_max_hp = 150
        else:
            bs.enemy_max_hp = _enemy.get("max_hp") or 80
        bs.enemy_hp = bs.enemy_max_hp

        ## Sanity guard — ensure player HP is never <= 0 at battle start.
        ## Power-card auto-fire effects + BH withdrawal could in theory push
        ## HP negative if max_hp was tiny.
        ## A non-positive HP at battle start triggers immediate defeat on the
        ## first damage tick, which is the long-standing 'insta-loss' bug.
        if bs.player_hp <= 0:
            bs.player_hp = max(1, bs.player_max_hp)
            bs.add_log("[[Sanity]: HP was non-positive at battle start; reset to {}.".format(bs.player_hp))

        bs.add_log("[[INIT]: HP {}/{}  Enemy {}/{}  deck {}  hand 0".format(
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

        ## Card-play counter resets every turn. If a 'restrict' intent set
        ## cards_cap_next_turn, latch that into the live cap and consume.
        bs.cards_played_this_turn = 0
        if bs.buffs.get("cards_cap_next_turn"):
            bs.current_turn_max_cards = bs.buffs["cards_cap_next_turn"]
            bs.buffs["cards_cap_next_turn"] = 0
        else:
            bs.current_turn_max_cards = None

        ## Phase C juice — timestamp the turn start so the screen can render
        ## a sliding TURN N banner that auto-fades after 1.4s.
        try:
            bs.last_turn_start_time = renpy.get_game_runtime()
        except Exception:
            pass

        ## Apply start-of-turn buffs
        if bs.buffs.get("starting_block_+1"):
            bs.player_block += 1
        if bs.buffs.get("stoic_anchor_block"):
            bs.player_block += bs.buffs["stoic_anchor_block"]
        if bs.buffs.get("presence_charges", 0) > 0:
            bs.player_block += 3
            bs.buffs["presence_charges"] -= 1
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
            bs.add_log("[[FLMod crash]: you lose this turn.")
            battle_end_player_turn()
            return

        ## Refill energy (BH gets +1 if they took FLMod yesterday — already in player_max_hp logic)
        bs.energy = bs.max_energy

        ## FLModafinil ebb — peak passes, max energy reduced this turn only
        if bs.buffs.get("max_energy_penalty_next_turn", 0) > 0:
            _pen = bs.buffs["max_energy_penalty_next_turn"]
            bs.energy = max(0, bs.energy - _pen)
            bs.buffs["max_energy_penalty_next_turn"] = 0
            bs.add_log("[[FLMod ebb]: -{} max energy this turn.".format(_pen))

        ## Stack-up crash — Biohacker pays for last turn's energy spike
        if bs.buffs.get("crash_next_turn"):
            bs.energy = max(0, bs.energy - 2)
            bs.buffs["crash_next_turn"] = False
            bs.add_log("[[Stack crash]: the spike wears off. -2 energy this turn.")

        ## --- Pre-draw wrinkles: modify draw pile or set buffs the draw sees ---
        ## Status injections insert at the TOP of the draw pile so they land
        ## in the player's hand THIS turn rather than waiting for reshuffle
        ## (which on a 20-card deck could be 4+ turns away).
        _eid = getattr(bs, 'enemy_id', 'colonel')
        if _eid == "spis" and bs.turn >= 2:
            bs.draw_pile.insert(0, "paperwork")
            bs.add_log("[[Paper-clog]: a form files itself onto your stack.")
        if _eid == "sprejeri":
            ## Tag stack: +1 per player turn (capped at 4 to avoid feel-bad
            ## end-game nukes from extended block/debuff streaks).
            bs.buffs["sprejeri_tags"] = min(4, bs.buffs.get("sprejeri_tags", 0) + 1)
        if _eid == "nguyen" and bs.turn == 3:
            bs.draw_pile.insert(0, "counterfeit")
            bs.add_log("[[Counterfeit]: a fake offer slides onto your stack.")
        if _eid == "inspekce" and bs.turn >= 3 and bs.turn % 2 == 1:
            bs.draw_pile.insert(0, "paperwork")
            bs.add_log("[[Audit]: another form joins your stack.")
        if _eid == "garda" and bs.turn in (3, 6):
            bs.draw_pile.insert(0, "tear_gas")
            bs.add_log("[[Tear gas]: a canister rolls onto your stack.")

        ## Draw 5 cards — minus any pending draw penalty from the previous
        ## enemy turn's debuff intents (authority_display, spray_blind,
        ## file_swap, gas_release, radio_static, audit). Floor at 1 so
        ## stacked penalties can't soft-lock the player to zero cards.
        _draw_count = 5
        _dp = bs.buffs.get("player_draw_penalty", 0)
        if _dp > 0:
            _draw_count = max(1, _draw_count - _dp)
            bs.buffs["player_draw_penalty"] = 0
            bs.add_log("[[Debuff]: -{} card draw this turn.".format(_dp))
        bs.draw_cards(_draw_count)

        if bs.buffs.get("kick_charges", 0) > 0:
            bs.draw_cards(1)
            bs.buffs["kick_charges"] -= 1

        ## --- Post-draw wrinkles: must run AFTER draw_cards(5) so hand exists ---
        if _eid == "dispatcher" and bs.turn >= 3 and bs.turn % 3 == 0 and bs.hand:
            ## Priority change: every 3rd turn, discard one random card from the
            ## freshly-drawn hand and replace it — the case got reassigned mid-shift.
            _victim = _battle_rand.choice(bs.hand)
            bs.discard(_victim)
            bs.draw_cards(1)
            bs.add_log("[[Reassigned]: lost {}, drew replacement.".format(_victim))

        bs.add_log("--- Turn {} ---".format(bs.turn))


    def battle_play_card(card_id):
        """Play a card from hand.

        Returns None unconditionally. We deliberately do NOT return a
        bool here: this function is wired up as a Ren'Py screen Function
        action, and Ren'Py's behavior.run() propagates the LAST non-None
        return value from an action list as an implicit screen Return —
        which would exit battle_screen on every click. battle_outcome()
        then falls through to its conservative 'defeat' default because
        bs.over was never set, jumping the player straight to the defeat
        ending. This was the long-standing 'play any card → instant
        defeat' bug. Keep the early-exits as bare `return` statements.
        """
        bs = battle_state
        if bs is None or bs.is_over():
            return
        if card_id not in bs.hand:
            return
        ok, reason = bs.hand_playable(card_id)
        if not ok:
            bs.add_log("Cannot play: " + reason)
            return

        c = CARD_LIBRARY.get(card_id, {})
        cost = c.get("cost", 0)
        if isinstance(cost, int):
            bs.spend_energy(cost)

        ## Tick the per-turn card counter — feeds the 'restrict' intent gate.
        bs.cards_played_this_turn += 1

        ## Phase A juice — play card-type sfx immediately on click,
        ## before the effect resolves, so the audio feedback feels snappy.
        bs.last_card_type = c.get("type", "Skill")
        _play_battle_sfx("card_" + bs.last_card_type.lower())

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


    def battle_end_player_turn():
        """Player ends their turn — discard hand, resolve enemy intent."""
        bs = battle_state
        if bs is None or bs.is_over():
            return

        ## Phase A juice — end-turn sfx (commits the player's plan)
        _play_battle_sfx("end_turn")

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

        ## Block expires at the start of the OWNING character's next turn.
        ## Player block resets in battle_start_player_turn (line ~529).
        ## Enemy block must reset here — otherwise a turn-1 block intent
        ## carries forward forever (bug: dodge stacks turn-on-turn).
        bs.enemy_block = 0

        ## Reset damage trackers — fresh intent, fresh accounting
        bs.last_damage_to_player = 0
        bs.last_damage_to_enemy = 0

        ## Phase 1A diagnostic — track which branch handled this intent so the
        ## end-of-function safety-net knows whether a 0-damage attack is bug or
        ## expected (algorithm/refactor/mirror/immunity all legitimately 0).
        ## Toggle persistent.debug_battle in console to see the raw trace.
        ##
        ## Capture pre-resolve block so the safety-net can distinguish "no
        ## damage taken because the player had no defense" (true bug signal)
        ## from "no damage taken because the player's block exactly absorbed
        ## the hit" (legitimate gameplay, must NOT warn).
        _debug = bool(getattr(persistent, 'debug_battle', False))
        _intent_was_attack = False
        _pre_resolve_block = bs.player_block
        if _debug:
            _ic_dbg = bs.current_intent()
            bs.add_log("[[DBG]: enter resolve — intent={} skip={} cancel={} mirror={} block={}".format(
                (_ic_dbg or {}).get("id", "none"),
                bs.skip_attack_count,
                bs.cancel_next_attack,
                bool(bs.buffs.get("mirror_next")),
                _pre_resolve_block,
            ))

        ## --- Grundza lab-timer: synthesize a burst intent that replaces
        ## the scheduled turn-7 intent. Synthesizing (rather than early-
        ## return) lets the normal pipeline fire below: brawl bleed ticks,
        ## retaliate buffs (Iron Stance / Iron Body / single_retaliate_dmg)
        ## respond, damage gets logged through state.deal_damage.
        _grundza_burst_intent = None
        if bs.enemy_id == "grundza":
            _wd = ENEMY_LIBRARY.get("grundza", {}).get("wrinkle_data", {})
            _det_turn = _wd.get("detonation_turn", 7)
            _det_dmg = _wd.get("detonation_dmg", 22)
            if bs.turn == _det_turn and not bs.buffs.get("grundza_detonated", False):
                bs.buffs["grundza_detonated"] = True
                bs.add_log("[[Lab Timer]: the rig blows.")
                _grundza_burst_intent = {
                    "id":     "grundza_burst",
                    "name":   "Lab Detonation",
                    "intent": "attack",
                    "value":  _det_dmg,
                    "tags":   [],
                }

        ## Brawl bleed — applied at the START of each colonel intent if active
        if bs.buffs.get("bleed_turns", 0) > 0:
            _bleed = bs.buffs.get("bleed_dmg", 0)
            if _bleed > 0:
                bs.deal_damage("enemy", _bleed)
                bs.add_log("[[Bleed]: {} takes {} dmg from open wound.".format(bs.enemy_log_name.lower(), _bleed))
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
                bs.add_log("[[Algorithm]: skipped {}'s '{}'.".format(bs.enemy_log_name.lower(), ic.get("name", "?")))
            bs.advance_intent()
            if _debug:
                bs.add_log("[[DBG]: branch=algorithm_skip")
            return

        ic = _grundza_burst_intent if _grundza_burst_intent is not None else bs.current_intent()
        if ic is None:
            ## Out of intents — reshuffle the deck and continue. NO auto-victory
            ## on deck exhaustion: the only win condition is enemy_hp == 0.
            ## Players found the old HP<=25 auto-win cheap and unsatisfying.
            bs.intent_queue = build_enemy_deck(bs.enemy_id, prev_card_id=bs.last_intent_resolved)
            bs.intent_index = 0
            ## --- Rvac drunken double-down: first reshuffle adds +3 to
            ## the next attack (uses existing one-shot enemy_attack_bonus
            ## slot which zeros after one attack).
            if bs.enemy_id == "rvac" and not bs.buffs.get("rvac_doubled", False):
                bs.buffs["enemy_attack_bonus"] = bs.buffs.get("enemy_attack_bonus", 0) + 3
                bs.buffs["rvac_doubled"] = True
                bs.add_log("[[Drunken double-down]: he's seeing red. +3 to his next swing.")
            ic = bs.current_intent()
            if ic is None:
                ## Deck somehow rebuilt empty (registration bug). Bail rather
                ## than crash — the player just gets a free turn.
                return

        ## Defensive guard — every branch above either reassigned ic or returned,
        ## but a future edit could miss this; bail rather than crashing the
        ## immunity check at the dict access below.
        if ic is None:
            return

        ## Cancellation check
        if bs.cancel_next_attack:
            bs.cancel_next_attack = False
            bs.add_log("[[Refactor]: cancelled {}'s '{}'.".format(bs.enemy_log_name.lower(), ic.get("name", "?")))
            bs.advance_intent()
            if _debug:
                bs.add_log("[[DBG]: branch=refactor_cancel")
            return

        ## Class immunity
        if stats and stats.player_class in ic.get("immunity", []):
            bs.add_log("[[{}]: '{}' bounces off you.".format(stats.player_class.upper(), ic.get("name", "?")))
            bs.advance_intent()
            if _debug:
                bs.add_log("[[DBG]: branch=class_immunity")
            return

        ## Conditional counters (player-side buffs and stat thresholds)
        damage_reduction = 0
        for cond, mod in ic.get("counter", {}).items():
            if _check_battle_condition(bs, cond):
                if mod.get("negate"):
                    bs.add_log("[[{}]: '{}' is negated.".format(cond.upper(), ic.get("name", "?")))
                    if mod.get("damage_to_self"):
                        bs.deal_damage("enemy", mod["damage_to_self"])
                    bs.advance_intent()
                    return
                damage_reduction += mod.get("reduce_damage", 0)

        ## Mirror buff — return next attack at double damage instead of taking it
        if bs.buffs.get("mirror_next") and ic.get("intent") in ("attack", "compound"):
            bs.buffs["mirror_next"] = False
            ## Set cooldown so Mirror can't fire again for 2 player turns
            bs.buffs["mirror_cooldown"] = 2
            base = ic.get("value", 0) * (ic.get("value2", 1) if ic.get("intent") == "compound" else 1)
            bs.deal_damage("enemy", base * 2)
            bs.add_log("[[Mirror]: '{}' bounced for {} dmg. (2-turn cooldown.)".format(ic.get("name", "?"), base * 2))
            bs.advance_intent()
            if _debug:
                bs.add_log("[[DBG]: branch=mirror_bounce")
            return

        ## Reframe buff — convert next attack into block
        if bs.buffs.get("reframe_next") and ic.get("intent") in ("attack", "compound"):
            bs.buffs["reframe_next"] = False
            base = ic.get("value", 0)
            bs.gain_block("player", base)
            bs.add_log("[[Reframe]: '{}' reframed into +{} block.".format(ic.get("name", "?"), base))
            bs.advance_intent()
            if _debug:
                bs.add_log("[[DBG]: branch=reframe")
            return

        ## Frame Trap (DE) — additional one-shot damage reduction on the next attack
        if bs.buffs.get("next_attack_reduction", 0) > 0:
            damage_reduction += bs.buffs["next_attack_reduction"]
            bs.buffs["next_attack_reduction"] = 0
            bs.add_log("[[Frame Trap]: attack softened.")

        ## Resolve intent by type
        intent_type = ic.get("intent", "attack")
        bs.last_intent_resolved = ic["id"]
        _intent_was_attack = intent_type in ("attack", "compound")

        ## --- Lawyer paragraph_cite: on every Nth turn, his next attack/compound
        ## intent gets +bonus_dmg damage AND caps max_energy_penalty_next_turn at 1.
        ## Cap (vs +=1) prevents intimidate+cite stacking into a 2-energy lockout.
        _paragraph_fires = False
        if bs.enemy_id == "lawyer" and intent_type in ("attack", "compound"):
            _wd = ENEMY_LIBRARY.get("lawyer", {}).get("wrinkle_data", {})
            _cad = _wd.get("cadence", 3)
            if bs.turn > 0 and bs.turn % _cad == 0:
                _paragraph_fires = True

        if intent_type == "attack":
            dmg = max(1 if ic.get("value", 0) > 0 else 0, ic.get("value", 0) - damage_reduction)
            ## Permanent enemy Strength buff (StS analog) — adds to every
            ## attack/compound hit. Granted by 'strength' intent type.
            dmg += bs.enemy_strength
            ## --- Sprejeri tag stack spend: +tags dmg on attack when stack >= 3 ---
            if bs.enemy_id == "sprejeri":
                _tags = bs.buffs.get("sprejeri_tags", 0)
                if _tags >= 3:
                    dmg += _tags
                    bs.buffs["sprejeri_tags"] = 0
                    bs.add_log("[[Tag stack x{}]: +{} damage, stack reset.".format(_tags, _tags))
            ## --- Garda formation strength: +3 dmg while above 50% HP ---
            if bs.enemy_id == "garda" and bs.enemy_hp > bs.enemy_max_hp // 2:
                dmg += 3
            if _paragraph_fires:
                _bonus = ENEMY_LIBRARY.get("lawyer", {}).get("wrinkle_data", {}).get("bonus_dmg", 6)
                dmg += _bonus
                bs.buffs["max_energy_penalty_next_turn"] = max(bs.buffs.get("max_energy_penalty_next_turn", 0), 1)
                bs.add_log("[[Paragraf cite]: +{} dmg, your next turn loses 1 energy.".format(_bonus))
            bs.deal_damage("player", dmg, source_kind="intent")
        elif intent_type == "compound":
            hits = ic.get("value2", 1)
            per_hit = max(1 if ic.get("value", 0) > 0 else 0, ic.get("value", 0) - (damage_reduction // max(1, hits)))
            ## Strength applies PER HIT (StS rule) — compound attacks scale
            ## sharply with strength stacks.
            per_hit += bs.enemy_strength
            if _paragraph_fires:
                _bonus = ENEMY_LIBRARY.get("lawyer", {}).get("wrinkle_data", {}).get("bonus_dmg", 6)
                per_hit += max(1, _bonus // max(1, hits))
                bs.buffs["max_energy_penalty_next_turn"] = max(bs.buffs.get("max_energy_penalty_next_turn", 0), 1)
                bs.add_log("[[Paragraf cite]: +{} dmg per hit, your next turn loses 1 energy.".format(max(1, _bonus // max(1, hits))))
            for _i in range(hits):
                if bs.is_over():
                    break
                ## popup_delay staggers the damage popup render so multi-hit
                ## compounds show as -N, -N, -N consecutively instead of all
                ## five collapsing into one frame. The delay is consumed by
                ## the popup screen's transform, NOT renpy.pause — pausing
                ## from a screen-action callback silently fails.
                bs.deal_damage("player", per_hit, source_kind="intent", popup_delay=_i * 0.14)
        elif intent_type == "block":
            bs.gain_block("enemy", ic.get("value", 0))
        elif intent_type == "buff":
            ## Cold Stare — add to a self-attack-bonus stack (one-shot bonus
            ## that fires + decays after the next attack lands).
            bs.buffs["enemy_attack_bonus"] = bs.buffs.get("enemy_attack_bonus", 0) + ic.get("value", 0)
        elif intent_type == "strength":
            ## Permanent +N strength for the rest of the fight (StS Strength).
            ## Used by ramp enemies (Inspekce case_review, Colonel cold_stare
            ## v2) — every subsequent attack hits harder.
            _gain = ic.get("value", 0)
            bs.enemy_strength += _gain
            bs.add_log("{} gains +{} Strength (now {}).".format(bs.enemy_log_name, _gain, bs.enemy_strength))
        elif intent_type == "restrict":
            ## Limit how many cards the player can play on their NEXT turn.
            ## Latched in battle_start_player_turn into current_turn_max_cards.
            _cap = ic.get("value", 1)
            bs.buffs["cards_cap_next_turn"] = _cap
            bs.add_log("{} restricts you to {} card(s) next turn.".format(bs.enemy_log_name, _cap))
        elif intent_type == "debuff":
            ## Default debuff_key is player_draw_penalty (Colonel + Easy enemies).
            ## Medium/Hard enemies override via ic["debuff_key"] (e.g.
            ## "max_energy_penalty_next_turn" for energy-suppress intents).
            _dbuff_key = ic.get("debuff_key", "player_draw_penalty")
            bs.buffs[_dbuff_key] = bs.buffs.get(_dbuff_key, 0) + ic.get("value", 1)

        ## Apply enemy_attack_bonus to attacks
        if intent_type == "attack" and bs.buffs.get("enemy_attack_bonus"):
            bonus = bs.buffs["enemy_attack_bonus"]
            bs.buffs["enemy_attack_bonus"] = 0
            bs.deal_damage("player", bonus, source_kind="intent")
            bs.add_log("Pressure bonus: +{} damage.".format(bonus))

        ## Stoic Anchor heal-on-hit
        if bs.buffs.get("stoic_anchor_heal") and bs.last_damage_to_player > 0:
            bs.heal("player", bs.buffs["stoic_anchor_heal"])

        ## Iron Stance retaliate-on-hit (BB) — scales with turn count, capped.
        ## Turn 1: 4 dmg. Turn 5: 12 (cap). Turn 10+: 12. Audit nerf: was
        ## uncapped (turn 10 = 22), interacting with multi-hit enemy intents
        ## (baton_combo, tag_team) to deal 60+ free damage per turn at long
        ## fights. Cap at 12 keeps the scaling identity, stops the runaway.
        if bs.buffs.get("iron_stance_active") and bs.last_damage_to_player > 0:
            _retaliate = min(12, 4 + (max(1, bs.turn) - 1) * 2)
            bs.deal_damage("enemy", _retaliate)
            bs.add_log("[[Iron Stance]: retaliated for {} dmg (turn {}).".format(_retaliate, bs.turn))

        ## Iron Body single-shot retaliate (BB common) — fires once on next hit
        if bs.buffs.get("single_retaliate_dmg", 0) > 0 and bs.last_damage_to_player > 0:
            _sr = bs.buffs["single_retaliate_dmg"]
            bs.buffs["single_retaliate_dmg"] = 0
            bs.deal_damage("enemy", _sr)
            bs.add_log("[[Iron Body]: retaliated for {} dmg.".format(_sr))

        ## Phase 1A safety-net — self-report if an attack intent landed but
        ## did 0 damage despite no early-return branch firing AND the player
        ## had no block at intent-resolve time. This is the "colonel never
        ## attacks" symptom from the playtest. Gating on `_pre_resolve_block
        ## == 0` (captured at function entry) eliminates the false-positive
        ## of "block exactly absorbed the hit" — block-absorption is the
        ## intended path, not a bug.
        if _intent_was_attack and bs.last_damage_to_player == 0 and _pre_resolve_block == 0:
            bs.add_log("[[WARN]: '{}' resolved 0 dmg with no player block — investigate.".format(ic.get("name", "?")))

        bs.advance_intent()


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
        """Tear down — clear singleton + persist HP on victory + hide any
        lingering damage popup so it doesn't carry over.

        Persistent HP rule: on victory, write bs.player_hp to store.run_hp so
        the next battle starts at the post-fight HP. On defeat, forced_detour
        writes the hospital-floored HP itself — battle_finish leaves run_hp
        alone in that case (writing 0 here would over-write the detour's
        floor and start the next fight at 0 HP)."""
        global battle_state
        if battle_state is not None:
            bs = battle_state
            if bs.over == "victory":
                store.run_hp = max(1, bs.player_hp)
            for _i in range(1, getattr(bs, '_popup_enemy_seq', 0) + 1):
                try:
                    renpy.hide_screen("dmg_popup_enemy_{}".format(_i))
                except Exception:
                    pass
            for _i in range(1, getattr(bs, '_popup_player_seq', 0) + 1):
                try:
                    renpy.hide_screen("dmg_popup_player_{}".format(_i))
                except Exception:
                    pass
        for _popup in ("damage_popup_enemy_inner", "damage_popup_player_inner"):
            try:
                renpy.hide_screen(_popup)
            except Exception:
                pass
        battle_state = None


    ## ---------------- BATTLE OUTCOME ----------------

    def battle_outcome():
        """Returns 'victory_perfect' / 'victory_pyrrhic' / 'victory_close' / 'defeat'.

        If bs.over is None at call-time, the battle didn't end normally —
        return 'defeat' as the conservative default. The floor-clamp on
        player damage (deal_damage source_kind='effect') ensures bs.over
        is never set by card-play, so the only way to reach this fallback
        is genuine engine misuse — better to fail closed than hand the
        player a free victory.
        """
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
