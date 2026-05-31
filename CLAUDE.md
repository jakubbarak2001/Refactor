# CLAUDE.md — REFACTOR

Project-level guidance for Claude. This file is auto-loaded every session.

## Project

**REFACTOR** is a Ren'Py game — visual novel / deckbuilder hybrid. Player is JB, a Czech cop trying to escape into tech over a 30-day countdown to a confrontation with the Colonel. Three character classes (Bodybuilder / Dark Empath / Biohacker), four difficulty tiers, ~20 random events, multiple endings.

**Status:** Mid-refactor. Phase 0 (balance + polish) → Phase 1 (deckbuilder pivot, replaces text-Colonel-fight with Slay-the-Spire-style turn-based deck battle) → Phase 2 (coding mini-game) → Phase 3 (new endings: Reunion). See `docs/REFACTOR_PLAYBOOK.md` for the full plan and per-phase checklists.

## Tech

- Ren'Py 8.x project at `REFACTOR/`
- Python game logic embedded in `init python:` blocks
- Entrypoint: `REFACTOR/game/script.rpy`
- All code lives in `REFACTOR/game/**/*.rpy`

## File map

| File | Role |
|------|------|
| `script.rpy` | Main 30-day loop, daily menu, all activities, salary, end-day |
| `python_logic.rpy` | `Stats`, `DayCycle` classes; difficulty/achievements/nootropic data |
| `screens.rpy` | All UI screens (stats bar, outcome panel, achievements, ending screen, difficulty/class selection) |
| `characters.rpy` | Character + image declarations |
| `endings.rpy` | All ending labels |
| `events/colonel_event.rpy` | Arc III boss fight (will be rewritten Phase 1 as deck battle) |
| `events/martin_meeting.rpy` | Day 24 Arc II event (8 phases, affection-gated buff/card grant) |
| `events/midnight_call.rpy` | Day 15 phone-call interlude |
| `events/random_events.rpy` | All `re_*` random events (pool of ~20, distilled v2) |
| `events/opportunity_events.rpy` | Bonus micro-events (no daily slot) |
| `events/car_incident.rpy` | Arc I prologue |
| `events/class_arcs.rpy` | 3-stage class-locked arcs (BB Trainer / DE Kovář / BH Telegram) |
| `cards/card_data.rpy` | PlayerDeck, CARD_LIBRARY, grant_card, offer_card |
| `cards/card_library.rpy` | All card definitions (45+) |
| `cards/card_effects.rpy` | Card effect functions + EFFECT_DESCRIPTIONS |
| `cards/colonel_deck.rpy` | Enemy deck (ENEMY_DECK_LIBRARY + COLONEL_DECK_TEMPLATES) |
| `cards/battle_engine.rpy` | BattleState class + battle_init/start/play/resolve |
| `cards/battle_screen.rpy` | Battle UI screen (hand, intent, energy, help, peek) |

## Critical conventions

### Stat mutations go through helpers
- `stats.try_spend_money(amount)` for purchases (returns False if insufficient)
- `stats.increment_stats_value_money(amount)`
- `stats.increment_stats_coding_skill(amount)`
- `stats.increment_stats_pcr_hatred(amount)`

Direct mutation (`stats.available_money -= X`) bypasses clamping and achievement triggers. Don't.

### Outcome panel text must match code math
The most common bug class in this codebase. If code does `+4000` to money, the `outcome_panel("+ 4000 CZK")` text must say 4000, not 3000. When class bonuses are involved (`+ _bb_cash`), the displayed text must reflect the conditional sum via `.format()` — not a hardcoded number.

