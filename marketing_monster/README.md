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

33 tests, T1–T13 — the ten from doc 004 §6 plus the dig and locate guards. They are the laws written as code that
fails — a future refactor that quietly drops a law breaks a test with the
law's name on it.

## Start here, on the PC

```bash
python -m monster locate ~            # or: locate "C:/Users/<you>/Desktop"
```

Walks the folder, ranks every file that could be a Well, and prints the header
row of each candidate. **It reads names, sizes and one header line — never a
record — and writes nothing.** That output answers the hub/cabinet question in
one command instead of a conversation.

Then:

```bash
cd <wherever the marketing root should live>          # e.g. FARIDOS/marketing
export PYTHONPATH=/path/to/marketing_monster

python -m monster init pipes                          # builds the tree, mints the salt
python -m monster inspect pipes ~/…/ebay_sold.csv     # READS HEADERS ONLY, writes nothing
python -m monster load    pipes ~/…/ebay_sold.csv     # derived features only
python -m monster dig     pipes --save                # the pipes dig, written up
python -m monster report  pipes
python -m monster verify  pipes                       # hash chains + the wall
```

`inspect` is the safe first move: it opens the file, reads the header row,
proposes a column mapping, prints what it would drop on the floor, and exits
without reading a single record. Run it, look at the mapping, then `load`.

If the export's columns are unusual, save the corrected mapping as JSON and
pass `--mapping mapping.json`. No format work is needed in advance — CSV out
of eBay, a spreadsheet export, anything with a header row.

## The dig (wave 3, built)

`monster dig pipes` answers the four questions from the DIG ORDER: what sold
fastest, at what price, which title words, who bought twice. Three things make
it a dig rather than a spreadsheet:

- **Every figure carries its n**, and below 12 it is labelled an observation,
  not evidence. The dig will say "this Well is not big enough to read title
  effects" rather than produce a pattern.
- **Title words are compared within brand.** The naive version of this
  analysis just re-discovers the brands — a Castello outsells a Stanwell
  however it is described — and produces unusable "lessons" like *use the word
  Castello*. A word must also show its effect in two or more brands.
- **It proposes PROPOSED lines only.** One dataset is one cohort; nothing can
  reach CONFIRMED from a single look (B2).

It also states what it cannot see: unsold inventory is invisible in a
sold-item export, so "what sells" means "what sold" and the denominator is
missing. That limitation is printed in the report, not left for someone to
discover later.

## What is still blocked

**Wave 2 only: the location of the hub and cabinet data.** That is a fact
about Farid's PC, not a decision — the cloud side cannot look. `locate`
answers it in one command; then `inspect` → `load` → `dig` is a five-minute
sequence.

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
