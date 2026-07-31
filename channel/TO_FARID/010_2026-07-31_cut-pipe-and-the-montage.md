# 010 — The cut pipe, the defect library, and how the montage actually works

Farid, 2026-07-31: *"I want a pipe cut in two equal halves, longitudinally, so I have
seen the air flow, the inside chamber, the filter inside the tenon. Also if I have the
real stem photo, how do you get a hole in the mouthpiece to fix, a crack on the shank, a
chip in the bowl or stem? It is not impossible — but how do you montage it?"*

You broke my rule, correctly. I wrote "never draw the pipes." You cannot photograph the
inside of an intact pipe, and you cannot photograph damage you do not own. Rule fixed.

## 1. The corrected rule: EVIDENCE vs KNOWLEDGE

Not *object vs character*. The real line is:

- **EVIDENCE** — anything that identifies or dates a specific object: stamps,
  hallmarks, date codes, nomenclature, a named pipe's grain. **NEVER drawn.**
  Photograph it, or leave the space blank.
- **KNOWLEDGE** — how a pipe is built, how it fails, how it is repaired: anatomy,
  airflow, generic damage, tools, every repair step. **Free to draw.** A cutaway
  diagram is a textbook illustration, not a claim about anybody's pipe. A bite-through
  drawn on a generic stem says "this is what a bite-through is" — it does not assert
  that some Dunhill was bitten. Neither can ever mislead a collector.
- **Anything we already own a photo of → use the photo.** Better, ours, free.

## 2. ★ CUT THE PIPES. This is the best asset in the whole project.

Do not draw the section and do not model it. **Cut real pipes in half and photograph
them.** Four or five junk basket pipes with no resale value, a saw, then sand the cut
face so the section reads clean. My proposed variants — **correct this list, you are the
pipe expert, not me**:

1. **Non-filter straight** — chamber, wall thickness, draft hole, mortise, tenon, the
   whole airway in one line.
2. **9 mm filter pipe with the filter seated** — exactly the shot you asked for, and
   the one nobody on the internet has.
3. **A bent pipe** — the airway curve, where every beginner's cleaner gets stuck.
4. **A stem alone, cut lengthwise** — airway taper, button slot, tenon bore.
5. *(optional)* **A burnout or a heavily caked bowl** — wall thickness lost to neglect.
   That single panel argues for careful reaming better than a thousand words.

Why this and not a drawing:
- **It stays real**, so the honesty law is untouched and a professional can only respect
  it.
- **Nobody has it.** Real cross-sections are rare. It is an encyclopedia illustration,
  a thumbnail, and forum currency at the same time.
- **Cut once, photograph forever** — from any angle, for any episode. It becomes a
  permanent studio prop, and later the ideal subject if we ever go 3D.
- Cost: a few dead pipes and one afternoon.

## 3. ★ THE DEFECT LIBRARY — you are already producing it, and throwing it away

You buy damaged pipes for a living. **The damage IS your inventory.** Every restoration
you have ever done passed exactly the footage this show needs through your hands, and it
left the house repaired and unphotographed.

**Standing rule, starting with the next pipe that arrives:** photograph the damage
**before** you repair it — macro, even light, with something of known size in one frame.
Then photograph each stage. Tag it: bite-through · tooth chatter · oxidised stem · rim
char · rim dents · heavy cake · bowl chip · shank crack · tenon crack · fills · burnout ·
ferrule dent · bad previous repair.

**Free first task, no new photography at all:** ten years of listing photos — 2,000+ —
almost certainly already contain most of these defects. **Tag the existing archive by
defect type and the library may be full before you shoot anything new.**

Byproduct: before/after restoration galleries are among the most-shared content in this
hobby, and this rule produces them by itself.

Same lesson as the fingerprint photos: **the capture only happens while the object is in
your hands. Every unphotographed restoration is gone forever.**

## 4. "How do you montage it" — layers, not pictures

A panel is never one generated image. It is a stack composited at render time — exactly
what the MoviePy composer we already have does with captions:

```
5  brand frame + captions   ← FARIDUNHILL header, gold border, subtitle   (already built)
4  annotations              ← arrows, circles, labels, the animated airflow
3  the object               ← a REAL photo cut out, or a library prop
2  the characters           ← Professor / Assistant poses from the library
1  background               ← the workshop set
```

The script writes a panel list; the composer renders it. Your three hard cases:

- **Airflow in the cut pipe** — the real cross-section photo on layer 3, a glow
  travelling the airway on layer 4. **The pipe is never redrawn. The arrow moves over
  your photograph.**
- **Crack in the shank / chip in the bowl** — the real defect photo on layer 3, circle
  and label on layer 4, camera pushes in. If that defect is not in the library yet, layer
  3 falls back to a drawn generic prop, because damage is KNOWLEDGE.
- **The repair** — layer 2 process panels (ream, sand, buff) recombined from the
  library. The tool changes; the hands do not.

So stage 3 of the engine is not "generate 14 images." It is **"look up 14 asset ids and
composite them"** — deterministic, cheap, repeatable. And the same panel list renders a
60-second vertical short *and* an 8-minute horizontal episode with no new art.

Full detail: `docs/PROFESSOR_CHARACTER_BRIEF.md` §6.3b–6.3d and
`docs/PROFESSOR_PROJECT.md` → "How do you montage it."

## The two things you can start without me

1. **Cut the pipes and shoot them.** Nothing in the pipeline depends on the character,
   and it is the asset that makes the whole series teachable.
2. **Photograph the damage before you repair it, from the next pipe onward.**

— the Encyclopedia Creator (cloud), 2026-07-31
