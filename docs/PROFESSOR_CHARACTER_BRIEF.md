# THE PROFESSOR — CHARACTER DESIGN BRIEF
Version 1.0 | 2026-07-31 | Written after Farid's Gemini takes (the best results so far,
and still rejected: *"I need professional output"*)

**What this document is.** Two things at once:
1. **The exact diagnosis** of why every attempt so far — 2 LoRAs, injection, voicebox,
   identity-editing, and now Gemini — produces something that is *almost* right and
   never professional.
2. **The brief you hand a professional character designer** — and the same yardstick
   you use to judge any future AI take. It converts "I don't like it" into a list of
   named, testable requirements.

---

# PART 1 — THE EXACT PROBLEM

Farid asked: *"we are in the 21st century, I have all Claude power, we can fund the
tools — point me to the exact problem if there is one."* There is one. It is not
money, not tools, and not the century.

## 1.1 The problem is not "can a model draw a cartoon of Farid"

The Gemini takes settle that question. They are recognisably him, correctly lit,
high resolution. **The stylisation step works.** So that is not where the failure is.

## 1.2 The problem: AI stylisation ADDS a style. Character design SUBTRACTS.

This is the whole thing, in one sentence.

A professional character designer looks at a face and decides **which three or four
features carry the identity** — the brow, the set of the eyes, the line of the nose,
the way the mouth sits — then **exaggerates those and throws almost everything else
away.** That deletion is the craft. It is why a well-designed character is
recognisable as a *black silhouette*, and why a child can draw one from memory.

A generative model cannot decide what to throw away, because it has no idea what the
identity *is*. So it keeps everything — every pore, every blotch, the exact
photographic position of every mole, the real asymmetry of a tired eye — and then
coats it in smooth plastic shading.

The result is not a drawing. **It is a retouched photograph wearing a cartoon's
lighting.** That is precisely the "almost, but amateur" feeling, and it is why more
prompting, more tools, or more money will not fix it. It is a category error, not a
quality shortfall.

## 1.3 Read the takes against that rule

| What I see in the takes | Why it reads amateur |
|---|---|
| Skin keeps photographic pores, blotches and shading on cartoon geometry | Real skin on unreal proportions is the classic uncanny signature. Designed characters use flat, painted skin with **drawn** detail |
| Every mole copied at photographic size and position | A designer keeps **one or two** as character marks, redrawn at character scale. Copying the map is transcription, not design |
| Enlarged glassy eyes with photoreal irises (takes 1 and 4) | Doll effect. Designed eyes use simplified iris shapes and a **fixed** highlight position that repeats every frame |
| Hairline artifacts — the odd peak in take 1, real hair strands elsewhere | Hair must be designed as **shapes**, not rendered as fibres, or it changes on every generation |
| All five takes wear the same tired, neutral expression | **This is the biggest failure and it is not technical.** A character needs a *defining* expression — warmth, mischief, authority. These read as a man who did not sleep well, not a beloved professor |
| No designed costume. The blue striped jacket is just the source photo's shirt | The character bible says: elegant, slim, **small Irish cap, glasses, pipe in hand never lit.** None of that is present in a single take |
| No silhouette. Generic blurred bookshelf background | A professional character is identifiable as a black shape at thumbnail size. A photoreal head with glasses is not |
| Take 5 (the watercolour baker) is charming — and it is a different person in a different job | It proves the point: change the style and the identity drifts, because nothing was ever **specified** — each image is a fresh sample, not a build from a spec |

## 1.4 The second problem, which is fatal for an automated show

Even if one take were perfect: **a generated image is not a character. It is a sample.**

The show needs the *same* man in episode 1 and episode 400. Generation re-samples the
distribution every time — ears change, eye spacing drifts, moles move, the jaw
softens. There is no mechanism inside prompting that makes two generations identical,
because identity was never written down anywhere. It exists only as a lucky pixel
arrangement in one output file.

