# Marketing System — Priority 2 build

Implements the ratified specs: `MARKETING_DNA_SYNTHESIS_v1` +
Advisor F addendum verdicts + `BUILD_HANDOFF_MARKETING_P2`.

## Architecture (three layers)

| Layer | Where | Status |
|---|---|---|
| **GENOME** — immutable birth facts | `genome/` | **P2.2 — built** |
| **EXPRESSION** — generated marketing, disposable, versioned | `expression/` | **P2.6 — copy generator built** |
| **PHENOTYPE** — five-event append-only ledger | `phenotype/` (P2.5) | queued |

## What is in `genome/`

- `vocab.py` — controlled vocabularies (enum if a machine branches on it,
  text if a machine narrates from it). Add-only; deprecate, never rename.
- `schema.py` — Pydantic v2 genome schema v1.0. Every field declares its
  downstream consumer (governance rule 2, CI-enforced). Only `sku` and
  `product_type` are required — completeness is a score, never a gate.
- `corrections.py` — append-only corrections ledger + quarantine state
  machine (detect → quarantine → correct → republish). Birth records are
  never edited; `effective = birth + corrections` at read time. There is
  deliberately no "performance" correction reason.
- `store.py` — SQLite store (`genome.db`): insert-only birth table,
  corrections ledger, visibility states.
- `adapter_itemassets.py` — **THE CONNECTOR.** The only file that knows
  Priority 1 (itemassets.db / the Eye) exists. Wire the real database by
  implementing one class here; nothing else changes. Until wired, it
  fails loudly (`NotConnected`) — never silently empty.
- `intake.py` — **P2.3 intake pipeline.** Assembles a birth record from
  the Eye's assets (media, vision claims, stamping OCR) + the human hook
  (`why_special`, economics, floor price), records `field_provenance`
  (source + confidence) on every fact, and writes it insert-only.
  Never blocks on missing fields; fails loud if the Eye is not wired.
  `build_genome()` is pure (unit-testable); `ingest()` orchestrates
  fetch → build → persist. Human facts beat vision claims on the same
  field. It does NOT run the QA gate (that is P2.4) — it records the
  provenance the gate consumes.

## Standing walls

`control.yaml` — the numbers machines never cross (ad caps, visual-
generation ceilings, per-group post walls). Only Farid edits it. Every
ceiling breach = pause + one email, no silent retries.

## Firewall note (LAW 06)

This repository serves the pipe business only. The repeatable-physical
and digital extensions exist in the shared *method* library, never here.
No data, accounts, or credentials cross businesses.

## Running tests

```
pip install pydantic pytest pyyaml
python -m pytest marketing/tests/ -v
```

## Build queue position

P2.1 ✅ (store hygiene) · P2.2 ✅ (genome) · P2.3 ✅ (intake pipeline) ·
P2.4 ✅ (QA gate) · P2.5 five-event ledger · **P2.6 ✅ (copy generator)** ·
P2.7 social engine · P2.8 encyclopedia flywheel · P2.9 visual generation
(last, cohort-level only).

`gate.py` — the four routing rules (confidence / corroboration / price /
audit) over a genome's Tier A claims. Returns a `GateDecision`: PASS
(assert), REVIEW (list, but hedge routed fields until a human verifies),
or RESEARCH_LATER (withhold a high-value unverified attribution). Human
facts are never gated. Reads the `field_provenance` intake records.
