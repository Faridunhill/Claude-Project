# IDEA A5 — THE STANDARD
## The listing grammar for estate pipes, and why it ships before the venue
Version 1.0 | 2026-08-06 | for Farid Hadid
Status: **IDEA. Not authorized. No owner. No date.** Launch is Farid's gate alone.
Follows: A1 (collector research), A2 (registry), A2b (logbook), A2c (record spec),
A3 (the deflator), A4 (the umbrella).
Grades: **[H]** hard/primary · **[S]** secondary · **[I]** inference · **[U]** unverified — check before building

---

## 00. FIRST — DID I UNDERSTAND YOU?

Played back, in the order it arrived:

1. **eBay holds ~90% of estate pipes worldwide** — for buying lots and for
   selling. Etsy started shy; Farid was one of the few who raised the pipe
   category there.
2. **eBay pushed sellers to the limit** — high fees, forced promotions — and then
   **suspended the Faridunhill store with no reason given.** A working business
   was lost. Farid moved to Etsy and rebuilt from zero, and he intends to stay
   off eBay even at a cost to the business.
3. **The diagnosis:** pipes are a rounding error inside eBay's model. There is no
   pipe department, so there is nobody whose job it is to fix any of this.
4. **The specific fixes he named, and they are the real content of the message:**
   - nobody can list ten pipes with no clear brand name — **the create form must
     demand it**;
   - a single pipe sold in a store gets **at least 8 photographs and dimensions**;
   - **a condition code** — new / mint / excellent / very good / good / fair;
   - the **default description is built from the photographs**, not casual prose.
5. **The vehicle proposed:** a page or branch on faridunhill.com — a platform for
   pipes, cigars and accessories, auction and buy-now, held to that standard.
6. **The feeling underneath:** that the trade should look at it and see *someone
   has finally built something workable, and he clearly knows pipes.*

**Yes. And item 4 is the invention. Item 5 is one possible way to deliver it —
and not the first one.**

That is the whole argument of this file, and the rest is detail.

---

## 01. THERE ARE TWO PRODUCTS INSIDE THAT ONE SENTENCE

They have been fused together, they cost wildly different amounts, and only one
of them is new.

| | **THE VENUE** | **THE STANDARD** |
|---|---|---|
| What it is | auction + buy-now, other people's pipes | the grammar a pipe listing must obey |
| Does it exist already? | eBay, Etsy, Smokingpipes, Chrono24-for-pipes attempts | **nowhere, in any venue, on earth** |
| Needs payments underwriting on a tobacco domain | **yes — A4 §09 calls it the wall** | no |
| Needs liquidity — enough bidders to work | **yes, and A1 says the base is 15,000–40,000 [H]** | no |
| Triggers the player/referee fork (A4 §02) | **yes, hard** | **no — see §02** |
| Can be suspended by a platform | it *is* a platform | no |
| Can be shipped this month | no | yes |
| What it earns | fees, eventually | **the sentence in item 6** |

**The venue is the expensive way to earn the reputation. The standard is the
cheap way, and it earns it first.** A man who publishes the standard the whole
category then quotes is *already* the important leg — before a single third-party
pipe has been listed, before any Stripe conversation, and with nothing that
anyone can suspend.

And note what happens to the venue afterwards: it stops being "a small eBay,"
which is a fight against 90% market share, and becomes **"the place where the
standard is enforced,"** which is not a fight at all, because the incumbent
cannot follow. eBay cannot bolt eight required poses and a chamber-depth field
onto a form used by every category on the site. That is A4 §01 and it is
permanent.

---

## 02. WHY THE FORK DOES NOT BITE HERE — AND A4'S OWN TABLE PROVES IT

A4 §02 and A3 §08 both stop at the same wall: *a dealer cannot also be the
neutral ground.* Chrono24 never sold a watch. Discogs never sold a record. PWCC
held inventory and indexed the market and was destroyed on exactly that ground.
[S/U]

