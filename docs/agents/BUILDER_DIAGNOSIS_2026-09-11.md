# Is the local Builder broken? — diagnosis before replacement (2026-09-11)

> Farid, 2026-09-11: the local agent is active, polite, never says no; writes a law, saves
> it, then forgets it; his language is hard to read; his technical level is now in doubt.
> "Either fix this guy or find alternative. I have an agent under training called Hamada —
> can he replace Builder?"

## 0. The honest opening — the evidence cuts both ways
The one long technical reply I have actually seen from the local side (channel 005's
source, 2026-09-11) was **strong**: it carried facts I did not have (FACES_0902 and its
SHA manifest, folder 5 = the grandson, the six retired portraits, VOICE_1's id, the Aug-31
PVC deadlock, the real paid-tools list), it **caught a real mistake of mine** (my plan
opened Farid's face law without naming it), and it proposed Decision Zero with three roads
and a cost cap. That is not the work of an uneducated agent. It is better than most
reviews I receive.

So the complaint and the evidence disagree — which usually means the problem is **not
capability, it is consistency**. Inconsistency has specific, checkable causes. All four
below are settings, not character, and **none of them is fixed by hiring a different
agent.**

## 1. The four suspects (in order of likelihood)

**S1 — The local session is running a smaller model than the cloud one.**
Claude Code lets each install pick its model, and a session can also fall back to a smaller
model when the big one is busy. If the PC has been answering on a small model while this
cloud session runs the flagship, the gap Farid describes ("MS degree vs uneducated") is
exactly what that looks like, and it is a one-command fix.
*Test:* run `/model` and `/status` in the local session; read what it reports.

**S2 — The local agent cannot search the web.**
"Very polite, never says no, answers from memory" is the exact signature of an agent
without search. Law 7 is unenforceable if the tool is missing: the agent cannot verify, so
it agrees. The cloud side searched 30+ times for the Professor answer Farid compared.
*Test:* ask it "what is today's price of ElevenLabs Creator? give me the URL and the date
on the page." If it answers without a link, it has no search or is not using it.

**S3 — The laws are written where nothing loads them.** ★ most likely cause of "forgets"
Claude Code loads instruction files automatically at session start. A law written into
`SYSTEM_LEDGER.md`, `docs/RULES.md`, or a chat message is **not** loaded next session — the
agent is not disobeying, it never saw it. This exactly produces "he writes it, saves it,
then forgets it, never follows it."
*Test:* open the local `CLAUDE.md`. If the laws are not in it, the mystery is solved.

**S4 — A long session forgot mid-way (context compaction).**
Confirmed by the docs: when the context fills, Claude Code clears old tool output and
summarises the conversation. **Conversation-only instructions are not preserved**; the
project `CLAUDE.md` is re-read from disk and survives. `/context` shows the usage,
`/compact` forces it early. So a law given by voice in a long session is gone by evening —
another reason laws belong in the file, not in the chat.

## 1b. ★ S3 CONFIRMED — verified against the Claude Code documentation (2026-09-11)
Claude Code auto-loads **only** these at session start:
1. the organisation's managed policy file, 2. `~/.claude/CLAUDE.md`, 3. the project's
`./CLAUDE.md` (or `./.claude/CLAUDE.md`), 4. `./CLAUDE.local.md`, 5. `.claude/rules/*.md`,
6. anything pulled in by an `@path/to/file` import inside one of those.
**Every other markdown file — `SYSTEM_LEDGER.md`, `docs/RULES.md`, a law typed into chat —
is NOT loaded.** And on compaction, "conversation-only instructions are NOT preserved",
while the project `CLAUDE.md` is re-read from disk and re-injected.

So: a law the local Builder wrote into the ledger is invisible to the next session, and a
law given only in chat evaporates when a long session compacts. **He is not ignoring the
laws. He never sees them.** This alone explains "he writes it, saves it, then forgets it".

## 2. The fix list (do these before deciding anything)
1. **Model** — in the local session type `/status` (shows the model) and `/model` to change
   it, or start with `claude --model opus`. Also check the `fallbackModel` setting: when the
   big model is busy the session drops to a smaller one **for that turn** and says so — if
   Farid saw a notice like that, that turn's bad answer is explained.
2. **Search** — type `/context` to see which tools are loaded. If `WebSearch` is missing,
   look in `.claude/settings.json` for a `permissions.deny` entry blocking it, and allow it
   (`"permissions": {"allow": ["WebSearch"]}`), or start with
   `claude --allowedTools WebSearch`. **Without this tool Law 7 is impossible** and the
   agent can only agree politely.
3. **Laws into a file that is actually loaded** (see §1b) — every standing law goes into the
   local project `CLAUDE.md`, or into `.claude/rules/*.md`, or is pulled into `CLAUDE.md`
   with an `@` import line such as `@docs/LAWS.md`. The ledger records *what happened*;
   `CLAUDE.md` governs *what the agent does*. `/memory` lists which files are loaded and
   opens them.
3b. **Belt and braces** — a `SessionStart` hook in `.claude/settings.json` can print a rules
   file into every new session:
   `{"hooks":{"SessionStart":[{"matcher":"startup","hooks":[{"type":"command","command":"cat ${CLAUDE_PROJECT_DIR}/.claude/rules-inject.md"}]}]}}`
   (The docs do not guarantee how that text is merged, so test it once end to end.)
4. **One language rule, written down:** *"Farid's first language is not English. Short
   sentences. One idea per sentence. No word he would have to look up. If a sentence needs
   explaining, it was the wrong sentence."*
5. **One honesty rule, written down:** *"Never say yes to be agreeable. When you disagree,
   say so in one sentence and give the reason. When you do not know, say UNVERIFIED."*
6. **Re-test after the fixes**, with §3.

## 3. The same exam (the fair way to decide)
Give **both** agents the identical task, the identical files, and the identical time. Score
on the six criteria already published (channel/TO_FARID, the comparison rules):
truth with sources · diagnosis before prescription · completeness of the ask · registered
work (files, not chat) · honesty about limits · how few decisions it asks of Farid.

Suggested exam, because it has a checkable answer and needs real work:
> "Hunt fresh dating evidence for Charatan or James Upshall today. Give me every claim with
> its source and the date on the page, mark anything you cannot verify UNVERIFIED, and save
> the result as a file in the repo. Tell me what you did not check."

Rules: same prompt, same access, no hints, no second chances. Then read both.

## 4. Can Hamada replace the Builder?
**Not yet, and probably not for this reason.** Three facts:
1. **A new agent inherits the same environment.** If S1–S4 are the cause, Hamada on the
   same PC, same model, same missing search, same unloaded laws will behave the same way
   within a week. Replacing the driver does not fix the car.
2. **What the Builder holds is on disk, not in its head.** The cabinets, FACES_0902, the
   ledger, the paths, the retired folder, two months of decisions — all files. So the
   handover risk is **low**, and that cuts both ways: there is no emergency, and no reason
   to rush the decision.
3. **The real question is not who, it is what they are made of.** An assistant under
   training and a data-keeper are different jobs. Hamada can be given the assistant work
   today (drafting, sorting, chasing links) and grow into the keeper seat by passing the
   same exam, twice, a week apart.

**Recommendation:** run §2 then §3. If the local Builder passes the exam after the fixes,
keep it — it already proved it can outthink the cloud on its own ground. If it fails the
exam *with* a flagship model, search on, and the laws loaded, then it is not the settings
and Hamada gets a real trial on the same exam.

## 5. What the cloud side will do either way
The council (`docs/council/`) is the permanent answer to "is this agent's work good?" —
seven seats, six companies, the QC seat sees and hears the real file. **An agent's output
is judged by the council, not by whoever wrote it.** That protects the encyclopedia from
any single agent's bad week, mine included.
