# COUNCIL RESPONSE — MARKETING DNA (Round 2)

Brief: External AI Council — Round 2 Targeted Challenge, Advisor F (CODE)
Respondent: Advisor F
Date: 2026-07-11
Scope: F1, F2, F3 only. The five convergence points are accepted as
foundations and not re-argued.

---

## F1 — THE DELETION CONTRADICTION

The challenge is fair, and the resolution is (b) — with one concession
first: **my Round 1 deletion overshot.** As written, it would have cut the
event *ledger* along with the learning *loop*, and that violates my own
Q5 principle: sale events, like photos, are unrecoverable after the fact.
A view count can be re-polled next month; the fact that item FH-TP-034
sold in 11 days on eBay for 18% under list after two offers cannot be
reconstructed later. Deleting the ledger would have been destroying cheap,
irreplaceable data to save trivial effort.

The correct split — and what I should have written — is:

> **Record from day one. Infer only when the numbers earn it.**
> The ledger is cheap and unrecoverable. The inference layer is expensive
> and deferrable. Round 1 conflated them under one deletion.

### The minimal phenotype (day one)

**Five events, nothing else:**

| Event | Payload | Why it survives the cut |
|---|---|---|
| `listed` | sku, ts, channel, list_price | Starts the clock; enables days-to-sale |
| `price_changed` | sku, ts, old, new, reason | Reconstructs the price path to sale |
| `offer_received` | sku, ts, amount | The purest free price signal marketplaces emit |
| `sold` | sku, ts, channel, sold_price | The business's ground truth; extends the existing sold-price DB |
| `returned` | sku, ts, reason | The only negative signal worth a row |

**Explicitly excluded from day one:** views, watchers, favorites,
questions, click-throughs — the noisy engagement telemetry that requires
per-channel polling infrastructure and yields the least at low volume.
That telemetry *is* re-collectable later; it is exactly the deferrable
part.

**Cohort keys: two, fixed now** (because retro-keying is cheap but
choosing keys late invites churn): `taxonomy_node × price_band` and
`brand`. No photo-variant keys, no copy-variant keys — those belong to
the full loop.

**Size of the nightly script:** ~100–150 lines. Pull orders/offers from
eBay and Etsy APIs, ingest the own-store checkout webhook (which already
exists in this codebase), append JSONL rows, compute days-to-sale on
`sold`. This is honestly described as *the sold-price database the
founder already maintains, plus four columns* (channel, days-to-sale,
list-vs-sold delta, returned flag). It is not a new system; it is the
existing one done properly.

### The trigger condition for the full loop

Build the inference layer (signals table, generator feedback, engagement
telemetry) when **any single cohort at the `taxonomy_node × price_band`
grain accumulates 50 sold events within a rolling 12 months.** Below
that, any per-cohort "insight" is an anecdote wearing a percentage, and
an automated generator will obediently act on it.

