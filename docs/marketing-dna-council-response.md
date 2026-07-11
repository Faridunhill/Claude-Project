# COUNCIL RESPONSE — MARKETING DNA (Round 1)

Brief: External AI Council — Marketing DNA, 2026-07-10
Respondent: independent AI advisor (Claude)
Status: proposal from zero, no clarifying questions asked

---

## Assumptions (stated, not asked)

1. Scale is hundreds of items per business, not millions. Flat files in git
   (as this repo already uses) are an acceptable store for years yet.
2. Channels in play: eBay, Etsy, own store, email, organic social. Paid ads
   are marginal for tobacco-adjacent goods (most ad networks prohibit them).
3. The founder plus local agents do all data entry; there is no staff to
   feed a heavy schema.
4. The AI vision system, taxonomy, and sold-price database mentioned in the
   brief are real and reachable by nightly scripts.
5. "Marketing" here means: titles, descriptions, tags, channel placement,
   pricing moves, email/social content, and SEO corpus — not paid funnels.

## The verdict first

The premise is half right. A product record should be **born with every
FACT marketing will ever need — and none of the marketing itself.**

The trap hidden in "created at birth with everything automated marketing
will ever need" is that it invites you to store *marketing artifacts*
(titles, descriptions, tags, angles, channel copy) in the record. Do that
and you freeze July-2026 prompt quality into every product forever, and
every improvement to your generators demands a migration of stored content.

The correct model is three layers, only the first of which is "DNA":

| Layer | What it is | Written | Mutability |
|---|---|---|---|
| **GENOME** | Facts about the physical object | At entry, once | Immutable (error-corrections only, logged) |
| **EXPRESSION** | Generated marketing content (titles, copy, tags, posts) | Any time, by machines | Disposable, versioned, regenerated at will |
| **PHENOTYPE** | What the market did (views, offers, sale, returns) | After listing | Append-only event log |

Marketing content is a *function of the genome*, computed as late as
possible, as often as the generators improve. Capture facts once; generate
marketing a thousand times. Everything below follows from this.

Evidence from the founder's own repo that the collapsed-layer model is
already causing damage:

- `rating: '4.5'` is a **schema default** with `reviewCount: 0` — fabricated
  phenotype, born into every record. That is fake social proof on every
  product page: a trust, platform-policy, and consumer-protection liability.
  Delete the default today.
- `description` is identical boilerplate across items — expression stored
  as if it were genome, so it can never be regenerated per-item without a
  migration.

---

## Q1 — THE SCHEMA (the genome, concretely)

Every field below is a fact about the object, with the downstream marketing
function it feeds. Types are indicative; store in YAML/JSON as the repo
already does.

**Identity & classification**

| Field | Type | Example | Feeds |
|---|---|---|---|
| `sku` | string, immutable | `FH-TP-034` | Join key for expression, phenotype, sold-price DB |
| `taxonomy` | path from controlled tree | `pipes/estate/dublin` | Channel category mapping, store nav, SEO hub pages, **cohort learning key** (see Q3) |
| `brand` | string from controlled list | `Chacom` | Brand hub pages, search keywords, price benchmarking against sold DB |
| `model_line` | string | `Gentleman 836` | Collector SEO (shape-number searches convert), authentication content |
| `country_of_origin` | ISO string | `FR` | Marketplace item specifics, customs, "French briar" keywords |

**The forensic core (unique-item businesses live or die here)**

| Field | Type | Example | Feeds |
|---|---|---|---|
| `stampings_verbatim` | string, exactly as marked | `CHACOM / GENTLEMAN / 836 / FRANCE` | The anchor fact. Era attribution, authentication copy, collector search terms. Everything else can be re-derived from this plus photos. |
| `era` | `{min_year, max_year, basis}` | `{1950, 1962, "stamping style"}` | Never a point estimate. Feeds "circa" claims in copy, `vintage`/`antique` keyword eligibility (antique = 100y+, a legal claim), price-band selection. `basis` decides whether copy may assert or must hedge. |
| `materials` | enum array | `[briar, vulcanite]` | Filters, keywords, **compliance** — amber, horn, ivory-like materials trigger CITES/marketplace restrictions |
| `measurements` | object, SI units | `{length_mm: 148, weight_g: 41, chamber_mm: 19}` | Marketplace item specifics, size-filter buyers, shipping cost automation |
| `condition_grade` | enum: `mint/excellent/very_good/good/fair/project` | `very_good` | Price model input, title modifiers, buyer-expectation setting |
| `flaws` | controlled vocab array | `[rim_darkening, tooth_marks_light]` | The honesty layer: auto-disclosed in copy, mapped to flaw photos. Prevents returns and feedback damage — which are marketing outcomes. |
| `condition_notes` | free text (dictated) | "cleaned, sanitized, stem re-polished" | Copy generation detail |
| `provenance` | free text + optional structured `{collection, estate}` | "single-owner Bristol estate" | Story generation, trust content |

