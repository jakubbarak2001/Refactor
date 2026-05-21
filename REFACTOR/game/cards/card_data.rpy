################################################################################
## REFACTOR — Card & Deck Data Model (Phase 1.1)
##
## A Card has:
##   id        — stable string key (matches CARD_LIBRARY entry)
##   name      — display name
##   type      — "Attack" / "Skill" / "Power"
##   color     — "Physical" / "Mental" / "Money" / "Logic" / "Police" / "Special"
##   cost      — energy cost (0-3, 'X' allowed for cost-all)
##   rarity    — "common" / "uncommon" / "rare" / "boss"
##   effect    — function name (string) resolved at play time. Signature:
##                  effect_fn(state, source, target) -> None
##               Effects mutate `state` (BattleState) in place.
##   exhaust   — bool. If True, card is removed from the deck after one use.
##   class_lock — None or "bodybuilder"/"dark_empath"/"biohacker"
##   flavor    — short narrative tag
##
## A Deck is a list of card-ids. The battle engine (Phase 1.6) shuffles the
## deck into a draw pile, deals a hand, and tracks discard / exhaust piles.
##
## This file defines:
##   - CARD_LIBRARY (master dict, populated incrementally)
##   - card_effects (dict of effect_id -> callable)
##   - PlayerDeck container with helpers
##   - register_card() helper for adding cards
##   - grant_card() helper for activities/events
##
## Cards themselves are added in card_library.rpy (Phase 1.2+).
################################################################################

