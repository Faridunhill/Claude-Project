# IDEA A3 — THE DEFLATOR
## Why a sold-price archive rots, and what to measure it against
Version 1.0 | 2026-08-06 | for Farid Hadid
Status: **IDEA. Not authorized. No owner. No date.**
Follows: A2 README (registry research), A2b (logbook), A2c (record spec).
Grades: **[H]** hard/primary · **[S]** secondary · **[I]** inference · **[U]** unverified — must be checked before use

---

## 00. FIRST — DID I UNDERSTAND YOU?

Played back:

1. A sold price from 2016 is **not a valid price signal for 2026**. The number
   didn't change — the dollar did.
2. Pricing today's pipe from an unindexed old record is **unfair to the pipe and
   to whoever owns it**.
3. `$11 cost → $45 sold` is not a comp. It is a fossil.
4. So the archive needs a **benchmark to check against** — an outside ruler that
   translates a past number into a present one. Gold was the example, not the
   demand.

**Yes. And the correction matters more than it first appears.**

The first read of this treated it as a question about margins, and answered that
the ruler cancels in a buy/sell ratio. **That answer was correct and irrelevant.**
Farid was not asking about margin. He was asking how to convert a historical
observation into a current asking price — and there the ruler does not cancel,
because there is only one side of the trade.

Recorded here because the mistake is instructive: *a ratio is ruler-independent;
a single price is not.* Any reviewer applying the ratio argument to this document
has made the same error.

---

## 01. THE PROBLEM STATED PROPERLY

**A nominal sold-price archive is a decaying asset that looks like an
appreciating one.**

Every year it grows — more records, more evidence, more authority. And every year
each individual record becomes a worse guide to the present, silently, with no
warning marker on the page.

Ten years of eBay and five of Etsy is described elsewhere in this portfolio as
possibly the most valuable asset in the whole business. That is probably true.
**It is also true that publishing it raw would make it a machine for suppressing
prices in this category — including Faridunhill's own.**

Three separate harms, worth keeping separate because they have different fixes:

| Harm | Who is hurt | Fix |
|---|---|---|
| Underpricing own inventory | Faridunhill | index at listing time |
| Underpricing a consignor's pipe | the consignor, then the relationship | index in the estimate |
| Teaching the public a stale number | the whole category | index at display time |

The third is the one that scales, and it is the one that arrives with
publication.

---

## 02. WHAT A BENCHMARK IS ACTUALLY FOR

Not to say what a pipe is worth. **To say what a past dollar was worth.**

The chain has two links and they are usually confused:

1. **What did this pipe fetch, and when?** — a fact, recorded, never edited.
2. **What is that sum in today's money?** — arithmetic, recomputed on demand.

Neither of these is a valuation. A valuation is link 3 and requires judgment about
the object. Links 1 and 2 are mechanical, and being mechanical is what makes them
defensible.

**This preserves the A2c rule (facts and judgment visibly separate,
*CDN v. Kapes*).** The nominal price is fact. The index is public arithmetic on
fact. Only the estimate is opinion, and only the estimate carries a name.

---

## 03. THE CANDIDATE RULERS — AND WHY GOLD IS RIGHT AND ALSO DANGEROUS

⚠️ **[U] Every number in this section is approximate and must be verified against
BLS and LBMA source data before anything is built on it.** They are here to show
shape, not to be used.

Base 2016 → 2026, roughly:

| Ruler | Approx. multiple | What it actually measures |
|---|---|---|
| **US CPI** | ~1.40× | a basket of consumer necessities |
| **Median wage** | ~1.45× | ability to pay for a discretionary object |
| **Gold** | ~3.2× | inflation **+ fear + central-bank demand** |

**Applied to the Dunhill:**

- Sold then at **$165**
- CPI says today: **~$231**
- Wage says today: **~$239**
- Gold says today: **~$528**
- **Farid actually sells it at $259–325**

**Applied to the $45 pipe:**

- CPI: ~$63 · Wage: ~$65 · Gold: ~$144

