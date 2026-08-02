# ★ FARIDOS PATHS — where things actually are on Farid's PC
Established 2026-07-31 from a PowerShell search Farid ran and screenshotted.
**Read this before asking Farid where anything is.** A prior session burned 13 minutes
re-discovering a location that was already known; this file exists so that stops.

The cloud side cannot see any of these. A **local** session must act on them.

---

## THE CABINETS — settled
```
C:\Users\hadid\FaridOS\agents\dating\cabinets\
```
- **58 cabinets** (counted 2026-07-31, `.json` files). Format is **JSON**, not YAML.
- This supersedes every earlier count: `CLAUDE.md` says "55+ brand cabinets", channel doc
  002 says "the 56 cabinet JSONs". **The real number is 58.**
- The cloud repo holds exactly **one** cabinet — `dating/cabinets/peterson.yaml`, a YAML
  copy on a branch. Everything else is here, on the PC, and has never been in the cloud.
- Verified working: the Episode Engine read the Peterson copy and harvested 25 teachable
  dating facts with sources, refusing 18 that identify but cannot date.

## ★ THE HUB — the fact that unblocks the Marketing Monster
```
C:\Users\hadid\FaridOS\data\hub\pipes\
```
**This was THE blocker.** `marketing_monster/README.md` states it exactly:

> *"What is still blocked — Wave 2 only: the location of the hub and cabinet data. That
> is a fact about Farid's PC, not a decision — the cloud side cannot look. Once a path
> exists, `inspect` → `load` is a two-minute job and the pipes dig starts."*

The path now exists. **A local session can run wave 2** (branch
`claude/marketing-agent-eval-yzxetu`, 900 lines pure-stdlib Python, 26 passing tests):

```bash
export PYTHONPATH=/path/to/marketing_monster
python -m monster init    pipes
python -m monster inspect pipes <export.csv>   # reads the HEADER ROW ONLY, writes nothing
python -m monster load    pipes <export.csv>
python -m monster report  pipes
python -m monster verify  pipes
```
`inspect` is the safe first move — it proposes a column mapping, prints what it would
drop, and exits without reading a single record.

## Known sub-paths under the hub
| Path | What it appears to be | Action |
|---|---|---|
| `data\hub\pipes\shape_reference\charts\` | Shape-reference charts per brand | **Useful — send.** Feeds dating |
| `data\hub\pipes\library\trust_engine\ledgers\` | Trust-engine ledgers per brand | Unknown purpose. Ask a local session before moving |
| `data\hub\pipes\staging\pipedia\` | Raw captured Pipedia content | **NEVER send to the cloud.** LAW 2 — derived facts yes, raw capture no |

## THE ARK — never travels
~19,180 files / **2.28 GB** of mirrors and scanned catalogues. Stays on the PC forever.
**Only its manifest travels** (`channel/NEW_UPLOADS/ark_manifest.csv`, 1.4 MB) — and it
already did: it generated the public `/references` page, 227 catalogued holdings.

## Size reality, so nobody calls the cabinets "huge data" again
| Thing | Size |
|---|---|
| One cabinet | ~36 KB |
| **All 58 cabinets** | **~2 MB — smaller than one phone photo** |
| The ark | 2.28 GB — never |

---
## STILL UNKNOWN — the next thing worth locating
**`ashcombe-co`** — the Etsy/eBay publishing module (deploy `ashcombe-co-production`,
AWS us-east-1). Farid's repository list confirms it is **not on GitHub**: the three cloud
repos are `faridunhill-live`, `Claude-Project`, `groundtruth-website`. So it lives on the
PC or in a non-GitHub deploy. **Finding it is what unblocks multi-channel publishing.**
Suggested search, same method that found the hub:
```powershell
Get-ChildItem C:\ -Recurse -Directory -Filter "*ashcombe*" -ErrorAction SilentlyContinue |
  Select-Object -First 5 FullName
```
