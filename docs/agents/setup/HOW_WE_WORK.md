# How the three of us work — Farid, the cloud, the Builder (2026-09-11)

Farid asked: can he work with the cloud on his projects, keep the Builder as his hands on the
PC, and have the repository copy itself to the PC automatically?

**Yes to all three. Two are already true. The third is a script, written today.**

## Who does what
| | Farid | Cloud (this session) | Builder (the PC) |
|---|---|---|---|
| Decides | everything that costs money, launches, the domain, the brand list, his face | nothing | nothing |
| Plans and researches | | ✅ the whole web, the plans, the laws, the exams, the council | |
| Touches the PC | | ❌ cannot, ever | ✅ only he can |
| Holds the master data | | ❌ mirrors only | ✅ cabinets, the ARK, the ledger, the photos |
| Writes to the repository | | ✅ | ✅ |

That split is not a limitation to fix. It is the safe shape. The cloud can never reach
Farid's machine, so the cloud can never break it. The Builder can never spend money without
Farid. And Farid never has to be the memory.

## The one missing piece — the automatic mirror
Until today the repository only reached the PC when someone remembered to pull it.
`scripts/mirror_pull.py` fixes that. It copies the branch down every 10 minutes.

**Install, one line, on the PC:**
```
python scripts\mirror_pull.py --install-task
```
That creates a Windows timer named `FaridunhillMirror`. Run the window as Administrator once.

**What it does every 10 minutes**
1. Checks the folder for unsaved work. If it finds any, it stops and writes why. It never
   pulls over work in progress.
2. Fetches the branch.
3. Moves forward only if the history is a straight line. If the two sides have split, it
   stops and asks for a person. It never merges by guesswork.
4. Writes one line to `mirror.log`, always, even when nothing changed.

**How Farid checks it:** open `mirror.log`. Every line has a date and a time. No line for an
hour means the timer stopped.

## What this does NOT give
The mirror moves files one way, from GitHub to the PC. It does not let the cloud see the PC.
Anything that lives only on the PC — the cabinets, the ARK, the sold prices, the photos —
stays invisible to the cloud until the Builder pushes it or writes about it.

**So the rule stays: when the cloud needs a fact from the PC, it asks in
`channel/TO_FARID/` and the Builder answers.** The mirror does not change that.

## The other direction, already working
The Builder pushes his work to the same branch. The cloud pulls it before writing. That
happened today: he pushed his Python hook while the cloud was writing, the cloud's push was
refused, the cloud pulled his work in and kept it. That is the system behaving correctly.

## One warning about two agents on one branch
Both sides now write to `claude/builder-project-restart-so9z19`. When both change the same
file in the same hour, git will stop and ask a person. That is a real risk, not a theory.
**Rule: the Builder owns everything under `.claude/hooks/`, `dating/`, and the cabinets.
The cloud owns `docs/`, `channel/TO_FARID/`, and the plans.** Either may read all of it.
Neither rewrites the other's files without saying so first.
