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
