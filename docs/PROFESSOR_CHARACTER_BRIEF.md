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

# PART 6 — ★ THE ASSET PROBLEM (Farid, 2026-07-31)

> *"Don't think the character is the only problem. Imagine every episode needs the
> pipe with anatomy, all the pipe details for the maintenance, plus tools — everything
> on screen we need to invent it."*

Correct, and it is the larger half. If every episode required inventing its pipe, its
stamps, its tools and its workshop, the per-episode art cost would never fall and there
would be no engine. Three rules fix it — and the first one is a law, not a technique.

## 6.1 THE LAW: characters are DRAWN. Objects are PHOTOGRAPHED. Never the reverse.

**We must not draw the pipes.** Not because it is hard — because it is dishonest.

A drawn Dunhill stamp is an **invented** stamp. A drawn date code is an invented date
code. A drawn hallmark, band, nomenclature line or grain pattern is a fabricated piece
of evidence in a project whose entire product is *"every fact traces to a source."*
The moment an illustrator draws a "1962 Shell" stamp, we are publishing a forgery of
our own reference material — and the level-3 collector, the exact man whose endorsement
we are hunting, is the one person on earth guaranteed to notice.

So the objects are never invented. **We already own them:** 2,000+ photographs, 264
catalogued items, the ark. The pipes are the one thing in this entire show that we
never have to create.

**This is not a compromise. It is an upgrade.** A collector wants to see the real rim
burn, the real oxidised stem, the real stamp under raking light. A drawing of a stamp
is worth nothing to him; a macro photograph of ours is the whole point.

## 6.2 THE FORMAT THIS PRODUCES: the evidence cut

Every episode alternates two registers:

| Register | What it carries | Made of |
|---|---|---|
| **The story** | Professor and Assistant, her mistake, his correction, the workshop | Drawn ink panels |
| **The evidence** | The actual pipe, the actual stamp, the actual damage, the actual repair | **Our own photographs**, captioned with the source |

The photograph appears deliberately *as* a photograph — full-bleed with its citation, or
pinned on the workbench inside the drawn scene. It never pretends to be part of the
cartoon, and the cartoon never pretends to be evidence.

**The format is the honesty law made visual.** Drawn assets carry only the *story*;
they never carry a *fact*. That single rule removes anatomy accuracy from the
illustrator's job entirely — because when precision matters, we cut to the real thing.

## 6.3 THE MATH: the asset library is FIXED, not per-episode

The fear is that every episode needs new art. It does not. Animation calls this a
**prop bible**: draw it once, reuse it forever. Here is the entire list.

| Asset group | How many, ONCE | Reused |
|---|---|---|
| Generic pipe shapes (billiard, bent, apple, dublin, pot, freehand, meerschaum, churchwarden) | **8**, three views each | Every episode. Generic only — a specific pipe is always a photograph |
| Pipe anatomy cutaway (rim · chamber · bowl · shank · mortise · tenon · draft hole · stem · button · band) | **1–3** labelled diagrams | The single most-reused asset in the series; it is also an encyclopedia illustration |
| Tools (reamer, tamper, pipe cleaners, micromesh/sandpaper, buffing wheel, retort, alcohol, wax, files, brushes, stand, pouch) | **~20** | Forever |
| Process step panels (ream · clean the shank · de-oxidise · sand · buff · wax · polish), hands included | **~30** (3–5 per step) | Recombined across dozens of episodes with different pipes |
| Workshop backgrounds (bench, shelf of finished pipes, the drawer of "patients", the lamp corner) | **~6** plates, 2–3 angles | Every episode |
| The two characters (turnaround, expressions, hands, costume) | **1 design pass** | Every episode |

**Total: roughly 70–90 drawn assets, commissioned once.** Episode 1 is expensive.
Episode 5 reuses most of it. Episode 30 is nearly free. **That falling curve is what
the word "engine" actually means** — and it is only possible because facts were moved
out of the drawings and into the photographs.

## 6.3b ★ CORRECTION — the rule in §6.1 was too broad (Farid, 2026-07-31)

> *"Still we need to solve the pipe/tool anatomy. I want a pipe cut in two equal
> halves, longitudinally, so I have seen the air flow, the inside chamber, the filter
> inside the tenon. Also if I have the real stem photo, how do you get a hole in the
> mouthpiece to fix, a crack on the shank, a chip in the bowl or stem? It is not
> impossible — but how do you montage it?"*

He found the case that breaks "never draw the pipes." You cannot photograph the inside
of an intact pipe, and you cannot photograph damage you do not have. The rule needs a
sharper edge — and the edge is not *object vs character*, it is **evidence vs
knowledge**:

| Category | Rule | Examples |
|---|---|---|
| **EVIDENCE** — anything that identifies or dates a specific object | **NEVER drawn. Photograph, or leave blank.** | Maker's marks, stamps, hallmarks, date codes, nomenclature lines, band assay marks, a named pipe's grain |
| **KNOWLEDGE** — how pipes are built, how they fail, how they are repaired | **Free to draw.** It is craft teaching, not a claim about any object | Anatomy cutaways, airflow, generic damage types, tools, every repair step |
| **Everything we already own a photo of** | **Use the photograph.** Better, ours, and free | The 2,000+ archive |

A labelled cutaway is not a claim about anyone's pipe — it is the same class of thing as
a diagram in a textbook. A bite-through drawn on a generic stem is a *type of damage*,
not an assertion that a particular Dunhill was bitten. Neither can mislead a collector.
A drawn date code can, which is why that one stays permanently forbidden.

## 6.3c THE CROSS-SECTION — five routes, ranked *(Farid's ruling, 2026-07-31)*

> *"Cut the pipe to show the air flow — it is not easy, for something you maybe use in
> one episode or a couple. **The pipe anatomy is one episode's subject. The repair is
> every day's subject.** It needs a specific saw. Let us find alternatives until we
> solve it."*

**Ruling accepted, and it reorders the whole asset budget:** the defect/repair library
(§6.3d) is the daily engine and gets built first. The cross-section is a *recurring
insert* — it reappears whenever airflow, a stuck cleaner, moisture, filter seating or
wall thickness comes up — but it does not justify buying a saw. **Sawing drops to
route 5.** Ranked cheapest-and-best first:

### Route 1 — The vector master cutaway *(do this; it is already in the commission)*
Anatomy is KNOWLEDGE (§6.3b), so it may be drawn. One master cutaway, drawn **over a
photograph of a real pipe** so the proportions are honest, in our ink style, built in
**toggleable layers**:

> airway path · chamber and wall thickness · mortise + tenon fit · **the filter
> variants** (balsa, 9 mm charcoal, meerschaum, adapter, screw system) · cake build-up
> stages · burnout · a bent version showing the curve

One asset, drawn once, serving dozens of episodes at any zoom. **Zero saws, zero risk,
and it is the answer to "I'm sure we can do better"** — the reference diagrams Farid
sent are flat, single-purpose and unbranded; a layered master beats all of them.

### Route 2 — X-ray a real, intact pipe *(cheap, novel, and it stays evidence)*
A pipe can be X-rayed without being touched. Veterinary clinics and industrial NDT
shops do it for a small fee. The image shows the **real drilled airway inside an intact
pipe** — draft-hole alignment, how far the mortise runs, whether the drilling is
centred. **Nobody in this hobby publishes that.** A CT scan goes further: one scan
yields a full volume, so a section can be taken at *any* plane, plus a 3D model.
An episode in itself: *"we X-rayed three pipes to see who drills straight."*

### Route 3 — A single 3D anatomy model *(the professional answer, one-time)*
One modelled pipe → infinite sections, any angle, exploded views, animated airflow,
toon-shaded to match the ink. It also seeds the prop library scale-up (§6.4). Same
budget line as the character commission; beats every reference diagram in existence.

### Route 4 — Pipes that are already open
Restorations arrive with **burnouts, split shanks, cracked stems** — internals already
exposed, no tool required. These are free, they are real evidence, and they arrive on
their own. **Standing rule: photograph the inside of anything that comes in broken.**

### Route 5 — Actually cutting one *(last, and only if a pipe is already dead)*
Recorded for completeness, with one note: it does not need a bandsaw. **Sanding one
side away** on a disc/belt sander — equipment already in the workshop — reaches the
chamber under full control, and vulcanite stems part easily with a razor saw. If a pipe
is beyond saving anyway, the section costs nothing. Not a priority.

**Not an option:** re-using the published diagrams. Farid's own references make this
explicit — the four-page plates on Pipedia are the **A.S.P. Pipe Parts Charts by Bill
Burney, © 2003–2011, "used by permission; all rights reserved."** Chacom's cutaway and
the French plates are equally somebody's property. LAW 2 is absolute: we cite them, we
never republish them.

**But note how Pipedia got theirs: they ASKED.** "Buy, don't pirate" has a positive
form — *ask permission*. One polite email to Bill Burney / A.S.P. explaining the
encyclopedia, with full credit and a link, costs nothing and has two good outcomes:
permission (we have a professional reference immediately, properly credited) or a no
(we draw our own, exactly as planned, having lost a day). **Action: draft that letter.
It also opens a relationship with a respected figure in the field, which is worth more
than the diagram.**

### 6.3c-ter — What those charts just handed us: the content map

