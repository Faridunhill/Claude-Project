# THE EPISODE ENGINE

Turns a fact from a dating cabinet into a finished episode — subject, script,
panels, assembly, ledger — with no human filming and no per-episode art direction.

```bash
node engine/run.mjs --cabinet peterson --pick 3
# → engine/out/<slug>/storyboard.html   ← open this; it plays
```

## The seven stages

| # | Stage | File | State |
|---|-------|------|-------|
| 1 | **SUBJECT** — harvest teachable facts from a cabinet, pick one | `subject.mjs` | ✅ built |
| 2 | **SCRIPT** — fact → Professor/Assistant dialogue + panel list | `script.mjs` | ✅ built (template; Claude is a drop-in) |
| 3 | **PANELS** — resolve asset ids, render the sheets | `panels.mjs` | ✅ built (placeholder art) |
| 4 | **VOICE** — ElevenLabs for the Professor, a second voice for her | — | ⏳ needs the voice ids |
| 5 | **ASSEMBLE** — storyboard that plays on the narration timings | `assemble.mjs` | ✅ built (rough cut) |
| 6 | **PUBLISH** — YouTube/social + the encyclopedia entry | — | ⏳ needs accounts |
| 7 | **LEDGER** — what was claimed, from where, what was missing | `assemble.mjs` | ✅ built |

## The three laws this code enforces — as refusals, not comments

1. **No source, no episode.** `subject.mjs` refuses any read without a cabinet
   source and prints the refusal. A read that identifies but cannot date is
   refused too, and counted in the run log — never dropped silently.
2. **Drawn art carries the story; photographs carry the evidence.**
   `panels.mjs` throws `EvidenceWithoutCitation` if a photo slot is filled by an
   uncited photograph. A drawn stamp is a fabricated fact, so the engine cannot
   be made to render one.
3. **Nothing is stated that the cabinet did not carry.** Every claim, caveat,
   confidence and source line in the narration is read out of the cabinet. The
   assistant's *mistake* is derived from the caveat — where the cabinet says a
   widely-repeated date is wrong, that wrong date is what she says.

## Why the art can change later without rewriting anything

Panels are **layers resolved by id**, never image paths:

```
5 captions + brand frame · 4 overlays · 3 the object · 2 characters · 1 background
```

`prof-explaining-3q` is an id. Whether it resolves to an ink drawing today or a
render from a 3D rig later is invisible to stages 1, 2, 4, 5, 6 and 7. Swap the
files in `assets/library.json`, re-run, and **old episodes re-render in the new
style from their saved panel lists.**

**The rule that keeps this true: no stage may ever hard-code an image path.**

## Determinism
No `Date.now()`, no `Math.random()` anywhere. Same cabinet + same `--pick` =
the same episode, byte for byte, so two runs can be compared. The build date is
passed in with `--at`.

## What a run prints
```
1 SUBJECT   25 teachable facts · 18 refused
2 SCRIPT    7 panels · 46.4s
3 PANELS    7 rendered · 12 asset ids unfilled
4 VOICE     skipped — narration written, awaiting the ElevenLabs step
5 ASSEMBLE  storyboard.html
7 LEDGER    episode.json + ledger.json
```
The unfilled-asset count is printed on purpose. **Performance never prints
without its blind spots.**

## Next
- Stage 2b: swap the template for Claude, emitting the same panel-list shape.
- Stage 4: wire the approved ElevenLabs voice; a second, licensed voice for her.
- Stage 5b: hand `episode.json` to the MoviePy composer (the surviving half of
  the killed video generator) for the finished render.
- Fill `assets/library.json` as the commissioned art lands, id by id.
