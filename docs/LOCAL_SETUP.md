# Making local Claude Code work like the cloud session

## The thing to understand first

There is no "cloud Claude" and "local Claude". It is the **same Claude Code**,
the same model, the same abilities. A cloud session is just `claude` running on
a rented Linux box instead of your PC.

So there is nothing to move. The difference you noticed is **four settings**,
and all four are yours to change. In fact your local Claude Code can do *more*
than a cloud session, because it can see your whole machine and a cloud session
cannot.

One honest correction before you plan around it: **Claude Code is never fully
offline.** Wherever it runs, your prompts and the file contents Claude reads are
sent to Anthropic's API, because the model runs there. What "local" gets you is
that your code, your keys, your folders, and your git history stay on your PC
and are never copied to a cloud container. That is worth having. But there is no
version of Claude Code that runs with no internet.

---

## The four differences, and how to close each one

### 1. The model

The cloud session runs Opus. Your local install may be defaulting to something
smaller — that alone accounts for most of "he did fine, but not like you."

```
/model
```

Pick Opus. To make it the default for every project, it is the `"model"` key in
`~/.claude/settings.json` (see step 4).

Check what you are actually on at any time with `/status`.

### 2. Permission mode — this is the big one

In a cloud session Claude runs with wide autonomy, so it just works: reads,
edits, runs the build, commits. On a fresh local install Claude stops and asks
before nearly every command. That constant asking is what makes it *feel*
hesitant and less capable. It is not less capable. It is waiting for you.

Fix it by pre-approving the safe commands and denying the dangerous ones, so it
stops asking about `npm run build` but still stops dead at `rm -rf`. That is
what `docs/examples/user-settings.json` in this repo does.

Note: `defaultMode` values `auto` and `bypassPermissions` only take effect from
your **user** settings file, not a project one.

**Do not use `bypassPermissions`.** It approves everything with no questions. On
the machine that holds your shop, that is how you lose a `.env` file. Use
`acceptEdits`, which is what the example file sets.

### 3. Project knowledge

This is already solved and you may not have noticed. `CLAUDE.md`,
`.claude/commands/`, `.claude/agents/store-qa.md` and `.claude/settings.json`
are **committed to this repo**. Your local Claude reads them automatically:

```bash
cd <your Claude-Project folder>
git pull
```

That is it. Your local Claude now has the same truth rules, the same
`/trust-audit`, `/preflight`, `/add-product`, and the same `store-qa` reviewer
this cloud session has.

Confirm with `/context` — your files should be listed under **Memory files**.

### 4. Knowing your machine — what you actually asked for

A cloud session sees one cloned repo and nothing else. Your local Claude can
know your whole setup. Three mechanisms:

**`~/.claude/CLAUDE.md`** — loads in *every* project on your PC, before any
project file. This is where your machine, your folders, your OS, your habits,
and your hard rules go. Template: `docs/examples/user-CLAUDE.md`.

**`~/.claude/rules/*.md`** — same scope, split by topic, for when the one file
gets long.

**Extra folders** — Claude only sees the folder you launched it in. To reach
others:

```bash
claude --add-dir ../other-project
```

Or list them permanently under `permissions.additionalDirectories` in
`~/.claude/settings.json`. To also load *their* CLAUDE.md files:

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared
```

**Auto memory** — on by default. Claude writes its own notes about your
corrections and preferences into `~/.claude/projects/<project>/memory/`, and
loads them next session. Browse or edit it with `/memory`. This is machine-local
and never leaves your PC. It is the thing that makes local Claude get better at
*you* over time in a way a fresh cloud session never can.

---

## Do this now

```bash
# 1. Get the project config that already exists
cd <your Claude-Project folder>
git pull

# 2. Install the two personal files
#    macOS / Linux:
mkdir -p ~/.claude
cp docs/examples/user-CLAUDE.md   ~/.claude/CLAUDE.md
cp docs/examples/user-settings.json ~/.claude/settings.json

#    Windows PowerShell:
#    mkdir $env:USERPROFILE\.claude -Force
#    copy docs\examples\user-CLAUDE.md   $env:USERPROFILE\.claude\CLAUDE.md
#    copy docs\examples\user-settings.json $env:USERPROFILE\.claude\settings.json

# 3. EDIT ~/.claude/CLAUDE.md — fill in every <angle bracket> with your real
#    paths, OS, and folders. An unedited template is worse than none.

# 4. Make sure you are current
claude update
```

Then start Claude in the project and check three things:

```
/status     # correct model?
/context    # are CLAUDE.md and ~/.claude/CLAUDE.md both listed under Memory files?
/doctor     # any configuration problems?
```

If `/context` does not list your files, they are not loaded and nothing above is
in effect. Fix that before anything else.

---

## What you get afterwards

Local Claude Code, with this setup, does everything a cloud session does plus:

- runs your real `npm run dev` and sees the actual site at localhost:3000
- reads and edits any folder on your PC, not just one repo
- remembers your corrections across sessions via auto memory
- keeps your keys, code, and git history on your machine

The cloud session keeps exactly two advantages: it runs while your PC is off,
and it can be triggered from your phone. For building the shop, local is the
better tool. It was always the same Claude — it was just under-configured.

---

## If it still feels weaker

In order of likelihood:

1. **Wrong model.** `/status`. This is usually it.
2. **Still asking permission constantly.** Your settings file did not load, or
   has a JSON syntax error. Settings files are strict JSON — no comments, no
   trailing commas. Claude Code reports a broken one as a Settings Error at
   startup. Run `/doctor`.
3. **`/context` does not list your memory files.** Wrong path, or you are
   launching Claude from a different directory than you think.
4. **Out of date.** `claude update`.
5. **You are asking small.** A cloud session gets the whole job in one message.
   Give local Claude the same: the goal, the constraint, and what "done" means.
   "Fix the checkout" gets less than "checkout takes the price from the browser;
   make it look the price up server-side from lib/products.ts, reject unknown
   slugs, and show me the diff before committing."
