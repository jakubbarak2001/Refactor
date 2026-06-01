# REFACTOR — State of the Game & Roadmap

**Last updated:** 2026-06-01 (after a full playtest-and-build session — 21 commits)
**Purpose:** the single go-forward reference. Where the game is, what we learned today, and what's next. Read this first, then `REFACTOR_PLAYBOOK.md` (how-to) and the auto-memory `MEMORY.md`.

---

## 1. The Vision (the GOTY thesis)

REFACTOR is a **Slay-the-Spire-style deckbuilder fused with a 30-day life-sim**. JB, a Czech cop, claws his way out of a corrupt precinct into tech, racing a countdown to a final confrontation with the Colonel — and **HATRED is his death clock** (you lose at the cap; crossing 40/60/80 jams permanent Rage cards into the deck).

**The moat is the theme.** Slay the Spire is fantasy wallpaper; Balatro is abstract. REFACTOR is *specific* — the panelák, the Fixer, bribing Internal Affairs, the breach team yelling POLICIE, the Colonel as a 32-year `police_bureaucracy.exe` loop. No other deckbuilder has this. **Every system should sharpen the theme, not just the numbers.**

**The governing principle (learned today): the 30-day run must COMPOUND.** A great game you beat once becomes a GOTY game you replay 80 times only when the systems agree mechanically — builds snowball, the climax reads your history, and a meta-loop pulls you back. Today's work was largely about making that true.

**Scope note:** only the **Bodybuilder (BB)** class is playable. Dark Empath / Biohacker are locked (their cards/arcs exist but are out of scope). Balance for BB.

---

## 2. State of the Game (post-session)

### Builds — all three now snowball
BB can build three distinct, draftable archetypes, each with a build-defining **finisher** added today:
- **Hatred** — generators (Provoke/Sparring Partner) feed See Red (block/gain) + Roid Rage (now `+Hatred//20` per gain). Finisher: **Breakdown** (rare) — deal damage = your entire Hatred, then lose it all. Snowball the clock, then detonate it.
- **Stoic** — block fortress. Counterweight cap lifted **15→40**. Finisher: **Barricade** (rare Power) — keep ALL block each turn (Iron Posture keeps half), so the wall compounds into Counterweight-able numbers.
- **Tech** — energy/cycle. Finisher: **Pipeline** (rare Power) — every card you play chips the enemy for your Coding tier. Makes Coding matter in combat for BB and gives tech a persistent anchor.

The finishers start **locked** and unlock by *proving the build* in a fight (Hatred≥80, block≥40, Coding≥100), live and cross-run.

### Meta-progression — the "one more run" engine (NEW, v1)
Previously there was **zero** cross-run persistence. Now:
- Achievements persist (`persistent.achievements_unlocked`) — a real trophy collection.
- **Card unlock pool** (`persistent.unlocked_cards`) gates the draft + Fixer shop; the finishers drip in via milestones; a win safety-unlocks the rest.
- **Run record**: `persistent.runs_won` + `persistent.best_score`, shown on the trophies screen.
- **Difficulty select is live** (was hardcoded to easy) — easy/hard/insane reach the 2.5×/5× score multipliers and 7/9-card Colonel decks that were dead content.

### The Colonel — two-phase, threat over bulk
At ≤50% HP the bureaucracy act drops and he turns your run against you (Hatred→harder hits, Coding→energy debuff, bribes/pacifist→tailored beats) **and enrages**: +3 Strength/round (cap 15), an uncounterable escalation that makes the back half a race. HP trimmed 340→300 (gift +40) so it's tense, not a slog. The BB ending now branches on how you won.

### Economy & difficulty
- Bouncer is BB's money engine: rarity roll ~15k/20k/25k (EV ~17.5k/shift).
- Relics priced as real sinks (Taser 50k, Red Bull 30k, Protein/Duck 15k). Golden Handcuffs redesigned to **+25% money from any source** (was an OP energy bump).
- The Fixer is a proper **unified shop screen** (cards as widgets + gear + shred), every 5th day with a collision-shift so it's reliably reachable.
- Per-enemy **flee outcomes** are a rich design space: Bar Brawler −1k penalty, Vlk +1k/day crypto, Grundza's batch (heal+maxHP), IA/Guard bribes (+Hatred, −CZK). The flee system supports relief, cost, income, heal, max-HP, label, and bespoke narration per enemy.

### Difficulty curve (ladder)
Easy tier has teeth (per-enemy HP/damage/scaling wrinkles); Garda (Act II) is a real wall (320 HP + escalating formation strength + anti-passive); Nguyen buffed; the `no_double_passive` flag (garda/inspekce) makes bosses attack ≥ every 2nd turn.

---

## 3. What we did today (by theme)

**Builds & finishers:** Breakdown / Barricade / Pipeline; Roid Rage scaling; Counterweight uncap; Heavy Set+ now scales `8 + Hatred//3` (was flat +2); The Final Set 30→50; Adrenaline Dump exhausts.

**Meta-progression:** persistent achievements + card unlocks + run record; difficulty select enabled.

**Colonel:** two-phase rework + run-aware ending; threat-over-bulk pass (HP trim + enrage); HP-inversion fix.

**Ladder/enemies:** easy-tier teeth pass; Garda menace; Nguyen buff; Hooligan crew-rage 60%→25%; bribe/flee outcomes per enemy; Arc-I upgrade gate; "Peace Was Never An Option" achievement; hid 3 events for re-tuning (smell/karaoke/photocopier).

