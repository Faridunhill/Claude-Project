# SESSION HANDOVER — 2026-08-02
### The Marketing Monster: evaluated, built, automated, running

**Read this first if you are a new session picking up the marketing work.**
Branch: `claude/marketing-agent-eval-yzxetu` · Code: `marketing_monster/` · Docs: `channel/TO_FARID/003–006`

---

## 1. WHAT THIS SESSION DID

Started as a technical evaluation of MIND's `MARKETING MONSTER v1.0` design. Ended with the thing
built, automated on two timers, and running on Farid's PC with eleven years of his real trading
inside it.

| Doc | What it is |
|---|---|
| **003** | The evaluation. Conditional pass, 6.6/10. Three blocking findings: B1 measurement contract, B2 evidence thresholds, B3 the wall. Plus M1–M5, N1–N4 |
| **004** | v1.2 build spec — MIND's ruling engineered. Machine-written ledgers; email capture as GroundTruth's proxy |
| **005** | Dossier 001 — pipe & cigar lighters. The outward Digger's first real dig |
| **006** | The full-automation design: two timers, git as the bridge |
| **007** | This handover |

---

## 2. WHAT IS RUNNING RIGHT NOW

**On Farid's PC** — Windows scheduled task `Marketing Monster`, **daily 08:00**:
`C:\Users\hadid\FaridOS\marketing\monster_daily.bat` → `monster auto pipes`
It pulls the repo, reads new export files, records sales, writes listings, digs, learns, reports.

**In the cloud** — Routine `trig_01NMEPYMJ5NgX6UwqU4XhUYw`, **Mondays 06:00 UTC**, fresh session.
Researches the approved category, writes a dossier to `channel/TO_FARID/`, commits, pushes.
**First fire: 2026-08-03.** Its brief: the open question from dossier 001 — **lighter suppliers
and margins**.

**The bridge is git.** Neither half waits for the other; neither waits for Farid.

### Paths on his machine
| | |
|---|---|
| Repo checkout | `C:\Users\hadid\Desktop\FARID_CLAUDE_CHANNEL` |
| Marketing root (ledgers) | `C:\Users\hadid\FaridOS\marketing` |
| Dashboard | double-click `MARKETING DASHBOARD.bat`, or `monster dashboard` |
| eBay history | `…\OneDrive\Desktop\FARID_CHANNEL\TO_ME\PRICE_DATA\ebay_sales_2015-2026_ANONYMISED.csv` |
| Etsy history | `…\FaridOS\data\hub\pipes\etsy_sold\sold_listings_manifest.jsonl` |

---

## 3. THE STATE OF THE WELL

**8,042 transactions · 2015 → 2026 · $501,072 recorded · median price $49**
eBay 5,697 · Etsy 2,345. No names, no emails, no addresses — derived features only (M4).

What the first dig found: **Peterson is the volume engine** (1,202 sales, median $95).
**Dunhill is the premium tail** (158, median $204). **Billiards are 1,925 sales at $40, −19%**;
freehands are 92 at $77, **+58%**. Strongest title signals within brand: **`english`** (597
listings, 11 brands, +30%) and **`9mm`** (1,398 listings, 10 brands, +21% — the German filter
standard, sitting directly on the Germany-route edge).

**5 lessons PROPOSED · 0 CONFIRMED.** Nothing is believed until it appears in two separate weeks.

---

## 4. DECISIONS FARID MADE (do not re-litigate these)

1. **eBay Promoted Listings is OPEN.** v1.0 said all paid channels were closed; three of five
   sales on 2026-08-01 came through it. Pipes now flags `paid_allowed`, scoped in code to
   **marketplace promotion only** — Meta and Google stay closed. Spend ceilings remain his.
2. **Publish order: faridunhill → Etsy → eBay by CSV.** His admin holds the listing and pushes
   Etsy automatically, so `publish --where admin` records both in one step.
