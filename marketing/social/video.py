"""Video builder (SOCIAL-ENGINE-001): genome photos -> branded slideshow
via ffmpeg (motion, overlays, house music). Renders on the PC nightly;
this module BUILDS the exact ffmpeg command and manifest, and executes
it when ffmpeg is present. When absent it returns the command for the
PC job — the logic is testable everywhere, the rendering runs where
ffmpeg lives.

License rule (CHANNEL-MAP-001): every video logs its music license
source in the manifest; no manifest, no post.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

VIDEO_GENERATOR_VERSION = "video-1.0.0"


@dataclass(frozen=True)
class VideoSpec:
    sku: str
    photos: list[str]                     # genome media urls/paths, ordered
    title_overlay: str                    # item name
    fmt: str                              # "vertical" | "square"
    music_path: Optional[str] = None
    music_license_source: str = "meta_sound_collection"


@dataclass(frozen=True)
class VideoResult:
    output_path: str
    command: list[str]
    rendered: bool                        # False -> command handed to PC job
    manifest: dict = field(default_factory=dict)


#: ffmpeg is often already on the machine but not on PATH. FaridOS
#: ships one at voice/bin. Searching for it beats asking Farid to
#: install a second copy.
_FFMPEG_CANDIDATES = (
    "~/FaridOS/voice/bin/ffmpeg.exe",
    "~/FaridOS/voice/bin/ffmpeg",
    "C:/Users/hadid/FaridOS/voice/bin/ffmpeg.exe",
)


def resolve_ffmpeg() -> Optional[str]:
    """The ffmpeg binary: FFMPEG_BINARY, then PATH, then known installs."""
    explicit = os.environ.get("FFMPEG_BINARY", "").strip()
    if explicit and Path(explicit).exists():
        return explicit
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in _FFMPEG_CANDIDATES:
        path = Path(candidate).expanduser()
        if path.exists():
            return str(path)
    return None


def load_style(style_path: str | Path) -> dict:
    with open(style_path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


#: Serif faces to fall back on, in preference order, when style.yaml
#: names no `font_file`. Relying on a system default is not safe: a PC
#: with no DejaVu installed emits "Fontconfig error: Cannot load default
#: config file" and, on a machine without the fallback, fails outright.
_FONT_CANDIDATES = (
    # Windows
    "C:/Windows/Fonts/georgia.ttf",
    "C:/Windows/Fonts/times.ttf",
    "C:/Windows/Fonts/arial.ttf",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    # macOS
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
)


def resolve_font(style: dict) -> Optional[str]:
    """An actual font FILE for drawtext, or None to let ffmpeg guess.

    `style.yaml` may name one explicitly as `overlay.font_file`; that
    always wins. Otherwise the first candidate that exists on this
    machine is used.
    """
    explicit = (style.get("overlay") or {}).get("font_file")
    if explicit and Path(explicit).exists():
        return str(explicit)
    for candidate in _FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def _escape_fontfile(path: str) -> str:
    """Quote a font path for a filtergraph.

    Inside a filter argument, ":" separates options, so a Windows path
    like C:/Windows/... terminates the argument early and drawtext dies.
    Backslashes are normalised to forward slashes and the drive colon is
    escaped.
    """
    return "'" + path.replace("\\", "/").replace(":", r"\:") + "'"


#: Width of an average glyph as a fraction of the font size, for this
#: serif face. Measured off a rendered 1080-wide frame where a 46
#: character title at size 42 overran the frame: ~23px per character,
#: i.e. 0.55 of the size. Rounded up so the estimate errs toward
#: wrapping early rather than overflowing.
_GLYPH_WIDTH_RATIO = 0.58

#: Side margin kept clear at each edge.
_SIDE_MARGIN = 60


def _chars_per_line(width: int, font_size: int) -> int:
    usable = max(1, width - 2 * _SIDE_MARGIN)
    return max(12, int(usable / (font_size * _GLYPH_WIDTH_RATIO)))


def wrap_title(title: str, max_chars: int, max_lines: int = 2) -> list[str]:
    """Break a listing title into at most `max_lines` lines that fit.

    Marketplace titles run to 80+ characters and a single drawtext line
    is not clipped by ffmpeg - it is centred and simply runs off both
    edges of the frame, which reads as broken rather than as cropped.
    """
    words = title.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)

    # Anything that did not fit is dropped, with an ellipsis so the cut
    # is visible rather than looking like a truncated thought.
    used = len(" ".join(lines).split())
    if used < len(words) and lines:
        tail = lines[-1]
        if len(tail) + 3 > max_chars:
            tail = tail[: max_chars - 3].rstrip()
        lines[-1] = tail + "..."
    return lines


def build_command(spec: VideoSpec, style: dict, out_dir: Path) -> tuple[list[str], Path]:
    fmt = style["formats"][spec.fmt]
    w, h = fmt["width"], fmt["height"]
    motion = style["motion"]
    spp = float(motion["seconds_per_photo"])
    zoom = float(motion["zoom"])
    fps = int(motion.get("fps", 25))
    brand = style["brand_name"]
    out = out_dir / f"{spec.sku}-{spec.fmt}.mp4"

    # FRAME MATH — the part that was wrong and produced 100-second, 72 MB
    # videos instead of 2-second, 1.3 MB ones.
    #
    # zoompan emits `d` frames for EVERY frame it is fed. The old command
    # fed it a looped input bounded by "-t 2.0", i.e. 50 frames at 25fps,
    # and then asked for d=50 — so 50 x 50 = 2500 frames = 100 seconds
    # per photo.
    #
    # The fix is to feed each photo as exactly ONE frame (a still image
    # input with no -loop), so zoompan emits exactly `d` frames from it.
    # Bounding the OUTPUT with -t instead would also yield 2 seconds, but
    # only for a single photo: with several photos it would truncate the
    # video after the first. This way the arithmetic holds for any count.
    frames = max(1, round(spp * fps))
    step = (zoom - 1) / frames

    inputs: list[str] = []
    filters: list[str] = []
    for i, photo in enumerate(spec.photos):
        inputs += ["-i", photo]
        filters.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},zoompan=z='min(zoom+{step:.5f},{zoom})'"
            f":d={frames}:s={w}x{h}:fps={fps}[v{i}]"
        )
    concat = "".join(f"[v{i}]" for i in range(len(spec.photos)))
    filters.append(f"{concat}concat=n={len(spec.photos)}:v=1:a=0[slides]")

    font = resolve_font(style)
    font_arg = f"fontfile={_escape_fontfile(font)}:" if font else ""
    overlay = style["overlay"]
    title_size = int(overlay.get("title_size", 44))
    brand_size = int(overlay.get("brand_size", 28))

    # Keep the title clear of the platform's own furniture. Instagram and
    # TikTok draw the caption, the handle and the action buttons over the
    # bottom of a vertical video, so text placed near the edge is simply
    # covered up. Measured against a rendered frame, not guessed.
    bottom_margin = int(overlay.get("title_bottom_margin", 430))
    line_gap = int(title_size * 1.35)

    lines_of_title = wrap_title(spec.title_overlay, _chars_per_line(w, title_size))
    # A drop shadow, not a box: the overlay has to stay readable over a
    # pale photograph without putting a slab across the product.
    shadow = "shadowcolor=black@0.65:shadowx=2:shadowy=2:"

    draws = []
    for index, line in enumerate(lines_of_title):
        y = h - bottom_margin + index * line_gap
        draws.append(
            f"drawtext={font_arg}{shadow}text='{line}':"
            f"fontcolor={overlay['title_color']}:"
            f"fontsize={title_size}:x=(w-text_w)/2:y={y}"
        )
    draws.append(
        f"drawtext={font_arg}{shadow}text='{brand}':"
        f"fontcolor={overlay['brand_color']}:"
        f"fontsize={brand_size}:x=w-text_w-48:y=56"
    )
    filters.append("[slides]" + ",".join(draws) + "[vout]")

    cmd = ["ffmpeg", "-y", *inputs]
    maps = ["-map", "[vout]"]
    if spec.music_path:
        cmd += ["-i", spec.music_path]
        maps += ["-map", f"{len(spec.photos)}:a", "-shortest"]
    cmd += ["-filter_complex", ";".join(filters), *maps,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(fps), str(out)]
    return cmd, out


def build_video(spec: VideoSpec, style: dict, out_dir: str | Path) -> VideoResult:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd, out = build_command(spec, style, out_dir)

    manifest = {
        "sku": spec.sku,
        "format": spec.fmt,
        "photos": spec.photos,
        "music_license_source": spec.music_license_source,
        "music_path": spec.music_path,
        "generator_version": VIDEO_GENERATOR_VERSION,
        "is_synthetic": False,   # real photos with overlays — NOT generated imagery
    }

    rendered = False
    binary = resolve_ffmpeg()
    if binary:
        # cmd[0] is the literal "ffmpeg"; swap in the real path so a
        # binary that is installed but not on PATH still renders.
        subprocess.run([binary, *cmd[1:]], check=True, capture_output=True)
        rendered = True
    return VideoResult(output_path=str(out), command=cmd, rendered=rendered, manifest=manifest)
