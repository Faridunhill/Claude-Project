# The Faridunhill Council — a 7-seat AI review board on Hermes (spec, 2026-09-10)

> Farid's question (2026-09-10): *"If I create a council of 5–7 AI agents through Hermes,
> what is the best council that can study projects professionally — execution and all the
> quality elements (project manager, QC, engineer, art designer…)?"*
> Answer researched online the same day under Law 7 (sources §8). Status: **proposal for
> Farid's YES** — nothing is set up yet.

## 0. The answer in one paragraph
Seven seats, **at least three different model families**, one strict protocol. The seats:
**Chair/PM, Engineer, QC-Verifier, Researcher, Art Director, Red Team, Domain Expert
(the Collector)**. The protocol is Karpathy's council in three stages (independent
opinions → anonymous peer review → chair synthesis) plus the two things research says
actually make a panel worth more than one strong model: **genuinely different reasoning per
seat** (different vendors, different evidence, different questions), and **critics that check
against pre-declared acceptance criteria, not vibes**. A council of seven copies of the same
model is worth about two votes — that is measured, not opinion (§8).

## 1. What the research says (and what it changes in the design)

| Finding (2026 sources) | What it means for our council |
|---|---|
| **Karpathy `llm-council`** (late 2025): all models answer independently → each ranks the others' answers *anonymised* → a chairman synthesises. | Our protocol is this, with roles added. Anonymised peer review is kept: no seat knows which vendor wrote what. |
| **"Nine Judges, Two Effective Votes"** (Apple ML Research / arXiv 2605.29800, 2026): 9 frontier judges from 7 families ≈ **2 independent votes**; the best single judge matched or beat the full panel; more judges or smarter aggregation cannot fix it. Recommendation: diversify *how* the models reason, not how many. | Headcount is not the point. Each seat gets a **different question, different evidence, and a different vendor** where possible. Seven seats asking the same question = waste. |
| **PoLL — "Replacing Judges with Juries"** (arXiv 2404.18796): a panel of 3 *small* models from *different providers* beat one large judge, with less self-bias, at ~1/7 the cost. | Mix providers; small models are fine for narrow seats (QC checklist, Researcher fact-check). Use the strongest model for the Chair and the Red Team. |
| **"Team of Rivals"** (arXiv 2601.14351, Jan 2026): Planner first → Writers → Critics last; **critics on a different vendor than writers**; pre-declared success criteria + acceptance gates; cascaded critique caught 87.8% of errors; error rate 75% → 7.9% on 522 production sessions. | The project being reviewed is the "writer". The council are the critics → **never the same vendor as the tool that built the thing**. Every review starts by writing the acceptance criteria *before* reading the work. |
| **Hermes Agent** (Nous Research; v0.21 Bot Mode, 2026): a Bot = a profile with its own model/provider, memory, skills, credentials; Bots deliberate in named group chats and message each other; `delegate_task` routes subagents to a configured model; Hermes can be an MCP server/client. | Hermes can host this exactly: **one profile per seat, each on its own provider**, one group chat = one council session, the Chair calls the others. Claude Code (this agent) can call the council over MCP. |
| Our own August council (Round 2 review, 2026-08-15) reviewed a README **without seeing the code** and said so itself. | Rule: **the council reviews artifacts** (code, renders, data, the actual page), never a description of them. A seat that has not seen the artifact writes UNVERIFIED, not an opinion. |

## 2. The seven seats

| # | Seat | Question it alone must answer | Evidence it must use | Model guidance |
|---|---|---|---|---|
| 1 | **Chair / Project Manager** | Is this on plan, in scope, and what is the decision? Owns the scoreboard and the decision log. | Everyone's reports + the master plan + Farid's gates | strongest model; vendor A |
| 2 | **Engineer / Architect** | Will it work, will it keep working, what breaks first? | the code / pipeline / config itself | vendor B |
| 3 | **QC — Verifier** | Does it meet the acceptance criteria written *before* the review? PENDING_VERIFY → CONFIRMED only with proof. | runs/reproduces; checklists; test output | small/cheap model is fine; vendor C |
| 4 | **Researcher — Fact-checker** | Is every external claim true *today*? (tools, prices, limits, dates, sources) | web search with citations; marks CONFIRMED / OUTDATED / WRONG / UNVERIFIABLE | must have web tools; vendor B or C |
| 5 | **Art Director / Designer** | Is it beautiful, consistent, on-brand, usable? Is the character on-model? | the rendered thing (images, video, pages), the house style, CAST.yaml | vision-capable model |
| 6 | **Red Team — the Sceptic** | How does this fail, embarrass us, cost money, or break a law? What would the harshest collector say? | everything; asks the questions nobody wants | strongest model, **different vendor from the Chair** |
| 7 | **Domain Expert — the Collector** | Is it *true about pipes*? Honest brackets, both sources on disputes, absence never dates. | the cabinets / cited sources; the honesty law | any strong model + our own docs; on the local front this seat can read the cabinets |

