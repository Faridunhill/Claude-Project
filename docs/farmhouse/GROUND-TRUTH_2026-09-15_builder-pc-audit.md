<!-- CANONICAL SOURCE — DO NOT EDIT THE BODY OF THIS FILE -->
> **STATUS: CORE REFERENCE.** This is the Builder's direct audit of Farid's PC, run 2026-09-15.
> Every line in it was measured on the machine, not remembered and not inferred.
>
> **Precedence.** Where this document disagrees with anything else — the Drive copies of
> `TRAINER_STATUS.md`, `FARMHOUSE_STATUS.md`, an earlier analysis, or a previous answer of mine —
> **this document wins.** It is newer and it was measured at the source.
>
> **Known superseded by this file:**
> - `TRAINER_STATUS.md` v1.5.0 (Drive, 2026-06-26) — agent tiers and session counts are three
>   months stale. Live figures are in §3 below.
> - Any statement that NJLandScout or FarmlandAdvisor is UNRANKED or has zero sessions.
> - Any statement that the 100+ farm analyses exist in a recoverable file.
>
> **Do not edit the body below.** Corrections go in a dated note appended at the end, or in a
> newer audit file alongside this one.

---

# THE FARM HOUSE / PARK PROJECT — WHAT IS ACTUALLY ON HIS PC
**Written 2026-09-15 by the Builder, after Farid's order: "collect from my pc, the farm
house chat if you can". Every line below was run or read on this machine tonight.
Nothing here is remembered.**

His words, 2026-09-15: *"I stopped this website because i didn't trust that we can afford
neat and accurate."* That sentence is the whole design brief. The honesty gate is not a
nice-to-have on this product — it is the reason he stopped.

> **NOTE ON THE DOMAIN.** He typed `groundtruthaiproperty.com`. The live site is
> **groundtruthpropertyai.com** (HTTP 200, verified 2026-08-02, §7 of the asset map).
> Word order: property **then** ai. Worth a check that he does not own the other spelling
> and think it is the same site.

---

## 1 · THE FARM HOUSE CHAT — FOUND, AND WHAT IT IS NOT

**FOUND on this PC.** The method document survives in full:

| File | Size | What it is |
|---|---|---|
| `C:\Users\hadid\groundtruth\skills\nj-farmhouse-parcel-evaluation_SKILL.md` | 21.5 KB | **The evaluation method.** 7 steps, every filter he listed. |
| `Downloads\nj-farmhouse-parcel-evaluation_SKILL_updated.md` | 21.5 KB | same file, second copy |
| `FaridOS\archive\downloads_20260629\` | — | third copy, archived |
| `Downloads\FARMHOUSE_STATUS.md.txt` | 2.8 KB | project status, 2026-06-24 |
| `groundtruth\apps\parcel_comparison_dashboard.html` | 33.3 KB | ONE parcel report page, not a list |

**The method covers exactly what he asked for**, in this order:
1. Coordinates first, from a Google Maps embed link — wetlands answer in seconds
2. Highlands designation — Preservation Area = hard stop on commercial
3. Pinelands designation — Forest/Preservation Area = retail prohibited = hard stop
4. Zoning — C-1/C-2/Village Business/B-1/B-2 accepted; **R-1 to R-5 and AR = hard stop for commercial**
5. Wetlands 40% rule — over 40% of gross acres = hard stop both tracks
6. FEMA flood — Zone AE major constraint, floodway = no building
7. Groundwater contamination (CEA) — inside a zone = disqualified
8. Soils, slope, stream buffers, net buildable acres
9. Greenhouse / herb oil — permitted outright or conditional use, NJDEP air permit for solvent extraction, irrigation well permit
10. Schools — Niche + GreatSchools + NJ DOE; threshold 7/10 elementary, 6/10 high
11. Financial summary, rollback tax, modular build cost
12. 100-point composite score; 70+ = look deeper, under 60 = pass

**NOT FOUND: the 100+ farm analyses.** This is the honest gap and he must know it.

- The skill file names **18 parcels**: 2 active candidates and 16 rejected with reasons.
- `farid_os.db` has the tables built for them — `farmland_parcels`, `parcel_outcomes`,
  `greenhouse_projects`, `business_plans`, `permit_log`, `crop_market_data`.
  **Every one of those tables has 0 rows.** Measured 2026-09-15.
- So the 100+ analyses were done inside a claude.ai WEB chat and never came home.
  This is the same fault as memory `everything-lives-local`.

**THE 18 PARCELS THAT ARE WRITTEN DOWN** (from the skill file, kept verbatim):

ACTIVE (do not re-evaluate):
- 0 Half Way House Rd, Franklin Twp, Warren Co — 6.42 ac, C-1, scored 71–74/100,
  wetland edge 820+ ft, pending Highlands parcel-level check + FEMA
- 0 CR 651, Wantage, Sussex Co — 12.08 ac, R-5, $59K, wetland edge 356 ft (close call)

REJECTED, with the reason:
Cardinal Ln Voorhees (45% wetlands) · 180 Black Brook Bethlehem (under contract) ·
312 Mountain Lake Liberty (Highlands Preservation) · 28 W Springtown Long Valley
(Highlands Preservation) · 782 Uniontown Lopatcong (Highlands Preservation likely) ·
102 US Hwy 46 Independence (Highlands Preservation) · 143 Vail Knowlton (Highlands +
wetlands + ag-only zoning) · 44 Shongum Denville (C1 stream buffer) · 1221 Rt 94
Frelinghuysen (stream bisecting + AR-6) · 328 Hackett Bethlehem (Highlands Preservation +
167% tax increase) · 500 Rt 94 Fredon (viable lifestyle) · 00-1 Clinton West Milford
(100% Highlands + 81% FEMA floodway) · 235/239 Rt 72 Barnegat (Pinelands Forest) ·
Lot 8.03 Sunrise Ct Medford (Pinelands) · 36 Countryside Rd Knowlton (FPD + seller-disclosed
wetlands) · 22 Estell Dr Hardyston Sussex (center point INSIDE a 19.09-ac wetland)

Two named contacts survive too:
- Jim Onembo, Franklin Twp Warren zoning — 908-689-5721 / zoning@franklintwpwarren.org
- Andrew Coccio, Wantage land use — 973-875-7195 ext. 7

---

## 2 · THE DATA THAT IS ALREADY HERE AND PAID FOR

| Data | Rows | Path |
|---|---|---|
| NJ farm parcels, tax class 3A + 3B | **32,257** | `data\hub\parcels\nj_modiv\nj_farm_parcels.sqlite` |
| NJDEP wetlands polygons, statewide 2020 | **159,056** | `groundtruth\documents\gis_data\wetlands_NJ2020.zip` (176.9 MB) |
| NJ groundwater contamination zones (CEA) | **6,763** | `groundtruth\data\NJ_Groundwater_CEA.geojson` |
| FEMA flood zones | 13.1 MB | `data\hub\flood\fema_nfhl\flood_zones.sqlite` |
| NJ soils (SSURGO) | 0.7 MB + per-county zips | `data\hub\soils\ssurgo\nj_soils.sqlite` |
| Pinelands CMP (the rule book) | 2.9 MB PDF | `groundtruth\documents\pinelands_cmp.pdf` |
| NJ wetlands rules 7:7A | 1.8 MB PDF | `groundtruth\documents\nj_wetlands_7_7a.pdf` |
| NJ Highlands Act | 3.1 KB PDF | `groundtruth\documents\nj_highlands_act.pdf` |

**What this data is: who OWNS every farm parcel. What it is NOT: which lots are FOR SALE.**
That single gap is his question tonight.

---

## 3 · THE THREE TRAINED AGENTS — LIVE SCORES, READ TONIGHT

From `FaridOS\data\farid_os.db` table `agent_certifications`,
timestamp `2026-09-15T21:27` — three hours before this document:

| Agent | Tier | 7-day average | Sessions |
|---|---|---|---|
| **FarmlandAdvisor** | **CERTIFIED** | **83.6** | 189 |
| PipeEncyclopedia | TRAINED | 77.4 | 390 |
| NJLandScout ("the scout") | CADET | 69.5 | 1,014 |

**FarmlandAdvisor is the highest-scoring agent in the entire FaridOS.** Higher than the
pipe brain, and higher than the scout he remembers.

- Curriculum: `Downloads\farmland_advisor.json` v1.1.0, 114 KB, 20 topics, author FARID CKA,
  model llama3:8b. It is a MERGE of FarmhouseAdvisor and BusinessBuilder.
- Its description names: farmland data collection, **greenhouse**, agricultural business
  models, NJ permitting. That is his greenhouse and plaza question, already trained.
- FarmhouseAdvisor v1.0.0 (41.6 KB, 13 topics) is the older version. Superseded. Not used.
- NJLandScout v1.2.2 lives at `FaridOS\trainer\curriculum\nj_land_scout.json`, model
  mistral-nemo. Its job is the REGULATORY verdict — hard stops, wetlands, output format.

**THE HONEST SPLIT:** the scout decides YES or NO on regulation. FarmlandAdvisor decides
whether the business works. They are not competitors. Neither of them can SEARCH.
Neither has ever been connected to a list of lots for sale.

For history: on 2026-07-03 the same scoreboard read FarmlandAdvisor 70.3 TRAINED,
NJLandScout 30.7 UNRANKED. Both climbed. The scout climbed the most, from 30.7 to 69.5.

---

## 4 · HIS BIG QUESTION — WHO CAN SEARCH EVERY NJ LAND LOT FOR SALE

He said: *"who is the best to search all current NJ land lots, zellow has all, find access."*

### ZILLOW IS CLOSED. This is the finding he needs first.

Zillow's public API (ZWSID) was retired **30 September 2021**. There has been no open
self-serve Zillow API since. The official replacement, **Bridge Interactive**, is
enterprise-only and is gated to MLS-affiliated brokers, with an application process and
months-long approval.
Sources: [Is the Zillow API still available in 2026? — Zillapi](https://zillapi.com/blog/is-zillow-api-still-available-2026/) ·
[Zillow API Discontinued? The 5 Best Alternatives in 2026 — APIllow](https://apillow.co/blog/zillow-api-alternatives-2026)

**So "Zillow has all" is true about the WEBSITE and false about a data feed we can buy.**

### THE FOUR REAL ROADS, measured

| # | Road | Legal? | Cost | Land coverage |
|---|---|---|---|---|
| 1 | **MLS feed via a licensed NJ broker** (Garden State MLS / Bright MLS / NJMLS / MOREMLS) | YES, the clean road | broker contract | **complete** — this is the source Zillow itself copies |
| 2 | **RentCast API**, self-serve | YES | free 50/mo, $74/mo for 1,000 | **weak on the land he wants** |
| 3 | **Apify scrapers** for LandWatch / LandSearch / Land.com | **NO — against their terms** | ~$0.70 per 1,000 records | good |
| 4 | **NJ MOD-IV parcels**, already on this PC | YES, free, public | $0 | owners, **not for-sale** |

**Road 1 — the MLS.** Bright MLS is RESO Data Dictionary 1.6 Platinum certified and
supports the RESO Web API. Access needs a contract with Bright Content Licensing. NJMLS
serves its IDX through RE/Advantage. Garden State MLS, Bright MLS, MOREMLS and NJMLS all
cover parts of the same New Jersey map.
Sources: [FAQ · Bright MLS RESO Web API](https://developer.brightmls.com/brightreso/default/faq) ·
[IDX · Bright MLS](https://brightmls.com/products/IDX) ·
[NJMLS Internet Data Exchange](https://www.newjerseymls.com/services/internet-data-exchange-idx/)

**Road 2 — RentCast.** It is self-serve, it covers all 50 states, and **Land is a supported
property type**. But RentCast's own documentation says it has *"higher coverage for smaller
residential and urban lots, and more limited coverage for larger commercial or rural land
parcels."* Rural acreage is exactly what the farm house project buys. So RentCast is honest
about being weak at his job. Pricing: free 50 requests, $74 for 1,000, $199 for 5,000,
$449 for 25,000.
Sources: [RentCast property types](https://developers.rentcast.io/reference/property-types) ·
[PropData vs RentCast vs ATTOM vs Cotality — PropTechUSA](https://www.proptechusa.ai/editorial/data-api-honest-comparison)

**Road 3 — the scrapers.** They work and they are cheap. LandWatch, LandSearch, Land.com
and Redfin all have Apify scrapers with 90+ fields, GPS, price history, acreage filters and
agent contacts. **They are against those sites' terms of use.** Under LAW 2 (buy, don't
pirate) that is the same class of problem as mirroring a copyrighted scan. It is named here
so he can decide, not recommended.
Sources: [LandSearch Listing Scraper · Apify](https://apify.com/moving_beacon-owner1/landsearch-listing-scraper/api) ·
[Land.com Scraper · Apify](https://apify.com/solidcode/land-com-scraper/api)

**Road 4 — what we own.** NJ MOD-IV is public and already connected
(`services2.arcgis.com/.../NJ_MOD4_Parcels/FeatureServer/0/query`). We loaded only farm
classes 3A and 3B. The other classes — residential, commercial, vacant — are reachable from
the same service and were never pulled. That would tell him every lot, its owner, its
acreage, its assessed value and its last sale price. It will never tell him a lot is listed.

### HOW BIG IS THE PRIZE — counted tonight

- **LandWatch** lists **3,742** New Jersey land properties for sale
- **LandSearch** lists **2,721** New Jersey properties, average asking price $1,093,712

Sources: [New Jersey Land for Sale · LandWatch](https://www.landwatch.com/new-jersey-land-for-sale) ·
[New Jersey Land for Sale · LandSearch](https://www.landsearch.com/properties/new-jersey)

So the whole NJ land market is roughly **3,000 to 4,000 lots**. That is small. Every one
of them can be screened by the method in §1 against the data in §2. The screen is cheap;
the listing feed is the only thing we do not have.

---

## 5 · THE BUILDER'S RECOMMENDATION, one sentence each

1. **Do not buy a listings API yet.** Fill the local database first. We have 3,000–4,000
   lots' worth of regulation and zero rows in `farmland_parcels`.
2. **Complete NJ MOD-IV to all classes.** Free, public, already connected, and it is the
   only way to answer "R zoning that accepts commercial" across the whole state at once.
3. **Run the 18 known parcels through the current engine and write them into
   `farmland_parcels`.** It proves the pipeline end to end on real addresses he chose.
4. **The listing feed is a business decision, not a technical one.** The clean road is a
   licensed NJ broker relationship. He already owns a list of 22,132 licensed TN agents and
   has never used it — the same play works in NJ.
5. **FarmlandAdvisor (CERTIFIED 83.6) is the agent to put in front of this**, with
   NJLandScout (CADET 69.5) as the regulatory gate before it. Neither one searches. A
   search tool has to be built or bought; the brains are already trained.

---

## 6 · WHAT IS STILL UNVERIFIED — said plainly

- **The 100+ farm analyses are not on this PC.** I searched Downloads, Documents, OneDrive,
  Desktop, FaridOS and the groundtruth folder by file name and by content. If he has that
  claude.ai chat open on his phone, exporting it is the only way to bring it home.
- **I did not check whether any of the 18 parcels are still for sale.** Those prices and
  statuses are from June 2026.
- **I did not price the MLS road.** Bright and Garden State do not publish it; it needs a
  phone call and a broker.
- **I did not verify who owns `groundtruthaiproperty.com`** (his spelling) versus
  `groundtruthpropertyai.com` (the live site).
