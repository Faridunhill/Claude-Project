"""Runner, rotation and photo-cache tests.

The suite never touches the network: photo downloads go through an
injected stub. The governing rules under test are the ones that decide
whether a nightly job can be trusted to run unattended — walls hold,
failures degrade instead of aborting, and a re-run is safe.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from marketing.media import cache_name, fetch_all, fetch_photo
from marketing.rotation import Candidate, Rotation
from marketing.run import run_daily, run_doctor

# A 1x1 JPEG — enough for the cache and command-building paths.
_TINY_JPEG = bytes.fromhex(
    "ffd8ffe000104a46494600010100000100010000ffdb004300ff"
    "c00011080001000103011100021101031101ffc4001f0000010501"
    "010101010100000000000000000102030405060708090a0bffda00"
    "0c03010002110311003f00bfffd9"
)


def _stub_downloader(url: str, dest: Path) -> None:
    dest.write_bytes(_TINY_JPEG)


def _failing_downloader(url: str, dest: Path) -> None:
    raise OSError("network unreachable")


@pytest.fixture
def store(tmp_path: Path) -> Path:
    """A tiny catalog + the real control/brands/style files."""
    products = tmp_path / "products"
    products.mkdir()
    for i, (sku, name, price) in enumerate([
        ("FH-A-001", "Chacom Gentleman 836 Sandblasted Dublin circa 1955", "180.00"),
        ("FH-A-002", "Vintage German Leather Tobacco Pouch, Mid-Century", "35.00"),
        ("FH-A-003", "Bari Winking 1999 Army Mount Straight Billiard", "129.00"),
    ]):
        (products / f"{i}.yaml").write_text(yaml.safe_dump({
            "name": name, "sku": sku, "price": price,
            "department": "estate-pipes", "inStock": True,
            "images": [f"https://cdn.example/{sku}.jpg"],
        }))
    return products


def _run(store: Path, tmp_path: Path, **kwargs):
    root = Path(__file__).resolve().parent.parent
    defaults = dict(
        products_dir=store,
        out_root=tmp_path / "out",
        control_path=root / "control.yaml",
        brands_path=root / "brands.yaml",
        style_path=root / "social" / "style_faridunhill.yaml",
        downloader=_stub_downloader,
    )
    defaults.update(kwargs)
    return run_daily(**defaults)


# ── photo cache ──────────────────────────────────────────────────────

def test_cache_name_is_stable_and_extensioned():
    a = cache_name("https://cdn.example/x.jpg")
    assert a == cache_name("https://cdn.example/x.jpg")
    assert a.endswith(".jpg")
    assert a != cache_name("https://cdn.example/y.jpg")


def test_odd_extension_falls_back_to_jpg():
    assert cache_name("https://cdn.example/img.aspx?id=3").endswith(".jpg")


def test_photo_is_downloaded_once_then_cached(tmp_path):
    url = "https://cdn.example/a.jpg"
    first = fetch_photo(url, tmp_path, _stub_downloader)
    second = fetch_photo(url, tmp_path, _stub_downloader)
    assert first.ok and not first.cached
    assert second.ok and second.cached
    assert first.path == second.path


def test_failed_download_reports_instead_of_raising(tmp_path):
    result = fetch_photo("https://cdn.example/a.jpg", tmp_path, _failing_downloader)
    assert not result.ok
    assert "network unreachable" in (result.error or "")


def test_local_path_passes_through(tmp_path):
    local = tmp_path / "photo.jpg"
    local.write_bytes(_TINY_JPEG)
    assert fetch_photo(str(local), tmp_path / "cache").path == str(local)


def test_missing_local_path_is_an_error(tmp_path):
    assert not fetch_photo(str(tmp_path / "nope.jpg"), tmp_path / "cache").ok


def test_fetch_all_preserves_order(tmp_path):
    urls = [f"https://cdn.example/{n}.jpg" for n in "abc"]
    assert [r.url for r in fetch_all(urls, tmp_path, _stub_downloader)] == urls


# ── rotation ─────────────────────────────────────────────────────────

def _candidates():
    return [
        Candidate("A", 10.0, True, True),
        Candidate("B", 100.0, True, True),
        Candidate("C", 50.0, False, True),   # no photo
        Candidate("D", 75.0, True, False),   # out of stock
    ]


def test_ineligible_items_are_never_selected(tmp_path):
    rotation = Rotation(tmp_path / "r.db")
    assert set(rotation.select(_candidates(), date(2026, 9, 12), 10)) == {"A", "B"}


def test_price_breaks_ties_among_never_posted(tmp_path):
    rotation = Rotation(tmp_path / "r.db")
    assert rotation.select(_candidates(), date(2026, 9, 12), 1) == ["B"]


def test_cooldown_blocks_a_repeat(tmp_path):
    rotation = Rotation(tmp_path / "r.db", cooldown_days=45)
    rotation.record(["A", "B"], date(2026, 9, 12))
    assert rotation.select(_candidates(), date(2026, 9, 20), 5) == []


def test_cooldown_expires(tmp_path):
    rotation = Rotation(tmp_path / "r.db", cooldown_days=45)
    rotation.record(["A", "B"], date(2026, 9, 12))
    assert set(rotation.select(_candidates(), date(2026, 12, 1), 5)) == {"A", "B"}


def test_never_posted_drains_before_anything_repeats(tmp_path):
    rotation = Rotation(tmp_path / "r.db", cooldown_days=0)
    rotation.record(["B"], date(2026, 9, 1))
    # B is out of cooldown and worth more, but A has never been posted.
    assert rotation.select(_candidates(), date(2026, 9, 12), 1) == ["A"]


def test_record_is_idempotent(tmp_path):
    rotation = Rotation(tmp_path / "r.db")
    rotation.record(["A"], date(2026, 9, 12))
    rotation.record(["A"], date(2026, 9, 12))
    assert rotation.posted_count() == 1


def test_selection_is_deterministic(tmp_path):
    a = Rotation(tmp_path / "a.db").select(_candidates(), date(2026, 9, 12), 2)
    b = Rotation(tmp_path / "b.db").select(_candidates(), date(2026, 9, 12), 2)
    assert a == b


# ── the daily run ────────────────────────────────────────────────────

def test_daily_run_produces_a_plan_and_content(store, tmp_path):
    result = _run(store, tmp_path, run_date=date(2026, 9, 12), items_wanted=2)
    assert len(result.items) == 2
    plan = result.out_dir / "plan.md"
    assert plan.exists()
    body = plan.read_text()
    for item in result.items:
        assert item["sku"] in body
        assert item["caption"] in body


def test_every_item_gets_a_caption_with_hashtags(store, tmp_path):
    result = _run(store, tmp_path, run_date=date(2026, 9, 12), items_wanted=3)
    for item in result.items:
        assert "#" in item["caption"]
        assert item["caption"].isascii()


def test_tier1_is_dry_run_by_default(store, tmp_path):
    """Nothing may reach Meta until credentials are wired deliberately."""
    result = _run(store, tmp_path, run_date=date(2026, 9, 12), items_wanted=1)
    assert all("dryrun://" in p for p in result.items[0]["placements"])


def test_personal_profile_is_queued_never_auto_posted(store, tmp_path):
    """Tier 2 is a ToS wall: the machine prepares, a human taps."""
    result = _run(store, tmp_path, run_date=date(2026, 9, 12), items_wanted=1)
    item = result.items[0]
    assert any("profile" in q for q in item["queued"])
    assert not any("profile" in p for p in item["placements"])


def test_rerunning_the_same_date_does_not_double_spend(store, tmp_path):
    out = tmp_path / "out"
    first = _run(store, tmp_path, out_root=out, run_date=date(2026, 9, 12), items_wanted=2)
    second = _run(store, tmp_path, out_root=out, run_date=date(2026, 9, 12), items_wanted=2)
    assert [i["sku"] for i in first.items] == [i["sku"] for i in second.items]


def test_consecutive_days_pick_different_items(store, tmp_path):
    out = tmp_path / "out"
    day1 = _run(store, tmp_path, out_root=out, run_date=date(2026, 9, 12), items_wanted=1)
    day2 = _run(store, tmp_path, out_root=out, run_date=date(2026, 9, 13), items_wanted=1)
    assert day1.items[0]["sku"] != day2.items[0]["sku"]


def test_unfetchable_photo_skips_the_item_without_aborting(store, tmp_path):
    result = _run(
        store, tmp_path, run_date=date(2026, 9, 12), items_wanted=3,
        downloader=_failing_downloader,
    )
    assert result.items == []
    assert len(result.skipped) == 3
    assert (result.out_dir / "plan.md").exists(), "a plan must still be written"


def test_exhausted_cooldown_warns_instead_of_failing(store, tmp_path):
    out = tmp_path / "out"
    _run(store, tmp_path, out_root=out, run_date=date(2026, 9, 12), items_wanted=3)
    result = _run(store, tmp_path, out_root=out, run_date=date(2026, 9, 13), items_wanted=3)
    assert result.items == []
    assert any("cooldown" in w for w in result.warnings)


def test_render_script_is_written_when_ffmpeg_is_absent(store, tmp_path):
    import shutil as _shutil

    result = _run(store, tmp_path, run_date=date(2026, 9, 12), items_wanted=1)
    script = result.out_dir / "render.sh"
    if _shutil.which("ffmpeg"):
        assert result.rendered == 1
    else:
        assert script.exists()
        text = script.read_text()
        assert "ffmpeg" in text and "libx264" in text


def test_video_overlay_is_escaped_for_ffmpeg(tmp_path):
    """An apostrophe or colon in a title terminates drawtext's argument
    and the whole render fails."""
    from marketing.run import _ffmpeg_safe

    safe = _ffmpeg_safe("Rattray's Mary: 161 Rhodesian")
    assert "'" not in safe and ":" not in safe


def test_offline_mode_still_produces_captions(store, tmp_path):
    result = _run(store, tmp_path, run_date=date(2026, 9, 12), items_wanted=2, download=False)
    assert len(result.items) == 2
    assert all(i["caption"] for i in result.items)


def test_empty_catalog_warns_and_returns_cleanly(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    result = _run(empty, tmp_path, run_date=date(2026, 9, 12))
    assert result.items == []
    assert result.warnings


# ── doctor ───────────────────────────────────────────────────────────

def test_doctor_reports_every_subject(store, tmp_path):
    root = Path(__file__).resolve().parent.parent
    checks = run_doctor(
        products_dir=store, out_root=tmp_path / "out",
        control_path=root / "control.yaml", brands_path=root / "brands.yaml",
    )
    subjects = {subject for _, subject, _ in checks}
    assert {"Catalog", "ffmpeg", "Standing walls", "Publishing"} <= subjects
    assert all(status in ("OK", "WARN", "TODO") for status, _, _ in checks)


def test_doctor_flags_dry_run_publishing(store, tmp_path):
    root = Path(__file__).resolve().parent.parent
    checks = run_doctor(
        products_dir=store, out_root=tmp_path / "out",
        control_path=root / "control.yaml", brands_path=root / "brands.yaml",
    )
    publishing = [c for c in checks if c[1] == "Publishing"][0]
    assert publishing[0] == "WARN" and "DRY RUN" in publishing[2]


def test_rerun_with_a_higher_count_tops_up_the_same_day(tmp_path):
    """Asking for more items on a day already run adds to it rather
    than replacing it — the morning's posts stay valid."""
    rotation = Rotation(tmp_path / "r.db")
    day = date(2026, 9, 12)
    first = rotation.select(_candidates(), day, 1)
    rotation.record(first, day)
    second = rotation.select(_candidates(), day, 2)
    assert second[: len(first)] == first
    assert len(second) == 2