### Daily activity contract
A new daily activity must:
1. Appear in `select_activity` menu (`script.rpy:269-297`)
2. Use `try_spend_money` for funds check (don't compare manually)
3. Set `activity_selected = True` before returning
4. End with `jump daily_menu`

### Random event contract
A new `re_*` event needs:
1. Standard structure: `scene bg_random_event` / `play sound "audio/police_siren.mp3"` / banner / narrative / menu / `return`
2. Entry in `random_event_pool` list (`script.rpy:1108-1133`)
3. Stat mutations through helpers

### Class gating
Three classes, exact-match strings: `"bodybuilder"`, `"dark_empath"`, `"biohacker"`. Class-specific menu options use Ren'Py condition syntax: `"...":  if stats.player_class == "X"`.

### Class progression state (GOTY v2)
Each class has a unique tracker initialized in `init_game`:
- BB: `store.bb_soma` (0-10, +1 per gym session). Battle: +1 starting block per 2 stacks.
- DE: `store.de_profiles` (dict of NPC keys → cold-read counts). Battle: +N peek per profile at 3+ reads.
- BH: `store.bh_protocol` (string: "Daily" / "Cognitive" / "Racetam" / "Peptide" / "Research"). Battle: +1 max energy if not Daily.

Plus 3-stage class arcs in `events/class_arcs.rpy` (BB Trainer / DE Kovář / BH Telegram), gated to day windows 6-10 / 12-18 / 20-26. Fire via `class_arc_check()` from `random_event_check`.

### Card grants
- `grant_card(card_id, silent=False)` — force-add (used by `init_player_deck` and dev label)
- `offer_card(card_id, source_label="")` — show TAKE/PASS prompt, grant on accept (used by activities and events)

### Ren'Py text escaping
- `[[` for literal `[` in displayed text
- `%%` for literal `%` in displayed text

### Don't add comments
Default to no comments. Only add when the WHY is non-obvious (per global rules). The codebase has very few comments by design — preserve that.

### Don't use `print()`
Invisible in Ren'Py. Use dialogue (`"text"`), `renpy.say(None, "...")`, or `outcome_panel(...)`.

## Workflow

### After any non-trivial change
Invoke the **`refactor-judge`** subagent — it reviews the diff for code-level bug patterns and reports back. If the change touched balance/economy, also invoke **`balance-judge`**.

```
Agent({subagent_type: "refactor-judge", prompt: "Review staged changes against REFACTOR conventions.", description: "Refactor code review"})
```

Don't commit unless the judge passes (or the warnings are explicitly accepted).

### Reference docs
- `docs/REFACTOR_PLAYBOOK.md` — pre-flight + post-flight checklists, templates for adding events / activities / endings / cards, common foot-guns
- (memory) `MEMORY.md` — auto-loaded; pointers to architecture, bugs, plans, balance design

## Working mode

Solo dev, GOTY-ambition bar, single-player Ren'Py game — actions are cheap and reversible. Default to acting, not asking. The judge subagents are the safety net for non-trivial changes; lean on them instead of pre-action caution.

- **Just do it.** Don't ask before editing `.rpy` files, running the game locally, deleting assets you've confirmed unused, or refactoring clearly-broken adjacent code. Act, then report what you did.
- **Pick a lane.** When asked for a recommendation, pick one and defend it. Don't enumerate alternatives unless I ask for a comparison.
- **Adversarial on plans.** When I propose a plan, your default is to find the strongest objection. If there isn't one, say "no objection" — don't manufacture weak ones to pad.
- **Adjacent-fix license.** Spot a clear bug nearby while doing a task? Fix it inline and mention it. Don't quarantine yourself to the literal request.
- **No hedge words.** Drop "might", "could consider", "one approach would be". Say what is or what to do.
- **No "what do you think?" trailers.** State the call. I'll redirect if I disagree.
- **GOTY bar.** Ship-quality > shipped-fast. If something's good-enough but not great, say so and propose the great version.

## Don'ts

- Don't add comments unless the WHY is non-obvious
- Don't create new docs/markdown files unless explicitly asked
- Don't bypass the stat helpers
- Don't use `print()`
- Don't keep the `dev_corrupt` debug difficulty when shipping (Phase 0 deletes it)
- Don't skip the judge on changes >20 lines

## Memory caveat

The auto-memory at `~/.claude/projects/.../memory/` is point-in-time and may be stale. The `project_renpy_migration.md` plan was executed (game is Ren'Py now). The `project_known_bugs.md` list is mostly fixed. Verify against current code before citing memory as fact.
