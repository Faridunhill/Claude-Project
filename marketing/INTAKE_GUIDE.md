# INTAKE GUIDE — the 200-pipe protocol (P2.3)

The human side of intake. ~3 minutes per pipe. Nothing needs a keyboard
near the pipe. **When rushed: shoot more, type less** — a skipped photo
is unrecoverable after sale; a skipped field is a cheap batch job.

## Per pipe

1. **SKU tag** on or beside the item, visible in the first frame.
2. **Photos — 8 to 12 frames**, filenames start with a number and
   contain the role word:

   | Filename example | What it is |
   |---|---|
   | `01-hero.jpg` | the money shot |
   | `02-angle.jpg`, `03-angle.jpg` | other angles |
   | `04-stamping.jpg` | **macro of EVERY stamping — the critical frame** |
   | `05-flaw.jpg` | each flaw close-up |
   | `06-scale.jpg` | beside a ruler |
   | `07-weight.jpg` | on the scale, readout visible (weight = photo) |
   | `08-group.jpg` | only for lots |

   A file with no role word is fine — it becomes an "angle" and is
   marked machine-guessed.

3. **Voice note, ~30 seconds** (`note.m4a` in the same folder). Say, in
   any order, your own words:
   - condition ("cleaned and sanitized, rim darkening, light tooth marks")
   - provenance if any ("provenance: single-owner Bristol estate")
   - the hook — start it with the word **"special:"**
     ("special: unsmoked fifties French shop stock")
   - anything odd.

4. **Two numbers** — one row in `numbers.csv` at the intake root:
   `sku,cost_basis,floor_price,list_price` (list_price optional).

## Folder layout

```
intake/
  numbers.csv
  FH-TP-041/
    01-hero.jpg ... 08-weight.jpg
    note.m4a
```

## What happens next (no action needed)

- Nightly: Whisper on the PC writes `note.m4a.txt` next to each audio
  file; the pipeline structures it into the record (flaws and
  restoration matched against controlled vocabulary — exact phrases
  only, nothing fuzzy; the full transcript is always kept).
- The sweep is idempotent: re-running never duplicates or overwrites —
  existing SKUs are skipped, fixes go through the corrections ledger.
- The report lists each item's completeness score and any photo-checklist
  gaps. **Gaps never block** — an item with gaps still enters the system.

## Run it

```
python -m marketing.intake /path/to/intake --db marketing/genome.db
```

## DO NOT do at intake

Titles, descriptions, tags, era research, brand attribution, taxonomy,
channel decisions. Machines generate all of it later from photos +
stamping macros + transcripts — better later than manually now.
