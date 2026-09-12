"""The flywheel — sold item becomes a permanent asset.

    sold in the admin -> SOLD event -> archive page -> archive post

P2.5 built the phenotype ledger and P2.8 built the encyclopedia
flywheel, both tested. Nothing ever called either of them: the ledger
recorded no events and no sold item ever produced an archive page. The
designed loop existed as code and never turned once.

HOW A SALE IS DETECTED. Farid already marks an item sold in the admin by
unticking In Stock. That is the signal — no new habit, no extra step.
This module remembers each item's stock state between runs and treats a
true -> false transition as the sale.

Two guards worth stating:

  * The FIRST time a SKU is seen, its state is only recorded, never
    treated as a transition. Otherwise the first run would declare every
    already-sold item freshly sold and publish a burst of archive posts.
  * The sold PRICE is not published by default. The catalog holds the
    asking price, and an item that went for an accepted offer did not
    sell at it. A sold-price database is only an asset while the numbers
    in it are true.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from .encyclopedia.flywheel import on_sold
from .phenotype.ledger import Event, PhenotypeLedger

_SQL = """
CREATE TABLE IF NOT EXISTS stock_state (
    sku        TEXT PRIMARY KEY,
    in_stock   INTEGER NOT NULL,
    updated_ts TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class SoldItem:
    sku: str
    name: str
    archive_path: str
    caption: str


class StockWatcher:
    """Remembers stock state between runs so a sale can be noticed."""

    def __init__(self, db_path: str | Path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path))
        self._conn.executescript(_SQL)
        self._conn.commit()

    def known(self) -> dict[str, bool]:
        return {sku: bool(flag) for sku, flag
                in self._conn.execute("SELECT sku, in_stock FROM stock_state")}

    def remember(self, states: dict[str, bool]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.executemany(
            "INSERT INTO stock_state (sku, in_stock, updated_ts) VALUES (?,?,?) "
            "ON CONFLICT(sku) DO UPDATE SET in_stock=excluded.in_stock, "
            "updated_ts=excluded.updated_ts",
            [(sku, int(flag), now) for sku, flag in states.items()],
        )
        self._conn.commit()

    def newly_sold(self, items) -> list:
        """Items that were in stock last run and are not now.

        A SKU seen for the first time is never "newly sold" — it has no
        previous state to have changed from.
        """
        previous = self.known()
        return [
            item for item in items
            if previous.get(item.sku) is True
            and not item.effective.get("in_stock", True)
        ]

    def close(self) -> None:
        self._conn.close()


def turn(
    items: Iterable,
    out_root: str | Path,
    archive_dir: str | Path,
    channel: str = "store",
    show_price: bool = False,
    now: Optional[datetime] = None,
) -> tuple[list[SoldItem], list[str]]:
    """Run one turn of the flywheel. Returns (sold items, warnings).

    Every item is stamped into the stock table afterwards, including the
    ones that did not change, so the next run has a baseline.
    """
    items = list(items)
    out_root = Path(out_root)
    now = now or datetime.now(timezone.utc)

    watcher = StockWatcher(out_root / "stock.db")
    ledger = PhenotypeLedger(out_root / "phenotype.db")
    sold: list[SoldItem] = []
    warnings: list[str] = []

    try:
        for item in watcher.newly_sold(items):
            effective = item.effective
            payload = {"channel": channel, "ts": now.isoformat()}
            if show_price and item.price is not None:
                payload["sold_price"] = item.price

            try:
                ledger.record(
                    sku=item.sku, event=Event.SOLD, channel=channel,
                    payload=payload, taxonomy=effective.get("taxonomy"),
                    brand=effective.get("brand"), list_price=item.price, ts=now,
                )
                path, caption = on_sold(effective, payload, archive_dir,
                                        show_price=show_price)
            except Exception as exc:        # one bad item must not stop the rest
                warnings.append(f"{item.sku}: flywheel failed ({type(exc).__name__}: {exc})")
                continue

            sold.append(SoldItem(sku=item.sku, name=item.name,
                                 archive_path=str(path), caption=caption.full()))

        watcher.remember({
            item.sku: bool(item.effective.get("in_stock", True)) for item in items
        })
    finally:
        watcher.close()
        ledger.close()

    return sold, warnings


def record_listed(
    items: Iterable,
    out_root: str | Path,
    channel: str = "social",
    now: Optional[datetime] = None,
) -> None:
    """Stamp a LISTED event for each item posted today.

    Without this the ledger stays empty, `days_to_sale` can never be
    computed, and the inference layer's wake-up trigger can never fire —
    the measurement the whole design defers to.
    """
    out_root = Path(out_root)
    # sqlite will not create a missing parent directory: on a first run
    # this raised OperationalError and took the whole run down after the
    # posts had already gone out.
    out_root.mkdir(parents=True, exist_ok=True)
    ledger = PhenotypeLedger(out_root / "phenotype.db")
    try:
        for item in items:
            ledger.record(
                sku=item["sku"], event=Event.LISTED, channel=channel,
                payload={"targets": item.get("placements", [])},
                taxonomy=item.get("taxonomy"), brand=item.get("brand"),
                list_price=item.get("price"), ts=now,
            )
    finally:
        ledger.close()
