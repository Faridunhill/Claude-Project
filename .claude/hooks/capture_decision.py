#!/usr/bin/env python3
r"""DECISION CAPTURE + PLAIN LANGUAGE REMINDER. Runs by itself every time Farid sends a message.

WHY THIS IS PYTHON AND NOT THE ORIGINAL BASH.
The bash version needs `jq`. On 2026-09-11 the keeper checked Farid's PC: jq is not installed and is
not on the path. Installed as written, both hook commands would have failed silently and the hook
would have done nothing at all, while looking installed. That is the exact fault this whole day was
about: a rule that exists and nothing calls it. Python 3.11 is already on the PC, so this version
has no dependency to install.

WHAT IT DOES.
1. Writes the raw input it received to `.claude/hooks/last_input.json`. That answers the open
   question: which field actually carries Farid's message text in this version of Claude Code.
2. If his message looks like a decision, it tells the agent to write the decision into DECISIONS.md
   BEFORE answering, so nobody has to remember.
3. It always adds the plain-language reminder, because that law applies to every message.

Wire it in settings.json under hooks.UserPromptSubmit:
    python "${CLAUDE_PROJECT_DIR}/.claude/hooks/capture_decision.py"
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Words that usually mean Farid just decided something, in his own English.
DECIDED = re.compile(
    r"\b(yes|approved?|agreed?|go ahead|do it|start|stop|never|always|from now|new law|"
    r"new rule|i want|i decided|decision|confirm|cancel|drop it|keep it|change it|use |"
    r"don'?t |do not |no more|i will need|i need)\b", re.I)

PLAIN = ("Write for Farid. Max 12 words per sentence. No idioms and no word-pictures - say the "
         "physical thing that happens. One computer word per message, and give its meaning in the "
         "same sentence; pipe words are free. First line = what he must do or decide, or "
         "'Nothing needed from you.' Numbers and names, never 'several'. If he questions a "
         "sentence, delete it and write a new one - never explain it.")

WRITE_IT_DOWN = (
    "CHECK BEFORE YOU ANSWER. Farid may have just decided something, approved something, or made a "
    "new rule. If he did: write one line into DECISIONS.md FIRST, then answer him. The line is: "
    "date, what he decided, and what it changes. If he decided nothing, ignore this. Do not tell "
    "him you checked.")


def main():
    raw = sys.stdin.read()

    # Step 7 of his install job: find the real field name. Keep the last input so a human can look.
    try:
        with open(os.path.join(HERE, "last_input.json"), "w", encoding="utf-8") as f:
            f.write(raw)
    except Exception:
        pass

    prompt = ""
    try:
        d = json.loads(raw) if raw.strip() else {}
        for key in ("prompt", "user_prompt", "message", "text", "userPrompt", "content", "input"):
            v = d.get(key)
            if isinstance(v, str) and v.strip():
                prompt = v
                break
        if not prompt:
            # some versions nest it; take the longest string anywhere in the object
            found = []

            def walk(o):
                if isinstance(o, str):
                    found.append(o)
                elif isinstance(o, dict):
                    for x in o.values():
                        walk(x)
                elif isinstance(o, list):
                    for x in o:
                        walk(x)
            walk(d)
            prompt = max(found, key=len) if found else ""
    except Exception:
        prompt = raw          # not JSON - treat the whole thing as the text

    context = PLAIN
    if not prompt or DECIDED.search(prompt):
        # No text found = fail safe, remind anyway. A missed decision costs more than a nudge.
        context = WRITE_IT_DOWN + "\n\n" + PLAIN

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": context}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
