# 002 — Prime Agent (Prime Intellect): evaluation

You asked me to check `github.com/PrimeIntellect-ai/prime-agent` and say whether it works with our
system. Short answer: **it fits the LOCAL front well, it does nothing for this repo, and there is one
hard blocker (Windows) plus one law-level risk (self-rewriting instructions).**

I have **not run it.** This is a read of the repo, the README and the launch coverage — nothing more.

## What it is

An open-source agent harness released by Prime Intellect (MIT licence, ~3.3k stars, brand new —
announced this week). It is a command-line agent like the one you already use, not a website and not
a model. Two ideas carry it:

- **RLM (context as a variable).** Its *only* tool is a live Python (IPython) session. Instead of
  calling tools one at a time, the model writes Python — so it can loop over 19,000 files, hold the
  cabinets as variables, and spawn sub-agents as ordinary function calls.
- **Continual Harness.** Memory, skills and sub-agent specs survive between sessions as durable
  state; `/refine` writes evidence-backed updates into it. This is the "blank session" problem our
  `CLAUDE.md` was written to patch — solved at the tool level.

Also: background daemon sessions you can detach from and reattach to, autonomous mode with turn/token/
time budgets, and agents that message each other directly.

**Cost: no new bill.** It logs in with a Claude Pro/Max subscription (also Codex, Copilot, or plain
API keys, Bedrock, or self-hosted Ollama/vLLM). Your existing subscription drives it.

## Fit with our two fronts

**LOCAL (FaridOS — the dating engine, cabinets, the ARK): strong fit.** Everything there is already
Python. An agent whose native language *is* Python can load 55+ brand cabinets as variables, run the
test suite in the same kernel, and sweep the 19k-file ark manifest in one pass instead of tool-call by
tool-call. The interview harvest is the clearest win: background + autonomous budgets means the daily
Charatan/Upshall and CEO-interview URL hunt could run unattended and hand you a list. (Whisper
transcription still waits for your GPU all-clear — that doesn't change.)

**CLOUD (this repo): no fit, no action.** This front is Next.js on Vercel edited by a web session.
Prime Agent is a local terminal program; it cannot run here and would not touch the website. Nothing
to install, nothing to change in this repo. The `channel/` bridge is just files, so it keeps working
either way.

## The three things that must be answered before you install it

1. **Windows blocker.** The installer is macOS/Linux only (`curl … | sh`). Your notes are in
   PowerShell, so your PC is Windows — it will not install natively. It would have to run inside
   **WSL** (the Linux layer for Windows). That is a real setup step, not a download.
2. **It is not a sandbox — their words.** It "executes model-generated Python and project commands
   with your user permissions." On the machine that holds the ARK and the purchased scans, that is
   the whole library within reach of a bad line of code. Rule if we trial it: a **verified backup
   first**, and point it at a *copy* of one cabinet, never the master.
3. **Self-rewriting harness vs. our first law.** `/refine` lets the agent edit its own standing
   instructions. Our laws — wide brackets, both sources on disputes, absence never dates — are
   exactly the kind of constraint a self-optimising agent could soften to "move faster." Their base
   prompt is immutable but the supplemental layer is not. If we adopt it, the honesty laws go in the
   **immutable** layer, and drift gets checked, not trusted.

Add to that: it is days old, with ~48 open issues. Early software.

## My recommendation

**Don't adopt it — trial it, local only, on one bounded job.** The job I'd pick: the interview
harvest URL sweep. It is read-only, it is a chore that eats your working day, it needs no cabinet
writes, and if the tool is bad we lose an afternoon and nothing else. If it delivers a clean list,
we talk about letting it near the cabinets. Not before.

Nothing to decide about this repo. This is a local-PC question only.

Source: https://github.com/PrimeIntellect-ai/prime-agent

— your agent
