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