**A character is a specification, not an image.** Studios call it a model sheet: fixed
geometry, fixed proportions, a colour script, defined shape language. That document is
what makes the character reproducible by a different artist, a different tool, a
different year. We have never had one. Every attempt has tried to reach consistency by
repeating a prompt, which is like trying to reach a fixed address by rolling dice.

## 1.5 So the exact problem, in one line

> **We have been buying generations when what we need to buy once is a design.**

Nothing about the century, Claude, or the budget is the constraint. The constraint is
that a design decision — what to keep, what to delete, what makes this man *him* —
has never been made by anyone, human or machine.

---

# PART 2 — THE FIX, IN THE ORDER THAT WORKS

## Step 1 — Buy ONE human character design pass *(this is the answer)*

Hire a professional character designer (freelance character/animation designer;
concept artists who do "character model sheets" for animation). Give them Farid's
photos and this brief. What comes back is not a picture — it is **the specification**:
a turnaround, an expression sheet, a costume sheet, hands, and the shape rules.

Why this ends the two-year problem: the designer performs exactly the operation the
machine cannot — **deciding what to delete.** After that, the AI tools become good
again, because they are no longer being asked to invent a character; they are being
asked to *reproduce a reference*, which is the thing they genuinely do well.

Cost is a professional fee for one job, not an ongoing spend — modest against what has
already been spent on failed attempts. **Confirm current market rates before
commissioning; do not treat any figure in this file as a quote.**

## Step 2 — Turn the approved design into a machine-reproducible asset

Two routes; both start from the same approved sheet.

- **2D route:** the approved sheet becomes the permanent reference image for every
  generation (character-reference / multi-image mode), and — only if drift appears —
  a character LoRA trained on ~30 images **generated from the sheet.** Never on
  Farid's photographs. That was always the trap.
- **3D route (the one that is automated forever):** build a stylised 3D character
  from the sheet, once. Then consistency is **guaranteed by construction, not by
  luck** — episode 400 renders from the same file as episode 1. Lip-sync from an
  audio track is a mature, solved technique with blendshapes. Same for the assistant.
  Higher setup effort, zero drift forever, and it makes the workshop a real set the
  camera can move around in.

**My recommendation: sheet → 3D rig.** It is the only route where "automated" is a
property of the system rather than a hope, and automation is the whole point of the
project.

## Step 3 — Design the Assistant in the same commission

She is **invented** — she is nobody's likeness. That means she has no identity
constraint at all, which is the entire source of difficulty on the Professor. She is
the *easy* character and she should be designed in the same pass, so the two share one
visual language instead of looking like they came from two different shows.

---

# PART 3 — THE BRIEF ITSELF (hand this to the designer)

## 3.1 The show
Short, fun, informative episodes on pipe collecting, restoration and dating, published
to YouTube and social as the organic engine for a pipe encyclopedia. Two recurring
characters. Warm, literary, slightly Victorian world. Not loud, not "influencer."

## 3.2 The Professor
- **Likeness:** based on the supplied photographs of a real man (the owner). He must be
  **recognisable to people who know him** — but as a *designed character*, not a
  retouched photo. Deliberate exaggeration is wanted, not avoided.
- **Character:** elegant, slim. Master of pipes, restoration and repair. A scholar, not
  a salesman — he closes a book and names it at the end of every episode. Patient,
  dry humour, quietly proud of his workshop.
- **Costume (fixed, from the character bible):** small Irish cap · glasses ·
  waistcoat/workshop dress · **a pipe in his hand that is NEVER lit** — no smoke, no
  flame, ever, in any frame. This is an absolute rule, not a style preference.
- **Defining expression:** warmth with authority. If the neutral face reads tired or
  sad, the design has failed.

## 3.3 The Assistant
- Invented character, no likeness reference. Warm, charming presence; beginner's
  enthusiasm. She makes the honest mistakes every new pipe smoker makes, and the
  Professor corrects her — **her mistake is each episode's subject.**
