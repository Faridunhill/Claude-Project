# COUNCIL OPINION — ON THE README "THE WATCHER, THE FACE, THE HANDS" (v0.1)

| | |
|---|---|
| **Paper under review** | `docs/WATCHER_FACE_HANDS_README_v0_1.md`, authored by **Mind** |
| **Council member** | The Creator — Encyclopedia Creator (Manager), cloud session |
| **Submitted to** | Farid, for the final decision. This is one opinion, not the ruling. |
| **Date** | 2026-08-17 |
| **Status** | DESIGN review only. Nothing is authorized to build; nothing was built. |

---

## VERDICT, IN ONE PARAGRAPH

Mind's paper is the best-structured design this problem has received: the
three-part split, "Watcher first / Hands last," "evidence, not self-report," and
"no autonomous store writes" are correct and should stand. But the paper accepts
a false constraint at its foundation (§2), leaves its own named fatal flaw
unfixed (§9.3), contradicts itself on change-versus-state, and has no defense
against a silently dead feed — the exact disease that killed the last three
agents. **My vote: approve the skeleton, amend it with the twelve findings
below, and build nothing until Farid rules.**

---

## WHAT STANDS (so the council does not re-litigate it)

Mind got these right, and this opinion keeps them all:
three parts, not one creature · Watcher before Face before Hands · evidence
over self-report ("status is a story; a timestamp is a fact") · stores rank
above projects · report change, not noise · no autonomous writes to any live
store in v1 · the three death-tests in §10.

---

## THE TWELVE FINDINGS

### 1. The "hard constraint" (§2) is a false either/or — Farid already owns an always-on half
Mind treats "local on the PC" and "always-on elsewhere, gains cost" as opposites
and settles for shape C. But the empire already runs on two fronts: the PC, and
**the cloud repo, where scheduled Claude sessions run while the PC is off, at no
new cost** — already inside the existing subscription. The correct shape is a
**split by where the data lives**:
- **Cloud body** — watches everything on the internet: eBay, Etsy,
  faridunhill.com, Ashcombe. Runs whether the PC is on or not.
- **Local body** — watches what exists only on the PC: the ledger, cabinets,
  ID system, Academy, project folders. Runs when the PC runs.
This dissolves the "work while my PC is shut off" requirement instead of
compromising on it. Answers Open Question 1.

### 2. The §4.1 diagnosis is right but incomplete — half the feed already exists
"A Claude project cannot write to a local database" is true. But every cloud
project **can** write to the repo, and the repo's **git history is already the
evidence feed** Mind is designing: commit timestamps are exactly the
"file timestamp is a fact" principle (§4.3), readable by both bodies, submitted
by nobody. The projects section of the brief can be generated **today** from
`git log`. The paper builds a feed it partly already has.

### 3. Open Question 2 (the Etsy/eBay feed) has a real answer, and it is not scraping
eBay and Etsy both offer **official APIs** (eBay Sell/Fulfillment APIs; Etsy
Open API v3) that cleanly cover orders, shipping state, listings, and
quantities — three of the four money-checks, no scraping layer. The genuine gap:
**Etsy's API does not expose buyer conversations.** The universal fallback for
messages is the **notification e-mail inbox** — every store already e-mails
"you have a message / an order"; one inbox integration covers all three stores.
Mind's "single biggest technical unknown" is two-thirds solved by official APIs
and one-third solved by reading e-mail. Scraping is the last resort, not the plan.

### 4. The paper never closes the door on the local-LLM temptation (Qwen)
The Watcher's morning round is **deterministic reading**: call an API, compare a
number to yesterday, read a file timestamp. That is a script on a schedule, not
a model. A model is needed only for the closing summary sentence — and a small
local model that invents a fact reaches the §10 trust-death ("wrong twice")
fastest of all. v1 is boring code. The clever creature comes later, on top of a
feed that provably works.

### 5. §9.3 names the fatal flaw ("reporting changes nothing") and then leaves it unfixed
The fix is not the Hands. It is: **every report line carries a deep link to the
exact page where the action happens** — the eBay order page, the Etsy
conversation, the dead listing. "Three unshipped orders" is knowledge; "three
unshipped orders → tap → order page" is one thumb-press from done, even from the
car. Reduce the cost of acting instead of granting write access.

### 6. Internal contradiction: §4.2.4 vs §4.2.6 — and it answers Open Question 5
"Report change, not state" (rule 4) and "report what has not moved in 30 days"
(rule 6) cannot both be rules, because the second **is** a state report. Resolve
deliberately: **daily = change only; weekly = one full-state snapshot with aging
counters** ("encyclopedia profiles: 62 days without movement"). The weekly pass
is also the answer to Open Question 5 — slow drift at 1% a week never shows as a
daily change, but an aging counter that only counts up cannot hide it.

### 7. There is no "done" state — so the report will nag, and nagging kills it
An unshipped order reappears every morning until handled. By day three the brief
reads like scolding; by week two it stops being opened (§10.1). Report items
need **one-tap acknowledge** ("seen / handled"). Honest consequence Mind must
admit: acknowledging means the Face *writes* — to its own small state file. A
controlled leak of Hands into Face. Name it and cap it: **the Face may write
only its own state, never a store.**

### 8. No heartbeat — a dead feed impersonates a quiet day
When a token expires or an API call fails, the report silently gets shorter.
Since silence is defined as good news (§4.2.4), a broken feed **looks exactly
like health** — the paper's own worst failure, reporting something untrue
(§10.3). Mandatory: every report ends **"sources read: n/n"**, and an unreadable
source is itself a red item. This one missing line is the cheapest insurance in
the whole design.

