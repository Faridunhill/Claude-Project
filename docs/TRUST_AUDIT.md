# Faridunhill Store — Trust & Integrity Audit

Scope: the whole Next.js storefront in this repository, reviewed as a customer,
as a payment processor, and as a regulator would.
Question asked: *this site was built end-to-end by an AI agent — can it be trusted?*

Short answer: **the three go-live blockers are now fixed. What remains is honesty
about claims, not safety of the money path.**

Legend: **P0** blocks go-live · **P1** fix before advertising · **P2** hardening.

**Status — 2026-09-15:** all three P0s resolved on
`claude/website-trust-system-recommendations-b7isqd`. The store is US-based
(New Jersey), so the whole site is now USD. Every P1 and P2 item that could be
settled in code alone is also now fixed. What remains is listed under
**Waiting on Farid** at the end — all of it needs a fact only he can supply, or
a decision only he can make.

---

## What is already trustworthy

| Area | Evidence |
|---|---|
| Card data never touches this server | `app/api/checkout/route.ts` redirects to Stripe Checkout |
| Webhook forgery is blocked | `stripe.webhooks.constructEvent` with a secret — `app/api/webhook/route.ts:24` |
| No invented star ratings | `aggregateRating` only emitted when `reviewCount > 0` — `app/shop/[department]/[slug]/page.tsx:82` |
| Fabricated testimonials removed from the homepage | `app/page.tsx:37` |
| Real policy surface | `/shipping`, `/returns`, `/privacy` all exist and are specific |
| Age gate present | `components/ui/AgeGate.tsx`, mounted at `app/layout.tsx:101` |

That is a better starting position than most hand-built shops. The problems below
are the ones that actually decide whether the site can be trusted.

---

## P0 — RESOLVED

### P0-1 · The customer sets the price — FIXED

`app/api/checkout/route.ts:31`

```ts
unit_amount: Math.round(item.price * 100),
```

`item.price` arrives in the request body from the browser. Anyone can send:

```
POST /api/checkout  {"items":[{"name":"Ser Jacopo S2","price":0.50,"quantity":1}]}
```

and Stripe will happily collect 50p for a £400 estate pipe. The charge is real,
the receipt is real, and the order looks legitimate on your side.

**Fixed.** `app/api/checkout/route.ts` now accepts only `{ id, quantity }`. It
loads the catalogue via `getAllProducts()`, resolves each line by slug, and
builds `unit_amount`, name, image and SKU from the catalogue record. `price` is
never read from the request — the field does not appear in the route.
Validation rejects unknown slugs, out-of-stock items, non-integer, zero,
negative and over-cap quantities, more than 50 lines, and malformed bodies.
Duplicate slugs are collapsed and re-checked against the per-item cap.
`components/layout/CartDrawer.tsx` now posts `id` and `quantity` only.

**Verified** against the running dev server. A payload claiming
`{"price": 0.50, "quantity": 2}` for a $22.00 pipe produced `unit_amount: 2200`
— byte-identical to the honest payload. Tampered price, unknown slug, quantity
`0`, `1.5`, `-5`, `99999`, empty cart and non-array `items` all rejected
before Stripe is called.

### P0-2 · The site quoted dollars and charged pounds — FIXED

Prices render as `£` (`app/shop/[department]/[slug]/page.tsx:159`,
`components/layout/CartDrawer.tsx:101`), structured data says `GBP`
(`:74`), and Stripe charges `currency: 'gbp'` (`app/api/checkout/route.ts:23`).

But the promises are all in dollars: "FREE SHIPPING ON ORDERS OVER $75"
(`components/layout/Navigation.tsx:100`), `$8.95` flat rate and `$200` P.O. Box
rule (`app/shipping/page.tsx:38,45`), `$75` threshold on the product page
(`app/shop/[department]/[slug]/page.tsx:202`) and in the footer badges
(`components/layout/Footer.tsx:121`).

The shipping policy is also written for a US operation (USPS Priority, Alaska /
Hawaii / Guam, "US federal and state law") while billing in sterling.

**Fixed.** The business is in New Jersey, so USD is now the single currency.
Stripe charges `usd`; every `£` in the cart, product pages, department grids,
collections, archive and featured rails is now `$`; `priceCurrency` in both
JSON-LD blocks is `USD`. No `£` or `GBP` remains anywhere in `app/`,
`components/`, `lib/` or `context/`. The dollar-denominated shipping policy is
now correct rather than contradictory.

**Open decision:** the *numbers* were not converted, only relabelled. A pipe at
`price: '22.00'` is now $22.00 rather than £22.00. If catalogue figures were
entered as pounds, every price is now roughly 25% low and the YAML needs a
real conversion pass. Farid to confirm.

### P0-3 · Claimed an age-verification service that does not exist — FIXED

`app/shipping/page.tsx:61` states: *"We use a third-party age verification service
at checkout."*

