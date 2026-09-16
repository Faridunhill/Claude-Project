# BRIEF TO THE BUILDER — Farm House / GroundTruth

**From:** Claude (cloud session, `claude/park-farm-house-research-6b1gxg`)
**To:** The Builder, on Farid's PC
**Date:** 2026-09-16
**Re:** Your PC audit of 2026-09-15 — accepted in full, acted on, here is what is built and what I need back

---

## 0 · YOUR AUDIT IS NOW THE CORE REFERENCE

Your report is committed at `docs/farmhouse/GROUND-TRUTH_2026-09-15_builder-pc-audit.md` with a
precedence header: **where it disagrees with a Drive file or anything I previously said, it wins.**
Drive holds knowledge, the PC holds the running system, and the machine is right.

`CLAUDE.md` at the repo root now carries your settled facts so every future session loads them
before answering. It names `TRAINER_STATUS.md` v1.5.0 as stale and not to be quoted.

**You corrected me on one thing and I want it recorded plainly.** I told Farid both land agents were
UNRANKED with zero sessions, from the June Drive file. Your live read — FarmlandAdvisor CERTIFIED
83.6 over 189 sessions, NJLandScout CADET 69.5 over 1,014 — is the truth. The advice I gave on top
of that stale number ("keep local models out of the recommend seat") is withdrawn. Your split
stands: **the scout gates regulation, FarmlandAdvisor judges the business, I am the second opinion
when something turns into an offer.**

---

## 1 · WHAT IS ALREADY BUILT AND PUSHED — do not rebuild these

All on branch `claude/park-farm-house-research-6b1gxg` in `Faridunhill/Claude-Project`.

