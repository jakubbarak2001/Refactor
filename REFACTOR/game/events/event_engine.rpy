################################################################################
## REFACTOR — Event Engine
##
## Shared helpers for the Slay-the-Spire-style choice events. The two screens
## live in events/event_screen.rpy; the per-event ev_* labels (random_events.rpy)
## build their choice lists and drive them.
##
## Event-design rule: events trade in HP / cards / CZK / hatred only — the
## things the player actually feels. No "+1 coding" noise, no "no change"
## branch. Every choice costs something real.
################################################################################

init python:

    ## ── Choice-line formatters ────────────────────────────────────────────
    ## Inline color spans for the cost / gain / keyword text on a choice bar.
    ## Red = it costs you. Green = you gain. Gold = a thing worth naming.

    def ec(s):
        """Cost span — red."""
        return "{color=#e0563c}" + s + "{/color}"

    def eg(s):
        """Gain span — green."""
        return "{color=#6fc98a}" + s + "{/color}"

    def ek(s):
        """Keyword span — gold."""
        return "{color=#e8c878}" + s + "{/color}"

    ## ── Shared event pool ─────────────────────────────────────────────────
    ## The 10 ev_* events live in ONE pool, drained by two channels — the daily
    ## random_event_check slot and the Overtime activity — with no repeats
    ## across a run. init_game sets store.random_event_pool = None; this refills
    ## it on the next access.

    def _ensure_random_event_pool():
        if getattr(store, 'random_event_pool', None) is None:
            store.random_event_pool = [
                "ev_the_vending_machine", "ev_the_smell", "ev_designer_of_forms",
                "ev_lost_and_found", "ev_colonel_regards", "ev_pills",
                "ev_uniform_collector", "ev_karaoke", "ev_the_interview",
                "ev_photocopier",
            ]

    ## ── Run-HP helpers ────────────────────────────────────────────────────
    ## run_hp is the persistent battle-HP pool. It stays None until the first
    ## battle lazy-inits it (battle_engine.battle_init). An event can fire
    ## before any battle, so these init it from the class max on demand.

    def _event_class_max_hp():
        _gym = getattr(store, 'gym_max_hp_bonus', 0)
        _cls = stats.player_class if stats is not None else None
        if _cls == "bodybuilder":
            return 115 + _gym
        if _cls == "dark_empath":
            return 75 + _gym
        if _cls == "biohacker":
            return 80 + _gym
        return 80 + _gym

    def _event_ensure_run_hp():
        if getattr(store, 'run_hp_max', None) is None:
            store.run_hp_max = _event_class_max_hp()
        if getattr(store, 'run_hp', None) is None:
            store.run_hp = store.run_hp_max

    def event_heal(n):
        """Heal n run-HP, clamped to run_hp_max. Returns HP actually restored."""
        _event_ensure_run_hp()
        _before = store.run_hp
        store.run_hp = max(1, min(store.run_hp_max, store.run_hp + n))
        return store.run_hp - _before

    def event_hurt(n):
        """Lose n run-HP, floored at 1 — events never kill. Returns HP lost."""
        _event_ensure_run_hp()
        _before = store.run_hp
        store.run_hp = max(1, store.run_hp - n)
        return _before - store.run_hp

    ## ── Card transform ────────────────────────────────────────────────────
    ## No native transform exists — compose it from remove + grant. The
    ## replacement is rolled from the same reward-eligible pool the battle
    ## ladder draws from, biased to the removed card's rarity.

    def event_transform_card(card_id):
        """Remove one copy of card_id and grant a random different card of the
        same rarity where possible (else any reward-eligible card). Returns the
        new card id, or None if the deck has no such card / the pool is dry."""
        import random as _r
        if player_deck is None or card_id not in player_deck.cards:
            return None
        _rar = CARD_LIBRARY.get(card_id, {}).get("rarity", "common")
        _pool = [cid for cid, c in CARD_LIBRARY.items()
                 if _ladder_pool_eligible(c) and cid != card_id]
        _same = [cid for cid in _pool if CARD_LIBRARY[cid].get("rarity") == _rar]
        _choices = _same or _pool
        if not _choices:
            return None
        player_deck.remove(card_id)
        _new = _r.choice(_choices)
        grant_card(_new, silent=True)
        return _new
