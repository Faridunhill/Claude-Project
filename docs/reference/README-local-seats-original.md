# Local Seats — README for Claude Code

Read this fully before writing any code. Then build only what is in Steps 1 to 6.

---

## The problem

We have a council of AI agents that reviews designs. Each seat reads a design document and writes an opinion about it. The council runs under your supervision, it takes weeks, it costs money, and at the end nothing is built and nothing is measured.

The reason is not the model and not the supervision. It is the job shape. An opinion about a document can be produced forever. There is no point where it is finished and no way to tell if a seat was right.

We have also built local agents that shadow the council seats, and one that shadows you. They are improving very slowly. They will keep improving very slowly forever, because nothing records who was right. A shadow with no score is not learning. It is just running.

This is the same failure that killed the Helper. The Helper was given a broad job description and no live data feed, and after 149 tests it was still wrong. Setup makes an agent exist. A feed makes it useful.

## What we are changing

Local models stop giving opinions. They get one narrow job on real data, where the answer can be checked against something we already know.

You stay the supervisor and you keep the judgment work. The local models do the reading.

## What NOT to build

Do not build any of these. If one seems necessary, stop and say so instead of building it.

- No MCP server yet. Shell scripts first.
- No second seat until the first one has fifty scored rows.
- No council orchestration, no seat manager, no queue, no web UI, no dashboard.
- No model fine-tuning, no prompt auto-tuning, no retry-until-it-passes loop.
- No changes to live listings on eBay, Etsy, or faridunhill.com. This build reads data only.
- No hand-filled files. Every file in this system is written by a script.

---

## Step 1 — Prove the local endpoint answers

Ollama runs on `http://localhost:11434`. Confirm it is up and pick the model we will use.

```bash
ollama list
```

Choose one model from that list and put the name in a file at the repo root called `.local-seat-env`:

```bash
LOCAL_MODEL=<name exactly as ollama list prints it>
OLLAMA_URL=http://localhost:11434
```

Then prove a plain request works end to end:

```bash
curl -s --max-time 120 "$OLLAMA_URL/api/generate" \
  -d "{\"model\":\"$LOCAL_MODEL\",\"prompt\":\"Reply with the single word: ready\",\"stream\":false}" \
  | jq -r '.response'
```

If that does not print `ready`, stop here and report what it printed. Do not continue.

## Step 2 — The seat contract

Every seat is one shell script in `seats/`. Every seat obeys these rules, with no exceptions:

- Reads its input text from stdin.
- Prints only its answer to stdout. Nothing else. No progress text, no banner, no explanation.
- Prints all logging and errors to stderr.
- Uses `--max-time 120` on the curl call.
- Exits 0 only when it produced an answer. Any timeout, empty response, or bad JSON exits non-zero.
- Never writes to any file. A seat answers, it does not record.

This matters because you will call these scripts and read their output. Anything extra on stdout becomes part of the answer and corrupts the ledger.

## Step 3 — The first seat: brand extraction

Create `seats/seat-brands.sh`.

Input on stdin: the raw description text of one pipe lot listing.

Output on stdout: the brand names found in that text, one per line, nothing else. If no brand is named, print nothing and exit 0.

The prompt must tell the model to copy brand names that appear in the text and never to guess a brand that is not written there. A guessed brand is a wrong answer, not a partial one.

This job was chosen for three reasons. It is reading, not judgment, which is what a small local model can actually do. Around 70% of European lot listings write the brand names in the description as plain text, so the data is really there. And we can check the answer, because we already know what was in the lots we bought.

## Step 4 — The labeled set

Create `scripts/build-labeled-set.sh`.

It pulls fifty listings from the sold corpus that have both a description text and a known brand list, and writes them to `data/labeled-set.jsonl`, one JSON object per line:

```
{"id": "...", "description": "...", "known_brands": ["...", "..."]}
```

Built by the script, from the corpus. Never edited by hand. If fewer than fifty usable rows exist, write what exists and print the count to stderr.

## Step 5 — The ledger

Create `scripts/run-seat-brands.sh`.

It reads `data/labeled-set.jsonl`, pipes each description into `seats/seat-brands.sh`, and appends one line per listing to `data/ledger-brands.jsonl`:

```
{"ts": "...", "id": "...", "seat": "seat-brands", "seat_answer": ["..."], "known_brands": ["..."], "hit": 0, "missed": 0, "invented": 0}
```

- `hit` — brands the seat found that are in the known list
- `missed` — brands in the known list the seat did not find
- `invented` — brands the seat printed that are not in the known list and not in the description text

`invented` is the number that decides whether this is usable. A seat that misses a brand costs us a listing. A seat that invents a brand sends us to buy the wrong lot.

The ledger is append-only. It is never rewritten, never cleaned, never edited by hand.

## Step 6 — The report

Create `scripts/report-brands.sh`. It reads the ledger and prints five lines and nothing more:

```
rows scored:    50
total hits:     123
total missed:   31
total invented: 4
avg seconds per listing: 6.2
```

That report is the whole result of this build. Not a status update, a count.

---

## The death test

Set before we start, so the decision to stop is not an argument later.

Run the fifty rows. If the seat invents more than five brands across fifty listings, this seat has failed. We stop. We do not tune the prompt, we do not try a bigger local model, we do not run it again to see if it gets luckier. We write down that local brand extraction does not work and we go back to reading descriptions with plain text matching against the brand dictionary instead.

If invented is five or under, the seat is usable and we wire the next one the same way.

## Working rules for this build

- One seat, one job, one measurement. The second seat waits.
- Facts, not status. `read 50 listings, 4 invented brands` is a fact. `the seat is working well` is a story. Only print facts.
- Every file the system produces is written by a script. Anything that needs me to fill it in by hand will stop being filled in.
- If something in these steps turns out to be impossible or wrong, stop and say which step and why. Do not work around it and keep going.