init -1 python:

    ## Master library. Card-ids -> card-data dicts. Populated by register_card().
    CARD_LIBRARY = {}

    ## Effect dispatch table. effect_id -> callable.
    ## Filled by @register_effect decorator in card_effects.rpy.
    card_effects = {}

    def register_card(card_id, **fields):
        """Register a card definition. Idempotent — last registration wins.

        If `upgrade={...}` is supplied, a sibling `<card_id>_plus` is auto-
        registered with the base fields plus the overrides. Name auto-suffixes
        with `+`, `is_upgraded=True`, and `upgrade_to` is unset on the plus
        (can't upgrade twice). The base card's `upgrade_to` points at the
        plus id, signaling it's upgradeable.
        """
        defaults = {
            "id":         card_id,
            "name":       card_id,
            "type":       "Skill",
            "color":      "Special",
            "cost":       1,
            "rarity":     "common",
            "effect":     None,
            "exhaust":    False,
            "class_lock": None,
            "archetype":  None,
            "flavor":        "",
            "art":           None,
            "art_glyph":     None,
            "is_rage":       False,
            "is_compromise": False,
            "unplayable":    False,
            "is_upgraded":   False,
            "upgrade_to":    None,
        }
        upgrade_overrides = fields.pop("upgrade", None)
        defaults.update(fields)
        defaults["id"] = card_id

        if upgrade_overrides is not None:
            plus_id = "{}_plus".format(card_id)
            plus = dict(defaults)
            plus.update(upgrade_overrides)
            plus["id"] = plus_id
            plus["name"] = "{}+".format(defaults.get("name", card_id))
            plus["is_upgraded"] = True
            plus["upgrade_to"] = None
            plus["pool_excluded"] = True
            CARD_LIBRARY[plus_id] = plus
            defaults["upgrade_to"] = plus_id

        CARD_LIBRARY[card_id] = defaults
        return defaults

    def register_effect(effect_id):
        """Decorator: register a card-effect callable in card_effects."""
        def _wrap(fn):
            card_effects[effect_id] = fn
            return fn
        return _wrap

    def get_card(card_id):
        """Look up a card definition. Returns None if unknown."""
        return CARD_LIBRARY.get(card_id)

    def card_is_playable(card_id, player_class=None):
        """A card is playable if it exists and the player's class isn't blocked."""
        c = CARD_LIBRARY.get(card_id)
        if c is None:
            return False
        if c.get("class_lock") and c["class_lock"] != player_class:
            return False
        return True


    class PlayerDeck(object):
        """The player's accumulated deck across the 30-day run.

        cards: list[str] of card_ids. Duplicates allowed — same card can appear
        multiple times if the player gains it more than once.
        """

        def __init__(self):
            self.cards = []

        def add(self, card_id):
            if card_id in CARD_LIBRARY:
                self.cards.append(card_id)

        def remove(self, card_id):
            if card_id in self.cards:
                self.cards.remove(card_id)

        def count(self, card_id=None):
            if card_id is None:
                return len(self.cards)
            return self.cards.count(card_id)

        def by_color(self, color):
            return [c for c in self.cards if CARD_LIBRARY.get(c, {}).get("color") == color]

        def by_rarity(self, rarity):
            return [c for c in self.cards if CARD_LIBRARY.get(c, {}).get("rarity") == rarity]

        def snapshot(self):
            """Return a fresh copy of the card-id list (for shuffling/draw)."""
            return list(self.cards)


    ## Module-level deck — initialised in init_game alongside stats/day_cycle.
    player_deck = None

    ## Class-signature cards — protected from permanent-removal effects.
    ## Canonical set; the Fixer (`script.rpy::fixer_meet`) reads this when
    ## filtering shred-eligible cards. Both base and `_plus` upgraded ids
    ## are included so upgrading your signature doesn't unlock it for
    ## removal. One copy of each per class; the card IS the class fantasy.
    CLASS_SIGNATURE_CARDS = {
        "heavy_set", "read_him", "stack_up",
        "heavy_set_plus", "read_him_plus", "stack_up_plus",
    }

    ## ---------------------------------------------------------------------------
    ## Fixer pricing — flat current price for ANY removal, escalates per shred.
    ## Defined at init-python level (not inside label python blocks) so the
    ## helper is module-pickled with the rest of init state. Defining helpers
    ## inside label python: blocks puts them in store and breaks save pickling
    ## — see the 2026-05-14 crash on _fixer_price_for.
    ## ---------------------------------------------------------------------------
    FIXER_BASE_PRICE  = 5000
    FIXER_PRICE_STEP  = 3000
    FIXER_PRICE_CAP   = 20000

    def fixer_current_price():
        """Flat CZK cost for the NEXT card-removal. Escalates with each prior
        removal this run, capped at FIXER_PRICE_CAP. Reads store._fixer_removals
        (initialized in python_logic.rpy:init_game)."""
        n = getattr(store, '_fixer_removals', 0)
        return min(FIXER_BASE_PRICE + n * FIXER_PRICE_STEP, FIXER_PRICE_CAP)

    def fixer_next_price():
        """Price the NEXT removal will cost AFTER the current shred lands.
        Used by the picker header to telegraph the escalation."""
        n = getattr(store, '_fixer_removals', 0) + 1
        return min(FIXER_BASE_PRICE + n * FIXER_PRICE_STEP, FIXER_PRICE_CAP)

    ## Backward-compat shim for saves made during the broken-pickle window.
    ## The previous fixer revision defined `_fixer_price_for` inside a label
    ## python: block, which pushed a function into `store` that couldn't
    ## re-pickle on save. Defining the same name at init-python level here
    ## means any save carrying the stale store entry resolves to THIS
    ## function on load — and it's picklable. Returns the flat current
    ## price ignoring the per-card argument.
    def _fixer_price_for(card_id=None):
        return fixer_current_price()


    def register_upgrade(base_id, **overrides):
        """Register a `<base_id>_plus` variant for an existing base card,
        mirroring what `register_card(upgrade={...})` does inline. Use this
        when retro-fitting upgrades onto cards that were already registered
        without an `upgrade=` kwarg.

        Refuses to upgrade corruption (rage / compromise / status_*) — these
        are intentionally dead-weight and must not be sandable via gym."""
        base = CARD_LIBRARY.get(base_id)
        if base is None:
            return None
        if base.get("is_rage") or base.get("is_compromise"):
            return None
        if (base.get("effect") or "").startswith("status_"):
            return None
        plus_id = "{}_plus".format(base_id)
        plus = dict(base)
        plus.update(overrides)
        plus["id"] = plus_id
        plus["name"] = "{}+".format(base.get("name", base_id))
        plus["is_upgraded"] = True
        plus["upgrade_to"] = None
        plus["pool_excluded"] = True
        CARD_LIBRARY[plus_id] = plus
        base["upgrade_to"] = plus_id
        return plus

    def is_upgraded(card_id):
        c = CARD_LIBRARY.get(card_id)
        return bool(c and c.get("is_upgraded"))

    ## Bright green for upgraded card names everywhere they render — single
    ## visual signal across reward / deck / hand / fixer screens. The "+"
    ## suffix from register_upgrade stays in the name itself.
    UPGRADE_NAME_COLOR = "#44ee77"

    def card_name_color(card_or_id, fallback="#ffffff"):
        """Return UPGRADE_NAME_COLOR if the card is `_plus`-upgraded, else
        `fallback`. Accepts either a card_id string or a card dict. Use
        from any screen that renders an upgradeable card's name."""
        c = card_or_id
        if isinstance(c, str):
            c = CARD_LIBRARY.get(c)
        if c and c.get("is_upgraded"):
            return UPGRADE_NAME_COLOR
        return fallback

    def get_upgraded_id(card_id):
        c = CARD_LIBRARY.get(card_id)
        return c.get("upgrade_to") if c else None

    def is_upgradeable(card_id):
        """A card is upgradeable if it has an `upgrade_to` target. Rage,
        compromise, status, and already-upgraded `_plus` cards have no
        upgrade target by construction."""
        c = CARD_LIBRARY.get(card_id)
        if not c:
            return False
        if c.get("is_rage") or c.get("is_compromise"):
            return False
        if (c.get("effect") or "").startswith("status_"):
            return False
        return bool(c.get("upgrade_to"))

    def upgrade_card_in_deck(card_id):
        """Swap the FIRST occurrence of `card_id` in player_deck for its
        `_plus` variant. Returns the new id on success, None otherwise."""
        global player_deck
        if player_deck is None:
            return None
        plus_id = get_upgraded_id(card_id)
        if plus_id is None or plus_id not in CARD_LIBRARY:
            return None
        if card_id not in player_deck.cards:
            return None
        idx = player_deck.cards.index(card_id)
        player_deck.cards[idx] = plus_id
        return plus_id


    def grant_card(card_id, silent=False):
        """Force-add a card to the player's deck. Used by init_player_deck and dev label.

        Returns True if granted, False if unknown card or filtered by class lock.
        Shows the player a brief notification unless silent=True.
        """
        global player_deck
        if player_deck is None:
            return False
        if card_id not in CARD_LIBRARY:
            return False
        c = CARD_LIBRARY[card_id]
        if c.get("class_lock") and stats is not None and c["class_lock"] != stats.player_class:
            return False
        player_deck.add(card_id)
        if not silent:
            try:
                renpy.show_screen("card_acquired_toast", card=c)
                renpy.sound.play("audio/achivement_unlocked.mp3", channel="sound")
            except Exception:
                pass
        return True

    def can_offer_card(card_id):
        """Returns the card dict if offerable, None if filtered out.

        Pure-python predicate — no UI calls. Use BEFORE invoking the
        modal card-offer screen at script level.
        """
        if player_deck is None or card_id not in CARD_LIBRARY:
            return None
        c = CARD_LIBRARY[card_id]
        if c.get("class_lock") and stats is not None and c["class_lock"] != stats.player_class:
            return None
        return c


    def commit_card(card_id, took):
        """Caller invokes after the script-level `call screen card_offer_screen`
        returns. Adds card to deck if `took`. Returns `took` so callers can
        chain it: `$ _x = commit_card("foo", _return == "take")`.
        """
        if took and player_deck is not None and card_id in CARD_LIBRARY:
            player_deck.add(card_id)
        return bool(took)


    _LADDER_REWARD_WEIGHTS = {
        ## Battle rewards skew RARE so winning fights progressively powers
        ## the deck — beating monsters should feel materially stronger than
        ## the cards activities hand out. Activity grants are mostly commons
        ## / uncommons by design; ladder is where the rare power-ups live.
        "easy":   {"common": 0.50, "uncommon": 0.40, "rare": 0.10},
        "medium": {"common": 0.20, "uncommon": 0.40, "rare": 0.40},
        "hard":   {"common": 0.00, "uncommon": 0.30, "rare": 0.70},
    }

    ## Day-banded upgrade-roll for combat-reward cards. Each rolled reward
    ## checks `_plus` promotion AFTER the base rarity roll, with chance
    ## ramping over the 30-day run. Early run: an upgraded reward is a
    ## happy accident. Late run: a real possibility, never a guarantee.
    ## Tuning lever for balance-judge: edit these three rows.
    _LADDER_UPGRADE_DAY_CHANCE = (
        ## (max_day_inclusive, base_chance)
        (10,  0.03),  ## days 1-10  → 3%
        (20,  0.12),  ## days 11-20 → 12%
        (30,  0.25),  ## days 21-30 → 25%
    )
    _LADDER_UPGRADE_TIER_MULT = {
        ## Hard fights bias toward upgrades on top of biasing toward rares.
        "easy":   1.0,
        "medium": 1.25,
        "hard":   2.0,
    }
    _LADDER_UPGRADE_CHANCE_CAP = 0.50  ## even a Day-30 Hard fight tops out here


    def _ladder_pool_eligible(c):
        """Filter for the basic-reward pool: no class-lock, not boss-rarity,
        and not explicitly pool-excluded (status/curse cards opt out)."""
        if c.get("class_lock"):
            return False
        if c.get("rarity") == "boss":
            return False
        if c.get("pool_excluded"):
            return False
        return True


    def _weighted_choice(weights, _r):
        """weights: dict[label -> probability]. Returns the chosen label.
        Falls back to the first label if rounding leaves the roll above the
        last cumulative threshold."""
        roll = _r.random()
        cum  = 0.0
        last = None
        for k, w in weights.items():
            last = k
            cum += w
            if roll < cum:
                return k
        return last


    def _ladder_upgrade_chance(tier):
        """Compute the per-card upgrade-promotion probability for the
        current run-day and ladder tier. Reads day_cycle.current_day so
        late-run rewards lean upgraded; pure RNG below the cap."""
        try:
            _day = day_cycle.current_day if day_cycle is not None else 1
        except Exception:
            _day = 1
        _base = 0.0
        for _max_day, _chance in _LADDER_UPGRADE_DAY_CHANCE:
            if _day <= _max_day:
                _base = _chance
                break
        else:
            ## Past the last band — clamp to the highest tier's base chance.
            _base = _LADDER_UPGRADE_DAY_CHANCE[-1][1]
        _mult = _LADDER_UPGRADE_TIER_MULT.get(tier, 1.0)
        return min(_LADDER_UPGRADE_CHANCE_CAP, _base * _mult)


    def pick_battle_rewards(tier):
        """Pick 3 unique card_ids from the basic pool, weighted by tier.

        tier: 'easy' / 'medium' / 'hard' — Easy biases common, Hard biases
        uncommon/rare. Returns up to 3 ids; fewer only if the pool is too
        small for the requested rarities (won't happen in practice once
        Slice 3's cards ship).

        Each rolled reward then gets an independent shot at being
        PROMOTED to its `_plus` upgraded variant. Probability scales
        with `day_cycle.current_day` and `tier` — see _LADDER_UPGRADE_*
        constants. Cards without an `upgrade_to` (e.g. status / rage /
        compromise, though those never appear in the basic pool anyway)
        simply skip the roll and stay base.
        """
        import random as _r
        weights = _LADDER_REWARD_WEIGHTS.get(tier, _LADDER_REWARD_WEIGHTS["easy"])

        pool = [cid for cid, c in CARD_LIBRARY.items() if _ladder_pool_eligible(c)]
        buckets = {
            "common":   [c for c in pool if CARD_LIBRARY[c].get("rarity") == "common"],
            "uncommon": [c for c in pool if CARD_LIBRARY[c].get("rarity") == "uncommon"],
            "rare":     [c for c in pool if CARD_LIBRARY[c].get("rarity") == "rare"],
        }

        rolled = []
        attempts = 0
        while len(rolled) < 3 and attempts < 30:
            attempts += 1
            r = _weighted_choice(weights, _r)
            if not buckets.get(r):
                ## Fallback ladder: rare -> uncommon -> common
                for fallback in ("uncommon", "common"):
                    if buckets.get(fallback):
                        r = fallback
                        break
                else:
                    break
            cid = _r.choice(buckets[r])
            if cid not in rolled:
                rolled.append(cid)

        ## Promotion pass — independent per-card roll. Roll AFTER rarity
        ## picks so the upgrade chance compounds with the existing rare-
        ## bias on Hard fights (a Hard Day-25 fight rolls a rare AND has
        ## a 50% shot at upgrading it = the "this is the prize" feeling).
        _up_chance = _ladder_upgrade_chance(tier)
        if _up_chance > 0.0:
            promoted = []
            for cid in rolled:
                plus_id = get_upgraded_id(cid)
                if plus_id and plus_id in CARD_LIBRARY and _r.random() < _up_chance:
                    promoted.append(plus_id)
                else:
                    promoted.append(cid)
            rolled = promoted
        return rolled


    def offer_card(card_id, source_label="", pass_stats_text=""):
        """DEPRECATED for new activity callsites — use `can_offer_card` +
        script-level `call screen card_offer_screen(...)` + `commit_card`
        instead. Kept as a compatibility shim for event-file callsites
        (random_events / class_arcs / martin_meeting) that haven't been
        migrated yet.

        Calling `renpy.call_screen` from inside a python block leaves the
        transient layer's Many<Fixed> open under certain conditions
        (specifically: when followed by `window hide` + `show screen X` +
        `pause`). The next `pause` then crashes with "ui.interact called
        with non-empty widget/layer stack". Activities that hit that
        pattern MUST use the script-level path.
        """
        c = can_offer_card(card_id)
        if c is None:
            return False
        try:
            result = renpy.call_screen("card_offer_screen", card=c, source_label=source_label, pass_stats_text=pass_stats_text)
        except Exception:
            result = "take"
        return commit_card(card_id, result == "take")


    def offer_card_solo(card_id, source_label=""):
        """DEPRECATED — same caveat as `offer_card`. Use `can_offer_card` +
        `call screen card_solo_offer_screen(...)` + `commit_card` at
        script level instead.
        """
        c = can_offer_card(card_id)
        if c is None:
            return False
        try:
            result = renpy.call_screen("card_solo_offer_screen", card=c, source_label=source_label)
        except Exception:
            result = "take"
        return commit_card(card_id, result == "take")


    def show_outcome_panel(took_card, card_id, stat_text):
        """Phase 1 outcome panel renderer.

        Centralizes the post-offer panel branch so all activity sites use the
        same TAKE-vs-PASS rendering and can't drift from each other.

        - took_card: True if the player took the card (i.e. offer_card returned True)
        - card_id:   the card that was offered. Used to look up the display name on TAKE.
                     Pass None if there was no card offered (rare; usually call this
                     helper only when there's a real choice).
        - stat_text: the human-readable outcome string for the PASS branch — caller
                     formats this themselves (with all class bonuses, streak tags etc).

        The CALLER is responsible for applying the pending stat changes BEFORE calling
        this helper on the PASS branch. This keeps stat-mutation logic at the call site
        where it belongs (some sites have bespoke side-effects beyond simple deltas).
        """
        if took_card and card_id is not None:
            c = CARD_LIBRARY.get(card_id, {})
            text = "[CARD TAKEN] " + c.get("name", card_id)
        else:
            text = stat_text
        ## Return the text. Caller is responsible for `show screen
        ## outcome_panel(text)` at SCRIPT level (preceded by `window hide`).
        ## We used to call `renpy.show_screen` here from python, but doing
        ## that inside the same python block as `offer_card` (which calls
        ## `renpy.call_screen`) leaves the transient layer's Many<Fixed>
        ## open and the next `pause` trips ui.interact's stack check.
        return text


    def init_player_deck():
        """Build the starter deck for the chosen class. Called from init_game.

        StS-style baseline: every player gets a viable kit at game start —
        the class signature card plus 4×Strike and 4×Defend. The 30-day grind
        is about UPGRADING that kit (adding rares, replacing strikes), not
        building it from zero. The previous empty-deck pivot left DE and BH
        unable to deal any damage at the colonel fight if they didn't grind
        activities — the read_him / stack_up starters are utility, not damage.
        """
        global player_deck
        player_deck = PlayerDeck()
        cls = stats.player_class if stats else None

        ## Class-specific starter — the card that's about who JB is.
        if cls == "bodybuilder":
            player_deck.add("heavy_set")
        elif cls == "dark_empath":
            player_deck.add("read_him")
        elif cls == "biohacker":
            player_deck.add("stack_up")

        ## Universal baseline — muscle memory for the fight that's coming.
        for _ in range(4):
            player_deck.add("strike")
        for _ in range(4):
            player_deck.add("defend")
