# REFACTOR — Vision & Roadmap

Status: drafted 2026-05-13. North-star for the project. Supersedes the old Phase 0–4 plan in `REFACTOR_PLAYBOOK.md` (which stays as a workflow/checklist reference).

---

## 1. What this game is

**REFACTOR is a deckbuilder–life-sim where the deck you fight with is the 30 days you lived.** Player is JB, a Czech cop on a 30-day countdown to a confrontation with the Colonel, clawing his way out of policing and into tech. Every day is a resource decision (money / coding skill / hatred); every decision *writes a card into the deck*; the Colonel fight is the reckoning for the deck — and the man — those 30 days produced.

It is **not** a visual novel. It is a StS-shaped roguelike with a life-sim front half, sold on Steam.

### Design pillars
1. **The deck is your life.** No curated card pool handed to the player. Activities seed cards: gym → Body, coding bootcamp → Tech, cop work → Authority. The 30-day loop *is* deck construction. (This is the fix for the game's core flaw: today players bifurcate into "chase cards" vs "chase resources" camps — under this design, chasing resources is the *only* way you build a deck at all.)
2. **Hatred corrupts.** `pcr_hatred` escalation (Colonel mugshot beats, confrontations) jams **involuntary Rage cards** into the deck — high damage, self-corrupting (self-damage, hand discard, block-strip). A "hot" run is powerful but unstable. The Colonel fight weaponises your own hatred against you.
3. **Money is the only shop.** Card upgrades and removals are bought through in-fiction sim actions (a fixer, a coach, a night of study) — never a bolted-on StS shop screen.
4. **One tuned difficulty.** Curated, hand-balanced single experience. Ascension-style modifiers are post-1.0, not launch.
5. **Czech-cop-dark-comedy specificity.** Děčín, the Labe, the uniform jacket he can't get off the chair. Lean in. Cut prose 40–60% — texture, not paragraphs.

### Anti-goals
- Not a VN. Not a generic StS reskin. No separate shop screen. No three half-built classes (see §6). No coding mini-game (cut — coding stays an abstract stat). No `dev_corrupt` difficulty at ship.

### Top risk
**Combat depth/fun.** The whole bet is that the deck-is-your-life integration is *more* interesting than base StS, not less. Everything downstream is gated on a prototype proving that.

---

## 2. Combat model (target)

- **Battle ladder, not a single boss.** ~8–10 turn-based card battles over 30 days. Built by converting the existing class arcs (BB Trainer sparring / DE Kovář / BH Telegram ops) into fights, plus ~4 generic encounters (gym challenge, a cop-work bust, etc). Augments — does **not** replace — the random-event system: keep the best ~6–8 narrative events in the pool; a day-slot rolls *either* a battle node or an event.
- **Conventional HP per fight.** Readable, proven. Loss is **not** game-over — it triggers a **forced detour** (hospital / suspension / debt sub-event with its own choices and a stat/time cost). Multiple stalls degrade the run toward a worse ending; they don't end it.
- **The Colonel is a true capstone**, not battle #11: multi-phase, intent escalation scaled to `pcr_hatred`, mechanics the ladder telegraphs but never fully shows.
- **Stat→combat hooks (resolve in prototype):** how directly `coding_skill` (draw/energy?), `money` (consumables?), and `hatred` (volatile damage resource? corruption deck-injection?) touch *in-battle* state vs. only deck-construction. Default lean: integration lives at the deck-building layer (legible, fun); battles themselves stay clean. Hatred's exact combat role is the #1 prototype question.

---

## 3. 1.0 scope

Ship when the current arc is **excellent**, not when it hits a content quota. Baseline: **one 30-day campaign, high replayability** via class, events, RNG, and deck variance — ~2–4 hrs/run. Meta-progression and extra acts are explicitly out of v1.

---

## 4. Roadmap — phased to 1.0

### Phase A — Combat-integration prototype *(first milestone, throwaway-grade)*
Prove the thesis before building anything polished.
- 2–3 ladder battle nodes (one converted class-arc beat + one generic).
- Deck-from-activities: a handful of activities each grant a real card.
- Involuntary Hatred/Rage cards injected on `pcr_hatred` thresholds.
- Colonel fight v2 sketch: multi-phase + hatred-scaled intent.
- **Exit criteria:** it's *fun* and the resource↔deck loop feels like one strategy, not two. If not — iterate the model here, cheaply, before Phase B. Decide hatred's in-battle role.

### Phase B — Codebase reconciliation
- Audit Phase-1–4 "overnight" work: what survives the redirect, what gets gutted. Willing to rebuild anything that doesn't fit the narrative.
- Rebuild combat core as needed to support deck-from-life + corruption.
- Remove `dev_corrupt`. Collapse difficulty to the single tuned tier (Easy/Hard/Insane/Ultra → one curated experience; modifiers deferred).
- Cut the coding mini-game files.

### Phase C — Content build-out
- Full battle ladder (~8–10 nodes), all class arcs converted.
- Curate the random-event pool down to the best ~6–8; retire the rest.
- Card library pass: every card sourced from a specific activity/event; Rage card set; upgrade/removal paths via in-fiction money sinks.
- Forced-detour loss sub-events.
- Endings reconciled with the new combat outcomes.

### Phase D — Identity & polish pass
- Art consistency: keep the AI (Nano-Banana) pipeline, but heavy curation + Krita cleanup passes. Audio = curated royalty-free/licensed.
- Dynamic JB flat (see playbook §"Dynamic JB Flat") as the tactile progress meter — ship in slices.
- Writing pass: tone consistency, 40–60% prose cut, Czech specificity dialed up.
- The Colonel boss hardened to capstone quality.

### Phase E — Beta → Steam 1.0
- Playtest loop (the real mitigation for the combat-fun risk — get it in front of players, iterate on data not theory).
- Balance the single difficulty against the integrated economy.
- Steam page, capsule art, store assets, build pipeline, achievements wired to the new structure.

*Phases are roughly sequential but A→B and C↔D will interleave. Each slice should be independently mergeable. An intense sprint is coming — Phase A is built to exploit it.*

---

## 5. Out of scope for 1.0
Meta-progression / roguelite unlocks · additional acts/campaigns · coding mini-game · Ascension-style difficulty modifiers · commissioned art (AI-curated for v1; revisit if the game has legs).

---

## 6. Open questions (decide before Phase C)
- **DE / BH classes.** Currently locked, BB-only playable. Options: (a) BB-only permanently, remove the locked previews; (b) ship BB-only, DE/BH as post-1.0/DLC; (c) all three at parity for v1. **Undecided — needs a call before content build-out commits.**
- **Hatred's in-battle role** — resolve in Phase A prototype.
- **How far stats reach into in-battle state** vs. deck-construction only — resolve in Phase A.
- **Stat-stakes combat variant** (no HP bar; damage bleeds money/coding/rep) — rejected for now in favour of conventional HP, but worth a cheap try if Phase A combat feels generic.
