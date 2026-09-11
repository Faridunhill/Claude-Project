# How to make the writing rule actually stick — three layers

Writing a rule in a document does not make a model obey it. The model reads the document,
decides it was clear enough, and sends the message anyway. These three layers are different.
The first two are run by the program, not by the agent's memory.

## Layer 1 — the output style  ★ the real tool, do this one first
Claude Code has a feature built for exactly this. An output style is added to the agent's
core instructions, not to a document it may or may not re-read. It is saved in the settings
and it stays on across every session.

**Do this:**
1. Copy `farid-plain.md` (in this folder) to **`.claude/output-styles/farid-plain.md`** in
   the project on the PC. For every project, put it in `~/.claude/output-styles/` instead.
2. In the session, run `/output-style` and pick **Farid Plain**.
3. It saves itself. You do not repeat this.

`keep-coding-instructions: true` means the agent keeps all its normal skills. Only the
writing changes.

## Layer 2 — inject the rule on every single turn
A hook is a small command the program runs by itself. `SessionStart` runs once when the
session opens. **`UserPromptSubmit` runs every time you send a message** — that is the
stronger one, because it survives a long session and it survives compaction.

Put this in **`.claude/settings.json`** on the PC:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "jq -n '{hookSpecificOutput:{hookEventName:\"UserPromptSubmit\",additionalContext:\"Write for Farid. Max 12 words per sentence. No idioms or metaphors - say the physical thing. One computer word per message, with its meaning. First line = what he must do. Numbers not descriptions. Never explain a questioned sentence - rewrite it.\"}}'"
          }
        ]
      }
    ]
  }
}
```
Test it once: send any message, and ask the agent whether it received extra context.

## Layer 3 — your one-word correction
Layers 1 and 2 are reminders. This one is the feedback.

When you see a picture instead of a fact, reply with one word: **PICTURE**.
When a sentence is too long, reply: **LONG**.
When you had to ask what it meant, reply: **REWRITE**.

One word costs you two seconds. The agent must then delete and rewrite, not explain. Do this
for one week. It is the cheapest training signal you have, and it works inside the session
where the model can still see what it did.

## What does NOT work, so nobody wastes a day on it
- **A law in `SYSTEM_LEDGER.md` or any document that does not auto-load.** The agent never
  sees it. This was the original fault.
- **`--append-system-prompt`** on the command line. It works, but only for that one
  launch. It does not persist. Use the output style instead.
- **The statusline.** It can show text, but it refreshes reactively and the agent does not
  read it. It is for you, not for the agent.
- **Asking the agent to promise.** A promise is not a mechanism.

## The honest limit
No setup makes a model perfectly obedient. What these layers do is make failures **rare,
loud and cheap to catch**. Layer 1 changes what it is told at its core. Layer 2 repeats it
every turn so it cannot drift. Layer 3 catches what still gets through, in two seconds.

**UNVERIFIED:** a `Stop` hook fires after the agent finishes a reply and can block it and
force a rewrite. That would be a true automatic checker. The public documentation does not
confirm that the hook receives the text of the reply, so I cannot promise a script that
counts sentence length automatically. Someone on the PC should test it before we rely on it.
