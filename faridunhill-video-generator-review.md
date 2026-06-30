# faridunhill.com — Video Marketing Generator
### For Team Review

---

## Overview

A MoneyPrinterTurbo-inspired Python CLI tool purpose-built for **faridunhill.com**.
Input: a product ID/name or department → Output: a branded MP4 ready for Instagram Reels, TikTok & Facebook.

## Pipeline

```
Product JSON → Claude API (script) → Edge TTS (voiceover) → Pexels (B-roll) → MoviePy (compose) → MP4
```

## Directory Structure

```
video_generator/
├── __init__.py
├── config.py        ← Brand colors, paths, API key loading
├── products.py      ← Reads data/products/*.json catalog
├── llm.py           ← Claude API: generates 30-60s marketing script
├── tts.py           ← Edge TTS: voiceover MP3 + word-level subtitle timing
├── footage.py       ← Pexels: search + download B-roll clips (cached)
├── composer.py      ← MoviePy 2.x + Pillow: assembles final video
├── run.py           ← CLI entry point
├── requirements.txt
├── output/          ← Generated MP4s (gitignored)
└── .cache/          ← Downloaded Pexels clips (gitignored)
```

## Usage

```bash
# Install
pip install -r video_generator/requirements.txt

# Set keys
export ANTHROPIC_API_KEY=sk-ant-...
export PEXELS_API_KEY=...        # free at pexels.com/api

# Single product — vertical (Instagram Reels / TikTok / Facebook)
python -m video_generator.run --product pipe-001 --format vertical --verbose

# Department campaign
python -m video_generator.run --department cigars --format vertical

# Preview script only (no video rendered)
python -m video_generator.run --product "Dunhill Shell Briar" --dry-run
```

## API Keys Needed

| Key | Required | Where to get |
|-----|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | console.anthropic.com |
| `PEXELS_API_KEY` | No (uses gradient bg fallback) | pexels.com/api (free) |

---

---

## `requirements.txt` — Dependencies

```text
anthropic>=0.28.0
moviepy>=2.0.0
edge-tts>=6.1.9
Pillow>=10.3.0
requests>=2.31.0

```

---

## `config.py` — Brand Config & Settings

