<!-- Copy to ~/.claude/CLAUDE.md  (Windows: %USERPROFILE%\.claude\CLAUDE.md)
     This file loads in EVERY project on this machine, before any project CLAUDE.md.
     Keep it under ~200 lines — longer files get followed less reliably.
     Replace every <angle bracket> with your real value. Delete lines that are not true. -->

# Farid — machine and working preferences

## Who I am

I run Faridunhill, an online shop for estate pipes, cigars, and leather smoking
accessories. I am not a professional developer. Explain what a change does and
why before you make it, in plain language. English is not my first language —
short sentences, no jargon unless you define it once.

## This machine

- OS: <Windows 11 / macOS 15 / Ubuntu 24.04>
- Shell: <PowerShell / zsh / bash>
- Node: <run `node -v` and put the version here>
- Package manager: npm
- Editor: <VS Code / other>

## Where my work lives

- `<C:\Users\farid\projects\Claude-Project>` — the faridunhill.com storefront
  (Next.js 14, Stripe, Vercel). The real one. Has its own CLAUDE.md — read it.
- `<path>` — <what this folder is>
- `<path>` — <what this folder is>

Anything under `<path to a scratch folder>` is throwaway. You may experiment
freely there. Everywhere else, ask before creating new top-level folders.

## How I want you to work

- Plan first on anything that touches more than two files. Tell me the plan,
  wait for me to say go.
- Do the whole task. If part of it is blocked, finish the rest and tell me
  plainly what you left and why. Do not quietly shrink the job.
- When you are not sure whether something is true, say so. Do not guess and
  present the guess as fact. I would rather hear "I could not check this."
- Show me the command output when you claim something passed. If a test fails,
  say it failed.
- Never say a change is done until you have actually run it.

## Never, on this machine

- Never read, print, or copy `.env`, `.env.local`, or any file with a key in it
  into our conversation, into a commit, or into a file.
- Never run `git push --force`, `rm -rf`, or a database drop without asking me
  first, in the same message, and waiting for my answer.
- Never commit to `main` directly. Branch first.
- Never install a package, plugin, or MCP server I did not ask for.
- Live Stripe keys are not on this machine. If a task seems to need one, stop
  and tell me — the answer is to use a test key or to set it in Vercel.

## Git

- Branch naming: `claude/<short-description>`
- Commit messages: what changed and why, plain English, no marketing.
- Push with `git push -u origin <branch>`. Never force-push a branch I share.
