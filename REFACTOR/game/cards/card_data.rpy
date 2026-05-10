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
        """Register a card definition. Idempotent — last registration wins."""
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
            "flavor":     "",
            "art":        None,
        }
        defaults.update(fields)
        defaults["id"] = card_id
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
