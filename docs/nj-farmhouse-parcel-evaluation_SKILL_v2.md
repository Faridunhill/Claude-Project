---
name: nj-farmhouse-parcel-evaluation
version: 2.0.0
description: Full due-diligence evaluation of any NJ land parcel for Farid's Farmhouse Project. Triggers whenever the user provides a property address, Zillow link, MLS link, block/lot, or Google Maps embed link for a New Jersey parcel they want evaluated. Runs every regulatory, environmental, zoning, lifestyle, and commercial filter — Highlands, Pinelands, wetlands, flood, soils, contamination, schools, plaza viability, farm-market viability, greenhouse/herb oil operation, family compound score — and returns a structured verdict with red/orange/yellow flag tiers and a 100-point composite score.
---

# NJ Farmhouse Project — Parcel Evaluation Skill

## Purpose

Evaluate any New Jersey land parcel against Farid's investment thesis. **As of v2.0.0 there are
THREE tracks, not two.** Every parcel gets evaluated on all three. Failure on one track never ends
the evaluation — the other tracks are always assessed independently.

**Track A — Plaza Track (commercial).** A retail plaza of 3–4 stores. Needs commercially-zoned land.
This is the hardest track and the one most parcels fail.

**Track B — Farm Market Track (agricultural commerce). ⚡ NEW IN v2.0.0.** A commercial greenhouse
plus an on-site farm market selling what you grow — herbs, oils, plants, produce — protected by the
NJ Right to Farm Act *against* municipal zoning. This track works on agricultural and residential
land where Track A is impossible.

**Track C — Lifestyle Track.** Rural NJ family compound: school quality, privacy, acreage,
long-term appreciation.

---

## ⚡ WHAT CHANGED IN v2.0.0 — READ THIS FIRST

**The old rule was: R zoning or AR zoning = commercial dead. That rule was too blunt and it threw
away good parcels.**

Here is the simple version of what we learned:

> New Jersey has a law called the **Right to Farm Act**. It says that if you run a real farm, the
> town cannot use its zoning rules to shut down normal farming activity — and **selling your own
> crops on your own land is normal farming activity.** The state calls that shop a **"farm market."**
>
> So: a greenhouse on residential or agricultural land can legally run a retail store, selling your
> own herbs, oils, plants and produce, **without a use variance**, as long as more than half of what
> you sell is what you grew.
>
> That is not a plaza. You cannot rent it to a pizza shop and a nail salon. But it is real retail
> revenue, on land that costs a fraction of commercial land.

**What this means in practice:**

| | Old scoring (v1) | New scoring (v2) |
|---|---|---|
| C-1 / C-2 / B-1 / Highway Commercial | Commercial VIABLE | Track A VIABLE, Track B viable |
| AR / A-R / AG (agricultural) | Commercial HARD STOP | Track A hard stop, **Track B is the natural fit** |
| R-1 … R-5 (residential) | Commercial HARD STOP | Track A hard stop, **Track B often viable — check gate** |
| Highlands Preservation | Hard stop | **Still a hard stop for Track A. Agriculture is generally still allowed — check Track B** |
| Pinelands Forest/Preservation | Hard stop | **Still a hard stop for Track A. Agriculture has its own Pinelands rules — check separately** |
| Wetlands > 40% | Hard stop both tracks | **Still a hard stop on ALL tracks. Unchanged.** |
| Parcel centre inside wetland | Hard stop both tracks | **Still a hard stop on ALL tracks. Unchanged.** |
| CEA contamination hit | Hard stop both tracks | **Still a hard stop on ALL tracks. Unchanged.** |

**Environmental hard stops did not get softer. Only the ZONING hard stop got a second door.**

**Re-score these previously-passed parcels under Track B:**
- 0 CR 651, Wantage (R-5, 9.96 ac, $4,884/ac, outside Highlands entirely) — **highest priority
  re-score. R-5 is far less fatal than v1 scored it.**
- 312 Mountain Lake Rd, Liberty Twp (AR, 30.94 ac, **0% wetlands**) — 31 clean acres. Agriculture is
  the permitted use. Track A stays dead on Highlands Preservation; Track B may be strong.
- 328 Hackett Rd, Bethlehem Twp (AG, 14.03 ac, 0% wetlands) — same logic.
- 1221 Route 94, Frelinghuysen (AR-6, 34% wetlands, stream bisect) — re-check, but wetlands and the
  C1 stream buffer still hurt badly.

Do **not** re-score these — they failed on environment or on both, not on zoning alone:
143 Vail Rd (57.9% wetlands), Cardinal Ln Voorhees (45% wetlands), 22 Estell Dr Hardyston (centre
inside wetland), 36 Countryside Rd (FPD flood plain + seller-disclosed wetlands), 00-1 Clinton
West Milford (81% FEMA floodway).

---

## Required Inputs

Accept ANY of the following as the trigger. Missing items are looked up during the workflow:

- Property address (street, municipality, county)
- Zillow, Redfin, LandSearch, or MLS link
- Block and lot number
- Acreage and asking price (pull from listing if not stated)
- **Google Maps embed link (preferred — extract coordinates immediately)**

---

## ⚡ COORDINATE EXTRACTION — DO THIS FIRST FOR EVERY PARCEL

**The Google Maps embed link is the fastest path to wetlands analysis. Extract coordinates from it
before doing anything else.**

### How to extract lat/lon from a Google Maps embed link

The embed URL contains the coordinates directly. Example:

```
https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3005.6!2d-74.60922!3d41.12125!...
```

- The value after `!2d` = **longitude** (e.g. `-74.60922`)
- The value after `!3d` = **latitude** (e.g. `41.12125`)

Extract these two numbers and immediately run the wetlands analysis in Step 2D before any other step.

### What to ask Farid if no embed link is provided

Say: *"Please go to Google Maps, search the address, click Share → Embed a map, copy the iframe code,
and paste it here. This lets me run wetlands analysis in seconds."*

Alternatively, Farid can right-click the map pin → "What's here?" → paste the lat/lon numbers directly.

### Why this matters

- The NJDEP `Wetlands_(2020).shp` shapefile (159,056 polygons, statewide) is loaded locally
- A single lat/lon point query runs in under 5 seconds and gives immediate edge-distance results
- If the parcel center is INSIDE a wetland polygon → automatic hard stop, no further steps needed
- If nearest wetland edge is >500 ft → likely clean, continue full evaluation
- If nearest wetland edge is 100–500 ft → close call, flag as 🟠 MAJOR RISK, note that parcel
  boundary polygon needed to confirm

### Coordinate query logic (Python/geopandas against loaded shapefile)

```python
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer

# Shapefile path: /tmp/wetlands_data/Wetlands_(2020).shp
# CRS: EPSG:3424 (NJ State Plane, US Survey Feet)

gdf = gpd.read_file('/tmp/wetlands_data/Wetlands_(2020).shp')
transformer = Transformer.from_crs('EPSG:4326', 'EPSG:3424', always_xy=True)

lat, lon = [EXTRACTED_LAT], [EXTRACTED_LON]
x, y = transformer.transform(lon, lat)
pt = Point(x, y)

# Check containment first (instant hard stop)
contained = gdf[gdf.contains(pt)]
if len(contained) > 0:
    pass  # HARD STOP — center point is inside a wetland polygon

# Then check proximity
buf1km = pt.buffer(1000)
near = gdf[gdf.intersects(buf1km)].copy()
near['nearest_edge_ft'] = near.geometry.distance(pt)
near_sorted = near.sort_values('nearest_edge_ft')
# Report: polygon label, total acres, distance of nearest edge in feet
```

### Interpreting results

| Result | Meaning | Action |
|---|---|---|
| Center point INSIDE wetland polygon | Parcel is built on wetland | 🔴 HARD STOP — all tracks |
| Nearest edge < 100 ft | Wetland almost certainly overlaps parcel | 🔴 HARD STOP — flag for boundary confirmation |
| Nearest edge 100–500 ft | Could overlap depending on parcel shape/depth | 🟠 MAJOR RISK — need parcel boundary polygon |
| Nearest edge 500–1000 ft | Likely clear but flag for long/narrow parcels | 🟡 WATCH — note parcel geometry |
| Nearest edge > 1000 ft | Clean — proceed with full evaluation | ✅ Continue |

### Getting the parcel boundary polygon (for close calls)

When a close call requires exact polygon intersection:

1. **Warren County GIS Hub** → warrencountynj.gov/government/planning-department/data-and-mapping →
   download parcel layer → upload here
2. Or: **NJGIN open data** → njgin.nj.gov/edata/parcels → county download → upload here
3. Or: **NJGIN statewide** → "Parcels and MOD-IV Composite of NJ" ArcGIS feature service (all 21
   counties, 2024 tax-year MOD-IV) — preferred once loaded locally
4. Once uploaded, run exact polygon-on-polygon intersection for precise wetland acreage and percentage

---

## Evaluation Workflow (execute in this order)

### STEP 1 — Identify Parcel Basics

Collect or derive:

- Full address, municipality, county
- Block / Lot
- Gross acreage
- Asking price
- Price per gross acre
- Current zoning designation and zoning district name
- Current assessed value and tax amount
- **Farmland assessment (3B/QFARM)?** → Flag rollback tax liability, AND flag as a **positive signal
  for Track B** (see Step 4D — farmland-assessed land is already most of the way to commercial farm
  status)
- Link source (Zillow, Redfin, Google Maps embed, etc.)
- **Extract lat/lon from Google Maps embed link if provided** → queue for Step 2D

### STEP 2 — Hard-Stop Regulatory Screen

Check these in order. If a hard stop fires, label **only the affected track** DISQUALIFIED and
continue evaluating the remaining tracks.

