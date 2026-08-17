# COUNCIL REVIEW — THE WATCHER, THE FACE, THE HANDS (v0.1)
Reviewer: Encyclopedia Creator (Manager), cloud session | Date: 2026-08-17
Paper under review: `docs/WATCHER_FACE_HANDS_README_v0_1.md`
Status of everything here: **DESIGN. Nothing is authorized to build. Nothing was built.**

The paper's own instruction: *"an evaluation that scores this highly and restates it
in better language is not an evaluation. Find the twelve specific things that are
wrong with it."* Here are twelve.

---

## THE TWELVE FINDINGS

### 1. The "hard constraint" (§2) is a false either/or — Farid already owns an always-on half
The paper treats "local on the PC" and "always-on somewhere else, gains cost" as
opposites and picks the scheduled worker as a compromise. But the empire already
runs on two fronts (CLAUDE.md law): the PC, and **this cloud repo with scheduled
Claude sessions that run while the PC is off, at no new cost** — already paid for
inside the existing Claude subscription. The correct shape is not A, B, or C.
It is a **split by where the data lives**:
- **Cloud body** watches everything reachable over the internet: eBay, Etsy,
  faridunhill.com, Ashcombe. Runs on schedule whether the PC is on or not.
- **Local body** watches everything that exists only on the PC: the ledger, the
  cabinets, the ID system, the Academy, the project folders. Runs when the PC runs.
This dissolves spec 1's impossible wish ("work during my PC shut off") instead of
compromising on it. Answer to Open Question 1.

### 2. The §4.1 diagnosis is right but incomplete — half the feed already exists
"A Claude project cannot write to a local database" is true. But every cloud
Claude project **can** write to this repo, and the repo's **git history is already
the evidence feed** the paper wants: commit timestamps are exactly the
"file timestamp is a fact" principle (§4.3), readable by both bodies, submitted by
nobody. The projects section of the morning brief can be generated **today** from
`git log` — no new plumbing. The paper builds a feed it partly already has.

### 3. Open Question 2 (the Etsy/eBay feed) has a real answer, and it is not scraping
eBay and Etsy both have **official APIs** (eBay Sell/Fulfillment APIs; Etsy Open
API v3) that cleanly cover orders, shipping state, listings, and quantities —
three of the four money-checks, no scraping. The genuine gap: **Etsy's API does
not expose buyer conversations.** The universal fallback for messages is the
**notification e-mail inbox** — every store already e-mails "you have a message /
an order"; one inbox integration covers all three stores at once. So the "single
biggest technical unknown" is actually: two-thirds solved by official APIs,
one-third solved by reading e-mail. Scraping is the last resort, not the plan.

### 4. Qwen (or any local LLM) is the wrong tool for v1 — and the paper doesn't say so
The idea arrived from a Qwen headline, and the paper never closes the door. The
Watcher's morning round is **deterministic reading**: call an API, compare a
number to yesterday, read a file timestamp. That is a script, not a model. A
model is needed only for the one-paragraph summary at the end — and a small local
model that invents a fact hits the §10 trust-death ("wrong twice") fastest of all.
v1 is boring code on a schedule. The interesting creature comes later, on top of
a feed that works.

### 5. §9.3 names the fatal flaw ("reporting changes nothing") and then doesn't fix it
The fix is not the Hands. It is: **every report line carries a deep link to the
exact page where the action happens** — the eBay order page, the Etsy
conversation, the dead listing. "Three unshipped orders" is knowledge; "three
unshipped orders → tap → order page" is one thumb-press from done. Reduce the
cost of acting instead of granting write access.

### 6. Internal contradiction: §4.2.4 vs §4.2.6 — and it answers Open Question 5
"Report change, not state" (rule 4) and "report what has not moved in 30 days"
(rule 6) cannot both be rules, because the second **is** a state report. Resolve
it deliberately: **daily = change only; weekly = one full-state snapshot with
aging counters** ("encyclopedia profiles: 62 days without movement"). The weekly
state pass is also the answer to Open Question 5 — slow drift at 1% a week never
shows as a daily change, but an aging counter that only ever counts up cannot
hide it.

### 7. There is no "done" state — so the report will nag, and nagging kills it
An unshipped order reappears every morning until it ships. By day three the
report reads like scolding; by week two it stops being opened (§10.1). Report
items need **one-tap acknowledge** ("seen / handled"). Quiet consequence the
paper must admit: acknowledging means the Face *writes* — to its own small state
file. That is a controlled leak of Hands into Face. Name it and cap it: **the
Face may write only its own state, never a store.**

### 8. No heartbeat — a dead feed impersonates a quiet day
When a store token expires or an API call fails, the report silently gets
shorter. Silence is defined as good news (§4.2.4), so a broken feed **looks
exactly like health** — which is the paper's own worst failure, reporting
something untrue (§10.3). Mandatory: every report ends with **"sources read:
n/n"**, and a source that could not be read is itself a red item. This line is
missing from the design and it is the cheapest insurance in the whole system.

