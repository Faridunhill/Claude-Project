# Local Agents — System Plan v2.0

Supersedes `README-local-seats.md` (6 steps) and `Local Seats — Full Plan v1.0`
(Phases 0–5). Everything those two documents forbid is still forbidden. This
version adds the roster, the licence ladder, the 24/7 layer, and the rule that
decides when the Hermes council is switched off.

Read this whole file before writing any code. The build order is in
`docs/local-agents-builder-brief.md`.

---

## 0. What changed, and why

The v1.0 plan was right about one seat and wrong about the roster. It scored a
single reading job and left Hamada, the seven shadows, hunter, academy and
cabinet with no definition — which is exactly the condition that made them
improve slowly in the first place.

Three corrections carry the whole upgrade:

**Correction 1 — Most of the work on the list is not a model job.**
"Check that an Etsy-sold ID is dead on eBay", "check inventory", "check the
system is alive" — these are string comparisons and HTTP status codes. A model
adds error to them. They become **watchers**: deterministic scripts, no model,
no death test, ordinary correctness tests instead. This is the cheapest and
largest part of the build and it can run today.

**Correction 2 — A shadow scored against the council's opinion learns to
parrot the council.** Agreement with an opinion is not evidence of being right;
it is evidence of being similar. Every shadow seat is therefore scored on a
question that *reality settles later* — did the lot sell in 30 days, did the QA
gate route the item to review, did the fix land in the file it named. If no
settleable question exists for a seat, that seat does not get built. This is
the feed that was missing.

**Correction 3 — "Fix the bugs" is not a local-model capability, and saying so
now is cheaper than discovering it at test 149.** A 7–14B local model cannot
debug this system. What it can do is *triage*: read a stack trace, name the one
file most likely at fault, draft a patch. CODE fixes; the local narrows the
search. Every duty on the list that reads "fix / solve / manage" is rewritten
below as "detect, triage, propose" with an execution ladder above it.

---

## 1. The three kinds of worker

Nothing in this system is "an agent". Everything is one of three things, and
the kind decides the rules it lives under.

| Kind | Uses a model | May write files | Test it must pass | Lives in |
|---|---|---|---|---|
| **Watcher** | No | Its own ledger only | Correctness test: catches planted faults, zero false alarms on known-good rows | `local/watchers/` |
| **Seat** | Yes | Never | Death test, set in writing before the first run | `local/seats/` |
| **Proposer** | Yes | `local/proposals/` only | Acceptance rate over 30 days | `local/proposers/` |

Three names on the roster — **academy**, **cabinet**, and the registrar half of
**hamada** — are scripts, not agents. They are bookkeeping. Giving them a model
would add cost and error to arithmetic.

### The seat contract (unchanged from the README, no exceptions)

- Reads its input text from stdin.
- Prints only its answer to stdout. Nothing else. No banner, no progress text.
- All logging and errors to stderr.
- 120-second hard timeout on the model call.
- Exits 0 only when it produced an answer. Timeout, empty response or bad JSON
  exits non-zero.
- Never writes to any file. A seat answers; it does not record.

### The watcher contract (new)

- Takes its inputs from `local/data/corpus/` and its config from
  `local/roster.yaml`. Never from the network directly at first run.
- Appends one JSON line per check to `local/data/ledger/<watcher>.jsonl`.
- Writes `local/data/heartbeat.json` on every run, pass or fail.
- Never changes a listing, a price, or a file outside `local/data/`.
- Exits non-zero on any condition it cannot evaluate. Silence is a failure, not
  a pass.

### The proposer contract (new)

- Writes one file per proposal to `local/proposals/<ts>-<proposer>.json`:
  `{"ts", "proposer", "problem", "evidence_path", "proposed_command",
  "proposed_diff", "rollback", "risk"}`.
- **Never executes anything.** Not at L2, not at L3. Execution is a separate
  licensed action, described in §4.
- A proposal with no `rollback` field is invalid and is rejected by the
  registrar script.

---

## 2. The roster

Eleven names, one table. Each one gets a first job whose answer something else
already knows, and a death test written before it runs. A row with no settleable
question is not built — the row stays empty until one is found.

| Name | Shadows | Kind | First scored job | Ground truth comes from | Death test |
|---|---|---|---|---|---|
| **hamada** | the builder (CODE) | Seat → Proposer | Given a failing command's stderr + repo tree, print the one file path most likely at fault | The file CODE actually edited in the fix commit (`git show --name-only`) | >2 invented paths in 50 rows, or top-1 accuracy <40% |
| **hunter** | — (sourcing) | Seat | Brand names present in a lot description, one per line | Known contents of lots already bought | >5 invented brands in 50 rows |
| **shadow-qc** | QC seat | Seat | Will `marketing/qagate` route this item to REVIEW or PUBLISH? | `route_item()` — the gate's own decision, free and deterministic | Agreement <85% at 200 rows |
| **shadow-redteam** | Red Team seat | Seat | Flag trademark/policy risk phrases in listing text | Banned-terms dictionary, plus Farid's adjudication of anything the dictionary missed | >3 false flags in 50 rows |
| **shadow-pm** | PM seat | Seat | Will this listing sell within 30 days at this price? yes/no | The phenotype ledger, 30 days later | Accuracy ≤ coin-flip baseline at 100 settled rows |
| **shadow-4** | (Hermes seat 4) | — | *Unfilled. Name the settleable question first.* | — | — |
| **shadow-5** | (Hermes seat 5) | — | *Unfilled.* | — | — |
| **shadow-6** | (Hermes seat 6) | — | *Unfilled.* | — | — |
| **shadow-7** | (Hermes seat 7) | — | *Unfilled.* | — | — |
| **academy** | — | Script | Reads score files, issues and revokes licences, writes `local/data/licence.jsonl` | Arithmetic | n/a — it is tested, not scored |
| **cabinet** | — | Script | Concatenates every seat's five-line report + the licence table into one text output | Arithmetic | n/a |