#### 2A. Highlands Designation
- Use NJ GeoWeb Highlands layer or Highlands Council Interactive Map
- **Preservation Area = HARD STOP on Track A (plaza).** Severely limits residential. Note HDC
  (Highlands Development Credit) transfer path if relevant.
- **Preservation Area is NOT automatically a Track B hard stop** — agriculture is generally a
  continuing permitted activity in the Highlands, and the Highlands Act contains agricultural
  exemptions. Flag as 🟠 MAJOR RISK and verify with the Highlands Council before relying on it.
- Planning Area = workable for all tracks. Proceed.
- Outside Highlands = clear. Proceed.
- Tool: https://www.highlands.state.nj.us/njhighlands/maps/ and NJ GeoWeb parcel-level lookup
- Key note: Township-level designation is insufficient — must verify at parcel level.

#### 2B. Pinelands Designation
- Pinelands Forest Area or Preservation Area = retail prohibited = **HARD STOP on Track A**
- Pinelands has its own agricultural rules administered by the Pinelands Commission, separate from
  Right to Farm. **Do not assume Track B works in the Pinelands** — flag 🟠 and verify directly with
  the Commission.
- Growth Area or Rural Development Area = workable.
- Tool: NJ Pinelands Commission GIS

#### 2C. Zoning Compatibility — NOW EVALUATED PER TRACK

**Track A (Plaza) — acceptable zoning** (by right or with minor variance): C-1, C-2, Village
Business, Highway Commercial, General Commercial, Mixed Use, B-1, B-2, Highway Business, or any zone
permitting retail as a permitted or conditional use.

- Agricultural-only (AR, A-R, AG, FP, FPD), residential-only (R-1 through R-5), or conservation
  zones = **HARD STOP for Track A.**
- Flag if zoning would require a **use variance (d-variance)** — this needs 5 of 7 zoning board votes
  plus proof of both positive and negative criteria. Multi-year, five-figure legal fees, no
  guarantee. **Never recommend buying land on the assumption a d-variance will be won.**
- A bulk/dimensional variance (setback, coverage) is a much easier path — distinguish clearly.

**Track B (Farm Market) — the gate is different.** Go to **Step 4D**. The zoning question for
Track B is not "does this zone permit retail" — it is **"does this zone permit agriculture."**

#### 2D. Wetlands — 40% Rule ⚡ RUN FROM COORDINATES FIRST
- **PRIMARY METHOD: Extract lat/lon from Google Maps embed link → run Python query against
  `Wetlands_(2020).shp` (loaded locally)**
- Fallback tools (if no coordinates available): NJDEP e-LOI viewer at
  https://experience.arcgis.com/experience/c77c09b36a694d3a9e875c238eb72ac0
- Supplement with NWI (National Wetlands Inventory) freshwater wetlands overlay — e-LOI absence ≠ no
  wetlands
- **If mapped wetlands exceed 40% of gross acreage = HARD STOP ALL TRACKS**
- **If parcel center is INSIDE a wetland polygon = HARD STOP ALL TRACKS** (no acreage calc needed)
- Estimate net buildable acres = gross acres × (1 − wetland fraction)
- Calculate cost per buildable acre
- **Track B note:** greenhouses need less land than a plaza but still need dry, gradeable ground with
  vehicle access. Wetlands do not become acceptable because the use is agricultural.

#### 2E. FEMA Flood Zone
- Check FEMA MSC for FIRM panel: https://msc.fema.gov
- Zone AE (100-yr floodplain) on significant acreage = major constraint
- Floodway = building prohibited — **hard stop all tracks**
- Zone X = clear
- Note: FPD zoning designation often signals underlying flood plain exposure

#### 2F. Contamination / CEA Check ⚡ RUN FROM COORDINATES
- **PRIMARY METHOD: Run local Python connector against `NJ_Groundwater_CEA.geojson`
  (6,763 zones statewide)**
- Script: `C:\Users\hadid\groundtruth\cea_connector.py`
- Data: `C:\Users\hadid\groundtruth\data\NJ_Groundwater_CEA.geojson`
- Command: `python C:\Users\hadid\groundtruth\cea_connector.py <lat> <lon>`

**Hard stop triggers (ALL TRACKS):**
- Point INSIDE any CEA zone → automatic disqualification (no clean well permit, septic issues, title
  clouds)
- Active remediation = Yes → financing/title risk, flag immediately
- **Track B carries EXTRA contamination weight** — you would be growing food and medicinal herbs for
  sale. Contaminated groundwater is worse for a farm market than for a strip mall. Treat any CEA hit
  within 0.5 mi as 🔴, not 🟠, when Track B is the leading track.

**1-mile proximity flags (report top 5 nearest):**
- List site name, distance in miles, municipality, contaminants present
- Upgradient CEA zones (check `GW_FLOW` field) are higher risk than downgradient

**Key fields to report:** `CEA_NAME`, `ACTIVE_REMEDIATION`, `GW_CLASS` (II-A = drinking water
source), `DEPTH`, `PROGRAM` (VIC/LSRP/UST), `PFAS / TCE / BENZENE / HISTORIC_FILL`

