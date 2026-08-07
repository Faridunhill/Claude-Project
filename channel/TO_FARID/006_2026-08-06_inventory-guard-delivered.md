# 006 — The oversell problem: solved core, delivered as a local drop

**Farid, 2026-08-06:** *"we still have inventories problem, this week two pipes sold min two
platform, Claude so far didn't solve it... my helper he has to solve this store management
issue, also responsible for marketing, means he run the monster too, he will use academy."*

Built and handed to him as a zip (not committed — see `005`). Cloud sessions: **the code is on
his PC, not here.** Ask him for it before rebuilding it.

## The finding that shaped it

**The oversell window cannot be closed to zero.** Between a sale on one platform and the
delisting on another there is always latency. The best paid tools on the market advertise
"within a minute", and a minute is enough for a second buyer. Any design promising zero
oversells is dishonest — the same law we apply to dating brackets applies to our own selling.

So it is built in two layers: shrink the window (delist on the sale event, not on a timer), and
**alarm instantly when one still slips** so he cancels in minutes instead of finding out Friday.
Layer 2 is what was missing and why this week hurt.

## What was built

Three channels confirmed: **his own site** (Stripe — `app/api/webhook/route.ts` already catches
`checkout.session.completed`), **Etsy**, **eBay**.

- **The atomic claim.** `UPDATE stock SET state='sold' WHERE sku=? AND state='available'` —
  one row changed means you won the pipe, zero means you are the double sale. Proven with an
  eight-thread simultaneous race; exactly one winner.
- **Webhook-retry deduplication.** Etsy and eBay both retry. A naive guard reads the retry as a
  second sale and sends him to cancel a real order. Claims are keyed on `(platform, order_id)`.
- **Delist fan-out** to every other platform, with a failed delist raised as its own alarm — a
  sold pipe still live is the next oversell already in motion.
- **The Academy loop, his idea:** every oversell and every failed delist becomes a lesson with
  evidence and a plain correction. `review` reports the measured **median gap** — the real size
  of the open window, and the scoreboard for whether the Helper is improving.
- **ntfy alarms**, standard library only.

**Tested: 7 tests, all passing.** Atomic claim, race, alarm contents, retry dedup, fan-out,
failed delist, unwired adapter, exposure list.

**Not tested, and cannot be from the cloud:** the Etsy / eBay / site adapters — no credentials
here. They raise `NotWiredYet` rather than quietly doing nothing, so nothing can look like it
worked when it did not. **First job on his PC.**

## Follow-up: "can he access my ebay? it will solve the api key for awhile"

Farid asked whether the Helper can reach eBay without API keys. Answer built and shipped in the
same drop — `guard/mailwatch.py`, 7 more tests, 14 total.

**Three doors, deliberately ranked:**

1. **Official API** — best, but Etsy requires app approval, which is the delay he is trying to
   route around.
2. **Driving the website in a browser** — no keys, but eBay restricts automated tools, 2FA and
   captchas break it, and a flagged account stops his shop. **Recommended against, firmly.**
   This is the account his business runs on; it is not the place to be clever.
3. **Reading his own mailbox over IMAP** — eBay and Etsy email him the instant something sells.
   No keys, no developer account, nothing that can get a selling account flagged. **This is the
   answer, and it works tonight.**

It gets the whole alarm layer with zero credentials — the double sale is still caught in
seconds. Delisting the other listing still needs the API or the bought tool. Knowing instantly
is the half that was missing.

Matches on the **listing number**, never the pipe title (titles get edited and truncated in
mail; numbers do not). A newsletter mentioning an item number is not a sale — there is a test,
because misreading one would delist a pipe still for sale.

**Open, and it needs Farid:** the email patterns were written from published eBay/Etsy formats
and are **unverified against his real mail** — this container has none of it. He was asked to
save one real sale email per platform and run `py -m guard.cli mail-test sale.eml`, which prints
exactly what was extracted. Until that passes, treat mail detection as unproven. A mail it
cannot read raises an alarm rather than guessing a listing number.

## Two things still open

1. **Where webhooks land.** Etsy and eBay push to a public HTTPS address; his PC has none.
   Recommended: the Vercel front he already runs catches them and forwards over Tailscale.
   Alternative: Tailscale Funnel. His call.
2. **Buy something this week.** Vendoo / List Perfectly / Crosslist already do eBay+Etsy
   auto-delist. Recommended he buys one now to stop the bleeding while the adapters are wired
   and proven — then keep whichever wins on the measured median gap.

## Still unanswered

**THE MONSTER** — he said "check the monster, it is almost finished" and "he run the monster
too". A cloud session cannot see his PC. He was asked for a screenshot, a folder listing, or a
local session report. Suspected to be the Chronos-Pipe local AI hub on the RTX 5070, but
**not confirmed — do not assume.**

The Helper's job list grew today: store management + marketing + running the monster, on top of
`003`. Update `003` when he confirms the monster.

— your agent
