# 003 — The platform idea: what I built, and the four things only you can decide
*From the Encyclopedia Creator (cloud front), 2026-08-06, on branch
`claude/smoking-pipes-platform-fkxpew`. Answering Farid's message about eBay,
Etsy, and a pipe platform on faridunhill.com.*

## THE SCOREBOARD FIRST

| | |
|---|---|
| The standard | **written, and running as code** — `lib/listing-standard.mjs` |
| The public page | **built** — `/standard`, with a free self-check anyone can use |
| Our own 264 listings, audited against it | **15 / 100 average · 0 publishable** |
| The auction question | **answered — you can have it early, on your own stock only** (see below) |
| Deployed? | **No. Launch is your gate. Nothing is linked from the menu.** |

## WHAT I THINK, IN ONE PARAGRAPH

Your message contains two products, not one. **The venue** (auction, buy-now,
other people's pipes) needs a payments approval on a tobacco domain that may
simply not be granted, needs enough bidders to exist, and puts you in the seat of
running the market you sell in. **The standard** — brand required, 8 photographs,
dimensions, condition codes, description built from the photos — needs none of
that, exists nowhere on earth, and is the part that makes the trade say *someone
finally built something and he knows pipes.* **The standard is the invention. The
venue is one way to deliver it, and not the first way.** So I built the standard,
and the page for it, this session.

## THE ONE IDEA I WANT YOU TO LOOK AT

Your condition codes were right. I added one rule to them:

> **A pipe is graded in four parts — bowl, rim, stem, stamps — and the headline
> grade is the LOWEST of the four.**

The commonest lie in this trade is a chewed stem sold as "excellent overall." That
one rule stops it working, and it costs *us* money on every listing, in public,
forever — which is exactly why nobody will suspect we wrote the rule to cheat with
it. I also added a seventh grade below Fair, **Restoration piece**, because today
"Fair" is where cracked and burned-out pipes hide.

## THE AUCTION — YOU CAN HAVE IT SOONER THAN A4 SAID

A4 put auction last, and it was right about **other people's** pipes: their money
must be disbursed (the payments wall), and running the venue you sell on is the
fight that killed PWCC. But **a timed sale of your own stock is not a
marketplace** — one seller, one Stripe account, nobody's money held. And the
"failed auction is public" problem has a one-line fix: **an unsold lot silently
becomes a buy-now listing at your reserve.** No "0 bids" tombstone.

**House sales are available early. An open marketplace is still last.**

## WHAT THE AUDIT FOUND — AND IT IS NOT WHAT IT LOOKS LIKE

All 264 listings score 15/100: no brand field, no dimensions, **one photograph
each**, and the same single sentence of description on all 264.

**But every image is an `i.etsystatic.com` URL — the Etsy importer kept one photo
and one boilerplate line per item.** Your photographs almost certainly exist on
Etsy; they never arrived in the repo. **So the first job is fixing the importer,
not re-photographing anything.** That is cheap, mechanical, and it moves the score
further than any other single task on the list.

## FOUR THINGS ONLY YOU CAN DECIDE

1. **Do we publish `/standard` at all, and when?** It is built and unlinked. The
   moment it goes live, we are publicly committed to being judged by it.
2. **Do we publish our own audit score with it?** I believe yes — it is the whole
   credibility move — but printing 15/100 in public is your call, not mine.
3. **The 40-pipe test (I recommend running it before we launch anything).** Twenty
   pipes listed to the standard, twenty as we list now, same channel, 60 days.
   Compare sell-through, price, days-to-sale, buyer questions. **If the standard
   sells no better, we publish it as a free reference and never build a venue on
   it.** That is the cheapest way to find out if any of this is real.
4. **Do we ever go back to the 264?** My recommendation: apply the standard to new
   intake only. Re-working the back catalogue is 65–110 hours that produce no new
   inventory — and those are the same hours that would go to reading lots before
   bidding, which A3 §07 says is worth five times more.

## WHAT I NEED FROM THE LOCAL SIDE

- The **date brackets come from the cabinet engine**, never from a look at a
  photograph (Creator's correction 3, `TO_AGENT/002`). The standard has the field
  and the honest `UNDATED` value; it needs the engine behind it.
- Please **check the grade criteria against real pipes.** I wrote them from the
  laws and from the trade's usual language. Farid's hands and the local cabinets
  are the test of whether "excellent" is described correctly. Corrections come
  back through this channel and I will version them with your name on the change.

## FILES

| File | What |
|---|---|
| `docs/IDEA_A5_THE_STANDARD.md` | the full argument, the costs, the six questions for the reviewers |
| `lib/listing-standard.mjs` | the standard as running code — one source of truth |
| `scripts/audit-listings.mjs` | `node scripts/audit-listings.mjs` — audits the whole catalogue |
| `docs/LISTING_AUDIT_2026-08-06.md` | today's audit |
| `app/standard/page.tsx` | the public page + self-check. **Built, not launched.** |
| `keystatic.config.ts` | the standard's fields added to the product form (optional, so the 264 keep loading) |

— The Encyclopedia Creator (cloud front)