**Output block to include in every report:**

```
CEA CONTAMINATION QUERY:
  Point inside CEA zone: YES [HARD STOP] / NO
  CEA zones within 1 mile: X found / None
  Nearest zone: [name] — [X.XX mi] — [municipality]
  Contaminants: [list]
  Active Remediation: Yes/No
  Verdict: HARD STOP / PROXIMITY FLAG / CLEAN
```

- Fallback tool: NJ GeoWeb CEA layer at njgin.nj.gov if script unavailable

### STEP 3 — Environmental Deep Dive (if parcel passes Step 2 on any track)

#### 3A. Soils Assessment
- Use USDA Web Soil Survey (websoilsurvey.sc.egov.usda.gov)
- County SSURGO data on hand: NJ041 (Warren), NJ037 (Sussex), NJ027 (Morris)
- Key outputs: hydric soil %, drainage class, buildability rating
- Hydric soils correlate strongly with wetlands; high hydric % = flag
- **For Track B this is not a side-note, it is central.** Report prime farmland designation, drainage
  class, and pH suitability explicitly. A parcel that is merely buildable is not automatically
  farmable.

#### 3B. Topography and Slope
- Steep slopes (>15%) limit building envelope
- **Track B: greenhouses want flat.** Slopes over ~5% mean grading cost. Report the flattest
  contiguous area in acres, not just the average slope.
- Note any ridgeline or hilltop positions that create privacy and views (lifestyle positive)

#### 3C. Stream / Water Features
- Stream bisecting parcel = C1 or C2 stream buffer setback (300 ft or 50 ft respectively from top of
  bank)
- A stream through the center effectively splits usable acreage
- **Track B: a stream is not only a constraint.** Note surface water availability for irrigation, but
  do not assume a right to draw from it — NJDEP water allocation rules apply above threshold volumes.

#### 3D. Net Buildable Acre Calculation
Net buildable = Gross acres − wetland acres − floodway acres − steep slope acres (>25%)
Express as: "X.XX net buildable acres out of Y.YY gross acres (ZZ%)"
Express asking price as cost-per-buildable-acre.

### STEP 4 — Zoning & Use Analysis

#### 4A. Track A — Plaza Viability
- Confirm permitted uses: retail, office, food service, commercial greenhouse, agricultural
  processing
- Lot coverage, impervious surface limits
- Setbacks: front, side, rear
- Minimum lot size for commercial use
- Parking requirements
- Frontage: minimum required vs. available (flag if <150 ft for plaza layout)
- Site plan approval vs. use variance path
- Contact: municipal zoning officer before making offer

#### 4B. Greenhouse / Herb / Oil Extraction
- Agricultural use permitted outright? Or requires conditional use permit?
- Commercial extraction/processing — check if manufacturing use classification applies. **Extraction
  and processing are where Right to Farm protection gets thin** — growing and selling is clearly
  protected; industrial-scale solvent extraction may be treated as manufacturing. Flag it.
- NJDEP air permit may be required for solvent-based extraction
- Water well permitting for irrigation scale
- This is the "grow" component of the live/grow/sell vision

#### 4C. Track C — Residential / Family Compound
- Permitted dwelling units
- Accessory dwelling unit (ADU) rules
- Multi-generational / compound-style layout feasibility
- Modular construction permitted? (Preferred for ~25–26% cost savings vs. site-built)
- Septic vs. sewer availability

#### 4D. ⚡ Track B — FARM MARKET QUALIFICATION (new in v2.0.0)

**Plain-language summary of this step:** *We are checking whether this parcel can legally host a shop
that sells what we grow, without asking the town's permission. Three things must be true: the town
must allow farming here, the operation must be big enough to count as a real farm, and the shop must
sell mostly our own produce.*

Run these four gates **in order**. Gate 1 is the one that kills deals — check it first.

**GATE 1 — Locational eligibility. ⚠️ THIS IS THE REAL GATE.**

Right to Farm protection under **N.J.S.A. 4:1C-9** applies only to commercial farms located in areas
where, **as of December 31, 1997 or thereafter, agriculture is a permitted use under the municipal
zoning ordinance and is consistent with the municipal master plan** — or which were in operation as
of the effective date of P.L.1998, c.48.

- Read the municipality's zoning ordinance for the parcel's zone. Is agriculture / farming / a farm
  permitted, by right or as a conditional use?
- Most NJ rural residential zones (R-3, R-5, and similar large-lot zones) **do** permit agriculture.
  Do not assume — read it.
- If agriculture is **not** a permitted use in this zone → **Track B HARD STOP.** Right to Farm gives
  you nothing here, and you are back to a d-variance.
- Report the ordinance section number you relied on. Do not assert this from memory.

**GATE 2 — Commercial farm status (N.J.S.A. 4:1C-3).**

The operation must qualify as a "commercial farm":

