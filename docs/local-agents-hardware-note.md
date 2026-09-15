# Hardware Note — what to buy, what not to, and how to find out

Companion to `docs/local-agents-system-plan.md` and
`docs/local-agents-builder-brief.md`. Task **B1.5** at the end of this file is
the builder's job, written out in full. Nothing in it needs a decision from
Farid except pressing "deploy" and paying about £3.

---

## 1. The machine as it stands

| Part | What is there | What it means for models |
|---|---|---|
| GPU | RTX 5070, **12 GB** VRAM | The wall. Everything below is decided by this number. |
| CPU | Ryzen 7 | Irrelevant for GPU inference. Matters only for CPU offload. |
| RAM | **16 GB** | The real bottleneck today. Windows + a browser take 6–8 GB before Ollama opens. |
| Storage | 2 TB SSD | Plenty. A 30B model at Q4 is ~18 GB on disk. |

**Confirm the card first.** A 5070 is 12 GB; a 5070 **Ti** is 16 GB. If it is
the Ti, every VRAM figure below shifts one row and the 14B sits comfortably.
`nvidia-smi --query-gpu=name,memory.total --format=csv` settles it. Record the
output in `local/data/score/hardware.json` — script-written, like everything else.

### What fits in 12 GB

Rough rule: parameters × 4.5 bits ÷ 8 = GB, then add 1–3 GB for the KV cache,
which is what holds the context.

| Model class | Weights at Q4_K_M | Verdict on 12 GB |
|---|---|---|
| 7–9 B | ~5–6 GB | Comfortable. Long context. |
| 14 B | ~8.5–9 GB | Fits, with ~2.5 GB left for context — roughly 8–16k tokens and no more |
| 24–32 B | ~18–20 GB | Does not fit. Spills to system RAM, where 16 GB is already tight |
| 30B MoE (3B active) | ~18 GB | Only with CPU offload, which needs the RAM upgrade first |
| 70 B | ~40 GB | Not on this machine at any setting worth using |

---

## 2. The upgrades, ranked by what they actually buy

| Upgrade | Cost | What changes | Verdict |
|---|---|---|---|
| **RAM 16 → 64 GB** | £110–160 | MoE models via CPU offload, longer context, the PC stops choking when the model and a browser coexist | **Do it regardless of everything else on this page** |
| Used RTX 3090, 24 GB | £550–750 | 32B at Q4 with real context. Best £ per GB of VRAM there is | Only after B1.5 says so |
| RTX 5070 Ti / 5080, 16 GB | £700–1000 | 14B with proper context. Still no 32B | Poor value for this job — you are buying VRAM, and 16 GB does not reach the next class |
| RTX 5090, 32 GB | £1800–2300 | 32B comfortably, 70B at low quant | Only if money is not the constraint |
| **Second PC with no GPU** | — | **Nothing.** Splitting one model across two boxes replaces a ~670 GB/s memory link with a ~0.1 GB/s Ethernet one | Do not do this |
| Second PC as a watcher box | £150–300 used mini-PC | Watchers run every 15 minutes forever without the main PC having to stay up | Worth it at B5, for uptime — not for intelligence |
| Cloud GPU, 24/7 | $300–500/month | An always-on 24 GB card | No. More than CODE costs, and it ends "only CODE and my locals" |
| **Cloud GPU, one hour** | **~£3** | The answer to whether any of the above is worth buying | **This is B1.5** |

### Before buying a used 3090, check three physical things

1. **PSU** — 750 W minimum with two spare 8-pin PCIe connectors. A typical
   5070 build ships with 650–700 W and will not carry a 3090 as well.
2. **Case length** — most 3090s are 310–336 mm. Measure.
3. **What happens to the 5070** — keep it in the second slot for display and
   let the 3090 do inference, or sell it. Mixing the two for one model split
   across both works in llama.cpp but is fiddly; do not plan on it.

---

## 3. Two honest limits, stated before money is spent

**A bigger local model does not become a code writer you can trust.** Going
from 14B to 32B improves triage and draft patches. It does not change the
verdict in §9 of the plan: CODE writes the code, the local narrows the search.
No consumer GPU at any price in this range buys anything different.

**None of the three seats in the plan need a bigger model.** "Copy the brand
names that appear in this text" and "REVIEW or PUBLISH" are extraction and
classification. A 9B does those. If `seat-brands` invents twelve brands, the
likely fault is the job or the labelled data, not the GPU — and B1.5 is how
that is settled for £3 instead of £700.

---

## 4. Task B1.5 — the rented benchmark

**Run this only if G1 failed** (invented > 5 on 50 rows). If G1 passed, there is
nothing to buy and this task is skipped entirely.

This is a **new seat with its own row count**, recorded in its own ledger. It is
not a second attempt at the seat that died. The death test number stays 5 — a
rented GPU does not buy a softer bar.

### B1.5.1 — Export the rows, and only the rows

Write `local/scripts/export-benchmark-set.ps1`. It reads
`local/data/labeled/brands.jsonl` and writes
`local/data/bench/bench-rows.jsonl` containing **only** the input text and a row
number:

```
{"n": 1, "input": "Konvolut 8 Pfeifen ..."}
```

The `known_answer` lists stay on the PC. The rented machine generates answers;
**all scoring happens locally afterwards**. Nothing about what Farid bought, paid
or owns leaves the building.

