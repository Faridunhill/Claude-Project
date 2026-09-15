# Faridunhill Store — working rules

Next.js 14 (App Router) storefront for faridunhill.com. Tailwind, Keystatic
(YAML products in `content/products/`), MDX blog, Stripe Checkout, Vercel.

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
2. **Never invent history or credentials.** Founding year, years of experience,
   collection size, staff titles. If it is not verified by Farid, it does not ship.
3. **Never claim a service that is not wired up.** Age verification, insurance,
   carbon-neutral shipping, authentication guarantees. Describe what the code
   actually does.
4. **One currency.** Prices, structured data, policy pages, banners, and the
   Stripe session must all agree. Today the code charges GBP — copy that says `$`
   is a bug.
5. **Product copy describes the actual item.** Condition, provenance, and defects
   come from the intake record, not from inference.

## Money rules

- Prices for a Stripe session are looked up **server-side** from the catalogue.
  Never trust a price, SKU, or stock flag sent by the browser.
- Any change under `app/api/checkout/` or `app/api/webhook/` gets a manual test
  against Stripe test keys before it is pushed.
- Never log full customer PII or raw Stripe payloads.
- Secrets live in `.env.local` / Vercel env vars. Never commit a key, never paste
  one into a file, never read `.env.local` into the conversation.

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