| Farm size | Annual production value required |
|---|---|
| **5 acres or more** | **$2,500 or more** |
| **Less than 5 acres** | **$50,000 or more** |
| Beekeeping operation | $10,000 or more |

In all cases the unit must also satisfy the eligibility criteria for **farmland assessment** under
the Farmland Assessment Act of 1964.

- **Under 5 acres the bar jumps 20×.** This makes **acreage strategically important for Track B**:
  at 5+ acres the production hurdle is trivially low ($2,500/yr); below 5 acres it is a real
  business. **Strongly prefer parcels of 5+ acres for Track B.**
- A parcel already carrying **3B / QFARM farmland assessment is most of the way there** — it is
  already assessed as actively devoted agricultural land. Flag this as a significant Track B
  positive, and net it against the rollback tax liability.
- Confirm the specific farmland-assessment gross-sales and acreage thresholds with the county tax
  assessor before relying on them — do not state them from memory.

**GATE 3 — Farm market rules (N.J.A.C. 2:76-2A.13).**

A "farm market" is a facility for wholesale or retail marketing of the agricultural output of a
commercial farm, plus products that contribute to farm income. For **retail**:

- **At least 51% of annual gross retail sales** must be the commercial farm's own agricultural
  output, **OR at least 51% of the sales area** must be devoted to the farm's own output; and
- if the farm market is on **land less than five acres**, that land must produce **at least $2,500/yr**
  of agricultural or horticultural product.

**What this means for the business model:** up to 49% of the shop can be bought-in goods — pottery,
candles, local honey, packaged food, garden supply. That is the margin business. The greenhouse is
what makes the shop legal.

**What it does not permit:** leasing units to unrelated retail tenants. A pizza shop, a nail salon,
or a dry cleaner in the building is not farm output and is not protected. **If the vision is tenants
paying rent, that is Track A and it needs commercial zoning.**

**GATE 4 — Get it in writing before you buy.**

- The forum is the **County Agriculture Development Board (CADB)** for the county the parcel sits in
  (the SADC acts where no CADB exists).
- The instrument is a **Site-Specific Agricultural Management Practice (SSAMP)** determination — you
  can ask the CADB to rule in advance that your specific planned operation is a protected
  agricultural practice.
- **Recommend pursuing an SSAMP determination as a contract contingency, not after closing.**
- Operation must conform to the agricultural management practices adopted by the SADC.

**Track B output block — include in every report where Track B is live:**

```
FARM MARKET TRACK (Right to Farm):
  Gate 1 — Agriculture permitted in zone: YES / NO / UNVERIFIED  [ordinance § ______ ]
  Gate 2 — Commercial farm threshold: 5+ ac → $2,500/yr  |  <5 ac → $50,000/yr
           Parcel acreage: ____ ac  → applicable threshold: $______/yr
           Currently farmland assessed (3B/QFARM): YES / NO
  Gate 3 — Farm market 51% own-output test: ACHIEVABLE / MARGINAL / NOT ACHIEVABLE
  Gate 4 — CADB / SSAMP path: [county board name] — pre-purchase determination recommended
  Verdict: TRACK B VIABLE / CONDITIONAL / HARD STOP
```

### STEP 5 — Lifestyle Track Assessment

#### 5A. Schools
- Identify sending school district
- Elementary, middle, and high school ratings from Niche.com and GreatSchools
- NJ DOE School Performance Report (also the authoritative charter school list)
- Rating threshold: ≥7/10 elementary, ≥6/10 high school preferred
- Flag any school under 5/10 as a lifestyle negative
- Note nearest charter school options and whether the district is a choice district

#### 5B. Privacy and Setting
- Road type (county highway, township road, cul-de-sac, private lane)
- Adjacent land uses (farms, woods, residential, commercial)
- Visibility from road
- Lot shape — deep lots with road frontage at the narrow end = maximum privacy
- **Track B tension:** privacy and retail visibility are opposites. A farm market needs people to
  find it. If Track B is the leading track, road frontage and traffic count become positives, not
  negatives. Call this trade-off out explicitly when both B and C are live.

#### 5C. Appreciation Factors
- Recent comp sales in area
- Township growth trajectory
- Infrastructure investment signals (water/sewer extensions, road improvements)
- Proximity to employment centers

#### 5D. Commute
- Drive time to major employment hubs (NYC, Newark, Morristown, Trenton)
- Nearest NJ Transit access

### STEP 6 — Financial Summary

- Asking price
- Price per gross acre
- Price per net buildable acre
- Estimated rollback tax liability (if farmland-assessed)
- **If Track B is pursued: note that maintaining farmland assessment avoids the rollback entirely** —
  you are continuing the agricultural use, not converting it. This can be worth $30–100K+ and is a
  material Track B advantage over Track A.
