"""Video builder regression tests.

The bug these exist to prevent was measured on Farid's PC: a 2-second
clip rendered as 100 seconds and 72 MB. zoompan emits `d` frames for
EVERY frame it is fed, so a looped input bounded by `-t 2.0` fed it 50
frames and it emitted 50 x 50 = 2500. Verified against real ffmpeg:
old command 00:01:40.00, fixed command 00:00:02.00.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from marketing.social.video import (
    VideoSpec,
    _escape_fontfile,
    build_command,
    load_style,
    resolve_font,
)

STYLE_PATH = Path(__file__).resolve().parent.parent / "social" / "style_faridunhill.yaml"


@pytest.fixture(scope="module")
def style() -> dict:
    return load_style(STYLE_PATH)


def _filtergraph(cmd: list[str]) -> str:
    return cmd[cmd.index("-filter_complex") + 1]


def _spec(count: int) -> VideoSpec:
    return VideoSpec(
        sku="FH-TP-110",
        photos=[f"p{i}.jpg" for i in range(count)],
        title_overlay="Test Title",
        fmt="vertical",
    )


# ── the 50x duration bug ─────────────────────────────────────────────

def test_inputs_are_never_looped(style, tmp_path):
    """`-loop 1 -t 2.0` feeds zoompan 50 frames instead of 1, and
    zoompan multiplies. This is the whole bug."""
    cmd, _ = build_command(_spec(1), style, tmp_path)
    assert "-loop" not in cmd
    assert cmd.count("-i") == 1


def test_one_input_per_photo(style, tmp_path):
    cmd, _ = build_command(_spec(3), style, tmp_path)
    assert cmd.count("-i") == 3


def test_zoompan_duration_matches_seconds_times_fps(style, tmp_path):
    """d must equal seconds_per_photo * fps — 2.0s at 25fps = 50."""
    graph = _filtergraph(build_command(_spec(1), style, tmp_path)[0])
    expected = round(float(style["motion"]["seconds_per_photo"])
                     * int(style["motion"].get("fps", 25)))
    assert f":d={expected}:" in graph
    assert expected == 50


def test_output_is_not_truncated_with_t(style, tmp_path):
    """Bounding the OUTPUT with -t yields 2 seconds for one photo but
    silently truncates a multi-photo reel after the first. Verified:
    3 photos with output -t 2.0 rendered 00:00:02.00, not 00:00:06.00."""
    cmd, _ = build_command(_spec(3), style, tmp_path)
    assert "-t" not in cmd


def test_zoom_step_completes_exactly_one_cycle(style, tmp_path):
    """step * frames must reach the zoom ceiling: a step computed
    against the wrong frame count either stalls or overshoots."""
    graph = _filtergraph(build_command(_spec(1), style, tmp_path)[0])
    zoom = float(style["motion"]["zoom"])
    frames = 50
    step = (zoom - 1) / frames
    assert f"min(zoom+{step:.5f},{zoom})" in graph


def test_concat_count_matches_photo_count(style, tmp_path):
    graph = _filtergraph(build_command(_spec(4), style, tmp_path)[0])
    assert "concat=n=4:" in graph


# ── font ─────────────────────────────────────────────────────────────

def test_explicit_font_file_wins(style, tmp_path):
    font = tmp_path / "Brand.ttf"
    font.write_bytes(b"x")
    custom = {**style, "overlay": {**style["overlay"], "font_file": str(font)}}
    assert resolve_font(custom) == str(font)


def test_missing_explicit_font_falls_back(style):
    custom = {**style, "overlay": {**style["overlay"], "font_file": "/nope/x.ttf"}}
    assert resolve_font(custom) != "/nope/x.ttf"


def test_windows_drive_colon_is_escaped():
    """An unescaped "C:" ends the filter argument and drawtext dies."""
    escaped = _escape_fontfile("C:/Windows/Fonts/georgia.ttf")
    assert escaped.startswith("'") and escaped.endswith("'")
    assert "C\\:" in escaped
    assert "C:/" not in escaped


def test_backslashes_become_forward_slashes():
    assert "\\" not in _escape_fontfile("C:\\Windows\\Fonts\\georgia.ttf").replace("C\\:", "")


def test_fontfile_is_used_when_one_exists(style, tmp_path):
    font = tmp_path / "Brand.ttf"
    font.write_bytes(b"x")
    custom = {**style, "overlay": {**style["overlay"], "font_file": str(font)}}
    graph = _filtergraph(build_command(_spec(1), custom, tmp_path)[0])
    assert graph.count("fontfile=") == 2       # title + brand watermark


# ── output ───────────────────────────────────────────────────────────

def test_output_path_names_sku_and_format(style, tmp_path):
    _, out = build_command(_spec(1), style, tmp_path)
    assert out.name == "FH-TP-110-vertical.mp4"


def test_square_format_uses_square_dimensions(style, tmp_path):
    spec = VideoSpec(sku="S", photos=["a.jpg"], title_overlay="t", fmt="square")
    graph = _filtergraph(build_command(spec, style, tmp_path)[0])
    assert "1080x1080" in graph


# ── the overlay, as seen on a rendered frame ─────────────────────────

def test_a_long_title_never_overflows_the_frame(style, tmp_path):
    """ffmpeg does not clip a drawtext line - it centres it and lets it
    run off both edges. On a rendered frame a 46-character title at size
    42 was cut off on both sides and read as broken."""
    from marketing.social.video import _chars_per_line, wrap_title

    limit = _chars_per_line(1080, 44)
    for title in (
        "German Expandable Leather Tobacco Pouch Magic Box Medical Rubber Lined NOS",
        "Big Ben Kingline 427 Sandblast Tomato Nosewarmer Dutch Briar Vulcanite Saddle",
        "Rattray's Mary Sandblast Complete Set",
    ):
        lines = wrap_title(title, limit)
        assert lines and all(len(line) <= limit for line in lines)
        assert len(lines) <= 2


def test_a_truncated_title_shows_that_it_was_cut():
    from marketing.social.video import wrap_title

    lines = wrap_title(" ".join(["word"] * 40), 20)
    assert lines[-1].endswith("...")


def test_a_short_title_is_left_alone():
    from marketing.social.video import wrap_title

    assert wrap_title("Short Name", 37) == ["Short Name"]


def test_empty_title_does_not_crash():
    from marketing.social.video import wrap_title

    assert wrap_title("   ", 37) == [""]


def test_title_sits_clear_of_the_platform_ui(style, tmp_path):
    """Instagram and TikTok draw the caption, handle and buttons over the
    bottom of a vertical video. A title at y=h-140 is simply covered."""
    graph = _filtergraph(build_command(_spec(1), style, tmp_path)[0])
    height = style["formats"]["vertical"]["height"]
    import re

    # ":y=" only - "shadowy=2" also contains "y=".
    ys = [int(m) for m in re.findall(r":y=(\d+)", graph)]
    title_ys = [y for y in ys if y > height / 2]
    assert title_ys, "expected a title line in the lower half"
    assert max(title_ys) < height - 300, "title would sit under the app UI"


def test_overlay_has_a_shadow_for_legibility(style, tmp_path):
    """Parchment text over a pale photograph is unreadable without it."""
    graph = _filtergraph(build_command(_spec(1), style, tmp_path)[0])
    assert graph.count("shadowcolor=") >= 2
