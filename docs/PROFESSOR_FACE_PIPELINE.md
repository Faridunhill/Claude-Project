# The Professor's Face — Character-Bible Pipeline

> Companion to `PROFESSOR_PROJECT.md`. Goal: a cartoon professor with **Farid's face** that stays
> consistent forever — without LoRA training. Method: approve ONE portrait (like the voice was
> approved after 13 takes), then never generate him from text again.

## Step 1 — The source photo

One photo decides everything. Requirements:
- Front-facing, eyes to camera, neutral-to-slight-smile
- Even light on the whole face (daylight from a window is ideal), no hard shadows
- Sharp, high resolution, nothing covering the face
- Plain background preferred (not required)

Save it as `assets/professor/source.jpg` in the project.

## Step 2 — Generate candidate portraits (the "13 takes")

Use an identity-preserving **editing** model — you upload the photo and instruct the
transformation (Gemini image editing, GPT-image, or Flux + face-ID adapter in ComfyUI).
Do NOT use text-to-image alone and do NOT train anything.

### Base prompt (fill the brackets, keep the identity clause)

```
Transform this exact man into a [3D-animated / hand-drawn / painterly] cartoon character:
a distinguished professor of pipe craft and restoration.
KEEP HIS LIKENESS — same face structure, same eyes, same nose, same expression lines;
anyone who knows him must recognize him instantly.
Style: [e.g. warm Pixar-like 3D / classic European comic / vintage storybook illustration].
He appears about [age] years old, [beard/moustache/clean-shaven], [glasses: yes/no, style].
Wearing: [Victorian workshop waistcoat and rolled sleeves / tweed jacket / leather work apron].
Setting: neutral warm background, portrait framing, head and shoulders,
soft workshop lighting, looking at the camera.
```

### Iteration rules
- Change **one variable per take** (style OR age OR outfit — never several at once),
  and note what changed for each numbered take (`take-01.png`, `take-02.png`, …).
- Judge only one question: **"Is that me?"** Style problems are fixable in later takes;
  a lost likeness means the take is dead.
- When one portrait makes you say *"that's him — that's me"* → it becomes
  `assets/professor/BIBLE.png`. It is now permanent. Version it like source code.

## Step 3 — Character-bible rules (after approval)

1. Every future image of the professor is generated **from BIBLE.png as reference image**
   (character-consistency / multi-image reference mode), never from a text description.
2. Build a **character sheet** next: front view, 3/4 view, profile, 2–3 expressions,
   full body in the workshop outfit — all generated from BIBLE.png. Save in `assets/professor/sheet/`.
3. If consistency ever degrades at scale: train a **character LoRA on ~30 images generated from
   the sheet** (never on Farid's photos directly — that's the trap the first two attempts hit).

## Step 4 — Make him speak (the ten-second test)

1. HeyGen → create **Photo Avatar / Talking Photo** → upload `BIBLE.png`
   (HeyGen animates illustrated faces, not only photographs).
2. Voice: the approved ElevenLabs clone — either linked via HeyGen's ElevenLabs integration
   or uploaded as audio (generate the line in ElevenLabs, upload the MP3).
3. Test line, ten seconds:
   > "Welcome to my workshop. Tonight, my assistant made a very interesting mistake…"
4. Judge: Does the mouth track well on the cartoon face? Does the voice feel like it belongs
   to this face? If yes — the professor exists. Everything after this is production, not research.

## Step 5 — Acceptance checklist

- [ ] `source.jpg` chosen
- [ ] Portrait takes iterated, one variable at a time
- [ ] `BIBLE.png` approved by Farid ("that's me")
- [ ] Character sheet generated from the bible
- [ ] HeyGen talking-photo created from BIBLE.png
- [ ] Ten-second test rendered with the approved ElevenLabs voice
- [ ] Verdict recorded in PROFESSOR_PROJECT.md

## Voice track (parallel, independent)

- Keep using the approved clone (best of 13).
- Upgrade path: ElevenLabs **Professional Voice Clone** — record 30 min–3 h of clean speech
  (quiet room, one mic, presenting tone: read pipe-restoration passages, not a word list).
  Treat it as recording the professor's first lecture. Swap the voice ID when PVC is ready;
  nothing else in the pipeline changes.