The four unfilled shadows are deliberate. Transcribe the real Hermes seat names
into `local/roster.yaml`, then leave them empty until someone can write the
question reality settles. An unfilled row costs nothing. A row filled with
"reviews the design" costs weeks.

`shadow-qc` is the seat to build first among the shadows, because its labels are
free: `marketing/qagate/gate.py` already decides REVIEW or PUBLISH for every
item, deterministically, at zero cost. That is 200 labelled rows without asking
anyone for anything.

---

## 3. The duties, rewritten as buildable things

Every item from the brief, mapped to a worker and a gate. "Manage" and "fix"
do not appear.

| The duty as stated | What is actually built | Kind | Gate |
|---|---|---|---|
| Files/data reachable by any agent | `local/` tree with fixed paths + script-written `local/index.json` listing every dataset, its row count, its build time | Script | G0 |
| Etsy-sold IDs must be dead on eBay | `watch-crosspost.ps1` — reads the Etsy sold export and the eBay active export, emits `collisions.jsonl` of SKUs sold on one and live on the other, both directions. **Emits. Does not delist.** | Watcher | G3 |
| Check inventory | `watch-inventory.ps1` — counts live listings per marketplace against the genome store, flags SKUs live in two places, live with zero stock, or in stock with no listing | Watcher | G3 |
| 24/7 system check | `run-watchers.ps1` on Windows Task Scheduler every 15 min + `watch-heartbeat.ps1` that fails loudly when a watcher has not run in 45 min | Watcher | G5 |
| Auditing / QC | `shadow-qc` seat scored against the QA gate + `watch-ledger-integrity.ps1` (append-only violated? row counts fell? schema drifted?) | Seat + Watcher | G6 |
| Fix the bugs, solve technical issues | `hamada` triage seat names the suspect file → writes a proposal → CODE fixes | Seat → Proposer | G4 |
| Ask code to write or edit code | Proposal file format in §1; CODE reads `local/proposals/`, implements, and the registrar records accepted/rejected | Proposer | G7 |
| Suggest structure/parts upgrades | Same proposal channel, `risk: "structural"`. No structural proposal is implemented in the same week it is written. | Proposer | G7 |
| Learn PowerShell / manage PC software | The licence ladder in §4. Nothing executes before L4, and L4 is granted per command, never per agent. | — | §4 |

---

## 4. The licence ladder — "the windows level"

No agent skips a level. Promotion is issued by the **academy** script from the
score files, never by hand, and is written append-only to
`local/data/licence.jsonl`. Demotion is automatic and immediate on a failed
death test or a false alarm at L3+.

| Level | Name | May do | Earned by |
|---|---|---|---|
| **L0** | Observer | Read `local/context/`. Print to stdout. Write nothing. | Existing |
| **L1** | Scored | Same, but its answers are recorded to a ledger by a runner script | 50 rows scored, death test passed |
| **L2** | Proposer | Write to `local/proposals/`. Still executes nothing. | 200 rows at threshold, invented-per-50 still under its limit |
| **L3** | Reader-operator | Run commands from the **read-only allowlist** (`Get-*`, `git status`, `git log`, `dir`, `Test-Path`) on the PC | 30 days at L2, ≥90% of proposals accepted or judged harmless |
| **L4** | Operator | Run one specific named write command, with a rollback recorded before it runs | Granted by Farid per command, in `roster.yaml`, never by the academy script, never inherited |

Hard walls at every level:

- No agent at any level touches eBay, Etsy or faridunhill.com. Marketplace
  writes stay manual for the life of this plan. The crosspost watcher's whole
  job is to hand Farid a list, not to act on it.
- No agent at any level edits `local/roster.yaml`, `.local-seat-env`, or
  `marketing/control.yaml`. Those three are Farid's files, in the same sense
  that `control.yaml` already is.
- L4 grants are per command, per agent, and expire when the death test
  threshold they were granted under is breached.
- An agent that fails a death test drops to L0 on the spot and stays there until
  a rebuilt version passes a fresh 50 rows. There is no appeal and no "it was
  unlucky" rerun.

---

## 5. Data layout — one tree, fixed paths

Anything any agent needs is under `local/`. Seats read only `local/context/`,
which is a snapshot written by a script, so no agent can corrupt a corpus by
reading it.

