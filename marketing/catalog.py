"""Catalog adapter — the fuel line (P2.9a).

THE PROBLEM THIS SOLVES. P2.2-P2.8 built a complete marketing engine,
but nothing could run it: `genome/adapter_itemassets.get_source()`
returns `PlaceholderSource`, which raises `NotConnected` until the
Priority 1 database (itemassets.db / the Eye) is wired on the PC. So
the engine had no fuel, and the whole system idled.

Meanwhile 264 real products already live in `content/products/*.yaml` —
Farid's own imported Etsy inventory, with real SKUs, real prices, real
photographs. This module turns those files into EFFECTIVE GENOME dicts,
the exact shape `expression/copy.py`, `social/captions.py` and
`encyclopedia/flywheel.py` already consume.

Result: the marketing system runs TODAY, on the real catalog, with no
vendor, no API key and no spend. When Priority 1 is wired later it
becomes a richer source for the same pipeline — it does not replace
this one, and nothing downstream changes.

PROVENANCE HONESTY (the rule that governs this file). Every fact here
comes from a listing title and description that Farid wrote by hand
after handling the object. That makes it `FieldSource.HUMAN`, which is
why the copy generators may assert it. The adapter therefore never
invents: brand comes from an explicit allowlist (`brands.yaml`), era
only from a date the title actually states, and anything absent stays
absent. A missing field produces quieter copy — never a guess.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

import yaml

from .genome.vocab import EraBasis, FieldSource, MediaRole

CATALOG_ADAPTER_VERSION = "catalog-1.0.0"

#: Shape / form keywords. Detecting one turns "estate-pipes" into
#: "estate-pipes/billiard", which is what gives captions their specific
#: hashtags (#billiardpipe) instead of only the generic set.
_SHAPE_KEYWORDS = (
    "billiard", "dublin", "rhodesian", "bulldog", "apple", "pot",
    "brandy", "egg", "volcano", "calabash", "lovat", "canadian",
    "lumberman", "freehand", "churchwarden", "nosewarmer", "panel",
    "meerschaum", "cutter", "lighter", "ashtray", "pouch", "case",
    "stand", "humidor", "tamper", "pipe tool",
)

#: Country words a title may state. Consumer: `generate_title` builds
#: "French ... Billiard" when no brand is assertable.
_ORIGIN_KEYWORDS = {
    "french": "FR", "france": "FR", "saint-claude": "FR",
    "english": "GB", "england": "GB", "london": "GB", "british": "GB",
    "italian": "IT", "italy": "IT",
    "german": "DE", "germany": "DE", "solingen": "DE", "offenbach": "DE",
    "danish": "DK", "denmark": "DK",
    "dutch": "NL", "holland": "NL",
    "spanish": "ES", "spain": "ES", "ubrique": "ES",
    "turkish": "TR", "turkey": "TR",
    "swiss": "CH",
    "japanese": "JP", "japan": "JP",
}

#: Loose era phrases -> (min_year, max_year). Always EraBasis.STYLE:
#: the machine is reading a period word, not a stamping. STYLE makes
#: the copy generators say "mid-century", never "circa 1955".
_ERA_PHRASES = (
    ("art deco", 1920, 1939),
    ("edwardian", 1901, 1914),
    ("victorian", 1837, 1901),
    ("mid-century", 1945, 1969),
    ("mid century", 1945, 1969),
    ("midcentury", 1945, 1969),
    ("pre-war", 1918, 1939),
    ("medieval", 1300, 1600),
)

_DECADE_RANGE_RE = re.compile(r"\b(1[6-9]\d0)s\s*[-–]\s*(1[6-9]\d0|20[0-2]0)s\b")
_DECADE_RE = re.compile(r"\b(1[6-9]\d0|20[0-2]0)s\b")
_RANGE_RE = re.compile(r"\b(1[6-9]\d{2})\s*[-–]\s*(1[6-9]\d{2}|20\d{2})\b")
_YEAR_RE = re.compile(r"\b(1[6-9]\d{2}|20[0-2]\d)\b")

_NOS_TOKENS = ("new old stock", "nos", "unsmoked", "unused")


def _norm(text: str) -> str:
    """Lowercase, strip punctuation differences, collapse whitespace —
    so "Comoy's" matches "Comoys" and "Butz Choquin" matches
    "Butz-Choquin"."""
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text)


# ── brand allowlist ──────────────────────────────────────────────────

def load_brands(path: str | Path) -> list[str]:
    """Load `brands.yaml`, longest name first so multi-word brands win
    ("CTS Wolfertz" before "CTS", "Erik Nording" before "Nording")."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    brands = [str(b) for b in (data.get("brands") or [])]
    return sorted(brands, key=len, reverse=True)


