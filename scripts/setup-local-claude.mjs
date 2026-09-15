#!/usr/bin/env node
/**
 * Set up local Claude Code on Farid's PC to match the cloud sessions.
 *
 *   node scripts/setup-local-claude.mjs            apply
 *   node scripts/setup-local-claude.mjs --dry-run  show what would change
 *   node scripts/setup-local-claude.mjs --force    overwrite settings you
 *                                                  already set differently
 *
 * Writes two files in your home Claude folder:
 *   ~/.claude/CLAUDE.md      standing instructions, loaded in EVERY project
 *   ~/.claude/settings.json  model + permissions, applied in every project
 *
 * Safe to run more than once. It never destroys what is already there:
 *   - CLAUDE.md  keeps your own text and only rewrites the block between the
 *                BEGIN/END markers below.
 *   - settings.json is deep-merged; your existing keys win where they differ,
 *                   and permission lists are combined without duplicates.
 *   - Anything it changes is copied to ~/.claude/backups/<timestamp>/ first.
 *
 * Machine facts (OS, Node, shell) are detected and written in automatically.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync } from 'node:fs'
import { homedir, platform, release, arch, userInfo } from 'node:os'
import { join } from 'node:path'
import { execSync } from 'node:child_process'

const DRY_RUN = process.argv.includes('--dry-run')
const FORCE = process.argv.includes('--force')

const BEGIN = '<!-- BEGIN claude-code-setup (managed — edit outside these markers) -->'
const END = '<!-- END claude-code-setup -->'

const CLAUDE_DIR = join(homedir(), '.claude')
const MEMORY_FILE = join(CLAUDE_DIR, 'CLAUDE.md')
const SETTINGS_FILE = join(CLAUDE_DIR, 'settings.json')
const BACKUP_DIR = join(CLAUDE_DIR, 'backups', new Date().toISOString().replace(/[:.]/g, '-'))

const changes = []

function detect(cmd) {
  try {
    return execSync(cmd, { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim().split('\n')[0]
  } catch {
    return 'not found'
  }
}

function prettyOS() {
  const p = platform()
  if (p === 'win32') return `Windows (${release()}, ${arch()})`
  if (p === 'darwin') return `macOS (Darwin ${release()}, ${arch()})`
  return `${p} ${release()} (${arch()})`
}

// ── The standing instructions ────────────────────────────────────────────────

function memoryBlock() {
  const facts = [
    `- OS: ${prettyOS()}`,
    `- Node: ${detect('node -v')}   npm: ${detect('npm -v')}`,
    `- Git: ${detect('git --version')}`,
    `- Home: ${homedir()}`,
    `- User: ${userInfo().username}`,
    `- Detected ${new Date().toISOString().slice(0, 10)} by scripts/setup-local-claude.mjs`,
  ].join('\n')

  return `${BEGIN}

# Farid — standing instructions

These apply in every project on this machine. Project-specific rules live in
that project's own CLAUDE.md and take precedence over anything here.

## Who I am

Farid, New Jersey. I run **Faridunhill** — estate pipes, hand-carved meerschaum,
vintage leather, and smoking accessories — selling on eBay, on Etsy, and at
faridunhill.com. Over eight thousand sales across the two marketplaces.

I am not a professional developer. English is not my first language.

## How to talk to me

- Plain words, short sentences. Define a technical term once, then use it.
- **Lead with the outcome**, not the plan. Tell me what happened first.
- Read my intent generously. If a big instruction could mean two things, say it
  back to me in plain words and get a yes before you build it.
- Tell me what you actually did, with the real output. If it failed, say it
  failed. Do not soften a bad result.

## How to work

- **Finish the whole job.** If one part is blocked, do everything else and tell
  me plainly what you left and why. Do not quietly make the job smaller.
- **Verify before you claim.** Run the command, read the output, show it to me.
  "It should work" is not the same as "I ran it and it works".
- Never present a guess as a fact. **"I could not check this" is a good answer.**
- Plan first on anything touching more than a couple of files. Wait for my go.
- When you are done, say what is left and what you need from me.

## Honesty is the product

This is the rule behind all the others, and it applies to the shop, the
encyclopedia, and everything else:

- **Never invent a number, a review, a date, a credential, or a customer.** If a
  figure cannot be verified, it does not ship. A statistic belongs on a page only
  when it is linked to the source a reader can check.
- A claim on a website or a listing is a promise. Describe what the code and the
  item **actually are** — condition, flaws, and all.
- Wide brackets beat confident guesses. Disputed facts carry both sources.
  Absence of a stamp never dates a pipe.
- **Buy, don't pirate.** Never commit copyrighted scans or mirrors to a repo. We
  publish facts and cite sources; we never republish someone else's page images.

## Never, on this machine

- Never print, copy, or commit \`.env\` files, API keys, or tokens — not into a
  file, not into a commit, not into our conversation.
- Never run \`git push --force\` on a shared branch, \`rm -rf\`, or drop a database
  unless you ask in the same message and I answer.
- **Never push to \`main\` without telling me it will go live**, on any repo that
  deploys.
- Never install a package, plugin, or MCP server I did not ask for.
- Live payment keys do not belong on this machine. Test keys locally, live keys
  in the host's environment settings.

## Git

- Branch as \`claude/<short-description>\`; push with \`git push -u origin <branch>\`.
- Commit messages say what changed and why, in plain English. No marketing.
- Never commit straight to \`main\` on a deploying repo without saying so first.

## This machine

${facts}

<!-- Add your own notes below the END marker — re-running the setup script will
     not touch them. Worth adding: where your projects live, which folder is
     safe to experiment in, and anything you find yourself explaining twice. -->

${END}`
}

// ── Settings ─────────────────────────────────────────────────────────────────

const SETTINGS_PATCH = {
  model: 'claude-opus-5',
  permissions: {
    defaultMode: 'acceptEdits',
    allow: [
      'Bash(npm run lint)', 'Bash(npm run typecheck)', 'Bash(npm run build)',
      'Bash(npm run dev)', 'Bash(npm test:*)', 'Bash(npm ci)', 'Bash(npm install)',
      'Bash(git status:*)', 'Bash(git diff:*)', 'Bash(git log:*)',
      'Bash(git branch:*)', 'Bash(git add:*)', 'Bash(git commit:*)',
      'Bash(git fetch:*)', 'Bash(git checkout:*)',
      'Bash(ls:*)', 'Bash(cat:*)', 'Bash(head:*)', 'Bash(tail:*)',
      'Bash(grep:*)', 'Bash(rg:*)', 'Bash(find:*)', 'Bash(wc:*)',
      'Bash(python3:*)', 'Bash(pip list)', 'Bash(npx tsc:*)',
    ],
    deny: [
      'Read(**/.env)', 'Read(**/.env.local)', 'Read(**/.env.*.local)',
      'Read(**/id_rsa)', 'Read(**/id_ed25519)', 'Read(**/*.pem)',
      'Read(**/credentials.json)', 'Read(**/.aws/**)', 'Read(**/.ssh/**)',
      'Bash(git push --force:*)', 'Bash(git push -f:*)',
      'Bash(rm -rf:*)', 'Bash(sudo:*)', 'Bash(curl:* | sh)', 'Bash(curl:* | bash)',
    ],
  },
}

