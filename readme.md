# REFACTOR
> *"Code your way out, or lose your mind trying."*

REFACTOR is a dark, satirical life-sim visual novel set in Northern Bohemia. You play as JB — a young police officer who realizes his calling is software development, not law enforcement.

Survive 30 days. Learn to code. Escape the system before it breaks you.

---

## Core Loop

Every day you pick **one activity**. Every third day, a **mandatory event** interrupts your routine. Story events fire on fixed days. Between it all, **opportunity events** appear randomly — small moments that test whether you stick to the plan or seize the unexpected.

Your choices compound. There is no single winning strategy.

### Stats
- **Money (CZK)** — Pay for courses, therapy, gym. Hit zero → homeless ending.
- **Coding Skill** — Your escape velocity. Learn Python, grind Fiverr tutors, invest in bootcamps.
- **Police Hatred (PCR)** — Rises every night (scaling: +3 early, +5 late game). Hit 100 → breakdown.

### Daily Activities
| Activity | What It Does |
|---|---|
| **Gym** | Reduce hatred. Streak 3+ days → Focus Buff (+2 coding/night) |
| **Therapy** | Reduce hatred (diminishing returns over sessions, resets weekly) |
| **Bouncer** | High-risk money. Night club (safer) or strip bar (volatile) |
| **Coding** | Fiverr lessons (learn), Code for Money (earn, requires Tier 2+), Bootcamp (+5 coding/night for 10 days, repurchasable at scaling cost) |
| **Patrol** | +3,000 CZK, +3 coding, +8 hatred. The grind shift. |
| **Cold Read** | Dark Empath only. -20 hatred through observation. |

### Activity Combos
Sequential activities trigger bonuses:
- **Therapy → Gym** = Clear Mind (bad gym rolls upgraded)
- **Patrol → Fiverr** = Night Learner (+3 bonus coding)
- **Fiverr → Code for Money** = Flow State (+15% income)

### Opportunity Events
~30% chance on non-event days. 8-event pool, no repeats per run. Small encounters with real tradeoffs — a laptop deal, a freelance ping, an old friend, a midnight run. They don't consume your daily activity.

---

## Character Classes

Chosen once at game start. Permanent.

- **Bodybuilder** — Gym bonuses, bouncer pay bonus. Starts with -5 coding.
- **Dark Empath** — Cold Read replaces therapy. Starts with -10 hatred.
- **Biohacker** — Nootropics system, guaranteed top Fiverr tutors, BTC passive income. Starts with +10 coding.

---

## Difficulty

| Mode | Money | Coding | Hatred |
|---|---|---|---|
| Easy | 55,000 | 10 | 15 |
| Hard | 35,000 | 5 | 25 |
| Insane | 20,000 | 0 | 35 |
| Ultra | 10,000 | -25 | 50 |

---

## Story Structure

- **Day 1** — Car Incident. Three choices, multiple RNG outcomes. Sets the Colonel's attitude for the rest of the game.
- **Day 6 / 12 / 18** — The Bribe Chain. A corrupt cop arc with escalating consequences. Your choices here can lock you into a hidden ending.
- **Day 14** — Salary day. Amount depends on your hatred level.
- **Day 15** — Midnight Call. The Colonel phones you.
- **Day 24** — Martin Meeting. Your ex-colleague offers a way out.
- **Day 25-30** — Colonel Event. The final confrontation.

Random events fire every 3rd day between story beats. Pool-based, no repeats.

---

## Endings

| # | Ending | Trigger |
|---|---|---|
| 1 | **Mental Breakdown** | Hatred ≥ 100 before colonel day |
| 2 | **Homeless** | Money ≤ 0 |
| 3 | **Burnout** | Hatred ≥ 100 on colonel day+ |
| 4 | **Defeated** | Colonel wins the fight |
| 5 | **Escaped** | JB wins the fight |
| 6 | **Happy Nation** | Hidden. Beat the Colonel, but the Bribe Chain catches up. GIBS raids your apartment three weeks after you resign. |

---

## Tone

Dark comedy meets existential dread. JB isn't a victim who cries about his failures — he's a guy trapped in a broken system who decides to fight his way out. The humor is dry, the stakes are real, and the bureaucracy is the true antagonist.

The game doesn't moralize. It presents choices and lets the math do the talking.

---

## How to Run

### Ren'Py Launcher (Recommended)
1. Download [Ren'Py 8](https://www.renpy.org/latest.html)
2. Add the `REFACTOR/` folder as a project
3. Launch

### Built Distribution
Run the pre-built executable directly.

---

## Controls
- **Left click / Space / Enter** — Advance dialogue
- **Mouse wheel / Page Up/Down** — Scroll history
- **Escape** — Game menu
- **S** — Screenshot
- **H** — Hide dialogue

---

## Tech Stack
- **Engine:** Ren'Py 8
- **Scripting:** Ren'Py Script + Python 3
- **Audio:** MP3 (original AI-generated tracks)
- **Visuals:** AI-generated sprites, backgrounds, video cutscenes
- **Art:** Gemini, Midjourney
- **Music:** Suno AI

---

## Credits
**Developer:** Jakub Barak

---

*"Police officers preserve the status quo. Developers build the future."*
