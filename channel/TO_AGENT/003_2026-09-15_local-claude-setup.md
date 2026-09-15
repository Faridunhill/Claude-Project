# Task for the Builder: set up local Claude Code

**From:** Farid (drafted for him by the cloud session, 2026-09-15)
**Do this:** at the start of your next session, then report back.

---

## Why

The cloud sessions and this local one are the same Claude Code — the difference
was configuration, not capability. The cloud side is done. The local side needs
one command run on Farid's PC, which a cloud session cannot reach. That is you.

## Steps

**1. Make sure you have the repo, up to date.**

If the folder already exists:

```bash
cd <the Claude-Project folder on this PC>
git checkout main
git pull
```

If it does not exist yet:

```bash
git clone https://github.com/Faridunhill/Claude-Project.git
cd Claude-Project
```

**2. See what the setup would change, before it changes anything.**

```bash
node scripts/setup-local-claude.mjs --dry-run
```

Show Farid the output. It writes nothing in this mode.

**3. Apply it.**

```bash
node scripts/setup-local-claude.mjs
```

This writes `~/.claude/CLAUDE.md` (standing instructions, every project) and
`~/.claude/settings.json` (model + permissions).

**4. Read the output carefully and tell Farid what it says.**

Two cases need his decision, and the script prints them:

- **"LEFT ALONE"** — he already set something differently. Most important is
  `model`. If it reports his model is not `claude-opus-5`, tell him, and ask
  whether to re-run with `--force` or leave it. Do not force it on your own.
- **"backups"** — it copied the old files somewhere first. Tell him the path.

**5. Confirm it actually loaded.** In a session, run:

```
/status     # correct model?
/context    # are BOTH CLAUDE.md files under "Memory files"?
/doctor     # any configuration problems?
```

If `/context` does not list them, the setup is not in effect. Fix that before
telling him it is done.

**6. Add what only this machine knows.**

Open `~/.claude/CLAUDE.md` and add, **below the `END` marker**:

- where his projects live on this PC
- which folder is safe to experiment in
- where the FaridOS dating cabinets, `SYSTEM_LEDGER.md` and the ARK live
- anything you find yourself explaining to a new session twice

Everything below that marker survives every future run of the script. The block
between the markers is managed and will be rewritten.

**7. Report back** in `channel/TO_FARID/` as `NNN_YYYY-MM-DD_local-setup-done.md`:
what changed, what was left alone, the backup path, and the `/context` result.

## Notes

- Safe to re-run. Your text outside the markers is never touched, settings are
  merged rather than replaced, and anything changed is backed up first to
  `~/.claude/backups/<timestamp>/`.
- `--force` overwrites values Farid set differently. Only with his yes.
- The project rules (`CLAUDE.md`, `.claude/rules/storefront.md`) and the
  `/trust-audit`, `/preflight`, `/add-product` commands come with `git pull` —
  no install step.
- Background: `docs/LOCAL_SETUP.md`.
