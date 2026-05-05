# REFACTOR — Development Playbook

Workflow guide for changes to the REFACTOR Ren'Py game. Read `CLAUDE.md` first.

## Pre-flight (before any edit)

1. `git status` — am I on `master`? Are there pending changes from a different task?
2. Read the file(s) about to change. Don't trust memory — verify the current code.
3. Identify the contract — activity? event? ending? card? — and check the matching checklist below.
4. Make the smallest possible change that satisfies the requirement.

## Post-flight (before commit)

1. Invoke `refactor-judge` subagent on the diff (code-level review).
2. If the change touches balance/economy, invoke `balance-judge` (design-level review).
3. If FAIL: fix and re-judge. If WARN: review and accept-with-justification or fix.
4. Smoke-test by booting the game (`renpy.exe REFACTOR/`) — at minimum, reach the affected screen.
5. Commit with a descriptive message tied to the phase (`Phase 0:`, `Phase 1:`, etc).

---

## Checklist: Adding a Random Event

A random event fires every 3rd day before day 22, drawn without replacement from `random_event_pool`.

```
label re_my_new_event:
    scene bg_random_event
    play sound "audio/police_siren.mp3"
    "RANDOM EVENT — PRIORITY ALERT"

    "Setup narrative — what happened, where JB is."

    menu:
        "OPTION 1 — Outcome description":
            python:
                stats.increment_stats_value_money(2000)
            "Narrative result."
            show screen outcome_panel("+ 2000 CZK")    # MUST match the math above
            pause
            hide screen outcome_panel

        "OPTION 2 — Alternate path":
            ...

    return
```

Then add to the pool (`script.rpy:1108-1133`):

```
store.random_event_pool = [
    ...
    "re_my_new_event",
]
```

**Checklist:**
- [ ] Label name starts with `re_`
- [ ] Stat mutations use `increment_stats_*` helpers (not direct `-=`)
- [ ] Outcome panel text exactly matches the code math
- [ ] Added to `random_event_pool` (otherwise it never fires)
- [ ] If class-specific, gated with `if stats.player_class == "X"`
- [ ] Ends with `return`
- [ ] No `print()` calls

---

## Checklist: Adding an Opportunity Event

Opportunity events fire on non-event days at 30% chance. Do NOT consume the daily activity slot.

