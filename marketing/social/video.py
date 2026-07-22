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


def load_style(style_path: str | Path) -> dict:
    with open(style_path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build_command(spec: VideoSpec, style: dict, out_dir: Path) -> tuple[list[str], Path]:
    fmt = style["formats"][spec.fmt]
    w, h = fmt["width"], fmt["height"]
    spp = float(style["motion"]["seconds_per_photo"])
    zoom = float(style["motion"]["zoom"])
    brand = style["brand_name"]
    out = out_dir / f"{spec.sku}-{spec.fmt}.mp4"

    inputs: list[str] = []
    filters: list[str] = []
    for i, photo in enumerate(spec.photos):
        inputs += ["-loop", "1", "-t", str(spp), "-i", photo]
        frames = int(spp * 25)
        filters.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},zoompan=z='min(zoom+{(zoom - 1) / frames:.5f},{zoom})'"
            f":d={frames}:s={w}x{h}[v{i}]"
        )
    concat = "".join(f"[v{i}]" for i in range(len(spec.photos)))
    filters.append(f"{concat}concat=n={len(spec.photos)}:v=1:a=0[slides]")
    filters.append(
        f"[slides]drawtext=text='{spec.title_overlay}':fontcolor={style['overlay']['title_color']}:"
        f"fontsize=42:x=(w-text_w)/2:y=h-140,"
        f"drawtext=text='{brand}':fontcolor={style['overlay']['brand_color']}:"
        f"fontsize=28:x=w-text_w-40:y=40[vout]"
    )

    cmd = ["ffmpeg", "-y", *inputs]
    maps = ["-map", "[vout]"]
    if spec.music_path:
        cmd += ["-i", spec.music_path]
        maps += ["-map", f"{len(spec.photos)}:a", "-shortest"]
    cmd += ["-filter_complex", ";".join(filters), *maps,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "25", str(out)]
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
    if shutil.which("ffmpeg"):
        subprocess.run(cmd, check=True, capture_output=True)
        rendered = True
    return VideoResult(output_path=str(out), command=cmd, rendered=rendered, manifest=manifest)
