# One paste for the Builder — install the writing fix and the memory fix

Farid copies the block below into the local session. Nothing else. The Builder does the rest
on the PC, where he can see the files and merge safely.

---

Install job. Do it now, then report in seven short lines.

Everything you need is on the branch `claude/builder-project-restart-so9z19` of
`Faridunhill/Claude-Project`. Pull it first. The files are already at their final paths, so
you do not need to create any content — only put it in place and switch it on.

1. Pull that branch. Confirm these four files exist:
   - `.claude/output-styles/farid-plain.md`
   - `.claude/hooks/capture-decision.sh`
   - `.claude/rules/laws.md`
   - `.claude/settings.json.example`

2. Make the hook runnable: `chmod +x .claude/hooks/capture-decision.sh`

3. Settings. If `.claude/settings.json` does NOT exist, copy the example file to that name.
   If it DOES exist, **merge** the `outputStyle`, `permissions.allow` and `hooks` blocks into
   it by hand. Do not overwrite a settings file that already has things in it. Show me the
   final file.

4. Turn on the writing style: run `/output-style` and select **Farid Plain**. Confirm it
   saved.

5. Make sure the laws load. `.claude/rules/laws.md` should load by itself. Check with
   `/memory` that it is listed. If it is not, add the line `@.claude/rules/laws.md` to the
   project `CLAUDE.md`.

6. Create `DECISIONS.md` at the project root if it is missing. One heading line only:
   `# DECISIONS — one line each. Date | what Farid decided | what it changes`
   Then add the line `@DECISIONS.md` to the project `CLAUDE.md` so it loads every session.

7. Test the decision hook. The public docs do not name the field that carries Farid's message
   text into a `UserPromptSubmit` hook. My script tries three names — `.prompt`,
   `.user_prompt`, `.message` — and falls back to reminding on every turn if none match.
   **Find out which one is real.** Run a session, send yourself a message containing the word
   "approved", and capture the hook's raw input. Tell me the correct field name. If it is not
   one of the three, fix that one line in the script and push the fix.

Report format, seven lines, one per step. Say DONE or say what failed. No explanation unless
something failed.

---