# ── a new listing must not wait behind the backlog ───────────────────

def test_a_new_listing_is_posted_before_the_backlog(tmp_path):
    """Adding a pipe in the admin should put it on social within a day,
    not behind 200 older items waiting their turn."""
    rotation = Rotation(tmp_path / "r.db")
    today = date(2026, 9, 12)
    backlog = Candidate("OLD", 500.0, True, True, added=date(2026, 1, 1))
    fresh = Candidate("NEW", 30.0, True, True, added=date(2026, 9, 11))
    assert rotation.select([backlog, fresh], today, 1) == ["NEW"]


def test_newest_listing_wins_among_several_new_ones(tmp_path):
    """Needs a settled catalog around them: freshness only counts when
    it distinguishes a few items from the rest."""
    rotation = Rotation(tmp_path / "r.db")
    today = date(2026, 9, 12)
    backlog = [
        Candidate(f"B-{i}", 100.0, True, True, added=date(2026, 1, 1))
        for i in range(20)
    ]
    older = Candidate("A", 900.0, True, True, added=date(2026, 9, 5))
    newest = Candidate("N", 10.0, True, True, added=date(2026, 9, 11))
    assert rotation.select([*backlog, older, newest], today, 1) == ["N"]


def test_backlog_still_sorts_by_price(tmp_path):
    """Once nothing is new, the money at stake breaks the tie again."""
    rotation = Rotation(tmp_path / "r.db")
    cheap = Candidate("C", 20.0, True, True, added=date(2026, 1, 1))
    dear = Candidate("D", 500.0, True, True, added=date(2026, 1, 2))
    assert rotation.select([cheap, dear], date(2026, 9, 12), 1) == ["D"]


