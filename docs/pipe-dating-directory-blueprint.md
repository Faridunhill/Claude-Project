# Smoking Pipes Dating Directory — Blueprint

> Working record of the design brainstorm. Nothing here is built yet — this is the
> agreed plan we return to and keep editing. The build starts one brand (cabinet)
> at a time, Peterson first.

## Purpose

Identify and date pipes with confidence. **Hard marks decide.** The AI's eye and the
seller's own photos are *supporting* evidence — never the lead.

## Evidence ladder (order of trust)

1. **Nomenclature** (shank stamps) — the gold
2. **Band hallmark**
3. **Stem logo / patent number**
4. **Stem & mouthpiece clues**
5. **Shape / finish** — support only, never decides

## The 10 dating questions

- **Q1–Q5 date the pipe** (the marks)
- **Q6–Q9 confirm the era** (stem & mouthpiece)
- **Q10 reassures** (shape/finish matches the marks)

1. What is stamped on the shank? (brand, model, words)
2. Is there a country stamp? ("Made in ___")
3. Is there a shape number?
4. Is there a patent / patent-pending number?
5. Is there a silver band / hallmark? What are the little marks?
6. What is the stem logo — its shape and material?
7. Saddle or tapered stem? Any drop to the shank?
8. Vulcanite or acrylic mouthpiece? P-lip or fishtail?
9. Tenon type? (9mm filter? bone / metal / aluminium tenon?)
10. Does the finish & shape match the marks?

**Two silent checks, always run:**
- Do the clues agree? (disagreement = replaced stem / married parts / fake)
- Provenance? (box, sock, sleeve, invoice)

## Q1 = 9 small drawers (classified, never a pool)

`brand · city · made-in · model · shape number · briar logo · special statement · patent no. · band-flag`

**Band-flag logic:** if the model has no factory band but this one does → the band was
*added* → almost always a **repair (a rescue)**, possibly hiding the shape number.
Collectors never change the original shape; they only add a band to save a gem.

## Structure = cabinets, not a pool

- **Q1 (brand) picks the cabinet — and closes all the others.**
- Every question after = **one reach into one drawer.** Same tiny effort whether the
  directory holds 1 brand or 200. The "front-desk agent" never searches the pile.

## Nesting = 3 levels

```
CABINET (brand)
   └ DRAWER (evidence type: shank nomenclature · hallmark · stem · mouthpiece)
        └ SMALL DRAWERS (single facts)
             brand · city · made-in · model · shape no. · briar logo · patent · ...
```

- Shank-nomenclature drawer = the most important drawer.
- Each small drawer = one fact.
- The facts **combine** to point at the date
  (e.g. Peterson + "Dublin / England" line + shape 106 + no briar logo → an era).

Example read: `Peterson · Dublin · England (underneath) · shape 106 · no logo`.

## Recipes (per-brand dating playbooks)

The moment the brand is known, the agent loads **that brand's recipe** — the order and
rules for dating it. No two brands are dated the same way.

- **Premium makers — each gets its OWN recipe** (any pipe ~£100–120 and up):
  - **Peterson** — hallmark-first (silver hallmark can give the exact year)
  - **Dunhill** — patent number + date-code math
  - **Stanwell** — shape-number chart first (e.g. `06 = sitter large brandy, vulcanite
    saddle stem, by Eltang`; and backwards, that description → Stanwell 6)
  - **Charatan · James Upshall · De Paja · …** — built one by one
- **Regular Brands package** — one shared default recipe for ordinary brands.
- **Rule:** a shape number gives the *shape*, not always the *model*
  (06 could be Royal Prince *or* Danish Design) — never overclaim the model.

## Trust rule

The system may answer **"cannot date with confidence."** No guessing.
**A blank beats a lie.** Abstaining when the evidence is thin is what makes it trusted.

## The fingerprint (marks = the pipe's "face")

A face is recognised by turning landmarks into numbers (eye spacing, nose length) and
comparing. A pipe has **two** fingerprints:

1. **Marks fingerprint (the true identity)** — stamps, hallmark, stem logo, patent.
   We **READ** these (OCR), we don't measure them. A face has no writing, so machines
   must measure geometry — a pipe *does* have writing, so reading beats measuring.
2. **Shape fingerprint (support only)** — where there's no writing: bowl height ÷ width,
   shank length, bend angle, stem taper. Turned into numbers and compared to known shapes.

**Rule: read where there's text (marks); fingerprint where there isn't (shape).**

## Backed by research (2025–2026 state of the art)

- Build a **reference library and compare** — do NOT train a classifier on your own
  photos (confirmed even by luxury-bag authentication, Entrupy).
- **Embedding + nearest-neighbour** (the face-recognition mechanism) generalises to
  items never seen before — fingerprint + compare.
- **Fine-grained recognition:** attend to *parts*, suppress the background — look at the
  stamp / stem / logo, not the whole cluttered photo.
- **Read marks in two stages:** detect → rotate flat → recognise (engraved-mark pipeline).
- **Explainable evidence trail** (visual-RAG): observe → record evidence → reason →
  answer. This is exactly our ladder.
- **Abstain rather than over-claim** (Entrupy returns "Unidentified", not a false verdict).

## Open questions to resolve during structure design

- Real OCR accuracy on worn, shallow, low-contrast stamps and small hallmarks on curved
  metal — and whether any off-the-shelf reader is usable without a custom pipe-mark dataset.
- How to formally enforce the hierarchy (a legible hallmark/shape number overrides a
  high-similarity shape match) and how the system decides to abstain.
- Minimum viable reference archive: how many known-dated, mark-verified reference pipes
  per maker/shape are needed to be reliable, and how the references are provenance-verified.
- Whether hallmark date-letter and patent/shape-number systems have enough structured,
  machine-readable reference data to convert a read mark directly into a date range.
