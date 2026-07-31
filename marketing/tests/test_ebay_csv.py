"""eBay CSV export tests — the honesty rules matter more than the format."""

import csv

import pytest

from marketing.channels import (
    EBAY_TITLE_LIMIT,
    CatalogItem,
    EbayExportError,
    build_rows,
    load_catalog,
    write_csv,
)
from marketing.channels.ebay_csv import COLUMNS

CAT = "3204"
LOC = "NJ, USA"


def item(**kw) -> CatalogItem:
    base = dict(
        sku="FH-TP-001",
        name="Chacom Gentleman 836 Sandblasted Dublin",
        price=125.0,
        images=["https://img/1.jpg", "https://img/2.jpg"],
        description="A fine estate pipe.",
        in_stock=True,
    )
    base.update(kw)
    return CatalogItem(**base)


# ------------------------------------------------- never offer a sold piece

def test_sold_items_are_never_exported():
    rows, skipped = build_rows([item(in_stock=False)])
    assert rows == []
    assert "sold" in skipped[0]


def test_skips_are_reported_never_silent():
    rows, skipped = build_rows([
        item(sku="A", in_stock=False),
        item(sku="B", price=0.0),
        item(sku="C", images=[]),
        item(sku="D"),
    ])
    assert [r.custom_label for r in rows] == ["D"]
    assert len(skipped) == 3
    assert all(s.split(":")[0] in {"A", "B", "C"} for s in skipped)


# ------------------------------------------------------------ eBay limits

def test_title_truncated_to_ebay_limit():
    rows, _ = build_rows([item(name="X" * 200)])
    assert len(rows[0].title) == EBAY_TITLE_LIMIT


def test_title_under_limit_is_untouched():
    rows, _ = build_rows([item(name="Short Title")])
    assert rows[0].title == "Short Title"


def test_pictures_capped_at_24():
    rows, _ = build_rows([item(images=[f"https://img/{i}.jpg" for i in range(40)])])
    assert len(rows[0].pic_url.split("|")) == 24


def test_output_is_ascii_safe_law_09():
    rows, _ = build_rows([item(name="Chacom Gentleman - circa 1955–1962 — estate")])
    rows[0].title.encode("ascii")
    rows[0].description.encode("ascii")


# ------------------------------------------------- nothing is fabricated

def test_category_is_required_not_guessed():
    rows, _ = build_rows([item()])
    with pytest.raises(EbayExportError, match="Category"):
        write_csv(rows, "/tmp/x.csv", category="", location=LOC)


def test_location_is_required():
    rows, _ = build_rows([item()])
    with pytest.raises(EbayExportError, match="Location"):
        write_csv(rows, "/tmp/x.csv", category=CAT, location="")


# ------------------------------------------------------------- csv shape

def test_csv_has_file_exchange_header_and_row(tmp_path):
    rows, _ = build_rows([item()])
    out = write_csv(rows, tmp_path / "ebay.csv", category=CAT, location=LOC)

    with open(out, encoding="utf-8") as fh:
        parsed = list(csv.reader(fh))

    # File Exchange uses ONE header row; the upload directives ride in
    # the Action column's header cell.
    assert len(parsed) == 2
    header, listing = parsed[0], parsed[1]
    assert "SiteID=US" in header[0] and "Currency=USD" in header[0]
    assert header[1:] == COLUMNS[1:]

    row = dict(zip(COLUMNS, listing))
    assert row["Action"] == "Add"
    assert row["CustomLabel"] == "FH-TP-001"
    assert row["Category"] == CAT
    assert row["Quantity"] == "1"          # one-of-a-kind
    assert row["Format"] == "FixedPrice"
    assert row["Duration"] == "GTC"
    assert row["StartPrice"] == "125.00"
    assert row["Location"] == LOC


def test_currency_flows_into_directives(tmp_path):
    rows, _ = build_rows([item()])
    out = write_csv(rows, tmp_path / "e.csv", category=CAT, location=LOC, currency="GBP")
    assert "Currency=GBP" in out.read_text(encoding="utf-8")


# ------------------------------------------------------------- catalogue

def test_load_catalog_reads_real_yaml(tmp_path):
    (tmp_path / "a.yaml").write_text(
        "name: Test Pipe\nsku: FH-TP-999\nprice: '55.00'\n"
        "inStock: false\nimages:\n- https://img/a.jpg\n",
        encoding="utf-8",
    )
    (tmp_path / "no-sku.yaml").write_text("name: Ignored\n", encoding="utf-8")

    items = load_catalog(tmp_path)
    assert len(items) == 1
    assert items[0].sku == "FH-TP-999"
    assert items[0].price == 55.0
    assert items[0].in_stock is False


def test_real_catalogue_excludes_the_pipes_sold_today():
    """The four sold this session must not appear in an eBay export."""
    items = load_catalog("content/products")
    rows, _ = build_rows(items)
    exported = {r.custom_label for r in rows}
    for sold in ("FH-TP-011", "FH-TP-013", "FH-TP-058", "FH-LM-010"):
        assert sold not in exported
