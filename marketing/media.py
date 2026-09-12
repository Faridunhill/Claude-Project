"""Photo cache — remote listing images -> local files ffmpeg can read.

The catalog stores Etsy CDN urls (`https://i.etsystatic.com/...`).
ffmpeg's `zoompan` filter needs real files on disk, so the nightly job
downloads each photo once into `marketing/out/photos/` and reuses it
forever after. The cache key is the url hash: the same photo is never
fetched twice, and a re-run costs nothing.

OFFLINE IS NOT AN ERROR. If a download fails (no network, CDN blocked,
url rotted), the item is reported as unfetched and simply skipped for
video today — the run continues and the caption still gets written.
A marketing run must never abort because one photo was unreachable.
"""

from __future__ import annotations

import hashlib
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

_USER_AGENT = "faridunhill-marketing/1.0 (+local nightly job)"
_TIMEOUT_S = 20


@dataclass(frozen=True)
class FetchResult:
    url: str
    path: Optional[str]      # local file, or None when unavailable
    cached: bool             # True when it was already on disk
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.path is not None


def cache_name(url: str) -> str:
    """Stable filename for a url: <16 hex>.<ext>."""
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    suffix = Path(url.split("?", 1)[0]).suffix.lower()
    if suffix not in (".jpg", ".jpeg", ".png", ".webp"):
        suffix = ".jpg"
    return f"{digest}{suffix}"


def _download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as response:
        tmp = dest.with_suffix(dest.suffix + ".part")
        with open(tmp, "wb") as fh:
            shutil.copyfileobj(response, fh)
        # Atomic rename: a half-written photo is never left in the cache
        # for a later run to hand to ffmpeg as if it were complete.
        tmp.replace(dest)


def fetch_photo(
    url: str,
    cache_dir: str | Path,
    downloader: Optional[Callable[[str, Path], None]] = None,
) -> FetchResult:
    """Return a local path for `url`, downloading it once if needed.

    `downloader` is injected by the tests so the suite never touches
    the network.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    if not url:
        return FetchResult(url=url, path=None, cached=False, error="empty url")

    # A local path in the catalog is already usable; pass it straight
    # through rather than pretending to download it.
    if "://" not in url:
        local = Path(url)
        if local.exists():
            return FetchResult(url=url, path=str(local), cached=True)
        return FetchResult(url=url, path=None, cached=False, error="local file not found")

    dest = cache_dir / cache_name(url)
    if dest.exists() and dest.stat().st_size > 0:
        return FetchResult(url=url, path=str(dest), cached=True)

    try:
        (downloader or _download)(url, dest)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return FetchResult(url=url, path=None, cached=False, error=f"{type(exc).__name__}: {exc}")

    if not dest.exists() or dest.stat().st_size == 0:
        return FetchResult(url=url, path=None, cached=False, error="empty download")
    return FetchResult(url=url, path=str(dest), cached=False)


def fetch_all(
    urls: list[str],
    cache_dir: str | Path,
    downloader: Optional[Callable[[str, Path], None]] = None,
) -> list[FetchResult]:
    return [fetch_photo(url, cache_dir, downloader) for url in urls]