def extract_brand(name: str, brands: list[str]) -> Optional[str]:
    """Return the allowlisted brand named in the title, or None.

    Matching is on normalised word boundaries: "Bari" matches
    "Bari Winking 1999" but never "Barista". Nothing outside the
    allowlist is ever returned — that is the whole point of the file.
    """
    haystack = f" {_squash(_norm(name))} "
    for brand in brands:
        needle = f" {_squash(_norm(brand))} "
        if needle in haystack:
            return brand
    return None


# ── field derivation ─────────────────────────────────────────────────

def extract_shape(name: str) -> Optional[str]:
    """The most specific shape/form word in the title, if any."""
    haystack = f" {_squash(_norm(name))} "
    # Longest match wins (a "churchwarden" is more specific than a
    # "pipe"); ties break on _SHAPE_KEYWORDS order, which is declared
    # most-specific-first, so the result is always deterministic.
    best: Optional[str] = None
    for shape in _SHAPE_KEYWORDS:
        if f" {_norm(shape)} " in haystack:
            if best is None or len(shape) > len(best):
                best = shape
    return best


def extract_origin(name: str) -> Optional[str]:
    haystack = f" {_squash(_norm(name))} "
    for word, code in _ORIGIN_KEYWORDS.items():
        if f" {_norm(word)} " in haystack:
            return code
    return None


def extract_era(name: str) -> Optional[dict]:
    """Era from a date the title actually states. Always basis STYLE.

    The adapter is reading Farid's period wording, not a stamping it
    verified, so it must not license "circa 1955" copy. STYLE yields
    honest, loose language ("mid-century", "late 20th century"). When a
    piece really is stamp-dated, that belongs in the genome via the
    corrections ledger — not in a title parser.
    """
    low = _norm(name)
    # Ranges must be read BEFORE normalisation: _norm turns every
    # punctuation mark into a space, so "c. 1900-1930" would arrive as
    # "c 1900 1930" and the hyphen the range regex needs would be gone.
    raw = name.lower()

    span = _RANGE_RE.search(raw)
    if span:
        lo, hi = int(span.group(1)), int(span.group(2))
        if lo <= hi:
            return {"min_year": lo, "max_year": hi, "basis": EraBasis.STYLE.value}

    decade_span = _DECADE_RANGE_RE.search(raw)
    if decade_span:
        lo, hi = int(decade_span.group(1)), int(decade_span.group(2))
        if lo <= hi:
            return {"min_year": lo, "max_year": hi + 9, "basis": EraBasis.STYLE.value}

    decade = _DECADE_RE.search(low)
    if decade:
        start = int(decade.group(1))
        return {"min_year": start, "max_year": start + 9, "basis": EraBasis.STYLE.value}

    for phrase, lo, hi in _ERA_PHRASES:
        if phrase in low:
            return {"min_year": lo, "max_year": hi, "basis": EraBasis.STYLE.value}

    year = _YEAR_RE.search(low)
    if year:
        val = int(year.group(1))
        return {"min_year": val, "max_year": val, "basis": EraBasis.STYLE.value}

    return None


def build_taxonomy(department: str, shape: Optional[str]) -> str:
    """department/shape, but never "meerschaum/meerschaum": a leaf that
    only repeats its own department adds no information and reads as a
    bug in every caption that renders it."""
    dept = (department or "").strip() or "uncategorised"
    if not shape:
        return dept
    leaf = shape.replace(" ", "-")
    if leaf in _norm(dept).replace(" ", "-"):
        return dept
    return f"{dept}/{leaf}"


