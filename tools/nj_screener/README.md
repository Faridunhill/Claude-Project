# NJ Statewide Land Screener

Takes every parcel in New Jersey (~1.9M) and narrows it to a ranked, mapped shortlist that matches
the Farmhouse / GroundTruth filters.

**Yes — the output is a map.** One self-contained HTML file: pan and zoom New Jersey, every
surviving parcel drawn in its real shape, coloured by which track it qualifies for, shaded by score,
click any parcel for the numbers behind it. Plus a CSV for the spreadsheet and a GeoJSON for QGIS.

It runs on your PC, not in the cloud — the data is large and already mostly downloaded there.

**Two modes, because there are two universes:**

| Mode | What it screens | Size |
|---|---|---|
| `py screen.py` | **Stock** — every parcel in NJ, for sale or not | ~1.9M parcels |
| `py screen.py --listings lots.csv` | **Flow** — only lots actually for sale | ~3,000–4,000 lots |

The flow is tiny. LandWatch lists 3,742 NJ land properties, LandSearch 2,721 (counted 2026-09-15).
That whole market can be screened exhaustively in one run — the regulation screen is cheap and the
data is already paid for. The listing feed is the only thing missing, and that is a broker
relationship, not a piece of software.

The stock is where the margin is: parcels nobody has listed yet, which is the profile both active
candidates already fit (farmland-assessed, $41–130/yr tax, absentee owner).

---

## The filters, as configured

| # | Your requirement | How it is implemented | Default |
|---|---|---|---|
| 1 | Schools 7/10 or better | District rating joined by municipality, hard filter | `min_school_rating: 7.0` |
| 2 | Anywhere in NJ, Central/South preferred | Region computed from county; bonus points, not a gate | `region_mode: prefer` |
| 3 | R and C zoning both matter | Zone code → category via `zone_rules.csv`; keeps C and R | `zoning_categories_wanted: [C, R]` |
| 4 | Cluster / subdivision wanted | `est_lots = net buildable acres ÷ zone minimum lot size`, plus a per-municipality cluster flag | `subdivision_mode: prefer` |

Greenhouse is deliberately **not** a filter. You said it is flexible — hold it or buy cheap land
nearby. So the screener scores the *farm market* path (Track B) as a commercial option wherever
agriculture is permitted, and you decide later whether the greenhouse sits on the same parcel or a
second cheaper one.

Everything above lives in `config.yml`. Change the file, not the code.

---

## The three tracks it sorts into

| Colour on the map | Verdict | Meaning |
|---|---|---|
| 🟩 Green | **Track A + B** | Commercial zoning *and* agriculture permitted — both paths open. Rare and valuable. |
| 🟦 Blue | **Track A (plaza)** | Retail permitted by right. Plaza land. |
| 🟨 Amber | **Track B (farm market)** | Right to Farm path — greenhouse plus a farm market selling your own output. |
| 🟪 Purple | **Track B — verify ag permitted** | Looks right, but nobody has read the ordinance yet. Gate 1 unconfirmed. |
| ⬜ Grey | **Lifestyle only** | Land is fine, no commercial path found. |

Track B follows the evaluation skill v2.0.0: 5+ acres means the commercial-farm threshold is only
$2,500/yr; under 5 acres it jumps to $50,000/yr. The screener reports which threshold applies to
each parcel.

---

## Install

```bat
py -m pip install -r requirements.txt
```

`geopandas` on Windows is easiest via conda if pip fights you:
`conda install -c conda-forge geopandas folium pyogrio`

---

## Run it — five steps

### 1. Get the statewide parcels

**The MOD-IV service is already connected on this PC.** The farm-class pull (3A + 3B, 32,257 rows)
came from it and lives at `data\hub\parcels\nj_modiv\nj_farm_parcels.sqlite`. What has never
been pulled is everything else — class 1 vacant, 2 residential, 4A commercial — and those are
exactly what make "R zoning that accepts commercial" answerable statewide.

```bat
py fetch_data.py                                  # zoning, Highlands, Pinelands
py fetch_data.py --only parcels --classes 1,2,3A,3B,4A
```

That pulls zoning, Highlands and Pinelands automatically, and MOD-IV by property class. Parcels are the exception: the statewide
composite is far too big for the paging API, so download the per-county files from the NJGIN Open
Data portal ("Parcels and MOD-IV Composite of NJ"), drop them all in one folder, then:

```bat
py fetch_data.py --merge-counties C:\Users\hadid\Downloads\nj_parcels
```

