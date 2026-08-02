# THE MONSTER, 100% AUTOMATIC — design
### Two machines, one bridge, nothing typed

**Date:** 2026-08-02 · **Status:** DESIGN — waiting for Farid's go before building
**Replaces:** the hand-carried parts of docs 004–005

---

## The thing I kept getting wrong

I built the local half to run by itself, then hand-delivered the research myself and called it
finished. Farid is right: a system where a human carries files between two halves is not
automatic, it is a person doing chores between two robots.

The fix was in front of me the whole time. **This repository is already the bridge between the
cloud and the PC.** Both ends can run on a timer. Git carries everything between them, by itself.

---

## The design

```
        CLOUD (runs on a schedule, no PC needed)
        ────────────────────────────────────────
          every week:
            reads public pages for the category Farid pointed at
            writes a dossier — brands, prices, weak points, edge test
            commits it to this repo
                              │
                              │  git — the bridge
                              ▼
        THE PC (runs every morning at 08:00)
        ────────────────────────────────────
            git pull            ← picks up new dossiers by itself
            reads new export files from Downloads / FARID_CHANNEL
            records sales, hashes buyers
            writes listings: site + Etsy + eBay CSV
            digs, proposes lessons, expires stale ones
            writes the report and PENDING.md
                              │
                              ▼
        FARID — answers questions. Nothing else.
```

**Neither half waits for the other, and neither waits for Farid.** The cloud researches whether
or not the PC is on. The PC works whether or not the cloud ran. Git holds the results until each
side is ready.

---

## What is automatic, and what is not — the honest line

**AUTOMATIC (the machine, no typing):**

| | |
|---|---|
| Reading new sales exports | ✅ built |
| Recording sales, hashing buyers | ✅ built |
| Writing listings for all three channels | ✅ built |
| Digging own data, proposing lessons | ✅ built |
| Expiring lessons that went stale | ✅ built |
| Reports, ledger health, blind spots | ✅ built |
| Refusing bad data (listing batches, active reports) | ✅ built |
| **Pulling new dossiers from the cloud** | ❌ **to build** |
| **Cloud research on a schedule** | ❌ **to build** |

**NOT AUTOMATIC — and never will be, because v1.0 says so:**

> *"Farid alone holds: category picks, floor prices, spend ceilings, anything crossing a wall.
> Monster proposes; Farid disposes."*

Four decisions. They arrive as one line each in `PENDING.md`, and a word answers them. That is
not a gap in the automation — it is the automation's safety catch, and it is why the system
cannot spend money or enter a category on its own.

**Everything else runs without a human.**

---

## The three pieces still missing

**1 · The cloud runs on a timer.**
A scheduled job fires weekly, researches the category Farid last approved, writes the dossier
into `channel/TO_FARID/`, commits, pushes. No PC involved. If Farid's computer is off for a
week, the research still happens and is waiting when he returns.

**2 · The PC pulls before it works.**
One line added to the morning job: `git pull` before anything else. That is the whole handover —
new dossiers, and any fix I push, arrive by themselves. Today Farid pastes a pull command every
time, which is the last piece of manual work left in the daily loop.

**3 · A dossier queues itself.**
When the morning run finds a new dossier file, it records the source with its expiry and queues
the category pick in `PENDING.md` automatically. Today that needs one typed command.

Three small pieces. After them, the only thing a human does is answer questions.

---

## What the cloud will research, and how it stays legal

**Farid points at a category. The agent digs. It never picks the category** — that is v1.0's rule
and it survives automation unchanged.

Public pages, read once, no crawling, no marketplace account touched. Every claim carries its
source and an expiry date (180 days), and is replaced plank by plank by Farid's own transactions
as soon as he sells one. That is the standing law: **public data is scaffolding, own data is
truth.**

Each dossier answers the same five questions:

1. Who sells this, and at what prices?
2. What do buyers complain about? *(the quality gap — where sellers do badly)*
3. Does it pass an edge we own — audience, expertise, Germany route?
4. Is there a repeat purchase in it?
5. **What do we NOT know?** — stated plainly, because a dossier that hides its holes is worse
   than none.

Dossier 001 (lighters, doc 005) is the shape. The weekly job produces one like it, by itself.

---

## The three businesses

v1.0's end state is three: Faridunhill, GroundTruth, Ashcombe. One design, cloned, each locked in
its own kitchen with one shared cookbook of methods.

**The clone is now nearly free.** Everything above is one folder per business and one config file
— the machine is written once. What still gates it is the rule Farid and MIND both ratified:
prove the loop on pipes until one lesson is CONFIRMED, then copy. That needs weeks of real
trading, not weeks of building.

**Recommendation:** finish the three automation pieces on pipes, let it run a fortnight, and clone
the moment the first lesson confirms. Cloning before that copies an unproven machine three times.

---

## What I need from Farid

**One word: go** — and I build the three pieces. Roughly:

- the cloud timer, and the weekly research job
- `git pull` inside the morning run
- dossiers queueing themselves

**And one thing only he can answer:** which category should the cloud research first? Lighters
is already queued as D-003 and awaits a yes or no.

After that, the honest description of this system is: **it runs itself, and asks you four kinds
of question.**

---

*Written after Farid pointed out — correctly, and more than once — that a system needing a human
to carry files between its halves is not automated. He was right each time.*