```py
import glob
import os
from pathlib import Path

# ── Brand palette (mirrors tailwind.config.ts) ────────────────────────────────
MAHOGANY = "#2C1810"
MAHOGANY_LIGHT = "#3D2317"
GOLD = "#C9A84C"
GOLD_PALE = "#E8D5A3"
PARCHMENT = "#F5EDD6"
LEATHER = "#8B6B4A"

MAHOGANY_RGB = (44, 24, 16)
MAHOGANY_LIGHT_RGB = (61, 35, 23)
GOLD_RGB = (201, 168, 76)
GOLD_PALE_RGB = (232, 213, 163)
PARCHMENT_RGB = (245, 237, 214)
LEATHER_RGB = (139, 107, 74)

# ── Video settings ────────────────────────────────────────────────────────────
VIDEO_FORMATS = {
    "vertical": (1080, 1920),   # Instagram Reels, TikTok, Facebook Reels
    "landscape": (1920, 1080),  # YouTube
    "square": (1080, 1080),     # Instagram feed
}
FPS = 30

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent
OUTPUT_DIR = str(_HERE / "output")
CACHE_DIR = str(_HERE / ".cache")
MUSIC_DIR = str(_HERE / "music")
DATA_DIR = str(_HERE.parent / "data" / "products")

# ── Store info ────────────────────────────────────────────────────────────────
STORE_URL = "faridunhill.com"
STORE_NAME = "FARIDUNHILL"

# ── AI / TTS ──────────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-6"
TTS_VOICE = "en-GB-RyanNeural"
TTS_RATE = "-5%"   # slightly slower for premium feel

# ── Department → JSON filename mapping ───────────────────────────────────────
DEPT_FILES = {
    "tobacco-pipes": "pipes.json",
    "pipe-tobacco": "tobacco.json",
    "cigars": "cigars.json",
    "cigar-accessories": "cigar-accessories.json",
    "pipe-accessories": "pipe-accessories.json",
    "leather-bags": "leather-bags.json",
    "vaping": "vaping.json",
    "lighters": "lighters.json",
    "gift-sets": "gift-sets.json",
}

# ── Pexels fallback search terms per department ───────────────────────────────
PEXELS_SEARCH_MAP = {
    "tobacco-pipes": ["briar pipe smoking gentleman", "tobacco pipe classic"],
    "pipe-tobacco": ["tobacco tin vintage", "pipe tobacco blend"],
    "cigars": ["premium cigar luxury", "cigar lounge close up"],
    "cigar-accessories": ["cigar cutter luxury", "humidor cigars"],
    "pipe-accessories": ["pipe tools leather", "tobacco pouch antique"],
    "leather-bags": ["full grain leather bag", "luxury leather craft"],
    "vaping": ["vape device modern", "pod kit sleek"],
    "lighters": ["luxury lighter flame", "butane lighter close"],
    "gift-sets": ["luxury gift box premium", "gentleman gift unwrap"],
}


def _find_font(candidates: list[str]) -> str:
    search_dirs = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        str(Path.home() / ".fonts"),
        "/Library/Fonts",
        "/System/Library/Fonts",
        "C:/Windows/Fonts",
    ]
    for name in candidates:
        for d in search_dirs:
            matches = glob.glob(f"{d}/**/{name}", recursive=True)
            if matches:
                return matches[0]
    # Pillow always ships DejaVu — find it in the pillow package data
    try:
        import PIL
        pil_dir = Path(PIL.__file__).parent
        fallback = list(pil_dir.glob("**/*DejaVuSans*.ttf"))
        if fallback:
            return str(fallback[0])
    except Exception:
        pass
    raise FileNotFoundError(
        f"No font found from candidates {candidates}. "
        "Install a font or run: apt-get install fonts-dejavu"
    )


FONT_SERIF_BOLD = _find_font([
    "PlayfairDisplay-Bold.ttf",
    "PlayfairDisplay-ExtraBold.ttf",
    "Georgia Bold.ttf",
    "Georgia-Bold.ttf",
    "DejaVuSerif-Bold.ttf",
    "DejaVuSans-Bold.ttf",
])

FONT_SERIF = _find_font([
    "PlayfairDisplay-Regular.ttf",
    "Lora-Regular.ttf",
    "Georgia.ttf",
    "DejaVuSerif.ttf",
    "DejaVuSans.ttf",
])

FONT_BODY = _find_font([
    "Lora-Regular.ttf",
    "DejaVuSans.ttf",
    "DejaVuSerif.ttf",
])


def get_anthropic_key() -> str:
    _load_dotenv()
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set.\n"
            "Export it: export ANTHROPIC_API_KEY=sk-ant-...\n"
            "Or create video_generator/.env with ANTHROPIC_API_KEY=..."
        )
    return key


def get_pexels_key() -> str | None:
    _load_dotenv()
    return os.environ.get("PEXELS_API_KEY") or None


def _load_dotenv() -> None:
    env_file = _HERE / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

```

---

## `products.py` — Product Loader