**Media (photos ARE the DNA — see Q5)**

| Field | Type | Example | Feeds |
|---|---|---|---|
| `media[]` | `{url, role, seq}` where role ∈ `hero/angle/stamping/flaw/scale/group` | — | Hero-image selection per channel, Etsy image-allowlist compliance (already in this repo), flaw-photo pairing with `flaws[]`, alt-text generation |

**Economics (marketing without margin awareness is spend, not marketing)**

| Field | Type | Example | Feeds |
|---|---|---|---|
| `cost_basis` | money | `22.00` | Margin-aware promotion: which items can absorb a sale, offer-acceptance floors |
| `list_price` | money | `99.00` | Baseline |
| `floor_price` | money, human-set | `55.00` | The one number automation must never cross. Enables fully automated repricing/offers safely. |
| `acquired_at` | date | `2026-06-30` | Staleness-triggered promotion ("90 days unsold → rotate hero photo, cut 10%") |

**Compliance facts (store facts, derive eligibility)**

| Field | Type | Example | Feeds |
|---|---|---|---|
| `compliance` | `{age_restricted: bool, smoking_related: bool, restricted_materials: []}` | `{true, true, []}` | A rules engine maps facts → per-channel eligibility. Never store "allowed on Etsy: yes" — that answer changes when Etsy changes, and then you're migrating records instead of one rule. |

**The one human marketing judgment**

| Field | Type | Example | Feeds |
|---|---|---|---|
| `why_special` | one sentence, human-written | "Unsmoked 1950s French shop stock — the sandblast is factory-fresh" | The seed of every generated narrative. The single per-product fact machines cannot reliably infer. One sentence, 15 seconds, at intake. |

**Data about the data**

| Field | Type | Feeds |
|---|---|---|
| `field_provenance` | map: field → `{source: human/vision/inferred, confidence, ts}` | Decides what generated copy may *assert* vs must *hedge* ("stamped Dunhill" vs "attributed to"). Without this, one vision error propagates to every channel with full confidence — the single biggest automation risk for collectibles. |

That's ~20 fields. Deliberately absent: target audience, tone, channel
copy, keywords, campaign flags, "marketing angle." All of those are
expression — computable from the genome, better next year than this year.

## Q2 — UNIQUE vs. REPEATABLE vs. DIGITAL

One shared core, three thin extensions — but the real divergence is not
fields, it is **where learning attaches**, and getting that wrong is fatal.

**Shared core** (all three businesses): `sku`, `taxonomy`, `brand`,
`media[]`, `economics`, `compliance`, `why_special`, `field_provenance`.

**Unique items (estate pipes):** add the forensic core — `stampings`,
`era`, `condition`, `flaws`, `provenance`. Quantity is always 1; "sold" is
a terminal state, and the record then becomes an *asset* (sold-price
comparable + SEO archive page), not garbage. Scarcity is the marketing
angle and it's structural.

