# Local Seats — Full Plan v1.0 (superseded)

> Transcribed from the PDF "Local Seats — Full Plan, Version 1.0, September 2026"
> so the lineage exists in text. **Superseded by
> `docs/local-agents-system-plan.md` (v2.0).** Kept because v2.0 carries every
> rule below forward unchanged — the death test, facts-not-status, one seat at a
> time, and scripts write every file.

## Purpose

The council of AI agents produced opinions that could never be scored. Local
shadow agents improved slowly because nothing recorded who was right. This plan
fixes the job shape: local models stop giving opinions and get one narrow job on
real data, where the answer can be checked against something already known. You
stay the supervisor and keep the judgment work; local models do the reading.

## Phase 0 — Verification

Prove the endpoint before any code exists. `ollama list`, write `.local-seat-env`
with `LOCAL_MODEL` and `OLLAMA_URL`, then probe with the single-word `ready` curl.

**Gate G0** — If the probe does not print `ready`, stop. Report the output. Go no
further.

## Phase 1 — The first seat (README steps 1–6, unchanged)

Seat contract: reads stdin, prints only the answer to stdout, logging to stderr,
`--max-time 120`, exits 0 only when an answer was produced, never writes a file.

Build items: `seats/seat-brands.sh`, `scripts/build-labeled-set.sh`,
`scripts/run-seat-brands.sh`, `scripts/report-brands.sh`.

**Gate G1 — death test, set in advance:** invented > 5 across 50 rows and the
seat has failed. No prompt tuning, no bigger model, no reruns. Fall back to
plain-text matching against the brand dictionary. invented ≤ 5 and the seat is
usable.

## Phase 2 — Hardening the seat that passed

Scale to 200 rows via the same script. Same ledger, appended. Score file per
seat: `data/score-seat-brands.jsonl`, script-written — the record that makes
shadow agents comparable to seats, the feed that was missing. Latency is
recorded as a fact, not optimised away.

**Gate G2** — invented-per-50 stays ≤ 5 at 200 rows.

## Phase 3 — The second seat

Candidates in order of checkability: completeness check, condition-flag
extraction, language detection. Same shape, own death test set before the run.

**Gate G3** — second seat passes its pre-set false-positive threshold at 50+
rows. Two seats may run side by side. Still no orchestrator.

## Phase 4 — Wiring seats into real work (still no orchestrator)

A single dispatcher `scripts/run-daily.sh`, run by you or cron. Shadow agents get
scores too, in the same ledger format against the same known answers. You keep
judgment: seats read, you decide what the numbers mean.

## Phase 5 — Only if Phase 4 holds for 4+ weeks

Then, and only then, consider what was banned: an MCP server, a minimal
read-only local UI, a third seat. Written proposal first, death test before the
run, facts-only reporting.

## What does not change, ever

No council orchestration, no seat manager, no auto-tuning, no retry-until-pass.
No writes to eBay, Etsy or faridunhill.com. Every produced file is script-written.
Facts, not status. If a step is impossible or wrong: stop, name the step, say why.

## One-line summary

Verify endpoint → build seat-brands → death test at 50 rows → harder test at 200
→ seat #2 same shape → daily script + shadow scoring → wait 4 weeks → then
consider MCP / UI / seat #3.
