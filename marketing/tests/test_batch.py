"""Batch runner + folder adapter tests — simulate C:\\FaridunhillPipes."""

from __future__ import annotations

import json
from pathlib import Path

from marketing.batch import build_input, run_batch
from marketing.folder_source import FolderItemAssets, infer_role, parse_folder_name
from marketing.genome.vocab import MediaRole


def _make_pipe(root: Path, name: str, images: list[str], notes: str | None = None) -> Path:
    d = root / name
    d.mkdir(parents=True)
    for img in images:
        (d / img).write_bytes(b"\xff\xd8\xff")  # tiny fake jpeg header; content unused
    if notes is not None:
        (d / "pipe.txt").write_text(notes, encoding="utf-8")
    return d


def test_parse_folder_name_longest_brand_wins():
    assert parse_folder_name("Danske Club Vario 166 Sitter") == ("Danske Club", "Vario 166 Sitter")
    assert parse_folder_name("Dunhill Cumberland 41031") == ("Dunhill", "Cumberland 41031")


def test_infer_role_from_filename():
    assert infer_role("hero.jpg") is MediaRole.HERO
    assert infer_role("stamp-macro.jpg") is MediaRole.STAMPING
    assert infer_role("tooth-flaw.jpg") is MediaRole.FLAW
    assert infer_role("random.jpg") is MediaRole.ANGLE   # first-photo->hero is the adapter's job


def test_explicit_hero_wins_over_alphabetical_first(tmp_path):
    # 'angle.jpg' sorts first, but 'hero.jpg' must be the hero
    _make_pipe(tmp_path, "Dunhill 41031", ["angle.jpg", "hero.jpg", "stamp.jpg"])
    assets = FolderItemAssets(tmp_path).get("Dunhill 41031")
    heroes = [m for m in assets.media if m.role is MediaRole.HERO]
    assert len(heroes) == 1
    assert heroes[0].url.endswith("hero.jpg")


def test_first_photo_becomes_hero_when_none_named(tmp_path):
    _make_pipe(tmp_path, "GBD Cutty", ["aaa.jpg", "bbb.jpg"])
    assets = FolderItemAssets(tmp_path).get("GBD Cutty")
    assert assets.media[0].role is MediaRole.HERO
    assert assets.media[0].url.endswith("aaa.jpg")


def test_folder_source_reads_photos_and_stamping(tmp_path):
    d = _make_pipe(tmp_path, "Peterson XL 90S", ["a-hero.jpg", "b-stamp.jpg"])
    (d / "stamp.txt").write_text("PETERSON'S DUBLIN", encoding="utf-8")
    src = FolderItemAssets(tmp_path)
    assets = src.get("Peterson XL 90S")
    assert len(assets.media) == 2
    assert assets.stamping_ocr == "PETERSON'S DUBLIN"
    roles = {m.role for m in assets.media}
    assert MediaRole.HERO in roles and MediaRole.STAMPING in roles


def test_build_input_merges_notes_over_folder_name(tmp_path):
    d = _make_pipe(
        tmp_path, "Dunhill Cumberland 41031", ["hero.jpg"],
        notes="price: 425\ncurrency: USD\ncondition: very_good\n"
              "era: 1980-1990 hallmark\nflaws: rim_darkening\n"
              "why: A Cumberland sandblast with its original sterling band.\n",
    )
    intake = build_input(d)
    assert intake.human_facts["brand"] == "Dunhill"
    assert intake.economics["list_price"] == 425.0
    assert intake.human_facts["unique_physical.era"]["min_year"] == 1980
    assert intake.why_special.startswith("A Cumberland")


def test_run_batch_produces_all_outputs(tmp_path):
    root = tmp_path / "FaridunhillPipes"
    _make_pipe(root, "Dunhill Cumberland 41031", ["hero.jpg", "stamp.jpg"],
               notes="price: 425\ncurrency: USD\ncondition: excellent\nera: 1985-1990 hallmark\n")
    _make_pipe(root, "Vauen Luxus 3286", ["1.jpg"], notes="price: 95\ncurrency: USD\n")
    out = tmp_path / "out"
    report = run_batch(root, out, reference_year=2026)

    assert report["count"] == 2
    # per-pipe artifacts exist
    for sku in ("Dunhill Cumberland 41031", "Vauen Luxus 3286"):
        pdir = out / sku
        assert (pdir / "listing.md").is_file()
        assert (pdir / "post-instagram.txt").is_file()
        assert (pdir / "post-tiktok.txt").is_file()
        reel = json.loads((pdir / "reel.json").read_text())
        assert reel["orientation"] == "9:16"
    # index + machine report
    assert (out / "INDEX.md").is_file()
    rows = json.loads((out / "report.json").read_text())
    assert {r["sku"] for r in rows} == {"Dunhill Cumberland 41031", "Vauen Luxus 3286"}
    # the Dunhill listing asserts the maker (human-sourced) and shows the price
    listing = (out / "Dunhill Cumberland 41031" / "listing.md").read_text()
    assert "Dunhill" in listing


def test_run_batch_is_rerunnable(tmp_path):
    root = tmp_path / "FaridunhillPipes"
    _make_pipe(root, "GBD Cutty", ["hero.jpg"], notes="price: 145\n")
    out = tmp_path / "out"
    run_batch(root, out, reference_year=2026)
    # second run must not crash on the existing birth record
    report = run_batch(root, out, reference_year=2026)
    assert report["count"] == 1
