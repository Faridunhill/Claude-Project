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

## Not built yet (on purpose)

No app pages or CMS wiring — this is the structure/knowledge layer only, matching the
blueprint's "nothing here is built yet." Reading these cabinets into the app or into a
front-desk agent is a later, separate step.

## Next cabinets

Dunhill (patent + date-code math), Stanwell (shape-number chart first), then Charatan,
James Upshall, De Paja… and a shared **Regular Brands** default recipe for ordinary brands.
