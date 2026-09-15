# The Add-a-Pipe Process — why it produces mistakes, and what replaces it

Companion to `docs/local-agents-system-plan.md`. Tasks **B3.5** and **B8** at the
end are the builder's.

---

## 1. The worked example, from a real message

A collector wrote about a live listing:

> *"You might want to read a bit about Jima pipes, because the insert is not
> meerschaum, but ceramic. This is how they were marketed as the 'Pipe of the
> Year 2000' back in the 1970s."*

The listing title asserted **Meerschaum Bowl Insert** on a €99.15 item. The
insert is ceramic. A buyer paying a meerschaum premium for ceramic is a refund,
a case, and a reputation that took years to build.

Three things are worth separating out, because they have three different fixes.

**It is not a writing mistake.** No amount of better prose prevents it. The
writer asserted a material because nothing in the system ever told it the
material was unknown. There was no field, so there was no constraint, so the
plausible word won.

**It is not a knowledge mistake either.** Nobody needed to know Jima history.
The correct output was available without knowing anything: *insert material not
identified*. Unknown was the true answer and it was never an available answer.

**It is the exact failure the repository already has a machine for.**
`marketing/qagate/gate.py:28` lists `unique_physical.materials` as a Tier A
field — the misattribution class. `marketing/qagate/lock.py` exists so that a
generator physically cannot assert a Tier A value that is not verified: it
returns ASSERT, HEDGE, or OMIT. The machine was built. This listing never went
through it.

### And a real gap, found while writing this

`marketing/expression/copy.py` calls `assertable()` **twice** — both times for
`brand`, once in the title and once in the description. It never routes
`unique_physical.materials` through the lock at all. So even the built pipeline
would not have stopped "Meerschaum". The lock protects the maker's name and
leaves the material claim wide open.

That is B8.1, and it is a small fix with a large blast radius.

---

## 2. The three rules the new process runs on

**Rule 1 — Facts and prose are separate objects.** The genome holds what was
observed. The copy is generated from the genome. A word that is not backed by a
field cannot appear in the copy, no matter how well it reads.

**Rule 2 — `unknown` is a legal, publishable value.** "Bowl insert: not
identified" is an honest listing and it sells. Guessing is the only option that
carries a refund attached. Every Tier A field gets three possible states —
verified, candidate, unknown — and unknown is never an empty box that the writer
is invited to fill.

**Rule 3 — Length is not value.** A 4,000-character encyclopedia entry around
thin notes is not a richer listing; it is more surface area for invented claims,
and it buries the six facts a buyer actually decides on. The listing carries what
is known. The encyclopedia page is a **separate document with sources**, and it
is written when there is something to say, not to fill a template.

---

## 3. The process, as it should run

Target: fifty pipes added without the process being the bottleneck. That is only
possible because verification becomes a gate rather than a research project — a
pipe with eight unknown fields ships in four minutes with eight honest "not
identified" lines.

| Step | Who | What happens | Time |
|---|---|---|---|
| 1. Photos | Farid | Fixed checklist per item — stamping, bowl, shank, stem, base, flaws (`marketing/intake/photos.py` already defines it) | 90 s |
| 2. Voice note | Farid | Sixty seconds, unstructured, in whatever language comes out. Two numbers spoken aloud: cost, floor price | 60 s |
| 3. Structure | Local seat | Transcript → genome fields. **Only fields the note or photos actually support.** Anything else is written as `unknown`, never inferred | 20 s |
| 4. Stamping OCR | Watcher | Read the stamping photo; it is the corroboration source `route_claim()` already expects | 10 s |
| 5. Route | Existing gate | `route_item()` sends Tier A uncertainty to the review queue; everything else passes | instant |
| 6. Copy | Existing generator | Every Tier A field through `assertable()` — assert, hedge, or omit | 10 s |
| 7. Claim check | Watcher | **`watch-claims.ps1`** — the new gate in B3.5. Blocks publication of any claim word not backed by a field | instant |
| 8. Publish | Farid | One click, or a queue he approves in batches | 30 s |

Steps 3 and 6 are the only ones a model touches, and both are constrained jobs
rather than open writing.

---

## 4. "No search to make sure my information"

Two honest answers, because the obvious one is a trap.

**Do not give a local model web search and ask it to verify claims.** A small
model that searches, reads and summarises produces confident, well-written,
wrong attributions — the same failure as the Jima line, with a citation stapled
to it. That is worse than unknown, because it looks checked.

What works instead, in order of reliability:

1. **The stamping.** What is physically on the pipe, read by OCR from a
   photograph. This is evidence, and the gate already treats it that way.