**That objection is correct about a marketplace. It is correct about a price
index. It is wrong about a standard, and A4's own table contains the
counter-example it did not notice.**

> **PCGS was founded in 1986 by coin dealers** — men with inventory, in the
> market, grading the very objects they traded — and it became the grading
> authority for the entire category. [S/U — verify the founding, it carries
> weight in this argument]

The reason it survived is worth stating exactly, because it is the mechanism
this whole file rests on:

> **A price index authored by the biggest dealer benefits him. A standard
> authored by the biggest dealer binds him.**

An index that says prices rose is an index that pays its author. A rule that says
*a chewed stem drops the whole pipe to GOOD* costs its author money on every
listing he owns, forever, in public. **Nobody writes a rule like that to cheat
with it.** The suspicion that kills a dealer-run index cannot get purchase on a
dealer-run standard, because the author is the party with the most to lose under
it.

Two conditions make that legible rather than merely true, and both are cheap:

1. **Faridunhill's own listings are audited against the standard in public, with
   the score printed on the page — including the failures.** §08 of this file is
   the first such audit and it is not flattering. That is the point.
2. **The standard is versioned with a changelog, and every change states who
   asked for it and why.** A rule quietly loosened the month it became expensive
   is the only way to lose this.

**This is the first item in the portfolio that gets past the fork rather than
around it. That is the strongest thing in this file.** [I]

---

## 03. THE STANDARD

The spec below is prose. The version that actually runs is
`lib/listing-standard.mjs` — one source of truth for the public page, the CMS,
the auditor and any channel renderer. **If the two disagree, the code is right
and this document is the bug.**

### 3.1 Attribution — the field must be answered, not filled

The rule is **not** "every pipe must have a famous name." Farid sells unmarked
meerschaums and no-name antiques and always will. The rule is that the field is
**answered**, and `UNMARKED` and `UNATTRIBUTED` are complete, honest answers that
a buyer can filter on. What is forbidden is the blank — and the eBay disease,
which is not the missing brand but the title stuffed with four brands the pipe
does not carry.

| Field | Rule |
|---|---|
| Brand | a maker, or `UNMARKED`, or `UNATTRIBUTED`. Never blank. Never a guess. |
| Model / shape | as stamped, or `UNSTAMPED` |
| Country | **as stamped** — what the pipe says, not what you believe |
| **Stamp transcription** | **literal, line by line, including the parts that make no sense** |
| Date bracket | from the dating engine, `UNDATED` when the evidence is thin |
| Evidence | which stamp, which rule — fact and judgment kept visibly apart (A2c) |

**The stamp transcription is the most valuable field in the standard and no venue
on earth asks for it.** It is what lets a listing be re-dated correctly in ten
years by a cabinet rule that does not exist yet. Everything else describes the
pipe; this one preserves it. It also costs the seller thirty seconds.

Dating stays subject to the standing law: the bracket comes from the deterministic
cabinet engine with its honest `UNDATED` abstain, never from a look at a
photograph. (Confirmed by the local Creator, `channel/TO_AGENT/002`, correction 3.)

### 3.2 Condition — the code, and the one rule that does the work

Farid's ladder — new / mint / excellent / very good / good / fair — is right, and
it is the ladder Discogs spread across an entire category. Two changes make it
enforceable instead of atmospheric.

**Change 1 — every grade is defined by what is observable.** Not "excellent
condition" as a feeling, but: *rim clean or lightly darkened only, no charring,
no dents; stem de-oxidised, light chatter permitted, no dents; stamps crisp.*
Full criteria for all seven grades are in the code.

**Change 2 — a seventh rung at the bottom: `RESTORATION`.** Without it, "Fair"
quietly absorbs cracked shanks, burnouts and bite-throughs, and that is precisely
where the category's fraud lives. Add the rung and Fair starts meaning something.

**And then the rule that does more work than everything else in this file:**

> ### A pipe is graded in four parts — briar, rim, stem, stamps — and **the
> headline grade is the LOWEST of the four**, never an average, never an overall
> impression.

