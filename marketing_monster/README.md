# MARKETING MONSTER

The loop, as code, running on two timers with git as the bridge.

`Well → Digger → Judge → Maker → Mouth → Scale → Well`

Spec: `channel/TO_FARID/` — 003 (evaluation) · 004 (build spec) · 006 (automation design).

## How it runs

```
CLOUD — Mondays 06:00 UTC, by itself, Farid's PC off or on
  researches the approved category, writes a dossier, pushes it here
                          │  git
THE PC — every morning 08:00, by itself
  pulls · reads new export files · records sales · writes listings
  digs · proposes lessons · expires stale ones · writes the report
                          │
FARID — answers questions. Nothing else.
```

Four questions are his alone, and always will be — v1.0: *"category picks,
floor prices, spend ceilings, anything crossing a wall. Monster proposes;
Farid disposes."* They arrive one line each in `PENDING.md`:

```
python -m monster answer pipes D-004 yes
```

## What it refuses to do

The interesting part of this codebase is the refusals. Each names the finding
it enforces, so an error teaches the law instead of just blocking.

| Law | Where | It refuses to… |
|---|---|---|
| B1 · no invented attribution | `scale.py` | record a cause without a written reason |
| B2 · no superstition | `playbook.py` | confirm a lesson on one cohort, or accept one with no evidence or expiry |
| B3 · the wall | `wall.py` | let data cross into the shared cookbook wearing a method's coat |
| M2 · reject memory | `judge.py` | re-open a dead category unless you say what changed |
| M3 · scaffolding expires | `digger.py` | store a source without a named permission basis |
| M4 · no personal data | `well.py` | write a name, an email or an address into the Well |
| N1 · rollback key | `maker.py` | publish an asset without the playbook version that made it |
| §2.3 · no lying by omission | `report.py` | print performance before its own blind spots |
| — · sales are sales | `well.py`, `dig.py` | count active listings, upload files, or a bulk-listing day as sales |
| — · no price from nothing | `listing.py` | price a pipe from fewer than five comparables |

## Commands

```
monster auto     pipes          # the whole daily loop — this is the scheduled job
monster new      pipes "<title>" [--price N --sku X]   # listing a pipe: price, title, copy
monster stock    pipes          # what is live, how fast things sell
monster answer   pipes D-004 yes
monster report   pipes
monster explain  pipes          # the rows behind a number, when one looks wrong
monster dig      pipes --propose --save
monster rebuild  pipes --reason "..."   # archives, never deletes, then rebuilds
monster verify   pipes          # hash chains and the wall
monster locate   ~              # find data files; reads headers only
```

Setup, once:

```
monster setup pipes --watch "<exports folder>" --repo "<this checkout>" \
                    --dossiers "<checkout>/channel/TO_FARID"
monster schedule pipes --at 08:00
```

## Tests

```
python -m unittest discover -s marketing_monster/tests -t marketing_monster
```

84 tests. Most were written from real failures on Farid's own data — a guard
that refused his whole catalogue because a pipe was called "4 Star Dr Grabow",
an export whose dates read `Oct-21-25`, 72 listings counted as sales. Each one
is a law now, with the story in its docstring.

## Still open

- **The other two kitchens** — GroundTruth and Ashcombe. One design, cloned,
  each walled. Gated on one CONFIRMED lesson in pipes, which needs weeks of
  real trading, not building.
- **The cookbook is empty** — nothing has been confirmed twice yet. That is
  the rule working, not a gap.
