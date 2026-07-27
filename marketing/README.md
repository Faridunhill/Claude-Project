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

**`policy.py` enforces them.** Before it existed the walls were declared
but unread by any module — a "ceiling" was a comment. Every spend and
post decision now routes through `load_walls()`, and an absent config
key defaults to *prohibited*, never to *allowed*.

### POLICY-META-ADS-001 — no paid Meta promotion, ever

Meta prohibits paid advertising for tobacco products and smoking
paraphernalia; estate pipes fall under it. This is **not a budget of
zero** — it is a capability that does not exist. `SocialEngine.
request_boost()` is the single choke point and raises
`PaidPromotionProhibited` by design. Boosting risks the ad account *and*
the Page.

Distribution is **organic only**: own Page, own Instagram, own groups.
That is unaffected and is the entire strategy. Marketplace promoted
listings (Etsy/eBay) are a *separate* platform with separate rules,
kept in their own config block and disabled pending Farid's number.

### Video: CapCut replaced by the free in-house renderer

`visual_generation.vendor: local_ffmpeg` — real photos, Ken Burns
motion, title + FARIDUNHILL overlay, licensed house music, rendered on
the PC by `social/video.py`. **No AI imagery, no vendor, £0 per asset.**
Paid vendors stay off (`paid_vendors_enabled: false`); any non-zero
charge raises `SpendCeiling`.

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

P2.1 ✅ store hygiene · P2.2 ✅ genome layer · P2.3 ✅ intake pipeline
(`intake/`, `INTAKE_GUIDE.md`) · P2.4 ✅ QA gate (`qagate/`) ·
P2.5 ✅ five-event ledger (`phenotype/`) · P2.6 ✅ copy generators
(`expression/`) · P2.7 ✅ social engine (`social/`) · P2.8 ✅
encyclopedia flywheel (`encyclopedia/` + store `/archive` and
`/collections/[brand]` routes) · P2.9 ✅ spend/policy walls enforced
(`policy.py`, `control.yaml` v2) — vendor decided: **free local
renderer, £0**; paid Meta promotion permanently prohibited.

## What is still waiting on Farid (at the PC)

1. **Meta credentials** → follow `docs/META_SETUP.md`, then say
   "Meta credentials are on the PC" and the publisher switches from
   `DryRunPublisher` to live. Until then **nothing posts** — by design.
2. **Priority 1 connector** → `genome/adapter_itemassets.py` still
   returns `PlaceholderSource()`. The Eye's photos, vision claims and
   stamping OCR are invisible to marketing until one class is
   implemented there. It fails loudly (`NotConnected`), never silently
   empty.
3. **Marketplace promoted listings** → confirm platform + monthly
   number, or leave disabled. Nothing spends while `enabled: false`.

Note: Priority 1 (the Eye — photo corpus + DINOv3 stack) is a *separate
system on the PC*. Marketing consumes it as a client and never
retrains it. Photos and model weights do not live in this repo.