### The finding that decides the section

Farid's own selling behaviour — $259–325 against a CPI-implied $231 — sits at
roughly **1.15–1.4× CPI**, and **well under half** what gold implies.

**He has already been running an index for years. It is approximately CPI plus a
quarter. This document's job is not to invent a ruler. It is to write down the one
his hands already use, so it can be applied to 8,000 records instead of to
whichever pipe is in front of him.** [I]

### Why gold cannot be the ruler on its own

**It is start-date dependent to a degree that destroys it as a standard.**

Gold was near a trough in 2016 after four years of decline, and near record highs
in 2025–26 on central-bank buying and geopolitical fear. Index from 2011 (gold
~$1,900) instead of 2016 (~$1,250) and the same archive returns a completely
different "fair price" **for the same pipe** — purely because of when it happened
to sell. [S/U]

A standard that gives different answers to the same object based on an arbitrary
starting year is not a standard. It is noise wearing a suit.

**But the instinct behind it is sound and should not be discarded.** Gold is doing
one job better than CPI: it is a **global** ruler. Buyers are in Germany, Japan,
the Gulf. CPI is American. Gold is the same everywhere, is not revised by any
government, and is culturally legible to exactly the kind of person who collects
objects. Keep it — as the ceiling of a range, not as the number.

---

## 04. THE RULER NOBODY HAS BUILT

Every option in §03 is borrowed from outside the category. Each one answers
"what happened to money," not "what happened to pipes."

**The category's own index is buildable from material Faridunhill already holds
and nobody else does.**

Two accepted methods, both proven elsewhere:

- **Repeat-sales.** The same object sold twice, years apart. Art uses this
  (Mei Moses). Pipes have a structural advantage here that art does not — the
  **Grain Print** (A2b) can confirm a pipe returning years later *is the same
  pipe*, which is exactly the hard part of a repeat-sales index.
- **Matched-pair.** Same brand × era × shape × finish, sold in different years.
  Weaker per observation, far more observations. This is what 8,000 orders makes
  possible.

**This is the aggregate layer A2c already argued for, reached from a second
direction.** Not "one page per pipe" — *"Danish Stanwell smooth billiards, 60
recorded sales, 2015–2026, indexed."* The individual records are evidence. The
index is the reference. The reference is the authority.

### The objection a reviewer should raise, so it is pre-empted here

**An index built only on one dealer's sales measures that dealer's pricing
behaviour, not the market.** If Farid raised his prices, his index reports that
the market rose. Circular.

It needs external anchoring — published estate prices from Smokingpipes, auction
results, WorthPoint comparison. **Without external anchoring this index is a
mirror, and a mirror published as a reference is the thing that gets the whole
project attacked.** [I]

---

## 05. THE OPERATING RULE PROPOSED

Machine-maintained. Nothing filled by hand.

**STORE, permanently, never overwritten:**
- nominal price · currency · date · channel

**COMPUTE at display time, never stored:**
- indexed range, recalculated every time the page loads

**DISPLAY:**

> **Sold $45 — March 2017.**
> *In today's money: $63–$92.*
> *Range: CPI floor to category index. Method published.*

The **spread itself is honest information.** A wide spread says the ruler is
uncertain, and saying so is more credible than a single confident number.

Because it is computed and not stored, the entire archive re-prices itself
forever with zero manual work — which is the only version compatible with 8,000
records and one man.

**Gold is published as a third line, optional, labelled as what it is:** *"in gold
terms, 0.132 oz then → 0.073 oz now."* It is the most quotable line on the page
and it costs nothing, but it never sets the asking price.

---

## 06. THE SEPARATE UNFAIRNESS — `$11 → $45`

Two different complaints live inside that example and they should not be merged.

**Publishing $45 in 2026 as a current guide** — unfair, and §05 fixes it.