Burney's plates are a specification of what a complete anatomy asset must contain. Our
layered master (route 1) should carry at least:

- Stummel = bowl + shank · rim/head · heel · foot · chamber · air passage · draft hole
  · mortise · countersink · shank face · band/ferrule · stem face · tenon · bevel ·
  bit/button/lip
- **Mortise–tenon fit: good vs poor**, with the gap that traps moisture — *repair
  content, not anatomy content*
- **Air passage drilled correctly vs drilled too high on the bowl wall** — why tobacco
  below the hole will not burn
- **Stem types:** saddle · tapered · combination · military/army · screw fitting with
  evaporator
- **Bit types:** standard · fishtail · P-lip · denture · wide comfort · single vs double
  bore (bite-resistant)
- **Filter systems** (from Farid's Chacom reference): balsa 6/9 mm · 9 mm charcoal ·
  9 mm meerschaum · adapter · screw system
- Turbulence/moisture behaviour where an obstruction sits in the airway

**This changes the priority argument in Farid's favour and against my own framing:**
half of that list is *repair* content — tenon fit, bad drilling, bite-resistant bits,
filter seating. So the cutaway is **not** a one-episode asset. It is the diagram the
daily repair episodes keep cutting back to. One asset, built once, earning every week.

### 6.3c-bis — The idea hiding in those reference plates: the multilingual term map
Farid's examples are French — *foyer · tête · tige · mortaise · tuyau · floc ·
lentille · perçage* — while the English plate says *bowl · shank · mortise · stem ·
bit · tenon · draft hole*. **Pipe anatomy has no single vocabulary; it has one per
country**, and no reference consolidates them.

A single labelled cutaway carrying **EN / FR / DE / IT** terms side by side would be a
reference asset nobody currently owns, and it makes the encyclopedia findable by
collectors searching in their own language — organic reach on ground no English-only
competitor occupies. **The mapping must be built from the cabinets and cited, not
assumed from a diagram.** Raised as an idea, not a decision.

## 6.3d ★ THE DEFECT LIBRARY — his restorations are already producing it, and throwing it away

*"How do you get a hole in the mouthpiece, a crack on the shank, a chip in the bowl?"*

**Farid buys damaged pipes for a living.** The damage is his inventory. Every
restoration he has ever done passed exactly the footage this show needs through his
hands — and it went out the door repaired and unphotographed.

**Standing rule, effective the next pipe that arrives:** photograph the damage
**before** the repair, macro, even light, with an object of known size in one frame
(the same scale-card rule already proposed for dating). Then photograph each stage.
Tag by defect type:

> bite-through · tooth chatter · oxidised stem · rim char · rim dents · heavy cake ·
> bowl chip · shank crack · tenon crack · loose/over-tight tenon · fills · burnout ·
> ferrule dent · stem-shank misalignment · previous bad repair

- **Free first task:** the 2,000+ photos already taken over ten years of listings almost
  certainly contain most of these defects already. **Tagging the existing archive by
  defect type costs nothing and may fill the library before a single new photo.**
- Where a defect genuinely is not in the library, it is **KNOWLEDGE**, so it may be
  drawn on a generic pipe (§6.3b) until a real one arrives.
- Byproduct: before/after restoration galleries are among the most-shared content in
  this hobby, and this rule produces them automatically.

**This is the same lesson as the fingerprint photos: the capture can only happen while
the object is in your hands, and every unphotographed restoration is gone forever.**

## 6.4 The scale-up, if the library ever binds

If the flat library becomes limiting (an angle we never drew, a pose we never posed),
the answer is **one 3D model per generic shape and per tool, toon-shaded to match the
ink**. One model gives every angle forever. Photogrammetry from our own photographs of
real pipes is the natural route, and it shares its capture protocol with the
indentation-layer and scale-discipline work already proposed. **Not now** — it is the
optimisation after the library proves itself, not the starting position.

## 6.5 What this changes in the commission

The designer job is **not** "two characters." It is:

1. The two characters (Part 3).
2. **The prop bible** — the ~70–90 assets in §6.3, in the same locked ink style.
3. **The workshop set** as a consistent, repeatable place.
4. The written **shape and colour rules** that let a future illustrator — or a model
   referencing the sheets — add asset #91 without breaking the world.

One commission, one style, one world. Scope it that way from the first conversation;
adding the prop bible later costs more and risks a visible style seam.

**And one instruction to put in the contract in bold:** *no maker's marks, stamps,
hallmarks, date codes or brand nomenclature are ever to be drawn.* Where a panel needs
one, it is left blank for a photograph to be cut in.

---
*Character bible rules (cap, glasses, unlit pipe, his-likeness law) are Farid's and
are not negotiable by any designer, agency or model.*
