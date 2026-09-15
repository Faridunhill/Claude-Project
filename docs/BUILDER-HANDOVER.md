# Builder Handover — everything, in reading order

Branch: `claude/local-agents-system-plan-s9qo2u`
Repo: `github.com/Faridunhill/Claude-Project`
Web version of the build order: https://claude.ai/artifact/V2cTW6h5HBL5SMkH4i4gRE

Everything the builder needs is in this repository. Nothing lives only in a chat.

---

## Read in this order

| # | File | What it is | Read it |
|---|---|---|---|
| 1 | `docs/local-agents-system-plan.md` | **The plan, v2.0.** Why the work is shaped this way: watchers vs seats vs proposers, the roster, the licence ladder, the data layout, the gates, when Hermes gets switched off | Once, fully, before writing code |
| 2 | `docs/local-agents-builder-brief.md` | **The work order, B0–B8.** Exactly what to write, what each gate must print, where to stop. Includes the exact seat prompts and the `roster.yaml` skeleton | This is the working document — kept open |
| 3 | `docs/pipe-intake-process.md` | Why the add-a-pipe process produces wrong claims, and what replaces it. Contains the `watch-claims.ps1` spec (B3.5) and the intake rework (B8) | Before B3 |
| 4 | `docs/local-agents-hardware-note.md` | What the 12GB card holds, what each upgrade buys, and **task B1.5** — the £3 rented benchmark that decides whether to buy a GPU at all | Only if G1 fails |
| 5 | `docs/reference/README-local-seats-original.md` | The original six-step README. Every rule in it still holds | Background |
| 6 | `docs/reference/local-seats-plan-v1.0.md` | The v1.0 phased plan, superseded by #1 | Background |

`docs/BUILDER-BUNDLE.md` is all of the above concatenated into one file, written
by `docs/make-handover-bundle.sh`. Use it when the builder wants one paste.

---

## The three rules that decide everything else

1. **One task at a time.** The next thing waits until the current gate prints.
2. **A gate is passed when a script prints its number**, not when the work looks
   right. Facts, never status.
3. **If a step is impossible or wrong, stop** and say which task number and why.
   Never work around it and keep going.

---

## Order of work, at a glance

| Task | What | Gate |
|---|---|---|
| B0 | Endpoint, tree, index, roster, hardware recorded | G0 — the probe prints `ready` |
| B1 | First seat: brand extraction | G1 — **invented ≤ 5 in 50 rows**, or the seat is dead |
| B1.5 | Rented benchmark — only if G1 failed | Buy / buy nothing |
| B2 | Same seat at 200 rows | G2 — invented-per-50 still ≤ 5 |
| B3 | Watchers: crosspost, inventory, ledger integrity | G3 — catches 3 planted, zero false alarms |
| **B3.5** | **The claim check** — blocks published claims the genome does not support | G3.5 — blocks 5, passes 20, zero false blocks |
| B4 | Hamada, the triage seat | G4 — top-1 ≥ 40%, ≤ 2 invented paths |
| B5 | 24/7 scheduling and heartbeat | G5 — 14 days, zero silent failures |
| B6 | shadow-qc against the QA gate's own decisions | G6 — ≥ 85% at 200 rows |
| B7 | Academy, cabinet, first proposal | G7 — first script-issued licence |
| B8 | Intake rework (runs during B5's soak) | G8 — 10 listings cleaned, < 4 min per pipe |

**B3 and B3.5 use no model and are not blocked by a failed seat.** If B1 dies at
G1, they still get built. They are the part that pays for itself first.

---

## Getting this onto the PC

```bash
git clone https://github.com/Faridunhill/Claude-Project.git
cd Claude-Project
git checkout claude/local-agents-system-plan-s9qo2u
```

Already cloned:

```bash
git fetch origin claude/local-agents-system-plan-s9qo2u
git checkout claude/local-agents-system-plan-s9qo2u
git pull origin claude/local-agents-system-plan-s9qo2u
```

Then open `docs/BUILDER-HANDOVER.md` — this file — and start at B0.

---

## What the builder must never do

- Write to eBay, Etsy or faridunhill.com. This build is read-only.
- Let any agent execute a command before L3, or a write command without a named
  L4 grant in `roster.yaml`.
- Hand-fill a data file. Only `.local-seat-env` and `roster.yaml` are hand-written.
- Tune a prompt mid-run, or re-run a failed death test hoping for a better number.
- Skip, disable or quarantine a test to make something pass.
- Build a second seat before the first has fifty scored rows, or an orchestrator,
  queue, dashboard or MCP server at any point before four weeks past G7.

---

## Report format, after every gate

```
gate:        G1
date:        2026-09-22
rows:        50
result:      invented 4
verdict:     pass
next:        B2
```
