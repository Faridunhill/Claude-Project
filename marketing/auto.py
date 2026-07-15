"""Auto mode — new pipe in, post + video out, no asking.

    python -m marketing.auto "C:\\FaridunhillPipes"            # one pass
    python -m marketing.auto "C:\\FaridunhillPipes" --watch    # keep watching

One pass = generate listings + Instagram/TikTok posts + a rendered 9:16
reel.mp4 + JPG photos for every pipe, and leave them in
`_marketing\\<pipe>\\`. Text (listings/posts) regenerates every pass
(cheap); the expensive step — video render + HEIC->JPG — runs ONLY for a
pipe that is new or whose folder changed, tracked by a per-pipe signature.

`--watch` polls the folder on an interval: drop a new pipe folder in and
its post + video appear a moment later, untouched until you post them.

Posting itself is deliberately NOT done here — this leaves finished files
for you to review. Auto-posting to the platforms is a later, opt-in step
(it needs your account access and is the one thing worth a human's last
look before it goes public).
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Optional

from .batch import run_batch
from .render import _find_opener, convert_photos, render_reel


def _sig(folder: Path) -> str:
    files = [p for p in folder.iterdir() if p.is_file()]
    newest = max((p.stat().st_mtime_ns for p in files), default=0)
    return f"{len(files)}:{newest}"


def process(root: str | Path, *, reference_year: Optional[int] = None, force: bool = False) -> list[str]:
    """Full pass. Returns the pipes whose video/photos were (re)rendered."""
    root = Path(root)
    out = root / "_marketing"
    run_batch(root, out, reference_year=reference_year)   # cheap: all text regenerated

    rendered: list[str] = []
    for pipe_out in sorted(p for p in out.iterdir() if p.is_dir()):
        reel_json = pipe_out / "reel.json"
        source = root / pipe_out.name
        if not reel_json.is_file() or not source.is_dir():
            continue
        sig = _sig(source)
        sig_file = pipe_out / ".render_sig"
        mp4 = pipe_out / "reel.mp4"
        unchanged = (
            not force and mp4.is_file() and sig_file.is_file()
            and sig_file.read_text(encoding="utf-8") == sig
        )
        if unchanged:
            continue
        render_reel(reel_json, mp4, opener=_find_opener(source))
        convert_photos(source, pipe_out / "photos")
        sig_file.write_text(sig, encoding="utf-8")
        rendered.append(pipe_out.name)
    return rendered


def watch(root: str | Path, *, interval: int = 30, reference_year: Optional[int] = None) -> None:
    root = Path(root)
    print(f"Watching {root}\\ — drop a new pipe folder in and its post + video "
          f"will appear in _marketing\\. Press Ctrl+C to stop.")
    # first pass processes everything already present
    first = process(root, reference_year=reference_year)
    print(f"  ready: {len(first)} pipe(s) rendered." if first else "  up to date.")
    while True:
        try:
            time.sleep(interval)
            new = process(root, reference_year=reference_year)
            if new:
                print(f"  new/changed -> rendered: {', '.join(new)}")
        except KeyboardInterrupt:
            print("\nStopped watching.")
            return


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="marketing.auto",
        description="Auto-generate post + video for each pipe; leave them in _marketing.",
    )
    ap.add_argument("root", help=r'the pipes root, e.g. "C:\FaridunhillPipes"')
    ap.add_argument("--watch", action="store_true", help="keep watching for new/changed pipe folders")
    ap.add_argument("--interval", type=int, default=30, help="watch poll seconds (default 30)")
    ap.add_argument("--year", type=int, default=None, help="reference year for vintage/antique keywords")
    ap.add_argument("--force", action="store_true", help="re-render every pipe even if unchanged")
    args = ap.parse_args(argv)

    if args.watch:
        watch(args.root, interval=args.interval, reference_year=args.year)
        return 0
    rendered = process(args.root, reference_year=args.year, force=args.force)
    print(f"Done. {len(rendered)} pipe(s) rendered this pass; all posts/listings refreshed.")
    print(rf"Everything is in {Path(args.root)}\_marketing\<pipe>\ "
          "(listing.md, post-instagram.txt, post-tiktok.txt, reel.mp4, photos\\).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