- Rough site prep budget range (clearing, well, septic, utilities)
- Modular build estimate at 4,000 SF farmhouse scale (~$400–450K modular vs. ~$550–600K site-built)
- Commercial development budget placeholder
- **Track B build placeholder:** greenhouse structure + farm market retail space + well/irrigation.
  Budget separately from the residence.

### STEP 7 — Strategy Notes

Address the specific vision components:

- **Retail plaza (3–4 stores)**: Can a courtyard or hidden-gem plaza layout work given frontage
  constraints? Track A only.
- **Commercial greenhouse**: Footprint requirements, growing season extension, HVAC/energy
  infrastructure
- **Farm market**: Where does the shop sit relative to the greenhouse and the road? Parking? Is the
  51% own-output test comfortable or marginal at the planned scale?
- **Herb oil infusion/extraction**: Processing facility siting, regulatory pathway, whether it
  escapes Right to Farm protection into manufacturing
- **Family compound**: House placement, outbuildings, privacy screening, guest quarters
- **Phased capital deployment**: Buy land → build greenhouse → open farm market → use income to
  self-fund residential phase

**The split strategy, restated for v2.0.0:** the plaza and the grow do not have to be on the same
parcel, and after v2.0.0 they probably should not be. Commercial-zoned frontage land is expensive;
agricultural land with a Right to Farm market is cheap. **Buy C-zoned land for the plaza. Buy
ag/R-zoned land for the greenhouse and the farm market.** Two parcels, two price points, two
regulatory paths, one business.

---

## Output Format

### Header Block

```
ADDRESS: [Full address]
BLOCK/LOT: [Block XX, Lot XX]
COUNTY: [County]
ACREAGE: [X.XX gross / X.XX net buildable estimated]
ASKING: $[XXX,XXX] ($[XX,XXX]/buildable acre)
ZONING: [District code — District name]
COORDINATES: [lat, lon] (source: Google Maps embed / right-click / estimated)
```

### Verdict Line (one sentence, bold)

**TRACK A PLAZA: [VIABLE / CONDITIONAL / DISQUALIFIED] | TRACK B FARM MARKET: [VIABLE / CONDITIONAL /
DISQUALIFIED] | TRACK C LIFESTYLE: [STRONG / MODERATE / WEAK / DISQUALIFIED]**

### Red Flag Tiers

🔴 **HARD STOPS** — Deal killers. State which track(s) they kill.
🟠 **MAJOR RISKS** — Require verification before proceeding; could be deal-killers
🟡 **WATCH ITEMS** — Material but manageable with proper diligence

List each flag on its own line. Be specific — cite the constraint, what it means, which track it
affects, and what verification step resolves it.

### Wetlands Quick-Result Block (always include)

```
WETLANDS QUERY (Wetlands_2020.shp):
  Center point inside wetland polygon: YES / NO
  Nearest wetland edge: XXX ft
  Nearest wetland type: [LABEL20]
  Nearest wetland size: X.XX acres
  Wetland coverage estimate: X.XX ac / XX% (method: point buffer / parcel polygon)
  Verdict: HARD STOP / CLOSE CALL (need boundary) / CLEAN
```

### Composite Score (100 points) — REWEIGHTED IN v2.0.0

| Category | Weight | Score | Notes |
|---|---|---|---|
| Location & access (road frontage, traffic if Track B) | 15 | X/15 | |
| Acreage & price leverage | 15 | X/15 | |
| **Best commercial path** (Track A *or* Track B, whichever scores higher) | 20 | X/20 | |
| Environmental risk | 20 | X/20 | |
| Utilities & infrastructure | 10 | X/10 | |
| Schools (lifestyle) | 10 | X/10 | |
| Privacy & setting | 5 | X/5 | |
| Permitting runway | 5 | X/5 | |
| **TOTAL** | **100** | **XX/100** | |

**Best commercial path rubric (20 pts):**

| Situation | Points |
|---|---|
| Commercial zoning, retail by right (Track A clean) | 18–20 |
| Commercial zoning, conditional use or bulk variance only | 14–17 |
| Ag/R zoning, agriculture permitted, 5+ acres, farmland assessed (Track B clean) | 13–16 |
| Ag/R zoning, agriculture permitted, under 5 acres ($50K hurdle) | 7–10 |
| Ag/R zoning, agriculture permitted status unverified | 5–8 (and flag 🟠) |
| Agriculture NOT permitted in zone, retail not permitted — d-variance only path | 0–3 |

Threshold: **70+ warrants deeper investigation.** Below 60 = pass unless a lifestyle-only or
Track-B-only reframe changes the calculus.

### Outstanding Verification Items

Numbered checklist of items that must be confirmed before any offer or phone call:
1. [Item] → [Tool/contact to resolve it]
2. ...

### Recommended Next Step

One sentence: what Farid should do next with this parcel.

---

## Key Reference Data (always apply)

**Hard-Stop Rules — v2.0.0:**

*All tracks:*
- Wetlands >40% of gross acreage
- Parcel center INSIDE a wetland polygon
- Point inside a CEA contamination zone
- FEMA floodway on the buildable area