**You do not need to copy the regulatory layers** — `config.yml` now points at where they already
live on the PC:

| Layer | Rows | Path |
|---|---|---|
| NJDEP wetlands 2020 | 159,056 | `groundtruth\documents\gis_data\wetlands_NJ2020.zip` |
| NJ groundwater CEA | 6,763 | `groundtruth\data\NJ_Groundwater_CEA.geojson` |
| FEMA flood zones | 13.1 MB | `data\hub\flood\fema_nfhl\flood_zones.sqlite` |
| SSURGO soils | 0.7 MB | `data\hub\soils\ssurgo\nj_soils.sqlite` |

If any path has moved, fix it in `config.yml` — nothing is hardcoded in the scripts.

### 2. Scaffold the lookup tables

```bat
py scaffold_lookups.py
```

This writes three CSVs listing every municipality and zone code that actually appears in the data,
with the value columns **left blank on purpose**. No rating, lot size or cluster flag is invented —
a blank is honest, a guessed number quietly decides which land you buy.

| File | You fill in | Where it comes from |
|---|---|---|
| `data/school_ratings.csv` | `district`, `rating` (0–10) | NJ DOE School Performance Reports; Niche / GreatSchools for the 1–10 scale |
| `data/zone_rules.csv` | `zone_category`, `min_lot_acres`, `ag_permitted` | Municipal ordinance bulk tables; NJ Zoning Atlas covers 564 NJ jurisdictions |
| `data/municipal_flags.csv` | `allows_cluster` (Y/N/UNKNOWN) | Municipal ordinance; MLUL cluster/open-space provisions |

`zone_rules.csv` ships a `zone_category_guess` column derived from the code string (C-1 → C,
R-5 → R, AR → AG). **It is a starting guess, not an answer** — confirm against the ordinance,
especially `ag_permitted`, which is Right to Farm Gate 1 and the thing that decides Track B.

Re-running with `--force` refreshes the lists while keeping everything you already filled in.

You do not have to do all 565 municipalities. Fill in the counties you care about; parcels in
unfilled municipalities drop out with reason `school rating unknown` and are listed in
`out/nj_rejected.csv`, so nothing disappears silently.

### 3. Test on one county first

```bat
py screen.py --county WARREN
```

### 4. Run statewide — or just the for-sale list

```bat
py screen.py                              # all ~1.9M parcels
py screen.py --listings out\nj_lots.csv   # only lots for sale
```

The listings CSV needs either a `pin`/`apn` column (exact match, always prefer this) or
`address` + `municipality`. Export it from an MLS/IDX feed, a broker's spreadsheet, or build it by
hand. **The screener does not scrape** — obtaining the list is a separate decision and the legal
route is a licensed NJ broker.

Expect a few minutes to a couple of hours depending on how many parcels survive stage 1 — the
wetlands overlay is the slow part, which is exactly why the cheap filters run first.

### 5. Open the map

```
out\nj_candidates_map.html
```

Also written: `out\nj_candidates.csv`, `out\nj_candidates.geojson`, `out\nj_rejected.csv`.

To redraw the map without re-screening: `py make_map.py`

---

## How it works — the order is the whole trick

```
1.9M parcels
  │
  ├─ STAGE 1  attribute filters (cheap, no geometry)
  │     vacant / farm classes 1, 3A, 3B
  │     3–60 acres
  │     drop government, church, cemetery, land trust owners
  │  ≈ 40,000 left
  │
  ├─ STAGE 2  lookups and zoning (table joins + one centroid sjoin)
  │     school rating ≥ 7
  │     zone category in {C, R}
  │  ≈ 3,000 left
  │
  ├─ STAGE 3  geometry and regulatory screen (expensive — runs last)
  │     wetlands polygon intersection, >40% or centroid inside → drop, ALL tracks
  │     CEA contamination zone → drop, ALL tracks
  │     FEMA floodway → drop, ALL tracks
  │     Highlands Preservation → Track A only
  │     Pinelands Forest/Preservation → Track A only
  │  ≈ 400 left
  │
  └─ STAGE 4  tracks, subdivision estimate, 100-point score
        → CSV + GeoJSON + interactive map
```

Counts are illustrative. The real numbers come out in the log.

**Environmental hard stops kill all three tracks and are not configurable away** — wetlands over
40%, centroid inside a wetland, contamination zone, floodway. Zoning stops are per-track, which is
the whole point of evaluation skill v2.0.0.

