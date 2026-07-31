# FaridOS Laws — canonical register

Laws are ratified by Farid and binding on every machine and every agent.
They are not preferences, and no automation may work around one.

This file is the register. Where a law is enforced in code, the code
cites the law number — search the number to find its enforcement points.

---

## LAW 11 — THE DESK DRIVE IS THE SYSTEM OF RECORD

**All information is accessed from the desk drive on the master system,
even when a copy exists in GitHub.**

Ratified by Farid, 2026-07-29.

### What it means

1. **The desk drive is the authority.** GitHub holds mirrors. A mirror is
   never the original, however recent it looks.
2. **When the two disagree, the desk drive is right** and the GitHub copy
   is stale. There is no case where a mirror overrules the master.
3. **Corrections are made on the desk drive first,** then mirrored
   outward. Never the reverse.
4. **An agent that can only reach GitHub is working from a mirror** and
   must say so plainly. It may not present a mirrored figure, count or
   record as current fact.
5. **The existence of a GitHub copy is never evidence that information is
   current.** Age is a property of the master, not of the copy.

### Why

Mirrors drift silently. Nothing about a stale copy announces that it is
stale, so an agent reading one answers confidently and wrongly — and a
confident wrong answer is worse than an absent one. This law removes the
ambiguity by naming a single authority in advance.

### What it does NOT say

This law does **not** forbid copying information to GitHub. Mirroring is
encouraged: a corpus that exists on exactly one drive is one hardware
failure away from gone. LAW 11 governs *authority*, not *location* — back
everything up, and still read from the master.

### Known consequence — the cabinets

The FaridOS dating cabinets (the test-suite-green engine on the master
system) are the source of truth for every dating fact published in the
encyclopedia. Entries derived from them may be mirrored to GitHub; the
cabinet remains the authority. `faridunhill-live/lib/encyclopedia.ts`
already states the narrower form of this rule: *"Do not add facts that
are not in a cabinet."*

---

## Register of existing laws

| Law | Statement | Where enforced |
|---|---|---|
| **LAW 06** | ⚠️ **Collision — see below** | — |
| **LAW 09** | All generated output is ASCII-safe | `marketing/expression/copy.py` |
| **LAW 10** | Product rows are never hard-deleted; soft archive only | `faridunhill-live` |
| **LAW 11** | The desk drive is the system of record | this file |

### ⚠️ LAW 06 is used twice, for two different laws

| Repo | What LAW 06 says there |
|---|---|
| `Claude-Project` | Businesses are firewalled — no data, accounts or credentials cross between them |
| `faridunhill-live` | Stripe stays empty until Farid says otherwise |

Both are real, ratified rules; they simply collide on the number. **This
needs Farid to renumber one of them** — until then, always name the repo
when citing LAW 06. Unresolved as of 2026-07-29.

## Named rules (not numbered laws)

| Rule | Statement |
|---|---|
| `POLICY-META-ADS-001` | No paid Meta promotion — prohibited for smoking paraphernalia |
| `SOCIAL-ENGINE-001` | Tiered publishing; one post per group per day |
| `CHANNEL-MAP-001` | Every video logs its music licence source; no manifest, no post |
| `PERFECTION-001` | The intro overlay must never block a mid-page refresh |