**Repeatable stock (men's goods):** drop the forensic core; add
`variants[]` (size/color), `inventory_qty`, `reorder_point`, `supplier`.
Reviews and UGC accumulate on the product. A/B testing of copy and photos
is *possible* because the product persists across many sales.

**Digital reports (property intelligence):** the "product" is an offering,
not inventory. DNA lives at the offering level (deliverable spec,
turnaround, jurisdictions covered, sample report). Marketing is about the
*buyer's parcel*, not your product — the funnel and its content are the
asset. Forcing this into a per-item schema produces one lonely record and
a system that doesn't fit.

**The learning-granularity law** (the actual answer to this question):

- Unique items: an item sells once — n=1 forever, per-item A/B is
  impossible. Learning attaches to **cohorts** (taxonomy node × brand ×
  price band).
- Repeatable stock: learning attaches to the **product** (this photo
  converts, this title wins).
- Digital service: learning attaches to the **funnel stage** (this landing
  page, this proof element).

Share the core schema and the *method*; give each business its own
extension and its own learning key. Since the businesses are firewalled
anyway, this costs nothing.

## Q3 — WHAT MACHINES CANNOT KNOW AT BIRTH

Separation mechanism: the three layers are **physically separate stores**,
joined only by `sku`.

1. **Genome** — written at entry, immutable. Corrections allowed (a
   stamping was misread), but as logged corrections, never silent edits,
   and never performance-motivated ("it sells better if we call it 1940s"
   is fraud, and an automated system will happily industrialize it).
2. **Phenotype** — append-only events, one row per observation:
   `{sku, ts, channel, event, value}` — listed, viewed, watched, favorited,
   offer_received, question_asked, price_changed, sold (price,
   days_to_sale), returned. Cheap to collect from channel APIs nightly.
3. **Learned signals** — the feedback mechanism, and the key design move:
   **learned data never flows back into the product record.** A nightly
   job aggregates phenotype events into a signals table keyed by *cohort*,
   not by item: e.g. `(taxonomy=estate/dublin, price_band=75–125) →
   median_days_to_sale: 34; stamping-macro-as-second-photo → +9pp
   watch rate`. Generators read the signals table at generation time.

Why cohorts and not items: with unique inventory, per-item learning is
structurally impossible (the item is gone the moment you have your first
conversion datapoint). The item's sale teaches you about its *cohort*, and
the cohort teaches the next generation of listings. The existing sold-price
database is already a phenotype store — this formalizes it.

Effect: the record is never "updated by learning." The *generators* get
smarter; any item's expression can be regenerated tomorrow with everything
the whole store learned this month.

## Q4 — THE FAILURE MODES

Where these systems actually die, in observed order of lethality:

1. **Storing generated content as source data.** Copy gets hand-tweaked in
   place, the genome and the live listing drift apart, nobody knows which
   is true, regeneration becomes destructive, system abandoned. *Forbid:
   hand-editing expression. A bad description means fixing the genome or
   the generator, then regenerating.* (This repo's uniform boilerplate
   `description` field is this failure, pre-paid.)
2. **Fields for imagined futures.** Forty fields designed for channels you
   might use in 2028; 90% null; nulls read as facts ("no flaws recorded" ≠
   "no flaws"). *Forbid: any field without a consumer that exists, or will
   exist within 30 days.*
3. **Validation theater.** Required fields block intake, so humans enter
   garbage to pass the gate — and garbage is worse than null because it
   wears the costume of data. *Forbid: more than ~5 required fields. Use a
   completeness score per record instead; let generators degrade
   gracefully ("era unknown" → copy omits era claims).*
4. **Free text where enums belong, enums where free text belongs.**
   `condition: "pretty good"` × 200 spellings kills every filter and
   cohort; conversely an enum for `provenance` amputates the stories that
   sell estate goods. Rule: **if a machine branches on it, enum. If a
   machine narrates from it, text.**
5. **No field-level provenance.** Once vision-guessed and human-verified
   facts are indistinguishable, one bad guess poisons trust in the whole
   record, and humans start re-checking everything — the automation
   dividend evaporates.
6. **Fabricated phenotype.** Seeded ratings, fake review counts, inflated
   scarcity. Kills buyer trust, risks platform bans, and poisons your own
   learning loop with signals you invented. (Live in this repo today:
   `rating` defaults to 4.5 with zero reviews.)
7. **Taxonomy churn.** Reorganizing categories quarterly orphans every
   cohort statistic. Version the taxonomy; map old→new; never renumber.

Forbidden from day one, summarized: hand-edited expression; speculative
fields; >5 required fields; performance-motivated genome edits; per-item
custom fields; stored channel-eligibility answers; fabricated social proof.

## Q5 — MINIMUM VIABLE DNA (200 items, this week)

Governing principle: **capture only what requires the physical object in
your hand.** Everything else is recoverable later by machines from photos,
forever, at near-zero cost. Re-touching 200 items is expensive; re-running
a vision model over 200 photo sets is a nightly script.

Per item — roughly 3 minutes:

1. **`sku`** — assigned, on a tag, in the photo frame. (10 sec)
2. **Photos, over-shot to a fixed checklist** — 8–12 frames: all angles,
   **macro of every stamping**, every flaw close-up, one frame next to a
   ruler, one frame **on the scale with the readout visible** (weight
   captured as a photograph — no typing), group shot if lotted. Photos are
   the true DNA; a missed stamping macro is the one genuinely
   unrecoverable loss once the item ships. (2 min)
3. **`cost_basis`** — you will not remember it in October. (5 sec)
4. **30-second dictated voice note** — condition in your own words, any
   provenance, anything odd. Whisper-transcribed nightly; agents
   structure it into `condition_notes` / `flaws` / `provenance` later.
5. **`why_special`** — one spoken sentence, same voice note.
6. **`floor_price`** — one number, enables safe automation later. (5 sec)

Explicitly do **not** do this week: titles, descriptions, tags, era
research, brand attribution, taxonomy assignment, channel decisions.
The existing vision system + stamping macros + voice transcript can
generate all of it later, and will do it better later than you would
manually now.

The asymmetry to respect: a skipped photo is unrecoverable after sale; a
skipped *field* is a cheap batch job. When rushed, shoot more frames and
type less.

## Q6 — WHAT YOU DIDN'T ASK

**"Should marketing target individual products at all?"**

For the unique-inventory business, mostly no — and this reframes what the
DNA is *for*. An estate pipe sells once, usually to someone who searched
for it. Per-product promotion (ads, posts, campaigns) for a one-of-one has
almost no ROI: the audience is whoever is searching *this month* for that
brand/shape, and marketplace search already routes them to you if the
listing data is right.

The durable marketing assets for a one-of-one dealer are **corpus-level**,
compiled from product genomes in aggregate:

- Brand and shape hub pages ("Chacom shape guide," "dating Dunhill
  stampings") that rank for collector searches and route buyers to live
  inventory — generated from genomes + sold archive.
- The **sold archive** as public SEO surface: every sold item's page
  persists as a comparable-price reference collectors link to and search.
  Your sold-price database is a marketing asset wearing a spreadsheet
  costume.
- Newsletter/social generated from *cohorts of new arrivals*, not items
  ("six French estates entered the shop this week").

So the per-product DNA's chief marketing job is not to promote the product.
It is (a) to make marketplace/search listing data flawless at zero marginal
human cost, and (b) to be **feedstock for the corpus**. The men's-goods
store inverts this — repeatable products reward per-product promotion —
which is one more reason the businesses must not share one marketing
playbook just because they share a schema method.

---

## MANDATORY OUTPUT

### THREE WEAKNESSES of my own proposal

1. **The three-layer architecture has real carrying cost.** Genome /
   expression / phenotype separation demands plumbing and discipline from a
   solo founder. Under deadline pressure the layers will want to collapse
   back into one record — the design fights the operator's natural
   behavior, and I have no enforcement mechanism beyond convention.
2. **Cohort learning may never reach significance.** At hundreds of sales
   per year spread across a deep taxonomy, most cohorts get a handful of
   data points. The signals table risks producing noise dressed as insight,
   and an automated generator will obediently act on that noise.
3. **The MVP leans hard on later machine extraction.** If vision accuracy
   on stampings, era, and brand attribution is worse than assumed, the
   backfill cost I claimed to eliminate returns as per-item QA review —
   possibly exceeding what honest manual entry would have cost this week.

### THREE RISKS the founder should watch

1. **Automation launders errors at scale.** One misread stamping becomes a
   confident misattribution on every channel simultaneously. In
   collectibles, misdescription means returns, feedback damage, and
   marketplace suspension. The `field_provenance` hedging rule is the
   guardrail — it only works if generators actually respect it.
2. **Channel-policy shock.** This is a tobacco-adjacent catalog. Etsy,
   eBay, and payment processors change smoking-goods policy abruptly and
   retroactively. A marketing system optimized for today's channels can
   lose its primary channel in one policy email. The own-store and the
   email list are the only channels you own; weight investment
   accordingly.
3. **Silent judgment decay.** The system needs three human inputs per item
   (`why_special`, `floor_price`, condition grade). When the founder gets
   busy and stops supplying them, the machine keeps publishing — with
   blander copy and unsafe pricing floors — and nothing visibly breaks.
   Monitor input completeness like uptime. And delete the fake 4.5-rating
   default this week; it is the one item here with legal teeth.

### ONE DELETION

**The phenotype layer and its learning loop.** If forced to simplify, cut
it first — keep only the sold-price archive you already have. Genome +
regenerable expression delivers roughly 90% of the value; closed-loop
learning is where systems like this go to die of ambition, and at this
sales volume its statistical yield is the weakest part of my own proposal.
Build it in Round 3, if the data volume ever justifies it.