```py
import json
from pathlib import Path
from typing import Any

from . import config


Product = dict[str, Any]


def load_all_products() -> list[Product]:
    products = []
    for dept, filename in config.DEPT_FILES.items():
        path = Path(config.DATA_DIR) / filename
        if not path.exists():
            continue
        try:
            items = json.loads(path.read_text())
            products.extend(items)
        except (json.JSONDecodeError, OSError):
            continue
    return products


def load_department(department: str) -> list[Product]:
    if department not in config.DEPT_FILES:
        raise ValueError(
            f"Unknown department: {department!r}. "
            f"Valid options: {', '.join(config.DEPT_FILES)}"
        )
    path = Path(config.DATA_DIR) / config.DEPT_FILES[department]
    if not path.exists():
        raise FileNotFoundError(f"Product file not found: {path}")
    return json.loads(path.read_text())


def find_product_by_id(product_id: str, products: list[Product]) -> Product | None:
    for p in products:
        if p.get("id") == product_id:
            return p
    return None


def find_product_by_slug(slug: str, products: list[Product]) -> Product | None:
    for p in products:
        if p.get("slug") == slug:
            return p
    return None


def find_product_by_name(name: str, products: list[Product]) -> Product | None:
    name_lower = name.lower()
    for p in products:
        if name_lower in p.get("name", "").lower():
            return p
    return None


def select_single(query: str) -> Product:
    """Find a product by id, slug, or name substring across all departments."""
    all_products = load_all_products()

    found = (
        find_product_by_id(query, all_products)
        or find_product_by_slug(query, all_products)
        or find_product_by_name(query, all_products)
    )

    if not found:
        raise ValueError(
            f"No product found matching {query!r}. "
            "Try the product ID (e.g. pipe-001), slug, or part of the name."
        )
    return found


def select_featured(department: str, max_products: int = 4) -> list[Product]:
    """Return up to max_products featured, in-stock items from a department."""
    items = load_department(department)
    featured = [p for p in items if p.get("featured") and p.get("inStock", True)]
    if not featured:
        featured = [p for p in items if p.get("inStock", True)]
    return featured[:max_products]


def format_product_for_prompt(product: Product) -> dict:
    """Strip fields Claude doesn't need; format price as a string."""
    keep = {
        "name": product.get("name"),
        "brand": product.get("brand"),
        "price": f"${product['price']:.2f}" if product.get("price") else None,
        "original_price": (
            f"${product['originalPrice']:.2f}" if product.get("originalPrice") else None
        ),
        "department": product.get("department"),
        "category": product.get("category"),
        "description": product.get("description"),
        "rating": product.get("rating"),
        "tags": product.get("tags"),
    }
    # Department-specific fields
    for field in ("specs", "vitola", "size", "origin", "wrapper", "contents"):
        if product.get(field):
            keep[field] = product[field]

    return {k: v for k, v in keep.items() if v is not None}

```

---

## `llm.py` — Claude Script Generator

```py
import json
from typing import Literal

import anthropic

from . import config

_SYSTEM_PROMPT = f"""You are a copywriter for {config.STORE_URL}, a premium smoke shop with a Victorian-era aesthetic.
Your task is to write a punchy 30-60 second social media marketing video script.

Tone: Confident, literary, and aspirational — like a well-read gentleman writing copy.
Never use generic phrases like "amazing", "incredible", or "don't miss out".
Pricing should feel like a statement of quality, not a bargain pitch.
Always end with the call to action: "Shop now at {config.STORE_URL}"

Respond ONLY with valid JSON matching this exact schema — no markdown, no commentary:
{{
  "total_duration_seconds": <integer 30-60>,
  "pexels_search_query": "<3-5 word specific search term for B-roll footage>",
  "segments": [
    {{
      "index": 0,
      "type": "hook",
      "spoken_text": "<voiceover text for this segment>",
      "display_text": "<short on-screen text, max 8 words>",
      "duration_seconds": <float>,
      "style": "title"
    }}
  ]
}}

Segment types (in order):
- "hook": exactly 1 segment, 3-5s, style "title"
- "highlight": 2-4 segments, 4-8s each, style "subtitle" or "price"
- "cta": exactly 1 segment, 5-7s, style "cta"

Style values: "title", "subtitle", "price", "cta"
The last segment MUST be type "cta" with spoken_text ending in "Shop now at {config.STORE_URL}"
Use style "price" for the segment that mentions the product price.
"""


ScriptSegment = dict
VideoScript = dict


def generate_script(
    products: list[dict],
    video_format: str,
    mode: Literal["single", "department"],
    *,
    max_retries: int = 2,
) -> VideoScript:
    client = anthropic.Anthropic(api_key=config.get_anthropic_key())
    user_message = _build_user_message(products, video_format, mode)

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        message = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = message.content[0].text.strip()

        # Strip accidental markdown fences
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:].lstrip()

        try:
            script = json.loads(raw)
            _validate_script(script)
            return script
        except (json.JSONDecodeError, AssertionError, KeyError) as e:
            last_error = e
            if attempt < max_retries:
                continue

    raise ValueError(
        f"Claude returned an invalid script after {max_retries + 1} attempts: {last_error}"
    )


def _build_user_message(products: list[dict], video_format: str, mode: str) -> str:
    if mode == "single":
        product = products[0]
        return (
            f"Create a 30-45 second video script for this single product:\n\n"
            f"{json.dumps(product, indent=2)}\n\n"
            f"Video format: {video_format}\n"
            f"Hook: name the product and brand immediately.\n"
            f"Include 2-3 highlight segments: price, a standout spec or origin, and one line of brand story.\n"
            f"Keep display_text concise — it will appear as a large on-screen overlay."
        )
    else:
        return (
            f"Create a 45-60 second department campaign script featuring these {len(products)} products:\n\n"
            f"{json.dumps(products, indent=2)}\n\n"
            f"Video format: {video_format}\n"
            f"Hook: name the department category (e.g. 'Premium Tobacco Pipes').\n"
            f"Each product gets one highlight segment — focus on its most distinctive quality or price.\n"
            f"CTA segment should reference the department."
        )


def _validate_script(script: dict) -> None:
    assert "segments" in script, "Missing 'segments'"
    assert isinstance(script["segments"], list), "'segments' must be a list"
    assert len(script["segments"]) >= 2, "Need at least 2 segments"
    assert "pexels_search_query" in script, "Missing 'pexels_search_query'"
    last = script["segments"][-1]
    assert last.get("type") == "cta", "Last segment must be type 'cta'"
    for seg in script["segments"]:
        for field in ("index", "type", "spoken_text", "display_text", "duration_seconds", "style"):
            assert field in seg, f"Segment missing field: {field}"

```

