# MARKETING MONSTER v1.2 — FORGE HANDOFF
### The council ruling, engineered

**Document:** 004 · **Date:** 2026-07-31 · **Supersedes:** doc 003 as the build spec (003 remains the evaluation of record)
**Ruling accepted from:** MIND, on Farid's order · **Status:** ready for FORGE on three answers from Farid

---

## 0. SCOPE — what this evaluator read, and what it did not

**Read:** MIND's ruling in full, as relayed by Farid, and my own doc 003.

**NOT read:** the 8.8 evaluation and the "Ratified" spec. I have never seen those documents. Where §4
agrees with discarding the Opportunity Score, that agreement covers **only the formula as MIND quoted
it** — I am not endorsing or condemning documents I have not opened, and no later session should read
this as a review of them.

**On the scores.** I will not comment on 8.8 versus 6.6, because a scorer cannot referee his own score.
One structural note is safe to make and worth keeping: the correlation MIND observed — depth down, praise
up — is what you get when reviewers are asked *"is this good?"* instead of *"what breaks first, and what
would it cost?"* If the council keeps running, ask the second question. It is much harder to answer with
flattery.

---

## 1. THE RULING, ACCEPTED

v1.2 = **v1.0 (MIND) + the twelve changes from doc 003 + two amendments.** Nothing else moves. The
appendices in doc 003 (event schema, playbook grammar, admission test, decision record, source manifest)
stand as written and are what FORGE builds against; this document changes two things about them and adds a
wave-1 work order with acceptance tests.

The two amendments are both corrections to *my* spec, not MIND's, and both are right:

| # | Amendment | Origin |
|---|---|---|
| **A** | **Machine-maintained ledgers only.** If a file needs Farid to keep it by hand, it dies in three weeks and the system starts lying by omission. | MIND's caution — the strongest point in the ruling |
| **B** | **GroundTruth's proxy conversion = email capture on owned ground.** The only proxy that builds an asset. | MIND's answer to my M5 |

Amendment A is the one that decides whether any of this survives contact with a working week. Agreeing
with it in words is worthless; §2 engineers it.

---

## 2. AMENDMENT A, ENGINEERED — "the machine writes the rows, never you"

The caution is exactly right and it has a sharp edge I have to name rather than smooth over: **two of my
twelve mechanisms require a human judgement by design.** The cookbook admission test is a wall decision,
and the wall is Farid's reserved power. The Judge's floor prices and category picks are reserved powers
too. A rule that says "no human input" would either break the wall or be quietly broken in week two.

So the rule needs one more turn of precision, and with it, it holds:

> **Farid supplies verdicts. The machine supplies rows.**
> A verdict is a word in a chat. A row is a line in a file. He never types the second one, ever.

That distinction is implementable, and it is what §2.1–2.4 specify.

### 2.1 Ledger authorship — who writes every row

Five files are the system (doc 003 §4.2). For each, this is the contract FORGE must honour:

| Ledger | Rows written by | Farid's input | Where he gives it | Hand-editing |
|---|---|---|---|---|
| `scale/events.jsonl` | machine, append-only | none | — | **never** |
| `digger/sources.csv` | machine, at fetch time | none | — | **never** |
| `judge/decisions.csv` | machine, from the cycle | verdict word on reserved-power items only | chat | **never** |
| `playbook/PLAYBOOK.md` | machine proposes and promotes | override word, optional | chat | **never** (deleting a line is allowed and encouraged) |
| `cookbook/ADMISSION_LOG.md` | machine, with the four test results pre-filled | **yes / no** on the crossing | chat | **never** |

The pattern for the last three is identical: the machine drafts the row **complete**, including its own
recommendation, and holds it in a pending state. Farid says a word. The machine writes the verdict into
the row and moves on. The reserved power is fully intact — he still decides — and his hand never touches
a file.

**Deleting is not maintenance.** Farid may delete any playbook line at any time, with no ceremony and no
replacement row required. That is the safety valve of the frozen-brain design and it must stay free.

### 2.2 The decision queue — reserved powers without paperwork

One generated file, rewritten each cycle, never edited by hand:

