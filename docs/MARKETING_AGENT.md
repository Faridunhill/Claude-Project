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

## 4. The single biggest lever: the photo vault

The web catalog carries **one thumbnail per item**. For FH-TP-110 that
thumbnail is the *closed case* — the pipes are never shown — so the reel
was a two-second zoom on a black rectangle. No overlay tuning fixes that.

But the real shoots are already on the PC: **135 photographs** for that
one Rattray's set, 32 pipes with folders, thousands more harvested. The
agent was reading the thin catalog while the rich library sat on the
same disk.

`vault-scan` bridges them:

```bash
python -m marketing.run vault-scan --vault "C:/Users/hadid/FaridOS/photo_vault"
```

Folder names are not SKUs, so it matches `_WRONG_SPLIT_rattrays_mega` to
"Rattray's Mary Sandblast Complete Set" by **rarity-weighted word
overlap**: shared words score by how rare they are across the catalog, so
"rattray" (one title) counts far more than "vintage" (sixty-six). Every
match reports the words that earned it.

**It proposes; you confirm.** The scan writes
`marketing/photo_map.proposed.yaml` with weak matches commented out. The
runner reads only `marketing/photo_map.yaml`, which you create by copying
across the entries you agree with. Same rule as the QA gate: the machine
never publishes its own guesses.

Confirmed mapping turns FH-TP-110 from a 2-second single-photo zoom into
a **5-photo, 10-second reel** — verified end to end.

For items with no vault folder, three extra photos with a phone and a
window is still the best hour you can spend. It lifts the reel *and* the
Etsy listing the ads are already paying for.

## 5. Your routine — the actual answer to "lowest time and effort"

### Automated, 0 minutes
One command writes the scheduler entry for this machine:

```bash
python -m marketing.run schedule --at 07:00
```

On Windows it writes a Task Scheduler XML and prints the single
`schtasks` line that registers it; elsewhere it prints the crontab line.
The task sets `StartWhenAvailable`, which matters more than the time
does: a PC that was switched off at 07:00 runs the job when it next
wakes instead of skipping the day silently.

Safe to schedule now — it stays in dry run until credentials are
configured, so you get a plan every morning and nothing posts.

Each run: picks the day's items, downloads and caches photos, renders
branded vertical videos, writes captions through the QA-gate lock,
auto-posts Tier 1, queues Tier 2, and writes the plan.

### You, ~2 minutes a day
Open `marketing/out/<today>/plan.md` on your phone. For each item: the
video path, and the caption in a copy block. Tap, paste, post. Done.

### When something sells — 0 extra minutes
Untick **In Stock** in the admin. That is the whole workflow. The next
run notices the change and:

- records the sale in the ledger (which is what makes "days to sale"
  computable, and eventually wakes the deferred pricing layer)
- writes a permanent `/archive/<slug>` page — the sold-price reference
  that keeps earning search traffic after the item is gone
- puts a "from the archive" post in your plan

The asking price is **not** published as the sold price by default: an
item that went for an accepted offer did not sell at it, and a sold-price
database is only an asset while the numbers in it are true. Set
`social.publish_sold_prices: true` in control.yaml if you want it.

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

## 7. Live posting — and why Facebook refuses while Instagram works

Live publishing is **built** (`marketing/social/meta.py`). Set four
environment variables and the runner switches from dry run to live by
itself — no code change:

```bash
META_ACCESS_TOKEN=...     # long-lived user token
META_PAGE_ID=...          # the Facebook Page id
META_IG_USER_ID=...       # optional - discovered from the Page
MEDIA_BASE_URL=...        # public url serving marketing/out/
```

Never in the repo, never shared with another business (LAW 06). With
nothing set, `get_publisher()` returns `DryRunPublisher`.

### Diagnosing Meta

```bash
python -m marketing.run meta-check
```

It reads `faridunhill/config/meta.json` for the ids automatically, so
nothing has to be retyped. **Never paste a token into a shell.** Point
`META_TOKEN_COMMAND` at a command that prints the secret from the DPAPI
vault and it is read directly:

```
META_TOKEN_COMMAND=<command that prints the token>
```

### What the PC run established

**Facebook is not a code problem.** `pages_manage_posts` is *not offered
by the app's use case at all*, so there was never a runtime error to
find — the permission was never grantable. Separately, `/me/accounts`
returns **no pages** despite `pages_show_list`, which means no Page token
can be minted, and a Page owned by a Business portfolio usually needs
`business_management` to be visible.

So there are two routes, and the cheap one is worth trying first:

1. **Turn on the Instagram account's "Share to Facebook" setting.** Meta
   then crossposts reels to the Page by itself — no API call, no app
   review, no code. Try this before anything else.
2. Change the app's use case and pass Meta review for
   `pages_manage_posts` + `business_management`. Slow, and only worth it
   if route 1 proves insufficient.

**⚠ The token expires around 2026-09-26.** Renew it with one command:

```bash
python -m marketing.run meta-renew      # needs META_APP_SECRET for one call
```

Meta extends a token that is *still valid* — it cannot revive an expired
one, which is why the warning has to arrive early.
 It is a ~60-day user token
connected 2026-07-29, and there is no never-expiring Page token behind
it — when it lapses, **Instagram stops too**. `meta-check` now reports
days remaining and fails below fourteen.

### Video hosting — already solved

Instagram does not accept file uploads; Meta fetches `video_url` itself.
The host already exists and is proven in production: **Cloudflare R2**
behind `https://photos.faridunhill.com`, bucket `pipe-archive`. The
runner uploads there automatically when configured:

```bash
R2_ENDPOINT_URL=...      R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=... MEDIA_BASE_URL=https://photos.faridunhill.com/marketing
```

Keys mirror the local layout, so `out/2026-09-12/FH-TP-110-vertical.mp4`
becomes `.../marketing/2026-09-12/FH-TP-110-vertical.mp4`. Don't stand up
a new host.



---

## 8. Command reference

```bash
python -m marketing.run doctor          # readiness: what is ready, what needs you
python -m marketing.run meta-check      # what the Meta token can actually do
python -m marketing.run vault-scan --vault <path>   # match items to photo folders
python -m marketing.run meta-renew      # extend the token ~60 more days
python -m marketing.run schedule        # write the daily scheduler entry
python -m marketing.run daily           # today's content
python -m marketing.run daily --items 5 # more items this run
python -m marketing.run daily --date 2026-09-14
python -m marketing.run daily --no-download   # offline: captions + plan only
python -m pytest marketing/tests/ -q    # 227 tests
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

- **The render was broken and is now fixed.** A 2-second clip was
  producing 100 seconds and 72 MB, because `zoompan` emits `d` frames for
  every frame it is fed and the input was looped. Verified against real
  ffmpeg: 100.00s before, 2.00s after, and 6.00s for a 3-photo reel.
  **Nobody has watched a finished video with overlays yet** — this
  sandbox has no `drawtext` filter. Watch one before scheduling the job.
- **ffmpeg 7.1 is already on the PC** at `FaridOS/voice/bin`, just not on
  PATH. The runner now finds it there; don't install a second copy.
- **The overlay font is now explicit.** The PC has no DejaVu, so ffmpeg
  was emitting a Fontconfig error and silently falling back. It now picks
  a real serif file and escapes Windows drive colons. Verify the text
  still looks right on the first render.
- **Meta is untested against the live API from here.** Every Meta and R2
  test uses an injected transport; this sandbox cannot reach either. The
  logic is exercised, the wire is not.
- **Vault matching is a guess and stays a proposal.** Four confident
  matches, zero false positives against the real catalog in testing — but
  read `photo_map.proposed.yaml` before copying anything across.
- **Captions are template-built, not written.** Honest and consistent,
  which is right for 264 items. Not clever. Clever comes from
  `why_special`, which the voice-note intake exists to capture and which
  is empty for the whole catalog today.
