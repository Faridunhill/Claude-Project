"""Render + auto-mode tests. Skipped cleanly where heavy deps are absent."""

from __future__ import annotations

from pathlib import Path

import pytest

# these need pillow + imageio-ffmpeg (+ numpy); skip the module if missing
pytest.importorskip("PIL")
pytest.importorskip("imageio")
pytest.importorskip("numpy")

from PIL import Image, ImageDraw  # noqa: E402

from marketing.auto import process  # noqa: E402


def _pipe_with_photos(root: Path, name: str, n: int = 3) -> Path:
    d = root / name
    d.mkdir(parents=True)
    for i in range(n):
        im = Image.new("RGB", (1200, 900), (100 + i * 20, 60, 40))
        ImageDraw.Draw(im).ellipse([300, 300, 900, 600], fill=(200, 150, 90))
        im.save(d / f"{i}-photo.jpg", "JPEG")
    return d


def test_process_renders_mp4_and_photos(tmp_path):
    root = tmp_path / "FaridunhillPipes"
    _pipe_with_photos(root, "Dunhill 41031")
    (root / "prices.txt").write_text("dunhill: 425\n", encoding="utf-8")
    rendered = process(root, reference_year=2026)

    assert "Dunhill 41031" in rendered
    pdir = root / "_marketing" / "Dunhill 41031"
    assert (pdir / "reel.mp4").is_file()
    assert (pdir / "reel.mp4").stat().st_size > 1000
    jpgs = list((pdir / "photos").glob("*.jpg"))
    assert len(jpgs) == 3
    # posts exist alongside the video
    assert (pdir / "post-tiktok.txt").is_file()


def test_process_is_incremental(tmp_path):
    root = tmp_path / "FaridunhillPipes"
    _pipe_with_photos(root, "Vauen 3286")
    first = process(root, reference_year=2026)
    assert first == ["Vauen 3286"]
    # nothing changed -> second pass renders nothing (video step skipped)
    second = process(root, reference_year=2026)
    assert second == []


def test_new_pipe_is_picked_up(tmp_path):
    root = tmp_path / "FaridunhillPipes"
    _pipe_with_photos(root, "GBD Cutty")
    process(root, reference_year=2026)
    # a NEW pipe folder appears later
    _pipe_with_photos(root, "Winslow Viking")
    new = process(root, reference_year=2026)
    assert new == ["Winslow Viking"]           # only the new one renders
    assert (root / "_marketing" / "Winslow Viking" / "reel.mp4").is_file()
