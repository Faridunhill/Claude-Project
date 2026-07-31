"""eBay File Exchange CSV export.

SYSTEM_MAP lists eBay as a goal channel — "Faridunhill store + Etsy +
eBay(upload)" — reached by uploading a CSV rather than by API. This
module builds that CSV.

Rules carried from the rest of the system:

  * **Never offer a sold piece.** Items with `inStock: false` are
    excluded, and the count of skipped items is reported. These are
    one-of-a-kind estate pieces: sold means permanently off-market.
  * **LAW 09** — all output is ASCII-safe.
  * **Titles are truncated to eBay's 80-character limit**, matching
    `expression/copy.py`'s `generate_title(max_len=80)`.
  * **Nothing is fabricated.** eBay requires a numeric Category ID and
    an item Location; neither can be derived from the catalogue, so both
    are required inputs. Guessing a category ID produces a CSV that eBay
    silently rejects at upload, which is worse than refusing to build it.

Data source: this reads Claude-Project's `content/products/*.yaml`.
NOTE (SYSTEM_MAP): the LIVE store is faridunhill-live (Supabase), not
this catalogue. When the live catalogue should drive the export, add a
loader here that returns `CatalogItem`s from Supabase — `build_rows`
and `write_csv` do not change.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

import yaml

from ..expression.copy import ascii_safe

#: eBay's hard cap on listing titles.
EBAY_TITLE_LIMIT = 80

#: eBay ConditionID for a used item. Estate pipes are used by definition;
#: NOS stock is still "used" to eBay unless sold with original packaging.
CONDITION_USED = 3000

#: eBay accepts at most 24 pictures per listing.
MAX_PICTURES = 24

#: File Exchange header. The Action column carries the upload directives.
def _action_header(currency: str) -> str:
    return (
        f"Action(SiteID=US|Country=US|Currency={currency}|Version=1193|CC=UTF-8)"
    )


COLUMNS = [
    "Action",
    "CustomLabel",
    "Category",
    "Title",
    "Description",
    "ConditionID",
    "PicURL",
    "Quantity",
    "Format",
    "StartPrice",
    "Duration",
    "Location",
]


class EbayExportError(Exception):
    """Raised when the export cannot be built honestly."""


@dataclass(frozen=True)
class CatalogItem:
    sku: str
    name: str
    price: float
    images: Sequence[str]
    description: str = ""
    in_stock: bool = True


@dataclass(frozen=True)
class EbayRow:
    custom_label: str
    title: str
    description: str
    pic_url: str
    start_price: str

    def as_dict(self, category: str, location: str, currency: str) -> dict:
        return {
            "Action": "Add",
            "CustomLabel": self.custom_label,
            "Category": category,
            "Title": self.title,
            "Description": self.description,
            "ConditionID": str(CONDITION_USED),
            "PicURL": self.pic_url,
            "Quantity": "1",          # one-of-a-kind estate pieces
            "Format": "FixedPrice",
            "StartPrice": self.start_price,
            "Duration": "GTC",        # good 'til cancelled
            "Location": location,
        }


def load_catalog(products_dir: str | Path) -> list[CatalogItem]:
    """Read `content/products/*.yaml` into CatalogItems."""
    items: list[CatalogItem] = []
    for path in sorted(Path(products_dir).glob("*.yaml")):
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not data.get("sku"):
            continue
        try:
            price = float(str(data.get("price", "0")))
        except ValueError:
            price = 0.0
        items.append(
            CatalogItem(
                sku=str(data["sku"]),
                name=str(data.get("name", "")),
                price=price,
                images=list(data.get("images") or []),
                description=str(data.get("description", "")),
                in_stock=bool(data.get("inStock", True)),
            )
        )
    return items


def build_rows(items: Iterable[CatalogItem]) -> tuple[list[EbayRow], list[str]]:
    """Build eBay rows. Returns (rows, skipped_reasons).

    Skips rather than fabricates: a sold item, a priceless item or an
    item with no photo cannot be listed, and each skip is reported so
    nothing disappears silently.
    """
    rows: list[EbayRow] = []
    skipped: list[str] = []

    for item in items:
        if not item.in_stock:
            skipped.append(f"{item.sku}: sold — never offer a sold piece")
            continue
        if item.price <= 0:
            skipped.append(f"{item.sku}: no price")
            continue
        if not item.images:
            skipped.append(f"{item.sku}: no photo (eBay requires one)")
            continue

        title = ascii_safe(item.name).strip()
        if len(title) > EBAY_TITLE_LIMIT:
            title = title[:EBAY_TITLE_LIMIT].rstrip()

        rows.append(
            EbayRow(
                custom_label=item.sku,
                title=title,
                description=ascii_safe(item.description).strip(),
                pic_url="|".join(item.images[:MAX_PICTURES]),
                start_price=f"{item.price:.2f}",
            )
        )
    return rows, skipped


def write_csv(
    rows: Sequence[EbayRow],
    out_path: str | Path,
    category: str,
    location: str,
    currency: str = "USD",
) -> Path:
    """Write the File Exchange CSV.

    `category` (eBay numeric category ID) and `location` are required —
    see the module docstring for why they are not guessed.
    """
    if not str(category).strip():
        raise EbayExportError(
            "eBay Category ID is required. It cannot be derived from the "
            "catalogue, and a guessed ID uploads as a silent rejection. "
            "Find it in eBay's category lookup and pass it explicitly."
        )
    if not str(location).strip():
        raise EbayExportError("Item Location is required by eBay (e.g. 'NJ, USA').")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        # File Exchange wants the directives inside the Action header.
        writer.writerow({c: (_action_header(currency) if c == "Action" else c)
                         for c in COLUMNS})
        for row in rows:
            writer.writerow(row.as_dict(category, location, currency))
    return out_path


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Export the catalogue as an eBay File Exchange CSV.")
    ap.add_argument("--products", default="content/products", help="catalogue directory")
    ap.add_argument("--out", default="ebay-listings.csv", help="output CSV path")
    ap.add_argument("--category", required=True, help="eBay numeric Category ID")
    ap.add_argument("--location", required=True, help="item location, e.g. 'NJ, USA'")
    ap.add_argument("--currency", default="USD")
    args = ap.parse_args(argv)

    items = load_catalog(args.products)
    rows, skipped = build_rows(items)
    path = write_csv(rows, args.out, args.category, args.location, args.currency)

    print(f"wrote {len(rows)} listings -> {path}")
    if skipped:
        print(f"skipped {len(skipped)}:")
        for reason in skipped:
            print(f"  - {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
