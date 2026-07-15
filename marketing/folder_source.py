"""Folder adapter — read `C:\\FaridunhillPipes\\<pipe>\\` into the pipeline.

This is a concrete `ItemAssetsSource` for the common pre-Eye case: each
product is a folder of photos on disk (plus, optionally, a small notes
file of human facts). It lets the whole marketing pipeline run locally
against real folders before the automated Eye (itemassets.db) is wired —
without touching `adapter_itemassets.get_source()`, which stays the switch
point for the real database.

Layout expected (nothing is mandatory except the folder itself):

    FaridunhillPipes/
      Dunhill Cumberland 41031 .../      <- one folder per pipe
        hero.jpg  angle1.jpg  stamp.jpg  flaw.jpg  ...   <- photos
        pipe.txt   (optional)            <- human facts, key: value lines

Photo ROLES are inferred from filenames (hero/stamp/flaw/scale/group);
anything unrecognised is an ANGLE, and if no file says "hero" the first
photo becomes the hero. The folder NAME seeds brand + model when no notes
file overrides them. Facts are never invented — a missing fact stays a gap.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .genome.adapter_itemassets import ItemAssets, ItemAssetsSource, MediaAsset
from .genome.vocab import MediaRole

_IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff",
    ".heic", ".heif",   # iPhone default — common in on-disk pipe folders
}

# Longest-match brand table (multi-word brands must win over their first token).
_KNOWN_BRANDS = [
    "Danske Club", "Kong Christian", "Kapp & Peterson",
    "Amphora", "Barling", "Dunhill", "Peterson", "Stanwell", "Stanweel",
    "Winslow", "Vauen", "GBD", "Chacom", "Savinelli", "Charatan",
]

_ROLE_HINTS = [
    (MediaRole.HERO, ("hero", "main", "front", "cover", "_1", "-1", " 1")),
    (MediaRole.STAMPING, ("stamp", "nomen", "mark", "logo", "hallmark", "shank")),
    (MediaRole.FLAW, ("flaw", "damage", "tooth", "crack", "chip", "wear", "oxid")),
    (MediaRole.SCALE, ("scale", "ruler", "size", "weight", "measure", "mm")),
    (MediaRole.GROUP, ("group", "set", "box", "bag", "case", "all")),
]


def infer_role(filename: str) -> MediaRole:
    """Role from filename hints alone; ANGLE if nothing matches. The
    'first photo becomes hero when none is named hero' fallback is the
    adapter's job (see FolderItemAssets.get), so an explicit hero.jpg is
    never lost to an alphabetically-earlier angle shot."""
    stem = filename.lower()
    for role, hints in _ROLE_HINTS:
        if any(h in stem for h in hints):
            return role
    return MediaRole.ANGLE


def parse_folder_name(name: str) -> tuple[Optional[str], Optional[str]]:
    """(brand, model_line) from a folder name; longest known brand wins."""
    cleaned = " ".join(name.split())
    low = cleaned.lower()
    for brand in sorted(_KNOWN_BRANDS, key=len, reverse=True):
        if low.startswith(brand.lower()):
            remainder = cleaned[len(brand):].strip(" -,–—")
            return brand, (remainder or None)
    # unknown brand: first token as a weak brand guess, rest as model
    parts = cleaned.split()
    if not parts:
        return None, None
    return parts[0], (" ".join(parts[1:]) or None)


def _sorted_images(folder: Path) -> list[Path]:
    imgs = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in _IMAGE_EXTS]
    return sorted(imgs, key=lambda p: p.name.lower())


class FolderItemAssets(ItemAssetsSource):
    """Maps `<root>/<sku-folder>/` to ItemAssets. SKU = the folder name."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        if not self.root.is_dir():
            raise NotADirectoryError(f"folder source root not found: {self.root}")

    def folders(self) -> list[Path]:
        return sorted((p for p in self.root.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))),
                      key=lambda p: p.name.lower())

    def get(self, sku: str) -> Optional[ItemAssets]:
        folder = self.root / sku
        if not folder.is_dir():
            return None
        images = _sorted_images(folder)
        media: list[MediaAsset] = [
            MediaAsset(url=str(img.resolve()), role=infer_role(img.name), seq=i)
            for i, img in enumerate(images)
        ]
        # Fallback: if no file was named/hinted as the hero, promote the
        # first photo — but an explicit hero.jpg always wins.
        if media and not any(m.role is MediaRole.HERO for m in media):
            first = media[0]
            media[0] = MediaAsset(url=first.url, role=MediaRole.HERO, seq=first.seq)
        # optional stamping OCR text file (stamp.txt / nomenclature.txt)
        stamping = None
        for cand in ("stamp.txt", "stamping.txt", "nomenclature.txt", "marks.txt"):
            f = folder / cand
            if f.is_file():
                stamping = f.read_text(encoding="utf-8", errors="ignore").strip() or None
                break
        return ItemAssets(sku=sku, media=media, stamping_ocr=stamping)
