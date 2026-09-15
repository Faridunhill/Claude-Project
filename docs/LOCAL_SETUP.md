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
cd <your Claude-Project folder>
git pull
node scripts/setup-local-claude.mjs
```

That is the whole setup. The script writes two files in your home folder:

| File | What it does |
|---|---|
| `~/.claude/CLAUDE.md` | Your standing instructions — how to talk to you, how to work, the honesty rules, what never to do on this machine. Loads in **every** project. |
| `~/.claude/settings.json` | Model and permissions. Pre-approves the safe commands so Claude stops asking, and hard-blocks `.env` files, keys, `rm -rf`, `sudo` and force-push. |

It works on Windows, macOS and Linux — Node runs the same everywhere, and you
already have Node for this project.

**It is safe to run again.** It is not a file-clobbering installer:

- **Your own writing is never lost.** In `CLAUDE.md` it only rewrites the block
  between the `BEGIN`/`END` markers. Anything you add outside them stays.
- **Your settings are merged, not replaced.** Keys you already set win, and
  permission lists are combined without duplicates. If you had chosen a
  different model or mode, it says so and leaves yours alone — re-run with
  `--force` to take the recommended ones.
- **Anything it changes is backed up first** to `~/.claude/backups/<timestamp>/`.
- Run `--dry-run` first if you want to see the plan without writing anything.

It also detects your OS, Node, npm and Git versions and writes them into the
file, so Claude knows what machine it is on without you typing it.

Then open `~/.claude/CLAUDE.md` and add anything about your own folders **below
the END marker** — where your projects live, which folder is safe to experiment
in, anything you find yourself explaining twice.

### Confirm it worked

Start Claude Code in a project:

```
/status     # correct model?
/context    # are BOTH CLAUDE.md files listed under "Memory files"?
/doctor     # any configuration problems?
```

If `/context` does not list them, nothing above is in effect. Fix that before
anything else.

### The project rules come with git

`CLAUDE.md` at the repo root and `.claude/rules/storefront.md` are committed, so
`git pull` is all it takes for your local Claude to have the same truth rules,
money rules and `/trust-audit`, `/preflight`, `/add-product` commands as the
cloud sessions.

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
