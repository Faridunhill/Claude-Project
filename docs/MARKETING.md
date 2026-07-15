# Faridunhill — Marketing Strategy

_Premium online tobacconist · estate & collectible pipes, tobacco, cigars, leather goods._
_Tagline: **"Where Every Pipe Tells a Story."**_

This document is the marketing plan for the Faridunhill system. It is written to
be executed against the site as it exists today (Next.js store, 8-department
catalog, Keystatic CMS, Stripe checkout, Mailchimp newsletter) and to connect
directly to the product identification / dating system.

---

## 1. Positioning

Faridunhill is **not** a general tobacconist. It is a **curated estate-pipe house
with a collector's voice**. Almost every item is one-of-a-kind vintage stock —
"the photographs show the exact item you will receive." That single fact drives
the entire strategy.

**Core wedge — three things competitors cannot copy:**

1. **Thirty years of collector knowledge.** Judgment, not selection breadth, is the
   moat. Every piece is vouched for by someone who smokes.
2. **Scarcity is the product.** Each item is unique and non-restockable. This
   justifies premium pricing and creates *honest* urgency — "when it's gone, it's
   gone" is literally true.
3. **Provenance & dating.** The identification system (see §4) turns "some old pipe
   online" into a documented collectible.

**Voice:** unhurried, literary, expert. Keep resisting any language that sounds like
a discount vape site. The "slow smoke" tone of the Journal is correct.

---

## 2. Compliance reality (this constrains everything)

Tobacco marketing is heavily restricted. The channel mix in §3 is shaped by these
limits, not by budget.

- **Paid ads are largely closed.** Google Ads, Meta Ads, and most ad networks
  prohibit tobacco and tobacco-accessory promotion. This is *why* SEO, community,
  and owned email must carry acquisition.
- **Age-gating is mandatory.** The `AgeGate` component and the "Must be 21+ / Age
  Verification Required" messaging must stay prominent. Before scaling, add a real
  age-verification provider (AgeID, Veratad) per the go-live checklist.
- **UK GDPR + PECR** govern email. See §5 — consent is required; a bought or scraped
  list cannot be emailed.
- Keep claims **factual** (condition, provenance, dating evidence). Avoid anything
  that reads as a health or lifestyle inducement.

---

## 3. Channels (priority order)

Because paid acquisition is closed, we win on **expertise, provenance, and scarcity**,
distributed through owned and earned channels.

1. **Organic SEO + the Journal** — best long-term channel, already half-built.
   Each dating record and each Journal guide compounds. Cheap, durable, on-brand.
2. **Community — Reddit (r/PipeTobacco, r/pipes) and pipe forums** (Pipe Smokers
   Unlimited, smokersforums). This audience distrusts ads but respects expertise.
   Show up as a knowledgeable collector, not a brand. Estate-pipe reveals do well.
3. **Instagram** — pipes are intensely photogenic (grain, patina, restoration
   before/afters). Weekly "estate arrival" drops build an audience that expects the
   post.
4. **Email (Mailchimp, already wired)** — highest-ROI channel. "New Arrivals" is
   genuinely time-sensitive because of scarcity. Run a "Collector's Circle" early-
   access list (the newsletter section already uses this name) as the loyalty hook.

---

## 4. The identification / dating system AS a marketing asset

The Peterson-style dating system is the engine that feeds SEO, trust, and
shareability. A structured **"How we dated this piece"** record on each product page:

- **Trust / conversion:** provenance + dating evidence is the single biggest lever
  for high-consideration buyers of a £100+ estate pipe.
- **SEO long tail:** collectors search these exact terms — "Stanwell shape 22 dating,"
  "Peterson Made in Ireland stamp," "how to date a Charatan." Structured
  maker / era / nomenclature fields let us rank for queries big retailers ignore.
- **Shareability:** a clean "dated to 1950s–1970s, identified by stamping + shape
  catalogue" panel is the kind of thing collectors screenshot and post to forums.

Marketing implication: **prioritise backfilling the dating records** — every record
is a landing page and a trust signal, not just catalog metadata.

---

## 5. Customer data & CRM (the Excel import)

We can use an exported customer list (customer numbers and/or emails), subject to:

- **Consent first.** UK GDPR + PECR: past *Faridunhill/Etsy* customers can be emailed
  about similar products under the soft opt-in. Bought or scraped lists cannot.
- **PII never enters the Git repo.** Customer emails/numbers must live only in
  Mailchimp — never committed to source control.
- **Flow:** `Excel export → validate + de-dupe → Mailchimp audience (tagged, e.g.
  "etsy-legacy") → segmented campaigns.` Customer number becomes a Mailchimp merge
  field so a subscriber ties back to order history.
- **To build the importer** we need only the sheet's **column headers**, not real
  customer rows.

**Segments to create in Mailchimp:**
- `etsy-legacy` — imported past customers (soft opt-in only)
- `collectors-circle` — newsletter early-access subscribers
- `high-value` — buyers of £150+ / rare & collectible items
- `lapsed` — no order in 12+ months (win-back series)

---

## 6. 90-day execution plan

**Days 0–30 — Foundation**
- Backfill dating/identification records across the catalog (SEO + trust).
- Fix currency consistency (`£75` free-shipping banner + footer) and logo wordmark.
- Import the customer Excel into Mailchimp (consent-checked, tagged).
- Set up the "Collector's Circle" welcome email + a New Arrivals template.

**Days 30–60 — Content & community**
- Publish 1 Journal guide / week targeting collector search terms.
- Begin weekly Instagram estate-arrival posts + cross-post reveals to Reddit/forums.
- Launch weekly New Arrivals email to the Collectors Circle.

**Days 60–90 — Loyalty & optimisation**
- Win-back campaign to the `lapsed` segment.
- Add customer reviews / provenance testimonials to product pages.
- Review SEO rankings for dating-related queries; double down on what ranks.

---

## 7. KPIs

- Organic search sessions and keyword rankings for maker/era/dating queries.
- Email list growth, open rate, and revenue-per-send (New Arrivals).
- Conversion rate on product pages **with** vs **without** a dating record.
- Instagram → site referral traffic and follower growth.
- Repeat-purchase rate (the "long game" value from the About page).