def test_undated_items_are_treated_as_backlog(tmp_path):
    rotation = Rotation(tmp_path / "r.db")
    undated = Candidate("U", 900.0, True, True, added=None)
    fresh = Candidate("N", 10.0, True, True, added=date(2026, 9, 11))
    assert rotation.select([undated, fresh], date(2026, 9, 12), 1) == ["N"]


def test_the_admin_brand_field_is_used_directly(tmp_path):
    """Keystatic has a Brand field. A maker typed there needs no guessing
    from the title, and is not limited to the allowlist."""
    from marketing.catalog import load_brands, to_effective

    root = Path(__file__).resolve().parent.parent
    effective = to_effective(
        {"name": "Unsigned Straight Billiard", "sku": "X",
         "brand": "Some Maker Not In The Allowlist"},
        load_brands(root / "brands.yaml"),
    )
    assert effective["brand"] == "Some Maker Not In The Allowlist"


def test_allowlist_still_covers_an_empty_admin_field(tmp_path):
    from marketing.catalog import load_brands, to_effective

    root = Path(__file__).resolve().parent.parent
    effective = to_effective(
        {"name": "Chacom Gentleman 836 Dublin", "sku": "X", "brand": ""},
        load_brands(root / "brands.yaml"),
    )
    assert effective["brand"] == "Chacom"


