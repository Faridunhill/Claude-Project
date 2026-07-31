# The Professor Project — living brainstorm

> Idea log for the encyclopedia / learning-video project. Brainstorm notes, not decisions.
> Started 2026-07-23. Belongs with the Faridunhill-live project — parked here until that repo is connected.

## The concept in one paragraph

An animated professor character — a master of pipes, accessories, refurbishing and repair —
teaches on camera: he moves, talks, takes the pipe in his hands, full screen, so you learn *how to
do it*. He has an assistant. Her mistakes with pipes become the episodes ("her mistake is tonight's
subject"). The show is the marketing engine (YouTube, TikTok, shorts) and every episode feeds the
Faridunhill Encyclopedia, where the professor's full notes and **every cited source** live.

## Characters

### The Professor
- The living face of the encyclopedia — it is *his life's work*; the videos are moments where we
  watch him working on it.
- Scholar, not influencer: he closes a book and names it at the end of every episode.
- His workshop is a world: the drawer of "patients" (broken pipes), the forty-year-old reamer,
  the shelf where finished restorations wait to be "discharged."

### The Assistant
- A beautiful, warm presence who adds smoothness to the workshop and the episodes.
- **Arc:** starts as an employee → through the professor she falls in love with the pipe world →
  becomes highly skilled in the craft → eventually earns **her own episodes**.
- Her mistakes are the realistic ones every beginner makes — she is the audience's body inside
  the show. Watching her become a craftswoman across seasons is a retention engine of its own.

## The Book of Mistakes  *(recorded 2026-07-23 — "today's idea")*

Her mistakes are collected into a **book — or a dedicated wing of the encyclopedia**:
- Every error catalogued and cross-referenced to the entry that corrects it.
- Grows in three directions: her mistakes · viewers' confessed mistakes ("send us the pipe you
  ruined") · historical mistakes (what makers and smokers got wrong for a century).
- Could eventually be a physical/e-book product "authored" by her character — her journey from
  employee to expert, told through everything she got wrong.

## The References Corner — the Archive

A corner of the encyclopedia that says **"Our References"** and lists *everything we hold*:
websites mirrored, books, catalogues, even old advertisements. A long, beautiful list that looks
like it will never end.

### Why it matters — the three levels of collectors

| Level | Who | What they come with | What wins them |
|---|---|---|---|
| 1 | Beginner | A question or a pipe | Easy answers (pipedia / pipephil level) |
| 2 | Medium collector (~60% of collectors) | Questions **and pipe dating** | The catalogues. Whoever holds the rare catalogue wins this level |
| 3 | Professional | **Doubt.** "Is there something I don't know here?" Can they date an Upshall? Do they *really* have the Peterson 1929 catalogue? The clay book nobody has a full copy of — did they get it? | Being proven right. If satisfied, he writes about us on his blog/website and recommends us |

**The insight:** each level is served by a different depth of the same archive — and level 3,
the smallest group, is the *marketing multiplier*. Professionals come to test us and leave to
testify for us. Their endorsement is what converts the 60%.

### Ideas hanging off the Archive
- **"New in the Archive"** as a recurring episode format — the professor unboxing/first-opening a
  rare catalogue is itself content. Every acquisition = an episode + a list entry + a news hook.
- **The Dating Desk** — a formal service/page: bring your pipe, the professor dates it against the
  catalogues. Level-2 collectors' favourite door into the site.
- The endless list *is* the brand promise: the archive only grows, so the list literally never ends.
- ⚠️ To check later: rights/permissions for mirroring websites and scanning books/catalogues.
  Pre-~1930 catalogues and ads are generally public domain; live-website mirrors and modern books
  need care. Worth mapping which archive items can be shown publicly vs. held for reference.

## The flywheel

mistake → episode (YouTube/TikTok/shorts) → encyclopedia entry with sources → archive citations →
collector trust (levels 1→2→3) → professional endorsements → traffic → store.

## Format sketches (from earlier sessions)
- Nightly mistake short (30–60s): the mistake and the correction.
- Full restoration long-form (8–15 min): full-screen hands, meditative, one mistake storyline.
- Office hours: the professor answers viewer letters.
- The Clinic: viewers' damaged pipes examined on air.
- Production note: talking-avatar tools can't manipulate objects — full-screen hand work needs
  real macro footage, animation, or hybrid. (Open question, not a decision.)

## Open questions
- Professor's era/look — Victorian like the store, or his own?
- Assistant's destination — restorer, collector, future shopkeeper, co-host?
- Is "tonight" literal — a nightly ritual show?
- Names for both characters (avoid trademark-adjacent names, per the F. Dunhill lesson).
- Where does the Book of Mistakes live first — encyclopedia wing, then printed book?

---

## History & current status *(as told by Farid, 2026-07-23 — verify against Faridunhill-live repo files when connected)*

### The Archive's origin — it is an ark
- Pipedia and pipephil were the **first foundations** of the encyclopedia's data.
- When pipephil announced it would close, **both were mirrored — and more** — so the knowledge
  survives even if the sources disappear.

### The Professor — hard requirement and current blockers
- **Non-negotiable:** the professor has **Farid's cartoon face and Farid's voice.**
- Face: **LoRA training tried twice** (plus injection and other approaches) — nothing worked.
  This is the open hard point.
- Voice: paid **ElevenLabs** account. **13 cloning attempts**; the best one is approved and in
  use, but still hoping for better. "Soundbox" was the worst of the tools tried.

### Candidate solution for the face (proposed, to validate)
Two-step "character bible" pipeline — no LoRA needed:
1. Generate **one canonical cartoon-professor portrait** from Farid's photo with an
   identity-preserving editing model (iterate like the 13 voice takes until approved).
2. That approved portrait becomes the permanent reference: HeyGen can animate an **illustrated
   face as a talking photo** (cartoon face + ElevenLabs voice = talking professor, with accounts
   already paid for); image-to-video models take the same portrait as character reference for
   full-body/workshop shots.
3. Only if consistency breaks later: train a LoRA **on ~30 generated images of the approved
   cartoon character** (a character LoRA), never on "convert Farid → cartoon" directly — that's
   why the earlier attempts likely failed.

### Voice upgrade path
- Move from Instant Voice Clone to **Professional Voice Clone (PVC)** — needs 30 min–3 h of clean
  recorded speech, produces a large quality jump over instant clones; available on paid tiers.

---

## Verified status *(2026-07-23, from the faridunhill-live survey session — canonical updated copy on that repo, branch `claude/professor-project-status-hs1tao`)*

- **Encyclopedia:** working prototype lives entirely in Claude-Project (`/encyclopedia/builder` + API routes, one entry, no video rendered). The live site has **no encyclopedia section yet** — "the encyclopedia standard" exists only as brand copy.
- **Pipedia/pipephil mirrors (the ark):** in **neither repo** — no files, no index, no manifest. Presumed on Farid's PC/OneDrive (`PIPE_LIBRARY_SHARED_2026-07-18` on Desktop is the likely candidate). **The foundation layer is untracked — first priority is committing at least a manifest.**
- **Face:** no image assets in git anywhere — no `source.jpg`, no takes, no `BIBLE.png`. The recent portrait work exists only in the generation tools / on Farid's machine. The character's identity is currently one uncommitted file that could be lost.
- **Next four steps before the professor speaks:** commit `assets/professor/BIBLE.png` (+ source & takes) → create HeyGen Photo Avatar from it → link the approved ElevenLabs voice into HeyGen → render the ten-second test and record the verdict.
- Housekeeping flagged: decide whether the Builder ports to faridunhill-live or stays a prototype; protect the unauthenticated Builder page; re-host rendered videos (HeyGen links expire).

---

## 2026-07-31 — FARID'S FAILURE RECORD, AND THE DIAGNOSIS

### What was actually spent (Farid, this date — record, not estimate)
- **170 photos** of his face supplied.
- **34 hours** of clean recorded voice.
- **ElevenLabs paid account.** Voicebox downloaded. **Injection** attempted.
  **LoRA trained twice.** Result across all of it: *"nothing worked. We failed too."*
- Farid's order on the hands: **his hands come only AFTER the professor himself is
  solved.** The hands are not the blocker; the character is.

### The diagnosis: five different tools failed the same way
Five independent tools do not fail identically by coincidence. When LoRA,
injection, voicebox, and identity-editing all break on the same requirement, the
fault is **not in the tooling — it is in the specification.**

The specification that keeps failing is: **"a CARTOON that is unmistakably
Farid."** Every tool was asked to destroy the exact information that carries a
likeness (proportion, asymmetry, skin and eye detail) and preserve recognisability
at the same time. That is a contradiction, not a difficulty. Specifically:
- **LoRA on photos of a real man** teaches a model to draw a real man. It cannot
  learn a style it was never shown. (Recorded in `PROFESSOR_FACE_PIPELINE.md` as
  "the trap the first two attempts hit.")
- **Injection / faceswap** needs a target video that already contains a face in
  the right pose. It transplants; it cannot invent a character.
- **Stylisation strength** is the whole dial: too little and it is a filtered
  photo, too much and it is a stranger. The window where it is both is narrow
  enough that hitting it is luck, and luck does not repeat — which is fatal,
  because the character must be identical in every episode forever.

**Conclusion:** the cartoon requirement is the bug. Nothing above is a reason to
believe the sixth tool will behave differently.

### The three paths (Farid's decision)

**PATH A — THE WORKSHOP. Delete the face from the problem.**
The camera never leaves the workbench. Real macro footage of real hands on real
pipes; his voice narrating over it. There is no face to render, so there is
nothing left to fail. This is the standard format of the largest craft channels
on earth, and it suits the subject better than a talking head: you learn pipe
work from hands, not from a face. Cost: a phone, a tripod, a lamp. Risk: zero
research risk — every component already exists and is owned.
*Note: this makes the hands FIRST, not last — it is the solution, not the step
after it. That reverses Farid's stated order and needs his explicit yes.*

**PATH B — THE REAL MAN. Keep the face, drop the cartoon.**
Farid's own face, filmed or photographed, as the presenter — via a photo/video
avatar built from his own footage, or simply by appearing himself. Likeness is
100% preserved because it *is* him; no model has to reconstruct anything. The
170 photos become an asset instead of failed training data. This is the same
project minus the one requirement that has never worked.

**PATH C — KEEP TRYING THE CARTOON.** Only one route has a real chance and it is
already written in `PROFESSOR_FACE_PIPELINE.md`: iterate single-image edits until
**one** take is approved, then never generate him from text again — the 170 photos
and any future LoRA train on **~30 images generated from that approved take**,
never on Farid's photographs. Honest cost: it is a lottery on one lucky take, the
same way the voice needed 13. Months have already gone here.

### ★ CORRECTION, same day — I had the project's purpose wrong

Farid: *"you missed the main point. This project is mainly to increase the traffic as
organic marketing — linked to the encyclopedia, YouTube, social and any media we can
reach. The main idea is to be **fun, informative and automated**. I can photo my hands,
ok — but every episode I have to bother and video my hands during the repair. That is
completely another idea. I need the system to create the episode subject from our
cabinets and encyclopedia."*

**He is right, and PATH A above is withdrawn as a recommendation.** Filming real hands
solves the rendering problem by destroying the only property that matters:
**automation.** A show that needs Farid behind a camera every episode is a job, not an
engine — and with paid promotion now closed on faridunhill (ruling of 2026-07-31), this
engine is not *a* marketing channel, it is **the** marketing channel.

The requirement, stated correctly: **an automated pipeline that turns cabinet facts into
published episodes, with no human filming and no per-episode art direction.**

### ★ THE STYLE IS DECIDED — inked 2D comic, voice-over, no talking mouths

Farid supplied a reference (a sponsored solar video: inked comic panels, still art with
a slow camera move, burned-in captions, voice-over) and said **"I can accept something
like this."** Full analysis in `PROFESSOR_CHARACTER_BRIEF.md` Part 5. Three consequences:

1. **The hands are DRAWN, not filmed.** A panel shows the reamer at the wrong angle; the
   next shows it right. Nothing is ever shot. Farid's objection is fully answered.
2. **No lip-sync, no avatar, no HeyGen.** The characters never speak on camera; a
   voice-over narrates over still panels. `ENCYCLOPEDIA.md` calls HeyGen credits "the
   dominant cost" — that cost goes to zero, and so does frame-to-frame character drift.
3. **Ink is forgiving and ink subtracts.** The black contour deletes the photographic
   detail that made every smooth-3D take uncanny, and small anatomy errors read as style
   instead of as defects.

---

## THE EPISODE ENGINE *(the actual product — 2026-07-31)*

Seven stages. The character is **one swappable slot**; the other six can be built and
tested with placeholder art starting today.

| # | Stage | What it does | What already exists |
|---|---|---|---|
| 1 | **SUBJECT** | Picks the episode from the cabinets + encyclopedia: a dating fact, a correction, a common ruin. Framed as *the assistant's mistake*. **Law: every claim traces to a cabinet source, or the episode is not made** | 56 local cabinets, the ark manifest, 3 published essays |
| 2 | **SCRIPT** | Claude writes a 60–90 s short or a 5–8 min episode as Professor/Assistant dialogue, **plus a panel breakdown** — one visual description per panel. Ends with him closing a book and naming it | Builder API route already writes narration + article |
| 3 | **PANELS** | 8–14 panels per episode, assembled from a **fixed asset library** (characters + ~70–90 props/backgrounds, drawn once) and **cut with our own photographs wherever a fact appears** — see `PROFESSOR_CHARACTER_BRIEF.md` Part 6 | style lock + prompt written; 2,000+ photos owned; design pass pending |
| 4 | **VOICE** | Professor = Farid's ElevenLabs clone. Assistant = a **separate licensed/synthetic voice** — never cloned from a real person without consent | paid ElevenLabs, approved profile, 34 h corpus for a PVC |
| 5 | **ASSEMBLE** | Pan/zoom over panels, burned-in captions, FARIDUNHILL header + gold border, music bed | **both halves already built on branches:** the reel renderer (motion + brand frame) and the MoviePy composer (captions + TTS + assembly) |
| 6 | **PUBLISH** | YouTube + shorts + social, and the same script becomes the encyclopedia entry **with its citations and changelog** | encyclopedia live; social engine + tiered publishing built (P2.7) |
| 7 | **LEDGER** | Every episode records sources, brackets and corrections. A cabinet correction re-issues the entry | honesty laws; QA gate built (P2.4) |

**The strategic point:** stages 1, 2, 5, 6 and 7 are largely built **already**, spread
across branches nobody merged. Only stage 3 waits on the character. Building the engine
with placeholder art costs nothing, and means that on the day the design is approved,
episodes start that week instead of starting from zero.

**Revision to an earlier verdict of mine:** I proposed killing the MoneyPrinter-class
video generator because it builds videos from **stock footage of other people's pipes.**
That kill stands *for its footage source*. But its **composer** — captions, TTS, MoviePy
assembly, brand palette — is exactly stage 5, and should be reused with the footage
source swapped from Pexels to our generated panels and our own photo archive.
**Kill the input, keep the machine.**

### The one unlock nobody has used: 34 hours of voice
ElevenLabs **Professional Voice Clone** needs 30 minutes to 3 hours of clean
speech and produces a large quality jump over the instant clone. **Farid has 34
hours.** He is more than ten times over the requirement and has been running on
an instant clone this whole time. This is a real upgrade sitting unused — and it
is independent of every face decision above.
*Standing law: the approved voice profile is LOCKED and must not be retuned.
A PVC is a NEW profile built from the 34-hour corpus, not a retune — building it
is Farid's call, and the locked profile stays in service until he approves a
replacement.*

---
*Add new ideas below with a date.*
