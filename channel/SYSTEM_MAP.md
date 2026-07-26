# ★ SYSTEM MAP — how Farid's online-store system actually works (read before touching store/listings)

Purpose: stop cloud sessions guessing or searching blindly. If a fact here is marked
**[CONFIRMED]** it came from Farid or a repo we read. **[NEEDS FARID]** = not yet verified —
do NOT assert it as fact; ask.

## The pieces
- **faridunhill-live** (GitHub, private) — the store website + **admin page** (`app/admin`, Supabase).
  Farid uploads/edits products here; admin has Approve/Pending/Delete. **[CONFIRMED]**
- **ashcombe-co** — Farid's **"automated online-store module."** This is the engine that
  **publishes a product out to the sales channels.** **[CONFIRMED it publishes to faridunhill + Etsy]**
  Deploy seen as `ashcombe-co-production` (AWS us-east-1). **NOT one of the 3 GitHub repos** →
  its code is on Farid's PC or a non-GitHub deploy. **[NEEDS FARID: where is ashcombe-co's code?]**
- **Claude-Project** (this repo) — encyclopedia/Builder + the `channel/`. Also holds a
  **per-channel listing-copy generator** (commit `7fab6ab`, own_store/etsy/ebay). **[CONFIRMED]**
- **groundtruth-website** — separate business (property AI). Not part of the store.

## The publish flow (as Farid described it) **[CONFIRMED by Farid 2026-07-26]**
1. Farid uploads a product from the **faridunhill-live admin page**.
2. "The system published to **faridunhill AND Etsy**." → the admin triggers **ashcombe-co**, which
   pushes the listing to the channels. Etsy API keys already exist (held by ashcombe-co).
3. Goal channels: **Faridunhill store + Etsy + eBay(upload)**.

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
