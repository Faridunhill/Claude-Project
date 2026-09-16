# Farmhouse / GroundTruth — NJ Land Search Capability Research

**Date:** 2026-09-16 (revised same day after the Builder's PC audit)

> **CORRECTION — 2026-09-16.** The agent-certification figures in §3.4 of the first version of this
> memo were wrong. They came from `TRAINER_STATUS.md` v1.5.0 in Drive, dated **2026-06-26** — three
> months stale. The Builder read the live `farid_os.db` on the PC at 2026-09-15T21:27 and the real
> scores are far higher. §3.4 has been rewritten. The recommendation that followed from the stale
> numbers ("don't put local models in the recommend seat") is withdrawn — see §3.4.

**Branch:** claude/park-farm-house-research-6b1gxg
**Question asked:** Who — which tool, which data source, which agent, which person — is actually
best able to search *every current NJ land lot*, analyse it, and recommend? Filters that matter:
good schools / charter schools, zoning that will accept commercial (plaza), and a greenhouse
business.

---

## 0. What could and could not be collected

**Could not:** the PC at `C:\Users\hadid\` is not reachable from this session. This runs in an
isolated cloud container with access to the three GitHub repos and Google Drive only. Nothing was
read off the local machine.

**Could:** the entire farmhouse analytic corpus is already in Google Drive and was recovered from
there. Nothing important appears to be stranded on the PC — the PC holds the *runtime* (Python
connectors, Ollama models, `farid_os.db`), Drive holds the *knowledge*.

---

## 1. Corpus recovered from Drive

| File | What it is | Why it matters |
|---|---|---|
| `nj-farmhouse-parcel-evaluation_SKILL_updated.md` | The full 7-step parcel due-diligence skill | This is the crown jewel. Hard-stop rules, 100-point scoring model, output format, contacts, disposition list |
| `parcel_comparison_dashboard.html` | GIS-verified comparison of 11 parcels, 6 counties | The real analysis record — wetland % computed by polygon intersection, not estimated |
| `nj_land_scout.json` | NJLandScout agent curriculum, 17 topics / 30 questions | The search/screen agent |
| `farmhouse_advisor.json` | FarmhouseAdvisor curriculum (retired, merged) | Superseded by `farmland_advisor.json` v1.1.0 (24 topics / 38 questions) |
| `TRAINER_STATUS.md` v1.5.0 | Agent certification board | Tells us exactly how trained each agent is — answer: barely |
| `FARMHOUSE_STATUS.md` | Project status, LAW 06 dependency | Farmhouse consumes GroundTruth GIS, never rebuilds it |
| `NJ_Land_Intelligence_v1/v2/v3.html`, `nj_land_intelligence_point1.html` | Earlier intelligence builds | Iterations of the same idea |
| `parcels_shp_dbf_Morris.zip` | Morris County parcels + MOD-IV | One county of the statewide set |
| `SKILL-GROUNDTRUTH-001_report_pipeline.md`, `-002_local_intelligence_model.md` | GroundTruth report pipeline | The product these parcels feed |

### Correction on "more than 100"

There is no 100-farm analysis. The 120-item list in memory is `LOT_LIST_20260825.md` — that is the
**PIPE** project (tobacco pipe auction lots, 120 links checked down to 67 keepers). Different
project, same word "lot".

The real farmhouse record is **11 parcels fully GIS-verified** plus **18 addresses carrying a
disposition** in the skill file. That is the honest count. It is good work — it is just not 100.

**Independently confirmed on the PC, 2026-09-15.** The Builder searched Downloads, Documents,
OneDrive, Desktop, FaridOS and the groundtruth folder by filename and by content. The 100+ analyses
are not there. Worse, `farid_os.db` has the tables built for them — `farmland_parcels`,
`parcel_outcomes`, `greenhouse_projects`, `business_plans`, `permit_log`, `crop_market_data` — and
**every one has 0 rows.** So the analyses were done inside a claude.ai web chat and never came home.
If that chat is still open on the phone, exporting it is the only way to recover it.

---

## 2. The parcel record as it stands

**Active (2):**

| Parcel | County | Zoning | Gross ac | Wetlands | Net buildable | $/gross ac | Score |
|---|---|---|---|---|---|---|---|
| 0 Half Way House Rd, Franklin Twp | Warren | **C-1** | 6.67 | **0.0%** | 6.67 | $15,576 | 72 |
| 0 CR 651, Wantage Twp | Sussex | R-5 | 9.96 | 12.6% | 8.71 | **$4,884** | 65 |

Half Way House is the only parcel found so far where retail is permitted **by right**. CR 651 is the
cheapest buildable land in the set but needs a use variance for anything commercial.

**Lifestyle-only (1):** 500 Route 94, Fredon — R-1, 7.4% wetlands, FSA farm loan path noted.

**Disqualified (8 in the dashboard, ~16 named in the skill file).** The pattern is brutal and worth
internalising:

- **Highlands Preservation** killed 6 parcels — 312 Mountain Lake, 28 W Springtown, 782 Uniontown,
  328 Hackett, 102 US-46, 00-1 Clinton.
- **Pinelands Forest** killed 2 — Lot 8.03 Sunrise Ct Medford, 235/239 Rt 72 Barnegat.
- **Wetlands >40%** killed 143 Vail Rd (57.9%) and Cardinal Ln Voorhees (45%).
- **Zoning alone** killed the rest — AR / A-R / FPD / R-only.

Note 28 W Springtown scored **93/100 on lifestyle** — the highest in the set — and is still
disqualified commercially by Highlands Preservation. That tension is the whole project in one row.

---

## 3. The big question: who can search *all* current NJ land lots?

### 3.1 Zillow does not have them all

| Source | NJ land/lot listings (Sept 2026) |
|---|---|
| Zillow | ~1,787 |
| LandSearch | ~2,721 |
| Land.com (LandWatch / Lands of America) | ~3,105 |
| LandWatch (counted 2026-09-15) | ~3,742 |

Three sites, three different universes, ~75% spread between smallest and largest. No consumer site
is complete, and each hides a different slice. Anyone who tells you "Zillow has all" is wrong —
it is true about the **website** and false about any data feed we can buy.

**And the prize is small.** The entire NJ land market is roughly **3,000–4,000 lots**. That is a
number you can screen exhaustively. The regulation screen is cheap and we already own the data for
it; the listing feed is the only thing missing.

Worse for automation: **Zillow has no usable API.** The public Web Services API was retired
30 Sep 2021. Bridge Interactive — the only official remaining door — is gated to MLS members and
licensed brokers, with a months-long approval. Third-party scraper-wrappers exist but are
unlicensed and fragile; building GroundTruth on one is a legal and operational liability.

### 3.2 Two different universes — this is the key distinction

- **FLOW** — what is *for sale right now*. Owned by the MLS. Zillow/Redfin/LandSearch are partial
  mirrors of it.
- **STOCK** — *every parcel that exists*, for sale or not. Owned by the state and the counties.
  1.9M+ NJ parcels.

GroundTruth's defensible position is STOCK. Every competitor has FLOW. Almost nobody screens the
whole stock for regulatory hard stops. The off-market parcel whose owner has not listed it is where
the margin is — and the Half Way House / CR 651 pattern (farmland-assessed, $41–130/yr tax, absentee
owner) is exactly the profile you can only find in stock data.

### 3.3 The recommended stack

**STOCK (the complete lot universe):**

1. **NJGIN Parcels and MOD-IV Composite of NJ** — free, statewide, all 21 counties, refreshed with
   2024 tax-year MOD-IV, now published as an ArcGIS Online feature service. This is *the* answer to
   "who has all current NJ land lots". You already hold Morris County; take the statewide composite.
   Cost: $0.
2. **Regrid** — commercial upgrade. All 21 NJ counties, 156M+ standardised US records,
   **standardised zoning**, building footprints, REST API. Buy this when the free NJGIN schema
   friction costs more than the subscription. Its standardised zoning field is the thing NJGIN
   cannot give you cleanly.

**FLOW (what is actually on the market):**

3. **A licensed NJ land broker, for IDX/MLS feed access.** This is the only complete *and legal*
   route to live listings, and it is also the route to Bridge Interactive if you ever want it.
   Treat it as a hire/partner decision, not a software decision — it is the single highest-leverage
   unlock in this whole list.
4. **RentCast API** — self-serve, legal, all 50 states, Land is a supported property type. Free 50
   requests/mo, $74 for 1,000, $199 for 5,000. **But its own docs admit weak coverage of larger
   rural and commercial land parcels** — exactly what this project buys. Useful as a supplement,
   not as the backbone.
5. Until then: **LandSearch** (best map-based search), **LandWatch/Land.com** (largest NJ land
   counts), **Crexi/LoopNet** (commercial land). Query them, dedupe on APN, feed the result to
   `screen.py --listings`.
6. **Scrapers for LandWatch/LandSearch/Land.com exist and are cheap (~$0.70/1,000 records) — and
   they are against those sites' terms of use.** Named here so the decision is yours, not
   recommended. Same class of problem as mirroring a copyrighted scan.

**ZONING (the "will R accept commercial" question):**

5. **NJGIN Municipal Zoning (NJDCA)** — statewide zoning layer, free.
6. **New Jersey Zoning Atlas** (National Zoning Atlas) — 564 NJ jurisdictions being coded to
   uniform categories. This is the only source that lets you ask "which NJ municipalities permit
   retail in a residential zone" as a *query* rather than by reading 564 ordinances.
7. Regrid standardised zoning as the machine-readable fallback.

**SCHOOLS:**

8. **NJ DOE School Performance Reports** — authoritative, free, downloadable; also the official
   charter school list. Niche and GreatSchools for the consumer-facing rating you already use as a
   threshold (≥7 elementary, ≥6 high school).

**CONSTRAINTS — already owned, no action needed:**

9. NJDEP Wetlands 2020 (159,056 polygons), NJ Groundwater CEA (6,763 zones), FEMA MSC, Highlands
   Council, Pinelands Commission GIS, SSURGO for Warren/Sussex/Morris.

### 3.4 Naming the agent — live scores, read off the PC

Read from `FaridOS\data\farid_os.db`, table `agent_certifications`, timestamp **2026-09-15T21:27**:

| Agent | Tier | 7-day average | Sessions | Model |
|---|---|---|---|---|
| **FarmlandAdvisor** | **CERTIFIED** | **83.6** | 189 | llama3:8b, curriculum v1.1.0, 20 topics |
| PipeEncyclopedia | TRAINED | 77.4 | 390 | pipe-encyclopedia:latest |
| **NJLandScout** | CADET | 69.5 | 1,014 | mistral-nemo, curriculum v1.2.2 |

**FarmlandAdvisor is the highest-scoring agent in the whole of FaridOS** — above the pipe brain,
above the scout. Its curriculum names farmland data collection, greenhouse, agricultural business
models and NJ permitting: the greenhouse and plaza questions are already trained.

For contrast, on 2026-07-03 the same scoreboard read FarmlandAdvisor 70.3 TRAINED and NJLandScout
30.7 UNRANKED. Both climbed hard. The scout climbed the most, 30.7 → 69.5 over 1,014 sessions.

**The honest split between them:**

- **NJLandScout decides YES or NO on regulation** — hard stops, wetlands, Highlands, Pinelands,
  output format. It is the gate.
- **FarmlandAdvisor decides whether the business works** — greenhouse economics, crop and herb
  revenue, permitting cost, phasing. It is the recommender.

They are not competitors and neither replaces the other.

**But neither of them can SEARCH.** Neither has ever been connected to a list of lots for sale. The
brains are trained; the search tool is the missing piece, and that is what `tools/nj_screener`
is for.

**Withdrawn recommendation.** The first version of this memo said local models should be kept out of
the recommend seat and restricted to geometry, on the basis that they had zero drill sessions. That
was based on a stale June file and it is wrong. FarmlandAdvisor at CERTIFIED 83.6 over 189 sessions
has earned the recommend seat. The revised split is: **NJLandScout gates, FarmlandAdvisor
recommends, Claude is the second opinion on anything that turns into an offer** — not the default
first opinion.

## 4. The R-zoning / commercial / greenhouse question — there is a legal path

The skill file currently treats R-zoning as a commercial hard stop. That is correct for a retail
plaza. It is **not** correct for the greenhouse + sell-what-you-grow model, and this changes which
parcels are worth looking at.

**NJ Right to Farm Act (N.J.S.A. 4:1C-1 et seq.) + N.J.A.C. 2:76-2A.13** protect an on-farm direct
marketing facility — a **farm market** — on a commercial farm, and that protection runs *against*
municipal zoning. The test:

- At least **51% of annual gross retail sales**, **or** 51% of sales area, must be the commercial
  farm's own agricultural output; and
- if the farm market sits on **less than 5 acres**, the land must produce at least **$2,500/yr** of
  agricultural or horticultural product.

Meaning: a greenhouse operation on agricultural or residentially-zoned land can run a retail storefront
— selling its own herbs, oils, plants, produce, plus up to 49% bought-in goods — with Right to Farm
protection, no use variance. That is not a plaza, but it is retail revenue on land a plaza could never
touch.

**Practical consequence — the two-track buy:**

- **CR 651 Wantage (R-5, $4,884/ac, outside Highlands entirely)** should be re-scored. Under the
  farm-market path its R-5 zoning is far less fatal than the current model says. Get the commercial
  farm status, build the greenhouse, run the farm market.
- **A plaza still needs commercial zoning.** A d-variance (use variance) in NJ needs 5 of 7 board
  votes plus positive and negative criteria — a multi-year, five-figure-legal-fees path with no
  guarantee. Do not buy R-zoned land intending to win one. Buy C-zoned land for the plaza
  (Half Way House Rd is that parcel) and agricultural/R land for the grow.

This is the "split live/grow + sell" strategy already in the skill file — the Right to Farm angle
makes the grow half much cheaper than the current scoring assumes.

---

## 5. Recommended next actions, in order

1. **Pull the statewide NJGIN Parcels + MOD-IV composite** (all 21 counties, not just Morris). One
   download, $0. This is the "all current NJ land lots" the question asked for.
2. **Drill NJLandScout, then FarmlandAdvisor** — they have been at zero sessions since June. Watch
   the session-5 average; below 60, move FarmlandAdvisor to mistral-nemo as already planned.
3. **Rewrite the screener as a batch job**: statewide parcels → filter vacant/farm-assessed, 3–40
   acres → minus Highlands Preservation → minus Pinelands Forest/Preservation → minus wetlands >40%
   → minus CEA hits → minus FEMA floodway. Expect a few hundred survivors statewide.
4. **Add the Right to Farm farm-market path to the evaluation skill** as a second commercial track,
   so R and AR parcels stop being scored as commercially dead.
5. **Add the school filter** from NJ DOE data at the screening stage rather than at report time —
   it is cheap and it removes a lot of parcels early.
6. **Decide on the broker relationship.** MLS access is the one thing no amount of engineering
   substitutes for. Everything else on this list you can build yourself.

---

## 6. Sources

- [NJGIN — Parcels and MOD-IV Composite of NJ](https://njogis-newjersey.opendata.arcgis.com/documents/406cf6860390467d9f328ed19daa359d)
- [NJGIN — Municipal Zoning (NJDCA)](https://njogis-newjersey.opendata.arcgis.com/datasets/njdca::municipal-zoning)
- [Regrid — Property/Parcel API](https://regrid.com/api) · [New Jersey parcel data](https://regrid.com/new-jersey-parcel-data)
- [New Jersey Zoning Atlas (National Zoning Atlas)](https://www.zoningatlas.org/new-jersey)
- [Zillow — NJ land & lots](https://www.zillow.com/nj/land/) · [LandSearch — NJ](https://www.landsearch.com/properties/new-jersey) · [Land.com — NJ](https://www.land.com/New-Jersey/all-land/)
- [Is the Zillow API still available in 2026?](https://zillapi.com/blog/is-zillow-api-still-available-2026/) · [Bridge Interactive requirements & access](https://apillow.co/blog/bridge-interactive-api)
- [NJ Right to Farm Act (SADC)](https://www.nj.gov/agriculture/sadc/documents/rtfprogram/rtfact/rtfa.pdf) · [N.J.A.C. 2:76-2A.13](https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-2-76-2A-13) · [Rutgers FS1253](https://njaes.rutgers.edu/fs1253/)