---

## `tts.py` — Text-to-Speech (Edge TTS)

```py
import asyncio
from pathlib import Path
from typing import TypedDict

import edge_tts

from . import config


class WordTiming(TypedDict):
    word: str
    start_sec: float
    end_sec: float


class TTSResult(TypedDict):
    audio_path: str
    duration_sec: float
    word_timings: list[WordTiming]


def synthesize_segment(
    text: str,
    output_path: str,
    voice: str = config.TTS_VOICE,
    rate: str = config.TTS_RATE,
) -> TTSResult:
    return asyncio.run(_async_synthesize(text, output_path, voice, rate))


async def _async_synthesize(
    text: str, output_path: str, voice: str, rate: str
) -> TTSResult:
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    word_timings: list[WordTiming] = []
    audio_bytes = bytearray()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            # Edge TTS uses 100-nanosecond units
            offset_sec = chunk["offset"] / 10_000_000
            duration_sec = chunk["duration"] / 10_000_000
            word_timings.append({
                "word": chunk["text"],
                "start_sec": offset_sec,
                "end_sec": offset_sec + duration_sec,
            })

    Path(output_path).write_bytes(bytes(audio_bytes))

    total_duration = word_timings[-1]["end_sec"] if word_timings else 0.0

    # Fallback: if no word timings, estimate from text length (avg 3 chars/sec)
    if not word_timings:
        total_duration = max(len(text) / 15, 2.0)

    return {
        "audio_path": output_path,
        "duration_sec": total_duration,
        "word_timings": word_timings,
    }


def synthesize_full_script(
    script: dict,
    temp_dir: str,
    voice: str = config.TTS_VOICE,
) -> list[TTSResult]:
    results = []
    for seg in script["segments"]:
        out_path = str(Path(temp_dir) / f"seg_{seg['index']:02d}.mp3")
        result = synthesize_segment(seg["spoken_text"], out_path, voice=voice)
        results.append(result)
    return results

```

---

## `footage.py` — Pexels Footage Fetcher