# ── the record ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class CatalogItem:
    """A product file plus the effective-genome view of it."""

    sku: str
    name: str
    department: str
    price: Optional[float]
    source_path: str
    effective: dict

    @property
    def image_count(self) -> int:
        return len(self.effective.get("media") or [])


def _to_float(value) -> Optional[float]:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def to_effective(product: dict, brands: list[str]) -> dict:
    """Product YAML -> effective genome dict (birth + corrections view).

    Only `sku` is strictly required downstream; everything else is
    best-effort and silently absent when the title does not state it.
    """
    name = str(product.get("name") or "").strip()
    department = str(product.get("department") or "").strip()
    price = _to_float(product.get("price"))

    brand = extract_brand(name, brands)
    shape = extract_shape(name)
    origin = extract_origin(name)
    era = extract_era(name)

    media = [
        {"url": url, "role": MediaRole.HERO.value if i == 0 else MediaRole.ANGLE.value, "seq": i}
        for i, url in enumerate(product.get("images") or [])
    ]

    unique: dict = {}
    if era:
        unique["era"] = era
    if any(token in _norm(name) for token in _NOS_TOKENS):
        # A stated "new old stock / unsmoked" is a condition claim Farid
        # made himself; it is not a flaw and not an appraisal grade, so
        # it rides as provenance context rather than a condition_grade.
        unique["nos"] = True

    effective: dict = {
        "sku": str(product.get("sku") or "").strip(),
        "product_type": "unique_physical",
        "taxonomy": build_taxonomy(department, shape),
        "catalog_name": name,
        "list_price": price,
        "currency": "GBP",
        "media": media,
        "in_stock": bool(product.get("inStock", True)),
        # Provenance: every one of these facts was typed by a human.
        # This is what lets `assertable()` ASSERT rather than hedge.
        "field_provenance": {
            "brand": {"source": FieldSource.HUMAN.value},
            "unique_physical.era": {"source": FieldSource.HUMAN.value},
        },
        "generator_source": CATALOG_ADAPTER_VERSION,
    }

    if brand:
        effective["brand"] = brand
    if origin:
        effective["country_of_origin"] = origin
    if unique:
        effective["unique_physical"] = unique
    if unique.get("nos"):
        effective["provenance_context"] = ["unsold shop stock, never used"]

    return effective


def load_item(path: str | Path, brands: list[str]) -> Optional[CatalogItem]:
    """Load one product file. Returns None for a file with no SKU —
    it cannot be tracked, posted about, or joined to the ledger."""
    path = Path(path)
    with open(path, encoding="utf-8") as fh:
        product = yaml.safe_load(fh) or {}
    if not isinstance(product, dict):
        return None

    effective = to_effective(product, brands)
    if not effective["sku"]:
        return None

    return CatalogItem(
        sku=effective["sku"],
        name=effective["catalog_name"],
        department=str(product.get("department") or "").strip(),
        price=effective["list_price"],
        source_path=str(path),
        effective=effective,
    )


def iter_catalog(products_dir: str | Path, brands_path: str | Path) -> Iterator[CatalogItem]:
    brands = load_brands(brands_path)
    for path in sorted(Path(products_dir).glob("*.yaml")):
        item = load_item(path, brands)
        if item is not None:
            yield item


def load_catalog(products_dir: str | Path, brands_path: str | Path) -> list[CatalogItem]:
    """The whole catalog, de-duplicated by SKU (first file wins).

    Duplicate SKUs exist in the imported inventory; posting the same
    SKU twice from two files would double-spend the daily slots and
    corrupt rotation, so they are collapsed here, once, at the source.
    """
    seen: set[str] = set()
    items: list[CatalogItem] = []
    for item in iter_catalog(products_dir, brands_path):
        if item.sku in seen:
            continue
        seen.add(item.sku)
        items.append(item)
    return items
