# Reference Library Digitization Plan (for the RAG upgrade)

**Goal:** turn Farid's reference material — the mirrored Pipedia/Pipephil
content, paper catalogues, and books — into a searchable digital library the
Pipe Passport engine can consult during identification (Retrieval-Augmented
Generation), and that later powers the paid Encyclopedia.

**Why it matters:** today the engine identifies from general knowledge.
With the library attached, it will cite *your* catalogues and *your* dating
tables — answers get more precise, and the Encyclopedia gains content nobody
else can offer. This is also the moat: the data is the asset.

---

## What Farid has to do (the physical part)

This is the only part that needs your hands. Everything after it is mine.

### Step 1 — Inventory (1–2 hours)
Make a simple list of what exists. For each item: title, type (catalogue /
book / website mirror / price records), approximate year, and how it's stored
(paper, PDF, saved web pages, spreadsheet). Send me the list — I'll set the
priority order. **Priority rule: dating tables and shape charts first** —
they give the engine the most precision per page.

### Step 2 — Get the website mirrors to me as files
The Pipedia/Pipephil mirror is already digital. Zip the saved folders and put
them in the project repo (or a shared drive). No cleanup needed — I handle
parsing HTML.

### Step 3 — Scan the paper material
- Phone scanning is fine: use a scanning app (e.g. the iPhone Notes scanner
  or Adobe Scan) — flat pages, good light, one catalogue per PDF.
- 300 DPI or a sharp phone photo per page is enough; **don't retype anything**
  — OCR is my job.
- Name files simply: `dunhill-catalogue-1965.pdf`, `gbd-shape-chart-1970s.pdf`.
- Books under copyright: scan only for internal engine use, never republish
  pages in the Encyclopedia (summaries in your own words are fine).

### Step 4 — Export the sales history
Your 5,000+ sales records (Etsy/eBay exports, spreadsheets) as CSV. Brand,
model, year sold, price, condition note — whatever columns exist. This later
powers "comparable sales" in premium passports.

**Cadence suggestion:** one batch per week — even 20 pages a week compounds.
Start with the Dunhill and Peterson material since those are the most
submitted brands.

---

## What I do with it (the technical part)

1. **Ingest & OCR** — parse the HTML mirrors; OCR the scanned PDFs; clean the
   text into structured Markdown, one file per brand/topic, stored in this
   repo under `content/reference/` (version-controlled, private).
2. **Structure the gold** — dating tables, shape-number charts, and stamp
   conventions get converted into structured data (not prose), because
   tables are what the engine reasons over best.
3. **Retrieval layer** — embed the library into a vector index; at passport
   time, the engine's first pass reads the stamps, then retrieves the
   matching brand pages and re-assesses with them in context.
4. **Feed the Encyclopedia** — the same structured files become new public
   (later: subscriber-only) Encyclopedia articles, reviewed by Farid before
   publishing.
5. **Measure** — re-run the beta test set (the ~100 calibration pipes) with
   RAG on vs off, and keep it only where it demonstrably improves accuracy.

## Sequence

| Phase | Content | Effect |
|---|---|---|
| A | Website mirrors (already digital) | Fast win — broad brand coverage |
| B | Dating tables + shape charts from catalogues | Precision on the big brands |
| C | Remaining catalogues + books | Long-tail brands |
| D | Sales history CSV | Comparable-sales in premium passports |

**Bottom line for Farid:** your only jobs are the inventory list, zipping the
mirrors, scanning batches, and exporting the sales sheet. Send batch one and
I'll build the pipeline around it.
