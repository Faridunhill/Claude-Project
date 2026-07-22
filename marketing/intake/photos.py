"""Photo checklist ingest — scan an item folder, assign roles from
filenames, and report checklist gaps. Reports, never blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ..genome.schema import MediaItem
from ..genome.vocab import FieldSource, MediaRole
from .conventions import CHECKLIST, MIN_FRAMES, PHOTO_EXTS, ROLE_TOKENS

_SEQ_RE = re.compile(r"^(\d+)")


@dataclass
class PhotoScan:
    media: list[MediaItem] = field(default_factory=list)
    #: role -> how the role was decided (human filename vs fallback)
    role_sources: dict[str, FieldSource] = field(default_factory=dict)
    missing_critical: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)
    frame_count: int = 0

    @property
    def ok(self) -> bool:
        return not self.missing_critical and self.frame_count >= MIN_FRAMES

    def report(self) -> str:
        lines = [f"frames: {self.frame_count} (min {MIN_FRAMES})"]
        for gap in self.missing_critical:
            lines.append(f"CRITICAL gap: {gap}")
        for gap in self.missing_optional:
            lines.append(f"optional gap: {gap}")
        if self.ok:
            lines.append("checklist: PASS")
        return "\n".join(lines)


def _role_for(filename: str) -> tuple[MediaRole, FieldSource]:
    stem = Path(filename).stem.lower()
    for token, role in ROLE_TOKENS.items():
        if token in stem:
            return role, FieldSource.HUMAN  # named by the photographer
    return MediaRole.ANGLE, FieldSource.INFERRED  # fallback, marked as such


def _seq_for(filename: str, default: int) -> int:
    m = _SEQ_RE.match(Path(filename).stem)
    return int(m.group(1)) if m else default


def scan_photos(item_dir: Path) -> PhotoScan:
    """Scan one SKU folder for photos; assign roles; report gaps."""
    scan = PhotoScan()
    files = sorted(
        p for p in item_dir.iterdir()
        if p.is_file() and p.suffix.lower() in PHOTO_EXTS
    )
    for i, path in enumerate(files):
        role, src = _role_for(path.name)
        scan.media.append(
            MediaItem(url=str(path), role=role, seq=_seq_for(path.name, i))
        )
        scan.role_sources[str(path)] = src
    scan.frame_count = len(scan.media)

    present = {m.role for m in scan.media}
    for role, (label, critical) in CHECKLIST.items():
        if role not in present:
            (scan.missing_critical if critical else scan.missing_optional).append(label)
    return scan
