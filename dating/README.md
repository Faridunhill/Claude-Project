# Dating Directory — cabinets

Knowledge base for the Smoking Pipes Dating Directory. Design lives in
[`docs/pipe-dating-directory-blueprint.md`](../docs/pipe-dating-directory-blueprint.md);
this folder holds the built **cabinets** (one brand each).

- `cabinets/peterson.yaml` — **Peterson** (first cabinet; the reference implementation)

## How a cabinet maps to the blueprint

Every cabinet file follows the blueprint's 3 levels:

```
CABINET (brand)                 → cabinet: / brand:
  └ DRAWER (evidence type)      → drawers:
      └ SMALL DRAWER (one fact) → small_drawers:
```

And carries the blueprint's fixed parts:

| Blueprint idea            | Where it lives in the file |
| ------------------------- | -------------------------- |
| Per-brand recipe          | `recipe:` (Peterson = hallmark-first) |
| Evidence ladder (trust)   | `evidence_ladder:` (nomenclature → hallmark → stem/patent → mouthpiece → shape) |
| The 10 dating questions    | `questions:` (Q1–Q5 date · Q6–Q9 confirm · Q10 reassures) |
| Q1's 9 small drawers      | `drawers.shank_nomenclature.small_drawers` (incl. `band_flag`) |
| Band-flag logic           | `drawers.shank_nomenclature.small_drawers.band_flag` |
| Two silent checks         | `silent_checks:` (clues agree? / provenance?) |
| "A blank beats a lie"     | `abstain:` |

## Rules kept in the data

- **Marks decide; shape only reassures** — `shape_finish` is `weight: support only`.
- **A shape number gives the shape, not always the model** — never overclaim the model.
- **Facts combine** — no single small drawer dates a pipe; the era comes from the
  combination (e.g. `Peterson · Dublin · England · shape 106 · no logo → an era`).
- **Abstain over guess** — anything unverified is marked `confidence: verify`, not asserted.

## Hallmark drawer — complete (primary-sourced)

The `hallmark` drawer is fully populated from the owner-supplied primary sources — Mark
Irwin's PPN Hallmark Chart (1890–2026) and the PPN "Hallmarks" article:

- A **five-way stamp gate** (K&P mark · nickel faux-marks · Irish sterling · Irish gold ·
  British/London sterling) — classify before dating, so nickel marks are never read as a hallmark.
- The **complete Irish date-letter table**, six cycles 1890→2026, each with its letterform +
  shield style and its omitted letters, plus the 1939–1968 gap and the 1-June→1-January change.
- **Nickel**, **Irish gold** (4 marks), and **British/London** (its own 1937–1962 table) systems.

Cross-checked against the article's worked examples (capital N = 1999, lowercase n = 1979).

## Not built yet (on purpose)

No app pages or CMS wiring — this is the structure/knowledge layer only, matching the
blueprint's "nothing here is built yet." Reading these cabinets into the app or into a
front-desk agent is a later, separate step.

## Next cabinets

Dunhill (patent + date-code math), Stanwell (shape-number chart first), then Charatan,
James Upshall, De Paja… and a shared **Regular Brands** default recipe for ordinary brands.
