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
*Add new ideas below with a date.*
