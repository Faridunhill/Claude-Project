"""THE CONNECTOR — Priority 1 (itemassets.db / the Eye) plugs in HERE.
════════════════════════════════════════════════════════════════════════

Marketing consumes Priority 1 outputs as a CLIENT (handoff §DEPENDENCIES):
it reads them; it never rebuilds, retrains, or modifies them.

This module is the ONLY place in the marketing system that knows
Priority 1 exists. Everything else (schema, store, QA gate, generators)
talks to the `ItemAssetsSource` interface below. When Farid is next at
the PC, wiring the real database means implementing ONE class in THIS
file — nothing else changes.

WHAT PRIORITY 1 MUST SUPPLY (the interface contract):

  1. media_for(sku)        -> photo URLs/paths with roles, from the
                              intake photo checklist
  2. vision_claims(sku)    -> the Eye's per-field claims WITH confidence
                              (DINOv3 stack, 95.1% Top-1) — consumed by
                              the QA gate's confidence rule
  3. stamping_ocr(sku)     -> verbatim OCR text of stamping macros —
                              the second witness in the QA gate's
                              corroboration rule

HOW TO WIRE IT (when at the PC):
  * If itemassets.db is SQLite: implement SqliteItemAssets below with
    the real table/column names, and set ITEMASSETS_DB_PATH in the
    environment or control.yaml.
  * If Priority 1 exposes an API/files instead: implement the same
    three methods against that surface.
  * Then flip `get_source()` to return your implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from .vocab import MediaRole


@dataclass(frozen=True)
class VisionClaim:
    """One claim from the Eye about one genome field."""

    field_path: str            # e.g. "brand", "unique_physical.era"
    value: object              # the claimed value
    confidence: float          # 0.0–1.0 — QA gate routes Tier A < 0.90 to review
    model_version: str = ""    # for calibration tracking


@dataclass(frozen=True)
class MediaAsset:
    url: str
    role: MediaRole
    seq: int = 0


@dataclass(frozen=True)
class ItemAssets:
    """Everything Priority 1 knows about one SKU that marketing consumes."""

    sku: str
    media: list[MediaAsset] = field(default_factory=list)
    vision_claims: list[VisionClaim] = field(default_factory=list)
    stamping_ocr: Optional[str] = None
    voice_transcript: Optional[str] = None


class ItemAssetsSource(ABC):
    """The interface the marketing system codes against."""

    @abstractmethod
    def get(self, sku: str) -> Optional[ItemAssets]:
        """Return Priority 1's data for a SKU, or None if unknown."""


class NotConnected(Exception):
    """Raised until the real Priority 1 source is wired in."""

    def __init__(self) -> None:
        super().__init__(
            "itemassets.db is not connected yet. Implement ItemAssetsSource "
            "in marketing/genome/adapter_itemassets.py (see module docstring) "
            "— one class, three data kinds: media, vision claims, stamping OCR."
        )


class PlaceholderSource(ItemAssetsSource):
    """Default until the PC-side database is wired. Fails loudly and
    helpfully — never silently returns empty data (a silent empty would
    read as 'this item has no photos', which is a lie)."""

    def get(self, sku: str) -> Optional[ItemAssets]:
        raise NotConnected()


class StaticSource(ItemAssetsSource):
    """In-memory source for tests and for manual/CSV-driven intake before
    Priority 1 is connected. Also the reference implementation showing
    exactly what the real adapter must return."""

    def __init__(self, items: dict[str, ItemAssets]):
        self._items = dict(items)

    def get(self, sku: str) -> Optional[ItemAssets]:
        return self._items.get(sku)


def get_source() -> ItemAssetsSource:
    """Swap the return value for the real implementation when wiring
    Priority 1. Single switch point; nothing else in the system changes."""
    return PlaceholderSource()