### 9. The build order (§3) violates the paper's own §5.1
§5.1 says zero numbers make the most beautiful page a demo. Then the dashboard
must not be built second. **v1 of the Face is the plain-text morning message
itself.** Build the designed dashboard only after two weeks of evidence that
Farid opens the brief (the paper's own success test). Design effort before a
proven read-habit repeats the Helper mistake: existence before value.

### 10. §5.4 ("a page on the PC does not reach an iPhone") is solved cheaper than stated
Once finding 1 is accepted, delivery is a solved problem: the cloud body already
reaches the phone — the brief arrives as a message where Farid already reads
(the Claude app, or a free Telegram bot with push notifications; one evening of
setup). No hosting, no port-forwarding, no new infrastructure in v1.

### 11. "Improves itself" — answer to Open Question 4, with a hard limit
The Watcher and the ACADEMY stay **separate creatures sharing one memory**:
every Watcher miss ("report said X, the truth was Y") is logged to the Academy
as a mistake-record, and corrections are made *from* that record by a session
Farid runs — never by the Watcher rewriting its own code. A self-modifying
watcher reaches "wrong twice, trust gone" faster, because its errors change
shape each time. Self-improvement = self-documentation, not self-surgery.

### 12. §9.4's predicted pressure is already here — and the paper's decision must hold
Mind predicts "the pressure to let it just fix the quantity will be strong and
immediate," and the commissioning request itself proves the prediction: store
edits, quantity changes, and customer control were asked for in the same breath
as v1. The decision **"no autonomous writes to any live store in v1"** is
correct and must survive that pressure. The leash stays: the Hands propose →
Farid approves from the phone → the Hands execute — and only after the Watcher
has been provably right for weeks.

**Remaining open questions, answered in passing:** Q1 → finding 1. Q2 → finding
3. Q3 → 7:00 AM stands (it is the FaridOS design); "urgent at 2 PM" belongs to
the cloud body — an hourly *money-checks-only* pass that pushes a message only
above the existing escalation floor, otherwise holds everything for morning.
Q4 → finding 11. Q5 → finding 6.

---

## PROPOSED JOB DESCRIPTION (the paper amended by the findings)

### Position: THE WATCHER (v1) — Business State Reader
One job, two bodies, one report.

**Cloud body** — a scheduled Claude session in the repo. Works while the PC is
off. Watches everything on the internet.
**Local body** — a scheduled script on the PC (Task Scheduler, morning +
on-boot). Watches everything that lives only on the PC, and drops its digest
into `channel/` so the cloud body folds it into the one brief.

**Duties, in priority order:**
1. **Stores first — the four money-checks** on eBay, Etsy, faridunhill.com,
   Ashcombe: orders unshipped or past handling time; buyer messages unanswered;
   listings ended or at zero quantity; account defects or policy notices.
2. **Website integrity checks** — a permanent regression list, starting with:
   the /shop route serves OUR products (the incident found by accident becomes a
   check that can never be missed again).
3. **Projects — evidence only.** `git log` and file timestamps. Never asks a
   project to describe itself.
4. **Keeps the map:** a registry of every project — name, purpose, one-line
   reason it exists, last observed movement — including the quiet ones: the Eye,
   the Judge, the 4,700 encyclopedia pipe profiles, the automated store module.
   Nothing may be forgotten, only deliberately paused.
5. **Reports:** daily brief, maximum 5 lines, change-only, every line a deep
   link; weekly full-state snapshot with aging counters; every report ends
   **"sources read: n/n"**. Silence on a quiet day is correct.
6. **Logs its own misses** to the Academy. Never edits its own code.

**Explicitly NOT the job (v1):** touching any live listing, answering any
buyer, issuing any refund, changing its own code, building dashboards.

**Success:** Farid still opens the brief in week three.
**Dead:** the report needs manual input to exist; or it states something untrue
twice; or Farid stops opening it. (Mind's §10 tests, kept unchanged.)

### Mapping Farid's seven specifications to the amended design
| # | Specification | Where it lands |
|---|---|---|
| 1 | Local on my PC | Split: local body for PC data; cloud body so it works with the PC off (finding 1) |
| 2 | Improves itself | Logs own misses to the Academy; corrections by a Farid-run session, never self-surgery (finding 11) |
| 3 | Edit the 3 stores | **v3 — the Hands**, on the propose → phone-approve → execute leash only (finding 12) |
| 4 | Study projects, suggest strategy | The weekly state report is the raw material; strategy stays with Farid and the council |
| 5 | Wake sleeping projects (4,700 profiles…) | Aging counters make every sleeping project visible weekly; waking them is separate, ordered work |
| 6 | Knows the system network | The registry — duty 4 |
| 7 | Reminds me of forgotten pieces | Aging counters + the registry; nothing goes quiet unnoticed |

---

## THIS MEMBER'S RECOMMENDATION TO FARID

Approve Mind's skeleton with the twelve amendments. When you rule GO, build the
**local body's file-reader first** — it needs no API keys, no accounts, touches
nothing, and proves the whole loop (read evidence → write brief → channel →
phone) at zero risk — while you create the eBay and Etsy developer API keys, the
only ingredient the cloud store-watcher waits on. The dashboard waits for two
weeks of opened briefs.

*Submitted for the council record. Awaiting Farid's final.*
**— The Creator (cloud), council member**
