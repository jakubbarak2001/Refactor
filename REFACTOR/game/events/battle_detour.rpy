################################################################################
## REFACTOR — Forced Detour
##
## Shared loss handler for ladder fights. Tier-scaled stat/money/hatred cost;
## Easy-tier loss also sets _ladder_skip_tomorrow so the next slot is silent
## (the case files itself, the day after is too quiet to fight). Per-enemy
## flavor narration is read from ENEMY_LIBRARY[enemy_id]["detour_lines"].
##
## Slice 2 ships the mechanics + a generic banner. Slice 4 adds the per-enemy
## narration lines (the detour_lines field already exists in the schema).
################################################################################

label forced_detour(enemy_id, tier):

    scene bg_black with fade
    show screen detour_header("CASE WENT BAD")

    python:
        _ed = ENEMY_LIBRARY.get(enemy_id, {})
        _detour_lines = _ed.get("detour_lines", [])

    if _detour_lines:
        python:
            for _line in _detour_lines:
                renpy.say(None, _line)
    else:
        "You lost. The case files itself."

    python:
        ## Hospital sticks the player with a run-HP cost that carries forward
        ## into the next fight. Tier-scaled. Floor at 10 HP — keeps the run
        ## technically winnable but punishing. HP is the new persistent
        ## penalty since the old skip-tomorrow slot is gone (the player still
        ## has to fight the next slot — just worse off).
        _run_hp_max = getattr(store, 'run_hp_max', 115) or 115
        _cur_hp = getattr(store, 'run_hp', _run_hp_max) or _run_hp_max
        if tier == "easy":
            stats.increment_stats_value_money(-5000)
            stats.increment_stats_pcr_hatred(5)
            _hp_loss = 10
        elif tier == "medium":
            stats.increment_stats_value_money(-10000)
            stats.increment_stats_pcr_hatred(8)
            _hp_loss = 15
        else:
            stats.increment_stats_value_money(-15000)
            stats.increment_stats_pcr_hatred(10)
            _hp_loss = 20
        store.run_hp = max(10, _cur_hp - _hp_loss)
        _detour_summary = "- {:,} CZK   + {} hatred   - {} HP (hospital)".format(
            5000 if tier == "easy" else (10000 if tier == "medium" else 15000),
            5 if tier == "easy" else (8 if tier == "medium" else 10),
            _hp_loss,
        )

        ## Loss-stacking (vision §2 — multiple stalls degrade the run).
        ## First loss is just the stat cost; second and subsequent losses
        ## also inject a permanent UNPLAYABLE Compromise card into the deck.
        ## The deck IS the 30 days; bad weeks stick.
        store._battle_losses = getattr(store, '_battle_losses', 0) + 1
        if store._battle_losses >= 2:
            grant_card("compromise", silent=False)
            _detour_summary += "\n[CORRUPTION] + Compromise (dead weight in deck)"

    hide screen detour_header
    show screen outcome_panel(_detour_summary)
    pause 2.2
    hide screen outcome_panel
    return


screen detour_header(banner_text):
    layer "screens"
    zorder 250
    frame:
        xalign 0.5
        yalign 0.18
        padding (40, 18)
        background Frame("#1a0000ee", 4, 4)
        text banner_text:
            color "#ff4444"
            size 42
            bold True
            xalign 0.5
            font "fonts/RobotoMono-Regular.ttf"
            outlines [(2, "#000000aa", 0, 0)]
