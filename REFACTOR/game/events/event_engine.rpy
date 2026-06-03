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

    ## ── ARC-banded event pools ─────────────────────────────────────────────
    ## Marquee StS events are tagged to an ARC band so the right beat fires at
    ## the right time:
    ##   early = ARC I  (the precinct, the body, onboarding-tone gambles)
    ##   mid   = ARC II (the tech pull, deal-making, deck-craft)
    ##   late  = ARC III (the Colonel closing in, the escape on the line)
    ## The pool is a dict band -> [ids], drained with no repeats; the daily slot
    ## and the Overtime activity both draw from it. init_game sets
    ## store.random_event_pool = None; this refills it on next access.
    ## ev_the_smell / ev_karaoke / ev_photocopier CUT from rotation (the weakest
    ## surreal beats) — labels kept in random_events.rpy but no longer pooled.
    EVENT_BANDS = {
        "ev_the_vending_machine": "early",
        "ev_pills":               "early",
        "ev_synthol_brothers":    "early",   ## BB-only (class-gated below)
        "ev_the_collector":       "early",   ## event-launched fight (debt enforcer)
        "ev_designer_of_forms":   "mid",
        "ev_lost_and_found":      "mid",
        "ev_uniform_collector":   "mid",
        "ev_the_quartermaster":   "mid",     ## choose-1-of-3 gear (relic shelf)
        "ev_the_range":           "mid",     ## deck-craft — remove/upgrade for HP
        "ev_bh_acd856_offer":     "mid",     ## BH-only (class-gated below)
        "ev_the_interview":       "late",
        "ev_colonel_regards":     "late",
        "ev_the_tail":            "late",    ## event-launched fight (Colonel's reach)
        "ev_the_side_gig":        "mid",     ## CODING — freelance gig (skill for HP)
        "ev_the_contract":        "late",    ## CODING — a real job offer, big skill score
    }

    ## Recurring "station texture" beats — short, low-stakes, and NOT drained,
    ## so the world keeps breathing between the marquee events. Fired as the
    ## fallback whenever an event slot has no marquee event queued.
    RECURRING_EVENTS = ["evr_the_briefing", "evr_coffee_machine", "evr_locker_room", "evr_bad_call"]

    ## Days that force a narrative beat even if ladder fights remain — so the
    ## ARC-banded marquee events reliably surface (battles otherwise pre-empt
    ## them, per roll_ladder_or_event). One early + one late slot; the BB arc
    ## (class_arc_check) owns days 6/15/21, the act bosses own 24/colonel.
    EVENT_GUARANTEE_DAYS = {9, 18}

    _BAND_FALLBACK = {
        "early": ["early", "mid", "late"],
        "mid":   ["mid", "early", "late"],
        "late":  ["late", "mid", "early"],
    }

    def _arc_band(day):
        return {"easy": "early", "medium": "mid", "hard": "late"}.get(_battle_ladder_band(day), "mid")

    def _ensure_random_event_pool():
        if getattr(store, 'random_event_pool', None) is None:
            _pool = {"early": [], "mid": [], "late": []}
            _is_bb = (stats is not None and stats.player_class == "bodybuilder")
            _is_bh = (stats is not None and stats.player_class == "biohacker")
            for _eid, _band in EVENT_BANDS.items():
                if _eid == "ev_synthol_brothers" and not _is_bb:
                    continue
                if _eid == "ev_bh_acd856_offer" and not _is_bh:
                    continue
                _pool[_band].append(_eid)
            store.random_event_pool = _pool
        ## Back-compat: an in-progress save built before the banded rework holds
        ## a flat list — rebuild it into the banded dict.
        if isinstance(getattr(store, 'random_event_pool', None), list):
            store.random_event_pool = None
            _ensure_random_event_pool()

    def _marquee_events_left():
        _ensure_random_event_pool()
        p = store.random_event_pool
        return sum(len(p.get(b, [])) for b in ("early", "mid", "late")) > 0

    def _draw_marquee_event(day):
        """Pick + remove one marquee event for `day`, preferring the day's arc
        band and falling back to adjacent bands. Returns the id, or None when
        every marquee event has been seen this run."""
        import random as _r
        _ensure_random_event_pool()
        p = store.random_event_pool
        for b in _BAND_FALLBACK.get(_arc_band(day), ["early", "mid", "late"]):
            if p.get(b):
                eid = _r.choice(p[b])
                p[b].remove(eid)
                return eid
        return None

    def _draw_recurring_event(day):
        """Pick a recurring texture event (NOT removed — they recur). Avoids
        repeating the immediately-previous one when possible."""
        import random as _r
        _last = getattr(store, '_last_recurring_event', None)
        pool = [e for e in RECURRING_EVENTS if e != _last] or list(RECURRING_EVENTS)
        if not pool:
            return None
        eid = _r.choice(pool)
        store._last_recurring_event = eid
        return eid

    ## ── Run-HP helpers ────────────────────────────────────────────────────
    ## run_hp is the persistent battle-HP pool. It stays None until the first
    ## battle lazy-inits it (battle_engine.battle_init). An event can fire
    ## before any battle, so these init it from the class max on demand.

    def _event_class_max_hp():
        ## Thin wrapper around the canonical class_max_hp helper in
        ## python_logic.rpy. Previously inlined a stale `80 + _gym` for
        ## BH, which silently broke event_heal after the HP buff to 90.
        return class_max_hp()

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