- **Arc across seasons:** employee → falls in love with the craft → becomes genuinely
  skilled → eventually earns her own episodes. The design must age gracefully with
  that arc (same character, growing confidence in posture and dress).
- Must read as a colleague and a learner. Not a mascot, not decoration.

## 3.4 Style targets
- Shape language: soft, rounded, hand-crafted — closer to a warm illustrated
  storybook or a stylised 3D feature than to photorealism.
- **Skin must be painted, not photographic.** No pores, no photographic blotches.
- **Maximum two facial marks** on the Professor, kept as deliberate character marks,
  redrawn at character scale.
- Eyes: simplified irises, fixed highlight position.
- Hair: designed as shapes, never as strands.
- Palette must sit beside the brand's Victorian browns/golds without clashing.

## 3.5 Deliverables required
1. **Turnaround:** front, ¾, profile, back — both characters.
2. **Expression sheet:** at least 8 each — warm, amused, stern, curious, disappointed,
   delighted, explaining, listening.
3. **Hands:** holding a pipe, tamping, pointing, presenting an object. *(Hands are how
   this show teaches; they are not optional.)*
4. **Costume sheet** including the cap, glasses and unlit pipe.
5. **Colour script / palette** with hex values.
6. **Silhouette sheet** — both characters as flat black shapes.
7. **Source files** (layered), plus flat PNGs at high resolution.
8. Written **shape rules**: what may change between shots and what may never change.

## 3.6 Acceptance tests — run every one before paying, and on every future AI take

- **Silhouette test.** Fill the character solid black. Still identifiable? If not, the
  design has no shape language — reject.
- **Thumbnail test.** Shrink to 64 px. Is it still clearly him? YouTube is won or lost
  at thumbnail size.
- **The same-person test.** Put five separate renders side by side. Could a stranger
  cast them as one character in one show? **This is the test every attempt so far
  fails, and it is the one that matters most for an automated series.**
- **The child test.** Can someone draw the character from memory after ten seconds?
  That is what "designed" means.
- **The expression test.** Cover the costume. Does the neutral face read as *warm
  authority* rather than tired?
- **The Farid test.** *"Is that me?"* — final, absolute, and his alone. Style problems
  are fixable in a later pass; a lost likeness kills the take.

---

# PART 4 — WHAT SHOULD NOT WAIT FOR ANY OF THIS

The character is **one swappable component** of the show. The engine around it — the
part that actually produces traffic — depends on none of it and has never been built.
See `PROFESSOR_PROJECT.md` §"The Episode Engine". Build the engine with a placeholder
presenter; drop the approved character in when the design lands.

**Every week the engine waits for a face is a week of episodes not published.**

---

# PART 5 — ★ THE STYLE IS DECIDED (Farid, 2026-07-31)

Farid sent three frames from a sponsored solar video — an elderly couple at a
computer, outdoors under new panels, and over a map — and said: **"I can accept
something like this."** That reference settles the style question, and it is worth
understanding *why* it works, because it confirms every line of Part 1.

## 5.1 What that style actually is
Inked 2D comic / graphic-novel illustration: **heavy black outlines**, flat cel
shading, warm limited palette, light digital-paint texture. Still panels with a slow
camera move, burned-in captions, and a voice-over. No talking mouths on screen.

## 5.2 Why it succeeds where our Pixar-style takes failed — four reasons

1. **The ink line does the subtraction for us.** A black contour *is* the decision
   about what to keep. It deletes pores, blotches and photographic mole-maps
   automatically. That is Part 1.2 solved by the style itself, without a designer
   having to redraw every frame.
2. **The style is forgiving.** Look closely at the ad: the man's hand on the keyboard
   is anatomically loose. It does not matter — in ink, an error reads as *style*. In
   smooth 3D, the same error reads as a *defect*. We were fighting on the least
   forgiving ground available.