Same structure as random events but:
- Label starts with `opp_`
- Added to `_opportunity_pool` in `events/opportunity_events.rpy` `check_opportunity_event`
- Always offers a "Pass" option at zero cost
- Effect milder than random events (these stack with the day's activity)
- Does NOT set `activity_selected = True`

---

## Checklist: Adding a Daily Activity

```
label activity_xyz:
    scene bg_police_interior

    "Setup."

    menu:
        "PAY X CZK — Description":
            python:
                if not stats.try_spend_money(X):
                    renpy.say(None, "[[INSUFFICIENT FUNDS]] You need X CZK.")
                    renpy.jump("select_activity")
                # other stat effects via helpers
            "Narrative."
            show screen outcome_panel("- X CZK, +Y stat")
            pause
            hide screen outcome_panel
            python:
                activity_selected = True
            jump daily_menu

        "Return to menu.":
            jump daily_menu
```

Expose in `select_activity` (`script.rpy:269-297`):

```
"NEW ACTIVITY — description":
    jump activity_xyz
```

**Checklist:**
- [ ] `try_spend_money` checks funds (don't compare `.available_money` manually)
- [ ] `activity_selected = True` set before exit
- [ ] Ends with `jump daily_menu`
- [ ] Class-gated if applicable
- [ ] Outcome text matches code math

---

## Checklist: Rebalancing Stat Values

When changing an existing value (e.g. gym hatred reduction 25 → 30):

- [ ] Update the code (e.g. `stats.increment_stats_pcr_hatred(-30)`)
- [ ] Update the outcome panel text in the same block
- [ ] Search for sister mechanics that should rebalance proportionally — other gym roll outcomes (`script.rpy:336-350`), class-bonus stacking (`_bb_bonus`, etc.)
- [ ] Update memory `project_game_balance.md` if the change is design-level
- [ ] Test the affected difficulty tiers (Easy / Hard / Insane / Ultra)

---

## Checklist: Adding an Ending

```
label my_new_ending:
    play music "audio/<mood>.mp3" fadein 1.0
    scene bg_<location>

    "Narrative beats."

    python:
        _base_score = (stats.available_money / 100) + (stats.coding_skill * <weight>)
        _diff_mult  = {"easy": 1.0, "hard": 2.5, "insane": 5.0, "ultra": 10.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult * <ending_multiplier>)
        _diff_name  = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "<TYPE> ENDING",
        "<TITLE>",
        "<flavor text>",
        "<ending_type>",  # good/bad/perfect/bittersweet/difficult/neutral/burnout/secret
        score=_final_score,
        score_note="x{} ...".format(<ending_multiplier>),
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    $ renpy.full_restart()
```

**Checklist:**
- [ ] Trigger condition unambiguous — no overlap with other endings
- [ ] Trigger lives in `script.rpy` `day_start` or `do_end_day` for stat-based endings, or in event labels for event-based
- [ ] Music + scene set the tone
- [ ] Score calc includes difficulty multiplier
- [ ] Achievement unlocked if appropriate (`unlock_achievement("key")`)
- [ ] Ends with `renpy.full_restart()`
- [ ] Class epilogues added if narratively appropriate (see `good_ending` / `escape_artist_ending` for the pattern)

---

## Checklist: Adding a Card (Phase 1+)

*Deferred until the deckbuilder system is built. Will live in `cards/card_data.rpy`.*

- [ ] Card defined in central library with `id`, `name`, `type`, `color`, `cost`, `rarity`, `effect_fn`, `flavor`, `art`
- [ ] `effect_fn(battle_state, target)` is pure-ish — no global mutation outside `battle_state`
- [ ] Cost / rarity classified per the curve in `balance-judge.md`
- [ ] Source defined — which activity / event grants it
- [ ] Class-locked if applicable (must reinforce class identity, not power-creep)
- [ ] Tested against current colonel deck (winnable but not trivial)

---

## Foot-guns reference

### Outcome panel desync (most common bug)
```
stats.increment_stats_value_money(4000)
show screen outcome_panel("+ 3000 CZK")    # WRONG
```
Fix: update string to match the code value.

### Class-bonus arithmetic
```
_bb_cash = 1500 if stats.player_class == "bodybuilder" else 0
stats.increment_stats_value_money(4000 + _bb_cash)
show screen outcome_panel("+ 4000 CZK")    # WRONG when BB
```
Fix: `outcome_panel("+ {} CZK".format(4000 + _bb_cash))`.

### Bypassing helpers
```
stats.available_money -= 80000     # WRONG
stats.increment_stats_value_money(-80000)    # RIGHT
```
The helpers handle clamping and achievement triggers. Always use them.

### Hatred floor
`increment_stats_pcr_hatred(-X)` clamps at 0. Hatred is never negative. Don't try to use negative hatred as a state.

### Coding skill ceiling
`increment_stats_coding_skill(X)` clamps at 250 and unlocks `"hackerman"`. Don't manually clamp.

### Bare `print()`
Invisible in Ren'Py. Use dialogue (`"text"`), `renpy.say(None, "...")`, or `outcome_panel(...)`.

### Ren'Py text escaping
- `[[X` displays `[X` (single bracket needs to be doubled or it's interpreted as interpolation)
- `100%%` displays `100%` (single `%` is for printf-style interpolation)

### `from _call_X` clauses
Ren'Py auto-generates these for `call <label>`. Don't remove them — they pin save/load to specific call sites. If you rename a label, regenerate by running the game once.

### Audio file paths
All audio referenced as `"audio/X.mp3"` resolves relative to `REFACTOR/game/`. Verify the file exists in `REFACTOR/game/audio/` before referencing — Ren'Py won't error at parse time, only at runtime when the line is reached.

### Double night cycle
Random events historically fired an extra night cycle (memory bug #16). Adding a new "trigger event" pattern — be alert that you don't double-apply nightly passives.

---

## Invoking the judges

After any non-trivial change, the parent agent calls:

```
Agent({
  subagent_type: "refactor-judge",
  description: "Code review of staged changes",
  prompt: "Review the staged changes in git against REFACTOR conventions. Report CRITICAL/WARN/OBS."
})
```

If the change is balance-impacting (numeric values, new mechanics):

```
Agent({
  subagent_type: "balance-judge",
  description: "Balance review of staged changes",
  prompt: "Evaluate the design impact of the staged changes. Project 30-day budget at each difficulty."
})
```

Both judges return a structured report. Address CRITICAL items before committing. Run them in parallel — they read different things.

---

## Optional: hook-driven auto-review

To remind yourself to invoke the judge after every Edit/Write to .rpy files, add to `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "echo 'REMINDER: invoke refactor-judge before commit' >&2"
      }]
    }]
  }
}
```

Note: this only prints a reminder. Auto-spawning the judge from a hook needs the headless Claude CLI and is more setup than it's worth at this stage.
