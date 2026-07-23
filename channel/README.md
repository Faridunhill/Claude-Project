# The Channel — Farid ⇄ Agent

A file exchange between Farid and the Claude agent, living inside the repo so both sides can
always reach it.

## The three boxes

| Folder | Direction | Use |
|---|---|---|
| `TO_AGENT/` | Farid → Agent | Anything you want me to read or act on: notes, scripts, photos, questions as .md/.txt files |
| `TO_FARID/` | Agent → Farid | My replies, reports, and deliverables — numbered and dated |
| `NEW_UPLOADS/` | Farid → Agent | Raw dumps (folders like FARID_CHANNEL, corpus files, mirrors). I sort them from here into the right place |

## How Farid uses it

**Easy way (no tools needed):** github.com → `Faridunhill/Claude-Project` → switch to branch
`claude/session-71nyhc` → open `channel/TO_AGENT/` or `channel/NEW_UPLOADS/` →
**Add file → Upload files** → commit. Then tell the agent in chat: "check the channel."

**Desktop way (the folder lives on your Desktop like any other):** once, in a terminal:

```
cd %USERPROFILE%\Desktop
git clone https://github.com/Faridunhill/Claude-Project.git FARID_CLAUDE_CHANNEL
cd FARID_CLAUDE_CHANNEL
git checkout claude/session-71nyhc
```

After that, `Desktop\FARID_CLAUDE_CHANNEL\channel\` is the channel. Drop files into
`TO_AGENT` or `NEW_UPLOADS`, then run `git add . && git commit -m "drop" && git push`
(or say the word and we script a one-click `send.bat` for it).
To receive: `git pull` — new items from the agent appear in `TO_FARID`.

## How the agent uses it

- Checks `TO_AGENT/` and `NEW_UPLOADS/` whenever Farid says "check the channel" (and at the
  start of any work session).
- Writes replies to `TO_FARID/` as `NNN_YYYY-MM-DD_short-title.md`, then pushes.
- Never deletes anything Farid uploaded; sorted items are moved, with a note in `TO_FARID`.
