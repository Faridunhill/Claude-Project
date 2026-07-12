"""SQLite genome store — Layer 1 persistence.

Three tables:
  genome              — birth records, INSERT-ONLY (immutability in code)
  corrections_ledger  — append-only correction rows
  visibility          — quarantine state machine per SKU

The store is self-contained (its own genome.db). Priority 1's
itemassets.db is consumed through adapter_itemassets.py — marketing
reads it as a client, never extends or modifies it (handoff §DEPENDENCIES).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional

from .corrections import Correction, CorrectionReason, Visibility, apply_corrections, transition
from .schema import ProductGenome
from .vocab import FieldSource

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS genome (
    sku            TEXT PRIMARY KEY,
    record_json    TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    entry_ts       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS corrections_ledger (
    correction_id  TEXT PRIMARY KEY,
    sku            TEXT NOT NULL REFERENCES genome(sku),
    field_path     TEXT NOT NULL,
    old_value      TEXT,
    new_value      TEXT,
    reason         TEXT NOT NULL,
    note           TEXT,
    source         TEXT NOT NULL,
    ts             TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_corrections_sku ON corrections_ledger (sku, ts);
CREATE TABLE IF NOT EXISTS visibility (
    sku            TEXT PRIMARY KEY REFERENCES genome(sku),
    state          TEXT NOT NULL,
    reason         TEXT,
    updated_ts     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
"""


class BirthRecordExists(Exception):
    """Raised on any attempt to write a SKU that already has a birth
    record. Birth data is immutable — use the corrections ledger."""


class GenomeStore:
    def __init__(self, db_path: str | Path):
        self._conn = sqlite3.connect(str(db_path))
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA_SQL)
        self._conn.commit()

    # -- birth records ------------------------------------------------

    def write_birth(self, genome: ProductGenome) -> None:
        """INSERT-ONLY. A second write for the same SKU raises — there
        is no update path for birth records, by design."""
        try:
            self._conn.execute(
                "INSERT INTO genome (sku, record_json, schema_version, entry_ts) VALUES (?,?,?,?)",
                (
                    genome.sku,
                    genome.model_dump_json(),
                    genome.schema_version,
                    genome.entry_ts.isoformat(),
                ),
            )
            self._conn.execute(
                "INSERT INTO visibility (sku, state) VALUES (?,?)",
                (genome.sku, Visibility.LIVE.value),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as err:
            self._conn.rollback()
            raise BirthRecordExists(
                f"birth record for {genome.sku} already exists; "
                "corrections go to the ledger, never to the birth record"
            ) from err

    def get_birth(self, sku: str) -> Optional[dict[str, Any]]:
        row = self._conn.execute(
            "SELECT record_json FROM genome WHERE sku = ?", (sku,)
        ).fetchone()
        return json.loads(row[0]) if row else None

    # -- corrections ledger --------------------------------------------

    def record_correction(self, correction: Correction) -> None:
        if self.get_birth(correction.sku) is None:
            raise KeyError(f"no birth record for {correction.sku}")
        self._conn.execute(
            "INSERT INTO corrections_ledger "
            "(correction_id, sku, field_path, old_value, new_value, reason, note, source, ts) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                correction.correction_id,
                correction.sku,
                correction.field_path,
                json.dumps(correction.old_value),
                json.dumps(correction.new_value),
                correction.reason.value,
                correction.note,
                correction.source.value,
                correction.ts.isoformat(),
            ),
        )
        self._conn.commit()

    def get_corrections(self, sku: str) -> list[Correction]:
        rows = self._conn.execute(
            "SELECT correction_id, sku, field_path, old_value, new_value, reason, note, source, ts "
            "FROM corrections_ledger WHERE sku = ? ORDER BY ts",
            (sku,),
        ).fetchall()
        return [
            Correction(
                correction_id=r[0],
                sku=r[1],
                field_path=r[2],
                old_value=json.loads(r[3]) if r[3] is not None else None,
                new_value=json.loads(r[4]) if r[4] is not None else None,
                reason=CorrectionReason(r[5]),
                note=r[6],
                source=FieldSource(r[7]),
                ts=r[8],
            )
            for r in rows
        ]

    def get_effective(self, sku: str) -> Optional[dict[str, Any]]:
        """effective_data = birth + corrections. This is what every
        generator reads. The birth record itself is never modified."""
        birth = self.get_birth(sku)
        if birth is None:
            return None
        return apply_corrections(birth, self.get_corrections(sku))

    # -- visibility state machine ---------------------------------------

    def get_visibility(self, sku: str) -> Optional[Visibility]:
        row = self._conn.execute(
            "SELECT state FROM visibility WHERE sku = ?", (sku,)
        ).fetchone()
        return Visibility(row[0]) if row else None

    def set_visibility(self, sku: str, target: Visibility, reason: str = "") -> Visibility:
        current = self.get_visibility(sku)
        if current is None:
            raise KeyError(f"no visibility record for {sku}")
        new_state = transition(current, target)  # raises on illegal transition
        self._conn.execute(
            "UPDATE visibility SET state = ?, reason = ?, "
            "updated_ts = strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE sku = ?",
            (new_state.value, reason, sku),
        )
        self._conn.commit()
        return new_state

    def quarantine(self, sku: str, reason: str) -> Visibility:
        """detect → quarantine. Channel adapters must delist on this
        state; batch corrections where possible (rapid delist/relist
        cycles trip marketplace anomaly flags — Gemini's own caution)."""
        return self.set_visibility(sku, Visibility.QUARANTINED, reason)

    def close(self) -> None:
        self._conn.close()
