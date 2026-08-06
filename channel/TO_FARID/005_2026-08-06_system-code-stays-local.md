# 005 — STANDING RULE: Farid's system code never lives in this repo

**Farid, 2026-08-06:** *"everything i build will be local in my pc, nothing in repos."*
He confirmed it applies to THE DESK. This note exists so no future session re-commits it.

## The rule

This repo is **the public front** — the website, the encyclopedia entries, the Professor docs,
and this channel. Confirmed public on GitHub (`visibility: public`).

His **system** — THE DESK, THE HELPER, THE HUNTER, the Chronos-Pipe control panel, the dating
engine, the cabinets, the ARK — lives on his PC only. Design notes and questions come through
`channel/`. Code does not.

## What was done

`manager/` (THE DESK, 21 files) was removed from this repo and delivered to Farid directly as
a zip. It survives on his machine, not here.

**Checked before removal — nothing sensitive was ever exposed.** No API keys, no passwords, no
tokens. `.gitignore` had already kept `config.json` and `state/` out. What was public was the
architecture and two folder paths on his desktop. Not a leak, but it was still his to decide,
and he decided.

**One honest caveat:** deleting the files removes them from the current tree, not from git
history — anyone reading old commits can still see them. Scrubbing history means force-rewriting
this branch. That is a bigger, riskier operation and Farid's call, not mine. **He has not asked
for it. Do not do it unless he does.** Offered to him 2026-08-06; no answer yet.

## What THE DESK contained (so it isn't lost from memory here)

The laws file and its hash-lock, the honesty law-guard, the approval gate, the PowerShell
command registry, the SQLite job queue, the idea ledger, the Academy (evidence-backed memory),
the channel reader/writer, and 26 passing tests. All of it is in the zip he now holds. The
design that supersedes it is in `003` — the list replaces the approval tokens, and the
once-a-day command becomes a service that never sleeps.

— your agent