3. **Consistency comes from costume, not from the face.** He is beige cardigan + blue
   shirt + round glasses + white side-tufts; she is green blouse + pearls + grey bob.
   You recognise them across three completely different scenes **before you ever look
   at the face.** That is a design signature, and it is cheap to enforce.
4. **Nobody's mouth has to move.** The characters never talk on camera — a voice-over
   narrates over still panels. **This deletes lip-sync, avatar rendering, HeyGen
   credits and character drift from the project in one stroke.** ENCYCLOPEDIA.md calls
   HeyGen "the dominant cost." That cost is now zero.

## 5.3 And it answers Farid's real objection
> *"I can photo my hands, ok — but every episode I have to bother and video my hands
> during the repair. That is completely another idea."*

Correct, and that objection killed my earlier recommendation. In this style **the
hands are drawn, not filmed.** A panel shows the reamer in the professor's hand at
the exact wrong angle, and the next panel shows it right. Nothing is filmed, ever.
Fully automated, and it teaches better than a live shot because the drawing can
exaggerate the mistake.

## 5.4 THE STYLE LOCK — our version *(replaces §3.4 where they conflict)*

- **Medium:** inked 2D comic illustration. Bold black outlines, cel shading, subtle
  paper/paint texture. **Never** smooth 3D, never photoreal, never soft airbrush.
- **Palette:** the brand's Victorian world — briar browns, tobacco amber, brass and
  gold, deep green, warm lamplight. Cool tones only for daylight windows.
- **Line weight:** heavy on the character silhouette, lighter inside. This is what
  makes the thumbnail test pass.
- **PROFESSOR — costume signature (must appear in every panel):** small Irish cap ·
  glasses · tweed/waistcoat in warm brown · **unlit pipe in hand, never lit, no smoke,
  no flame, ever.** Elegant, slim.
- **ASSISTANT — costume signature:** one distinctive colour that is hers alone
  (proposal: deep teal or plum, so she never blends into the workshop browns) ·
  a work apron over it as she grows into the craft.
- **Likeness in ink is EASIER, not harder.** Ink is caricature, and caricature is how
  a likeness survives simplification: brow line, nose profile, the shape of the
  glasses, the jaw. Those four carry Farid. Everything else can go.
- **Backgrounds:** the workshop as a real, repeatable set — the drawer of "patients,"
  the shelf of finished restorations, the lamp, the bookshelf. Same set every episode
  builds a world the viewer recognises.

## 5.5 What still needs a human pass
The reference ad's characters are **invented archetypes** — nobody's likeness — which
is why their consistency was easy. Ours must be recognisably Farid, so one design pass
(Part 2, Step 1) still buys the thing generation cannot: a decided, repeatable face.
But the target is now far cheaper and far more likely to succeed, because the designer
is drawing **ink, not skin.**

## 5.6 Ready-to-run generation prompt *(for the next round of takes)*

```
Inked 2D comic-book illustration, bold black outlines, flat cel shading, warm
limited palette (briar brown, brass, amber lamplight), subtle paper texture.
NOT 3D, NOT photorealistic, NOT airbrushed.

An elegant, slim professor of pipe restoration — KEEP THIS MAN'S LIKENESS from
the reference photo: his brow line, his nose profile, his jaw. Simplify
everything else; do not copy skin detail, pores, or moles.

He wears a small Irish flat cap, thin gold-rimmed glasses, a warm brown
waistcoat with rolled sleeves. He holds a briar pipe in his hand —
THE PIPE IS NEVER LIT: no smoke, no flame, no glow.

Setting: his workshop — workbench, brass lamp, a shelf of restored pipes,
a drawer of broken ones. Head-and-shoulders, looking at the viewer.
```
Change **one** variable per take, number them, and judge with the six tests in §3.6 —
especially **the same-person test**, which is the one that decides whether a series is
possible at all.

---
*Character bible rules (cap, glasses, unlit pipe, his-likeness law) are Farid's and
are not negotiable by any designer, agency or model.*
