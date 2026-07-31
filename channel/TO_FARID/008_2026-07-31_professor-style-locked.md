# 008 — The Professor: the exact problem, and the style you accepted

Farid, 2026-07-31. Two messages from you changed this project. Both are recorded.

## 1. I had the purpose wrong — corrected

You: *"the main idea is to be fun, informative and automated... I can photo my hands,
ok, but every episode I have to bother and video my hands during the repair — it is
completely other idea."*

You are right. My "film your real hands" recommendation is **withdrawn.** It solved
the rendering problem by killing the only property that matters: automation. And since
your ruling closed paid promotion on faridunhill, this show is not *a* marketing
channel — it is **the** marketing channel. A show that needs you behind a camera every
episode is a job, not an engine.

## 2. The exact problem you asked me to point at

It is not money, not tools, not the century. In one line:

> **We kept buying generations, when what we needed to buy once is a design.**

An AI stylisation **adds** a style. Character design **subtracts** — a designer decides
which three or four features carry the identity and deletes everything else. That
deletion is the craft. A model cannot delete, because it does not know what the
identity *is*, so it keeps every pore, every blotch, the exact photographic position of
every mole, and coats it in plastic shading. **What comes out is a retouched photograph
wearing cartoon lighting** — which is exactly why it feels almost-right and never
professional. More prompting cannot fix a category error.

And the second half, which is fatal for a series: **a generated image is not a
character, it is a sample.** Every new generation re-rolls the dice — ears, eye
spacing, jaw. Consistency across 400 episodes cannot come from repeating a prompt,
because the identity was never written down anywhere.

Full diagnosis, with a line-by-line read of your Gemini takes:
`docs/PROFESSOR_CHARACTER_BRIEF.md`.

## 3. The solar ad you sent — that settles it, and here is why it works

Inked 2D comic: heavy black outlines, flat shading, warm palette, still panels with a
slow camera move, captions, voice-over. Four reasons it beats everything we tried:

1. **The ink line does the subtraction for us** — a black contour *is* the decision
   about what to keep. Pores and mole-maps are deleted automatically.
2. **Ink is forgiving.** Look at the man's hand on the keyboard in that ad — the
   anatomy is loose and nobody cares, because in ink an error reads as *style*. In
   smooth 3D the same error reads as a *defect*. We were fighting on the least
   forgiving ground that exists.
3. **Consistency comes from costume, not the face.** Beige cardigan + blue shirt +
   round glasses; green blouse + pearls. You recognise them across three different
   scenes before you ever look at the face.
4. **Nobody's mouth moves.** Voice-over on still panels. That deletes lip-sync, the
   avatar, HeyGen credits (called "the dominant cost" in our own setup guide) and
   frame-to-frame drift — all four, in one decision.

**And it answers your hands objection completely: in this style the hands are DRAWN,
not filmed.** One panel shows the reamer at the wrong angle, the next shows it right.
Nothing is ever shot. It teaches better than a live shot, because a drawing can
exaggerate the mistake.

**Style is now LOCKED** in the brief: inked 2D comic, briar-brown/brass palette, the
Professor's signature = small Irish cap + glasses + brown waistcoat + **unlit pipe,
always**; the Assistant gets one colour that is hers alone. A ready-to-paste generation
prompt is in §5.6 — run new takes with it, one variable at a time.

**Likeness in ink is EASIER than in 3D, not harder.** Ink is caricature, and caricature
is how a likeness survives simplification: your brow line, your nose profile, your jaw,
the shape of the glasses. Those four carry you. Everything else can go.

## 4. What I still recommend you buy — one human design pass

One professional character designer, one commission, both characters (the Assistant is
invented, so she is the easy one and should be drawn in the same pass). You give them
your photos and this brief; what comes back is not a picture, it is **the
specification** — turnaround, expressions, hands, costume, colour, silhouette sheet.
After that the AI tools become good again, because they stop being asked to *invent* a
character and start being asked to *reproduce a reference*, which is what they are
genuinely excellent at. Confirm current rates yourself — I will not quote a market I
cannot check from here.

## 5. The thing that should not wait — THE EPISODE ENGINE

The character is **one swappable slot in a seven-stage machine**, and I found that
**five of the other six stages are already built**, scattered across branches nobody
merged: the script writer, the reel renderer (motion + FARIDUNHILL frame + gold
border), the MoviePy composer (captions + TTS + assembly), the social publisher, and
the QA gate. Full table in `docs/PROFESSOR_PROJECT.md` → "The Episode Engine."

So: **subject from the cabinets → script as Professor/Assistant dialogue + panel
breakdown → panels → your voice + her voice → assemble → publish to YouTube/social +
the encyclopedia entry with its citations → ledger.**

I can build that engine now with placeholder art. On the day you approve the design,
episodes start that week instead of starting from zero. **Every week the engine waits
for a face is a week of episodes not published.**

*(One correction to my own kill list: I killed the MoneyPrinter video generator for
using stock footage of other people's pipes. That kill stands for its footage source —
but its composer IS stage 5, and we should reuse it pointed at our own panels. Kill the
input, keep the machine.)*

## Say the word and I start
1. Build the episode engine end-to-end with placeholder art — a real 60-second episode
   assembled from a real cabinet fact, so you can watch the machine work before the
   character exists. **This is what I would do next.**
2. Or commission-ready: I finalise the designer package so you can send it tomorrow.

— the Encyclopedia Creator (cloud), 2026-07-31
