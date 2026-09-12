"""THE RUNNER — one command that turns the catalog into today's posts.

    python -m marketing.run doctor     # what is ready, what is missing
    python -m marketing.run daily      # produce today's content

Everything under `marketing/` was built and tested by P2.2-P2.8, but
nothing connected the pieces, so the system never actually ran. This
module is the ignition key. Per run it:

  1. reads the standing walls (`control.yaml`) BEFORE doing anything
  2. loads the real catalog (`content/products/*.yaml`)
  3. picks today's items by rotation (never-posted first, then cooldown)
  4. caches each photo locally so ffmpeg can use it
  5. builds the branded video (renders when ffmpeg is present, otherwise
     writes the exact commands to `render.sh` for the PC)
  6. generates captions through the QA-gate lock, versioned in the
     expression store
  7. queues Tier-2 one-tap packages and publishes Tier-1 (page/IG)
  8. writes `plan.md` — the phone sheet: open it, tap, post, done

Safety posture: publishing defaults to DRY RUN. Nothing reaches Meta
until real credentials are wired into `get_publisher()` deliberately.
A dry run still produces every video, caption and plan, so the whole
system can be trusted before it is ever pointed at a live account.
"""

from __future__ import annotations

import argparse
import os

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import yaml

from .catalog import load_catalog
from .expression.copy import GENERATOR_VERSION, generate_title
from .flywheel import record_listed, turn as flywheel_turn
from .expression.store import ExpressionRecord, ExpressionStore, inputs_hash
from .media import fetch_all
from .social.meta import find_meta_json, load_meta_json
from .photovault import load_photo_map, photos_for, propose, scan_vault, write_proposal
from .rotation import Candidate, Rotation
from .storage import get_uploader, key_for
from .social.captions import (
    CAPTION_GENERATOR_VERSION,
    _subject_from_catalog_name,
    generate_caption,
)
from .social.publisher import (
    ChannelPaused,
    DryRunPublisher,
    FrequencyWall,
    PostRequest,
    SocialEngine,
    Tier1Publisher,
)
from .social.video import VideoSpec, build_video, load_style

RUNNER_VERSION = "runner-1.0.0"

ROOT = Path(__file__).resolve().parent.parent
MARKETING = ROOT / "marketing"
DEFAULTS = {
    "products_dir": ROOT / "content" / "products",
    "brands": MARKETING / "brands.yaml",
    "control": MARKETING / "control.yaml",
    "style": MARKETING / "social" / "style_faridunhill.yaml",
    "photo_map": MARKETING / "photo_map.yaml",
    "out": MARKETING / "out",
}


# ── configuration ────────────────────────────────────────────────────

def load_control(path: str | Path) -> dict:
    """The standing walls. Read before spending, pricing or posting.

    Optional keys the runner understands (add them to control.yaml
    yourself; the runner never writes to that file):

        social.daily_items      how many items per run   (default 3)
        social.cooldown_days    days before a repeat     (default 45)
        social.groups           group targets for Tier 2 (default none)
        social.profile          include personal profile (default true)
    """
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def get_publisher(out_root: Optional[Path] = None) -> Tier1Publisher:
    """Live Meta publisher when the environment supplies credentials,
    DryRunPublisher otherwise.

    Credentials are read from env vars only — never the repo, never
    shared across businesses (LAW 06). With nothing set, every run is a
    dry run that still produces all the content, so the system can be
    trusted before it is ever pointed at a live account.
    """
    from .social.meta import MetaConfig, MetaPublisher

    config = MetaConfig.from_env_or_none()
    if config is None:
        return DryRunPublisher()
    return MetaPublisher(config, out_root or DEFAULTS["out"])


# ── the daily run ────────────────────────────────────────────────────

class RunResult:
    def __init__(self, run_date: date, out_dir: Path):
        self.run_date = run_date
        self.out_dir = out_dir
        self.items: list[dict] = []
        self.skipped: list[dict] = []
        self.warnings: list[str] = []
        self.sold: list = []
        self.rendered = 0

    @property
    def ok(self) -> bool:
        return bool(self.items)