```
clones/pipes/PENDING.md      # machine-generated, overwritten every cycle
─────────────────────────────────────────────────────────────────────
D-014  category      Dig proposes: cigar lighters, mid-tier.
                     Edge: audience ✓ / germany_route ✓ / expertise ~
                     Machine recommends: DO.                      → yes / no
D-015  floor_price   Shell 1961 group, engine bracket 1959-1963.
                     Machine recommends: $310 floor.              → number
D-016  wall          Lesson wants to cross into the cookbook:
                     "photograph the maker's mark at an angle that
                      shows wear."
                     Admission test: 1 ✓ 2 ✓ 3 ✓ 4 ✓ → passes.    → yes / no
```

Three answers, thirty seconds. Every one of them lands as a machine-written row in the right ledger. If
`PENDING.md` is ever long enough to be a chore, that is a signal the Judge is escalating too much, and the
fix is to raise its autonomy on the non-reserved items — not to make Farid faster.

### 2.3 The health check — make omission a printed number

MIND's failure mode is "it dies in three weeks and the system starts lying by omission." The way to stop
that is not discipline. It is to **make silence visible**, exactly the way doc 003 makes unattributable
sales visible. Same principle, second axis.

Every weekly Scale report opens with three lines before anything else:

```
LEDGER HEALTH — week 2026-W32
  events.jsonl      312 rows this week   (prev 287)      ok
  decisions.csv       4 rows this week   (prev 6)        ok
  sources.csv         0 rows  14 days    (prev 3)     ⚠ DIGGER SILENT
  playbook          1 proposed, 0 confirmed, 2 due for review
  unattributable    68% of outcomes this week
```

An organ that stops writing rows gets flagged in the same breath as a bad number. Two consecutive cycles
of silence on any ledger and the report's headline is not marketing performance — it is *"the Digger has
stopped."* A system that reports its own decay cannot lie by omission; the omission is the report.

### 2.4 Maintenance budget, and what I cut first

Honest estimate, stated so it can be checked against reality rather than trusted:

| Who | What | Per week |
|---|---|---|
| Farid | answering `PENDING.md`, reading the report headline | **~15 minutes, no file editing** |
| Farid | reviewing playbook lines due for expiry | ~10 minutes, once a month |
| Machine | everything else | — |

**If it runs heavier than that, cut in this order** — I am naming my own process as the first thing to go,
because a mechanism that costs more than it returns is a liability no matter who designed it:

1. **`claims_derived` in the source manifest** (doc 003 App. E). Keep url, date, permission basis, expiry;
   drop the per-claim linking. Costs the ability to trace one claim back to one page; saves the most
   bookkeeping of anything in the spec.
2. **`STRUCT` tier reporting granularity** — collapse to a single weekly proxy number rather than per-lesson.
3. **Never cut:** the unattributable share, the evidence fields on playbook lines, the admission test, the
   reject log. Those four are the ones carrying the honesty law; everything else is convenience.

---

## 3. AMENDMENT B, ENGINEERED — email capture as GroundTruth's proxy

Accepted, and it is the right choice: it is the only proxy that leaves an asset behind, and it is the
legal replacement for the struck eBay list that doc 003 M4 and v1.0 both point at.

Two engineering conditions, because this asset must be **born clean** — the whole reason the eBay list was
struck is that it was not:

**1 · Consent-first storage.** Every subscriber row carries, from day one: `captured_at`, `source_page`,
`consent_text_version`, `double_opt_in_confirmed_at`. No row without a confirmation timestamp is mailable,
and the machine enforces that at send time rather than at judgement time. This costs nothing now and is
the difference between an asset and a liability later.

**2 · The Goodhart guard — one proxy is not enough.** A single optimized proxy always degrades: optimize
capture alone and you get pop-ups, dark patterns, and a large dead list that proves nothing. So the proxy
is a **pair**:

- **Primary:** verified email capture on owned ground.
- **Guard:** 30-day return rate of captured visitors.

**Promotion rule:** an `OUTCOME` lesson on GroundTruth confirms **only if capture rises and the guard does
not fall.** If capture rises while returns fall, the lesson is not confirmed — it is recorded as a
*learned trap* in the reject log. This makes the pair self-policing and needs no judgement call.

New Scale event, slotting into the existing schema with no change to it:

```json
{"event":"email_capture","surface":"site","clone":"groundtruth",
 "asset_id":"page/parcel-lookup","asset_version":"pb-2026-09-02.1",
 "attribution":"direct","cohort":"2026-W36","value":null}
```

---

## 4. THE ONE REJECTION I AGREE WITH — and the reason matters more than the verdict

