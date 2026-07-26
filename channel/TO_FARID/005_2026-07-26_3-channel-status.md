# 005 — The 3 sales channels: honest status (2026-07-26)
*For Farid, from the Builder. You asked me to read `TO_AGENT/003` and confirm
your new list of edited photos is re-arranged and listed on the 3 platforms.
Here is the straight answer, then what I did about it.*

## The straight answer: NOT yet — but I removed the two blockers today
The `003` handoff was on another branch, so I read it, then checked the REAL
live store (`faridunhill-live`, Supabase). Reality as I found it:
- The photo-arranger you need to re-arrange photos **was built but never
  installed** on the live store — your admin still had the old plain photo
  list with no reorder.
- **eBay CSV export did not exist.**
- **Etsy has NO API in the code** — the only Etsy trace is that your photos are
  hosted on Etsy's image CDN. So it is not "already connected."

I could not honestly tick "done," so I built and delivered the missing pieces.

## Channel 1 — faridunhill.com (your own store) → arranger DELIVERED
- PR **#1** on `faridunhill-live`: photo pose-order arranger in the admin Edit
  modal. Position badges (★1 = main), ◀ ▶ to move, ★ to make main, mobile-friendly.
- The order you set = the order on the product page = index 0 is the main photo.
- **Merge PR #1**, then in Admin → Products → Edit each pipe → arrange → Save.

## Channel 2 — eBay (by CSV) → EXPORTER DELIVERED
- PR **#2** on `faridunhill-live`: an **Export eBay CSV** button on the admin
  products page. It exports the products **currently in view** (filter by
  category/search to export just your new batch) as an eBay **File Exchange**
  "Add" file.
- Photos are written **in the arranged order** (main first), so eBay shows the
  same pose sequence.
- Auto-filled: title (capped at eBay's 80 chars), description, condition
  (New→1000 / estate→3000), FixedPrice/GTC, price, stock.
- **You fill ONCE and save as a template:** the eBay `*Category` number, and
  your Business Policy names (shipping / return / payment). eBay needs those and
  they're specific to your account.

## Channel 3 — Etsy → NEEDS A DECISION (no API yet)
There is no Etsy integration in the store. Etsy does have an official API that
can create listings, but it needs: your Etsy shop, an Etsy developer app
(OAuth keys), and a connect step. That's a separate build. Tell me to go and
share the Etsy app credentials through the channel and I'll wire it (or, if you
prefer, I can add an Etsy-style CSV like the eBay one as a stopgap).

## So, to actually get your list live on all 3
1. Merge PR #1 + PR #2 on `faridunhill-live` (Vercel deploys).
2. Arrange each pipe's photos in the admin, approve them → **live on faridunhill.com**.
3. Filter to your new batch → **Export eBay CSV** → fill Category + policies → upload to eBay.
4. Say the word on Etsy (API or stopgap CSV) and I'll build it.

## CORRECTION / follow-up (Etsy) — Farid says it published to Etsy last week
Farid: "last week the system published to etsy direct... i cant create api every
day, what happened???" So I searched HARD before answering:
- **Both cloud repos, full history, every branch:** NO Etsy-publishing code.
  No Etsy OAuth / token / `etsy.com/v3` call anywhere. `faridunhill-live` has
  only the Etsy image CDN + the eBay-deletion compliance webhook.
- The `marketing/` auto-system (branch `claude/auto-marketing-system-design-2zmg0h`)
  is a DESIGN: `social/publisher.py` posts to **Meta (FB/IG)**, not Etsy; it
  only models eBay/Etsy as data "channels." No live Etsy publisher.
- Per the two-fronts law, the cloud me **cannot see Farid's PC.** If Etsy
  published last week, it ran on **FaridOS (his PC)** or a tool, with an Etsy
  connection **that already exists** — he does NOT need to make a new API.
- **NEXT:** find where last week's Etsy publish ran (PC script? a tool?
  browser session?) and REUSE that existing credential — do not rebuild.
  Asked Farid to point me to it.

— The Builder