```
local/
  .local-seat-env             # LOCAL_MODEL, OLLAMA_URL, SHELL_FLAVOR   [Farid-owned]
  roster.yaml                 # names, jobs, death tests, licences, L4 grants [Farid-owned]
  seats/       <seat>.ps1     # model jobs. stdin -> stdout. Write nothing.
  watchers/    <watch>.ps1    # deterministic checks. No model.
  proposers/   <prop>.ps1     # L2+ only
  scripts/                    # builders, runners, reporters, academy, cabinet
  data/
    corpus/                   # raw pulls, script-written, never hand-edited
    context/                  # read-only snapshots agents may read
    labeled/  <seat>.jsonl    # {"id","input","known_answer"}
    ledger/   <name>.jsonl    # append-only. Never rewritten, never cleaned.
    score/    <seat>.jsonl    # {"run_ts","rows","invented","invented_per_50","avg_seconds"}
    licence.jsonl             # append-only promotions and demotions
    collisions.jsonl          # crosspost watcher output
    heartbeat.json            # last run time per watcher
  proposals/   <ts>-<name>.json
  logs/
  index.json                  # script-written map of every dataset above
```

Two files in that tree are hand-owned — `.local-seat-env` and `roster.yaml` —
and both are config, not data, exactly like `marketing/control.yaml`. Every
other file is written by a script. The rule from the README stands: anything
that needs Farid to fill it in by hand stops being filled in.

---

## 6. Gates

Each gate is passed once, in order, and the next thing waits. A gate is passed
when its number is printed by a script, not when it looks right.

| Gate | What must be true | If it fails |
|---|---|---|
| **G0** | The `ready` probe prints `ready`. `local/` exists. `index.json` is script-written. | Stop. Report the output. No further code. |
| **G1** | `hunter`/seat-brands: 50 rows scored, **invented ≤ 5** | The seat is dead. No prompt tuning, no bigger model, no reruns. Fall back to dictionary matching and record that local brand extraction does not work. |
| **G2** | 200 rows, invented-per-50 still ≤ 5 | Seat drops to L0. Ladder stops here. |
| **G3** | Crosspost + inventory watchers: catch 3 planted collisions, zero false alarms on 20 known-good SKUs | Fix the script. A watcher has no death test — a wrong watcher is a bug, not a verdict on local models. |
| **G4** | `hamada` triage: 50 rows from real fix commits, top-1 ≥ 40%, invented paths ≤ 2 | Hamada stays L0 and remains a note-taker. The build continues without him. |
| **G5** | 14 consecutive days of scheduled runs with zero silent failures (a missed run must have produced an alert) | Fix the scheduler before anything else is added. |
| **G6** | `shadow-qc` agrees with `route_item()` on ≥85% of 200 rows | That shadow is dead. Try `shadow-redteam` next, same shape. |
| **G7** | Academy issues the first L2 licence from the score files; CODE implements the first accepted proposal | Registrar bug. Fix; do not hand-issue a licence. |

After G7: four weeks of the daily runner holding, with no gate reopened, before
anything on the banned list is reconsidered.

---

## 7. Switching Hermes off

The goal is CODE plus locals. The switch-off condition is a number, set now.

A shadow may replace its council seat when **both** hold:

1. It has ≥200 scored rows on settleable questions, and
2. Its accuracy on those rows is **greater than or equal to** the council seat's
   accuracy on the same questions over the same period.

Which means: from the next council round onward, every question put to a Hermes
seat is logged in settleable form, with the seat's answer, into
`local/data/ledger/council-<seat>.jsonl`. Without that log there is no
comparison and the council cannot be retired on evidence — only on impatience.

Seats are retired one at a time. Seven shadows do not graduate together.

---

## 8. What stays banned

- No MCP server, no orchestrator, no seat manager, no queue, no web UI, no
  dashboard, until four weeks past G7.
- No model fine-tuning, no prompt auto-tuning, no retry-until-it-passes.
- No writes to eBay, Etsy or faridunhill.com. Read-only for the life of this plan.
- No agent executing any command before L3, and no write command before a named
  L4 grant.
- No second seat before the first has fifty scored rows.
- No hand-filled data files.
- No status reports. `4 invented brands in 50 rows` is a fact. `Hamada is coming
  along well` is a story.

---

## 9. What this plan does not promise

Stated now so it is not discovered at test 149:

- A local 7–14B model will not fix bugs, will not reliably write correct
  PowerShell, and will not manage PC software. It will triage and it will read.
  Every "manage" duty in the brief is delivered as detect → triage → propose,
  with CODE or Farid executing.
- `shadow-pm`'s sell-within-30-days job needs 30 days to produce its first
  label. It is the slowest seat on the roster and it is placed last for that
  reason.
- The crosspost and inventory watchers are worth more, sooner, than every model
  seat combined, and they need no model at all. If only one thing gets built
  from this plan, build those.
- Ollama on `localhost:11434` cannot be reached from the cloud session that
  wrote this document. Every gate here is verified on Farid's PC by the builder,
  and G0's output is the first thing reported back.