const conflicts = []

function mergeSettings(existing, patch, path = '') {
  const out = { ...existing }
  for (const [key, value] of Object.entries(patch)) {
    const where = path ? `${path}.${key}` : key
    if (Array.isArray(value)) {
      // Union, preserving the user's order first.
      out[key] = [...new Set([...(Array.isArray(out[key]) ? out[key] : []), ...value])]
    } else if (value && typeof value === 'object') {
      out[key] = mergeSettings(out[key] && typeof out[key] === 'object' ? out[key] : {}, value, where)
    } else if (out[key] === undefined) {
      out[key] = value
    } else if (out[key] !== value) {
      // You already chose something different. Without --force we keep your
      // value and say so, rather than silently overriding a deliberate choice
      // — or silently failing to apply the one that matters.
      if (FORCE) {
        conflicts.push({ where, was: out[key], now: value, applied: true })
        out[key] = value
      } else {
        conflicts.push({ where, was: out[key], now: value, applied: false })
      }
    }
  }
  return out
}

// ── Apply ────────────────────────────────────────────────────────────────────

function backup(file) {
  if (!existsSync(file) || DRY_RUN) return
  mkdirSync(BACKUP_DIR, { recursive: true })
  copyFileSync(file, join(BACKUP_DIR, file.split(/[\\/]/).pop()))
}

