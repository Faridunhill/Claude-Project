# The Marketing Agent — what it is, what you do, what it costs

**Status:** running. `python -m marketing.run daily` produces today's
videos, captions and post plan from the real 264-item catalog.

---

## 1. Why nothing ran for two months

The diagnosis is not "no experience" and not "missing tools". You built
almost the whole machine. P2.2–P2.8 are real, tested code: genome layer,
intake pipeline, QA gate, phenotype ledger, copy generators, social
engine, encyclopedia flywheel. 72 tests passed before this session.

Three things were missing, and all three were small:

| Missing | Effect |
|---|---|
| **Fuel line** | `get_source()` returned `PlaceholderSource`, which raises `NotConnected`. The engine had no data, because it was waiting on the PC-side `itemassets.db` that was never wired. |
| **Ignition key** | No runner. No single command. Every piece worked; nothing called them in order. |
| **A thing to look at** | No output a human could act on. Code that produces nothing you can open feels like it does not work. |

Meanwhile 264 real products with real prices and real photographs were
sitting in `content/products/*.yaml` the whole time — unused.

This session wired the catalog in as the fuel line, built the runner,
and made it write a plan you open on your phone.

---

## 2. The Pruna question — direct answer

You asked whether `playground.pruna.ai/p-image-ideogram` can make
videos for each listing and post to social media.

**No, on both counts.**

- **P-Image-Ideogram is a text-to-image model.** It makes still pictures
  from a written prompt. It has no video capability (Pruna sells a
  separate P-Video product) and no posting capability of any kind.
- Its actual strength is **typography** — rendering readable text inside
  an image. Roughly $0.003–$0.033 per image.

And there is a harder reason not to point it at your listings:

> **Generated imagery may never occupy a listing-image slot for a
> unique physical item.**

That is not my rule — it is the law already ratified in your own
`docs/marketing-dna-council-response-addendum-visual.md` (V1). It is
correct. You sell one-of-a-kind estate pieces where the buyer is buying
*that exact object*. An AI-generated picture of a pipe you are selling
is misrepresentation regardless of intent, and both Etsy and eBay treat
it as a policy violation. For your business this is the single worst
reputational accident available, and it is not recoverable.

**Where Pruna would actually be fine:** brand furniture that nobody can
mistake for the goods — an Etsy shop banner, a "New Arrivals" story
background, department header graphics. That is maybe 10–20 images,
once, for well under $1 total. Useful. Not a marketing engine.

**What actually makes a video for every listing:** ffmpeg, from your own
photographs, already built in `marketing/social/video.py`. £0 per video,
unlimited, and every frame is the real object.

---

## 3. The ad spend — the number worth checking this week

Your stated spend: **$25/day on Etsy Ads, weekends.**

| | |
|---|---|
| Per ad-day | ~£19–20 |
| Weekend days per month | ~8.7 |
| **Per month** | **~£165–175** |
| **Per year** | **~£2,000** |
| Your own ceiling in `control.yaml` | **£100/month** |

You are running at roughly **1.7–2× the wall you wrote for yourself.**
That file says machines never cross those numbers — but you set it, and
only you can change it. Right now the number and the behaviour disagree.

**The break-even test.** Your median item is £39. After the 15% Etsy fee
that is ~£33 gross. Take off what the piece cost you and call the margin
£18 on a typical sale. At ~£19.50 of ad spend per day:

> Etsy Ads must produce **at least one extra sale on every single
> ad-day** just to break even — before any profit at all.

This is checkable in two minutes: Etsy Ads dashboard → attributed orders
for the period, against spend for the same period. If attributed orders
are under one per ad-day, the ads are a subsidy, not marketing.

`python -m marketing.run doctor` flags this discrepancy every time you
run it, so it cannot quietly drift.

**The comparison that matters:** the social engine costs £0/month and
posts every day, including the five days a week your ads are off.

---

## 4. The single biggest lever you control

```
264/264 items have exactly ONE photograph.
```

This is the real bottleneck, and no tool fixes it:

- **Video**: one photo makes a slow zoom. Three or four make a real reel.
- **Etsy**: listings with several photographs convert materially better
  than single-photo listings. This lifts the ads you are already paying
  for — the same £19.50/day working harder.
- **Trust**: on estate goods, more angles is the whole sales argument.
  It is what "the photographs show the exact piece" means.

Three extra photos per item costs you minutes with a phone and a window.
It is worth more than any AI vendor you could buy this year.

---

## 5. Your routine — the actual answer to "lowest time and effort"