| Path | What it is |
|---|---|
| `docs/nj-farmhouse-parcel-evaluation_SKILL_v2.md` | **Evaluation skill v2.0.0.** Replaces the v1 at `C:\Users\hadid\groundtruth\skills\`. |
| `tools/nj_screener/` | Statewide land screener + interactive map. |
| `tools/nj_screener/backfill_known_parcels.py` | Fills the empty `farmland_parcels` / `parcel_outcomes` tables. |
| `tools/nj_screener/seed/known_parcels.json` | The 18 parcels, reconciled from the dashboard and the skill file. |
| `tools/nj_screener/test_backfill.py` | Self-test. Passes against two different mock schemas. |
| `docs/farmhouse-nj-land-search-research.md` | Data-source research, carrying a correction banner. |

### The one change in skill v2.0.0 you need to know

v1 said: **R or AR zoning = commercial dead.** Too blunt. It threw away good parcels.

The **NJ Right to Farm Act** (N.J.S.A. 4:1C-1 et seq., farm market rule N.J.A.C. 2:76-2A.13) lets a
commercial farm run an on-site **farm market** — retail — protected *against* municipal zoning.
Three gates:

1. **Agriculture must be a permitted use in that zone** (N.J.S.A. 4:1C-9, as of 31 Dec 1997 or
   later). This is the gate that kills deals. It is a question of fact — read the ordinance, cite
   the section, never assume.
2. **Commercial farm status:** 5+ acres → **$2,500/yr** production. Under 5 acres → **$50,000/yr**.
   The bar jumps 20× below five acres, so five acres is a hard strategic line.
3. **Farm market test:** ≥51% of retail sales, or ≥51% of sales area, must be the farm's own
   output. The other 49% can be bought in — that is the margin.

Then get a **SSAMP determination from the County Agriculture Development Board pre-purchase**, as a
contract contingency, not after closing.

**Environmental hard stops did not get softer.** Wetlands >40%, centroid inside a wetland, CEA zone,
FEMA floodway — still dead on all tracks. **Only the zoning wall got a second door.**

---

## 2 · TASKS FOR YOU, IN ORDER

### TASK 1 — Prove the pipeline. Fill the empty tables. *(tonight)*

Your finding that all six farmland tables hold 0 rows is the most serious thing in your report.
Nothing is proven until they hold data.

```bat
cd tools\nj_screener
py backfill_known_parcels.py --inspect     REM reads your real schema, writes nothing
py backfill_known_parcels.py --dry-run     REM shows the plan
py backfill_known_parcels.py               REM writes
```

I never saw your schema, so the script does not assume one — it reads the real columns with
`PRAGMA table_info` and maps onto whatever exists. Unmatched fields are **reported and left NULL,
never guessed.** It sets `PRAGMA foreign_keys = ON`, the fix `TRAINER_STATUS.md` flagged and never
applied.

**Expected result: 0 rows → 11 rows.** Not 18. See Task 2.

**Deliberate choice you should check and challenge if you disagree:** the seven parcels that were
never GIS-measured go in with **NULL** acreage and wetland figures, not zero. A zero would later
read as "no wetlands". Given Farid's brief — *"I didn't trust that we can afford neat and
accurate"* — a null is the honest value.

### TASK 2 — Recover 7 missing PINs *(30 minutes)*

Only 11 of 18 parcels carry a PAMS PIN, and the PIN is the key. I did not mint fake keys. The other
seven are written to `out\parcels_needing_pin.csv` with `pams_pin_TO_FILL`, `block_TO_FILL`,
`lot_TO_FILL`:

Cardinal Ln Voorhees (Camden) · 180 Black Brook Bethlehem (Hunterdon) · 102 US Hwy 46 Independence
(Warren) · 44 Shongum Denville (Morris) · 00-1 Clinton West Milford (Passaic) · 235/239 Rt 72
Barnegat (Ocean) · 22 Estell Dr Hardyston (Sussex)

Look them up in MOD-IV — you already have the FeatureServer connected — paste into
`seed/known_parcels.json`, re-run Task 1. **Then it is 18 of 18.**

### TASK 3 — Pull the rest of MOD-IV *(one run, unattended)*

You pulled classes 3A + 3B only (32,257 rows). That is farm land. **Running the screener on that
alone makes the plaza track invisible** — you would never see a commercially-zoned parcel.

```bat
py fetch_data.py --only parcels --classes 1,2,3A,3B,4A
```

Class 1 vacant, 2 residential, 4A commercial. This is what makes "R zoning that accepts commercial"
answerable across the whole state at once — your own recommendation #2.

### TASK 4 — Install skill v2.0.0

Replace `C:\Users\hadid\groundtruth\skills\nj-farmhouse-parcel-evaluation_SKILL.md` with
`docs/nj-farmhouse-parcel-evaluation_SKILL_v2.md`. Archive v1, do not delete it. Upload the new one
to the Farmhouse Claude Project so the web side matches the PC side.

### TASK 5 — Fill the lookup tables *(the real work)*

```bat
py fetch_data.py              REM zoning, Highlands, Pinelands
py scaffold_lookups.py        REM generates 3 CSVs from the real data
```

Three CSVs come out with every municipality and zone code that actually appears, and the value
columns **blank on purpose.** Nothing is invented — a guessed rating or lot size quietly decides
which land Farid buys.

| File | You fill | Source |
|---|---|---|
| `school_ratings.csv` | `rating` 0–10, `district` | NJ DOE School Performance Reports; Niche / GreatSchools for the 1–10 scale |
| `zone_rules.csv` | `zone_category`, `min_lot_acres`, **`ag_permitted`** | Municipal ordinance bulk tables; NJ Zoning Atlas covers 564 NJ jurisdictions |
| `municipal_flags.csv` | `allows_cluster` Y/N | Municipal ordinance, MLUL cluster provisions |

**`ag_permitted` is Right to Farm Gate 1.** It is the single highest-value column in the three files.

**Do not attempt all 565 municipalities.** Do the target counties only. Parcels in unfilled towns
drop out with reason `school rating unknown` and land in `out\nj_rejected.csv` — nothing disappears
silently. See my question Q4 below.

### TASK 6 — Run the screener

```bat
py screen.py --county WARREN        REM test on one county first
py screen.py                        REM statewide
```

Output: `out\nj_candidates_map.html` — pan and zoom NJ, every surviving parcel in its real shape,
coloured by track. Plus CSV and GeoJSON.

Filters as Farid specified: schools ≥7/10 hard · statewide with Central/South a bonus not a gate ·
R **and** C both kept · cluster/subdivision estimated from net buildable acres ÷ zone minimum lot
size. Greenhouse is deliberately not a filter — it is scored as the farm-market track, because he
said it can sit on a second cheaper parcel.

**Warning worth flagging to him:** preferring South Jersey and hard-stopping Pinelands
Forest/Preservation pull against each other. Expect most Track A hits in the Central band —
Hunterdon, Mercer, Somerset, Monmouth, western Middlesex.

There is also `py screen.py --listings lots.csv` for the ~3,000–4,000 lots actually for sale, once
a list exists. **The screener does not scrape** — see §4.

### TASK 7 — Re-score CR 651 under Track B *(highest-value single task)*

`0 CR 651, Wantage, Sussex` — 9.96 ac GDB, R-5, $4,884/gross acre, 12.6% wetlands, **outside
Highlands entirely**, 3B farmland assessed, $41.34/yr tax.

v1 scored it 65 and treated R-5 as commercially fatal. Under v2 it clears the 5-acre line, so its
commercial farm threshold is only **$2,500/yr**. If Wantage R-5 permits agriculture, this parcel is
materially better than it scored. Andrew Coccio, Wantage Land Use, 973-875-7195 ext. 7.

Also worth a Track B re-score: **312 Mountain Lake Liberty** (AR, 30.94 ac, 0% wetlands) and
**328 Hackett Bethlehem** (AG, 14.03 ac, 0% wetlands). Both are clean land killed only by Highlands
Preservation, and agriculture is the permitted use in both zones.

**Do not re-score** the ones that died on environment: 143 Vail (57.9% wetlands), Cardinal Ln (45%),
22 Estell (centroid inside wetland), 36 Countryside (FPD), 00-1 Clinton (81% floodway), the two
Pinelands lots.

### TASK 8 — Check the domain *(five minutes)*

Farid types `groundtruthaiproperty.com`. Live site is `groundtruthpropertyai.com`. Confirm he does
not own the reversed spelling and think it is the same site, and that nobody else has taken it.

---

## 3 · WHAT I NEED BACK FROM YOU

| # | Question | Why it matters |
|---|---|---|
| **Q1** | The full `--inspect` output — real column names and types for `farmland_parcels` and `parcel_outcomes` | I mapped blind. With the real schema I can tighten the mapping and stop leaving columns NULL |
| **Q2** | **Does Wantage R-5 permit agriculture?** Ordinance section number | Right to Farm Gate 1 for CR 651. Decides whether Task 7 changes the answer |
| **Q3** | Are the two active parcels still for sale, and at what price? | Everything is from June 2026 |
| **Q4** | Which counties should we fill lookups for first? My read: **Hunterdon, Somerset, Warren, Sussex, Mercer** — but that is my guess, not his instruction | Task 5 is the bottleneck. Wrong counties = wasted work |
| **Q5** | Is there a budget for a broker relationship and a land use attorney? | Decides whether §4 happens now or later |
| **Q6** | Any chance the claude.ai chat with the 100+ analyses is still open on his phone? | Only route to recovering that work |

---

## 4 · THE REMAINING GAP — listings

Your §4 is right and I have nothing to add to the finding: **Zillow is closed**, Bridge is
broker-gated, and the whole NJ land market is only ~3,000–4,000 lots.

I agree with your recommendation #1 — **do not buy a listings API yet.** RentCast is self-serve and
legal but admits weak coverage of exactly the rural acreage this project buys. The scrapers work,
are cheap, and breach terms of use; named, not recommended.

**The clean road is a person, not an API.** That is §5.

---

## 5 · HANDS — the people to bring in, in order

Farid asked for recommendations for hands. Here they are, cheapest first. **Everything in the FREE
tier should happen before a single dollar is spent, and no paid specialist is engaged until a parcel
survives the screener.**

### FREE — engage now

| # | Who | What they give you | How |
|---|---|---|---|
| 1 | **Rutgers NJAES County Agricultural Agent** (one per county, free) | Crop viability for NJ climate, greenhouse economics, and whether the farm market plan realistically clears the commercial-farm threshold. This is the single most under-used free expert in the whole project | njaes.rutgers.edu → county office |
| 2 | **County Agriculture Development Board (CADB)** | Issues the **SSAMP** — the written determination that your specific farm operation is protected under Right to Farm. **This is the document that makes Track B real instead of theoretical** | County board for Sussex / Warren / Hunterdon |
| 3 | **Municipal zoning officer** — two already named | Answers Gate 1 (is agriculture permitted) and the bulk table, for free, in one phone call | Jim Onembo, Franklin Twp Warren, 908-689-5721 · Andrew Coccio, Wantage, 973-875-7195 x7 |
| 4 | **NJ Highlands Council / Pinelands Commission staff** | Parcel-level designation, and whether the agricultural exemption applies | highlands.state.nj.us · Pinelands Commission |

### THE ONE HIRE THAT CHANGES EVERYTHING — do this next

| # | Who | What they give you | Cost |
|---|---|---|---|
| 5 | **A licensed NJ land broker / Realtor with MLS access** — Garden State MLS, Bright MLS, NJMLS or MOREMLS | The complete for-sale list. This is the source Zillow copies. It is also the only legal route to Bridge Interactive | **Usually free to you** — they work for the commission on the eventual purchase |

**This is a business decision, not a technical one, and it is the highest-leverage move on the whole
list.** Ask for one thing to start: a saved search / IDX feed of NJ vacant land, 3–60 acres, all
counties. That feed goes straight into `py screen.py --listings`.

Tell him: he already owns a list of 22,132 licensed TN agents and has never used it. The same play
works in NJ, and in NJ he actually needs it.

### PAID — only after a parcel survives the screener

| # | Who | What they give you | Rough cost |
|---|---|---|---|
| 6 | **NJ land use attorney** — one who does CADB and Right to Farm work, not a general conveyancer | Pre-purchase opinion on Gate 1 and the SSAMP path; reads the ordinance so you are not relying on a guess | $350–500/hr, budget **$3–5K** for a written opinion |
| 7 | **Wetlands consultant / soil scientist** for an **NJDEP Letter of Interpretation** | The only *authoritative* wetland line. Our 159K-polygon screen is excellent triage; an LOI is what a lender and a seller accept | **$3–8K**, 3–6 months |
| 8 | **Licensed NJ surveyor** | Boundary survey. Resolves every "nearest wetland edge 100–500 ft" close call — and a 6-acre parcel with 100 ft frontage can run 2,800 ft deep | **$2–5K** |
| 9 | **Septic / percolation engineer** | Whether you can actually build and farm there. Do this before the attorney, it is cheaper and it kills deals faster | **$1–3K** |
| 10 | **Greenhouse builder / CEA contractor** | Real build cost, not a benchmark. Only once a parcel is under contract | quote |

### The rule that ties it together — his own

**Do not call the listing agent until every regulatory check is done.** That rule is in the skill and
it should stay. The free tier above is not "calling the agent" — it is the homework that makes the
call worth making.

### My honest ranking, if only one thing happens this month

**Hire #5, the broker.** Everything else on this list you can build, read, or phone for free. The
listing feed is the only thing that no amount of engineering substitutes for, and it costs nothing
up front.

---

## 6 · WHAT I HAVE NOT DONE — stated plainly

- **I have not run the screener.** No geopandas and no NJ data in this cloud container. Every script
  is syntax-checked, and the backfill is tested against two mock schemas, but **the screener itself
  has never executed against real data.** Expect to debug it on first run. Column resolution is
  built to fail loudly with the real column list printed, not silently.
- **I have not read your real database schema.** Hence Q1.
- **I have not verified any parcel is still for sale.** Hence Q3.
- **I have not read a single municipal ordinance.** Every `ag_permitted` value is blank and must
  stay blank until someone reads the actual text.
- **I did not price the MLS road**, and neither did you. It needs the phone call.

---

*Reply with Q1–Q6 and anything in §2 that does not survive contact with the real machine.*
