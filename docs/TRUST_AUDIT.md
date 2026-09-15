# Faridunhill Store — Trust & Integrity Audit

Scope: the whole Next.js storefront in this repository, reviewed as a customer,
as a payment processor, and as a regulator would.
Question asked: *this site was built end-to-end by an AI agent — can it be trusted?*

Short answer: **the foundations are honest, but it is not yet safe to take live money.**
The presentation layer is clean (no fake reviews, real policy pages, Stripe-hosted
payments). The money path and several public claims are not.

Legend: **P0** blocks go-live · **P1** fix before advertising · **P2** hardening.

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

## P0 — blocks go-live

### P0-1 · The customer sets the price

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

**Fix:** send only `{ slug, quantity }` from the client. Look the product up
server-side via `lib/products.ts` and build `unit_amount` from the catalogue
price. Reject unknown slugs, non-integer quantities, and out-of-stock items.

### P0-2 · The site quotes dollars and charges pounds

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

A customer reading "$75" and being charged in GBP has a valid chargeback and, in
the UK/EU, a consumer-law complaint. **Pick one jurisdiction and currency and
make every page agree.**

### P0-3 · You claim an age-verification service you do not have

`app/shipping/page.tsx:61` states: *"We use a third-party age verification service
at checkout."*

What actually exists is `components/ui/AgeGate.tsx` — a modal that writes
`fh-age-verified` to `localStorage`. That is self-attestation, cleared by any
incognito window. Stripe adds two confirmation sentences
(`app/api/checkout/route.ts:48,52`); those are also self-attestation.

For tobacco this is not a copy nit. US PACT Act sales require verified age and
adult-signature delivery; UK Challenge 25 expects equivalent diligence. Either
integrate a real provider (AgeChecked, Veratad, AgeID) or delete the sentence and
describe what you truly do.

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

### P1-2 · The fabricated testimonials are still in the tree
`components/home/CustomerReviews.tsx` holds six invented five-star reviews with
named customers. It is no longer imported, but it is one autocomplete away from
returning. Delete the file.

### P1-3 · No verifiable business identity
There is no legal entity name, registered address, or phone number anywhere —
not in the footer, not on `/contact`, not in `/privacy`. `/contact` lists three
`@faridunhill.com` addresses (`app/contact/page.tsx:61-63`) and nothing else.

A shop selling age-restricted goods with no findable address reads as a scam to
exactly the careful customer you want. Add entity name, trading address, a phone
number, and (if applicable) VAT or EIN to the footer and `/privacy`.

### P1-4 · HTML injection into your own inbox
`app/api/contact/route.ts` escapes `message` but interpolates `name`, `email`,
and `subject` raw into the email body, and passes `email` straight to `reply_to`.
Escape all four and validate the address.

### P1-5 · No rate limiting on any public POST
`/api/contact`, `/api/newsletter`, and `/api/checkout` accept unlimited requests.
That is free Resend spend, Mailchimp list poisoning, and Stripe session spam. Add
per-IP limiting (Vercel KV, Upstash, or `@vercel/firewall`).

---

## P2 — hardening

- **No security headers.** `vercel.json` and `next.config.mjs` set none. Add HSTS,
  `X-Content-Type-Options`, `Referrer-Policy`, and a CSP.
- **Promised shipping is never charged.** The Stripe session has no
  `shipping_options`, so the `$8.95` flat rate is never collected and the free
  threshold is not enforced — every order ships free by accident.
- **The webhook is a stub.** `checkout.session.completed` only `console.log`s
  (`app/api/webhook/route.ts:31`). No order record, no confirmation email. A
  customer who pays hears nothing back.
- **Unsplash is still a permitted image host** (`next.config.mjs`), so stock
  photography can reappear on a product page.
- **Contact routing.** `/contact` advertises three `@faridunhill.com` inboxes but
  mail lands at `vintagepipevault@gmail.com` (`app/api/contact/route.ts:4`).
  Fine operationally — but the `from:` domain must be verified in Resend or the
  mail will be spoof-flagged, and those three inboxes must actually receive mail.

---

## Verdict

Trustworthy *as an artefact*: yes — the code is coherent, the payment
architecture is right, and the previously fabricated social proof was removed
rather than hidden.

Trustworthy *as a shop taking real money today*: no. P0-1 lets anyone set their
own price, P0-2 quotes a currency you do not charge, and P0-3 claims a
compliance control you do not run. Those three are the gate.

The honest summary: an AI agent building from scratch produces a site that looks
finished well before it is safe. Everything cosmetic is done. Everything with
money, law, or a verifiable claim attached needs a human to confirm it is true.