def run_daily(
    run_date: Optional[date] = None,
    items_wanted: Optional[int] = None,
    download: bool = True,
    products_dir: Optional[Path] = None,
    out_root: Optional[Path] = None,
    control_path: Optional[Path] = None,
    brands_path: Optional[Path] = None,
    style_path: Optional[Path] = None,
    publisher: Optional[Tier1Publisher] = None,
    downloader=None,
) -> RunResult:
    run_date = run_date or date.today()
    products_dir = Path(products_dir or DEFAULTS["products_dir"])
    out_root = Path(out_root or DEFAULTS["out"])
    control = load_control(control_path or DEFAULTS["control"])
    brands_path = Path(brands_path or DEFAULTS["brands"])
    style = load_style(style_path or DEFAULTS["style"])

    social_cfg = control.get("social") or {}
    count = items_wanted if items_wanted is not None else int(social_cfg.get("daily_items", 3))
    cooldown = int(social_cfg.get("cooldown_days", 45))
    group_wall = int(social_cfg.get("max_posts_per_group_per_day", 1))
    groups = [str(g) for g in (social_cfg.get("groups") or [])]
    want_profile = bool(social_cfg.get("profile", True))
    max_photos = int(social_cfg.get("max_photos_per_video", 5))

    # Confirmed vault mapping, if a human has reviewed one. Local photo
    # sets beat the single catalog thumbnail and need no download.
    photo_map = load_photo_map(DEFAULTS["photo_map"])

    # Present only when R2 is configured; without it Tier 1 has no url
    # to hand Meta and the run prepares rather than publishes.
    uploader = get_uploader()

    day_dir = out_root / run_date.isoformat()
    day_dir.mkdir(parents=True, exist_ok=True)
    photo_cache = out_root / "photos"

    result = RunResult(run_date, day_dir)

    catalog = load_catalog(products_dir, brands_path)
    if not catalog:
        result.warnings.append(f"No products found in {products_dir}")
        return result

    # The flywheel turns first: an item marked sold in the admin becomes a
    # permanent archive page and a "from the archive" post, and the SOLD
    # event lands in the ledger. Running it before selection also means a
    # just-sold item is never chosen to be advertised as available.
    archive_dir = Path(products_dir).parent / "archive"
    sold, sold_warnings = flywheel_turn(
        catalog, out_root, archive_dir,
        show_price=bool(social_cfg.get("publish_sold_prices", False)),
    )
    result.warnings.extend(sold_warnings)
    result.sold = sold

    rotation = Rotation(out_root / "rotation.db", cooldown_days=cooldown)
    engine = SocialEngine(
        out_root / "social.db", publisher or get_publisher(out_root),
        max_posts_per_group_per_day=group_wall,
    )
    expression = ExpressionStore(out_root / "expression.db")

    by_sku = {item.sku: item for item in catalog}
    candidates = [
        Candidate(
            sku=item.sku,
            price=item.price or 0.0,
            has_photo=item.image_count > 0 or item.sku in photo_map,
            in_stock=item.effective.get("in_stock", True),
            added=item.added,
        )
        for item in catalog
    ]
    selected = rotation.select(candidates, run_date, count)

    if not selected:
        result.warnings.append(
            f"Every eligible item is inside its {cooldown}-day cooldown. "
            "Nothing to post today — that is the wall working, not a failure."
        )

    render_commands: list[list[str]] = []

    for sku in selected:
        item = by_sku[sku]
        effective = item.effective

        # The vault wins when it has this item: real shoots, already
        # local, several angles instead of one thumbnail.
        photos = photos_for(sku, photo_map, limit=max_photos)
        photo_source = "vault" if photos else "catalog"

        if not photos:
            urls = [m["url"] for m in effective.get("media", [])]
            fetched = fetch_all(urls, photo_cache, downloader) if download else []
            photos = [f.path for f in fetched if f.ok]
            if download and urls and not photos:
                errors = "; ".join(f.error or "?" for f in fetched) or "no photos"
                result.skipped.append({
                    "sku": sku, "name": item.name,
                    "reason": f"photos unavailable ({errors})",
                })
                continue

        # -- caption (through the QA-gate lock, versioned) -------------
        caption = generate_caption(effective, kind="new_arrival")
        expression.put(ExpressionRecord(
            sku=sku, kind="caption", channel="social", text=caption.full(),
            generator_version=CAPTION_GENERATOR_VERSION,
            inputs_hash=inputs_hash(effective),
        ))
        expression.put(ExpressionRecord(
            sku=sku, kind="title", channel="core", text=generate_title(effective),
            generator_version=GENERATOR_VERSION, inputs_hash=inputs_hash(effective),
        ))

        # -- video ------------------------------------------------------
        overlay = _subject_from_catalog_name(item.name, max_len=90)
        video_path = ""
        video_note = ""
        if photos:
            spec = VideoSpec(sku=sku, photos=photos, title_overlay=_ffmpeg_safe(overlay), fmt="vertical")
            try:
                video = build_video(spec, style, day_dir)
            except Exception as exc:
                # A corrupt or truncated photo makes ffmpeg exit non-zero.
                # That must cost one item, not the whole night's run: the
                # caption is already written and the rest still go out.
                detail = getattr(exc, "stderr", b"") or b""
                tail = detail.decode("utf-8", "replace").strip().splitlines()[-1:] or [str(exc)]
                result.warnings.append(f"{sku}: video render failed - {tail[0][:200]}")
                video_note = "render failed - caption only"
                video = None

            if video is not None:
                video_path = video.output_path
                if video.rendered:
                    result.rendered += 1
                else:
                    render_commands.append(video.command)
                    video_note = "queued for render (ffmpeg not on this machine)"
        else:
            # --no-download (offline preview) or a photo-less item:
            # captions and the plan still get produced.
            video_note = "no local photo - caption only"

        # -- host the video so Meta can fetch it -------------------------
        # Instagram does not accept uploads: it fetches `video_url`
        # itself, so an unhosted render can be prepared but never posted.
        public_video = video_path
        if uploader and video_path and Path(video_path).exists():
            upload = uploader.upload(video_path, key_for(video_path, out_root))
            if upload.ok:
                public_video = upload.url
            else:
                result.warnings.append(
                    f"{sku}: upload failed ({upload.error}); Tier 1 cannot post "
                    "an unhosted video, but the package is still queued."
                )

        # -- publish / queue --------------------------------------------
        placements: list[str] = []
        queued: list[str] = []
        for target in ("page", "ig"):
            request = PostRequest(sku=sku, target=target, video_path=public_video,
                                  caption=caption.full())
            try:
                placements.append(f"{target}: {engine.publish_tier1(request)}")
            except ChannelPaused as exc:
                result.warnings.append(f"{sku}: {exc}")
            except Exception as exc:                       # never abort the run
                result.warnings.append(f"{sku} {target}: {type(exc).__name__}: {exc}")

        tier2_targets = ([f"group:{g}" for g in groups] + (["profile"] if want_profile else []))
        for target in tier2_targets:
            request = PostRequest(sku=sku, target=target, video_path=video_path, caption=caption.full())
            try:
                queued.append(f"{target} (#{engine.queue_tier2(request)})")
            except FrequencyWall as exc:
                result.warnings.append(f"{sku}: {exc}")
            except ChannelPaused as exc:
                result.warnings.append(f"{sku}: {exc}")

        result.items.append({
            "sku": sku,
            "name": item.name,
            "price": item.price,
            "taxonomy": effective.get("taxonomy"),
            "brand": effective.get("brand"),
            "photo_count": len(photos) or item.image_count,
            "photo_source": photo_source,
            "video_path": video_path,
            "video_note": video_note,
            "caption": caption.full(),
            "placements": placements,
            "queued": queued,
            "source_path": item.source_path,
        })

    if result.items:
        rotation.record([i["sku"] for i in result.items], run_date)
        # Without this the ledger stays empty and days-to-sale can never
        # be computed for anything.
        record_listed(result.items, out_root)

    if render_commands:
        _write_render_script(day_dir / "render.sh", render_commands)

    _write_plan(result, day_dir / "plan.md", rotation, len(catalog))

    rotation.close()
    engine.close()
    expression.close()
    return result


