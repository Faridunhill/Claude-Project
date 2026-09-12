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


#: A listing added within this many days counts as "new" and is posted
#: before the backlog. Beyond it, an item is just part of the catalog.
NEW_LISTING_DAYS = 14

#: If more than this fraction of eligible items look new, they are not
#: new — it is a fresh clone or a bulk import, and every file carries
#: the same date. Freshness is then ignored.
FRESH_SIGNAL_LIMIT = 0.2


@dataclass(frozen=True)
class Candidate:
    sku: str
    price: float
    has_photo: bool
    in_stock: bool
    added: Optional[date] = None      # when the listing file appeared


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

        fresh_after = run_date - timedelta(days=NEW_LISTING_DAYS)

        def is_fresh(cand: Candidate) -> bool:
            return cand.added is not None and cand.added >= fresh_after

        # "New" only means something when it distinguishes a few items
        # from the rest. After a fresh clone or a bulk import every file
        # carries today's date, so everything looks new and the signal is
        # noise — fall back to price, which still ranks sensibly.
        fresh_count = sum(1 for cand, _ in eligible if is_fresh(cand))
        freshness_meaningful = 0 < fresh_count <= max(1, len(eligible) * FRESH_SIGNAL_LIMIT)

        def sort_key(pair: tuple[Candidate, Optional[str]]):
            cand, last = pair
            never_posted = 0 if last is None else 1     # never-posted first
            # A listing added this week goes out before the backlog:
            # adding a pipe to the shop should put it on social within a
            # day, not behind 200 older items. Newest first among those.
            if freshness_meaningful and is_fresh(cand):
                freshness = (0, -cand.added.toordinal())
            else:
                freshness = (1, 0)
            return (never_posted, *freshness, last or "", -cand.price, cand.sku)

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
