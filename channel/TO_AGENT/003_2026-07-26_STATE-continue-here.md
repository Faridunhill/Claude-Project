# ★ NEXT SESSION START HERE — live state (2026-07-26)

You are the Builder/Manager (see CLAUDE.md). This note is so you DON'T wake blank. Read it first.

## THE THREE CLOUD REPOS (Farid granted the Claude GitHub App "All repositories" — you can read+write all 3 in a fresh session)
1. **Claude-Project** (this repo) — encyclopedia / Builder / Professor + the Farid↔Agent `channel/`. Public.
2. **faridunhill-live** — ★THE LIVE STORE★ (faridunhill.com). Next.js + **Supabase** products. Has a real admin at `app/admin` with an **Approve / Pending / Delete** workflow. Products live in a Supabase `products` table; `images TEXT[]` = photo order (index 0 = main). Normally **private** (Farid briefly made it public 2026-07-26 so this session could read it; he's setting it back to private). This is where the store work happens — NOT Claude-Project.
3. **groundtruth-website** — GroundTruth Property AI landing (paid TN property due-diligence reports; Faridunhill LLC, NJ). Public.

⚠️ Do not confuse Claude-Project's `content/products/*.yaml` store with the live store. **The live store is faridunhill-live (Supabase).**

## OPEN TASK #1 — deploy the photo-arranger to faridunhill-live (BUILT, needs delivery)
Farid published **30+ new pipes** (status = pending) in the faridunhill-live admin and needs to **arrange each product's photos** before approving. The admin's Edit modal (`components/admin/ProductModal.tsx`) showed photos but had **no reorder**. I built the reorder UI (position badges, ◀ ▶ move, ★ make-main, mobile-friendly) but could NOT push (old session scoped to claude-project only).
**The finished change is saved here:** `channel/PENDING_DELIVERY/ProductModal.tsx.NEW` (full file) and `photo-arranger-ProductModal.patch` (diff).
**DO THIS in a fresh session with faridunhill-live in scope:** apply the change to `faridunhill-live/components/admin/ProductModal.tsx` (copy the .NEW file or `git apply` the patch), commit on a branch, push, open a PR (Vercel will deploy). Then tell Farid it's live and he can arrange all 30 pipes' photos.

## OPEN TASK #2 — multi-channel publish (Etsy/eBay/store) — ★WHERE THE ETSY CODE LIVES★
Farid confirmed (2026-07-26): he **uploads from the faridunhill-live admin page and "the system published to faridunhill AND Etsy."** So multi-channel publishing ALREADY WORKS.
**DO NOT re-search faridunhill-live for Etsy API code — it is NOT there** (a prior session burned 13 min confirming this; `_archive` was just `.bak` files). The Etsy/eBay publishing lives in **ashcombe-co** — Farid's *"automated online store module"* (deploy: `ashcombe-co-production`, AWS us-east-1). faridunhill-live's admin only **calls out** to ashcombe-co.
**To finish the listing job:** (1) read the faridunhill-live admin **Approve/Publish action** to see exactly what it calls (env URL / fetch to ashcombe-co / Supabase function) — that reveals the trigger; (2) locate **ashcombe-co's code** (NOT one of the 3 GitHub repos — likely Farid's PC or a non-GitHub deploy; ask Farid for its repo/location); (3) use its EXISTING Etsy connection to re-publish the 30 pipes with arranged photos — do not rebuild a new Etsy publisher from scratch.
Related: Claude-Project commit `7fab6ab` (P2.6) has a **per-channel listing copy generator** (own_store/etsy/ebay title limits, hero photo leads) — part of this pipeline.

## OPEN TASK #3 — attorney letter (portfolio) — mostly done
`channel/TO_FARID/004_...weinstein-intake-letter-draft.md` — worry-led intake to Cher Sauer / Law Offices of David A. Weinstein, P.C. (Freehold, NJ) for website terms/disclaimers across the 3 sites. Sections A (faridunhill) + B (GroundTruth, from real repo) done. **Section C (ashcombe-co) still generic** — ashcombe-co is a deploy project (seen on the hosting dashboard) with no standalone GitHub repo; its code likely lives in faridunhill-live or on Farid's PC. Confirm what ashcombe-co is, then finish Section C. Entity = **Faridunhill LLC (New Jersey)**. Farid to add his name/phone before sending.

## DONE THIS SESSION
- Marked 2 eBay-sold German leather pouches Sold Out (content/products).
- Built + pushed the attorney portfolio letter (A+B).
- Improved Claude-Project's Keystatic images field labels (parallel/older store — low priority vs faridunhill-live).
- Cloned groundtruth-website (public) + faridunhill-live (while public); read both.