```py
import hashlib
import json
from pathlib import Path
from typing import TypedDict

import requests

from . import config


class FootageClip(TypedDict):
    path: str
    duration: float
    width: int
    height: int
    source: str


def fetch_clips(
    search_query: str,
    target_duration: float,
    video_format: str,
    api_key: str | None,
    department: str | None = None,
    *,
    max_clips: int = 4,
) -> list[FootageClip]:
    if not api_key:
        return []

    width, height = config.VIDEO_FORMATS[video_format]
    orientation = "portrait" if height > width else ("square" if height == width else "landscape")

    cache_key = hashlib.md5(f"{search_query}:{orientation}".encode()).hexdigest()[:8]
    cached = _load_from_cache(cache_key)
    if cached:
        return cached

    clips = _search_and_download(search_query, orientation, api_key, cache_key, max_clips)

    # Fallback: try department default terms if Claude's query returned nothing
    if not clips and department and department in config.PEXELS_SEARCH_MAP:
        for fallback_query in config.PEXELS_SEARCH_MAP[department]:
            fb_key = hashlib.md5(f"{fallback_query}:{orientation}".encode()).hexdigest()[:8]
            clips = _search_and_download(fallback_query, orientation, api_key, fb_key, max_clips)
            if clips:
                break

    if clips:
        _save_to_cache(cache_key, clips)

    return clips


def _search_and_download(
    query: str, orientation: str, api_key: str, cache_key: str, max_clips: int
) -> list[FootageClip]:
    try:
        videos = _search_pexels(query, orientation, api_key, per_page=10)
    except requests.RequestException:
        return []

    clips = []
    for video in videos[:max_clips]:
        best = _select_best_file(video.get("video_files", []))
        if not best or not best.get("link"):
            continue
        try:
            local_path = _download_clip(best["link"], cache_key, len(clips))
        except Exception:
            continue
        clips.append({
            "path": local_path,
            "duration": float(video.get("duration", 5)),
            "width": best.get("width", 1080),
            "height": best.get("height", 1920),
            "source": "pexels",
        })

    return clips


def _search_pexels(query: str, orientation: str, api_key: str, per_page: int) -> list[dict]:
    resp = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": api_key},
        params={"query": query, "orientation": orientation, "size": "large", "per_page": per_page},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("videos", [])


def _select_best_file(video_files: list[dict]) -> dict | None:
    if not video_files:
        return None
    # Prefer hd over sd, avoid uhd (too large)
    for quality in ("hd", "sd"):
        candidates = [f for f in video_files if f.get("quality") == quality]
        if candidates:
            return sorted(candidates, key=lambda f: f.get("width", 0))[0]
    return video_files[0]


def _download_clip(url: str, cache_key: str, index: int) -> str:
    dest = Path(config.CACHE_DIR) / f"{cache_key}_{index}.mp4"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return str(dest)
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return str(dest)


def _load_from_cache(cache_key: str) -> list[FootageClip] | None:
    manifest = Path(config.CACHE_DIR) / f"{cache_key}.json"
    if not manifest.exists():
        return None
    try:
        data = json.loads(manifest.read_text())
        if all(Path(c["path"]).exists() for c in data):
            return data
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def _save_to_cache(cache_key: str, clips: list[FootageClip]) -> None:
    manifest = Path(config.CACHE_DIR) / f"{cache_key}.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(clips, indent=2))

```

---

## `composer.py` — Video Composer (MoviePy + Pillow)

```py
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

```

---

## `run.py` — CLI Entry Point

