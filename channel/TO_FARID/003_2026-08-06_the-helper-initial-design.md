# 003 — THE HELPER: the initial design (before I write any code)

You gave me four answers. I did the deep search. This is the plan. **Nothing is built yet —
read it, tell me what's wrong, then I build.**

## What you asked for, in my words — say YES or correct me

1. **Two windows, one helper.** A dashboard on your iPhone where you can send messages, and
   the dashboard you already have on the desktop — both showing the same helper, at the same
   time.
2. **The list is the power.** You give him a to-do list. Whatever is on the list, he does. He
   does not come back asking permission for each step.
3. **He reaches every corner of the system.** But Claude stays on top in the first period and
   does the hard jobs; he works underneath.
4. **Awake all the time.** Not only when you call him.

---

## The scoreboard: what this actually is

One program on your PC that never sleeps. It has **one brain and two windows** — your phone
and your desktop see the same thing, live. You put work on a list; he does the list. He can
touch anything on the machine. He stops for four things only, all of them things that cannot
be undone.

## The five pieces

### 1. The brain — a service that never stops
A Python program running as a Windows service, started at boot. Built on Anthropic's **Claude
Agent SDK** — that's Claude Code sold as a library, so he gets the real tools out of the box:
read/write files, run PowerShell, search the web, spawn helpers, remember across restarts.

This is the honest answer to what Prime Agent was showing us. Same five bones — Python as the
language, memory that survives, helpers as function calls, background running, skills he writes
himself — but from Anthropic, made for Claude, and it does not need WSL and does not rewrite
its own laws.

He wakes on three things: **your list changes**, **the clock** (the standing daily work), or
**you talk to him.** Between those he sleeps, so he isn't burning your subscription doing
nothing.

### 2. The list — this is the permission system
This replaces the approval tokens from THE DESK. **The list IS the approval.**

You write a line — "clean the disk", "hunt Upshall auctions", "sort the ARK photos", "update
the drivers" — and that line is his authority to do it. He works top to bottom, marks each one
done with proof, and reports.

**The four stops.** He stops and asks only for things that cannot be undone:
- spending your money
- publishing anything public (the domain, the site, the museum list — your gates)
- deleting the ARK or your original photos
- wiping or formatting a disk

These are my choice, not yours yet. **If you want any of the four removed, say so and I remove
it.** Everything else — installing, downloading, deleting caches, writing code, editing files,
rebuilding the cabinets — he just does.

These four stops are not written in a prompt where he could talk himself past them. They are
locked in code, before the tool runs. He cannot argue with them.

### 3. The desk — one door, two windows
A small web server on your PC. Both dashboards talk to it, so they always agree:
the list, the status, the chat, the log, photo drops.

### 4. The phone
A web app served from your own PC, reached over **Tailscale** — a private tunnel between your
iPhone and your PC. No domain to buy, no open ports, no port forwarding, and it works on
cellular anywhere. Your ARK never goes to any cloud; the phone reads it from your machine.

You add it to your Home Screen once and it looks and opens like a real app. Because it's on the
Home Screen, iPhone lets it **send you notifications** — so he can tap you on the shoulder when
he finishes the overnight run or hits one of the four stops.

On the phone screen: the scoreboard (what he did while you slept) · the list (type it, or hold
the microphone and speak it) · a chat box · "needs Farid" · drop a photo straight in.

**Cost: nothing.** Tailscale is free for one person.

### 5. The hierarchy — Claude on top
Exactly your answer 3:
- **The Manager** (Claude Opus 5 — me, the same Creator, with `laws.md`) plans, decides, checks
  the work against the honesty laws, and writes to you.
- **The workers** underneath do the grinding — sweeping the 19,000 ARK files, hunting Charatan
  and Upshall evidence, collecting interview videos, PC chores, cabinet checks.
- Nothing a worker finds becomes a published fact until the Manager has checked it against the
  laws. Wide brackets. Both sources on a dispute. Absence never dates.

---

## What I need from you before I build

1. **The desktop dashboard you already have — what is it?** I'm in the cloud; I cannot see your
   PC. Is it the Claude Code window you type in, THE DESK commands, the Builder studio, or
   something else? Whatever it is, the new phone window will point at the same brain — I just
   need to know what I'm connecting to.
2. **The job list** — which of these is his work? (I'll assume all four unless you cut some.)
   PC care and files · encyclopedia work · research and harvest · email and buying catalogues.
3. **The four stops** — keep all four, or cut some?

## What I am NOT hiding from you

- **Windows.** I write the code here in the cloud; I cannot test it on your machine. The first
  install needs one local session to prove it runs. I will not tell you it works until it has
  run on your PC.
- **Your login.** He runs under your own Claude login on your own machine. If that ever hits a
  limit, the fallback is a paid API key — I'll tell you before that ever matters, not after.
- **Tailscale is a third-party program.** You install it on the PC and the iPhone. If you don't
  want it, the fallback is a private Telegram bot — less of a dashboard, but zero install.
- **THE DESK already on this branch gets rebuilt, not thrown away.** The laws, the honesty
  guard, the memory, the idea ledger and the job queue all survive. What changes: the approval
  tokens become the list, and the once-a-day command becomes a service that never sleeps.

---

**Say what's wrong. Then I build the whole thing and prove it live.**

— your agent