*Track A (plaza) only:*
- Highlands Preservation Area
- Pinelands Forest / Preservation Area
- AR / A-R / AG / FP / FPD zoning
- R-1 through R-5 zoning
- Retail not permitted and only a d-variance available

*Track B (farm market) only:*
- Agriculture NOT a permitted use in the zone (N.J.S.A. 4:1C-9 locational gate)
- Under 5 acres AND cannot credibly reach $50,000/yr production
- Pinelands Forest/Preservation until the Pinelands Commission confirms otherwise

**Right to Farm reference:**
- Statute: N.J.S.A. 4:1C-1 et seq. — commercial farm definition at 4:1C-3, protections at 4:1C-9
- Farm market / direct marketing rule: N.J.A.C. 2:76-2A.13
- Commercial farm thresholds: 5+ ac → $2,500/yr · <5 ac → $50,000/yr · beekeeping → $10,000/yr,
  each plus farmland assessment eligibility
- Farm market retail test: ≥51% of gross retail sales **or** ≥51% of sales area from own output;
  market on <5 ac → land must produce ≥$2,500/yr
- Locational gate: agriculture permitted under municipal zoning as of 31 Dec 1997 or thereafter, and
  consistent with the master plan
- Forum: County Agriculture Development Board (CADB); SADC where no CADB exists
- Instrument: Site-Specific Agricultural Management Practice (SSAMP) determination — pursue
  pre-purchase as a contract contingency
- SADC: https://www.nj.gov/agriculture/sadc/ · Rutgers plain-English overview: FS1253

**Wetlands Shapefile (loaded locally — PRIMARY TOOL):**
- Path: `/tmp/wetlands_data/Wetlands_(2020).shp`
- CRS: EPSG:3424 (NJ State Plane, US Survey Feet)
- Records: 159,056 polygons statewide
- Source: NJDEP 2020 Land Use/Land Cover
- Key fields: LABEL20 (wetland type), ACRES, TYPE20, STATUS
- Note: This file replaces the need for the e-LOI live web viewer for most analyses

**Google Maps Embed Coordinate Extraction:**
- From iframe src URL: `!2d[LONGITUDE]!3d[LATITUDE]`
- Ask Farid to: Google Maps → search address → Share → Embed a map → copy iframe → paste here
- Alternative: right-click map pin → "What's here?" → copy lat/lon

**NJ Regulatory Links:**
- FEMA MSC: https://msc.fema.gov
- Highlands Map: https://www.highlands.state.nj.us/njhighlands/maps/
- NJ GeoWeb: https://njgin.nj.gov/njgin/
- NJGIN Municipal Zoning (NJDCA) layer: njogis-newjersey.opendata.arcgis.com
- New Jersey Zoning Atlas (564 jurisdictions, uniform categories): https://www.zoningatlas.org/new-jersey
- NJ DOE School Performance Reports (incl. charter list): rc.doe.state.nj.us
- USDA Web Soil Survey: https://websoilsurvey.sc.egov.usda.gov
- e-LOI Fallback Viewer: https://experience.arcgis.com/experience/c77c09b36a694d3a9e875c238eb72ac0

**Parcel Boundary Download:**
- NJGIN statewide: "Parcels and MOD-IV Composite of NJ" — all 21 counties, 2024 tax-year MOD-IV
- Warren County GIS Hub: warrencountynj.gov/government/planning-department/data-and-mapping
- Format: GeoJSON or Shapefile → upload to chat → run exact polygon intersection

**CEA Groundwater Contamination Data (loaded locally — PRIMARY TOOL):**
- Path: `C:\Users\hadid\groundtruth\data\NJ_Groundwater_CEA.geojson`
- Script: `C:\Users\hadid\groundtruth\cea_connector.py`
- Records: 6,763 NJ contamination zones statewide
- Source: NJDEP Site Remediation Program
- Key fields: CEA_NAME, ACTIVE_REMEDIATION, GW_CLASS, DEPTH, PROGRAM, contaminant flags
- CRS: WGS84 (EPSG:4326) — query directly with lat/lon, no projection needed
- Note: Centroid-based proximity (not exact polygon edge) — flag anything within 0.5 mi for boundary
  confirmation

**SSURGO County Files On Hand:**
- NJ041 = Warren County · NJ037 = Sussex County · NJ027 = Morris County

**Key Contacts:**
- Jim Onembo, Franklin Twp Warren Zoning: 908-689-5721 / zoning@franklintwpwarren.org
- Andrew Coccio, Wantage Land Use: 973-875-7195 ext. 7
- CADB contacts to add per county as Track B parcels come up

**Active Candidates (do not re-evaluate, reference only):**
- **0 Half Way House Rd, Franklin Twp, Warren Co** — 6.42 ac listed / 6.67 ac GDB, C-1, $100K
  ($15,576/gross ac), **0% wetlands GIS-confirmed**, scored 71–74/100. Pending: Highlands
  parcel-level check, FEMA panel. Wetlands nearest edge 820+ ft. **Track A lead candidate.**