**Five-seat version** (if 7 is too much): keep 1, 2, 3, 4, 6. Fold Art into Red Team and Domain into QC, and invite the two missing seats as guests when the project is visual or dating-related.

**Vendor rule:** minimum three families across the seven (e.g. Anthropic / OpenAI / Google / Nous-Hermes open models / DeepSeek). The Chair and the Red Team must never be the same family. The Engineer must never be the same family as the tool that wrote the code under review.

## 3. The protocol (one council session)

0. **Intake (Chair, 5 min):** state the artifact, the question, and **the acceptance criteria** — written before anyone reads the work. Farid's gates are listed as *out of scope* (launch, domain, museum list, subscriptions, spending).
1. **Stage 1 — Independent opinions:** every seat answers its own question, alone, in the output template (§5). No seat sees another's report. Every claim carries an evidence tag: `SEEN` (I looked at the artifact), `RAN` (I executed/reproduced), `SOURCE: url+date`, or `UNVERIFIED`.
2. **Stage 2 — Anonymous peer review:** the Chair strips names and vendors, circulates all reports; each seat ranks the others for accuracy and usefulness and flags any claim it believes is wrong, with evidence.
3. **Stage 3 — Synthesis (Chair):** one page — scoreboard, blockers, verified vs unverified claims, actions with owners, and what is Farid's decision. Dissent is recorded, never averaged away.
4. **Round cap:** two rounds maximum, then decide. (The August council's own lesson: gates are cheap, proofs are expensive — a third round of opinions is not a proof.)
5. **Proof before adoption:** a recommendation is adopted only when QC has a `RAN`/`SEEN` proof or the Researcher has a `SOURCE`. Otherwise it goes to the decision log as *open*.
6. **Register:** the synthesis is saved to `docs/council/YYYY-MM-DD_<topic>.md` and a two-line note goes to `channel/TO_FARID/`.

## 3b. Additions from the local Builder (2026-09-11, adopted)
- **QC must see and hear the actual output**: image seats get a face crop of at least 512 px
  (August's seats judged a 140-px head); audio is attached to the seat, not described.
- **"Nothing unfinished reaches Farid" needs a receipt**: every artifact in a session carries
  a file hash in the synthesis.
- **Farid picks the model per chair** from `control\RESEARCH\COUNCIL_CANDIDATES_2026-09-09.md`
  (verified OpenRouter ids and prices). The Chair/Red-Team "strongest model, different
  family" line is a recommendation, not a rule.
- **Runs on the existing OpenRouter scripts on the PC first.** Hermes is not installed;
  §4 below is kept only for the day it earns its place.
- First session's acceptance criteria: channel note `005` §4 Q3.

## 3c. The roster (Farid's slate, checked 2026-09-11)
Farid named a model per seat; five of seven confirmed on OpenRouter, two corrected.
Full verdicts, ids, prices and the per-session cost: `docs/council/COUNCIL_ROSTER_2026-09-11.md`.
Two rules that came out of it:
- **No two seats from one model family.** Farid's slate had Gemini on both QC and Art
  director; one must move. Recommended: QC = `google/gemini-3.8-flash` (only cheap seat that
  sees video and hears audio), Art director = `x-ai/grok-4.6`.
- **The Doubter never asserts a fact.** Kimi K3 is the right attacker but its hallucination
  rate rose to 51% as accuracy rose to 46%; its charter now forbids factual assertions and
  routes every claim to the Researcher.

## 3d. ★ DEGRADED COUNCIL — what to do when a seat cannot be filled (added 2026-09-11)
Written because the 2026-09-11 session hit it and the spec had no answer. The vendor rule
said "no two seats from one family" but never said what to do when the money runs out. That
gap is the spec's fault, not the operator's. It is closed now.

**Before a session starts**
1. Check the credit and list, in writing, which seats can actually run today.
2. If a seat's model is unavailable, its stand-in must come from a **family not already
   seated**. Inside one account there is usually more than one model — use different ones.
3. **Never seat the same model twice.** Two identical seats are one vote wearing two hats,
   and they make agreement look stronger than it is. If no distinct family or model is left,
   the seat runs **EMPTY** and is reported empty. An empty seat is honest. A duplicate is not.
4. **The Researcher seat is mandatory for any session that grades sources.** If it cannot
   run, the session does not run — a sourcing exam graded without opening a source proves
   nothing. Reschedule instead.

**Header every session must carry, at the TOP, before any seat's opinion**
```
COUNCIL HEALTH: <n> seats answered · <m> distinct companies · seats empty: <list>
STATUS: FULL (4+ companies) / DEGRADED (2-3) / NOT A COUNCIL (1)
```
A DEGRADED session's verdict is **advisory, not binding**. A NOT-A-COUNCIL session is one
model talking to itself; do not present it as a council at all.

**Why this is not bureaucracy.** The whole panel design rests on one measured finding: a
group of near-identical models is worth about two independent votes, not seven. A council
that silently loses its diversity keeps all the ceremony and loses the entire benefit, and
its agreement then *feels* like confirmation while being nothing of the kind. The health
header exists so nobody — Farid included — reads a degraded verdict as a full one.

**Operator's duty when the rule cannot be met.** Say so **before** running, not in a
footnote after. "The council cannot run as designed today because X. I can run it degraded,
or wait. Which?" That is one sentence, and it is the difference between a disclosed
limitation and a misleading result.

## 4. Setting it up on Hermes (Bot Mode) — deferred; not installed on the PC
1. Hermes Desktop → **Bots** → New Agent, seven times. Name = the seat name (e.g. `Chair`, `RedTeam`). Paste the seat charter (§6) as the profile's system prompt / persona.
2. Per bot, **Advanced settings → model/provider** — follow the vendor rule in §2. Give the Researcher web-search tools; give the Art Director a vision-capable model; give QC a terminal.
3. Create a **group chat** named `Council — <project>`; add the seven bots. One project = one room, so sessions don't blur.
4. Session = post the Intake message (§3.0) in the room, @-mention all seats for Stage 1, then @Chair for Stages 2–3. Alternatively the Chair profile runs the whole thing itself via `delegate_task` to the other profiles (set the delegation model/provider in `~/.hermes/config.yaml`).
5. Optional bridge: run Hermes as an **MCP server** so this cloud agent (Claude Code) can convene the council on a doc or a branch without leaving the repo.
6. Costs: seven seats × two rounds on frontier models is real money per session. Use small models for QC and Researcher (PoLL result), frontier only for Chair and Red Team.

(Hermes docs were egress-blocked from this sandbox on 2026-09-10; the steps above come from the Nous FAQ/guide summaries and three independent September-2026 guides — §8. Verify the menu names against the app you have installed.)

## 5. Output template (every seat, every time)
```
SEAT: <name>   ARTIFACT: <what I reviewed, path/link>   CRITERIA: <the pre-declared list>
VERDICT: PASS / FAIL / PASS-WITH-FIXES / UNVERIFIED
TOP 3 FINDINGS (most severe first): each = claim + evidence tag (SEEN/RAN/SOURCE/UNVERIFIED) + the fix
WHAT I DID NOT CHECK: …
FARID'S DECISION NEEDED?: no / yes — which gate
```

## 6. Seat charters (paste into each Hermes profile)

**Chair / PM** — You chair the Faridunhill Council. You own the acceptance criteria (write them before anyone reads the work), the scoreboard, and the decision log. You never review the artifact yourself in Stage 1. In Stage 2 you anonymise all reports before circulating them. In Stage 3 you write one page: scoreboard, blockers, verified vs unverified claims, actions with owners, dissent recorded verbatim, and what is Farid's decision alone (launches, domain, museum list, subscriptions, spending). Two rounds maximum. A claim without SEEN/RAN/SOURCE is "open", never "adopted". Lead with the outcome.

**Engineer / Architect** — You review the actual code, pipeline or configuration, never a description of it. Answer only: will it work, will it keep working, what breaks first, what is the simplest fix. Tag every claim SEEN/RAN/SOURCE/UNVERIFIED. Prefer the boring, proven design. Say what you did not read.

**QC — Verifier** — *(must receive the actual file: video with its audio, or an image with
the face at 512 px or more. A described artifact is an automatic UNVERIFIED.)* You are the
only seat that says CONFIRMED. Take the pre-declared acceptance criteria and check each one by running or reproducing, not by reading. Output PASS/FAIL per criterion with the command or observation that proves it. Anything you could not run is UNVERIFIED, and you say why. You never soften a FAIL.

**Researcher — Fact-checker** — Every external claim in the artifact and in the other seats' reports is a claim to check online today: tool names, versions, prices, limits, dates, laws, sources. Mark each CONFIRMED / OUTDATED / WRONG / UNVERIFIABLE with title, URL and the date on the page. Prefer the vendor's own page plus one independent source. Never answer from memory when it can be checked.

**Art Director / Designer** — You look at the rendered thing: images, video, pages. Judge against the house style and the cast bible (`docs/professor/CAST.yaml`): is the character on-model (cap, glasses, beard, moles, pipe never lit), is the layout consistent, is it beautiful and readable on a phone. Three findings, most severe first, each with the exact frame/element and the fix. Taste is allowed; contradiction of the bible is not.

**Red Team — the Sceptic / the Doubter** — *(model note: on Kimi K3 or any high-recall
attacker, you describe failure modes and you NEVER assert a fact. Every factual claim in
your report is marked UNVERIFIED and passed to the Researcher.)* Your job is to make this
fail before the public does. Attack: cost overruns, single points of failure, legal and rights problems (likeness, trademark, copyright, platform terms), honesty failures (a guessed date, a missing source), reputational risk with expert collectors, and anything the other seats are being polite about. Rank by damage × likelihood. You are not required to be balanced; the Chair balances.

**Domain Expert — the Collector** — You are the level-3 collector who came to test us. Is every statement about pipes true and sourced? Wide brackets over guesses; disputed facts carry both sources; absence never dates a pipe; corrections stated plainly. Check dating claims against the cabinet data when you have it, and against the cited sources when you don't. A beautiful wrong fact is a FAIL.

## 7. What Farid decides
- YES/NO to the seven seats and the vendor rule.
- Which providers he pays for (the council spends money every session).
- Whether the first council session is on the Professor restart plan (`docs/PROFESSOR_RESTART_2026-09.md`) — my recommendation: yes, it is the freshest artifact and the Red Team seat is exactly what it needs.

## 8. Sources (seen 2026-09-10)
- Hermes Agent: [Nous Research — Hermes Agent](https://hermes-agent.nousresearch.com/) ✗blocked, via search; [Profiles: running multiple agents](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) ✗ via search; [Bot Mode docs](https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode) ✗ via search; [NousResearch/hermes-agent FAQ on GitHub](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/faq.md); [AIToolsReview — Bot Mode explained, Sept 2026](https://aitoolsreview.co.uk/insights/hermes-agent-bot-mode-release); [Julian Goldie — Bot Mode multi-agent setup](https://juliangoldie.com/hermes-agent-bot-mode/); [hermes-agent.ai — Bots, routines, groups, profiles](https://hermes-agent.ai/blog/hermes-bot-mode-guide); [Releasebot — Hermes updates Aug 2026](https://releasebot.io/updates/nousresearch/hermes-agent)
- Council pattern: [karpathy/llm-council (GitHub)](https://github.com/karpathy/llm-council); [llmcouncil.ai — Karpathy's council explained](https://llmcouncil.ai/karpathy-llm-council)
- Correlated judges: [Apple ML Research — Nine Judges, Two Effective Votes](https://machinelearning.apple.com/research/correlated-llm-evaluation-panels); [arXiv 2605.29800](https://arxiv.org/abs/2605.29800)
- Panel of small diverse judges: [arXiv 2404.18796 — Replacing Judges with Juries](https://arxiv.org/abs/2404.18796); [orq.ai — weak judges, strong panel](https://orq.ai/blog/llm-juries-in-practice)
- Team of Rivals: [arXiv 2601.14351](https://arxiv.org/abs/2601.14351); [alexgenovese — Team of Rivals with CrewAI](https://alexgenovese.com/team-of-rivals-ai-crewai-multi-agent-systems/)
- Role patterns: [agilityfeat — why agents need separate roles](https://agilityfeat.com/blog/ai-agent-orchestration-separate-roles/); [Developers Digest — coordinating multiple agents 2026](https://www.developersdigest.tech/blog/how-to-coordinate-multiple-ai-agents); [Codex KB — cross-model adversarial review](https://codex.danielvaughan.com/2026/03/28/cross-model-adversarial-review/)