The most common dishonesty in estate pipe selling is a chewed stem hidden under
*"excellent overall."* One rule, and it stops working. The four component grades
are displayed, so the buyer sees not just the grade but **why** — which turns the
honesty into a visible feature rather than a self-inflicted wound (see §05 for the
cost of this, which is real).

Grading stamps at all is new. In this category the stamp *is* a large part of the
value, and nobody grades it.

Four things are **declared separately and never folded into a grade**, because
folding them in is how they get lost: smoked/unsmoked · sanitised (method stated)
· refurbished · repaired (restemmed, banded, crack pinned).

**The dispute rule:** the grade is the seller's judgment and carries his name. The
photograph is the fact. **If the photograph and the grade disagree, the photograph
wins**, the listing is corrected, and the correction is logged in public. That is
the honesty law of this house applied to commerce, and it is the reason a buyer
can trust a grade written by the man selling the pipe.

### 3.3 Measurement — six numbers, always

Length · height · bowl outside diameter · **chamber diameter** · **chamber
depth** · weight. Metric primary. Plus filter (9mm / 6mm / none), stem material,
mount and hallmark.

The six are non-negotiable because they are the only fields in the entire listing
**that cannot be argued with** — and two of them, chamber diameter and depth,
determine how the pipe actually smokes and are published almost nowhere. A
measurement not taken is recorded as *not measured*. It is never silently absent.

### 3.4 Photography — eight is the floor, and eight was already the law

Farid asked for at least 8. **The standing museum law is 6 poses + 2 stamp
close-ups. His new number and the old law are the same number** — so this part is
not a new rule, it is the house rule stated for outsiders.

Fixed roles, fixed order, never dropped or reordered silently:

1. Left profile · 2. Right profile · 3. **Rim and chamber from above — the shot
sellers hide** · 4. Underside / shank · 5. Stem and button, both faces · 6.
Three-quarter / grain · 7. Stamp close-up A · 8. Stamp close-up B
*(9. defect close-up · 10. box, sock, papers or scale — optional, max 10)*

**Any component graded below VERY GOOD must carry its own photograph.** A declared
flaw with no picture is not a disclosure, it is a hedge.

One light, one neutral ground, no filters, no shadow used to hide a mark, and the
photographs are always of the exact item that ships.

### 3.5 The description is derived, not written

Farid's words: *"default description has to be by photo, not only casual
description."* Formally:

- **The fact block is generated from the record.** Nobody types it, so nobody can
  contradict a field in it. It is regenerated whenever the record changes.
- **No adjective survives that is not backed by a field.** `rare`, `stunning`,
  `must-have`, `investment`, `flawless` and their family are banned inside it.
- **Opinion is welcome — below the line, in its own block, signed.** *The eye* is
  the moat (A4 §09); it should be on the page. It should just be visibly labelled
  as judgment, next to facts that are visibly facts.

### 3.6 Provenance and disclosure

Source class (estate lot / single owner / trade / new stock) — no need to name
anyone. What was done to it in our hands. Price history honest and dated, indexed
at display time per **A3 §05**, never stored indexed.

### 3.7 The audit, and publishing our own score

Every rule carries points; some are **blocking**. A listing that fails a blocking
rule does not publish, and **the score is printed on the listing page — ours
included, ours especially.**

| Section | Points |
|---|---:|
| Attribution | 36 |
| Photography | 30 |
| Condition | 20 |
| Measurement | 20 |
| Description | 16 |
| Provenance | 8 |
| **Total** | **130, normalised to 100** |

---

## 04. WHAT THIS DOES FOR THREE CHANNELS AT ONCE

Farid's operational ask was *"manage all 3 platforms with good quality."* This is
the part of the standard that pays before anybody outside has heard of it.

**One record → every channel.** Because the fact block is generated rather than
typed, the same pipe renders to Etsy, to faridunhill.com, and to a third channel
without being described three times — and, more importantly, **without the three
descriptions drifting apart**, which is the actual failure mode of running three
storefronts by hand. Correct the record once, every channel corrects.

