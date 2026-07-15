# Faridunhill — HANDOVER (start-of-chat brief for the next agent)

_Updated 2026-07-15. Paste this at the START of a new chat (or drop it in the repo's
`docs/`) so the agent knows where we stopped. Do NOT change files until Farid confirms._

## TWO REPOS
1. `Faridunhill/faridunhill-live` (branch `master`) — the LIVE store. Next 16 · Supabase ·
   Resend · payments OFF (LAW 06) · **USD only** · sells collectible/display pieces, NOT
   tobacco · real photos only. NOT in-session yet; add before live-site work.
2. `Faridunhill/Claude-Project` (branch `claude/peterson-pipe-dating-system-6xcj9v`) — the
   systems/knowledge workbench. Everything below is here and PUSHED.

## WHAT IS BUILT & WORKING (marketing system — all on the branch)
A full method -> marketing pipeline, run locally against `C:\FaridunhillPipes`:

- Genome (Layer 1) `genome/` — vocab, schema (Pydantic), corrections ledger, SQLite store,
  the-Eye adapter. P2.2.
- P2.3 `genome/intake.py` — birth record from photos + human facts; provenance on every
  fact; never blocks; fails loud if the Eye isn't wired.
- P2.4 `genome/gate.py` — QA gate: 4 rules (confidence <0.90 / corroboration vs stamping /
  price >=150 / 5% audit). PASS / REVIEW (list+hedge) / RESEARCH_LATER. "A blank beats a lie."
- P2.6 `expression/listing.py` — title/description/tags/images/alt-text; asserts only what
  the gate cleared, hedges the rest, auto-discloses flaws, reports gaps (never fabricates).
- P2.7 `expression/social.py` — IG/TikTok/X/Reddit/email posts + a 9:16 VideoReel storyboard.
- `folder_source.py` + `batch.py` + `__main__.py` — read `C:\FaridunhillPipes\<pipe>\`
  (HEIC ok), optional `pipe.txt` notes, root `prices.txt` / `whys.txt` (key:substring),
  write listing + posts + reel.json per pipe. ASCII-safe output.
- `render.py` — reel.json -> real 1080x1920 reel.mp4 (blur-frame so the whole pipe fits,
  gold border, FARIDUNHILL header, brand-name-only caption) + HEIC->JPG. Per-pipe motion
  opener: a video dropped in a pipe's folder plays first. Reels ~30s from ~7-8 photos.
- `auto.py` — `python -m marketing.auto <root> [--watch]`: post + video per pipe, left in
  `_marketing\`, incremental (only new/changed pipes re-render). Posting stays manual/opt-in.
- `control.yaml` — standing walls (spend/price/post caps; only Farid edits).
- 69 tests pass. Deps: `pip install pydantic` (core) + `pillow pillow-heif imageio imageio-ffmpeg numpy` (video).

## HOW TO RUN (Farid's PC, local)
```
python -m marketing.auto "C:\FaridunhillPipes" --watch --year 2026     # all + watch
python -m marketing.auto "C:\FaridunhillPipes" --force --year 2026     # re-render all
```
Output per pipe in `C:\FaridunhillPipes\_marketing\<pipe>\`:
listing.md · post-instagram.txt · post-tiktok.txt · reel.mp4 · photos\ · reel.json
Prices in `prices.txt`, hooks in `whys.txt` (root); a per-pipe motion clip goes IN the folder.

## LIVE CATALOG STATE (11 pipes)
All 11 have photos + price + brand + hook + a 30s reel. Remaining per-pipe gap: era (needs the
dating directory) and condition grade on 6 (one word each).

## THE ACADEMY = the self-correction loop (the system's core principle)
catch invention -> tighten the rule -> regenerate -> the correction becomes PERMANENT LAW.
Machinery in place: corrections ledger (per product) · QA-gate abstain + 5% audit (per claim,
self-calibrating) · governance-in-CI + the 69-test suite (per rule — every bug caught this
session became a locked test). Extending it system-wide = P2.5 ledger + P2.8 flywheel + a
single named "laws" registry.

## NEXT (in order)
1. Auto-posting (opt-in) to TikTok/Instagram — needs account access; last human look first.
2. P2.5 five-event phenotype ledger + P2.8 encyclopedia flywheel (the Academy, systematised).
3. Dating directory -> fill "era" (Peterson/Dunhill hallmark dating) — crown-jewel tie-in.
4. Wire the real Eye (itemassets.db) into `adapter_itemassets.get_source()` (one class).

## OPEN DECISIONS FOR FARID
- Add `faridunhill-live` next session (for live-site + auto-posting)?
- `control.yaml` currency says GBP; business is USD — reconcile.
- Confirm `promotion.monthly_ceiling` before paid promotion (100, "TO BE CONFIRMED").
- Next dating cabinet after Peterson: Dunhill or Stanwell first?

## RULES THAT MUST NOT BREAK
Dating: hard marks decide; shape only reassures; abstain over guess; primary sources only.
Marketing: control.yaml ceilings never crossed by a machine (breach = pause + one email).
Video: reels are social/email only, never a listing image; real photos only (no synthetic).
Business: USD · collectible/display NOT tobacco · no fabricated history/reviews · real photos.