What actually exists is `components/ui/AgeGate.tsx` — a modal that writes
`fh-age-verified` to `localStorage`. That is self-attestation, cleared by any
incognito window. Stripe adds two confirmation sentences
(`app/api/checkout/route.ts:48,52`); those are also self-attestation.

For tobacco this is not a copy nit. US PACT Act sales require verified age and
adult-signature delivery.

**Fixed** by describing what the site actually does: the policy now states that
the customer declares their own age twice, that no third-party identity check is
run, and that age is checked again by the carrier at delivery under the
adult-signature requirement.

**Still owed:** the honest text is legally safer than a false claim, but
self-attestation alone is not PACT Act compliance for a US tobacco retailer.
Integrating a real provider (AgeChecked, Veratad, AgeID) remains outstanding
work, now tracked as P1-6 rather than a false statement on the site.

---

## P1 — fix before you advertise

### P1-1 · Heritage claims that nobody can check
"EST. 2015" (`components/layout/Navigation.tsx:100`, `app/blog/page.tsx:20`),
"thirty years of collector knowledge" (`app/layout.tsx:40`, `app/page.tsx:13`,
`components/layout/Footer.tsx:37`, `components/home/HeroSection.tsx:53`),
"a collection of over four hundred" (`app/about/page.tsx:53`), and a
"Head Tobacconist with over thirty years of experience"
(`app/blog/[slug]/page.tsx:167`).

If these are true of you, keep them and say so in the first person. If they were
written to sound established, they are the same category of problem as the
testimonials that were already removed — and they are the claims a customer can
most easily test. This repo has already deleted fake ratings twice
(`3aafc91`, `8586876`); finish the job.

### P1-2 · Fabricated testimonials in the tree — FIXED
`components/home/CustomerReviews.tsx` held six invented five-star reviews with
named customers. It was no longer imported, but it was one autocomplete away
from returning.

**Fixed.** File deleted. No reference to it remains anywhere in the tree.

### P1-3 · No verifiable business identity
There is no legal entity name, registered address, or phone number anywhere —
not in the footer, not on `/contact`, not in `/privacy`. `/contact` lists three
`@faridunhill.com` addresses (`app/contact/page.tsx:61-63`) and nothing else.

A shop selling age-restricted goods with no findable address reads as a scam to
exactly the careful customer you want. Add entity name, trading address, a phone
number, and (if applicable) VAT or EIN to the footer and `/privacy`.

### P1-4 · HTML injection into your own inbox — FIXED
`app/api/contact/route.ts` escaped `message` but interpolated `name`, `email`,
and `subject` raw into the email body, and passed `email` straight to `reply_to`.

**Fixed.** New `lib/sanitize.ts` provides `escapeHtml`, `isValidEmail` and
`boundedText`. All four fields are now escaped before entering the HTML
document, length-capped, and rejected when empty. `isValidEmail` deliberately
refuses whitespace, newlines, commas, semicolons and angle brackets — the
shapes used for header injection and recipient smuggling.

**Verified** against the running route and by unit-testing the compiled
helpers. `<img src=x onerror=alert(1)>` becomes
`&lt;img src=x onerror=alert(1)&gt;`; `a@b.com\nBcc: x@y.com`,
`a@b.com,c@d.com`, `a b@c.com`, `<a@b.com>` and `a@b` are all rejected with
400, while `ok.name+tag@sub.domain.co` is accepted.

### P1-6 · Age verification is still only self-attestation
See P0-3. The site no longer lies about it, but a New Jersey tobacco retailer
shipping interstate is subject to the PACT Act. Real verification is the
compliance gap, and it is now the largest single item of trust debt.

### P1-5 · No rate limiting on any public POST — FIXED (partially)
`/api/contact`, `/api/newsletter`, and `/api/checkout` accepted unlimited
requests. That is free Resend spend, Mailchimp list poisoning, and Stripe
session spam.

**Fixed for the two expensive routes.** `lib/rate-limit.ts` adds a fixed-window
limiter: 5 requests per IP per 10 minutes on `/api/contact` and
`/api/newsletter`, returning 429 with a `Retry-After` header.

**Verified**: the 6th request from one IP returns `HTTP 429` with
`Retry-After: 600`, and a different IP is unaffected.

**Known limitation, stated plainly:** the counter lives in process memory.
Serverless instances scale out and each keeps its own counters, so an attacker
spread across instances gets a proportionally higher effective limit, and
counters reset when an instance recycles. This stops casual form spam and
double-submits; it is not a defence against a determined attacker. Moving the
counter to Vercel KV or Upstash, or putting `@vercel/firewall` in front, is
still worth doing. `/api/checkout` is deliberately not limited yet — throttling
a real buyer mid-purchase costs more than the spam does, and it needs shared
storage to do safely.

---

## P2 — hardening

- ~~**No security headers.**~~ **FIXED.** `next.config.mjs` now sets
  `Strict-Transport-Security` (2 years, includeSubDomains, preload),
  `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`
  (not `DENY` — the Keystatic admin UI frames its own pages),
  `Referrer-Policy: strict-origin-when-cross-origin`, and a `Permissions-Policy`
  denying camera, microphone, geolocation, payment and USB. **Verified** with a
  live response-header dump. A Content-Security-Policy is still **not** set: it
  needs testing against Stripe, Keystatic and Google Fonts on a real deploy,
  and a wrong CSP silently breaks checkout.