2. **Your own corpus.** Every lot you have bought and every item you have sold
   is ground truth nobody else has. A brand-and-model dictionary built from it,
   by script, is the reference the writer consults.
3. **CODE, when it matters.** A €99 item with an uncertain maker is worth one
   research request. A €12 item is worth the word "unknown".
4. **Collectors.** The message that opened this document is free expertise of a
   quality no search returns — which is what §5 is about.

---

## 5. The correction loop, which already exists and is not wired up

`marketing/genome/corrections.py` implements exactly what this situation needs:
an append-only corrections ledger and a **detect → quarantine → correct →
republish** state machine, where birth records are never edited and
`effective = birth + corrections` at read time.

So the collector's message should have become:

```
detect     — Tier A claim disputed by an external source
quarantine — the listing's material claim is suspended, the item stays live
             with the claim removed rather than being pulled
correct    — unique_physical.materials: "ceramic (per collector report,
             unverified)" → attribution UNVERIFIED, so copy hedges or omits
republish  — regenerated copy, corrections ledger carries who and when
```

**Every correction of this kind is also a labelled row.** Which field was
wrong, what the system had asserted, what it should have said. That is the most
valuable training data in the entire business and it currently arrives as an
Instagram message and disappears. B8.4 makes it a file.

---

## 6. Tasks

### B3.5 — `watch-claims.ps1` (deterministic, no model, build with the watchers)

The single highest-value script in this system for the business. It cannot be
skipped because a seat failed, because it does not use a seat.

**What it does.** Read generated title and description. Scan for Tier A claim
vocabulary. For each hit, look up the backing genome field and its
`assertable()` mode:

| Mode | Required in the copy | Otherwise |
|---|---|---|
| ASSERT | the term may appear plainly | — |
| HEDGE | the term may appear **only** inside hedging language — "attributed to", "appears to be", "described as" | exit non-zero, block |
| OMIT | the term must not appear at all | exit non-zero, block |

**The claim vocabulary**, script-loaded from `local/reference/claim-terms.txt`,
starting with:

- *Materials* — meerschaum, briar, morta, ivory, bone, amber, horn,
  tortoiseshell, bakelite, vulcanite, ebonite, cherrywood, olivewood, silver,
  sterling, 9k, 14k, gold
- *Era* — antique, vintage, pre-war, wartime, Victorian, Edwardian, and every
  decade form (1920s, '30s, …)
- *Maker* — every name in the brand dictionary

**Gate G3.5.** Plant five listings whose copy claims a material the genome does
not support — one of them the Jima title verbatim — and run against twenty
listings whose claims are all backed. It must block all five and pass all twenty.
Zero false blocks: a watcher that cries wolf gets switched off by the person it
protects.

**This one runs on every listing before publication, forever.** It is not scored
and not promoted; it is infrastructure, like a smoke alarm.

### B8 — The intake rework

Runs on the CODE-and-Farid track. It may proceed during B5's fourteen-day soak,
because it touches the marketing pipeline and not the local agents.

**B8.1** Route `unique_physical.materials` through `assertable()` in
`marketing/expression/copy.py`, in both `generate_title` and
`generate_description`, exactly as `brand` already is. Add a test that a listing
with an unverified material never emits the material word — the Jima case as a
named test.

**B8.2** Make `unknown` a first-class state in `marketing/intake/structure.py`:
any field the transcript and photos do not support is written as `unknown`, and
the structurer's prompt forbids inference. Assertions that arrive with no
evidence are the defect being fixed; a blank is not.

**B8.3** Split the output. The **listing** carries what is known, short. The
**encyclopedia page** is a separate document, written only where there is
sourced material, and each of its claims carries its source
(`marketing/encyclopedia/flywheel.py` already turns a sold event into a permanent
page — this gives it something true to say). No 4,000-character minimum
anywhere in the system.

**B8.4** `scripts/record-correction.ps1` — one command that turns an external
correction into a corrections-ledger row plus a labelled training row in
`local/data/labeled/corrections.jsonl`: the claim asserted, the claim corrected,
the field, the source, the date. Run it on the Jima item first, as row one.

**Gate G8.** Take ten of your worst existing listings — the ones with
unsupported claims — run them through the new path, and count. Every unsupported
Tier A claim removed or hedged, zero facts lost that were actually evidenced,
and the whole run under four minutes per pipe of Farid's time.

---

## 7. What this buys

The fifty-pipe week does not come from writing faster. It comes from three
things: **unknown becoming a legal answer**, so no item stalls waiting for
research; **the claim check being a script**, so nothing needs re-reading by
eye; and **the encyclopedia being optional**, so no item waits on 4,000
characters nobody asked for.

And the collector who took the trouble to write gets a system that records what
he said. That is worth more than the sale.
