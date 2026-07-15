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

## Cross-checked against a second source

The cabinet has been reconciled with **Leverette, "A Peterson Dating Guide; A Rule of Thumb"**
(Pipedia, 2006). It **confirmed** the hallmark structure and independently validated two
date-letter entries (SH Meerschaum 2006 = U/2005; Ebony & Ivory = V/2006). It also added the
COM-stamp formats and sub-eras (incl. the shorter Éire window), datable series, the forked-tail
vs script **P** lettering, the P-Lip 1898 floor, the 300-series rule, "A Peterson Product", the
military-ferrule shape clue, and non-briar material windows.

**Source precedence:** where PPN/Irwin and Leverette disagree, PPN wins (more authoritative +
recent); Leverette conflicts are flagged in place (e.g. the nickel marks — "wolf hound / round
tower" per PPN vs "prone fox / stone tower" per Leverette), never silently resolved. Leverette
material is tagged **medium** confidence ("rule of thumb").

## Shape reference — populated (primary-sourced)

A `shape_reference` appendix now maps **shape number → name → production span**, from Mark
Irwin's PPN "Guide to System Shapes, 1896–2019" (Parts 1 & 2):

- **300 System group** — complete: 301–317 with names and years (305/306 have two variants
  each; 310/311/315/316 are unassigned gaps). E.g. `308 Large Chubby Billiard = 1896–1959`.
- **House pipes / straights / peculiars** — the entries whose years were text-readable (31,
  XXL Bent Billiard, Freehand, Darwin/B42, Mark Twain System…); a few remain `verify` (years
  locked in page images).
- **Shape families** (GQ Tobaccos retail chart) — groups numbers into billiard/pot, Dublin/
  apple/prince/zulu, bent-non-system, Liverpool/lovat, bulldog/rhodesian, System. Grouping only,
  **no dates**.

**Dating rule:** a shape's span brackets the pipe — START = "not earlier than", END (if
discontinued) = "not later than" — then the COM stamp / hallmark pins the exact year inside it.
The `patent` drawer also now carries the real System patent dates (reservoir 1890, graduated
bore 1891, P-Lip 1894 & 1898).

## Not built yet (on purpose)

No app pages or CMS wiring — this is the structure/knowledge layer only, matching the
blueprint's "nothing here is built yet." Reading these cabinets into the app or into a
front-desk agent is a later, separate step.

## Next cabinets

Dunhill (patent + date-code math), Stanwell (shape-number chart first), then Charatan,
James Upshall, De Paja… and a shared **Regular Brands** default recipe for ordinary brands.
