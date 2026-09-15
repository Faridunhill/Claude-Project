# Builder Brief — Local Agents, Tasks B0 to B7

For the builder working on Farid's PC. Read
`docs/local-agents-system-plan.md` first; this file is the order of work and
the acceptance test for each piece. Build only what is listed here, in this
order, and stop where a task says stop.

**Rules that override any instinct to be helpful:**

1. One task at a time. Do not start the next task before the current gate prints.
2. If a step is impossible or wrong, stop and say which task number and why.
   Do not work around it and keep going.
3. Print facts, never status. `rows scored: 50 / invented: 4` is a report.
   `the seat is working well` is not.
4. Every file this system produces is written by a script. The only two files
   you may write by hand are `local/.local-seat-env` and `local/roster.yaml`.
5. Nothing in this build writes to eBay, Etsy or faridunhill.com. Read-only.
6. No agent executes any command. Watchers run; agents propose.

---

## B0 — Endpoint, tree, index

**B0.1** Record the shell flavour. If Ollama runs on Windows natively, everything
in this build is PowerShell 7 (`.ps1`) and uses `Invoke-RestMethod` — no curl, no
jq dependency. If Farid runs WSL or Git Bash, everything is `.sh` with curl+jq.
Pick one. Write it into `local/.local-seat-env` as `SHELL_FLAVOR=`. Do not
write both flavours of any script.

**B0.2** `ollama list`. Choose one model. Write `local/.local-seat-env`:

```
LOCAL_MODEL=<name exactly as ollama list prints it>
OLLAMA_URL=http://localhost:11434
SHELL_FLAVOR=<powershell|bash>
```

**B0.3** Prove the endpoint. PowerShell form:

```powershell
$env:LOCAL_MODEL; $r = Invoke-RestMethod -Uri "$env:OLLAMA_URL/api/generate" `
  -Method Post -TimeoutSec 120 -Body (@{
    model  = $env:LOCAL_MODEL
    prompt = "Reply with the single word: ready"
    stream = $false
  } | ConvertTo-Json); $r.response
```

Bash form:

```bash
curl -s --max-time 120 "$OLLAMA_URL/api/generate" \
  -d "{\"model\":\"$LOCAL_MODEL\",\"prompt\":\"Reply with the single word: ready\",\"stream\":false}" \
  | jq -r '.response'
```

**If it does not print `ready`, stop here and report exactly what it printed.**
Do not continue. Do not try a different model to make it pass.

**B0.4a** Record the machine, script-written, to
`local/data/score/hardware.json`: `nvidia-smi --query-gpu=name,memory.total
--format=csv`, total system RAM, free disk. The GPU's VRAM figure decides which
models are even loadable — a 5070 is 12 GB, a 5070 **Ti** is 16 GB, and the
difference changes what B1 can run. Do not assume which card is installed.

**B0.4** Create the tree in §5 of the plan. Empty directories with a
`.gitkeep`. Then write `local/scripts/build-index.ps1`: it walks
`local/data/`, and writes `local/index.json` — one entry per dataset with
`path`, `rows`, `bytes`, `built_ts`, `schema`. Never hand-written.

**B0.5** Write `local/roster.yaml` by hand, once. Eleven rows from the plan's
§2 table, with the four unfilled shadows left as `job: null`. Transcribe the
real Hermes seat names into the `shadows:` field. Each row carries
`licence: L0`, `death_test:` and `l4_grants: []`.

**B0.6** The exact `local/roster.yaml` skeleton. Eleven rows, four left null.

```yaml
# Farid-owned. No agent may edit this file. Same standing as marketing/control.yaml.
version: 1
agents:
  - name: hamada
    shadows: builder
    kind: seat
    job: triage
    licence: L0
    death_test: "invented_paths > 2 in 50 rows OR top1 < 0.40"
    l4_grants: []
  - name: hunter
    shadows: null
    kind: seat
    job: brands
    licence: L0
    death_test: "invented > 5 in 50 rows"
    l4_grants: []
  - name: shadow-qc
    shadows: "<Hermes QC seat name>"
    kind: seat
    job: qc
    licence: L0
    death_test: "agreement < 0.85 at 200 rows OR publish_when_review > 0.05"
    l4_grants: []
  - name: shadow-redteam
    shadows: "<Hermes Red Team seat name>"
    kind: seat
    job: null
    licence: L0
    death_test: "false_flags > 3 in 50 rows"
    l4_grants: []
  - name: shadow-pm
    shadows: "<Hermes PM seat name>"
    kind: seat
    job: null
    licence: L0
    death_test: "accuracy <= baseline at 100 settled rows"
    l4_grants: []
  - name: shadow-4
    shadows: "<Hermes seat 4>"
    kind: null
    job: null          # stays null until a settleable question exists
    licence: L0
    death_test: null
    l4_grants: []
  - name: shadow-5
    shadows: "<Hermes seat 5>"
    kind: null
    job: null
    licence: L0
    death_test: null
    l4_grants: []
  - name: shadow-6
    shadows: "<Hermes seat 6>"
    kind: null
    job: null
    licence: L0
    death_test: null
    l4_grants: []
  - name: shadow-7
    shadows: "<Hermes seat 7>"
    kind: null
    job: null
    licence: L0
    death_test: null
    l4_grants: []
  - name: academy
    kind: script
    job: licence_registrar
  - name: cabinet
    kind: script
    job: report_surface