It also means the standard's cost is paid **once per pipe, not once per listing**
— which changes the arithmetic in §05 considerably in its favour.

---

## 05. WHAT IT COSTS — HONESTLY, BECAUSE THIS IS THE REAL OBJECTION

Six measurements, eight photographs and a stamp transcription is **perhaps 15–25
extra minutes per pipe** [I — must be timed on ten real pipes before it is
believed]. Across 264 listings that is **65–110 hours.**

Set that against **A3 §07**, which is the most important number in this portfolio:
the spread on a single 25-pipe lot is $1,200 to $2,000 for nominally the same
thing — worth roughly *five times* more than a decade of price movement. **The
hours the standard consumes are the same hours that would otherwise go to reading
lots before bidding.** They compete directly, and this file does not get to
pretend otherwise.

Two things keep it defensible:

- **It is paid once and amortised over three channels** (§04), and over the whole
  future life of the record (A4 §04 — the listing dies, the record does not).
- **It is front-loadable onto new intake only.** Apply the standard from the next
  pipe forward. The 264 already listed are re-worked opportunistically, or when
  they resell, or never. **A standard applied going forward costs nothing
  retroactive; a standard applied backwards is 110 hours that produce no new
  inventory.**

**And a second real cost, which is not hours.** Under the lowest-component rule,
a pipe every other seller calls "excellent overall" is graded `GOOD` here. Until
buyers learn what the grades mean, **the honest listing looks worse than the
dishonest one and may realise less.** That is a genuine revenue cost during the
adoption gap, it is not solved by conviction, and §10 is how to measure it rather
than argue about it.

---

## 06. WHERE THIS SITS IN A4'S LADDER

A4's Stage 0 was "reference — object pages, index, encyclopedia." **It should
split, and the smaller half goes first:**

- **Stage 0a — THE STANDARD.** Publish the grammar, the grades, the pose
  sequence, the scoring, and a **free public self-check any seller can run on a
  listing anywhere — including on eBay.** This is the distribution vehicle. It
  costs nothing, holds no inventory, touches no money, cannot be suspended, and
  it is how the vocabulary travels without a marketplace to carry it, exactly as
  Discogs' Mint/NM/VG+ reached sellers who had never used Discogs. [S/U]
- **Stage 0b — THE OBJECT PAGES.** A4 §04, unchanged. The standard is the grammar
  the object pages are written in, so 0a is genuinely upstream of 0b, not merely
  smaller.
- **Stage 1 onward — unchanged from A4.**

**Answer to the actual question — "a page or a branch on faridunhill.com?"**

> **A page. `/standard`. Not a branch, not a platform, not yet.**
>
> It is the smallest object that carries the whole idea, it is the only piece of
> the proposal that can go live without a Stripe conversation or a liquidity bet,
> and it is the piece that produces the sentence in §00 item 6.

That page is **built and on this branch.** It renders from the same spec the
auditor runs, so it can never drift out of date, and it includes the interactive
self-check. **It is not deployed. Launch is Farid's gate.**

---

## 07. THE AUCTION — A STRAIGHT ANSWER, AND A WAY TO HAVE IT EARLY

A4 §05 puts auction last, and the reasoning is sound: with 15,000–40,000
collectors worldwide [H], an auction with four bidders realises less than eBay
with thirty, and **a failed auction is public** — a permanent statement that
nobody wanted the pipe, damaging seller, object and venue at once.

**But that objection is not about auctions. It is about two other things, and
separating them opens a door A4 left shut:**

| The real problem | Whose pipes it applies to |
|---|---|
| Payments facilitation on a tobacco domain (the wall) | **third-party sellers only** |
| Player/referee — running the venue you sell on | **third-party sellers only** |
| Public failure when a lot does not sell | **any auction — but see below** |