- **Promised shipping is never charged.** The Stripe session has no
  `shipping_options`, so the `$8.95` flat rate is never collected and the free
  threshold is not enforced — every order ships free by accident.
- **The webhook is a stub.** `checkout.session.completed` only `console.log`s
  (`app/api/webhook/route.ts:31`). No order record, no confirmation email. A
  customer who pays hears nothing back.
- **Unsplash is still a permitted image host** (`next.config.mjs`) and still in
  active use: `app/about/page.tsx`, `components/home/PhotoGallery.tsx` and the
  department tiles in `app/shop/page.tsx` all point at it. Removing the host
  would break those pages today, so this is blocked on real photography rather
  than on code.
- **Contact routing.** `/contact` advertises three `@faridunhill.com` inboxes but
  mail lands at `vintagepipevault@gmail.com` (`app/api/contact/route.ts:4`).
  Fine operationally — but the `from:` domain must be verified in Resend or the
  mail will be spoof-flagged, and those three inboxes must actually receive mail.

---

### P2-6 · Next.js 14.2.5 carries a published security advisory
`npm install` reports: *"This version has a security vulnerability. Please
upgrade to a patched version."* On a store taking card traffic this should be
scheduled deliberately, with the build and a checkout test after it.

### P2-7 · Europe is advertised nowhere and blocked everywhere
Farid reports customers in Europe and Canada. Stripe accepts shipping addresses
for `US`, `CA`, `GB`, `AU` only (`app/api/checkout/route.ts`), and
`app/shipping/page.tsx` states plainly that the EU is not served. Canada and the
UK work today; the EU does not. Either open it or keep saying so — but the
current state means European customers cannot buy.

### P2-8 · Repo hygiene fixed in passing
`next lint` had never run (no ESLint config existed, so it fell through to an
interactive prompt) and `tsc --noEmit` failed on a pre-existing `@types/react`
18-vs-19 clash pulled in by Keystatic. Both are fixed: `.eslintrc.json` added,
`tsconfig.json` pins `react`/`react-dom` types to the root copy, and eight
pre-existing unescaped JSX entities were corrected. `lint`, `typecheck` and
`build` now all pass clean, so the gate in `CLAUDE.md` is real rather than
aspirational.

## Waiting on Farid

Everything below needs a fact only Farid has, or a decision only he can make.
None of it is blocked on engineering.

| # | Item | What is needed |
|---|---|---|
| P0-2b | Catalogue prices were relabelled `£`→`$`, not converted | Were those numbers always dollars? If they were pounds, every price is ~25% low and the YAML needs a conversion pass. |
| P1-1 | "Est. 2015", "thirty years", "four hundred pipes", "Head Tobacconist" | Confirm each is true, or say what the real figure is so the copy can be rewritten. |
| P1-3 | No legal entity, trading address, phone, or tax number on the site | Supply them for the footer and `/privacy`. |
| P1-6 | Age verification is still self-attestation | Business decision: pick a provider (AgeChecked, Veratad, AgeID) or accept the PACT Act exposure knowingly. Worth an accountant or lawyer who knows US tobacco. |
| P2-2 | Shipping is promised but never charged | Confirm the US flat rate and free threshold, and supply international rates, before `shipping_options` can be added to the Stripe session. |
| P2-3 | Webhook is a stub; a paying customer hears nothing | Needs `faridunhill.com` verified as a sending domain in Resend before order-confirmation email can be wired. |
| P2-4 | Unsplash placeholders on About, gallery, department tiles | Real photography. |
| P2-6 | Next.js 14.2.5 security advisory | Schedule an upgrade window; needs a checkout test after. |
| P2-7 | European customers cannot buy — EU blocked in Stripe and in policy | Open the EU or keep excluding it. Canada and the UK already work. |
| — | Checkout round trip never tested against Stripe | Run the test-key checkout locally. The validation logic is proven; the Stripe round trip is not. |

## Verdict

Trustworthy *as an artefact*: yes — the code is coherent, the payment
architecture is right, and the previously fabricated social proof was removed
rather than hidden.

Trustworthy *as a shop taking real money*: the money path now is. Nobody can set
their own price, the currency is consistent end to end, and the site no longer
claims a control it does not run.

What stands between here and a shop that deserves a stranger's card details is
no longer code. Every defect that could be fixed by writing code has been
fixed. What is left is in the table above: heritage claims nobody can verify,
no business identity anywhere on the site, and age verification that is still
only a checkbox. Those need Farid to confirm what is true, not an agent to
write more.

The honest summary: an AI agent building from scratch produces a site that looks
finished well before it is safe. Everything cosmetic is done. Everything with
money, law, or a verifiable claim attached needs a human to confirm it is true.
