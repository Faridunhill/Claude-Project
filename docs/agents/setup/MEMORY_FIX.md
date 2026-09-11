# The second fault — memory. And how to take it off Farid.

The agent diagnosed this himself, correctly, on 2026-09-11:

> "Nothing makes me write such a file. I wrote it because you caught me. If you do not catch
> me, I do not write it. So today the memory system is you. That is the wrong place for it."

He is right. That is the whole problem in three sentences, and it is a better diagnosis than
most reviews produce. The writing fault is fixed. This is the next one.

## Why the writing fix worked, and why it teaches us the answer
Writing got fixed because we stopped asking the model to remember a rule, and made the
**program** apply it — an output style in its core instructions, and a hook that repeats the
rule on every message. The model's goodwill was removed from the loop.

Memory needs the same move. Asking an agent to "always record decisions" fails for the same
reason "always write short sentences" failed. It judges its own performance, decides it did
fine, and carries on.

## The fix — three layers, same shape as the writing fix

### Layer 1 — catch the decision at the moment it is made  ★ the main one
Farid's decisions arrive inside his own messages. So check his messages, not the agent's
memory.

`capture-decision.sh` (in this folder) runs by itself every time Farid sends a message. It
looks at his words. If it sees a decision word — yes, approved, go ahead, never, from now,
new rule, stop, cancel, I want — it injects one instruction into that turn:

> "Farid may have just decided something. Write one line into DECISIONS.md FIRST, then
> answer him."

The agent cannot skip it, because it is not relying on memory. The reminder arrives with the
message itself.

**Install**
1. Copy `capture-decision.sh` to `.claude/hooks/capture-decision.sh` on the PC.
2. `chmod +x .claude/hooks/capture-decision.sh`
3. In `.claude/settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/capture-decision.sh" }
      ]}
    ]
  }
}
```
If you already have the plain-language hook here, put both commands in the same list. They
both run.

**It fails safe.** If the script cannot read Farid's message text, it reminds on every turn
instead of none. Noise is cheaper than a lost decision.

### Layer 2 — one file, one line, loaded every session
`DECISIONS.md` at the project root. One line per decision. Date, what he decided, what it
changes. Nothing else. It must be pulled into `CLAUDE.md` with an `@DECISIONS.md` line, or
it will not load and we are back where we started.

Rule for the agent: **one line, written before answering.** Not a report. A long entry is a
reason to postpone; a single line is not.

### Layer 3 — the weekly count
Once a week, ask one question: how many lines were added to DECISIONS.md this week? If the
answer is zero and you know you decided things, layer 1 is broken. That check takes ten
seconds and it tests the machine, not the agent's word.

## What does NOT work
- **"Always record decisions" in the laws.** Same class of instruction that already failed.
- **A summary at the end of the session.** Sessions end by crashing, by closing the window,
  by running out of context. The end is the least reliable moment to save anything.
- **Farid catching it.** That is today's system. It is his time, and it is the fault itself.

## UNVERIFIED — test this once on the PC
The public documentation does not name the exact field that carries Farid's message text into
a UserPromptSubmit hook. The script tries three names and falls back to reminding every turn.
Someone on the PC should run it once, send a message containing "approved", and confirm the
agent received the extra instruction. If the field name is different, fix one line.

## The honest limit
This makes forgetting rare and cheap to catch. It does not make it impossible. The measure of
success is not that the agent never forgets. It is that **Farid is no longer the backup.**