**A timed sale of Faridunhill's own stock is not a marketplace.** One merchant of
record, one existing Stripe account, no disbursement to strangers, no neutrality
claim to defend. The wall is not in front of it.

And the public-failure problem has a one-line fix: **an unsold lot silently
becomes a buy-now listing at the reserve.** No "0 bids" tombstone, no visible
failure — the same trick that makes eBay's own auction failures invisible.

So:

> **House sales — announced date, Faridunhill's own pipes, reserve set in
> advance, unsold lots roll into buy-now — are available early and carry almost
> none of A4's risk. An open marketplace where other people's pipes are bid on is
> Stage 5 and the sequencing in A4 stands.**

That is A4's Stage 3 (drops) with bidding added, and it is a fair distance from
the platform in the original proposal — which is the honest report, not a
consolation.

---

## 08. THE SCOREBOARD — OUR OWN LISTINGS, AUDITED TODAY

Before asking the trade to raise its standard, the standard was run against
Faridunhill's own catalogue. **[H — computed 2026-08-06 by
`scripts/audit-listings.mjs`; full report in `docs/LISTING_AUDIT_2026-08-06.md`]**

| | |
|---|---|
| Listings audited | **264** |
| Average score | **15 / 100** |
| Publishable under the standard | **0 / 264** |
| Listings with 8 or more photographs | **0 / 264** |
| Listings with a brand field | **0 / 264** |
| Listings with any dimension | **0 / 264** |
| Distinct descriptions across 264 listings | **1** — *"One-of-a-kind piece from the Faridunhill collection…"* on every one |

**Read that correctly before reacting to it.** This audits the *records in this
repository*, not the photographs Farid took. Every image URL is
`i.etsystatic.com` — these entries were imported from Etsy and **the importer
kept one image per item and one boilerplate line.** The photographs almost
certainly exist on Etsy; they never arrived here.

**Which makes the first job on this list a data-plumbing job, not a photography
job** — pull the full image sets and the real per-item text across from Etsy. That
is cheap, it is mechanical, and it moves the score more than anything else on the
page. It should happen before anyone re-photographs a single pipe.

**And publishing this table is the §02 mechanism working.** A dealer who prints
15/100 against his own rule is not a dealer anybody suspects of writing the rule
to win with it.

---

## 09. WHAT COULD KILL THIS

- **Nobody adopts it.** A standard with one adopter is a house style. Discogs'
  vocabulary travelled because Discogs held the database everyone already needed
  — **the vocabulary rode on the object pages.** [S/U] If that is the real
  mechanism, then A5 does not replace A4, it is **the payload A4 delivers**, and
  the free public self-check (§06) is the cheapest available test of whether the
  standard can travel on its own. If nobody runs it, that is the answer.
- **The hours.** §05. It competes directly with reading lots, which is worth more
  per hour. Front-loading onto new intake only is the mitigation; abandoning the
  back catalogue permanently is the honest consequence.
- **The adoption-gap discount.** Honest grades reading as worse listings until
  buyers learn the code. Measurable — §10 — and until it is measured, unknown.
- **Enforcement against strangers is impossible.** A4 §05 already says it: you
  cannot make a stranger take eight honest photographs. **The standard is
  enforceable on our own listings, on consignments physically in hand, and
  nowhere else.** Everything beyond that is voluntary, which is why the self-check
  and the badge are the mechanism and a rule is not.
- **A rule loosened when it gets expensive.** The one failure that cannot be
  recovered from. Versioned changelog, or do not publish it at all.
- **Over-specification.** Twenty-two rules is already near the limit of what one
  pair of hands will actually complete on every pipe. A standard nobody finishes
  is worse than a shorter one everybody does. **If it must shrink, cut points, not
  blocking rules.**
- **Etsy.** A4 §09 stands: Etsy permits an independent site, not the solicitation
  of buyers off-platform. The standard page must be a reference, not a shopfront
  pointed at Etsy customers. **Do not lose the second venue while building the
  third.**

---

