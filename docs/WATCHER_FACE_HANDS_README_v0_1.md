# THE WATCHER, THE FACE, THE HANDS
### README v0.1 — for council review
Author: Farid Hadid | Date: 2026-08-17 | Status: DESIGN — not authorized to build

---

## 1. WHY THIS EXISTS

Farid runs three businesses (Faridunhill estate pipes, Ashcombe & Co., GroundTruth
Property AI) and 15+ Claude projects. All of it currently requires him to sit at
one PC. If he is in the car, in the shop, or asleep, nothing is being watched.

The loss is not mainly *doing*. It is *remembering*. Projects go quiet and nobody
notices — the 4,700 pipe profiles have not moved since June. The /shop route on
faridunhill.com served another store's tobacco and cigar products and was found by
accident, not by a system. Buyer questions sit unread; roughly 17% of them ask the
same thing (bowl dimensions and 9mm filter fit) and each unanswered one is a lost
sale.

**Goal: something that knows the state of the business every morning without Farid
opening anything.**

---

## 2. THE HARD CONSTRAINT (stated up front so the council does not waste time on it)

A local agent on Farid's PC **cannot run while the PC is off.** There is no version
of "local" that survives shutdown. Three possible shapes:

- **A.** PC stays on; agent works while Farid is away from the desk.
- **B.** Agent lives somewhere always-on — stops being local, gains cost.
- **C.** Scheduled worker — wakes at a set hour, does the round, writes a report, sleeps.

**Current assumption: C, with A as the fallback.** Council may challenge this.

---

## 3. THE THREE PARTS, AND THE ORDER

This is deliberately **not one creature.** Three parts, different risk levels,
built in this order:

| | Part | What it does | Risk | Build order |
|---|---|---|---|---|
| 1 | **The Watcher** | Reads, knows, reminds. Touches nothing. | Near zero | First |
| 2 | **The Face** | Dashboard on PC and iPhone. Shows what the Watcher found. | Zero | Second |
| 3 | **The Hands** | Edits listings, fixes quantities, answers buyers. | Real | Last |

Reasoning: the Watcher is the part that actually replaces Farid's time, and it
cannot break anything. The Face is worthless until the Watcher has something to
say. The Hands are the only part that can cause damage, so they come last and
only after the Watcher has proved it reads the world correctly.

---

## 4. PART ONE — THE WATCHER

### 4.1 It already exists

This is important: **a watcher is already fully designed** inside FARID OS —
the COA role, the 7:00 AM daily brief, `morning_dispatch.py`, nightly QC at 11:59,
the five-line daily snapshot into `farid_os.db`.

It does not function. Not because the design is bad, but because of one line:

> *"All projects submit 5-line Daily Snapshot."*

Nobody submits them. A Claude project cannot write to a local database on its own.
So the submitter is Farid — which defeats the purpose entirely. The brief is a
format waiting for a feed that never arrives.

This is the same failure that killed FarmhouseAdvisor, BusinessBuilder, and the
current Helper: **a system prompt with no live data.** The known principle applies —
*a data feed makes an agent valuable; setup only makes it exist.*

### 4.2 What changes — six changes, nothing more

1. **Input flips.** Delete "projects submit snapshots." Nothing is submitted. The
   Watcher opens the sources himself and reads what is actually there.

2. **Stores go first, before projects.** Order every morning: eBay → Etsy →
   Faridunhill.com → Ashcombe. These are the money. Projects come after.

3. **Four things per store** — the ones that cost money when missed:
   - orders unshipped / past handling time
   - buyer messages unanswered
   - listings ended, or quantity fallen to zero
   - account defect or policy notice

4. **Report change, not state.** Today against yesterday. *"Three unshipped, was
   one"* is useful. *"Store healthy 🟢"* is noise. Silence on quiet days is correct
   behaviour.

5. **Propose, never touch.** In v1 the Watcher has no write access to anything.

6. **Projects section becomes evidence, not status.** No self-reported text. Only
   observable facts: which folder last changed, what has not moved in 30 days.
   *Checks beat takes.*

### 4.3 The principle underneath

**Status is a story. A file timestamp is a fact.** The Watcher must never ask
anything to describe itself. It reads evidence directly.

---

## 5. PART TWO — THE FACE (dashboard)

### 5.1 The problem observed

A first attempt was built by Claude Code and came out basic — buttons, no design.
Two causes, and the second matters more:

- Code is a builder, not a designer, and received no design brief.
- **There was no data behind it.** Ten live numbers make a plain page feel alive.
  Zero numbers make the most beautiful page feel like a demo.

### 5.2 Proposed split of labour

- **Claude Design** produces the visual design — layout, hierarchy, typography.
- **Claude Code** wires that design to the Watcher's output.
- Alternative: buy a finished dashboard template and hand it to Code as the picture
  to follow. Cheapest route to professional-looking, because nobody has to invent.

### 5.3 The design test

**What must Farid see in four seconds, on a phone, before putting it down?**
Everything on the first screen must earn its place against that question.

### 5.4 Unsolved

A page running on the PC does not reach an iPhone by itself. Delivery method is
undecided and is a separate decision from design.

---

## 6. PART THREE — THE HANDS (last)

Real value, real danger. One bad edit on a live listing is discovered three days
later, after the damage.

**Proposed leash:** the Hands *propose* → Farid approves from the phone → the Hands
execute. No autonomous writes to any live store in v1 or v2.

Escalation floor already exists in FARID OS and should be inherited unchanged:
stop and escalate on any price change above 20%, any SKU deletion, any refund
above $50, any external message that cannot be recalled.

---

## 7. DECISIONS ALREADY MADE (do not re-open unless the council can break them)

- Three parts, not one agent.
- Watcher first, Hands last.
- Watcher reads evidence; nothing reports to it.
- Stores rank above projects.
- No autonomous store writes in v1.
- Rebuild the existing watcher's input. Do not create a new agent.

---

## 8. OPEN QUESTIONS FOR THE COUNCIL

1. Is the scheduled-worker shape (C) right, or does the always-on requirement
   eventually force a non-local host?
2. Can a local agent read Etsy and eBay order/message state reliably without a
   fragile scraping layer? This is the single biggest technical unknown.
3. What is the correct morning hour, and what should the Watcher do when it finds
   something urgent at 2 PM?
4. Should the Watcher and the existing ACADEMY (mistake-collector) be the same
   creature or stay separate?
5. Is "report change, not state" going to hide slow drift — something rotting at
   1% a week that never registers as a change?

---

## 9. KNOWN WEAKNESSES — attack these

- **The feed is the whole risk.** If the store data cannot be read cleanly, this
  becomes another prompt with no input, and it dies exactly like the last three.
- **Alert fatigue.** If the morning report is long, it stops being read within two
  weeks and the project has silently failed.
- **The Watcher may report perfectly and change nothing.** Knowing about three
  unshipped orders does not ship them. The value depends entirely on Farid acting
  on what he reads — which is the same assumption that made the original 7 AM brief
  fail.
- **Scope creep into the Hands.** The pressure to let it "just fix the quantity"
  will be strong and immediate.

---

## 10. HOW WE KNOW IT FAILED

- Farid stops opening the morning report → dead.
- The report needs manual input to be produced → dead, same disease as v1.
- It reports something that is not true, twice → trust gone, restart required.

---

*Council instruction: an evaluation that scores this highly and restates it in
better language is not an evaluation. Find the twelve specific things that are
wrong with it.*