function writeMemory() {
  const block = memoryBlock()
  let next
  let how

  if (!existsSync(MEMORY_FILE)) {
    next = block + '\n'
    how = 'created'
  } else {
    const current = readFileSync(MEMORY_FILE, 'utf8')
    if (current.includes(BEGIN) && current.includes(END)) {
      const before = current.slice(0, current.indexOf(BEGIN))
      const after = current.slice(current.indexOf(END) + END.length)
      next = before + block + after
      how = 'updated the managed block, left your own text untouched'
    } else {
      next = current.trimEnd() + '\n\n' + block + '\n'
      how = 'appended the managed block, left your existing file above it'
    }
    if (next === current) {
      changes.push(`~/.claude/CLAUDE.md          already up to date`)
      return
    }
  }

  backup(MEMORY_FILE)
  if (!DRY_RUN) writeFileSync(MEMORY_FILE, next)
  changes.push(`~/.claude/CLAUDE.md          ${how}`)
}

function writeSettings() {
  let existing = {}
  let how = 'created'

  if (existsSync(SETTINGS_FILE)) {
    const raw = readFileSync(SETTINGS_FILE, 'utf8')
    try {
      existing = JSON.parse(raw)
      how = 'merged — your existing values kept, permission lists combined'
    } catch {
      console.error(`\n  ! ~/.claude/settings.json is not valid JSON.`)
      console.error(`    Claude Code reports that as a Settings Error at startup.`)
      console.error(`    Fix the syntax (no comments, no trailing commas) and re-run.\n`)
      process.exitCode = 1
      return
    }
  }

  const merged = mergeSettings(existing, SETTINGS_PATCH)
  const next = JSON.stringify(merged, null, 2) + '\n'

  if (existsSync(SETTINGS_FILE) && next === readFileSync(SETTINGS_FILE, 'utf8')) {
    changes.push(`~/.claude/settings.json      already up to date`)
    return
  }

  backup(SETTINGS_FILE)
  if (!DRY_RUN) writeFileSync(SETTINGS_FILE, next)
  changes.push(`~/.claude/settings.json      ${how}`)
}

console.log(`\n  Claude Code local setup${DRY_RUN ? '  (dry run — nothing will be written)' : ''}`)
console.log(`  ${prettyOS()}\n`)

if (!DRY_RUN) mkdirSync(CLAUDE_DIR, { recursive: true })
writeMemory()
writeSettings()

for (const line of changes) console.log(`  ${line}`)
if (existsSync(BACKUP_DIR)) console.log(`\n  backups            ${BACKUP_DIR}`)

if (conflicts.length) {
  const kept = conflicts.filter((c) => !c.applied)
  const forced = conflicts.filter((c) => c.applied)
  if (forced.length) {
    console.log(`\n  Overwritten (--force):`)
    for (const c of forced) console.log(`    ${c.where}: ${JSON.stringify(c.was)} -> ${JSON.stringify(c.now)}`)
  }
  if (kept.length) {
    console.log(`\n  You already set these differently, so they were LEFT ALONE:`)
    for (const c of kept) {
      console.log(`    ${c.where}: yours ${JSON.stringify(c.was)}   recommended ${JSON.stringify(c.now)}`)
    }
    const model = kept.find((c) => c.where === 'model')
    if (model) {
      console.log(`\n    ^ model is the setting that decides how capable local Claude feels.`)
      console.log(`      To use the recommended one: run /model in Claude Code, or re-run`)
      console.log(`      this script with --force.`)
    } else {
      console.log(`\n    To apply the recommended values, re-run with --force.`)
    }
  }
}

console.log(`
  Next:
    1. Open ~/.claude/CLAUDE.md and add anything about your own folders
       below the END marker. Re-running this script will not touch it.
    2. Start Claude Code in a project and check:
         /status    correct model?
         /context   are both CLAUDE.md files listed under Memory files?
         /doctor    any configuration problems?

  If /context does not list them, nothing above is in effect — fix that first.
`)
