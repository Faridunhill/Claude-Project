# Marketing System — Priority 2 build

Implements the ratified specs: `MARKETING_DNA_SYNTHESIS_v1` +
Advisor F addendum verdicts + `BUILD_HANDOFF_MARKETING_P2`.

## Architecture (three layers)

| Layer | Where | Status |
|---|---|---|
| **GENOME** — immutable birth facts | `genome/` | **P2.2 — built** |
| **EXPRESSION** — generated marketing, disposable, versioned | `expression/` (P2.6–P2.7) | queued |
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

P2.1 ✅ (store hygiene) · **P2.2 ✅ (this)** · P2.3 intake pipeline ·
P2.4 QA gate · P2.5 five-event ledger · P2.6 copy generators ·
P2.7 social engine · P2.8 encyclopedia flywheel · P2.9 visual generation
(last, cohort-level only).