Do not upload: `.env`, `.local-seat-env`, `roster.yaml`, any API key, the genome
database, the corpus, or any file with a SKU in it. The bench rows are public
marketplace description text and nothing else.

### B1.5.2 — Rent the box

RunPod (simpler) or Vast.ai (cheaper, more fiddly). On RunPod:

1. Deploy a **Secure Cloud** pod.
2. GPU: **1 × 24 GB** (RTX 3090, A5000 or equivalent) for the 30B run.
   For the 70B run: **1 × 48 GB** (A6000 or L40S) — a 70B at Q4 needs ~40 GB.
3. Image: `ollama/ollama`. Container disk 20 GB, volume 100 GB.
4. Expose port `11434` and set `OLLAMA_HOST=0.0.0.0`.
5. Record the live hourly price at the moment of deploy. Do not use the
   estimates on this page as the figure in the report.

Expect roughly $0.20–0.45/hr for 24 GB and $0.60–0.90/hr for 48 GB. Both runs
together should finish inside one hour.

### B1.5.3 — Tunnel, do not expose

```powershell
ssh -N -L 11435:localhost:11434 root@<pod-host> -p <pod-port> -i <key>
```

Then the seat script runs **completely unchanged** — only two environment
variables move:

```powershell
$env:OLLAMA_URL  = "http://localhost:11435"
$env:LOCAL_MODEL = "<exact tag as ollama list prints it on the pod>"
```

That is the whole point of the stdin/stdout seat contract: the seat does not
know or care which machine answered. If SSH is unavailable, RunPod's HTTPS proxy
URL for port 11434 works, but it is unauthenticated — use it only for these
public description rows, never for anything else.

### B1.5.4 — Pull the models and record the exact tags

Candidates, in order of interest:

| Slot | Candidate tags | VRAM needed |
|---|---|---|
| 30B class | `qwen3:30b-a3b`, `qwen2.5:32b-instruct-q4_K_M`, `gpt-oss:20b` | 24 GB |
| 70B class | `llama3.3:70b-instruct-q4_K_M`, `qwen2.5:72b-instruct-q4_K_M` | 48 GB |

If a tag does not resolve, pull the nearest available and **record which tag was
actually used** in the results file. A benchmark whose model name is guessed
afterwards is worthless.

### B1.5.5 — Run, score locally, print five lines

Add two parameters to the existing runner rather than writing a second one:

```powershell
run-seat.ps1 -Seat brands -Ledger brands-bench -Runtime "rented-30b"
run-seat.ps1 -Seat brands -Ledger brands-bench -Runtime "rented-70b"
```

Every row written to `local/data/ledger/brands-bench.jsonl` carries
`"runtime"` and `"model_tag"`. The local 14B run is re-scored into the same
bench ledger as `-Runtime "local-14b"` so all three are compared on identical
rows. `report-seat.ps1 -Ledger brands-bench -Runtime <name>` prints the same
five lines per runtime, and one comparison block:

```
runtime         model                          rows  hits  missed  invented  s/row
local-14b       <tag>                            50   118      36        12    6.2
rented-30b      <tag>                            50   131      23         2    3.4
rented-70b      <tag>                            50   139      15         1   11.8
```

### B1.5.6 — Destroy the pod, and prove it

Stop **and terminate** the pod — a stopped pod still bills for its volume.
Then open the billing page and confirm the spend stopped. Write the real cost
into `local/data/score/benchmark-rented.jsonl` alongside the results. A
benchmark whose cost is estimated is a story, not a fact.

---

## 5. The decision, set in advance

Read the table, buy what it says, and nothing else. `invented` is the number
that decides, exactly as it does at G1.

| What the benchmark shows | What it means | What to buy |
|---|---|---|
| local-14b already ≤ 5 | G1 passed; B1.5 should not have run | Nothing |
| local > 5, **rented-30b ≤ 5** | A 24 GB card fixes it, and you now know the exact model tag to run | RAM to 64 GB, then a used 24 GB card |
| local > 5, 30b > 5, **rented-70b ≤ 5** | Only a 48 GB-class model passes. That is £3–4k of hardware for one reading job | **Nothing.** Use dictionary matching for brands, or send that one job to CODE |
| all three > 5 | The fault is the job or the labelled data, not the GPU | **Nothing.** G1's verdict stands: local brand extraction does not work. Fall back to plain-text matching against the brand dictionary |

The third row is the one that saves the most money and is the easiest to talk
yourself out of. A model that only passes on a 48 GB card has not proven the
upgrade is worth it; it has proven the job is too hard for hardware at this
price.

---

## 6. The watcher box, if a second PC is bought

Only at B5, and only for uptime. Specification: any used mini-PC, 8 GB RAM, no
GPU, wired Ethernet, £150–300. It runs `run-watchers.ps1` on the 15-minute
schedule and nothing else — no model, no seats, no proposals. The main PC can
then be rebooted, updated and used normally without breaking the heartbeat that
G5 depends on.

---

## 7. Cloud GPU as a permanent home — the numbers that rule it out

A 24 GB card on demand at roughly $0.35/hr is about **$250/month** if it never
sleeps, and a 48 GB card is closer to **$500**. That is several times the cost of
the CODE subscription that already does the hard work better, it puts the data
on someone else's machine, and it ends the one premise the whole plan is built
on — that only CODE and the local agents are in the loop.

Rent by the hour to answer a question. Do not rent by the month to host a
capability.
