# ★ SYSTEM MAP — how Farid's online-store system actually works (read before touching store/listings)

Purpose: stop cloud sessions guessing or searching blindly. If a fact here is marked
**[CONFIRMED]** it came from Farid or a repo we read. **[NEEDS FARID]** = not yet verified —
do NOT assert it as fact; ask.

## ★ THE ENCYCLOPEDIA IS ALREADY BUILT AND LIVE — in faridunhill-live, NOT here
The real, published encyclopedia lives in **faridunhill-live** (e.g. the Peterson & Dunhill dating
guides). It already has the **trust-tier system**: per-era **HIGH / MEDIUM / LOW trust badges** with
honest dating brackets, kept overlaps, and "sources disagree → keep the wide bracket" notes. It is
excellent and DONE — do not propose building it.
**Claude-Project's `content/encyclopedia/` has only a sample article** — it is NOT the real encyclopedia.
**Rule:** never conclude an encyclopedia/store feature is missing by checking Claude-Project. The live
product is in faridunhill-live. If you can't see it, say so and open faridunhill-live — don't guess.

## The pieces
- **faridunhill-live** (GitHub, private) — the store website + **admin page** (`app/admin`, Supabase).
  Farid uploads/edits products here; admin has Approve/Pending/Delete. **[CONFIRMED]**
- **ashcombe-co** — Farid's **"automated online-store module."** Deploy seen as
  `ashcombe-co-production` (AWS us-east-1). **NOT one of the 3 GitHub repos.**
  **[UNVERIFIED — DO NOT ASSERT]** Whether ashcombe-co is the thing that publishes to Etsy is a
  GUESS a cloud session made; it was NOT confirmed by Farid. The publish could be direct from the
  admin, via ashcombe-co, or another path. **Nobody has read the code that does it.**
  **[NEEDS FARID: where is ashcombe-co's code, and does the admin publish directly or call it out?]**
- **Claude-Project** (this repo) — encyclopedia/Builder + the `channel/`. Also holds a
  **per-channel listing-copy generator** (commit `7fab6ab`, own_store/etsy/ebay). **[CONFIRMED]**
- **groundtruth-website** — separate business (property AI). Not part of the store.

## The publish flow — what is actually CONFIRMED vs GUESSED
**[CONFIRMED by Farid 2026-07-26]:** Farid uploads/approves a product from the **faridunhill-live
admin page**, and "the system published to **faridunhill AND Etsy**." Etsy publishing already works.
**[GUESS — NOT confirmed]:** that ashcombe-co is the engine, or that Etsy keys live there. Unknown.
**Goal channels:** Faridunhill store + Etsy + eBay(upload).
**To learn the truth (don't guess):** read the faridunhill-live admin Approve/Publish action code
to see what it calls — that is the only way to know if it publishes directly or hands off elsewhere.

## What this means for the current job (arrange 30 pipes' photos, then finish listings)
- **Do NOT search faridunhill-live for Etsy API code — it is not there. The Etsy code is in ashcombe-co.**
  (A session already burned 13 min learning this the hard way.)
- The photo-arranger (in `channel/PENDING_DELIVERY/`) goes into the faridunhill-live **admin**.
- After arranging, Farid re-publishes from the admin → ashcombe-co → channels.
- **[NEEDS FARID / check ashcombe-co]** Does re-publishing **update** the existing Etsy listing's
  photo order, or **create a duplicate**? Verify in ashcombe-co before mass re-publishing.

## Rule for every session
If you cannot see a part of the system (e.g., ashcombe-co isn't in scope), say
"I can't see it from here" and ask Farid — do NOT declare it missing or nonexistent.
Best permanent fix: **add ashcombe-co to GitHub** so this system is fully readable by the cloud.
