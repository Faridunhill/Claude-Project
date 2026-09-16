# Claude-Project — working rules

## Read this before answering anything about the Farm House / GroundTruth project

**`docs/farmhouse/GROUND-TRUTH_2026-09-15_builder-pc-audit.md` is the core reference.**
It is the Builder's direct audit of Farid's PC, measured on the machine on 2026-09-15.

**Precedence.** Where it disagrees with a Drive file, an older document, or a previous answer,
**the audit wins.** Drive holds knowledge; the PC holds the running system. When the two conflict,
the machine is right.

### Facts that are settled — do not re-derive them from Drive

| Fact | Value | Source |
|---|---|---|
| FarmlandAdvisor | **CERTIFIED, 83.6 avg, 189 sessions** — highest-scoring agent in FaridOS | `farid_os.db`, 2026-09-15T21:27 |
| NJLandScout | **CADET, 69.5 avg, 1,014 sessions**, model mistral-nemo, curriculum v1.2.2 | same |
| PipeEncyclopedia | TRAINED, 77.4 avg, 390 sessions | same |
| The "100+ farm analyses" | **Do not exist on the PC.** 18 parcels are written down. Farmland tables have **0 rows** | filesystem + DB search |
| Zillow data feed | **Closed.** Public API retired 30 Sep 2021; Bridge is broker-gated | §4 of the audit |
| Whole NJ land market | ~3,000–4,000 lots for sale (LandWatch 3,742 · LandSearch 2,721) | §4 |
| Live site domain | **groundtruthpropertyai.com** — property *then* ai. Farid sometimes types it reversed | §7 note |

**`TRAINER_STATUS.md` in Drive (v1.5.0, 2026-06-26) is stale and must not be quoted.**
It says both land agents are UNRANKED with zero sessions. That has been false since roughly July.

### The design brief, in his words

> *"I stopped this website because I didn't trust that we can afford neat and accurate."*

The honesty gate is not a feature of this product. It is the reason he stopped building it. Never
present an estimate as a measurement, never fill a blank with a plausible number, and always say
which checks did not run.

### Project files

| File | What it is |
|---|---|
| `docs/farmhouse/GROUND-TRUTH_2026-09-15_builder-pc-audit.md` | Core reference. Precedence over everything. |
| `docs/nj-farmhouse-parcel-evaluation_SKILL_v2.md` | The evaluation method. Three tracks: plaza, farm market, lifestyle. |
| `docs/farmhouse-nj-land-search-research.md` | Data-source and capability research. Carries a correction banner. |
| `tools/nj_screener/` | Statewide land screener and map. |

### Standing rules for this project

1. **Environmental hard stops are absolute** — wetlands over 40%, parcel centre inside a wetland,
   inside a CEA contamination zone, FEMA floodway. They kill all three tracks. Never soften them.
2. **Zoning hard stops are per-track.** R and AR block a plaza; they do not block a farm market
   where agriculture is a permitted use. That is skill v2.0.0 and it is deliberate.
3. **Never assume Right to Farm protection without reading the ordinance.** Gate 1 — agriculture
   permitted in the zone as of 31 Dec 1997 or later — is a question of fact, cited by section number.
4. **A missing data layer is skipped, not passed.** Say so in the output.
5. **No scraping.** LandWatch/LandSearch/Land.com scrapers exist and are cheap; they breach those
   sites' terms. Name the option, do not take it.
6. **Parcel data tells you who owns land, never that it is for sale.** Do not blur the two.
