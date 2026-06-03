# REKURZE — State of the Game & Roadmap

> **The game is now named REKURZE** (renamed from REFACTOR, 2026-06-03 — see the top handoff section). This doc keeps its old filename/history; "REFACTOR" in older sections is the former title.

**Last updated:** 2026-06-03 (evening: Biohacker overhaul + REKURZE rename; all pushed)
**Purpose:** the single go-forward reference. Where the game is, what we learned today, and what's next. Read this first, then `REFACTOR_PLAYBOOK.md` (how-to) and the auto-memory `MEMORY.md`.

---

## ⏭️ 2026-06-03 (evening) — Biohacker overhaul + REKURZE rename / NEXT SESSION (2026-06-04)

> Read this first tomorrow. Two commits pushed to `origin/master`: `c39076e` (BH) + `d4d1c7a` (rename). Lint clean. **Not yet playtested by the user** — that's job #1.

### Shipped this session

**1. Renamed the game REFACTOR → REKURZE** (`d4d1c7a`).
- **Why:** "Refactor" is an exact-title collision on Steam (another unreleased game + a Chinese cut) *and* a saturated keyword. We live-searched Steam: every common word and clean CS term is taken (`exit` → 5,649 results; SIGKILL, SEGFAULT, Heisenbug, Halt, Daemon, Overclock, Kernel all exist). Only a coined/uncommon token survives — the Balatro/Inscryption/Noita play. **REKURZE** = Czech for "recursion," chosen over NULLCOP/HATEROOT/DECOMMIT (all also screened clear). It's on-theme: the 30-day loop is a recursive call, **Breakdown (hatred=100) is the stack overflow**, the true ending is the loop **terminating** (`exit code 0`), the Colonel is the recursion with no base case, the roguelike is recurrence.
- **Done in code:** `config.name` + `build.name`; the hardcoded main-menu wordmark + `case-file //` top bars + the THANK-YOU-FOR-PLAYING end screen (these were hardcoded text in `screens_system.rpy:624/634/889` + `screens.rpy:3696`, NOT `config.name` — that's why the first pass missed them); README title + intro.
- **Intentionally unchanged:** `config.save_directory` (would orphan saves), the repo folder `REFACTOR/` (codename ≠ store name), and the diegetic motif — the `coding_refactor` daily activity *titled* "REFACTOR" (you refactor/upgrade a card) and the colonel-ghost "It's REFACTORING time" title drop both stay.
- **Cosmetic follow-ups (low priority):** README screenshots/folder paths + this doc still say "refactor"; the menu video filename `title_refactor.webm` is just JB-walking footage (the wordmark is text, already REKURZE) — no re-render needed.

**2. Biohacker overhaul** (`c39076e`) — **BH is back in scope** (was locked; user: "biohacker doesn't work… boring cards, core mechanics don't work; BB is the bar"). Dark Empath stays locked.
- **THE headline fix — the "infinite energy / spam-fest, no thinking" bug.** Root cause was **`Open Source PR`**, a *draftable* coding Power that did `max_energy += 1` **permanently, every play** → draft 2–3 and the ceiling climbed unbounded → play your whole hand every turn → zero decisions. Reworked to one-shot tempo (gain energy now + draw 1 + next Power free). Steady-state BH energy now caps ~6. (Meditation was NOT the cause — but it had a *lying log* "+1 max energy this fight" that made it look guilty; removed. It's correctly +2 turn-1-only now.)
- **Draft engine was blind to BH:** `DRAFT_ARCHETYPES` now includes stimulant/neurochem/wetware/coding (they were collapsing into the 0.5-weight neutral bucket, so BH builds never snowballed).
- **Supplements no longer drop from enemies** (user: "no 15yo sprayer kid drops you modafinil") — stimulant/neurochem/wetware excluded from fight/enemy drops; doses + suppliers are the only source. Coding stays draftable.
- **Content:** `the_compound` → draftable rare finisher; coding cards retagged `coding`; new attacks tweak/redline/adrenaline/decompile + 3 absurd ones with generated art (red_light_therapy/theragun/ice_bath); Phenibut buffed to 44 dmg / −5 HP (was a weak −1 max-energy); Homeostasis Power (heal→damage).
- **6 BH-locked relics** (modafinil_bottle **8k**/bulk_order/standing_desk/dual_monitors/recovery_ring/peptide_vial). Olympic Barbell → **BB-locked**.
- **Recovery actually raises Max HP now** — sauna/cold plunge/red light bumped `gym_max_hp_bonus` but never recomputed `run_hp_max`, so the +Max HP never applied (user-reported). Fixed (+5/+10/+5).
- **`Modafinil` skill → `Megadose`** (de-collide vs `FLModafinil Spike` — user: "two cards basically same name").
- **BH true-ending epilogue** — the true ending hardcoded the *bodybuilder* "fitness app" outro for every class; BH now gets its own (developer at a pharma giant, compound in trials with his initials, *"you don't need a dose to keep it quiet"*).
- Tuning: BH base HP 90→105; coding STUDY xp 18→12 (study-spam capped Coding too fast — user hit 249 by day 16); nootropic tiers unlock by **day OR purchase count** (not just cash) + affordability gating on tier buttons & the Fixer shred button.

### NEXT (start here, 2026-06-04)

1. **Playtest the BH energy fix first.** Does combat still feel like a spam-fest now the ceiling is ~6 instead of unbounded? **This read decides whether #2 is needed.**
2. **BH decision-texture pass — the deep one (greenlight pending the playtest read).** Capping energy was step 1, but BH cards are still interchangeable "deal X" with no sequencing tension; BB makes you *think* (scarce energy + block/SOMA/presence decisions). **Proposed lever: lean into the crash mechanic as BH's identity** — energy abundant, but dumping your whole hand triggers escalating crashes next turn, so "spam everything" becomes a *gamble*, not the free optimum. Touches several cards → confirm with the user before rewriting.
3. **BH random events / Arc 3 thinness** (user-flagged, twice) — add BH-flavored events (suppliers, black market, lab, trial-subject beats) and flesh out the BH "Telegram" class arc.
4. Carried from the morning session: 1–2 BB-accessible Coding-scaling cards (Pipeline is the lone anchor); prose-tighten the OLD keeper events; SFX assets.

---

## ⏭️ 2026-06-03 (morning) — where we left off / NEXT SESSION

**Shipped today (all pushed to `origin/master`):**
- **Six new random events**, each with generated painterly art (`images/events/ev_*.jpg`): **The Collector** (press-your-luck relic gamble — pay 25 HP or 5,000 CZK per 50% pull, walk = +20 Hatred), **The Quartermaster** (choose 1 of 3 seen relics, one per HP/CZK/Hatred lane), **The Range Instructor** (HP-priced deck-craft: remove 1 OR upgrade 1 for −8 HP — both lanes cost the same, no dominant option), **The Tail** (event-launched hard fight, the Colonel's reach), **The Side Gig** + **The Contract** (the new CODING lane — trade HP/cash for Coding skill). Removed the weak Pawnbroker.
- **`event_fight(enemy_id, tier)`** (`cards/battle_ladder.rpy`) — first wrapper that drops you into a real battle from inside a random event (loss → `forced_detour`, win → counts as a kill + the event pays a bespoke reward). Used by The Tail; reusable.
- **Pills, Probably** reworked from a trap (50/50 heal/hurt + permanent Compromise) into a worth-taking 0-cost exhaust gamble (5-of-6 upside: heal/block/+Str/draw/damage, 1-in-6 = −10 HP, no Compromise).
- **Coding lane, finally visible + reachable:** the stats bar shows the live **Coding tier** (`Coding 35 · T2`); STUDY/Refactor coding gain **12 → 15**; the two coding events feed the lane without the 35k bootcamp wall.
- **Balance pass:** relic shop prices set across ~12 relics; Fixer's Business Card corrected to **25% off everything incl. the shred service**; Spiral Notebook now **once per fight** (not per turn); Grundza's "Try His New Batch" flee grants **+10 Max HP**; enemy HP — **Lifer 225, The Tail 240, police_bureaucracy.exe 450**; bribe-flee button copy trimmed.
- **New title-screen video** (`video/title_refactor.webm`, VP9, silent) replacing the old menu loop. (mp4 looped badly in Ren'Py's player → converted to VP9.)
- Deleted the stale **refactor/balance-judge** subagents (per the user — verify via lint + an ad-hoc Workflow critic instead; see [[feedback_judges_stale]]).
- An adversarial **audit workflow** over the whole session's diff came back **clean** (every high-confidence finding refuted; zero real bugs/balance issues).

**NEXT (start here):**
1. **Playtest the new events in-hand** — The Collector gamble, The Quartermaster relic-choice, the Range deck-craft, The Tail at 240 HP, and the coding events firing in their bands (early/mid/late).
2. **Coding lane, part 2:** the events now grant Coding *skill*, but BB has few Coding-scaling *cards* to spend it on (Pipeline is the lone anchor). Add 1–2 BB-accessible Coding cards so the tier pays off in combat.
3. **Prose-tighten the OLD keeper events** (designer_of_forms / lost_and_found / uniform_collector / the_interview) — same "too long, no one reads that" note the new events got.
4. SFX assets (still open from 06-02).

(Art pipeline note: `gen_bg.py` needs **Python 3.13/3.14** — `py -0p` — NOT the repo `.venv` (its pip is broken on this machine: platformdirs can't read a missing CSIDL_COMMON_APPDATA registry key). Event art = painterly, no-people environment scenes; pass two existing `ev_*.jpg` as `--ref` to lock the style.)

---

## ⏭️ 2026-06-02 — where we left off / NEXT SESSION

**Shipped today (all pushed to `origin/master`):** killed the emoji render-bug (combat icons/buff chips were tofu) + buff/debuff polarity colour; card **rarity** visuals; **keyboard shortcuts**; battle **SFX** (incl. a Škoda-horn on The Final Set); **ARC-banded + recurring events** + a new **BB "Trainer" arc** (days 7/13/19) + revived **Midnight Call**; balance (Grundza flee, difficulty economy, Coding lane, Colonel enrage, Pipeline→1dmg/cost3, Internal Affairs→200HP, Chalk Bag→35k rare, shop prices rounded to 50); writing/UX (show-don't-tell pass, run-recap + NEW BEST, **redesigned Trophies screen**); the **secret boss rebuilt** (glitched-Colonel sprite + kernel-space bg + 280HP + phase-2 surge — no longer a 120HP office reskin); the **Fixer's own back room** bg; and a big **card-art pass** — cop cards as a young Czech cop in the POLICIE vest, the tech lane as absurd metaphors, gut_punch = Grundza, **Outnumbered = a John Wick keyart parody**, Refactor→**Debugging**, Git Blame→**Paper Trail**, Cuff 'Em **deleted**.

**NEXT (start here):**
1. **Events funnier-prose pass** — the one unfinished task. Rewrite the keeper events (designer_of_forms, lost_and_found, pills, uniform_collector, the_interview) in the dark Czech-cop-comedy tone (mechanics unchanged). The 3 weakest (smell/karaoke/photocopier) are already cut; synthol rebalanced.
2. **Full playtest** of everything above — esp. the secret boss, the BB arc, banded/recurring event firing, all new card art in-hand, the Fixer room.
3. **took_the_heat** art: confirm the head shows after a clean reload; recenter if the in-game art zone center-crops.
4. Optional: art for placeholder events (bb_trainer_* + evr_*); decide opportunity_events (delete vs port to StS style); more Colonel intent variety.

(Art-gen note: the image model outputs variable aspect — always normalize card art to **1456×720** or single-figure portraits get beheaded; it also refuses body-horror prompts, so the boss sprite was a procedural glitch of an existing sprite.)

---

## 1. The Vision (the GOTY thesis)

REFACTOR is a **Slay-the-Spire-style deckbuilder fused with a 30-day life-sim**. JB, a Czech cop, claws his way out of a corrupt precinct into tech, racing a countdown to a final confrontation with the Colonel — and **HATRED is his death clock** (you lose at the cap; crossing 40/60/80 jams permanent Rage cards into the deck).

**The moat is the theme.** Slay the Spire is fantasy wallpaper; Balatro is abstract. REFACTOR is *specific* — the panelák, the Fixer, bribing Internal Affairs, the breach team yelling POLICIE, the Colonel as a 32-year `police_bureaucracy.exe` loop. No other deckbuilder has this. **Every system should sharpen the theme, not just the numbers.**

**The governing principle (learned today): the 30-day run must COMPOUND.** A great game you beat once becomes a GOTY game you replay 80 times only when the systems agree mechanically — builds snowball, the climax reads your history, and a meta-loop pulls you back. Today's work was largely about making that true.

**Scope note:** **Bodybuilder (BB)** is the design bar and most-tuned class. **Biohacker (BH) is back in scope as of 2026-06-03** (overhauled — see the top handoff). **Dark Empath stays locked / out of scope.**

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