def _ffmpeg_safe(text: str) -> str:
    """Make text safe for a drawtext filter argument.

    A straight apostrophe cannot be quoted cleanly inside a filtergraph,
    but deleting it turns "Rattray's" into "Rattrays" on a brand name.
    The typographic apostrophe avoids the quoting problem entirely and
    is what the name should look like anyway.
    """
    text = text.replace("'", "\u2019")
    for char, repl in (("\\", ""), (":", " -"), ("%", " pct")):
        text = text.replace(char, repl)
    return text


def _write_render_script(path: Path, commands: list[list[str]]) -> None:
    import shlex
    lines = [
        "#!/usr/bin/env bash",
        "# Videos for today. Run this on the PC where ffmpeg lives.",
        "set -euo pipefail",
        "",
    ]
    lines += [" ".join(shlex.quote(part) for part in cmd) for cmd in commands]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)


def _write_plan(result: RunResult, path: Path, rotation: Rotation, catalog_size: int) -> None:
    """The phone sheet. This is the ONLY file Farid needs to open."""
    done = rotation.posted_count()
    lines = [
        f"# Post plan - {result.run_date.isoformat()}",
        "",
        f"**{len(result.items)} item(s) ready.** Catalog covered: {done}/{catalog_size}.",
        "",
        "How to use this: for each item below, open the video, copy the",
        "caption, post. Tier 1 (page/IG) is already handled automatically",
        "unless it says DRY RUN.",
        "",
    ]

    if result.rendered:
        lines += [f"Videos rendered here: `{result.out_dir}`", ""]
    elif (result.out_dir / "render.sh").exists():
        lines += [
            "ffmpeg is not on this machine, so videos were not rendered.",
            f"Run `bash {result.out_dir / 'render.sh'}` on the PC to produce them.",
            "",
        ]

    for i, item in enumerate(result.items, 1):
        price = f"GBP {item['price']:.2f}" if item["price"] is not None else "price not set"
        lines += [
            "---",
            "",
            f"## {i}. {item['name']}",
            "",
            f"`{item['sku']}` - {price} - {item['taxonomy']}"
            + (f" - brand: {item['brand']}" if item["brand"] else " - brand not asserted"),
            "",
        ]
        if item["video_path"]:
            lines += [f"**Video:** `{item['video_path']}`"
                      + (f" _({item['video_note']})_" if item["video_note"] else ""), ""]
        elif item["video_note"]:
            lines += [f"**Video:** {item['video_note']}", ""]

        if item["photo_count"] <= 1:
            lines += [
                "> Only 1 photo, from the web catalog. The video is a single slow",
                "> zoom. If this item has a real photo folder on the PC, map it:",
                "> `python -m marketing.run vault-scan --vault <path>`.",
                "",
            ]
        elif item.get("photo_source") == "vault":
            lines += [f"_{item['photo_count']} photos from the vault._", ""]

        lines += ["**Caption - copy from here:**", "", "```", item["caption"], "```", ""]
        if item["placements"]:
            lines += ["Auto-posted: " + ", ".join(item["placements"]), ""]
        if item["queued"]:
            lines += ["Waiting for your tap: " + ", ".join(item["queued"]), ""]

    if result.sold:
        lines += ["---", "", "## Sold - archive pages created", ""]
        for item in result.sold:
            lines += [
                f"### {item.name[:70]}",
                "",
                f"`{item.sku}` - permanent page: `{item.archive_path}`",
                "",
                "**Archive post - copy from here:**",
                "", "```", item.caption, "```", "",
            ]

    if result.skipped:
        lines += ["---", "", "## Skipped", ""]
        lines += [f"- `{s['sku']}` {s['name'][:50]} - {s['reason']}" for s in result.skipped]
        lines += [""]

    if result.warnings:
        lines += ["---", "", "## Warnings", ""]
        lines += [f"- {w}" for w in result.warnings]
        lines += [""]

    lines += ["---", "", f"_{RUNNER_VERSION} - generated {datetime.now().isoformat(timespec='seconds')}_"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── doctor ───────────────────────────────────────────────────────────

def run_doctor(
    products_dir: Optional[Path] = None,
    out_root: Optional[Path] = None,
    control_path: Optional[Path] = None,
    brands_path: Optional[Path] = None,
) -> list[tuple[str, str, str]]:
    """Readiness report: (status, subject, detail). Status is OK, WARN
    or TODO — TODO means it needs Farid, not the machine."""
    products_dir = Path(products_dir or DEFAULTS["products_dir"])
    out_root = Path(out_root or DEFAULTS["out"])
    brands_path = Path(brands_path or DEFAULTS["brands"])
    control_path = Path(control_path or DEFAULTS["control"])

    checks: list[tuple[str, str, str]] = []

    catalog = load_catalog(products_dir, brands_path)
    checks.append(("OK" if catalog else "TODO", "Catalog",
                   f"{len(catalog)} items loaded from {products_dir}"))

    if catalog:
        one_photo = sum(1 for i in catalog if i.image_count <= 1)
        branded = sum(1 for i in catalog if i.effective.get("brand"))
        checks.append((
            "WARN" if one_photo > len(catalog) / 2 else "OK",
            "Photos per item",
            f"{one_photo}/{len(catalog)} items have only 1 photo. "
            "More photos = better video and better listing conversion. "
            "This is the single biggest lever you control.",
        ))
        checks.append((
            "WARN" if branded < len(catalog) / 3 else "OK",
            "Brand coverage",
            f"{branded}/{len(catalog)} titles name an allowlisted brand. "
            f"Add missing makers to {brands_path.name} to sharpen captions.",
        ))

    from .social.video import resolve_ffmpeg, resolve_font

    binary = resolve_ffmpeg()
    checks.append((
        "OK" if binary else "TODO",
        "ffmpeg",
        f"found at {binary} - videos render here" if binary
        else "not found on PATH or in the known install locations. Videos "
             "are written to render.sh instead. Set FFMPEG_BINARY to point "
             "at an existing copy rather than installing a second one.",
    ))

    try:
        font = resolve_font(load_style(DEFAULTS["style"]))
        checks.append((
            "OK" if font else "WARN",
            "Overlay font",
            f"{font}" if font
            else "No font file found, so drawtext falls back to a system "
                 "default. That emits a Fontconfig warning and can fail "
                 "outright on another machine. Set overlay.font_file in "
                 "style_faridunhill.yaml.",
        ))
    except OSError:
        pass

    try:
        control = load_control(control_path)
        promo = control.get("promotion") or {}
        checks.append(("OK", "Standing walls", f"loaded from {control_path.name}"))
        ceiling = promo.get("monthly_ceiling")
        if ceiling is not None:
            checks.append((
                "WARN", "Ad ceiling",
                f"control.yaml caps promotion at GBP {ceiling}/month. "
                "Etsy Ads at $25/day on weekends is roughly 2x that. "
                "Either raise the number deliberately or cut the spend.",
            ))
    except OSError as exc:
        checks.append(("TODO", "Standing walls", f"cannot read control.yaml: {exc}"))

    from .storage import get_uploader as _get_uploader

    uploader = _get_uploader()
    checks.append((
        "OK" if uploader else "WARN",
        "Video hosting",
        "R2 configured - rendered videos are uploaded automatically"
        if uploader else
        "R2 is NOT configured, so nothing can be posted to Instagram: Meta "
        "fetches the video from a url rather than accepting an upload. Set "
        "R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY and "
        "MEDIA_BASE_URL (the bucket behind photos.faridunhill.com already "
        "works - point at it rather than standing up a new host).",
    ))

    publisher = get_publisher(out_root)
    checks.append((
        "WARN" if isinstance(publisher, DryRunPublisher) else "OK",
        "Publishing",
        "DRY RUN - content is produced but nothing is posted. Wire real "
        "credentials in run.get_publisher() when you are ready."
        if isinstance(publisher, DryRunPublisher) else "live publisher configured",
    ))

    rotation_db = out_root / "rotation.db"
    if rotation_db.exists():
        rotation = Rotation(rotation_db)
        checks.append(("OK", "Rotation", f"{rotation.posted_count()} items covered so far"))
        rotation.close()
    else:
        checks.append(("OK", "Rotation", "no history yet - first run starts the backlog"))

    return checks


# ── preview ──────────────────────────────────────────────────────────

def _preview(sku: Optional[str]) -> int:
    """Render one video on demand, for a human to look at.

    `daily` is deliberately hard to repeat: once an item is posted it
    sits in a 45-day cooldown, so re-running it produces nothing and
    there is no new video to judge. That is right for the feed and
    useless for "show me what this looks like". This command ignores
    rotation entirely, records nothing, and posts nothing.
    """
    from .social.video import VideoSpec, build_video, load_style, resolve_ffmpeg

    out_root = DEFAULTS["out"]
    preview_dir = out_root / "preview"
    catalog = load_catalog(DEFAULTS["products_dir"], DEFAULTS["brands"])
    if not catalog:
        print(f"\n  No products found in {DEFAULTS['products_dir']}\n")
        return 1

    if sku:
        chosen = next((i for i in catalog if i.sku.lower() == sku.lower()), None)
        if chosen is None:
            print(f"\n  No item with SKU {sku!r}. Try `doctor` to confirm the catalog.\n")
            return 1
    else:
        # The dearest item with photographs: the one most worth judging.
        usable = [i for i in catalog if i.image_count or i.sku in
                  load_photo_map(DEFAULTS["photo_map"])]
        if not usable:
            print("\n  No item in the catalog has a photo.\n")
            return 1
        chosen = max(usable, key=lambda i: i.price or 0)

    print(f"\n  {chosen.sku}  {chosen.name[:60]}")

    photos = photos_for(chosen.sku, load_photo_map(DEFAULTS["photo_map"]), limit=5)
    if photos:
        print(f"  {len(photos)} photos from the vault")
    else:
        urls = [m["url"] for m in chosen.effective.get("media", [])]
        fetched = fetch_all(urls, out_root / "photos")
        photos = [f.path for f in fetched if f.ok]
        if not photos:
            errors = "; ".join(f.error or "?" for f in fetched) or "no photos"
            print(f"\n  Could not get a photo: {errors}\n")
            return 1
        print(f"  {len(photos)} photo(s) from the catalog")

    binary = resolve_ffmpeg()
    if not binary:
        print("\n  ffmpeg not found, so nothing can be rendered here.")
        print("  Set FFMPEG_BINARY to an existing copy, e.g.")
        print("    FFMPEG_BINARY=C:/Users/hadid/FaridOS/voice/bin/ffmpeg.exe\n")
        return 1
    print(f"  ffmpeg: {binary}")

    style = load_style(DEFAULTS["style"])
    spec = VideoSpec(sku=chosen.sku, photos=photos,
                     title_overlay=_ffmpeg_safe(
                         _subject_from_catalog_name(chosen.name, max_len=90)),
                     fmt="vertical")
    try:
        video = build_video(spec, style, preview_dir)
    except Exception as exc:
        print(f"\n  Render FAILED: {type(exc).__name__}: {exc}")
        stderr = getattr(exc, "stderr", b"")
        if stderr:
            print("\n" + stderr.decode("utf-8", "replace")[-1500:])
        print()
        return 1

    seconds = len(photos) * float(style["motion"]["seconds_per_photo"])
    size = Path(video.output_path).stat().st_size if Path(video.output_path).exists() else 0
    print(f"\n  VIDEO: {video.output_path}")
    print(f"  {seconds:.0f} seconds, {size / 1_000_000:.1f} MB, {len(photos)} photo(s)")
    print("\n  Open it and look. Nothing was posted and nothing was recorded,")
    print("  so you can run this as many times as you like.\n")
    return 0


# ── scheduling ───────────────────────────────────────────────────────

_TASK_XML = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Faridunhill marketing agent - daily videos, captions and post plan.</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T{time}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python}</Command>
      <Arguments>-m marketing.run daily</Arguments>
      <WorkingDirectory>{cwd}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""


