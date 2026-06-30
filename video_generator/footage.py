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
