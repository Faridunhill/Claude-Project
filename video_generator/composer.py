import math
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import config

try:
    from moviepy import (
        AudioFileClip,
        CompositeVideoClip,
        ImageClip,
        VideoFileClip,
        concatenate_audioclips,
        concatenate_videoclips,
    )
except ImportError as e:
    raise ImportError("moviepy>=2.0 is required. Run: pip install moviepy>=2.0") from e


# ── Text rendering helpers ────────────────────────────────────────────────────

def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def _scale(base: int, canvas_w: int, reference: int = 1080) -> int:
    return max(16, int(base * canvas_w / reference))


def make_text_image(
    text: str,
    canvas_size: tuple[int, int],
    font_path: str,
    font_size: int,
    text_color: tuple,
    bg_color: tuple | None = None,
    align: str = "center",
    padding: int = 20,
    max_width_fraction: float = 0.9,
) -> np.ndarray:
    W, H = canvas_size
    max_w = int(W * max_width_fraction) - padding * 2
    font = _load_font(font_path, font_size)

    # Word-wrap
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        test = " ".join(current + [word])
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] > max_w and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))

    line_h = font_size + 8
    block_h = line_h * len(lines) + padding * 2
    block_w = max((font.getbbox(l)[2] for l in lines), default=100) + padding * 2

    img = Image.new("RGBA", (block_w, block_h), (0, 0, 0, 0))
    if bg_color is not None:
        img = Image.new("RGBA", (block_w, block_h), bg_color)

    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        y = padding + i * line_h
        if align == "center":
            bbox = font.getbbox(line)
            x = (block_w - (bbox[2] - bbox[0])) // 2
        else:
            x = padding
        draw.text((x, y), line, font=font, fill=text_color)

    return np.array(img)


def make_text_clip(text: str, canvas_size: tuple[int, int], duration: float, **kw) -> ImageClip:
    arr = make_text_image(text, canvas_size, **kw)
    return ImageClip(arr, duration=duration)


# ── Background builders ───────────────────────────────────────────────────────

def _build_gradient_bg(W: int, H: int, duration: float) -> ImageClip:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    top = config.MAHOGANY_LIGHT_RGB
    bottom = (10, 5, 3)
    for y in range(H):
        t = y / H
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    draw.rectangle([0, 0, W - 1, 3], fill=config.GOLD_RGB)
    draw.rectangle([0, H - 4, W - 1, H - 1], fill=config.GOLD_RGB)
    return ImageClip(np.array(img), duration=duration)


def _stitch_footage(clips: list[dict], W: int, H: int, total_duration: float) -> Any:
    video_clips = []
    for c in clips:
        try:
            vc = VideoFileClip(c["path"]).without_audio()
            # Crop/resize to fill target dimensions
            clip_ratio = vc.w / vc.h
            target_ratio = W / H
            if clip_ratio > target_ratio:
                new_w = int(vc.h * target_ratio)
                x1 = (vc.w - new_w) // 2
                vc = vc.cropped(x1=x1, y1=0, x2=x1 + new_w, y2=vc.h)
            else:
                new_h = int(vc.w / target_ratio)
                y1 = (vc.h - new_h) // 2
                vc = vc.cropped(x1=0, y1=y1, x2=vc.w, y2=y1 + new_h)
            vc = vc.resized((W, H))
            video_clips.append(vc)
        except Exception:
            continue

    if not video_clips:
        return None

    # Loop until we exceed total_duration
    looped = []
    acc = 0.0
    i = 0
    while acc < total_duration:
        vc = video_clips[i % len(video_clips)]
        remaining = total_duration - acc
        if vc.duration > remaining:
            vc = vc.subclipped(0, remaining)
        looped.append(vc)
        acc += vc.duration
        i += 1

    return concatenate_videoclips(looped)


def _build_background(footage_clips: list[dict], W: int, H: int, total_duration: float) -> Any:
    if footage_clips:
        bg = _stitch_footage(footage_clips, W, H, total_duration)
        if bg:
            # Darken footage for overlay legibility
            dark = ImageClip(
                np.zeros((H, W, 4), dtype=np.uint8),
                duration=total_duration,
            )
            dark_arr = np.zeros((H, W, 4), dtype=np.uint8)
            dark_arr[:, :, 3] = 120  # semi-transparent black
            dark_overlay = ImageClip(dark_arr, duration=total_duration)
            return CompositeVideoClip([bg, dark_overlay], size=(W, H))
    return _build_gradient_bg(W, H, total_duration)


# ── Brand overlay builders ────────────────────────────────────────────────────