allowlist_readonly:
  - "Get-ChildItem"
  - "Get-Content"
  - "Get-Process"
  - "Test-Path"
  - "git status"
  - "git log"
```

**Gate G0 prints:** the word `ready`, then `build-index.ps1` output showing
`local/index.json` written with 0 datasets.

---

## B1 — First seat: brand extraction (`hunter`)

Unchanged from the original README. Do not improve it mid-flight.

**B1.1** `local/seats/seat-brands.ps1`. Input on stdin: the raw description text
of one pipe-lot listing. Output on stdout: brand names found in that text, one
per line, nothing else. No brand named → print nothing, exit 0.

The prompt must tell the model to **copy brand names that appear in the text and
never to guess a brand that is not written there**. A guessed brand is a wrong
answer, not a partial one. Obeys the seat contract: stdout is the answer only,
logging to stderr, 120s timeout, non-zero exit on timeout/empty/bad JSON,
writes no file.

**B1.2** `local/scripts/build-labeled-set.ps1 -Seat brands -Rows 50`. Pulls rows
from the sold corpus that have both a description and a known brand list, writes
`local/data/labeled/brands.jsonl`:

```
{"id": "...", "input": "...", "known_answer": ["...", "..."]}
```

Script-written, never hand-edited. Fewer than 50 usable rows → write what exists
and print the count to stderr. `-Rows` is a parameter from the first version, so
that 200 rows at B2 needs no new script.

**B1.3** `local/scripts/run-seat.ps1 -Seat brands`. Reads the labeled set, pipes
each `input` into the seat, appends one line per row to
`local/data/ledger/brands.jsonl`:

```
{"ts","id","seat","seat_answer":[],"known_answer":[],"hit":0,"missed":0,"invented":0,"seconds":0.0}
```

- `hit` — brands the seat found that are in the known list
- `missed` — known brands the seat did not find
- `invented` — brands the seat printed that are neither in the known list nor
  present in the description text

Append-only. Never rewritten, never cleaned, never hand-edited.

**B1.4** `local/scripts/report-seat.ps1 -Seat brands` prints five lines and
nothing more:

```
rows scored:    50
total hits:     123
total missed:   31
total invented: 4
avg seconds per listing: 6.2
```

**Gate G1 — the death test, set before the run:** invented > 5 across 50 rows and
this seat has failed. Stop. No prompt tuning, no bigger model, no rerun for
luck. Write to `local/data/score/brands.jsonl` that local brand extraction does
not work, and fall back to plain-text matching against the brand dictionary.
invented ≤ 5 → the seat is usable; continue.

---

## B1.5 — The rented benchmark (only if G1 failed)

Full detail in `docs/local-agents-hardware-note.md` §4. **Skip this task
entirely if G1 passed** — there is nothing to buy.

This is a new seat with its own row count, in its own ledger. It is not a
second attempt at the seat that died, and the threshold stays at 5. A rented
GPU does not buy a softer bar.

**B1.5.1** `local/scripts/export-benchmark-set.ps1` → `local/data/bench/bench-rows.jsonl`,
carrying **only** `{"n", "input"}`. The `known_answer` lists stay on the PC and all
scoring happens locally afterwards. Never upload `.env`, `.local-seat-env`,
`roster.yaml`, the genome database, the corpus, or any file containing a SKU.

**B1.5.2** Rent one pod on RunPod (Secure Cloud, image `ollama/ollama`, port
11434 exposed, `OLLAMA_HOST=0.0.0.0`): a 24 GB card for the 30B run, a 48 GB card
for the 70B run. Record the live hourly price at deploy time — not an estimate.

**B1.5.3** Tunnel; do not expose:

```powershell
ssh -N -L 11435:localhost:11434 root@<pod-host> -p <pod-port> -i <key>
$env:OLLAMA_URL  = "http://localhost:11435"
$env:LOCAL_MODEL = "<exact tag as ollama list prints it on the pod>"
```

The seat script runs unchanged. That is what the stdin/stdout contract is for —
the seat does not know which machine answered.

**B1.5.4** Pull one 30B-class model (`qwen3:30b-a3b`, `qwen2.5:32b-instruct-q4_K_M`
or `gpt-oss:20b`) and one 70B-class model (`llama3.3:70b-instruct-q4_K_M` or
`qwen2.5:72b-instruct-q4_K_M`). If a tag does not resolve, pull the nearest and
**record the tag actually used**.

**B1.5.5** Add `-Ledger` and `-Runtime` parameters to the existing `run-seat.ps1`
rather than writing a second runner. Run all three over the identical 50 rows:

```powershell
run-seat.ps1 -Seat brands -Ledger brands-bench -Runtime "local-14b"
run-seat.ps1 -Seat brands -Ledger brands-bench -Runtime "rented-30b"
run-seat.ps1 -Seat brands -Ledger brands-bench -Runtime "rented-70b"
```

Every bench row carries `runtime` and `model_tag`. Then print one block:

```
runtime         model                          rows  hits  missed  invented  s/row
local-14b       <tag>                            50   118      36        12    6.2
rented-30b      <tag>                            50   131      23         2    3.4
rented-70b      <tag>                            50   139      15         1   11.8
```

**B1.5.6** **Terminate** the pod — a stopped pod still bills for its volume —
then open the billing page and confirm the spend stopped. Write the real cost
into `local/data/score/benchmark-rented.jsonl`. An estimated cost is a story.

**The decision, set in advance. Buy what this table says and nothing else:**

| Result | Buy |
|---|---|
| local-14b already ≤ 5 | Nothing. G1 passed and this task should not have run. |
| local > 5, **rented-30b ≤ 5** | RAM to 64 GB, then a used 24 GB card. You now know the exact model tag to run on it. |
| only **rented-70b ≤ 5** | **Nothing.** That is £3–4k of hardware for one reading job — use the brand dictionary, or send that job to CODE. |
| all three > 5 | **Nothing.** G1's verdict stands: local brand extraction does not work. Fall back to dictionary matching. |

Report the outcome in the six-line form with `gate: B1.5` and the chosen row of
that table as `verdict:`.

## B2 — Harden the seat that passed

Only after G1 passes.

**B2.1** `build-labeled-set.ps1 -Seat brands -Rows 200`. Same script, new count.

**B2.2** Re-run through the same seat, same ledger, appended — never rewritten.

**B2.3** `local/scripts/write-score.ps1 -Seat brands` appends one line per run to
`local/data/score/brands.jsonl`:

```
{"run_ts","seat","rows","hits","missed","invented","invented_per_50","avg_seconds"}
```

This file is the feed. Everything the academy script does later reads it.

**B2.4** Record the latency as a fact. If seconds-per-listing is unusable, say
the number. Do not optimise the model; design around it.

**Gate G2:** invented-per-50 ≤ 5 at 200 rows.

---

## B3 — The watchers (no model, highest value in this build)

These need no gate above them and no model. Build them even if G1 failed.

**B3.1** `local/scripts/pull-corpus.ps1` — reads the Etsy sold export, the eBay
active export and the eBay sold export from a folder Farid drops them in, and
normalises each to `local/data/corpus/<source>-<kind>.jsonl` with at minimum
`{"sku","listing_id","title","state","ts"}`. SKU mapping comes from the genome
store (`marketing/genome/store.py`); where a SKU is unknown, write the row with
`"sku": null` and count those rows to stderr. Never drop a row silently.

**B3.2** `local/watchers/watch-crosspost.ps1` — the one Farid asked for first.
For every SKU sold on Etsy, check whether it is still live on eBay, and the
reverse. Append to `local/data/collisions.jsonl`:

```
{"ts","sku","sold_on","sold_ts","still_live_on","live_listing_id","age_hours"}
```

It emits. **It does not delist.** Delisting stays manual for the life of this
plan.

**B3.3** `local/watchers/watch-inventory.ps1` — flags three conditions per SKU:
live in two places at once, live with zero stock, in stock with no live listing.
Same append-only ledger shape.

**B3.4** `local/watchers/watch-ledger-integrity.ps1` — fails loudly if any
ledger file shrank, lost its append-only ordering, or changed schema between
runs.

**Gate G3 — correctness test, not a death test.** Plant three known collisions
and run against 20 SKUs known to be clean. The watcher must catch all three and
raise zero false alarms. A miss or a false alarm is a bug in the script; fix it
and re-run. This gate may be re-run as many times as it takes — that is the
difference between a watcher and a seat.

---

## B4 — Hamada, the triage seat

**B4.1** `local/scripts/build-labeled-set.ps1 -Seat triage -Rows 50` builds its
own labels from git history: for each recent fix commit, the input is the error
text from the commit message or the linked log, and `known_answer` is the file
list from `git show --name-only`. No human labels this set.

**B4.2** `local/seats/seat-triage.ps1` — input on stdin: error text plus the
output of `git ls-files` truncated to the relevant directories. Output: exactly
one repo-relative file path, or nothing if it cannot name one. One path. Not a
ranked list, not an explanation.

**B4.3** Score with the same `run-seat.ps1`: `hit` = the path is in the fix
commit's file list; `invented` = the path does not exist in the repo.

**Gate G4:** top-1 ≥ 40%, invented paths ≤ 2 in 50 rows. Below either number,
hamada stays at L0 and the build continues without him.

---

## B5 — 24/7

**B5.1** `local/scripts/run-watchers.ps1` — runs every watcher in order, appends
their ledgers, writes `local/data/heartbeat.json` with a per-watcher last-run
timestamp and exit code, and prints one five-line report per watcher. No
retries, no queue, no auto-tuning.

**B5.2** Register it in Windows Task Scheduler every 15 minutes. Put the exact
`schtasks` command in `local/scripts/install-schedule.ps1` so the schedule
itself is script-written and reproducible.

**B5.3** `local/watchers/watch-heartbeat.ps1` — fails loudly when any watcher has
not run in 45 minutes. One alert, then stop alerting. No silent retries — the
same rule `marketing/control.yaml` already sets for spend ceilings.

**Gate G5:** 14 consecutive days, zero silent failures. A missed run is
acceptable only if it produced an alert.

---

## B6 — First shadow: `shadow-qc`

The labels are free — `marketing/qagate/gate.py:route_item()` already decides
REVIEW or PUBLISH deterministically.

**B6.1** `build-labeled-set.ps1 -Seat qc -Rows 200` runs `route_item()` over 200
items and records its decision as `known_answer`.

**B6.2** `local/seats/seat-qc.ps1` — input: the item's fields as text. Output:
one word, `REVIEW` or `PUBLISH`. Nothing else.

**B6.3** Score: agreement rate, plus the confusion split (how often it said
PUBLISH when the gate said REVIEW — that direction is the expensive one and is
reported separately).

**Gate G6:** ≥85% agreement at 200 rows, and PUBLISH-when-gate-said-REVIEW under
5%. Below that, this shadow is dead; try `shadow-redteam` next, same shape.

---

## B7 — Academy, cabinet, and the first proposal

**B7.1** `local/scripts/academy.ps1` — reads every file in `local/data/score/`,
applies the ladder in §4 of the plan, and appends promotions and demotions to
`local/data/licence.jsonl`:

```
{"ts","name","from","to","reason","evidence_rows","evidence_file"}
```

It never issues L4 — L4 comes only from a `l4_grants:` entry Farid writes in
`roster.yaml`. It demotes to L0 automatically on a breached death test.

**B7.2** `local/scripts/cabinet.ps1` — prints every seat's five-line report, the
current licence table, the last heartbeat, and the open collision count. Text
only. No HTML, no server, no browser.

**B7.3** First proposal round: hamada at L2 writes one
`local/proposals/<ts>-hamada.json` per the contract in §1 of the plan. CODE
reads it, implements or rejects it, and the registrar records which. A proposal
with no `rollback` field is rejected by the script before a human sees it.

**Gate G7:** the first L2 licence appears in `licence.jsonl`, written by the
script, and the first proposal is marked accepted or rejected.

---

## After G7

Four weeks of the daily runner holding with no gate reopened. Then, and only
then, reconsider what is banned: an MCP server, a read-only local UI over the
ledgers, a third seat, the next shadow. Each one gets a written proposal first,
a death test set before the run, and facts-only reporting.

## The exact seat prompts

Use these strings. Do not improve them, do not add "be helpful", do not add
examples. Every seat call sets `temperature: 0` and `stream: false`.

**`seat-brands`**

```
You extract brand names from marketplace listing text.
Rules:
- Copy brand names exactly as they are written in the text.
- Never output a brand that is not written in the text.
- One brand per line. No numbering, no commentary, no blank lines.
- If the text names no brand, output nothing at all.

TEXT:
<<<
{INPUT}
>>>
```

**`seat-triage`**

```
You name the single file most likely responsible for an error.
Rules:
- Output exactly one repo-relative file path, copied from the FILES list.
- Never output a path that is not in the FILES list.
- No explanation, no ranking, no second choice.
- If no file in the list is a plausible cause, output nothing.

ERROR:
<<<
{STDERR}
>>>

FILES:
<<<
{GIT_LS_FILES}
>>>
```

**`seat-qc`**

```
You predict one routing decision for a product listing.
Answer with exactly one word: REVIEW or PUBLISH.
REVIEW means a Tier A field (brand, maker, era, restricted material) is
uncertain, unsupported by the photos or OCR text, or missing.
No explanation. No punctuation. One word.

ITEM:
<<<
{ITEM_FIELDS}
>>>
```

If a seat returns anything other than the shape above, that is a scored wrong
answer. It is not a reason to edit the prompt mid-run. The prompt may only
change before a run starts, and a changed prompt resets the row count to zero.

## Report back after every gate

Six lines, no prose:

```
gate:        G1
date:        2026-09-22
rows:        50
result:      invented 4
verdict:     pass
next:        B2
```