**Buying at $11 and selling at $45** — not unfair, and no fix is needed. The $11
was not the cost. The cost was $11 plus cleaning, restemming, buffing,
photography, measurement, attribution research, listing, packing, platform fee and
the risk that it does not sell. On a pipe taking 90 minutes of skilled hands, a 4×
gross is a working wage, not a windfall.

**Conflating these two would be an expensive error**, because it leads to
apologising for a margin that is in fact thin, in a business whose real problem is
acquisition variance (below), not markup.

---

## 07. WHAT THIS DOES NOT SOLVE, AND IS BIGGER

Indexing the archive is worth roughly **half a turn of margin.**

The observed spread on a single premium 25-pipe lot — **$1,200 to $2,000 for
nominally the same thing** — is worth **two and a half turns.**

| Scenario | Cost per pipe | Ratio at $292 retail |
|---|---|---|
| Lot at $1,200 | $48 | **6.1×** |
| Lot at $2,000 | $80 | **3.65×** |

The difference between a good buy and a bad buy on a single Thursday is roughly
**five times** more consequential than the entire decade of price movement this
document is about.

**Stated plainly so it is not lost:** the deflator is worth building, and it is not
the highest-value thing on the table. Reading a lot correctly before bidding is.
Those compete for the same pair of hands.

---

## 08. WHAT COULD KILL THIS

- **Player and referee.** Largest dealer in the category also publishing the price
  index. Flagged in A2 §06 and unresolved. Indexing makes it sharper, because now
  the dealer is not just reporting prices — he is *adjusting* them upward by a
  method he chose.
- **Circular index.** §04. Fatal if unanchored, survivable if anchored.
- **Publishing indexed prices the market ignores.** Then Faridunhill is simply the
  expensive dealer with a spreadsheet. The index only works if others adopt it —
  which is an adoption problem, not a maths problem, and this document does not
  address adoption at all.
- **Gold's start-date sensitivity** used against the project by a critic. Better to
  publish the weakness first.
- **Books.** Facts from the reference library are free to use. Reproduced text and
  scanned pages are not, and a public price reference built on lifted content is
  one complaint from deletion.
- **[U] on every number here.** Nothing in §03 has been verified against source
  data. If a reviewer treats these as findings rather than illustrations, the
  review is worthless.

---

## 09. FOR THE REVIEWERS — READ THIS BEFORE RESPONDING

This file is being circulated for critique. The known failure mode of that process
is agreement: three reviewers restating the document back in more confident
language, scoring it highly, and adding nothing.

**A review that concludes this is strong is a review that has not done the work.**
The document has at least four soft spots and probably more. Find them.

**Attack these specifically:**

1. **§03 finding — "his hands already run an index at ~1.25× CPI."** This is
   inferred from *two* data points on *one* brand. Is it a finding or a
   coincidence? What would falsify it? How many observations would be needed?
2. **§04 circularity.** Is external anchoring actually sufficient, or does a
   dealer-built index in a 15,000–40,000 person market remain unusable regardless?
   Name a category where a participant-built index survived scrutiny.
3. **§05 display range.** Does showing a range read as honest, or as evasive? Is
   there evidence either way from operators who publish ranges?
4. **§07 priority claim.** Is the half-turn vs two-and-a-half-turn comparison a
   fair comparison, or is it comparing a permanent structural asset against a
   per-transaction gain and calling them the same unit?
5. **The unasked question.** Every deflator here assumes the correct current price
   is *higher* than the historical one. **What if the category is in real decline
   and the honest indexed answer is sometimes a lower number than the pipe sold
   for in 2016?** The A1 research says the collector base is dying. This document
   has no mechanism for reporting a fall, which suggests it was designed to
   justify raising prices rather than to find the truth. **This is the most
   serious objection in the file and it is raised here because a friendly reviewer
   will not raise it.**

**Do not score it. Do not summarise it back. Answer the five.**

---

## 10. THE ONE-LINE VERSION

*A price without a date is a rumour. A price with a date and a published method is
a reference. Faridunhill has 8,000 of the first and none of the second.*

---

*Ends.*