### Automated, 0 minutes
One scheduled job:

```bash
cd /path/to/Claude-Project && python -m marketing.run daily
```

Linux/Mac cron, 07:00 daily:
```
0 7 * * * cd /path/to/Claude-Project && /usr/bin/python3 -m marketing.run daily
```
Windows: Task Scheduler → daily 07:00 → same command.

Each run: picks the day's items, downloads and caches photos, renders
branded vertical videos, writes captions through the QA-gate lock,
auto-posts Tier 1, queues Tier 2, and writes the plan.

### You, ~2 minutes a day
Open `marketing/out/<today>/plan.md` on your phone. For each item: the
video path, and the caption in a copy block. Tap, paste, post. Done.

### You, ~20 minutes a week
Photograph new stock — **3–5 shots each**, not one. Voice-note what is
interesting about it. Run the intake pipeline (`marketing/INTAKE_GUIDE.md`).

### You, ~10 minutes a month
Run `python -m marketing.run doctor`. Check Etsy Ads attributed orders
against spend. Add any missing makers to `marketing/brands.yaml`.

**Total: about 10 minutes a day, most of it holding a camera.**

---

## 6. What the machine will not do, on purpose

These are walls, not gaps:

- **It never posts to your personal profile or to groups.** Those are
  Tier 2: the machine prepares the package, a human taps post. Automating
  them violates Meta's terms and risks the account that carries your
  audience.
- **It never posts more than once per day to any one group.**
- **On any Meta warning it pauses that channel and emails you once.** No
  silent retries.
- **It never asserts a maker it is not entitled to assert.** Brands come
  from `brands.yaml` matched against titles *you* wrote. Everything else
  stays quiet. A missing brand produces a plainer caption, never a guess.
- **It never says "circa 1955" from a title.** Title-derived dates are
  `basis: style`, which produces honest loose language ("mid-century").
- **It publishes nothing until you wire credentials.** Every run today is
  a dry run that still produces all the content, so you can read a month
  of output before a single post goes live.

---

## 7. Turning on live posting

Everything works in dry run now. When you want Tier 1 live:

1. Get a Meta Business page + Instagram Business account with API access.
2. Put the credentials in **environment variables on the PC** — never in
   this repo, never shared with another business (firewall, LAW 06).
3. Implement one class and return it from `get_publisher()` in
   `marketing/run.py`. That is the only line that changes.

Until then `DryRunPublisher` records what would have been posted.

---

## 8. Command reference

```bash
python -m marketing.run doctor          # readiness: what is ready, what needs you
python -m marketing.run daily           # today's content
python -m marketing.run daily --items 5 # more items this run
python -m marketing.run daily --date 2026-09-14
python -m marketing.run daily --no-download   # offline: captions + plan only
python -m pytest marketing/tests/ -q    # 123 tests
```

Outputs land in `marketing/out/`:

```
marketing/out/
  photos/                 photo cache (downloaded once, reused forever)
  rotation.db             which items have been posted, and when
  social.db               placements log + Tier 2 queue
  expression.db           every caption, versioned
  2026-09-12/
    plan.md               ← the only file you open
    render.sh             ffmpeg commands, if ffmpeg is not on this machine
    FH-TP-110-vertical.mp4
```

---

## 9. Tuning it

`marketing/control.yaml` — **only you edit this file.** The runner reads
these optional keys (add them if you want to change the defaults):

```yaml
social:
  daily_items: 3        # items per run
  cooldown_days: 45     # days before an item can appear again
  profile: true         # queue a personal-profile package
  groups:               # group targets for Tier 2 one-tap packages
    - "Pipe Collectors UK"
```

`marketing/brands.yaml` — the only names that may be read out of a title
and asserted as a maker. Add a line, and every future caption uses it.

---

## 10. Honest limits

- **ffmpeg is not installed here**, so this session could not render an
  actual .mp4. The commands are generated, shell-quoted and written to
  `render.sh`; install ffmpeg on the PC and they run. The video *logic*
  is tested; the rendered output has not been watched by anyone yet.
  **Watch the first one before scheduling the job.**
- **Etsy's CDN is blocked from this sandbox**, so no real photo was
  downloaded here. The cache is tested with an injected stub. It should
  work on your machine — verify with one run before trusting the cron.
- **Captions are template-built, not written.** They are honest and
  consistent, which is the right default for 264 items. They are not
  clever. Clever comes from `why_special`, which is what the voice-note
  intake exists to capture — and which is empty for the whole catalog
  today.
- **Nothing here fixes the photo problem.** See §4.
