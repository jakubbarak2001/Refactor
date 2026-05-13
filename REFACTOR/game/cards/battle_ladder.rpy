################################################################################
## REFACTOR — Battle Ladder
##
## Slot rotation: random_event_check (script.rpy) consults
## roll_ladder_or_event(day) to decide between a ladder fight and the
## narrative random-event pool. Ladder pool drains as battles fire
## (no repeats per run) and is keyed by day band:
##     easy (d3-9)   = rvac / sprejeri / fanousek / spis
##     medium (d9-18)= nguyen / varic / pastyrak / dispatcher
##     hard (d19-30) = inspekce / garda
## The Colonel (Day 30) stays on his own colonel_event label — his
## multi-phase resolution and ending-jump logic are NOT routed through
## the wrapper.
##
## battle_with(enemy_id, tier) is the wrapper label:
##     init  -> screen -> outcome -> (forced_detour OR card_reward_trio)
################################################################################

default _ladder_skip_tomorrow = False


init python:

    def _battle_ladder_band(day):
        if day <= 9:
            return "easy"
        if day <= 18:
            return "medium"
        return "hard"

    def _ladder_init_pool():
        """Lazy-init the per-run drainable ladder pool."""
        if not hasattr(store, 'battle_ladder_pool') or store.battle_ladder_pool is None:
            store.battle_ladder_pool = {
                "easy":   ["rvac", "sprejeri", "fanousek", "spis"],
                "medium": ["nguyen", "varic", "pastyrak", "dispatcher"],
                "hard":   ["inspekce", "garda"],
            }

    def roll_ladder_or_event(day):
        """Decide what fires this random-event slot.

        Returns:
            ('battle', enemy_id, tier)  fire battle_with(enemy_id, tier)
            ('event',  None, None)      fall through to narrative pool
            (None,     None, None)      silent slot (Easy-loss penalty)

        Battles STRICTLY take priority over narrative events: as long as the
        current tier's battle pool has enemies, the slot is a battle. Events
        only fire on a tier where the pool is drained. This was a player
        request — random events felt like dead air between fights.
        """
        import random as _r
        _ladder_init_pool()

        if getattr(store, '_ladder_skip_tomorrow', False):
            store._ladder_skip_tomorrow = False
            return (None, None, None)

        tier = _battle_ladder_band(day)
        battle_pool = store.battle_ladder_pool.get(tier, [])

        if battle_pool:
            eid = _r.choice(battle_pool)
            battle_pool.remove(eid)
            return ("battle", eid, tier)

        event_pool = getattr(store, 'random_event_pool', []) or []
        if event_pool:
            return ("event", None, None)

        return (None, None, None)


## ---------------------------------------------------------------------------
## battle_with — generalised entry point for any ENEMY_LIBRARY enemy.
## Colonel keeps colonel_event; this wrapper handles ladder rungs only.
## ---------------------------------------------------------------------------

label battle_with(enemy_id, tier):

    if tier == "medium":
        play music "audio/system_knows_better.mp3" fadein 0.8
    elif tier == "hard":
        play music "audio/kryty_spis.mp3" fadein 0.8
    else:
        play music "audio/panelak_loop.mp3" fadein 0.8
    $ renpy.save("auto-ladder", "Ladder — {}".format(enemy_id))

    python:
        battle_init(enemy_id)
        battle_start_player_turn()

    call screen battle_screen

    python:
        _outcome = battle_outcome()
        battle_finish()

    if _outcome == "defeat":
        call forced_detour(enemy_id, tier)
        return

    python:
        _rewards = pick_battle_rewards(tier)

    if _rewards:
        call screen card_reward_trio_screen(cards=_rewards)
        python:
            if _return and _return not in ("skip", None):
                grant_card(_return, silent=False)

    return