def _build_brand_bar(W: int, H: int, total_duration: float) -> ImageClip:
    bar_h = _scale(60, W)
    bar = Image.new("RGBA", (W, bar_h), config.MAHOGANY_RGB + (210,))
    draw = ImageDraw.Draw(bar)
    draw.line([(0, bar_h - 2), (W, bar_h - 2)], fill=config.GOLD_RGB, width=2)
    font = _load_font(config.FONT_SERIF_BOLD, _scale(22, W))
    text = config.STORE_NAME
    bbox = font.getbbox(text)
    x = (W - (bbox[2] - bbox[0])) // 2
    draw.text((x, 14), text, font=font, fill=config.GOLD_RGB + (255,))
    return ImageClip(np.array(bar), duration=total_duration).with_position((0, 0))


def _build_segment_overlays(
    seg: dict,
    tts: dict,
    W: int,
    H: int,
    t_start: float,
    seg_duration: float,
) -> list[ImageClip]:
    clips = []
    style = seg["style"]
    display_text = seg["display_text"]

    if style == "title":
        clip = make_text_clip(
            display_text,
            canvas_size=(W, H),
            duration=seg_duration,
            font_path=config.FONT_SERIF_BOLD,
            font_size=_scale(72, W),
            text_color=config.GOLD_RGB + (255,),
            bg_color=config.MAHOGANY_RGB + (190,),
            align="center",
        ).with_position("center").with_start(t_start)
        clips.append(clip)

    elif style == "subtitle":
        font_size = _scale(44, W)
        y_pos = int(H * 0.70)
        clip = make_text_clip(
            display_text,
            canvas_size=(W - 80, font_size + 50),
            duration=seg_duration,
            font_path=config.FONT_SERIF,
            font_size=font_size,
            text_color=config.PARCHMENT_RGB + (255,),
            bg_color=config.MAHOGANY_RGB + (200,),
            padding=14,
        ).with_position((40, y_pos)).with_start(t_start)
        clips.append(clip)

    elif style == "price":
        badge = make_text_clip(
            display_text,
            canvas_size=(320, 100),
            duration=seg_duration,
            font_path=config.FONT_SERIF_BOLD,
            font_size=_scale(48, W),
            text_color=config.MAHOGANY_RGB + (255,),
            bg_color=config.GOLD_RGB + (230,),
            align="center",
        ).with_position((W - 340, 80)).with_start(t_start)
        clips.append(badge)

        # Also show the text in lower display area
        sub = make_text_clip(
            display_text,
            canvas_size=(W - 80, _scale(44, W) + 50),
            duration=seg_duration,
            font_path=config.FONT_SERIF,
            font_size=_scale(44, W),
            text_color=config.PARCHMENT_RGB + (255,),
            bg_color=config.MAHOGANY_RGB + (200,),
            padding=14,
        ).with_position((40, int(H * 0.70))).with_start(t_start)
        clips.append(sub)

    elif style == "cta":
        pass  # CTA card is built separately as a full-screen overlay

    # Subtitle chunks for all non-CTA segments
    if style != "cta":
        subtitle_clips = _build_subtitle_chunks(tts["word_timings"], W, H, t_start)
        clips.extend(subtitle_clips)

    return clips


def _build_subtitle_chunks(
    word_timings: list[dict], W: int, H: int, seg_start: float
) -> list[ImageClip]:
    clips = []
    chunk_size = 5
    y_pos = int(H * 0.83)
    font_size = _scale(32, W)

    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i: i + chunk_size]
        if not chunk:
            continue
        text = " ".join(w["word"] for w in chunk)
        t_start = seg_start + chunk[0]["start_sec"]
        t_end = seg_start + chunk[-1]["end_sec"]
        duration = max(t_end - t_start, 0.15)

        clip = make_text_clip(
            text,
            canvas_size=(W - 60, font_size + 30),
            duration=duration,
            font_path=config.FONT_BODY,
            font_size=font_size,
            text_color=config.PARCHMENT_RGB + (255,),
            bg_color=(0, 0, 0, 140),
            padding=10,
        ).with_position((30, y_pos)).with_start(t_start)
        clips.append(clip)

    return clips


