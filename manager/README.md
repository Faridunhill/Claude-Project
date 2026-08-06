# THE DESK — the Encyclopedia Manager

The coordinator Farid asked for: one standing manager on his PC that brainstorms and
reinforces ideas, looks after the machine through PowerShell, gives orders to the local
agents, schedules the work, and gets better over time — without ever being able to drift
off the honesty laws.

This directory is the code. It runs on Farid's PC, not in the cloud; the cloud front (the
Next.js site in this repo) is untouched by it. The two halves sync through `channel/`, as
they already do.

---

## What it does

| Ask | Where it lives | How it works |
|---|---|---|
| Coordinate the local agents | `desk/queue.py` | SQLite job queue. Workers claim jobs; the manager assigns, blocks, and closes them. Survives reboots. |
| Brainstorm, suggest, **reinforce** | `desk/ideas.py` | Ideas are durable rows. An idea only gets stronger when new *evidence* is attached, so the ones that survive contact with reality rise and the rest sink. Parked ideas are never deleted. |
| PC management via PowerShell | `desk/machine.py` | A fixed registry of named commands — updates, drivers, disk, GPU, memory, Defender, startup, temp. |
| Schedule downloads, updates, GPU work | `desk/queue.py` | Priority + `run_after` + `needs_gpu`. GPU jobs are not handed out until Farid sets the all-clear. |
| Improve itself over time | `desk/harness.py` | The Academy: an evidence-backed, append-logged memory of lessons, skills and agent specs, loaded into every future run. |
| Stay in sync with the cloud | `desk/channel.py` | Reads `channel/TO_AGENT`, writes numbered notes to `channel/TO_FARID`. |

---

## The three safety properties

Farid's laws are not comments in this codebase — they are enforced, and each one has a
test that fails if it stops being true.

**1. The model never writes PowerShell.** It picks a name from the registry and we run the
fixed string. No prompt turns `winget list` into a delete, because the model's only input
is a key lookup. Destructive commands aren't gated — they're *absent*. Adding one is a
deliberate edit to `machine.py`.

**2. Nothing changes the machine without Farid's token.** Read-only CHECK commands run
unattended. ACTION commands need a single-use, expiring token he mints with
`desk approve <action>`. A token for one action does not work on another, and does not
work twice.

**3. The Academy cannot teach itself out of the laws.** `laws.md` is hash-locked in
`laws.lock`; if it changes without a deliberate relock, the Manager refuses to start.
Self-improvement writes only to the separate refinable layer, and every entry passes a
law-guard that rejects anything combining a protected topic (approval, honesty, the
piracy rule, Farid's decision gates) with loosening language. The rejection is logged.

Verified end-to-end against a stubbed model that tried both attacks:

```
[ERR] REFUSED: 'restart.now' changes the machine and needs an approval token from Farid.
[ERR] REFUSED BY LAW-GUARD: touches protected topic 'approv' with loosening language 'Skip'.
[ok ] learned 'lesson:restart-needs-a-token'
```

---

## Install (Windows)

Python 3.11+ and a Claude Pro/Max login or an API key.

```powershell
cd $env:USERPROFILE\Desktop\FARID_CLAUDE_CHANNEL\manager
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy config.example.json config.json     # then set channel_dir to your real path
py -m desk.cli laws                      # should print a verified digest
py -m desk.cli check                     # read-only sweep, no model, no network
py -m desk.cli seed                      # put the standing daily work on the queue
```

`desk check` is deliberately model-free and network-free — it has to work when the API is
down or the key has expired.

---

## Daily use

```powershell
py -m desk.cli brief                 # the standing daily run
py -m desk.cli run "..."             # one run against your own instruction
py -m desk.cli queue                 # what the agents are working on
py -m desk.cli review                # everything the Manager has taught itself
py -m desk.cli approve updates.apply # mint one token, then tell it to go ahead
```

To run it every morning, Task Scheduler → daily at 08:00 →
`...\.venv\Scripts\python.exe -m desk.cli brief`.

`desk review` is the one to read weekly. It prints the refinable memory newest-first, and
the full append-only history is in `state/harness_log.jsonl` — every change with its
evidence and a before/after. Self-improvement you can audit as a diff.

---

## Honest status

- **Tested here (26 tests, all passing):** laws lock and tamper detection, the approval
  gate, single-use and action-scoped tokens, expiry, the law-guard in both directions,
  Academy round-trip and logging, the GPU hold, queue priority and lifecycle, the idea
  ledger, channel numbering. Plus the full agent loop against a stub client.
- **Not tested here:** the PowerShell command strings. This container is Linux with no
  `pwsh`, so every check returns a structured "unavailable" rather than real output.
  **They need one pass on the real machine** — `desk check` will show which, if any,
  need adjusting for the Windows build. That's the first thing to do after install.
- **Not written yet:** the workers that claim jobs and do the harvesting. The queue,
  the orders, and the manager are here; the hands are the next piece.

## Model configuration

`claude-opus-5`, effort `high`, no `thinking` field (thinking is on by default on this
model) and no sampling parameters (removed — they return 400). The laws block is a
separate cached system block: byte-stable across every run, so it stays in the prompt
cache while the memory and scoreboard churn beneath it.