The Opportunity Score (`Market Demand + Margin − Complexity`) should be rejected, on the same grounds MIND
gives, stated technically: **it is a scoring function over unmeasured inputs.** None of the three terms has
a measurement procedure, a unit, or a source. What such a formula actually does is take a judgement,
convert it to a number, and thereby launder it — the number then survives arguments the judgement would
have lost, because numbers look like evidence. It is the marketing-side version of a confident date with
no stamp behind it, and it fails the same law.

The honest replacement already exists in v1.0 and costs less: **the edge filter, plus a written reject
reason in `decisions.csv`.** "REJECT — edge=NONE, competes head-on with Amazon" carries more real
information than "score: 4.2", and unlike the score it can be checked against what happened next.

There is a version of scoring that *would* be legitimate later: once `decisions.csv` and `events.jsonl`
have twelve months of paired decisions and outcomes, a score fitted to **your own recorded history** is
measurement rather than invention. That is a v2 conversation, and it is only available to a system that
kept the ledgers. One more reason the ledgers are the product.

---

## 5. THE THREE ANSWERS THAT RELEASE THE BUILD

Two are confirmations; one is a fact only Farid's side holds.

**1 · The Well lives as files on disk.** *(confirm)* — MIND's reasoning and mine converge: the wall has to
be something you can see. Recommended layout is doc 003 §5. Unblocks wave 1 immediately.

**2 · Pipes is the only clone until one lesson reaches CONFIRMED.** *(confirm)* — no GroundTruth or
Ashcombe build begins before that, no exceptions, because the point of the rule is to prove the loop turns
before it is copied three times.

**3 · Where do the hub and the cabinet actually live?** *(fact, not a decision — I cannot look)* — I run on
the cloud front and I do not have your PC in context. Wave 2 loads the Well from real data and cannot start
without a path. The fastest possible answer, in whatever form suits you:

- the folder path, or
- a `dir` / `ls` of the folder pasted into chat, or
- a drop into `channel/NEW_UPLOADS/` and the word "check the channel."

Formats do not matter — CSV, JSON, XLSX, a database file, a folder of exports. Structure is wave 1's
problem, not yours. Only the location is blocking.

---

## 6. WAVE 1 WORK ORDER — what FORGE builds first, with acceptance tests

Scoped to the pipes clone only. Nothing here needs the encyclopedia stack, a server, or a framework —
files, a writer, a loader, and a report.

**Build:**
1. The directory tree (doc 003 §5), pipes root only.
2. `scale/events.jsonl` append-only writer, enforcing the schema in doc 003 App. A.
3. `well/SCHEMA.md` plus the loader that turns the eBay sold-item export into `well/derived/`.
4. The weekly report generator, opening with the LEDGER HEALTH block from §2.3.
5. `PENDING.md` generator (§2.2).

**Acceptance tests — the laws, expressed as code that fails.** This is how the honesty rules survive a
future refactor; the same way the dating engine's 324 tests keep the cabinets honest:

| # | Test | Law it enforces |
|---|---|---|
| T1 | An event written with no `attribution` field stores `unattributable` | B1 — no invented attribution |
| T2 | Upgrading `attribution` above `unattributable` without a `reason` string is rejected | B1 |
| T3 | An edit to an existing `events.jsonl` row is rejected; corrections must append and reference | append-only truth |
| T4 | The loader emits **zero** rows containing an email address, a personal name field, or a street address | M4 — derived features only |
| T5 | The same customer across two exports resolves to the same salted hash, and the hash is not reversible without the salt | M4 |
| T6 | A playbook line missing `n`, `effect`, `born` or `review` fails validation and cannot reach CONFIRMED | B2 |
| T7 | A line promoted to CONFIRMED on a single cohort is rejected unless `src=farid` | B2 |
| T8 | A Maker output written without `asset_version` fails | N1 — rollback key |
| T9 | The weekly report prints the unattributable share and per-ledger row counts, even when both are bad | B1 + §2.3 |
| T10 | A cookbook line added without a matching `ADMISSION_LOG.md` entry fails the build | B3 — the wall |

**Definition of done for wave 1:** an event can be written and queried, the Well has a schema, the loader
holds no personal data, the report prints its own blind spots, and T1–T10 pass.

When they pass, the pipes dig starts and the Monster has a spine.

---

*Prepared for Farid (FARIDHD1969@aol.com), 2026-07-31, on MIND's ruling. Architectural and specification
work only; the evaluator holds no access to the eBay export, hub/cabinet, or GroundTruth data — see §0.*