def _write_schedule(at: str) -> int:
    """Write the scheduler entry for this machine.

    StartWhenAvailable matters more than the time does: a PC that was
    off at 07:00 runs the job when it next wakes, instead of skipping
    the day silently.
    """
    try:
        hour, minute = (int(part) for part in at.split(":", 1))
        assert 0 <= hour < 24 and 0 <= minute < 60
    except (ValueError, AssertionError):
        print(f"\n  --at must be HH:MM, not {at!r}\n")
        return 1

    time_str = f"{hour:02d}:{minute:02d}"
    python = sys.executable
    cwd = str(ROOT)

    if os.name == "nt":
        path = ROOT / "marketing" / "faridunhill-marketing.xml"
        path.write_text(
            _TASK_XML.format(time=time_str, python=python, cwd=cwd),
            encoding="utf-16",
        )
        print(f"\n  Written: {path}\n")
        print("  Register it (one command, in an admin terminal):\n")
        print(f'    schtasks /Create /TN "Faridunhill Marketing" /XML "{path}" /F\n')
        print("  Check it:   schtasks /Query /TN \"Faridunhill Marketing\"")
        print("  Run it now: schtasks /Run /TN \"Faridunhill Marketing\"")
        print("  Remove it:  schtasks /Delete /TN \"Faridunhill Marketing\" /F\n")
    else:
        line = f"{minute} {hour} * * * cd {cwd} && {python} -m marketing.run daily"
        print("\n  Add this line to your crontab (`crontab -e`):\n")
        print(f"    {line}\n")

    print("  It runs in DRY RUN until credentials are configured, so scheduling")
    print("  it now is safe - you get a plan every morning and nothing posts.\n")
    return 0


