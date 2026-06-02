################################################################################
## REFACTOR — Overtime Resolution
##
## The OVERTIME activity (activity_overtime, script.rpy) is REFACTOR's
## Slay-the-Spire "?" node. The flat +5,000 CZK / +15 Hatred shift cost is
## paid first; the night then resolves via _roll_overtime():
##
##   - A pity-ramped chance of a battle-ladder fight. Starts at 10%; every
##     overtime that does NOT land a fight raises it by 10%; a fight resets
##     it to the 10% floor. Enemies are drawn from the SHARED battle ladder
##     pool (current day band) — overtime drains the same roster the daily
##     cycle does, and never repeats an enemy.
##   - Otherwise an StS-style choice event, drawn from the shared event pool
##     (random_event_pool) that the daily random-event slot also drains —
##     so an event seen on overtime never repeats in the daily slot.
##   - Otherwise the flat night roll back in activity_overtime.
################################################################################

init python:

    def _pick_overtime_event():
        """Drain one marquee event for the current arc band, or a recurring
        texture beat once every marquee has been seen.

        Overtime and the daily random-event slot share the marquee pool, so a
        marquee event seen one way never repeats the other."""
        _ensure_random_event_pool()
        day = day_cycle.current_day if day_cycle is not None else 1
        ev = _draw_marquee_event(day)
        if not ev:
            ev = _draw_recurring_event(day)
        return ev

    def _roll_overtime():
        """Decide what tonight's overtime resolves into.

        Returns one of:
            ("battle", enemy_id, tier)  fire battle_with(); pity resets to 10%
            ("event",  label, None)     fire an overtime narrative event
            ("flat",   None, None)      fall through to the flat night roll

        The pity counter (store.overtime_enemy_chance) only ramps and only
        rolls while the current day band still has enemies left in the ladder
        pool; once that band is cleared, overtime can no longer pull a fight
        there and falls through to events / flat roll.
        """
        import random
        _ladder_init_pool()
        if not hasattr(store, 'overtime_enemy_chance'):
            store.overtime_enemy_chance = 10

        tier = _battle_ladder_band(day_cycle.current_day)
        battle_pool = store.battle_ladder_pool.get(tier, [])

        if battle_pool:
            if random.randint(1, 100) <= store.overtime_enemy_chance:
                eid = random.choice(battle_pool)
                battle_pool.remove(eid)
                store.overtime_enemy_chance = 10
                return ("battle", eid, tier)
            store.overtime_enemy_chance = min(100, store.overtime_enemy_chance + 10)

        ev = _pick_overtime_event()
        if ev:
            return ("event", ev, None)
        return ("flat", None, None)
