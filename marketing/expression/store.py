"""Expression store — versioned, disposable generated content.

Every generated text is recorded with generator_version + inputs_hash
(hash of the effective genome it was computed from). Regeneration is
detected by hash: genome corrected or generator upgraded -> stale ->
regenerate. Rows are never edited; new versions are appended and the
latest wins. Hand-editing has no API on purpose.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_SQL = """
CREATE TABLE IF NOT EXISTS expression_records (
    record_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sku               TEXT NOT NULL,
    kind              TEXT NOT NULL,          -- title | description | caption | ...
    channel           TEXT NOT NULL DEFAULT 'core',
    text              TEXT NOT NULL,
    generator_version TEXT NOT NULL,
    inputs_hash       TEXT NOT NULL,
    created_ts        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_expr_latest ON expression_records (sku, kind, channel, record_id);
"""


def inputs_hash(effective: dict) -> str:
    return hashlib.sha256(
        json.dumps(effective, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


@dataclass(frozen=True)
class ExpressionRecord:
    sku: str
    kind: str
    channel: str
    text: str
    generator_version: str
    inputs_hash: str


class ExpressionStore:
    def __init__(self, db_path: str | Path):
        self._conn = sqlite3.connect(str(db_path))
        self._conn.executescript(_SQL)
        self._conn.commit()

    def put(self, record: ExpressionRecord) -> None:
        self._conn.execute(
            "INSERT INTO expression_records (sku, kind, channel, text, generator_version, inputs_hash) "
            "VALUES (?,?,?,?,?,?)",
            (record.sku, record.kind, record.channel, record.text,
             record.generator_version, record.inputs_hash),
        )
        self._conn.commit()

    def latest(self, sku: str, kind: str, channel: str = "core") -> Optional[ExpressionRecord]:
        row = self._conn.execute(
            "SELECT sku, kind, channel, text, generator_version, inputs_hash "
            "FROM expression_records WHERE sku=? AND kind=? AND channel=? "
            "ORDER BY record_id DESC LIMIT 1",
            (sku, kind, channel),
        ).fetchone()
        return ExpressionRecord(*row) if row else None

    def is_stale(self, sku: str, kind: str, effective: dict,
                 generator_version: str, channel: str = "core") -> bool:
        """Stale when no record exists, the genome changed (corrections),
        or the generator was upgraded."""
        latest = self.latest(sku, kind, channel)
        if latest is None:
            return True
        return (
            latest.inputs_hash != inputs_hash(effective)
            or latest.generator_version != generator_version
        )

    def close(self) -> None:
        self._conn.close()
