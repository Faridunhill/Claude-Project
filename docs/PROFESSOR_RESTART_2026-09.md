# The Professor — RESTART from a blank page (2026-09-10)

> Farid's order, 2026-09-10: *"When you try to solve a problem and in the end you fail,
> don't start from the last solution. Throw out all the old solutions and start from
> scratch — a mind free from the old ideas gives the right answer."*
> This document is that blank page. Everything before it is **retired** (§1).
> Everything in it was **researched online on 2026-09-10** (§9, Sources) under the new
> standing law `.claude/skills/research-first/SKILL.md`.

> **MIRROR NOTICE (2026-09-11):** the master record of this project lives on Farid's PC in
> `FaridOS\control\` (records law). This file is the cloud mirror. Corrections from the
> local Builder (channel note 005) are folded in below; where they conflict with older text,
> the local facts win.

## 0.5 DECISION ZERO — Farid's face law (added 2026-09-11)
Farid's standing law: **his face is never generated; his face is his pixels.** Steps C–D of
this plan (a drawn Professor from his photos) would open that law. That is his decision
alone and it comes **before any tool is bought**. Three roads, one 15-second test each, same
line in VOICE_1, same scene, side by side, cost cap $10 total, his eye decides:
- **Road A (keep the law):** Farid on camera, cut out into a drawn workshop; the four
  co-characters drawn and rigged. Professional standard for a real host; his real hands
  solve the hands problem for free. **Default while undecided.**
- **Road B (keep the law):** layered puppet from one real photo, mouths from his pixels,
  voice-driven. Local and cheap; weak on mouths and turns.
- **Road C (open the law):** this document's Steps C–D — illustrated Farid from five real
  photos, spec-locked likeness, his eye as the gate. History: drawn faces were rejected
  Aug 31 and Sep 3 (face-matcher 0.63–0.67 against his photos).
Under A or B, Steps C–D apply to the four co-characters only; everything else in this plan
is unchanged.

## 0.6 Corrections from the local side (2026-09-11) — facts the cloud could not see
- Photos: all Faces files are already on the PC (`master\references\FACES_0902`, SHA-256
  manifest, 281 files by the local count); **folder 5 contains Farid's grandson and is
  excluded**; the reference kit is picked locally. Ask 3 withdrawn.
- The retired portraits: six files moved to `master\concepts\RETIRED_0909\` (fingerprinted,
  not erased). Ask 2 done.
- Voice: VOICE_1 (`1zXuOXOwN0vBqtS2MYTC`), chosen by blind test Aug 31; 61 own takes + a
  36-min reading set on disk. **The PVC road already failed on Aug 31 (verification
  deadlock; law: no support tickets ever). Ask 4 withdrawn.** MOSS-TTS benched locally.
- Paid tools: ElevenLabs Creator, Adobe Firefly Pro, ~$17 OpenRouter. **HeyGen, Hedra,
  Kling, Runway are NOT paid** — all four are new spend, Farid's gate. Road tests run on
  free tiers (HeyGen 3 videos/month ≤1 min watermarked; Hedra ≈15 s free) and on
  OpenRouter `google/gemini-3-pro-image` (~$0.15–0.25 per 2K image).
- Council: Hermes is not installed; the council runs as OpenRouter scripts per seat + a
  chat room + the ledger. Build the protocol there. QC must see and hear real output;
  receipts carry file hashes; Farid picks the model per chair.

## 0. Scoreboard (read this first)

| Item | State on 2026-09-10 |
|---|---|
| Old face approach (LoRA ×2, single "approved portrait" → talking photo) | **RETIRED** — see §1 |
| The two approved portraits | **RETIRED as references.** Not trashed from Drive (I cannot be sure which two you mean — §1 lists the candidates; you trash, or tell me the names and I do it) |
| Identity photos available | **10 folders in Drive `Downloads/Faces/1…10` = 139 files** (inventory §2) + ~150 on your PC (not reachable from the cloud) |
| Voice | Professor's clone = LOCKED (unchanged). PVC reading pack exists (`PVC_READING_PACK.txt`, 10 sections ≈ 25 min). Cast voices = to be *designed*, not cloned (§5) |
| New method | **Design spec first → master portrait from up to 5 real photos (Nano Banana Pro) → turnaround/expression/hands sheets → animation chosen per shot type** (§4) |
| Cast | 5 characters defined as a first draft for your verdict (§5): the Professor, the Cabinet (Madame), the Assistant, the Third Chair, Alfred |
| First gate | The ten-second test, remade with the new master portrait (§6) |
| What you do next | 6 small things, §7 |

## 1. What is retired, and why (so nobody resurrects it)

| Retired | Why it failed (honest diagnosis) |
|---|---|
| **LoRA training on Farid's real photos → "make him a cartoon"** (tried twice + injection) | Two conflicting objectives in one training: *keep this exact identity* and *change the whole rendering style*. Trainers and 2026 guides say the same: never mix real photos and cartoon images in one dataset; a likeness LoRA needs 15–30 images of ONE consistent style. A cartoon of Farid does not exist yet, so there was nothing consistent to train on. (Sources: nerdbot 2026-09-05; thefluxtrain 2026; fal.ai FLUX.2 trainer.) |
| **"One approved portrait = the bible"** (PROFESSOR_FACE_PIPELINE.md, July) | The takes drifted because there was **no written design spec** before generating: one take has a green tartan cap and a dark beard, one is bald with a scarf, one has a rust flat cap and amber glasses. Each "take" changed several variables at once, so "is that me?" was judged against a moving target. A single square close-up also cannot drive full-body or hands. |
| **The two approved portraits** — candidates in Drive: `CHANNEL_AVATAR_professor.png` (2026-09-02, used for EPISODE_01), `ARTIST_1_sunset_scarf.png`, `ARTIST_6R_green_cap.png`, `ARTIST_5_bw_drawing_COLOR.png` and the other `ARTIST_*` files in `Downloads/voice/` | Retired as references by your order. My own read of them (viewed 2026-09-10): the channel avatar has the strongest likeness (nose, cheek moles, mouth) but heavy black outlines and orange skin; the sunset take has the best bone structure but no cap and no beard; the green-cap take reads as a generic younger man. None is a usable master. |
| **Talking-photo-only production** (HeyGen photo avatar as the whole show) | Verified 2026-09-10: HeyGen motion prompts control face/body/gesture only, *not props*; "picking up an object" is unreliable. The Professor must handle pipes. So the talking photo can only ever be ONE shot type, not the pipeline. |
| **EPISODE_01_clean_airway** renders (v1, REVIEW_0907) | Built on the retired portrait. Keep the script and audio; the picture gets remade after the ten-second gate (§6). |

Not retired: the **ElevenLabs voice** (locked), the **PVC reading pack** (good, use it), the
**concept** (Book of Mistakes, the Archive, the flywheel — `docs/PROFESSOR_PROJECT.md`),
and the **character bible rules** you gave (elegant, slim, small Irish cap, glasses,
pipe-in-hand never lit).

## 2. What we actually have (inventory, Drive, 2026-09-10)

### 2.1 Identity photos — `My Drive/Downloads/Faces/`
| Folder | Files | Notes from viewing samples |
|---|---|---|
| 1 | 6 (IMG_3934–3939, HEIC) | Evening, waterfront. **IMG_3935 = best frontal identity reference of everything I saw**: sharp, eyes to camera, faint smile, black cap, gold rectangular glasses, grey stubble, grey waistcoat over black polo. IMG_3934 is a low-angle selfie — secondary only. |
| 2 | 9 (IMG_5696–5717) | not viewed yet |
| 3 | 15 (IMG_1324–1338) | contiguous burst — likely one session, many angles |
| 4 | 22 (IMG_1517–1534, 2017–2035 + 2 PNG screenshots) | two shoots |
| 5 | 21 (IMG_2084–2143 + 3 PNG screenshots) | |
| 6 | 14 (IMG_4248–4256, IMG_6840 + 3 PNG screenshots) | IMG_4249 duplicated |
| 7 | 4 (PNG screenshots only) | no camera originals |
| 8 | 16 (IMG_6765–6779 + stray IMG_4249) | |
| 9 | 13 (IMG_6829–6842) | |
| 10 | 19 (IMG_5031–5051) | Indoor workshop, no cap, buzzed grey hair, half-rim gold glasses, pipe in mouth. **IMG_5045** = good right three-quarter/profile (jaw, ear, nose). IMG_5043 = eyes closed, disqualified. |
| `New wave/Face` (Aug 26) | 6 HEIC | IMG_0852 is a **pipe product photo**, misfiled — check the other five. |

Total: **139 files** in Faces/1–10. Full manifest with recommendations: `docs/professor/REF_KIT_MANIFEST.md`.

**Privacy rule:** your face photos stay in Drive. This repo may be public — only *manifests*
(file names, counts, which ones are chosen) go into git, never the photos themselves.

### 2.2 Voice — `Downloads/voice/` + `Downloads/`
`ANCHOR_1_REAL_FARID.mp3`, `ANCHOR_2_THE_CLONE.mp3`, `HUMAN_A–D.mp3`, `VOICE_A/B.mp3`,
`DEEP_TEST_A/B/C.mp3`, `MR_FARIDUNHILL_VOICE.mp3`, `MOSS_SAMPLE_0902.mp3`,
`EP1_MOSS_narration.mp3`, four `68 Rising Sun Tavern Rd *.wav` recordings,
`PVC_READING_PACK.txt` (10 sections, English, written for the Professional Voice Clone).

### 2.3 Prior renders (history only)
`PROFESSOR_FIREPLACE_LIVE_v1.mp4`, `PROFESSOR_SUNSET_LIVE_v1.mp4`, `PROOF_CUTAWAY_v1.mp4`,
`SAMPLE_F_conversation.mp4`, `EPISODE_01_clean_airway_v1.mp4`, `…_REVIEW_0907.mp4`,
`ENCYCLOPEDIA_TOUR_v1/v2`, `ENCYCLOPEDIA_STORY_v2.mp4`.

## 3. The blank-page principle: DESIGN FIRST, LIKENESS SECOND, ANIMATION THIRD

The July plan started from an image. The new plan starts from **words that cannot drift**:

1. A written **design spec** per character (cap, glasses, beard, clothes, age, body,
   the one house style) — locked before any pixel is generated.
2. A **master portrait** generated *from the real photos + the spec* with a model that
   accepts several human reference images at once (not from a text prompt, not by
   training).
3. From the master: **turnaround sheet, expression sheet, hands-with-pipe sheet.**
   These sheets are the bible — not one square close-up.
4. **Animation is chosen per shot type** (talking close-up / two-shot dialogue /
   hands-on-the-pipe / establishing shots). No single tool does all four; pretending
   one does is what stalled the project.

## 4. The pipeline (each tool verified online 2026-09-10 — §9)

### Step A — Reference kit (this week, CPU work, mine)
- From the 139 files pick **8–12**: 2 frontal (eyes to camera, neutral + slight smile),
  2 left ¾, 2 right ¾, 1 left profile, 1 right profile, 1 looking down at hands,
  1 laughing. Even light, sharp, glasses on, no pipe in the mouth for the face set.
- First picks from what I viewed: **IMG_3935** (front), **IMG_5045** (right ¾).
  The rest come from folders 2–9 after viewing (next session, or a local session which
  also has the 150 PC photos).
- Convert HEIC → JPG at 2048 px, name them `REF_01_front.jpg …`, put them in Drive
  `Professor/REF_KIT/`. The manifest lives in this repo.

### Step B — The written design spec (draft in §5; you approve the words)
One **house style** for the whole cast. Recommendation (from the three retired takes):
**painterly 2D with soft shading** — it kept the best bone structure and animates well in
every talking-face tool tested (illustrated faces are supported by HeyGen Avatar IV and by
Hedra Character-3). Avoid heavy black comic outlines (they aged and hardened the face) and
avoid photoreal 3D (uncanny, and it makes the "his-likeness" judgement harder, not easier).

### Step C — Master portrait: Nano Banana Pro (Gemini 3 Pro Image)
- Verified: Nano Banana Pro takes **up to 14 reference images, keeps the likeness of up
  to 5 people**, outputs up to 4K, and is the model most 2026 comparisons rank first for
  character consistency. Flux Kontext / FLUX.2 Edit are the fallback editors.
- Method: upload the **5 best REF_KIT photos** + the written spec, ask for the Professor
  in the house style, head-and-shoulders, neutral warm background. Generate takes; change
  **one variable per take**; Farid judges only "is that me?".
- **Likeness test before approval:** show the winning take to three people who know you,
  without telling them who it is. If two of three say "Farid", it passes. This replaces
  self-judgement (we are the worst judges of our own face).
- The winner becomes `MASTER_professor_v1.png` (Drive `Professor/MASTER/`). Versioned.

### Step D — The sheets (the real bible)
From the master, with "the same character as in the reference image":
- **Turnaround:** front, ¾ L, ¾ R, profile L, profile R, back (2026 guides confirm Nano
  Banana Pro produces 360° turnarounds at 4K in one pass).
- **Expressions:** neutral, warm smile, listening, surprised, disapproving-eyebrow,
  the "closing the book" look.
- **Hands with pipe:** holding a billiard by the bowl, pointing at a stamp with a
  magnifier, reaming, holding up a stem — pipe **never lit**.
- **Full body** in the workshop outfit, and seated at the bench.
- Only if drift appears later: train a **character LoRA on 20–30 of these generated
  on-model images** (FLUX.2 trainer on fal.ai) — never on the real photos.

### Step E — The cast (four more characters, §5)
Same Steps B–D, but with **no reference photos** — they are designed from words only, so
they are free of likeness problems and of any real person's rights.

### Step F — Voices
- Professor: keep the locked clone. **PVC upgrade** when you record the reading pack:
  verified requirements — floor 30 min, recommended 2–3 h of one consistent voice, one
  language per clone (record the pack in **English only**, no Arabic mixed in, the pack
  already says this), quiet room, consistent distance, no compression. Creator plan or
  above. Loudness target −23 to −18 dB RMS, peaks −3 dB.
- Cast: **ElevenLabs Voice Design v3** — describe the voice in words, get three
  candidates, pick one. Prompts drafted in §5. You pay only for the prompt characters.
- Dialogue scenes: **Eleven v3 Text to Dialogue API** — one JSON of speaker turns, each
  turn its own voice_id, audio tags like `[laughs]`, `[whispers]`, natural overlaps.
  This is how the Professor and the Assistant talk *to each other*.

### Step G — Animation, by shot type (this is the part that was missing)

| Shot type | Tool (verified 2026-09-10) | Why | Cost signal |
|---|---|---|---|
| **Talking close-up, one character** | HeyGen **Avatar IV** (illustrated faces supported; Avatar V is for photoreal humans, not us) | best lip-sync + micro-expressions; ElevenLabs voice can be linked | ≈20 credits/min on Creator per May-2026 reviews |
| **Two or three characters talking in one frame** | **Hedra Character-3** (native multi-character scenes, stylized images, gaze direction) | one pass, one frame, conversational rhythm | 6 credits/s; Creator $30 ≈ 11 min/month at 720p |
| **Scene with movement + dialogue (workshop, cabinet, guest arrives)** | **Kling 3.0 Omni** "Elements": bind each character's images **and a ≥3 s voice** to a named element; multi-shot up to 6 shots; lip-sync in 5 languages; 50 named elements per account | keeps the cast on-model across cuts | 5 s ≈ 3 cr · 10 s ≈ 4 cr · 15 s ≈ 6 cr on kling.ai tiers (Standard $6.99 → Ultra $59.99/mo) |
| **Stylized episodic multi-shot (alternative)** | **Seedance 2.0** reference-to-video, 15 s clips with 4–7 shots | 2026 guides call it the workhorse for stylized episodic animation | check current pricing when we get there |
| **Hands doing the work (reaming, cleaning, reading stamps)** | **NOT an avatar tool.** Two honest options: (a) **real macro footage of your hands** on the bench, cut in; (b) **Runway Act-Two performance capture**: you film yourself doing it, the cartoon Professor reproduces head, face, body *and finger-level hand motion* | avatars cannot manipulate objects; Act-Two exists exactly for this | Runway credits; Act-Two public since 2025-07-15 |
| **Cinematic establishing shots** | Veo 3.1 Ingredients (3 reference images) — good but reference mode sits behind Google AI Ultra ($250/mo). **Not recommended** until the show earns it. | | |

### Step H — Gates (in order, each one a yes/no from you)
1. **Ten-second gate:** master portrait → HeyGen Avatar IV → locked voice → the line
   *"Welcome to my workshop. Tonight, my assistant made a very interesting mistake…"*
   Judge: mouth tracks, voice belongs to this face, still you.
2. **Two-shot gate:** Professor + Assistant, 20 s, Hedra multi-character, Text-to-Dialogue.
3. **Hands gate:** 15 s of Act-Two (or real hands) — a pipe being reamed.
4. **Episode 01 remake** (clean airway) with all three shot types cut together.
Only after gate 4 do we talk about a channel launch — that is your gate, not mine.

## 5. The cast bible — first draft for Farid's verdict

House rules for all five: one house style (§4 B); no real person's likeness except the
Professor's; names are working names (**you choose the final names** — avoid brand-adjacent
names, the F. Dunhill lesson); nobody smokes on camera — pipes are handled, admired,
repaired, never lit.

### 5.1 The Professor (Farid's likeness — locked design)
- **Role:** the master of pipes, accessories, restoration and dating. The encyclopedia is
  his life's work; the episodes are moments we catch him working on it. Scholar, not
  influencer. Closes a book and names it at the end of every episode.
- **Look (from your photos + your bible):** ~60s, elegant and slim, short grey hair under
  a **small Irish flat cap** (dark tweed), **gold rectangular half-rim glasses** (as in
  IMG_3935/5045), short grey stubble beard, the **two cheek moles kept** (they are identity
  anchors — the old channel avatar proved it), waistcoat over a dark shirt, sleeves
  rolled at the bench, **pipe in hand, never lit.**
- **Voice:** the locked ElevenLabs clone → PVC.
- **Never:** lights the pipe; guesses a date; mocks the Assistant.

### 5.2 The Cabinet — "Madame of the Cabinet" (working name)
- **Role:** the nice lady who keeps the cabinet and the Archive. She knows where every
  pipe is and which catalogue page proves it. When the Professor says "the 1929 Peterson
  catalogue says…", she is the one who brings the page. She is the voice of the
  References Corner ("Our References"). Warm, unhurried, a little proud of her shelves.
- **Look:** 60s, silver hair pinned up, reading glasses on a chain, cardigan, keys.
- **Voice Design prompt:** *"Elderly British woman, warm and wise, unhurried, slightly
  amused, like a museum keeper who loves her collection; clear diction; perfect audio
  quality."*
- **Never:** contradicts the engine's dating bracket; she reads the source, she doesn't
  invent.

### 5.3 The Assistant (working name to be chosen)
- **Role:** the beautiful, cheeky, mischievous young assistant — the audience's body inside
  the show. Her mistakes are the episodes ("tonight's subject"); the **Book of Mistakes** is
  hers. Arc across seasons: employee → falls in love with the craft → skilled → earns her
  own episodes. Playful and quick, never stupid; she asks the questions the viewer is too
  shy to ask.
- **Look:** late 20s, bright eyes, modern workshop apron over a smart blouse, hair tied
  back for bench work, always one tool in the wrong pocket.
- **Voice Design prompt:** *"Young woman, late twenties, bright and playful, quick
  mischievous energy with a warm laugh, light British-international accent, confident,
  perfect audio quality."*
- **Never:** vulgar; the "naughty" is mischief and cheek, kept elegant, per the house.

### 5.4 The Third Chair (working name)
- **Role:** the guest chair by the bench. Whoever sits there brings **doubt**: a pipe they
  could never identify, a claim they read on a forum, a catalogue they say nobody else
  has. It is the level-3 collector of the master plan — the professional who comes to test
  us and leaves to testify. Can be one fixed character (the sceptical old collector) *or*
  a rotating guest. **Recommendation: one fixed sceptic** first (cheaper: one design, one
  voice), rotating guests later.
- **Look:** 50s, bow tie, tweed, a loupe on a cord, a leather case of pipes on his knee.
- **Voice Design prompt:** *"Middle-aged man, dry, sceptical, precise, refined British
  accent, a collector who has seen every fake, perfect audio quality."*

### 5.5 Alfred (working name — see note)
- **Role:** the house's old hand: the man who receives the "patients" (broken pipes), keeps
  the drawer of them, announces the guest, brings tea, and "discharges" the finished
  restorations to the shelf. Comic timing, very few words. He also opens and closes the
  workshop — the show's frame.
- **Look:** 70s, tall and straight, waistcoat and sleeve garters, a cloth over the arm.
- **Voice Design prompt:** *"Elderly English butler, deep, calm, dignified, dry humour,
  very slow pacing, perfect audio quality."*
- **Note on the name:** "Alfred" is an ordinary name and fine to use; what we must not
  copy is the famous comic-book butler's look and story. Our Alfred is a workshop man,
  not a manor butler.

Structured copy for the Builder: `docs/professor/CAST.yaml` (one source of truth — the
bible text above is generated from it in spirit; when you change a character, change the
YAML first).

## 6. The ten-second test, remade (the first gate)
1. Master portrait approved (Step C, with the three-person likeness test).
2. HeyGen → Avatar IV → upload the master → link the locked ElevenLabs voice.
3. Line: *"Welcome to my workshop. Tonight, my assistant made a very interesting mistake…"*
4. Verdict recorded in this file with the date.

## 7. What Farid does now (small, in order)
1. **Say YES/NO to the house style** (painterly 2D soft shading) and to the five
   character sketches in §5, or change them in words.
2. **Trash the retired portraits** in Drive if you want them gone (I did not delete
   anything you uploaded — channel law), or tell me the two file names and I will.
3. **Move the 150 PC photos** into Drive `Faces/PC_150/` (or let a local session pick the
   REF_KIT from them — it can see the PC, I cannot).
4. **Record the PVC reading pack** when you have a quiet hour: English only, one section
   per file, drop into `Downloads/voice/PVC/`.
5. **Confirm the tools you already pay for** (HeyGen tier, ElevenLabs tier). Kling / Hedra /
   Runway are new spend → your gate; I will not subscribe to anything.
6. Nothing else. Everything else in this document is my work.

## 8. Council suggestions — checked, as ordered
The council documents in Drive (`COUNCIL_EVAL_ROUND2_faridunhill_2026-08-15.md`,
`COUNCIL EVALUATION ROUND 2 — FARIDUNHILL (FINAL).md`) are about the **store spine /
control room**, not the Professor. Under the research-first law each item gets a verdict:

| Council item | Verdict (2026-09-10) |
|---|---|
| Fingerprint uniqueness enforced at mint + check character + multi-row lookup = UNKNOWN | **CONFIRMED** — standard engineering practice; the collision table in the report is correct maths for 5-char codes. Needs a *local* audit query on the real DB (local session). |
| Heartbeat / dead-man push to the phone | **CONFIRMED** — cheapest, most-skipped item; agree. |
| Short SQLite write transactions, WAL + busy_timeout, never hold a transaction across an AI call | **CONFIRMED** — matches SQLite's own concurrency guidance. |
| Rename "instant rollback" to STOP; build real undo separately; put STOP on the phone | **CONFIRMED** — naming point is right, especially for a non-native reader under stress. |
| Sale-event push (webhooks) as a trigger-to-verify, not as money proof | **CONFIRMED** in principle; both eBay and Etsy offer notification APIs — the exact endpoints must be verified against the current developer docs at build time (vendor docs were not fetchable from this sandbox today). |
| PENDING_VERIFY → CONFIRMED on every write | **CONFIRMED** — sound. |
| Claims check (every date/stamp/maker in generated copy must trace to a cabinet entry) | **CONFIRMED and already our law** (honesty law + "entries generated from cabinets"). |

None of these is adopted by this document — they are for the local store spine; this is
the verified reading so the next session does not re-argue them.

## 9. Sources (seen 2026-09-10; vendor domains marked ✗ were egress-blocked from this sandbox, so their facts come via search summaries and independent pages)
- Nano Banana Pro reference limits (14 images, 5 people, 4K): Google DeepMind / blog.google ✗ via search; [fal.ai — best image editing tools 2026](https://fal.ai/learn/tools/ai-image-editing-tools); [The Insight — Nano Banana Pro vs Midjourney vs Flux](https://www.theinsight.tech/articles/best-ai-image-generators-in-2026-i-tested-nano-banana-pro-vs-midjourney-vs-flux-heres-what-actually-wins); [Imagine with Rashid — consistent characters with Nano Banana Pro](https://imaginewithrashid.com/how-to-create-consistent-characters-using-gemini-nano-banana-pro/) ✗ via search
- Turnaround sheets at 4K: [AnimateAI — 2026 leaders review](https://animateai.pro/blog/2026-ai-video-generation-leaders-nano-banana-kling-3-0-and-hailuo-2-3-performance-review/)
- LoRA: [nerdbot 2026-09-05 — when to train a LoRA](https://nerdbot.com/2026/09/05/from-one-reference-image-to-a-reusable-character-asset/); [thefluxtrain — noob's guide 2026](https://thefluxtrain.com/blog/noobs-guide-to-flux-lora-training/); [fal.ai — training FLUX.2 LoRAs](https://blog.fal.ai/training-flux-2-loras)
- HeyGen Avatar IV / props limit / Avatar V vs IV: [help.heygen.com — custom motion prompts](https://help.heygen.com/en/articles/12805098-fine-tune-avatar-gestures-and-movements-with-custom-motion-prompts-avatar-iv-v) ✗ via search; [AI Tool Analysis — HeyGen review May 2026](https://aitoolanalysis.com/heygen-review/); [EzUGC — HeyGen review 2026](https://www.ezugc.ai/blog/heygen-review); [therundown — Avatar V vs IV](https://www.therundown.ai/tools/avatar-v)
- Hedra Character-3 multi-character + pricing: [magichour — Hedra guide 2026](https://magichour.ai/blog/guide-to-hedra-ai); [fluxnote — Hedra review 2026](https://fluxnote.io/guides/hedra-ai-review); [videoai.me — Hedra vs HeyGen](https://videoai.me/compare/hedra-vs-heygen) ✗ via search
- Kling 3.0 Omni elements, voice binding, multi-shot, pricing: [kling.ai — subject binding guide](https://kling.ai/blog/kling-3-subject-binding-character-consistency) ✗ via search; [kling.ai — credit cost guide](https://kling.ai/blog/kling-video-3-0-credit-cost-guide) ✗ via search; [Atlas Cloud — Kling 3.0 review](https://www.atlascloud.ai/blog/guides/kling-3.0-review-features-pricing-ai-alternatives); [morphic — Kling 3.0 guide](https://morphic.com/resources/how-to/kling-3.0-guide)
- Seedance 2.0 for stylized episodic: [Atlabs — consistent cast in Seedance 2.0](https://www.atlabs.ai/blog/how-to-build-a-consistent-cast-of-ai-characters-in-seedance-2.0-for-a-video-series); [MindStudio — what is Seedance 2.0](https://www.mindstudio.ai/blog/what-is-seedance-2-video-model)
- Veo 3.1 Ingredients (3 refs, AI Ultra): [Google Cloud — Veo 3.1 prompting guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1); [sider — Veo 3.1 consistency](https://sider.ai/blog/ai-tools/how-veo-3_1-maintains-character-scene-consistency-in-ai-video)
- Runway Act-Two (hands, performance capture): [Runway help — Act-Two](https://help.runwayml.com/hc/en-us/articles/42311337895827-Performance-Capture-with-Act-Two); [AI Wiki — Act-Two](https://aiwiki.ai/wiki/runway_act_two)
- ElevenLabs PVC requirements, one-language rule, loudness: [elevenlabs.io — PVC docs](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning) ✗ via search; [ElevenLabs blog — 7 tips](https://elevenlabs.io/blog/7-tips-for-creating-a-professional-grade-voice-clone-in-elevenlabs) ✗ via search; [help.elevenlabs.io — why does my voice change accent](https://help.elevenlabs.io/hc/en-us/articles/19631995406481-Why-does-my-voice-change-accent-or-language); [Coval — ElevenLabs review 2026](https://www.coval.ai/blog/elevenlabs-review-2026-voice-cloning-and-synthesis-capabilities-explained/)
- Eleven v3 Text to Dialogue + Voice Design v3: [elevenlabs.io — Text to Dialogue docs](https://elevenlabs.io/docs/overview/capabilities/text-to-dialogue) ✗ via search; [ElevenLabs — Voice Design v3](https://elevenlabs.io/blog/voice-design-v3) ✗ via search; [elevenlabsmagazine — Voice Design prompting guide 2026](https://elevenlabsmagazine.com/elevenlabs-voice-design-guide-2026/)

---
*Verdicts go below with dates. Next: Farid's YES/NO on §5 and §7.*
