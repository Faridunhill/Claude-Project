# THE HELPER — brief for any session that has not met him

**Read this if you are working on Farid's selling, marketing, inventory, or the local machine.**
Written 2026-08-08 from the session on `claude/prime-agent-github-review-d0omns`. Several
sessions are currently blocked on questions this answers.

---

## What the Helper is

An always-on program on Farid's PC. Not a chat session — a service that starts at boot and never
sleeps. Built on the **Claude Agent SDK** (Claude Code as a Python library: real file tools,
PowerShell, web search, subagents, memory that survives restarts).

Farid's four decisions, in his words:

1. **Two windows, one helper** — a dashboard on his desktop, and his iPhone as the alert channel.
2. **"the power that i can gave it to do list, whatever it is each time"** — the to-do list *is*
   the permission system. A line on the list is the authority to do it. He does not approve
   step by step.
3. **"he interfere in each corner of this system, only claude can be on top in first period"** —
   the Helper reaches everywhere; the Manager (Opus 5, `laws.md`) plans, judges and reviews;
   workers do the grinding underneath.
4. **Awake all the time.**

**His job list, as of 2026-08-08:** store management (the inventory problem below) · marketing ·
running **the monster** · plus the standing encyclopedia work.

## The four hard stops

Everything else he does without asking. He stops only for what cannot be undone:

- spending Farid's money
- publishing anything public (domain, museum brand list, launches — Farid's gates)
- deleting the ARK or the original photos
- wiping or formatting a disk

These are enforced in code before the tool runs (SDK hooks), not written in a prompt. A model
cannot talk its way past them. **If you are designing anything for the Helper, do not add a
fifth stop without asking Farid — friction is what he asked us to remove.**

## The phone is ntfy, not a dashboard

Decided 2026-08-08. Alerts and tap-to-approve, self-hosted on his PC, reached over Tailscale.
Telegram was considered and rejected for now (messages would sit on Telegram's servers, and the
ARK is private research). WhatsApp rejected outright (Meta business account, per-message fees).

**The one setting that matters:** the self-hosted ntfy server needs `upstream-base-url:
"https://ntfy.sh"` or iPhone alerts arrive 20–30 minutes late. Only a message id travels; the
content stays on his machine.

## THE INVENTORY GUARD — already built, and it unblocks several of you

Farid, 2026-08-06: *"this week two pipes sold min two platform, Claude so far didn't solve it."*
Three channels: **his own site** (Stripe — `app/api/webhook/route.ts` already catches
`checkout.session.completed`), **Etsy**, **eBay**.

Built, 14 tests passing, delivered to his PC as a zip:

- **The atomic claim.** `UPDATE stock SET state='sold' WHERE sku=? AND state='available'` — one
  row changed means you won the pipe, zero means you are the double sale. Proven under an
  eight-thread race: exactly one winner.
- **Webhook-retry deduplication**, keyed on `(platform, order_id)`. Etsy and eBay both retry; a
  naive guard reads the retry as a second sale and sends Farid to cancel a *real* order.
- **Delist fan-out**, with a failed delist raised as its own alarm.
- **The Academy loop** (Farid's idea): every oversell becomes a lesson with evidence and a plain
  correction, and `review` reports the measured **median gap** — the real size of the open window.

**The finding that shapes everything: the oversell window cannot be closed to zero.** There is
always latency between a sale on one platform and the delisting on another; the best paid tools
advertise "within a minute". So the design is two layers — shrink the window, *and* alarm
instantly when one still slips. Do not design anything that promises zero oversells. The same
honesty law we apply to dating brackets applies to our own selling.

### If you are blocked on Etsy or eBay credentials — read this

At least three sessions are stuck asking Farid for API keys. **There is a path that needs none.**

| Way in | Keys | Risk | Verdict |
|---|---|---|---|
| Official API | eBay dev account; Etsy needs app approval | none | Best, but Etsy approval is the delay |
| Driving the site in a browser | none | eBay restricts automated tools; 2FA/captcha break it; a flagged account stops his shop | **No — not on the account his business runs on** |
| **Reading his own mailbox (IMAP)** | none | none | **Start here** |

eBay and Etsy email him the instant something sells. `guard/mailwatch.py` reads that mailbox and
turns those mails into claims — the whole alarm layer with zero credentials. It matches on the
**listing number**, never the pipe title.

**Status: unproven.** The mail patterns were written from published eBay/Etsy formats and have
**not** been checked against Farid's real mail. He was asked to run
`py -m guard.cli mail-test sale.eml` on one real sale email per platform. Until that passes, do
not describe mail detection as working. A mail it cannot read raises an alarm rather than
guessing a listing number.

## Two rules about where code lives

1. **Farid's system code never goes in this repo.** His words, 2026-08-06: *"everything i build
   will be local in my pc, nothing in repos."* This repo is public (confirmed). THE DESK and the
   inventory guard were both delivered to him as zips and removed from here. Design notes and
   questions go through `channel/`; code does not.
2. **Never commit the pipedia/pipephil mirrors or purchased scans.** Unchanged, absolute.

## Still open — do not assume answers

- **THE MONSTER.** Farid: *"check the monster, it is almost finished"* and *"he run the monster
  too"*. A cloud session cannot see his PC. Suspected to be the **Chronos-Pipe local AI hub** on
  the RTX 5070 (DINOv3 pipe identifier, gemma4 stamp reader, Command R dating) — his dashboard
  design names it — but **not confirmed. Ask him; do not assume.**
- **Where Etsy/eBay webhooks land.** His PC has no public address. Recommended: the Vercel front
  he already runs catches them and forwards over Tailscale. His call, not yet made.
- **His existing desktop dashboard** is a design preview only — the numbers on it are drawn in by
  hand, nothing is wired to anything.

## The full record

`channel/TO_FARID/003` (Helper design) · `005` (system code stays local) · `006` (inventory
guard, and the no-API-key path). `004` holds the build queue: the 50 new faridunhill listings,
then the monster, the Helper, the Hunter.
