# Storefront working rules

Applies to the faridunhill.com shop: `app/`, `components/`, `content/products/`,
`lib/`, `keystatic.config.ts`. Next.js 14 App Router, Tailwind, Keystatic (YAML
products), MDX blog, Stripe Checkout, Vercel.

## Commands

```bash
npm run dev        # local server on :3000
npm run build      # must pass before any push
npm run lint       # next lint
npm run typecheck  # tsc --noEmit
```

## Truth rules (non-negotiable)

This store sells age-restricted goods. Every claim on the site is a legal claim.

1. **Never invent social proof.** No testimonials, no star ratings, no review
   counts, no "trusted by N customers", no press mentions. Ratings render only
   when `reviewCount > 0` and that count comes from real reviews. Fabricated
   testimonials have been removed from this repo twice — do not reintroduce them.
   **The one exception is the marketplace record in `lib/links.ts`**: public
   eBay and Etsy seller statistics, each rendered beside a link to the page it
   came from, so any visitor can check it in one click. That is the test — a
   number stays only while it is linked to its source, rounded down from what
   the live page shows, and stamped with `verifiedOn`. Re-read the live pages
   before touching a figure; a stale boast is the same problem as an invented
   one. Never add a statistic here that has no public page behind it.
2. **Never invent history or credentials.** Founding year, years of experience,
   collection size, staff titles. If it is not verified by Farid, it does not ship.
3. **Never claim a service that is not wired up.** Age verification, insurance,
   carbon-neutral shipping, authentication guarantees. Describe what the code
   actually does.
4. **One currency.** The business is in New Jersey and the store is USD
   end to end: Stripe charges `usd`, every price renders as `$`, and
   `priceCurrency` is `USD`. A `£` or a `GBP` anywhere is a bug. Local-currency
   display for overseas customers is handled by Stripe Adaptive Pricing in the
   Dashboard — never by converting prices in this codebase, which would show
   one number and charge another.
5. **Product copy describes the actual item.** Condition, provenance, and defects
   come from the intake record, not from inference.
6. **The catalogue contains no consumable tobacco.** 264 products: estate pipes,
   meerschaum, vintage leather, cigar accessories, lighters, pipe tools. No
   tins, no cigars, no vaping products. Never write copy that sells tobacco,
   and never reason about tobacco import or PACT Act rules as if they applied
   to this catalogue. If tobacco is ever stocked, this line changes first.
   The word "cigar" is fine where it names a real accessory — cigar cutters,
   cigar cases, humidors — and so is "tobacco pouch", because a pouch is not
   tobacco. What is never fine is copy that offers the leaf itself, a
   "tobacconist" title, or a blend named as if it were for sale.
7. **Never name a maker the shop does not stock.** Verify against
   `content/products/*.yaml` before a brand name goes on a page. Dunhill
   especially: there are zero Dunhill pipes, the shop name already invites the
   comparison, and a prior commit backed away from this exact trademark risk.

## Money rules

- Prices for a Stripe session are looked up **server-side** from the catalogue.
  The browser sends `{ id, quantity }` and nothing else. Never read a price,
  name, image, SKU, or stock flag from the request body — that is the exact bug
  that was fixed in `app/api/checkout/route.ts`, do not reintroduce it.
- Any change under `app/api/checkout/` or `app/api/webhook/` gets a manual test
  against Stripe test keys before it is pushed.
- Never log full customer PII or raw Stripe payloads.
- Secrets live in `.env.local` / Vercel env vars. Never commit a key, never paste
  one into a file, never read `.env.local` into the conversation.

## Shipping

Shipping is **free on every order, no minimum, everywhere we ship** — US, EU-27,
UK, Switzerland, Norway, Canada, Australia, New Zealand. The Stripe session has
no `shipping_options` and no shipping line, which is correct. Never reintroduce
a threshold, a flat rate, or an expedited tier into site copy unless the
checkout actually charges it.

## Code conventions

- Server Components by default; add `'use client'` only when state or effects
  are genuinely needed.
- Product data flows through `lib/products.ts`. Do not read `content/products/`
  directly from a page.
- Tailwind only, using the Victorian tokens in `tailwind.config.ts`
  (`mahogany`, `parchment`, `gold`, `burgundy`). No inline hex, no new palettes.
- Escape every user-supplied value before it enters an HTML email or the DOM.
- Images: only hosts listed in `next.config.mjs`. Prefer real photography;
  Unsplash placeholders are not acceptable on a live product.

## Before you say a change is done

`npm run lint && npm run typecheck && npm run build` — all three clean.

## Open trust debt

`docs/TRUST_AUDIT.md` lists the P0/P1 items still outstanding. Read it before
touching checkout, the shipping policy, or any heritage copy.
