# Faridunhill — start here

**READ `docs/HANDOVER.md` FIRST.** It is the current state of this project and where the
last session stopped — two repos, the built marketing system, how to run it, the Academy
self-correction loop, what's next, and the open decisions. Do not change files until Farid
confirms the task.

Working branch: `claude/peterson-pipe-dating-system-6xcj9v`.

Key docs:
- `docs/HANDOVER.md` — start-of-chat brief (read this first)
- `docs/pipe-dating-directory-blueprint.md` — the Smoking Pipes Dating Directory brief
- `docs/MARKETING.md` — marketing strategy
- `docs/marketing-dna-council-response*.md` — the ratified marketing-system design
- `marketing/README.md` — how the built marketing system + CLI works

The marketing system runs locally against `C:\FaridunhillPipes`:
```
python -m marketing.auto "C:\FaridunhillPipes" --watch --year 2026
```