```py
"""
faridunhill.com Product Marketing Video Generator

Usage:
  python -m video_generator.run --product "pipe-001" --format vertical
  python -m video_generator.run --department cigars --format vertical
  python -m video_generator.run --product "Dunhill Shell Briar" --dry-run
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

from . import config
from . import composer
from . import footage
from . import llm
from . import products
from . import tts


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="video_generator",
        description="Generate a branded marketing video for faridunhill.com products.",
    )

    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--product", "-p",
        metavar="NAME_OR_ID",
        help="Product name (fuzzy match), ID (e.g. pipe-001), or slug.",
    )
    source.add_argument(
        "--department", "-d",
        metavar="DEPT",
        choices=list(config.DEPT_FILES.keys()),
        help="Department name. Generates a multi-product campaign video.",
    )

    p.add_argument(
        "--format", "-f",
        choices=["vertical", "landscape", "square"],
        default="vertical",
        help="Output format. Default: vertical (9:16 for Reels/TikTok).",
    )
    p.add_argument(
        "--max-products",
        type=int,
        default=4,
        metavar="N",
        help="Max products in a department campaign. Default: 4.",
    )
    p.add_argument(
        "--no-footage",
        action="store_true",
        help="Skip Pexels and use brand gradient background only.",
    )
    p.add_argument(
        "--output-dir",
        default=config.OUTPUT_DIR,
        metavar="PATH",
        help=f"Output directory. Default: {config.OUTPUT_DIR}",
    )
    p.add_argument(
        "--voice",
        default=config.TTS_VOICE,
        help=f"Edge TTS voice name. Default: {config.TTS_VOICE}",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated script as JSON without producing a video.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print progress at each pipeline stage.",
    )

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log = print if args.verbose else lambda *a, **kw: None

    # ── 1. Load product(s) ────────────────────────────────────────────────────
    if args.product:
        mode = "single"
        log(f"[1/6] Finding product: {args.product!r}")
        try:
            product = products.select_single(args.product)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        product_list = [product]
        dept = product.get("department")
        log(f"      Found: {product['name']} (${product.get('price', '?'):.2f})")
    else:
        mode = "department"
        dept = args.department
        log(f"[1/6] Loading department: {dept}")
        try:
            product_list = products.select_featured(dept, args.max_products)
        except (ValueError, FileNotFoundError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        product = None
        if not product_list:
            print(f"ERROR: No in-stock products found in department '{dept}'.", file=sys.stderr)
            sys.exit(1)
        log(f"      Selected {len(product_list)} products")

    prompt_products = [products.format_product_for_prompt(p) for p in product_list]

    # ── 2. Generate script ────────────────────────────────────────────────────
    log("[2/6] Generating marketing script with Claude...")
    try:
        script = llm.generate_script(prompt_products, args.format, mode)
    except Exception as e:
        print(f"ERROR: Script generation failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(json.dumps(script, indent=2))
        return

    log(f"      {len(script['segments'])} segments, ~{script['total_duration_seconds']}s")

    # ── 3–6: Audio + footage + compose ───────────────────────────────────────
    with tempfile.TemporaryDirectory(prefix="fh_video_") as tmpdir:

        # 3. Synthesize voiceover
        log("[3/6] Synthesizing voiceover (Edge TTS)...")
        try:
            tts_results = tts.synthesize_full_script(script, tmpdir, voice=args.voice)
        except Exception as e:
            print(f"ERROR: TTS synthesis failed: {e}", file=sys.stderr)
            sys.exit(1)
        total_audio = sum(r["duration_sec"] for r in tts_results)
        log(f"      Audio: {total_audio:.1f}s total")

        # 4. Fetch footage
        footage_clips: list[dict] = []
        if not args.no_footage:
            log("[4/6] Fetching B-roll footage from Pexels...")
            pexels_key = config.get_pexels_key()
            if pexels_key:
                footage_clips = footage.fetch_clips(
                    search_query=script["pexels_search_query"],
                    target_duration=total_audio,
                    video_format=args.format,
                    api_key=pexels_key,
                    department=dept,
                )
                log(f"      Got {len(footage_clips)} clips")
            else:
                log("      PEXELS_API_KEY not set — using brand gradient background")
        else:
            log("[4/6] Footage skipped (--no-footage)")

        # 5. Compose video
        log("[5/6] Composing video...")
        slug = product["slug"] if product else dept
        out_filename = f"{slug}_{args.format}.mp4"
        out_path = str(Path(args.output_dir) / out_filename)

        try:
            composer.compose_video(
                script=script,
                tts_results=tts_results,
                footage_clips=footage_clips,
                product=product,
                video_format=args.format,
                output_path=out_path,
            )
        except Exception as e:
            print(f"ERROR: Video composition failed: {e}", file=sys.stderr)
            sys.exit(1)

        # 6. Report
        log("[6/6] Done.")
        size_mb = Path(out_path).stat().st_size / 1_048_576
        print(f"\nVideo saved: {out_path}")
        print(f"Size:        {size_mb:.1f} MB")
        print(f"Format:      {args.format} {config.VIDEO_FORMATS[args.format]}")
        print(f"Duration:    {total_audio:.1f}s")


if __name__ == "__main__":
    main()

```