def test_a_bulk_import_is_not_treated_as_new(tmp_path):
    """After a fresh clone every file carries today's date. If everything
    looks new, nothing is — otherwise the whole backlog would sort by
    filesystem timestamp instead of by value."""
    rotation = Rotation(tmp_path / "r.db")
    today = date(2026, 9, 12)
    imported = [
        Candidate(f"I-{i}", float(i), True, True, added=date(2026, 9, 12))
        for i in range(20)
    ]
    # highest price wins, not an arbitrary same-day timestamp
    assert rotation.select(imported, today, 1) == ["I-19"]


# ── scheduling ───────────────────────────────────────────────────────

def test_schedule_rejects_an_impossible_time():
    from marketing.run import _write_schedule

    assert _write_schedule("25:00") == 1
    assert _write_schedule("07:61") == 1
    assert _write_schedule("morning") == 1


def test_schedule_accepts_a_valid_time():
    from marketing.run import _write_schedule

    assert _write_schedule("07:00") == 0


def test_windows_task_survives_a_pc_that_was_switched_off():
    """StartWhenAvailable matters more than the time: without it a PC
    that was off at 07:00 skips the day silently."""
    from marketing.run import _TASK_XML

    assert "<StartWhenAvailable>true</StartWhenAvailable>" in _TASK_XML
    assert "<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>" in _TASK_XML
    assert "-m marketing.run daily" in _TASK_XML
