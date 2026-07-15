"""Reel renderer — storyboard -> a real 9:16 .mp4 (and HEIC -> JPG).

Turns each pipe's `reel.json` (from the batch) into a vertical video ready
for TikTok / Instagram Reels, and converts the pipe's HEIC photos to
upload-ready JPGs at the same time (HEIC won't upload to most platforms).

    python -m marketing.render "C:\\FaridunhillPipes"

For each `<root>/<pipe>/` that has a rendered `_marketing/<pipe>/reel.json`
it writes, into `_marketing/<pipe>/`:
    reel.mp4            the vertical video (real photos, Ken-Burns motion,
                        text overlays; slow documentary pace, no synthetic
                        imagery — PLACEMENT LAW respected)
    photos/NN-role.jpg  every source photo converted to JPG for posting

This uses ONLY the real genome photographs; it generates no imagery. It is
a separate, heavier step (needs pillow / pillow-heif / imageio-ffmpeg), so
it is invoked on its own, not by the main batch.

Deps:  pip install pillow pillow-heif imageio imageio-ffmpeg numpy
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

try:  # HEIC/HEIF support (iPhone photos)
    import pillow_heif
    pillow_heif.register_heif_opener()
    _HEIC = True
except Exception:  # pragma: no cover - optional
    _HEIC = False

W, H, FPS = 1080, 1920, 24
_BAND_H = int(H * 0.26)                 # bottom caption band height
_CREAM = (245, 240, 232)
_GOLD = (201, 168, 76)

_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _open_rgb(path: str | Path) -> Image.Image:
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def _cover(img: Image.Image, w: int, h: int) -> Image.Image:
    """Resize + center-crop so the image fully covers a w x h box."""
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    resized = img.resize((max(1, int(src_w * scale)), max(1, int(src_h * scale))), Image.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def _fit(img: Image.Image, w: int, h: int) -> Image.Image:
    """Resize so the WHOLE image fits inside w x h (no crop)."""
    src_w, src_h = img.size
    scale = min(w / src_w, h / src_h)
    return img.resize((max(1, int(src_w * scale)), max(1, int(src_h * scale))), Image.LANCZOS)


#: foreground pipe size as a fraction of the frame — whole pipe visible,
#: with room left for the caption band.
_FG_W = 0.90
_FG_H = 0.60


def _blur_bg(img: Image.Image) -> Image.Image:
    """A darkened, blurred cover of the same photo — the backdrop the pipe
    sits on (the design system's blur-frame, so the pipe reads smaller)."""
    bg = _cover(img, W, H).filter(ImageFilter.GaussianBlur(48))
    return ImageEnhance.Brightness(bg).enhance(0.45)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines[:3]


def _overlay(frame: Image.Image, text: str) -> Image.Image:
    """Draw a translucent band + wrapped caption at the bottom."""
    if not text:
        return frame
    out = frame.convert("RGBA")
    band = Image.new("RGBA", (W, _BAND_H), (10, 8, 6, 205))
    out.alpha_composite(band, (0, H - _BAND_H))
    draw = ImageDraw.Draw(out)
    font = _font(58)
    lines = _wrap(draw, text, font, int(W * 0.86))
    line_h = font.size + 16
    total = line_h * len(lines)
    y = H - _BAND_H + (_BAND_H - total) // 2
    for ln in lines:
        w = draw.textlength(ln, font=font)
        draw.text(((W - w) / 2, y), ln, font=font, fill=_CREAM)
        y += line_h
    # thin gold rule above the band
    draw.rectangle([int(W * 0.30), H - _BAND_H - 4, int(W * 0.70), H - _BAND_H - 1], fill=_GOLD)
    return out.convert("RGB")


def _shot_frames(img: Optional[Image.Image], seconds: float, overlay: str, motion: str) -> list[np.ndarray]:
    n = max(1, int(seconds * FPS))
    frames: list[np.ndarray] = []
    top_area = H - _BAND_H                                    # region above the caption band

    if img is None:
        blank = Image.new("RGB", (W, H), (10, 8, 6))         # photo pending
        for _ in range(n):
            frames.append(np.asarray(_overlay(blank, overlay)))
        return frames

    bg = _blur_bg(img)                                        # blurred backdrop (static)
    fg_base = _fit(img, int(W * _FG_W), int(top_area * _FG_H))  # whole pipe, fitted
    for i in range(n):
        p = i / max(1, n - 1)
        # gentle zoom on the pipe only (bg stays put); capped so it never clips
        if motion == "ken_burns":
            s = 1.0 + 0.05 * p
            fg = fg_base.resize((int(fg_base.width * s), int(fg_base.height * s)), Image.LANCZOS)
        else:
            fg = fg_base
        frame = bg.copy()
        fx = (W - fg.width) // 2
        fy = (top_area - fg.height) // 2
        frame.paste(fg, (max(0, fx), max(0, fy)))
        frames.append(np.asarray(_overlay(frame, overlay)))
    return frames


def render_reel(reel_json: Path, out_mp4: Path) -> bool:
    import imageio.v2 as imageio

    data = json.loads(reel_json.read_text(encoding="utf-8"))
    writer = imageio.get_writer(
        out_mp4, fps=FPS, codec="libx264", quality=8,
        pixelformat="yuv420p", macro_block_size=8,
    )
    wrote_any = False
    try:
        for shot in data.get("shots", []):
            url = shot.get("image_url")
            img = None
            if url and Path(url).is_file():
                try:
                    img = _open_rgb(url)
                except Exception:
                    img = None
            for frame in _shot_frames(img, float(shot.get("seconds", 2.0)),
                                      shot.get("overlay", ""), shot.get("motion", "cut")):
                writer.append_data(frame)
                wrote_any = True
    finally:
        writer.close()
    return wrote_any


def convert_photos(source_folder: Path, out_dir: Path) -> int:
    """HEIC/any -> JPG for posting. Returns count converted."""
    from .folder_source import _IMAGE_EXTS
    out_dir.mkdir(parents=True, exist_ok=True)
    imgs = sorted(p for p in source_folder.iterdir()
                  if p.is_file() and p.suffix.lower() in _IMAGE_EXTS)
    count = 0
    for i, p in enumerate(imgs):
        try:
            img = _open_rgb(p)
        except Exception:
            continue
        img.save(out_dir / f"{i:02d}.jpg", "JPEG", quality=88, optimize=True)
        count += 1
    return count


def render_all(root: str | Path) -> dict[str, int]:
    root = Path(root)
    marketing = root / "_marketing"
    if not marketing.is_dir():
        raise NotADirectoryError(f"no _marketing folder in {root} — run `python -m marketing` first")
    reels, photos = 0, 0
    for pipe_out in sorted(p for p in marketing.iterdir() if p.is_dir()):
        reel_json = pipe_out / "reel.json"
        if not reel_json.is_file():
            continue
        if render_reel(reel_json, pipe_out / "reel.mp4"):
            reels += 1
        source = root / pipe_out.name
        if source.is_dir():
            photos += convert_photos(source, pipe_out / "photos")
    return {"reels": reels, "photos": photos, "out": str(marketing)}


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="marketing.render",
                                 description="Render reel.mp4 + JPG photos from batch output.")
    ap.add_argument("root", help=r'the pipes root, e.g. "C:\FaridunhillPipes"')
    args = ap.parse_args(argv)
    if not _HEIC:
        print("WARNING: pillow-heif not installed — HEIC photos will be skipped. "
              "Run: pip install pillow-heif")
    report = render_all(args.root)
    print(f"Rendered {report['reels']} reels, converted {report['photos']} photos -> {report['out']}")
    print("Each pipe now has reel.mp4 and a photos\\ folder of JPGs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
