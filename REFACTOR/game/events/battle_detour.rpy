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
        if tier == "easy":
            stats.increment_stats_value_money(-5000)
            stats.increment_stats_pcr_hatred(5)
            store._ladder_skip_tomorrow = True
            _detour_summary = "- 5,000 CZK   + 5 hatred   (next slot quiet)"
        elif tier == "medium":
            stats.increment_stats_value_money(-10000)
            stats.increment_stats_pcr_hatred(8)
            _detour_summary = "- 10,000 CZK   + 8 hatred"
        else:
            stats.increment_stats_value_money(-15000)
            stats.increment_stats_pcr_hatred(10)
            _detour_summary = "- 15,000 CZK   + 10 hatred"

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
