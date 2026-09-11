#!/bin/bash
# Decision capture. Runs by itself every time Farid sends a message.
# If his message looks like a decision, it tells the agent to write it down
# BEFORE answering. The agent does not have to remember to do this.
#
# Install: chmod +x .claude/hooks/capture-decision.sh
# Wire it in .claude/settings.json under hooks.UserPromptSubmit (see SETUP_INSTRUCTIONS.md).

INPUT=$(cat)

# Try to read Farid's message text. Field name may vary by version.
PROMPT=$(printf '%s' "$INPUT" | jq -r '.prompt // .user_prompt // .message // empty' 2>/dev/null)

# Words that usually mean a decision was just made, in Farid's own English.
PATTERN='yes|approved|approve|agreed|go ahead|do it|start|stop|never|always|from now|new law|new rule|i want|i decided|decision|confirm|cancel|drop it|keep it|change it|use |dont |do not |no more'

NEEDED=0
if [ -z "$PROMPT" ]; then
  # Could not read the text. Fail safe: remind on every turn, quietly.
  NEEDED=1
elif printf '%s' "$PROMPT" | grep -qiE "$PATTERN"; then
  NEEDED=1
fi

if [ "$NEEDED" -eq 1 ]; then
  jq -n '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:"★ CHECK BEFORE YOU ANSWER. Farid may have just decided something, approved something, or made a new rule. If he did: write one line into DECISIONS.md FIRST, then answer him. The line is: date, what he decided, and what it changes. If he did not decide anything, ignore this and answer normally. Do not tell him you checked."}}'
fi
exit 0