**Economy/UI:** Fixer unified shop + cadence; Bouncer rarity payout; relic prices; Golden Handcuffs redesign; relic icons wired + crisp + 2x + 5-per-row wrap; encounter screen cleanup; shredder now shows real card faces; day-15 CALL artifact removed.

**Bugs:** vending +Max HP persistence (and the broader `run_max_hp_bonus` generalization + the battle_init max-HP-resync fix so earned max HP is never wiped — only reconciled upward); event-pool cache scrub for in-progress saves.

**Art:** Strike (JB lunging punch) + Breakdown (mental-breakdown) card art in the painterly BB style; paragraph_4b swap. Prompts saved in `tools/prompts/`, variants archived in `images/cards/_variants/`.

---

## 4. Insights from playtesting (the lessons)

1. **Theme is the moat — lean into it.** The bespoke flee outcomes (crypto, batch, bribes) and the Colonel's glitch are what make REFACTOR *itself*. Keep mechanics that only make sense as a Czech cop escaping a corrupt boss.
2. **Compounding beats flat.** Every build payoff was a flat tax that the late game laughed off. The fix pattern: one **uncapped scaling finisher** per lane.
3. **A high-HP boss without escalating threat is a meatball.** The Colonel was tanky-but-boring; worse, his story-attacks get **negated by your counter items**, so engaging with the run made him *more* toothless. The fix isn't HP — it's an **uncounterable, escalating threat** (the enrage) that makes the fight a race.
4. **Dead content is invisible.** The difficulty tiers + score multipliers were fully built and switched off behind one hardcoded line. Audit for built-but-unwired systems.
5. **Persistence has gotchas.** Ren'Py reserves `persistent._` (leading underscore) names; per-run caches (event pool, run_hp_max) need scrubs/reconciliation so in-progress saves get fixes. Reconcile max HP **upward only** — it never drops mid-run.
6. **The judges are stale** — verify via lint + reading the source, not the refactor/balance-judge verdicts (per the user). They still occasionally catch a real bug, but treat that as a lead to verify, not a gate.

---

## 5. Future Roadmap (prioritized)

### High leverage / still open
1. **Coding lane fix (OPEN, flagged in playtest).** Coding cards feel weak for BB and Coding *skill* is hard to get — the only source is the 35k bootcamp, unaffordable early on insane. Tech has only **one** BB-accessible Coding anchor (Pipeline); the real Coding-scaled engine cards are BH-locked. **Proposed fix:** make BB's STUDY days grant Coding XP (a cheap, day-cost path), and/or add 1–2 BB-accessible Coding-scaling cards, so the tech build is reachable without the bootcamp wall.
2. **SFX assets (asset drop, zero code).** `card_skill`, `card_power`, `end_turn` + victory/defeat stings fire into silence — half the combat is mute. Source/record per `audio/sfx/REQUIRED_SFX.md` and drop them in. Then route hatred-climb music (breakdown_theme / heartbeats) on the 60/80 bands.
3. **Full ascension ladder + relic unlock pool.** Today shipped difficulty-on + a card unlock pool. Next: escalating per-clear modifiers (reuse `DIFFICULTY_SETTINGS`) and persisting unlocked relics.
4. **Playtest & balance the new OP builds + Colonel.** Breakdown at 120 Hatred, Pipeline at Coding tier 5, Barricade+Counterweight loop, the Colonel enrage cap — all want real-hands tuning.

### Medium
5. **Colonel polish:** a signature telegraphed move; deeper ending branches; make the colonel_day 25-vs-30 choice change the fight, not just its timing.
6. **Re-tune & re-enable the 3 hidden events** (ev_the_smell / ev_karaoke / ev_photocopier — pull the id from `_HIDDEN_EVENTS`).
7. **More card art** in the painterly style for cards still on glyph fallback.

### Long-term
8. **DE/BH unlock** (currently BB-only) — design non-peek class identities (no peek-intent mechanics, per house rule).
9. **Coding mini-game** (the original Phase 2 idea) if the coding lane warrants it.

---

## 6. Key systems — where to look

- **Builds/cards:** `cards/card_library.rpy` (defs), `cards/card_effects.rpy` (effects + dynamic descriptions), `cards/card_data.rpy` (draft pool, `_ladder_pool_eligible`, unlock gate).
- **Combat:** `cards/battle_engine.rpy` (BattleState, wrinkles, the Colonel phase-2 block ~line 942, `gain_hatred`/`gain_block` unlock hooks).
- **Meta-progression:** `python_logic.rpy` (`card_unlocked`/`unlock_card`/`META_LOCKED_CARDS`, `unlock_achievement` → persistent, the milestone hooks in the stat mutators); `endings.rpy` (run record before `full_restart`); trophies UI in `screens.rpy`.
- **Enemies/flee/bosses:** `cards/enemy_data.rpy` (defs + the flee_* fields + `no_double_passive` + `build_enemy_deck`), `cards/colonel_deck.rpy` (intents + Colonel deck), `cards/battle_ladder.rpy` (`flee_effects`, `boss_check`, `BATTLE_MONEY_REWARD`, `LADDER_EVENT_DAYS`/`fixer_visits_today`).
- **Fixer shop:** `screen fixer_shop` in `screens.rpy`, driven by `fixer_shop_loop` in `script.rpy`.
- **Art pipeline:** `tools/gen_bg.py` (`--cards`/`--sprites`/`--relics` + `--ref` style images), prompts in `tools/prompts/`.
