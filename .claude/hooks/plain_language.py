#!/usr/bin/env python3
"""Repeat the writing rule on every message Farid sends.
No dependencies. Python 3 only. Fails loud: writes hook_errors.log if anything breaks."""
import json, sys, pathlib

RULE = ("Write for Farid. Max 12 words per sentence. No idioms or metaphors - say the "
        "physical thing. One computer word per message, with its meaning in the same "
        "sentence. First line = what he must do or decide; if nothing, say 'Nothing needed "
        "from you.' Numbers and names, not descriptions. Never explain a sentence he "
        "questioned - delete it and write a new one.")

try:
    sys.stdin.read()
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": RULE}}))
except Exception as e:
    # Fail loud, never silent. A quiet hook buys false confidence.
    try:
        log = pathlib.Path(__file__).with_name("hook_errors.log")
        log.open("a", encoding="utf-8").write("plain_language.py failed: %r\n" % (e,))
    except Exception:
        pass
    print("plain_language hook failed - writing rule NOT injected", file=sys.stderr)
    sys.exit(1)