def _build_cta_card(W: int, H: int, duration: float, t_start: float) -> ImageClip:
    card_h = int(H * 0.28)
    card_w = W - 40
    y = H - card_h - 30

    card = Image.new("RGBA", (card_w, card_h), config.GOLD_RGB + (245,))
    draw = ImageDraw.Draw(card)

    # Gold border line at top
    draw.rectangle([0, 0, card_w - 1, 3], fill=config.MAHOGANY_RGB)

    font_large = _load_font(config.FONT_SERIF_BOLD, _scale(58, W))
    font_small = _load_font(config.FONT_SERIF, _scale(32, W))

    # "SHOP NOW"
    shop_text = "SHOP NOW"
    bbox = font_large.getbbox(shop_text)
    x = (card_w - (bbox[2] - bbox[0])) // 2
    draw.text((x, 18), shop_text, font=font_large, fill=config.MAHOGANY_RGB)

    # URL
    url_text = config.STORE_URL
    bbox2 = font_small.getbbox(url_text)
    x2 = (card_w - (bbox2[2] - bbox2[0])) // 2
    y2 = 18 + _scale(58, W) + 10
    draw.text((x2, y2), url_text, font=font_small, fill=config.MAHOGANY_LIGHT_RGB)

    return ImageClip(np.array(card), duration=duration).with_position((20, y)).with_start(t_start)


def _build_product_frame(
    image_url: str, W: int, H: int, t_start: float, duration: float, video_format: str
) -> ImageClip | None:
    try:
        req = urllib.request.Request(
            image_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; faridunhill-video-gen/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            img_bytes = resp.read()
        import io
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    except Exception:
        return None

    target_w = int(W * 0.30)
    ratio = target_w / img.width
    target_h = int(img.height * ratio)
    img = img.resize((target_w, target_h), Image.LANCZOS)

    border = 3
    framed = Image.new("RGBA", (target_w + border * 2, target_h + border * 2), config.GOLD_RGB + (255,))
    framed.paste(img, (border, border))

    if video_format == "vertical":
        x = W - framed.width - 40
        y = int(H * 0.30)
    elif video_format == "landscape":
        x = 60
        y = int(H * 0.25)
    else:
        x = W - framed.width - 40
        y = int(H * 0.28)

    return ImageClip(np.array(framed), duration=duration).with_position((x, y)).with_start(t_start)


def _build_audio_track(tts_results: list[dict]) -> Any:
    audio_clips = [AudioFileClip(r["audio_path"]) for r in tts_results]
    return concatenate_audioclips(audio_clips)


# ── Main composer ─────────────────────────────────────────────────────────────

def compose_video(
    script: dict,
    tts_results: list[dict],
    footage_clips: list[dict],
    product: dict | None,
    video_format: str,
    output_path: str,
) -> str:
    W, H = config.VIDEO_FORMATS[video_format]
    total_duration = sum(r["duration_sec"] for r in tts_results)
    cta_duration = 6.0
    main_duration = total_duration

    # ── Background ────────────────────────────────────────────────────
    background = _build_background(footage_clips, W, H, main_duration)

    # ── Brand bar ─────────────────────────────────────────────────────
    brand_bar = _build_brand_bar(W, H, main_duration)

    # ── Segment overlays ──────────────────────────────────────────────
    overlay_clips: list[ImageClip] = [brand_bar]
    t_cursor = 0.0

    for seg, tts in zip(script["segments"], tts_results):
        seg_duration = tts["duration_sec"]

        if seg["style"] == "cta":
            # CTA gets a full card overlay at the bottom
            cta_card = _build_cta_card(W, H, seg_duration, t_cursor)
            overlay_clips.append(cta_card)
            # Subtitle for CTA text
            if tts["word_timings"]:
                sub_clips = _build_subtitle_chunks(tts["word_timings"], W, H, t_cursor)
                overlay_clips.extend(sub_clips)
        else:
            seg_clips = _build_segment_overlays(seg, tts, W, H, t_cursor, seg_duration)
            overlay_clips.extend(seg_clips)

        t_cursor += seg_duration

    # ── Product image frame (shown after the hook) ────────────────────
    if product and product.get("images"):
        hook_end = tts_results[0]["duration_sec"] if tts_results else 0.0
        img_duration = main_duration - hook_end - (tts_results[-1]["duration_sec"] if tts_results else 0)
        img_duration = max(img_duration, 3.0)
        frame = _build_product_frame(
            product["images"][0], W, H,
            t_start=hook_end,
            duration=img_duration,
            video_format=video_format,
        )
        if frame:
            overlay_clips.append(frame)

    # ── Composite ─────────────────────────────────────────────────────
    final = CompositeVideoClip([background] + overlay_clips, size=(W, H))

    # ── Audio ─────────────────────────────────────────────────────────
    audio = _build_audio_track(tts_results)
    final = final.with_audio(audio)

    # ── Export ────────────────────────────────────────────────────────
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        output_path,
        fps=config.FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        logger="bar",
    )

    return output_path
