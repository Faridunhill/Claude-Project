# Hooks — read this before adding one

## ★ SUPERSEDED: capture-decision.sh
**Do not use the .sh version.** The Builder replaced it with
`.claude/hooks/capture_decision.py` on 2026-09-11, and his version is the correct one.

Two reasons, both found on the PC, both my errors:
1. **`jq` is not installed on Farid's PC.** My script called it. A missing command fails,
   the script emits nothing, and it exits 0. The hook installs clean and does nothing.
   Silent. Nothing complains. That is the worst failure a hook can have.
2. **Farid's PC is Windows.** A `.sh` file needs a shell that may not be there. Python 3.11
   is already on the machine and needs nothing installed.

His version also dumps the raw hook input to `last_input.json` every time, so the open
question about the field name gets answered whether or not his guesses were right. That is
better engineering than mine.

## THE RULE THIS TAUGHT US — a hook must fail loud, never silent
My script was written to fail open: if it could not run, it stayed quiet and returned
success. That is backwards. Farid would have believed the memory fix was installed while
nothing ran.

**Every hook we write from now on must, when it cannot do its job, say so.** Write to a log
file, or emit a message, or exit non-zero. A hook that cannot work and says nothing is worse
than no hook, because it buys false confidence.

## SECOND ERROR — my install step was ambiguous about which settings file
I wrote "if `.claude/settings.json` does not exist, copy the example to that name." I meant
the project file. Farid's **home** file at `~/.claude/settings.json` already held a
`permissions.deny` block and `defaultMode`. Read one way, my step would have overwritten it.
The Builder merged by hand and kept a backup, which was the right call.

**Rule: never tell anyone to copy a file over a settings file. Say "merge, and back up
first," always, even when you think the target is empty.**

## Also: I used a JSON tool to print a fixed string
Both my commands called `jq` only to produce text that never changes. `printf` does that with
nothing installed. Adding a dependency for a constant is a mistake on any machine, and on
this one it was fatal.

## THIRD FIX, same day — I nearly made the rule fire twice
The Builder's `capture_decision.py` already adds the plain-language rule to every message.
I had written a second script, `plain_language.py`, doing the same thing, and listed both in
the settings example. Two hooks, one rule, injected twice per message.

Deleted. **One hook command only: `capture_decision.py`.** It carries both jobs.

Lesson for the next session: before adding a hook, read the hooks already installed.

## STILL OPEN — the field name (install step 7)
`last_input.json` currently holds `{"someOtherField":"hello just a question"}`. That is a
test string, not a real message from Farid. So the real field name is still unknown.
It gets answered on the next real session: the script saves whatever Claude Code sends.
Until then the script falls back to the longest string it can find, and reminds anyway when
it finds nothing. Nothing is lost while we wait.

## ★ STEP 7 ANSWERED — 2026-09-11, from a real message on Farid's PC

The field is **`prompt`**. Your first guess was right.

The full object the hook receives on stdin, captured live from Claude Code on Windows:

| field | what it holds |
|---|---|
| `prompt` | **Farid's message text.** This is the one. |
| `session_id` | the session's id |
| `session_title` | the title shown in the app |
| `transcript_path` | full path to this session's transcript |
| `cwd` | the working folder |
| `scratchpad_dir` | a temp folder for this session |
| `prompt_id` | id of this one message |
| `permission_mode` | e.g. `acceptEdits` |
| `hook_event_name` | `UserPromptSubmit` |

So `.prompt` alone is enough. `capture_decision.py` keeps the other guesses and the
longest-string fallback anyway — they cost nothing and they cover a future rename.

Confirmed working: the hook fired on Farid's real messages in session
`5d8ac762-…`, and the reminder text arrived in the agent's context.