---

## Honest limits — read before trusting a run

- **A missing layer is skipped, not passed.** If `fema_nfhl.gpkg` is absent the floodway check does
  not run and the log says so. It does not silently mark parcels clean.
- **School ratings are not free statewide data.** NJ DOE publishes performance data, not a 1–10
  score. You are maintaining that table by hand. That is a real cost, and it is why the rating is a
  municipality-level join rather than a per-school one.
- **Cluster/subdivision has no statewide dataset.** `est_lots` is arithmetic — net buildable acres
  divided by the zone minimum lot size. It ignores road frontage, soil for septic, environmental
  constraints on layout, and municipal density bonuses. Treat it as a flag to investigate, never as
  a yield.
- **Zone codes are not standardised across 565 municipalities.** `zone_rules.csv` is where that mess
  gets normalised, and it is only as good as what you put in it.
- **South Jersey is Pinelands-heavy.** Preferring Central/South and hard-stopping Pinelands
  Forest/Preservation pull against each other. Expect the Central band — Hunterdon, Mercer,
  Somerset, Monmouth, western Middlesex — to produce most of the Track A hits.
- **This finds candidates. It does not do due diligence.** Every survivor still goes through
  `nj-farmhouse-parcel-evaluation` v2.0.0 before anyone picks up a phone.
- **Parcel ≠ for sale.** The default run screens the whole stock, not the market. Most survivors
  are not listed. That is the point — it is also why an MLS relationship stays on the roadmap. Use
  `--listings` when you want the market instead.
- **The farm-only extract is not enough on its own.** `nj_farm_parcels.sqlite` holds classes 3A/3B.
  Run against that and Track A (plaza, commercial zoning) is invisible — you will only ever see
  farm land. Pull the other classes first.

---

## Files

| File | Purpose |
|---|---|
| `config.yml` | Every filter and weight. Edit this. |
| `fetch_data.py` | Download statewide layers; merge per-county parcel files |
| `scaffold_lookups.py` | Generate the three lookup CSVs from the real data |
| `screen.py` | The four-stage screener |
| `make_map.py` | Interactive Leaflet map |
| `common.py` | Column resolution, region lookup, config loading |

---

## Backfill: get the 18 known parcels into the database

`farmland_parcels`, `parcel_outcomes`, `greenhouse_projects`, `business_plans`, `permit_log` and
`crop_market_data` were built in June 2026 and **every one holds 0 rows** (measured 2026-09-15).
Until they hold data, nothing about this pipeline is proven end to end.

```bat
py backfill_known_parcels.py --inspect    # read the live schema, write nothing
py backfill_known_parcels.py --dry-run    # show the plan
py backfill_known_parcels.py              # write
```

The real schema lives on your PC and was never read from here, so the script does not assume it. It
reads the actual columns with `PRAGMA table_info` and maps the seed fields onto whatever is there.
A column it cannot match is **reported and left NULL**, never guessed. It sets
`PRAGMA foreign_keys = ON`, which the `parcel_outcomes` foreign key needs and which
`TRAINER_STATUS.md` flagged as an outstanding fix.

Verified against two deliberately different mock schemas: `py test_backfill.py`.

### What goes in, and what does not

`seed/known_parcels.json` holds all 18 parcels, reconciled from two sources:

- **11 parcels with GIS-measured geometry** — wetland acreage from real polygon intersection
  against NJDEP Wetlands 2020 in EPSG:3424, plus price, tax class, assessed value, score.
- **7 parcels with a disposition and reason but no measurements.** Their numeric fields are
  **null on purpose.** A null is honest; a zero would be a lie that later reads as "no wetlands".

**Only 11 can actually be written.** The other 7 have no PAMS PIN, and the PIN is the key. They are
not dropped quietly and they are not given a fake key — they are written to
`out/parcels_needing_pin.csv` with `pams_pin_TO_FILL`, `block_TO_FILL` and `lot_TO_FILL` columns.
Look each one up in MOD-IV, paste the PINs back into `seed/known_parcels.json`, re-run, and all 18
land.

The seven: Cardinal Ln Voorhees · 180 Black Brook Bethlehem · 102 US Hwy 46 Independence ·
44 Shongum Denville · 00-1 Clinton West Milford · 235/239 Rt 72 Barnegat · 22 Estell Dr Hardyston.

**Prices and listing status in the seed are from June 2026 and are not current.** The script says so
every time it runs.