- **0 CR 651, Wantage, Sussex Co** — 12.08 ac listed / 9.96 ac GDB, R-5, $59K ($4,884/gross ac),
  12.6% wetlands, outside Highlands entirely, 3B farmland assessed, $41.34/yr tax.
  **⚡ RE-SCORE UNDER TRACK B — top priority.** 9.96 ac clears the 5-acre threshold, so the
  commercial farm hurdle is only $2,500/yr. Verify Wantage zoning permits agriculture in R-5.

**Passed/Disqualified — v1 dispositions, with v2 re-score flags:**

| Parcel | v1 reason | v2 status |
|---|---|---|
| 312 Mountain Lake Rd, Liberty (30.94 ac, AR, 0% wetlands) | Highlands Preservation | ⚡ **Re-score Track B** — 31 clean acres, ag is the permitted use |
| 328 Hackett Rd, Bethlehem (14.03 ac, AG, 0% wetlands) | Highlands Preservation + 167% tax increase | ⚡ **Re-score Track B** |
| 1221 Rt 94, Frelinghuysen (AR-6) | Stream bisect + AR zoning | ⚡ Re-check Track B, but 34% wetlands + C1 buffer still severe |
| 782 Uniontown, Lopatcong (R-5/2, 0% wetlands) | Highlands Preservation | ⚡ Re-check Track B — only 5.8 ac, verify ag permitted |
| 28 W Springtown, Long Valley (lifestyle 93/100) | Highlands Preservation | Lifestyle-only. Not actively pursued |
| 500 Rt 94, Fredon (R-1, 7.4% wetlands) | Lifestyle-only, FSA loan noted | Unchanged |
| 143 Vail Rd, Knowlton | 57.9% wetlands + Highlands + ag-only | ❌ Stays dead — environmental |
| Cardinal Ln, Voorhees | 45% wetlands | ❌ Stays dead — environmental |
| 22 Estell Dr, Hardyston | Centre INSIDE 19.09-ac wetland | ❌ Stays dead — environmental |
| 36 Countryside Rd, Knowlton | FPD + seller-disclosed wetlands | ❌ Stays dead |
| 00-1 Clinton, West Milford | 100% Highlands + 81% FEMA floodway | ❌ Stays dead |
| Lot 8.03 Sunrise Ct, Medford | Pinelands Forest, 34.8% wetlands | ❌ Stays dead |
| 235/239 Rt 72, Barnegat | Pinelands Forest | ❌ Stays dead |
| 180 Black Brook, Bethlehem | Under contract | Gone |
| 102 US Hwy 46, Independence | Highlands Preservation | Re-check Track B if it returns to market |
| 44 Shongum, Denville | C1 stream buffer | ❌ Stays dead |

**Financial Benchmarks:**
- Modular construction: ~25–26% savings vs. site-built
- 4,000 SF farmhouse modular: ~$400–450K
- Commercial site prep (well, septic, clearing, utilities): $80–150K range depending on site

---

## Execution Notes

- **Extract Google Maps embed coordinates FIRST** — run wetlands query before opening Zillow or doing
  any other research. A wetland hard stop takes 10 seconds and saves everything else.
- **Run the environmental screen before the zoning screen.** Environmental hard stops kill all three
  tracks; zoning only kills one.
- **Never write off a parcel on zoning alone any more.** If the zone blocks retail, run Step 4D
  before declaring it commercially dead. That is the whole point of v2.0.0.
- **Never assume Right to Farm without reading the ordinance.** Gate 1 is where Track B deals die,
  and it is a question of fact, not of memory. Cite the ordinance section.
- **Always search Zillow/Redfin link** to pull acreage, price, listing photos, and agent notes.
  Remember no single site is complete — Zillow carries far fewer NJ land listings than Land.com or
  LandSearch. Check more than one.
- **Web search the address** to find block/lot if not provided.
- **Bottom line first**: lead every section with the verdict, then the evidence.
- **Don't call the listing agent until all regulatory checks are done** — that's the rule.
- Flag farmland-assessed parcels immediately — rollback tax can be $30–100K+ at acquisition on
  Track A, and is **avoided entirely** if Track B continues the agricultural use. Model both.
- **For close-call wetland parcels** (nearest edge 100–500 ft): 6-acre parcels with narrow frontage
  can extend 2,800+ ft deep — always flag geometry risk and request the boundary polygon before
  calling it clean.

---

## Version History

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-23 | Initial skill. Two tracks: Commercial, Lifestyle. Wetlands shapefile and CEA connector integrated. |
| **2.0.0** | **2026-09-16** | **Farm Market Track added (Right to Farm Act). Zoning hard stops now per-track rather than global. Composite score category 3 reweighted to "best commercial path" with rubric. Environmental hard stops unchanged and explicitly marked all-track. Re-score flags added for 5 previously-passed parcels.** |