3. **D-003 = DO** — pipe & cigar lighters, mid tier + consumables, as the **first test category**.
4. **Pipes only until one lesson is CONFIRMED**, then clone. Ratified by MIND and by him.

---

## 5. FIVE BUGS FARID CAUGHT, AND WHAT THEY BECAME

He found every one of these by knowing his own business. Each is now a test.

| What looked wrong | What it was |
|---|---|
| Loader refused his whole catalogue | The address detector fired on *"4 Star **Dr** Grabow"* — a pipe name, not a street |
| Autopilot crashed | eBay writes `Oct-21-25`, Etsy writes `2026-07-14`. Mixed formats sort and cohort wrongly rather than failing |
| **"72 sales" he never made** | 72 rows on one day with consecutive eBay item numbers — a bulk **listing** upload. Now quarantined from the Scale, kept in the Well |
| Report cried "DIGGER NOT STARTED" while digging | Judged by the wrong file — a written dig now counts as activity |
| Proposals promoted noise | Ranked by effect size, so +176% on 2 brands beat +30% on 11. Now ranked by evidence breadth |

**The lesson for the next session: when Farid says a number smells wrong, he is right. Go and
look.** He has been right every time.

---

## 6. WHAT IS OPEN

**Blocked only by time:**
- **The cookbook is empty.** No lesson has appeared twice yet. That is the rule working.
- **Kitchens 2 and 3** (GroundTruth, Ashcombe) are unbuilt, gated on that first CONFIRMED lesson.
  The clone itself is nearly free — one folder and one config; the machine is written once.

**Real work still to do:**
1. **54% of the catalogue matches no brand.** Every brand table is a report on a biased sample
   until that closes. The dig prints the unnamed words; feed the real house names back in.
2. **Suppliers and margins for lighters** — Monday's cloud run. Without margin, dossier 001 is
   interesting, not actionable.
3. **The twin backlog** runs 50 per day until it catches up. If it still says 50 in a week,
   something is wrong.
4. **Unsold stock is still partly invisible.** The listing desk fixes this going forward — every
   pipe listed through `monster new` starts a clock — but the historical active-listings report
   has not been loaded, and it is deliberately refused as a sales file.

---

## 7. THE LAWS THIS CODE ENFORCES

Not documentation — code that refuses. Each error names the finding it comes from.

`scale.py` no invented attribution (B1) · `playbook.py` no lesson confirmed on one cohort (B2) ·
`wall.py` no data crossing as a method (B3) · `judge.py` permanent reject memory (M2) ·
`digger.py` sources carry a permission basis and expire (M3) · `well.py` no personal data, ever
(M4) · `maker.py` nothing published unstamped (N1) · `report.py` blind spots before performance
(§2.3) · `listing.py` no price from fewer than five comparables ·
`well.py`/`dig.py` an active listing, an upload file and a bulk-listing day are not sales.

**88 tests.** Most were written from real failures on real data.

---

## 8. WHAT NEVER BECOMES AUTOMATIC

v1.0, unchanged and not up for revision:

> *"Farid alone holds: category picks, floor prices, spend ceilings, anything crossing a wall.
> Monster proposes; Farid disposes."*

Four questions. They arrive one line each in `PENDING.md` and on the dashboard, and a word
answers them. **This is the brake, not a gap.** It is what stops the machine spending money or
entering a category on its own.

---

## 9. IF YOU ARE THE NEXT SESSION

1. Read `CLAUDE.md`, then docs 003, 004, 006, then this.
2. Farid speaks plainly and English is not his first language — **read intent generously, answer
   in short sentences, and give commands he can paste**. When he says the same thing twice, he
   has already been right once.
3. Do not hand him files to carry. Both halves are automated; if you find yourself asking him to
   move something between cloud and PC, that is a bug in the design, not a task for him.
4. The dashboard is his front door now, not the command line.

---

*Written 2026-08-02 at Farid's request, to end this session and open the next one cleanly.*