### 9. The build order (§3) violates the paper's own §5.1
§5.1: zero numbers make the most beautiful page feel like a demo. Then the
dashboard must not be built second. **v1 of the Face is the plain-text morning
message itself.** Build the designed dashboard only after two weeks of evidence
that Farid opens the report (the paper's own success test, §10.1). Spending
design effort before the read-habit is proven repeats the Helper mistake:
existence before value.

### 10. §5.4 ("a page on the PC does not reach an iPhone") is solved cheaper than stated
The cloud body already reaches the phone: a scheduled cloud session can deliver
the brief as a message in a place Farid already reads (the Claude app itself, or
a free Telegram bot — one evening of setup, push notifications included). No
hosting, no port-forwarding, no new infrastructure in v1. Delivery is a solved
problem the moment finding 1 is accepted.

### 11. Spec 2 ("improves itself") — answer to Open Question 4, with a hard limit
The Watcher and the ACADEMY stay **separate creatures sharing one memory**: every
Watcher miss ("report said X, the truth was Y") is logged to the Academy as a
mistake-record, and corrections to the Watcher are made *from* that record — by a
session Farid runs, not by the Watcher rewriting its own code. A self-modifying
watcher reaches "wrong twice, trust gone" (§10.3) faster, because its errors
change shape each time. Self-improvement = self-documentation, not self-surgery.

### 12. Farid's own request is Exhibit A for §9.4 — and the paper's decision must hold
The paper predicts "the pressure to let it just fix the quantity will be strong
and immediate," and the commissioning message proves it: spec 3 asks for store
edits, quantity changes, and customer control in the same breath as v1. The
decision **"no autonomous writes to any live store in v1"** is correct and must
survive contact with its own author. The leash stays: the Hands propose → Farid
approves from the phone → the Hands execute — and only after the Watcher has
been provably right for weeks.

**Remaining open questions, answered in passing:** Q1 → finding 1 (split, not
compromise). Q2 → finding 3. Q3 → 7:00 AM stands (it is the FaridOS design);
"urgent at 2 PM" belongs to the cloud body — an hourly *money-checks-only* pass
that pushes a message **only** above the existing escalation floor, otherwise
holds everything for morning. Q4 → finding 11. Q5 → finding 6.

---

## THE JOB DESCRIPTION (what Farid asked for)

### Position: THE WATCHER (v1) — Business State Reader
One job, two bodies, one report.

**Cloud body** — a scheduled Claude session in this repo. Works while the PC is
off. Watches everything on the internet.
**Local body** — a scheduled script on the PC (Task Scheduler, morning + on-boot).
Watches everything that lives only on the PC, and drops its digest into
`channel/` so the cloud body can fold it into the one brief.

**Duties, in priority order:**
1. **Stores first — the four money-checks** on eBay, Etsy, faridunhill.com,
   Ashcombe: orders unshipped or past handling time; buyer messages unanswered;
   listings ended or at zero quantity; account defects or policy notices.
2. **Website integrity checks** — permanent regression list, starting with:
   the /shop route serves OUR products (the incident that was found by accident
   becomes a check that can never be missed again).
3. **Projects — evidence only.** `git log` and file timestamps. Never asks a
   project to describe itself. *Status is a story; a timestamp is a fact.*
4. **Keeps the map** (spec 6 and 7): a registry of every project — name, purpose,
   one-line reason it exists, last observed movement — including the quiet ones:
   the Eye, the Judge, the 4,700 encyclopedia pipe profiles, the automated store
   module. Nothing is allowed to be forgotten, only deliberately paused.
5. **Reports:** daily brief, maximum 5 lines, change-only, every line a deep
   link; weekly full-state snapshot with aging counters; every report ends
   **"sources read: n/n"**. Silence on a quiet day is correct.
6. **Logs its own misses** to the Academy (finding 11). Never edits its own code.

**Explicitly NOT the job (v1):** touching any live listing, answering any buyer,
issuing any refund, changing its own code, building dashboards.

**Success:** Farid still opens the brief in week three.
**Dead:** the report needs manual input to exist; or it states something untrue
twice; or Farid stops opening it. (Unchanged from §10 — those tests are right.)

### Mapping Farid's seven specifications to this design
| # | Spec | Where it landed |
|---|---|---|
| 1 | Local on my PC | Split: local body for PC data, cloud body so it works with the PC off (finding 1) |
| 2 | Improves itself | Logs own misses to Academy; corrections by Farid-run session, never self-surgery (finding 11) |
| 3 | Edit the 3 stores | **v3 — the Hands**, on the propose→phone-approve→execute leash only (finding 12) |
| 4 | Study projects, suggest strategy | Weekly state report is the raw material; strategy stays with Farid + council sessions |
| 5 | Wake sleeping projects (4,700 profiles…) | Aging counters make every sleeping project visible weekly; waking them is separate, ordered work |
| 6 | Knows the system network | The registry — duty 4 |
| 7 | Reminds me of forgotten pieces | Aging counters + registry; nothing can go quiet unnoticed |

---

## RECOMMENDED FIRST STEP (when Farid says GO — not before)
Build the **local body's file-reader first**: it needs no API keys, no accounts,
touches nothing, and proves the whole loop (read evidence → write brief →
channel → phone) with zero risk. In parallel, Farid creates the eBay and Etsy
developer API keys — the only ingredient the cloud store-watcher waits on.
The dashboard waits for two weeks of opened briefs.