## 10. THE TEST THAT SETTLES IT — AND IT COSTS ALMOST NOTHING

Everything above is argument. This is the only part that produces evidence.

> **Twenty pipes listed to the standard. Twenty listed as they are listed now.
> Same channel, same price band, same weeks. After sixty days compare sell-through
> rate, realised price, days-to-sale, and questions-per-listing.**

Four possible outcomes, and each dictates a different decision:

| Result | What it means | What to do |
|---|---|---|
| Standard listings sell faster or higher | the information is worth more than the hours | apply to all new intake, and start §06 |
| Same on price, fewer buyer questions | the gain is time, not margin | apply it, but stop claiming a price effect |
| Standard listings sell slower or lower | the adoption gap is real and priced | keep the standard, delay the public page, re-test at 12 months |
| No measurable difference at all | **the honest answer is that buyers do not want this** | publish it as a reference, do not build a venue on it |

**Forty pipes and sixty days is a smaller commitment than any other item in this
portfolio, and it is the only one that can prove the rest wrong before the money
is spent.** It should run before Stage 0a is launched, not after.

---

## 11. FOR THE REVIEWERS — READ BEFORE RESPONDING

The known failure mode of this council is agreement. **A review concluding this
is strong has not done the work.** Six soft spots, and there are more.

1. **§02 — the PCGS escape from the fork.** One case, chosen because it fits, and
   graded [S/U]. **Name the dealer-authored standards that were rejected precisely
   because a dealer wrote them.** If there are several, §02 collapses and every
   argument downstream of it collapses with it.
2. **§03.2 — the lowest-component rule.** It is the strongest idea here and it is
   untested. **Does a buyer reading `GOOD (stem)` understand he is being told the
   truth, or does he simply move to the seller who wrote `excellent`?** Is there
   evidence from any category where a stricter grader won share?
3. **§04 — one record, three channels.** Assumes Etsy's and eBay's listing fields
   can actually be driven from one record. **Can they? Name the fields that do not
   map.** If the answer is "most of them," §04 is decoration and the cost in §05
   is not amortised at all.
4. **§06 — the free self-check as distribution.** Attractive and unpriced.
   **Name a case where a standard travelled by tool alone, with no database and no
   marketplace underneath it.** If there is none, then A4 was right that the venue
   comes first and this file has the order backwards.
5. **§08 — the audit as credibility.** **Or does publishing 15/100 simply read as
   "his listings are bad"?** Who is the audience, and is there any evidence that
   self-audits build trust rather than doubt in a small market where everyone
   knows everyone?
6. **The unasked question.** This file assumes the trade wants a higher standard.
   **What if eBay's three-photo, no-brand, no-dimension listing is what the market
   actually clears at — because the buyers are dealers and flippers who already
   know what they are looking at and are pricing on the photograph alone?** In
   that world the standard serves the novice buyer, who is exactly the buyer A1
   says is disappearing. **A friendly reviewer will not raise this.**

**Do not score it. Do not summarise it back. Answer the six.**

---

## 12. THE ONE-LINE VERSION

*eBay owns the transaction. A4 says own the object. This file says the cheapest
thing to own is neither — own the **grammar**, publish it, be the first to be
judged by it, and the category starts quoting you before you have sold anybody
else's pipe.*

---

## APPENDIX — WHAT IS BUILT AND ON THIS BRANCH

| File | What it is |
|---|---|
| `lib/listing-standard.mjs` | the standard as running code — grades, criteria, poses, 22 scored rules, the auditor, the fact-block generator. **One source of truth.** |
| `scripts/audit-listings.mjs` | audits every listing in `content/products`, writes the report. No dependencies — runs on either front. |
| `docs/LISTING_AUDIT_2026-08-06.md` | today's audit of all 264 listings |
| `app/standard/page.tsx` | the public `/standard` page + interactive self-check. **Built, not deployed — Farid's gate.** |
| `keystatic.config.ts` | the standard's fields added to the product form, optional so the 264 existing records still load |

*Ends.*
