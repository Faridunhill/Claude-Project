# MARKETING MONSTER — wave 1

The loop, as code. `Well → Digger → Judge → Maker → Mouth → Scale → Well`

Spec: `channel/TO_FARID/003` (evaluation) and `004` (v1.2 build spec).
Built 2026-07-31 while the hub/cabinet location was still unknown — **nothing
here needed Farid's data**, which is why it could be built first.

## What this is

Pure-stdlib Python 3.10+. No pip install, no framework, no network. The same
property the dating engine has: it runs on Farid's PC as-is, and it would port
anywhere. About 900 lines, of which the interesting part is the refusals.

**The machine writes every row. Farid answers with a word.** Nothing in this
package offers a way to hand-edit a ledger, by design (doc 004 §2.1).

## What it enforces (the point of the whole thing)

| Law | Where | It refuses to… |
|---|---|---|
| B1 · no invented attribution | `scale.py` | record a cause without a written reason; the default is `unattributable` |
| B2 · no superstition | `playbook.py` | confirm a lesson on one cohort, or accept a line with no evidence, effect, or expiry |
| B3 · the wall | `wall.py` | let data cross into the shared cookbook wearing a method's coat |
| M2 · reject memory | `judge.py` | re-open a dead category unless you state what changed |
| M3 · scaffolding expires | `digger.py` | store a source without a named permission basis |
| M4 · no personal data | `well.py` | write a name, an email, or an address into the Well — ever |
| N1 · rollback key | `maker.py` | publish an asset without the playbook version that produced it |
| §2.3 · no lying by omission | `report.py` | print performance without first printing its own blind spots |

Every refusal names the finding it comes from, so an error message teaches the
law rather than just blocking.

## Run the tests

```
python -m unittest discover -s marketing_monster/tests -t marketing_monster
```

26 tests, T1–T11 from doc 004 §6. They are the laws written as code that
fails — a future refactor that quietly drops a law breaks a test with the
law's name on it.

## When Farid is back at his PC

```bash
cd <wherever the marketing root should live>          # e.g. FARIDOS/marketing
export PYTHONPATH=/path/to/marketing_monster

python -m monster init pipes                          # builds the tree, mints the salt
python -m monster inspect pipes ~/…/ebay_sold.csv     # READS HEADERS ONLY, writes nothing
python -m monster load    pipes ~/…/ebay_sold.csv     # derived features only
python -m monster report  pipes
python -m monster verify  pipes                       # hash chains + the wall
```

`inspect` is the safe first move: it opens the file, reads the header row,
proposes a column mapping, prints what it would drop on the floor, and exits
without reading a single record. Run it, look at the mapping, then `load`.

If the export's columns are unusual, save the corrected mapping as JSON and
pass `--mapping mapping.json`. No format work is needed in advance — CSV out
of eBay, a spreadsheet export, anything with a header row.

## What is still blocked

**Wave 2 only: the location of the hub and cabinet data.** That is a fact
about Farid's PC, not a decision — the cloud side cannot look. Once a path
exists, `inspect` → `load` is a two-minute job and the pipes dig starts.

## Layout it builds

```
<marketing root>/
├── cookbook/            COOKBOOK.md · ADMISSION_LOG.jsonl     ← shared, methods only
└── clones/pipes/
    ├── well/raw/ derived/ .salt      ← never leaves the machine, never enters git
    ├── digger/  sources.jsonl  digs/
    ├── judge/   decisions.jsonl
    ├── playbook/PLAYBOOK.md
    ├── maker/out/                    ← every asset stamped with a playbook version
    ├── scale/   events.jsonl  reports/
    └── PENDING.md                    ← generated; answering it is Farid's 15 min/week
```

One root is one wall. Run the process with one clone's root and nothing else.

## Deliberately not built yet

The Mouth (publishing to owned/borrowed ground) and the Digger's actual
research runs. Both need decisions or credentials that are Farid's, and
wave 1's job was the two missing ends — the Well and the Scale.