# ── cli ──────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m marketing.run", description=__doc__)
    sub = parser.add_subparsers(dest="command")

    daily = sub.add_parser("daily", help="produce today's content")
    daily.add_argument("--items", type=int, default=None, help="how many items (default: control.yaml)")
    daily.add_argument("--date", default=None, help="run date YYYY-MM-DD (default: today)")
    daily.add_argument("--no-download", action="store_true", help="skip photo download")

    sub.add_parser("doctor", help="report what is ready and what is missing")

    preview = sub.add_parser(
        "preview",
        help="render ONE video now so you can look at it (ignores rotation, posts nothing)",
    )
    preview.add_argument("--sku", default=None, help="which item (default: best candidate)")
    sub.add_parser("meta-check", help="ask the Graph API what the token can actually do")
    sub.add_parser("meta-renew", help="exchange the current token for a fresh ~60-day one")

    schedule = sub.add_parser(
        "schedule", help="write the scheduler entry that runs this daily")
    schedule.add_argument("--at", default="07:00", help="local time, HH:MM (default 07:00)")

    vault = sub.add_parser(
        "vault-scan",
        help="match catalog items to photo folders on this PC (proposes, never applies)",
    )
    vault.add_argument("--vault", required=True, help="root of the photo library")
    vault.add_argument("--min-photos", type=int, default=2,
                       help="ignore folders with fewer photos (default 2)")

    args = parser.parse_args(argv)
    command = args.command or "doctor"

    if command == "doctor":
        print("\nFARIDUNHILL MARKETING - readiness\n")
        for status, subject, detail in run_doctor():
            print(f"  [{status:4}] {subject}")
            print(f"         {detail}\n")
        return 0

    if command == "vault-scan":
        try:
            folders = scan_vault(args.vault, min_photos=args.min_photos)
        except FileNotFoundError as exc:
            print(f"\n  {exc}\n")
            return 1

        catalog = load_catalog(DEFAULTS["products_dir"], DEFAULTS["brands"])
        matches = propose(catalog, folders)
        confident = [m for m in matches if m.confident]
        weak = [m for m in matches if m.folder and not m.confident]

        proposal = MARKETING / "photo_map.proposed.yaml"
        write_proposal(matches, proposal)

        photos = sum(m.folder.photo_count for m in confident)
        print(f"\nVAULT SCAN - {args.vault}\n")
        print(f"  {len(folders)} folders with >= {args.min_photos} photos")
        print(f"  {len(confident)} confident matches ({photos} photographs)")
        print(f"  {len(weak)} weak matches (listed, commented out)")
        print(f"  {len(matches) - len(confident) - len(weak)} items matched nothing\n")

        for match in confident[:15]:
            print(f"  {match.sku:12} {match.name[:44]:46} {match.folder.photo_count:>4} photos")
            print(f"  {'':12} via {', '.join(match.evidence)}  (score {match.score:.1f})")
        if len(confident) > 15:
            print(f"  ... and {len(confident) - 15} more\n")

        print(f"\nWritten: {proposal}")
        print("Nothing is live yet. Review it, then copy the entries you agree")
        print(f"with into {DEFAULTS['photo_map']} - that is the file the runner reads.\n")
        return 0

    if command == "preview":
        return _preview(args.sku)

    if command == "schedule":
        return _write_schedule(args.at)

    if command == "meta-renew":
        import os

        from .social.meta import MetaClient, MetaConfig, MetaError, NotConfigured

        try:
            config = MetaConfig.from_env()
        except NotConfigured as exc:
            print(f"\n  {exc}\n")
            return 1

        meta = load_meta_json(find_meta_json(os.environ.get("META_CONFIG_FILE")))
        app_id = (os.environ.get("META_APP_ID") or meta.get("app_id") or "").strip()
        app_secret = (os.environ.get("META_APP_SECRET") or "").strip()
        if not app_id or not app_secret:
            print("\n  Renewal needs the app id and secret.")
            print(f"  app id:     {'found: ' + app_id if app_id else 'MISSING - set META_APP_ID'}")
            print("  app secret: " + ("found" if app_secret else
                                      "MISSING - set META_APP_SECRET"))
            print("\n  The secret is in the Meta app dashboard under Settings > Basic.")
            print("  Set it for one command only; it is never written to the repo.\n")
            return 1

        client = MetaClient(config)
        try:
            fresh = client.exchange_for_long_lived(app_id, app_secret)
        except MetaError as exc:
            print(f"\n  Renewal FAILED: {exc}")
            print("  Meta extends a token that is still valid; it cannot revive an")
            print("  expired one. If it has lapsed, reconnect the account instead.\n")
            return 1

        token = fresh.get("access_token", "")
        expires_in = int(fresh.get("expires_in") or 0)
        if not token:
            print(f"\n  Meta returned no token: {fresh}\n")
            return 1

        print("\n  NEW TOKEN OBTAINED"
              + (f" - valid about {expires_in // 86400} days.\n" if expires_in else ".\n"))
        print("  It is NOT printed here and NOT written to the repo. Store it in")
        print("  the vault the same way as the current one, then confirm with:")
        print("    python -m marketing.run meta-check\n")
        print(f"  Length {len(token)} chars, starts {token[:6]}... (to verify the store)\n")
        return 0

    if command == "meta-check":
        from .social.meta import MetaConfig, NotConfigured, diagnose

        print("\nMETA GRAPH API - what this token can actually do\n")
        try:
            config = MetaConfig.from_env()
        except NotConfigured as exc:
            print(f"  [FAIL] Configuration\n         {exc}\n")
            return 1
        failed = 0
        for status, subject, detail in diagnose(config):
            if status == "FAIL":
                failed += 1
            print(f"  [{status:4}] {subject}")
            print(f"         {detail}\n")
        return 1 if failed else 0

    run_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    result = run_daily(
        run_date=run_date,
        items_wanted=args.items,
        download=not args.no_download,
    )

    print(f"\n{len(result.items)} item(s) prepared for {result.run_date.isoformat()}")
    for item in result.items:
        print(f"  - {item['sku']}  {item['name'][:56]}")
    for skipped in result.skipped:
        print(f"  ! skipped {skipped['sku']}: {skipped['reason']}")
    for warning in result.warnings:
        print(f"  ! {warning}")
    print(f"\nPlan: {result.out_dir / 'plan.md'}\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
