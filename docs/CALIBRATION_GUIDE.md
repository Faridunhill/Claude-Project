# Cabinet Calibration Guide — testing the Pipe Passport on 200 pipes

The engine assesses **one pipe per analysis, always** — that's deliberate
(full attention per pipe = accuracy). "Bulk" means the runner feeds pipes
through automatically, 3 at a time in parallel. Two hundred pipes take
roughly 1–2 hours of machine time and about **$20–30** in API cost.

## Stage 1 — single pipes (start here)

Use the beta web page directly: `/encyclopedia/pipe-passport` (it's hidden
from menus until launch, but the URL works). Submit 5–10 pipes you know
perfectly and read the assessments critically. This catches obvious problems
before spending money on the full cabinet.

## Stage 2 — the bulk run

### Farid's part: organize the photos

One folder per pipe, named so you recognize it, with the six photos named by
view:

```
test-cabinet/
  001-dunhill-shell-1962/
    left.jpg  right.jpg  top.jpg  bottom.jpg  stampA.jpg  stampB.jpg
    info.json          ← optional but valuable
  002-peterson-system-premier/
    ...
```

- Photo names just need to **start with** the view word (`left-2.jpg` works).
- **JPEG, not HEIC** — on iPhone, share/export as JPEG, or set
  Settings → Camera → Formats → Most Compatible before shooting.
- `stampB` is optional; the other five are required (folders missing photos
  are skipped and listed, not failed).

`info.json` per pipe (optional, recommended) — the `truth` field is what
makes scoring possible:

```json
{
  "stampText": "DUNHILL SHELL BRIAR MADE IN ENGLAND 12",
  "length": "5.5 in",
  "notes": "replacement stem suspected",
  "truth": "Dunhill Shell Briar 120, 1962"
}
```

Leave `brandGuess` out for a fair blind test — give the engine only what a
stranger would provide, and keep what YOU know in `truth`.

### Running it

From the project folder on a computer (or hand the cabinet folder to me and
I run it):

```bash
ANTHROPIC_API_KEY=sk-ant-... npm run bulk-test
```

- Progress prints per pipe; results save after **every** pipe, so an
  interrupted run resumes where it stopped — just run the command again.
- Output: `test-cabinet/results/results.csv` (open in Excel/Numbers) and
  `results.json`. The CSV has one row per pipe: your truth next to the
  engine's brand, era, confidence, stamping transcription, and reasoning.

## Stage 3 — scoring

For each row mark: brand right? era right (within the stated range)?
stamping transcribed correctly? Then we look at the failures **by pattern**
(a brand it always misses, faint stamps, a wrong dating convention) — those
patterns become prompt fixes or digitization priorities, and we re-run only
the failed folders. When accuracy satisfies you across the cabinet, flip
`NEXT_PUBLIC_PASSPORT_LIVE=true` and launch.

The negotiated number: 100 was the plan, the cabinet is 200 — more is
strictly better, since the same folders become the permanent regression set
we re-run after every future engine change.
