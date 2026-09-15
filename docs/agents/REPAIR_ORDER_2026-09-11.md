# REPAIR ORDER — paste this whole block into the local Claude Code session

*Farid pastes once. The agent does the rest and reports back in one short message.*

---

Before any other work, repair your own setup and report. Do these seven steps in order and
answer in one short message, one line per step. Do not explain, just report.

1. Run `/status`. Tell me the exact model name you are running, and whether a fallback model
   is configured.
2. Run `/context`. Tell me whether `WebSearch` and `WebFetch` are in your loaded tools. If
   they are not, open `.claude/settings.json` and look for a `permissions.deny` entry
   blocking them. Report what you find.
3. Run `/memory`. List every instruction file that is actually loaded in this session, with
   its full path.
4. Open the project `CLAUDE.md`. Tell me whether it contains Farid's standing laws. Answer
   yes or no and give the number of laws you find.
5. Fix the loading problem. Take the file `docs/agents/LAWS.md` from the Claude-Project repo
   branch `claude/builder-project-restart-so9z19` (or the copy Farid gives you). Put its
   content where it will load every session: either merge it into the project `CLAUDE.md`,
   or save it as `.claude/rules/laws.md`, or add the single line `@docs/agents/LAWS.md`
   inside `CLAUDE.md`. Then start a fresh session and confirm with `/memory` that it loads.
6. Search your own files for standing laws that exist only in `SYSTEM_LEDGER.md` or in other
   documents that are never loaded. List them. Those are the laws you have been forgetting
   through no fault of your own. Move them into the loaded file.
7. Confirm in one line: model, search on or off, laws loaded yes or no, and how many laws
   you moved in step 6.

Then stop and wait. Do not start any project work. Farid will send one task next.

---

## If step 1 shows a small model
Run `/model` and choose the strongest model the account allows, or start the session with
`claude --model opus`. A small model is the single most likely cause of weak answers.

## If step 2 shows no WebSearch
Add it to the allow list in `.claude/settings.json`, or start with
`claude --allowedTools WebSearch`. Without search, Law 7 cannot be obeyed at all.

## Optional belt and braces
A SessionStart hook can print the laws into every new session. In `.claude/settings.json`:
`{"hooks":{"SessionStart":[{"matcher":"startup","hooks":[{"type":"command","command":"cat ${CLAUDE_PROJECT_DIR}/.claude/rules/laws.md"}]}]}}`
Test it once end to end before relying on it.
