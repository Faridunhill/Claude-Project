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

## OPEN TASK #2 — multi-channel goal (Farid's words)
He wants each product's arranged photos + listing across **3 sales channels: Etsy, eBay (upload), and the Faridunhill store.** Faridunhill store = direct (Supabase). Etsy/eBay = build ready-to-upload packs (photos in arranged order + title/description). Scope with him.

## OPEN TASK #3 — attorney letter (portfolio) — mostly done
`channel/TO_FARID/004_...weinstein-intake-letter-draft.md` — worry-led intake to Cher Sauer / Law Offices of David A. Weinstein, P.C. (Freehold, NJ) for website terms/disclaimers across the 3 sites. Sections A (faridunhill) + B (GroundTruth, from real repo) done. **Section C (ashcombe-co) still generic** — ashcombe-co is a deploy project (seen on the hosting dashboard) with no standalone GitHub repo; its code likely lives in faridunhill-live or on Farid's PC. Confirm what ashcombe-co is, then finish Section C. Entity = **Faridunhill LLC (New Jersey)**. Farid to add his name/phone before sending.

## DONE THIS SESSION
- Marked 2 eBay-sold German leather pouches Sold Out (content/products).
- Built + pushed the attorney portfolio letter (A+B).
- Improved Claude-Project's Keystatic images field labels (parallel/older store — low priority vs faridunhill-live).
- Cloned groundtruth-website (public) + faridunhill-live (while public); read both.
