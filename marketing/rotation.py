"""Rotation — which items get posted today, and why.

The engine could always generate content; nothing decided WHAT to
generate. That decision has to be boring, explainable and repeatable,
because Farid has to be able to look at any day's output and see why
those items and not others.

The policy, in order:

  1. Eligible only — in stock, has a SKU, has at least one photo.
  2. Cooldown — an item selected within `cooldown_days` is skipped, so
     the feed never repeats itself while followers are still seeing it.
  3. Never-posted first — the 264-item backlog drains before anything
     comes round again.
  4. Then longest-since-posted, then highest price — the money at stake
     breaks ties.

Deterministic: the same date and the same history always select the
same items, which is what makes the runner testable and a re-run safe.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

DEFAULT_COOLDOWN_DAYS = 45

_SQL = """
CREATE TABLE IF NOT EXISTS selections (
    selection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku          TEXT NOT NULL,
    run_date     TEXT NOT NULL,
    ts           TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sel_sku ON selections (sku, run_date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sel_unique ON selections (sku, run_date);
"""


@dataclass(frozen=True)
class Candidate:
    sku: str
    price: float
    has_photo: bool
    in_stock: bool


class Rotation:
    def __init__(self, db_path: str | Path, cooldown_days: int = DEFAULT_COOLDOWN_DAYS):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path))
        self._conn.executescript(_SQL)
        self._conn.commit()
        self._cooldown = cooldown_days

    def last_selected(self, sku: str) -> Optional[str]:
        row = self._conn.execute(
            "SELECT MAX(run_date) FROM selections WHERE sku=?", (sku,)
        ).fetchone()
        return row[0] if row and row[0] else None

    def _history(self) -> dict[str, str]:
        return {
            sku: last
            for sku, last in self._conn.execute(
                "SELECT sku, MAX(run_date) FROM selections GROUP BY sku"
            )
        }

    def selected_on(self, run_date: date) -> list[str]:
        """SKUs already chosen for this date, in the order chosen."""
        return [
            sku for (sku,) in self._conn.execute(
                "SELECT sku FROM selections WHERE run_date=? ORDER BY selection_id",
                (run_date.isoformat(),),
            )
        ]

    def select(self, candidates: Iterable[Candidate], run_date: date, count: int) -> list[str]:
        """Return up to `count` SKUs for `run_date`. Pure: records
        nothing. Call `record` once the run actually produces output,
        so a crashed run does not burn the cooldown.

        A DAY IS IDEMPOTENT. If this date already has selections, they
        are returned again (topped up only if `count` grew). Re-running
        a day — because the job fired twice, or because Farid wanted the
        videos regenerated — must reproduce that day, not chew through
        the backlog a second time.
        """
        history = self._history()
        cutoff = (run_date - timedelta(days=self._cooldown)).isoformat()
        today = run_date.isoformat()

        already = self.selected_on(run_date)
        if len(already) >= count:
            return already[:count]

        chosen = set(already)
        eligible = []
        for cand in candidates:
            if not (cand.in_stock and cand.has_photo and cand.sku):
                continue
            if cand.sku in chosen:
                continue
            last = history.get(cand.sku)
            if last is not None and last > cutoff and last != today:
                continue          # still inside its cooldown window
            eligible.append((cand, last))

        def sort_key(pair: tuple[Candidate, Optional[str]]):
            cand, last = pair
            never_posted = 0 if last is None else 1     # never-posted first
            return (never_posted, last or "", -cand.price, cand.sku)

        eligible.sort(key=sort_key)
        return already + [cand.sku for cand, _ in eligible[: count - len(already)]]

    def record(self, skus: Iterable[str], run_date: date) -> None:
        """Mark these SKUs as used today. Idempotent — re-running the
        same date does not create duplicate history."""
        now = datetime.now(timezone.utc).isoformat()
        self._conn.executemany(
            "INSERT OR IGNORE INTO selections (sku, run_date, ts) VALUES (?,?,?)",
            [(sku, run_date.isoformat(), now) for sku in skus],
        )
        self._conn.commit()

    def posted_count(self) -> int:
        return int(
            self._conn.execute("SELECT COUNT(DISTINCT sku) FROM selections").fetchone()[0]
        )

    def close(self) -> None:
        self._conn.close()