Secondary trigger, whichever comes first: a concrete generator decision
is *blocked* by missing engagement data (e.g. "which photo role should
be hero?" cannot be answered from sold events alone). Then build only
the telemetry that unblocks that one decision — not the whole loop.

### What replaces learning until then

Three things, all already in the design: the sold-price DB (pricing
priors), the founder's own judgment encoded per-item in 15 seconds
(`why_special`, `floor_price`, condition grade), and cohort priors from
*public* comparables (completed-listing searches) that need no phenotype
infrastructure at all. A genome-plus-expression system with those three
inputs is not "a system that never learns" — it is a system whose
learning is manual, priced correctly for its data volume.

---

## F2 — THE 95.1% PROBLEM: THE OPERATIONAL QA GATE

Accepted framing: 95.1% Top-1 at 200 items ≈ 10 confident errors
published everywhere at once, in a business whose product is appraisal
accuracy. A vague gate is a skipped gate. Here is the exact gate.

### Principle: gate by consequence × confidence, and make skipping structurally impossible

**Field tiers by consequence of error:**

- **Tier A (assertable claims that move price or authenticity):** brand,
  maker, era, restricted materials. An error here is a misattribution —
  the reputation-killing class.
- **Tier B (descriptive):** shape, finish, country of origin. An error
  is embarrassing, correctable, cheap.
- **Tier C:** everything else. Never gated.

### The four routing rules

1. **Confidence rule.** Any Tier A field with model confidence < 0.90 →
   human review queue. (0.90 is a starting point, not a truth — see
   calibration note below.)
2. **Corroboration rule.** Vision classification and stamping-OCR are
   two independent extractors. If the claimed brand/era is *inconsistent
   with the verbatim stamping text*, route to review **regardless of
   confidence**. Cross-checking two extractors is the cheapest error
   detector available and catches exactly the confident-but-wrong case
   the confidence rule misses.
3. **Price rule.** Any item whose proposed list price is ≥ £150 (or the
   catalog's top quartile, whichever is lower) gets human review of all
   Tier A fields regardless of confidence. Errors on expensive items
   carry the reputation and the financial cost; buy insurance where the
   loss is.
4. **Audit rule.** A random 5% of auto-passed items also enters the
   queue, labeled as audit. Without this the gate's own false-accept
   rate is unmeasurable and the 0.90 threshold can never be calibrated.
   The gate needs its own phenotype.

Expected volume at 200 items: roughly 30–45 reviews (15–20% routing
rate). That is the honest number; plan ~20 minutes of founder time per
100 items, batched.

### What the human sees (one screen, one question)

Side-by-side, single screen:

1. The **stamping macro photos**, full zoom (this is why Q5 demanded
   them);
2. The **OCR'd verbatim stamping text**;
3. The **model's claim** — brand, era range, confidence;
4. **Two or three reference exemplars** of the claimed brand's stamping
   from the sold archive or a reference library.

One question: *"Is this stamping consistent with [Chacom, 1950–1962]?"*
Three buttons: **Yes / No / Can't tell.**

This is verification, not attribution — and verification is an order of
magnitude faster than research. Budget: **20–40 seconds per item, 30s
average.** 40 items ≈ 20 minutes per intake batch. The founder is a
domain expert; the screen exists to eliminate lookup time, not judgment.

### What happens to "Can't tell"

The item **lists anyway, and the machine does not guess.** The genome
records the honest state:

```yaml
brand: null
attribution:
  candidate: "Chacom"
  basis: vision
  status: unverified
```

Generated copy hedges by rule ("unsigned, French-made characteristics
of the period," "attributed to") — and, critically, **the price model
treats the item as unattributed**, pricing at the no-name floor for its
shape and condition. The asymmetry is the whole design: *underclaiming
costs margin; overclaiming costs the business.* A buyer who identifies
a hedged bargain is a delighted collector and a completed sale; a buyer
who receives a misattributed pipe is a return, a negative feedback, and
a story told on the forums.

One exception: if the candidate attribution would raise the price by
≥ £50 over the unattributed floor, the item goes to a **research-later
queue instead of listing** — at that spread, the expected value of a
correct attribution exceeds the carrying cost of the shelf.

### Why this gate cannot be silently skipped

It is enforced in code, not policy: **the listing generator refuses to
emit an assertive Tier A claim for any field whose provenance is
`vision` + `unverified`.** Skipping the review queue doesn't produce
wrong listings — it produces hedged listings and lost margin. The
failure mode of laziness is a visible cost on a report, not an invisible
misattribution on eBay. A gate whose bypass is self-punishing needs no
discipline to survive.

**Calibration note:** 0.90 and £150 are priors, not findings. The first
100 items — with the 5% audit — are the calibration set. If the model's
confidence is poorly calibrated (a 0.95 that is right 80% of the time),
the corroboration rule and price rule still hold the line while the
threshold is corrected.

---

## F3 — THE STRONG CLAIM UNDER FIRE

### (a) The one per-item marketing-intelligence element that earns its place

**The hook — `why_special` — one human sentence at intake.** It is the
entire per-item hook matrix collapsed to one row, and it survives
because it is the only marketing fact that is genuinely a property of
the *item* rather than of its cohort.

Everything else the other advisors propose per-item — personas,
emotional positioning, channel scores — are **cohort properties stored
at the wrong altitude.** The buyer persona of a 1958 Dunhill billiard is
identical to that of every other 1958 Dunhill-class piece; write it per
item and you have denormalized cohort data that drifts, bloats, and
violates convergence point 4 (every field names its consumer — and the
consumer of a persona is a cohort-level generator, not an item record).
Per-item marketing intelligence for one-of-ones is cohort data wearing
an item costume. One sentence of genuine item-level difference; the
rest lives on the taxonomy node.

### (b) The 90-day falsification test

The corpus-first claim predicts that buyers of one-of-ones arrive by
*search routing*, so per-item promotion buys sales that search would
have delivered free. Two measurements, one decisive:

**Decisive — the promotion test.** Enroll ~30 mid-band items (£50–150)
in per-item promotion (eBay Promoted Listings at standard rate + one
generated social post each); hold ~30 matched-cohort items unpromoted.
**Metric: 90-day sell-through rate and net margin after fees and ad
cost.** My claim is *falsified* if promoted items show a sell-through
lift of ≥15 percentage points **and** positive net margin after
promotion cost. It is *supported* if the lift is inside noise or the
margin is negative. (Honesty clause: n=30 of unique items is weak
matching — treat a marginal result as "not proven," not "proven right.")

**Supporting — the corpus test.** Publish 3–5 hub pages (brand guide,
shape guide, dating guide) generated from genomes + sold archive.
**Metric: organic impressions/clicks from Search Console routed to live
listings, and assisted sales at 90 days.** Concession up front: 90 days
is short for SEO; this test can show green shoots, not verdicts. The
promotion test is the one that can actually kill my claim inside the
window.

### (c) Where per-item promotion DOES pay — the concessions, plainly

It does not "never pay." Three concessions, each bounded:

1. **Marketplace-native promoted placement pays mechanically, above
   thresholds.** eBay Promoted Listings is not content marketing — it is
   a fee tier with zero creative cost. Automate it: enroll any item at
   price ≥ £75 *or* unsold ≥ 60 days, at a low ad-rate computed from
   margin (`cost_basis`, `floor_price` — fields already in the genome),
   with a hard ad-rate cap. This is per-item promotion requiring **zero
   new intelligence fields.**
2. **Trophy tier earns individual content.** Top ~5% by expected price
   (≥ £300) or named-collector brands (Dunhill-class, high-grade
   Charatan, notable makers): these items can carry an audience's
   attention on their own, and their margin absorbs the cost of a
   dedicated post or newsletter centerpiece. Even here, the content is
   *generated at listing time from the genome* — the concession buys the
   trophy items a generator, not a schema.
3. **Staleness rescue.** Any item unsold past 90 days has, by
   definition, not been found by search — the corpus-first mechanism has
   failed *for that item*, and individual intervention (repricing, hero
   rotation, one promotion push) is justified as the exception path.

The refined claim, restated for the record: **per-item marketing
*intelligence fields* never pay for one-of-one items; per-item marketing
*spend* pays mechanically above price and staleness thresholds, computed
from economics fields the genome already carries.** The distinction the
council should adopt is fields vs. spend — Round 1 blurred them, which
is what invited this challenge.

---

## MANDATORY OUTPUT

### THREE WEAKNESSES of my Round 2 answers

1. **The gate's numbers are priors, not findings.** 0.90 confidence,
   £150 price rule, 5% audit, £50 research-queue spread — all invented
   ahead of contact with the model's real calibration curve. If the
   vision system's confidence is badly calibrated, the routing rate
   could be 40% (queue swamps intake) or 5% (errors sail through), and
   nothing in my answer detects this before the first 100-item
   calibration set is processed.
2. **The decisive F3 experiment is underpowered and I said so myself.**
   True matching of one-of-one items is impossible; at n=30 per arm,
   sell-through differences will rarely clear noise. There is a real
   chance the 90-day window ends "not proven," and my corpus-first claim
   survives by default rather than by evidence — which is exactly the
   kind of unfalsified comfort I warned against in Round 1.
3. **The F1 trigger may never fire.** At this business's realistic
   volume, 50 sold events in one cohort within 12 months could take
   years. If so, "deferred, not deleted" is deletion with extra steps —
   my resolution of the contradiction is honest only if the founder
   accepts that the full learning loop may simply never be built, and
   the ledger's payoff horizon is long.

### THREE RISKS the founder should watch

1. **Hedged listings leak margin silently.** The "underclaim is safe"
   default means every unresolved attribution costs real money (an
   unverified Chacom priced at no-name floor), and because hedging never
   produces a visible error, the cost accumulates invisibly. Put
   "hedged-listing discount" on a monthly report — the sum of (candidate
   price − hedged price) across live hedged items — or the gate's true
   cost will never be known.
2. **The review queue becomes the intake bottleneck.** The 30-seconds-
   per-item figure holds only if reviews are batched and the reference-
   exemplar library exists. Without exemplars, each review silently
   becomes a ten-minute research session, the queue backs up, and the
   founder starts approving on fatigue — which is how gates die in
   practice even when they cannot be skipped in code.
3. **Automated ad spend ratchets.** The staleness-triggered Promoted
   Listings rule is a machine authorized to spend money on every item
   that isn't selling — precisely the inventory with the worst return on
   spend. Without a hard ad-rate cap and a monthly total-spend ceiling
   in the same class as `floor_price` ("numbers the machine must never
   cross"), the automation will buy sales the corpus would have
   delivered free, and the F3 experiment's numbers will be poisoned by
   its own remedy.

### ONE DELETION

**The controlled 90-day promotion experiment.** If forced to simplify,
cut the A/B scaffolding first: at this catalog size it is science
theater — underpowered, unmatchable, and consuming setup effort that
proves little. Replace it with the cheap version: switch low-rate
Promoted Listings on for everything above the price threshold, read
eBay's own promoted-vs-organic attribution reports after a quarter, and
let the corpus test run in the background. Keep the QA gate and the
five-event ledger — those are load-bearing. The experiment was always
scaffolding.

---

FARID OS — Council Response Round 2 — Advisor F (CODE)
