"""Flywheel tests: sold in the admin -> archive page -> archive post.

P2.5 (ledger) and P2.8 (encyclopedia) were both built and tested, and
neither was ever called - the ledger recorded nothing and no sold item
ever produced a page. These tests cover the wiring that makes the loop
actually turn, and the two guards that stop it turning wrongly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from marketing.flywheel import StockWatcher, record_listed, turn
from marketing.phenotype.ledger import Event, PhenotypeLedger


class Item:
    def __init__(self, sku: str, name: str, in_stock: bool, price: float = 100.0):
        self.sku, self.name, self.price = sku, name, price
        self.effective = {
            "sku": sku, "catalog_name": name, "product_type": "unique_physical",
            "taxonomy": "estate-pipes/billiard", "brand": "Chacom",
            "in_stock": in_stock, "list_price": price, "media": [],
            "field_provenance": {"brand": {"source": "human"}},
        }


def _turn(items, tmp_path, **kw):
    return turn(items, tmp_path / "out", tmp_path / "archive", **kw)


# ── the guard against a first-run burst ──────────────────────────────

def test_first_sighting_is_never_a_sale(tmp_path):
    """Otherwise the very first run declares every already-sold item
    freshly sold and publishes a burst of archive posts."""
    sold, warnings = _turn([Item("A", "Already Sold Pipe", in_stock=False)], tmp_path)
    assert sold == [] and warnings == []


def test_a_transition_is_a_sale(tmp_path):
    _turn([Item("A", "Chacom Gentleman 836", in_stock=True)], tmp_path)
    sold, _ = _turn([Item("A", "Chacom Gentleman 836", in_stock=False)], tmp_path)
    assert [s.sku for s in sold] == ["A"]


def test_a_sale_is_announced_only_once(tmp_path):
    _turn([Item("A", "Pipe", in_stock=True)], tmp_path)
    _turn([Item("A", "Pipe", in_stock=False)], tmp_path)
    again, _ = _turn([Item("A", "Pipe", in_stock=False)], tmp_path)
    assert again == []


def test_restocking_then_selling_announces_again(tmp_path):
    for in_stock in (True, False, True):
        _turn([Item("A", "Pipe", in_stock=in_stock)], tmp_path)
    sold, _ = _turn([Item("A", "Pipe", in_stock=False)], tmp_path)
    assert len(sold) == 1


# ── what a sale produces ─────────────────────────────────────────────

def test_sale_writes_a_permanent_archive_page(tmp_path):
    _turn([Item("A", "Chacom Gentleman 836", in_stock=True)], tmp_path)
    sold, _ = _turn([Item("A", "Chacom Gentleman 836", in_stock=False)], tmp_path)
    page = Path(sold[0].archive_path)
    assert page.exists() and page.suffix == ".md"
    assert "Chacom" in page.read_text()


def test_sale_produces_an_archive_caption(tmp_path):
    _turn([Item("A", "Chacom Gentleman 836", in_stock=True)], tmp_path)
    sold, _ = _turn([Item("A", "Chacom Gentleman 836", in_stock=False)], tmp_path)
    assert "From the archive" in sold[0].caption
    assert "#" in sold[0].caption


def test_sale_lands_in_the_ledger(tmp_path):
    _turn([Item("A", "Pipe", in_stock=True)], tmp_path)
    _turn([Item("A", "Pipe", in_stock=False)], tmp_path)
    ledger = PhenotypeLedger(tmp_path / "out" / "phenotype.db")
    try:
        events = ledger.events_for("A")
    finally:
        ledger.close()
    assert [e["event"] for e in events] == [Event.SOLD.value]


# ── price honesty ────────────────────────────────────────────────────

def test_asking_price_is_not_published_as_the_sold_price(tmp_path):
    """An item that went for an accepted offer did not sell at its
    asking price. A sold-price database is an asset only while true."""
    _turn([Item("A", "Pipe", in_stock=True, price=528.0)], tmp_path)
    sold, _ = _turn([Item("A", "Pipe", in_stock=False, price=528.0)], tmp_path)
    assert "528" not in Path(sold[0].archive_path).read_text()


def test_price_is_published_when_explicitly_enabled(tmp_path):
    _turn([Item("A", "Pipe", in_stock=True, price=528.0)], tmp_path)
    sold, _ = _turn([Item("A", "Pipe", in_stock=False, price=528.0)], tmp_path,
                    show_price=True)
    assert "528" in Path(sold[0].archive_path).read_text()


# ── resilience ───────────────────────────────────────────────────────

def test_one_broken_item_does_not_stop_the_others(tmp_path):
    good, bad = Item("G", "Good Pipe", in_stock=True), Item("B", "Bad Pipe", in_stock=True)
    _turn([good, bad], tmp_path)
    bad.effective.pop("sku")             # breaks page generation
    good.effective["in_stock"] = bad.effective["in_stock"] = False
    sold, warnings = _turn([good, bad], tmp_path)
    assert [s.sku for s in sold] == ["G"]
    assert any("B:" in w for w in warnings)


def test_unchanged_items_are_still_remembered(tmp_path):
    """Every item is stamped each run, so the next run has a baseline
    even for items that did not move."""
    _turn([Item("A", "Pipe", in_stock=True), Item("B", "Other", in_stock=True)], tmp_path)
    watcher = StockWatcher(tmp_path / "out" / "stock.db")
    try:
        assert watcher.known() == {"A": True, "B": True}
    finally:
        watcher.close()


# ── listed events ────────────────────────────────────────────────────

def test_posting_records_a_listed_event(tmp_path):
    """Without LISTED, days-to-sale can never be computed and the
    deferred inference layer can never be woken."""
    record_listed(
        [{"sku": "A", "taxonomy": "estate-pipes", "brand": "Chacom",
          "price": 180.0, "placements": ["page: url"]}],
        tmp_path / "out",
    )
    ledger = PhenotypeLedger(tmp_path / "out" / "phenotype.db")
    try:
        events = ledger.events_for("A")
    finally:
        ledger.close()
    assert events[0]["event"] == Event.LISTED.value


def test_listed_then_sold_gives_days_to_sale(tmp_path):
    from datetime import datetime, timedelta, timezone

    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    record_listed([{"sku": "A", "price": 100.0}], tmp_path / "out", now=start)
    _turn([Item("A", "Pipe", in_stock=True)], tmp_path)
    _turn([Item("A", "Pipe", in_stock=False)], tmp_path, now=start + timedelta(days=12))

    ledger = PhenotypeLedger(tmp_path / "out" / "phenotype.db")
    try:
        assert ledger.days_to_sale("A") == pytest.approx(12.0, abs=0.1)
    finally:
        ledger.close()
