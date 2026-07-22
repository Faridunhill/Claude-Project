"""Five-event phenotype ledger (P2.5 — Synthesis V3, ratified).

Record the ledger, defer the brain. Five unrecoverable events, nothing
else — views/watchers/favorites are explicitly excluded (re-collectable
noise; they arrive only when a named generator decision is blocked).

Append-only. Cohort keys fixed now: taxonomy_node x price_band, brand.
The inference layer stays asleep until any cohort reaches
TRIGGER_SOLD_EVENTS sold events inside TRIGGER_WINDOW_DAYS — this module
only measures the trigger; it never acts on it.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

#: The wake-up trigger for the deferred inference layer (Code F1).
TRIGGER_SOLD_EVENTS = 50
TRIGGER_WINDOW_DAYS = 365

#: Fixed price bands (GBP) for the cohort key. Add bands only at the
#: top; never re-cut existing boundaries (it orphans cohort history).
PRICE_BANDS: tuple[tuple[float, float, str], ...] = (
    (0, 25, "0-25"),
    (25, 50, "25-50"),
    (50, 100, "50-100"),
    (100, 150, "100-150"),
    (150, 300, "150-300"),
    (300, float("inf"), "300+"),
)


def price_band(price: Optional[float]) -> str:
    if price is None:
        return "unknown"
    for lo, hi, label in PRICE_BANDS:
        if lo <= price < hi:
            return label
    return "unknown"


class Event(str, Enum):
    LISTED = "listed"
    PRICE_CHANGED = "price_changed"
    OFFER_RECEIVED = "offer_received"
    SOLD = "sold"
    RETURNED = "returned"


_SQL = """
CREATE TABLE IF NOT EXISTS phenotype_events (
    event_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    sku        TEXT NOT NULL,
    ts         TEXT NOT NULL,
    channel    TEXT NOT NULL,
    event      TEXT NOT NULL,
    payload    TEXT NOT NULL DEFAULT '{}',
    taxonomy   TEXT,
    brand      TEXT,
    band       TEXT
);
CREATE INDEX IF NOT EXISTS idx_pheno_sku ON phenotype_events (sku, ts);
CREATE INDEX IF NOT EXISTS idx_pheno_cohort ON phenotype_events (event, taxonomy, band);
"""


@dataclass(frozen=True)
class CohortStat:
    taxonomy: str
    band: str
    sold_count: int
    median_days_to_sale: Optional[float]
    median_sold_price: Optional[float]
    trigger_met: bool


class PhenotypeLedger:
    """Append-only. There is deliberately no update or delete method."""

    def __init__(self, db_path: str | Path):
        self._conn = sqlite3.connect(str(db_path))
        self._conn.executescript(_SQL)
        self._conn.commit()

    def record(
        self,
        sku: str,
        event: Event,
        channel: str,
        payload: Optional[dict] = None,
        taxonomy: Optional[str] = None,
        brand: Optional[str] = None,
        list_price: Optional[float] = None,
        ts: Optional[datetime] = None,
    ) -> None:
        self._conn.execute(
            "INSERT INTO phenotype_events (sku, ts, channel, event, payload, taxonomy, brand, band) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                sku,
                (ts or datetime.now(timezone.utc)).isoformat(),
                channel,
                event.value,
                json.dumps(payload or {}),
                taxonomy,
                brand,
                price_band(list_price),
            ),
        )
        self._conn.commit()

    # -- derived metrics (computed, never stored) ----------------------

    def days_to_sale(self, sku: str) -> Optional[float]:
        rows = dict(
            self._conn.execute(
                "SELECT event, MIN(ts) FROM phenotype_events "
                "WHERE sku=? AND event IN ('listed','sold') GROUP BY event",
                (sku,),
            ).fetchall()
        )
        if "listed" not in rows or "sold" not in rows:
            return None
        listed = datetime.fromisoformat(rows["listed"])
        sold = datetime.fromisoformat(rows["sold"])
        return round((sold - listed).total_seconds() / 86400, 2)

    def cohort_stats(self, now: Optional[datetime] = None) -> list[CohortStat]:
        """Sold-event stats per (taxonomy x band) cohort over the rolling
        trigger window, plus whether the inference-layer trigger is met."""
        now = now or datetime.now(timezone.utc)
        cutoff = (now - timedelta(days=TRIGGER_WINDOW_DAYS)).isoformat()
        rows = self._conn.execute(
            "SELECT taxonomy, band, sku, ts, payload FROM phenotype_events "
            "WHERE event='sold' AND ts >= ? AND taxonomy IS NOT NULL",
            (cutoff,),
        ).fetchall()

        by_cohort: dict[tuple[str, str], list[tuple[str, str, dict]]] = {}
        for taxonomy, band, sku, ts, payload in rows:
            by_cohort.setdefault((taxonomy, band), []).append((sku, ts, json.loads(payload)))

        def median(values: list[float]) -> Optional[float]:
            if not values:
                return None
            values = sorted(values)
            n = len(values)
            mid = n // 2
            return values[mid] if n % 2 else (values[mid - 1] + values[mid]) / 2

        stats = []
        for (taxonomy, band), sales in sorted(by_cohort.items()):
            dts = [d for d in (self.days_to_sale(sku) for sku, _, _ in sales) if d is not None]
            prices = [p["sold_price"] for _, _, p in sales if "sold_price" in p]
            stats.append(
                CohortStat(
                    taxonomy=taxonomy,
                    band=band,
                    sold_count=len(sales),
                    median_days_to_sale=median(dts),
                    median_sold_price=median(prices),
                    trigger_met=len(sales) >= TRIGGER_SOLD_EVENTS,
                )
            )
        return stats

    def inference_trigger_met(self) -> bool:
        """True the day any cohort earns the deferred inference layer."""
        return any(s.trigger_met for s in self.cohort_stats())

    def events_for(self, sku: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT ts, channel, event, payload FROM phenotype_events WHERE sku=? ORDER BY ts",
            (sku,),
        ).fetchall()
        return [
            {"ts": r[0], "channel": r[1], "event": r[2], "payload": json.loads(r[3])}
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()
