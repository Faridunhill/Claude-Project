---
description: Re-run the storefront trust audit and update docs/TRUST_AUDIT.md
---

Re-audit this storefront for trust and integrity problems, then rewrite
`docs/TRUST_AUDIT.md` with current findings and `file:line` references.

Check every category:

1. **Fabricated social proof** — testimonials, star ratings, review counts,
   aggregate ratings in JSON-LD, "as seen in", customer-count claims. Search
   components, pages, and product YAML. Flag dead files that still hold invented
   reviews, not just live ones.
2. **Unverifiable claims** — founding year, years of experience, collection size,
   staff titles, awards, authentication or appraisal guarantees.
3. **Claims vs. reality** — does every service the copy promises (age
   verification, insured shipping, free-shipping thresholds, returns windows)
   actually exist in code? Compare `/shipping`, `/returns`, `/privacy` against
   `app/api/` and `components/ui/AgeGate.tsx`.
4. **Currency and price integrity** — every `$`/`£`, `priceCurrency`, and the
   Stripe session currency must agree. Confirm `unit_amount` is derived
   server-side from the catalogue, never from the request body.
5. **Business identity** — legal entity, trading address, phone, tax number
   present in the footer and `/privacy`.
6. **Input handling** — every public POST route: validation, escaping before
   HTML email or DOM, rate limiting.
7. **Security posture** — webhook signature verification, security headers,
   secrets never in tracked files, image host allowlist.

Rank findings P0 (blocks go-live) / P1 (fix before advertising) / P2 (hardening).
Keep the "What is already trustworthy" table honest — do not pad it.
Report only what you verified in the code. Do not fix anything unless asked.
