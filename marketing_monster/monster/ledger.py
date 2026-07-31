"""Ledger primitives — append-only files with a tamper-evident hash chain.

Law (doc 004 §2.1): the machine writes every row. Nothing in this module
offers an update or a delete, by design. A correction is a new row that
points at the row it corrects.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import secrets
from datetime import datetime, timezone

GENESIS = "0" * 64


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def cohort_of(ts: str) -> str:
    """ISO week label, e.g. 2026-W32 — the Scale's default grouping window."""
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def row_hash(prev: str, payload: dict) -> str:
    blob = prev + json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class AppendOnlyLog:
    """A JSONL ledger. Rows carry `seq`, `prev` and `hash`, so an edit made
    outside this API is detectable by verify()."""

    def __init__(self, path: os.PathLike | str):
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def rows(self) -> list[dict]:
        if not self.path.exists():
            return []
        out = []
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def _tail(self) -> tuple[int, str]:
        rows = self.rows()
        if not rows:
            return 0, GENESIS
        return rows[-1]["seq"], rows[-1]["hash"]

    def append(self, payload: dict) -> dict:
        seq, prev = self._tail()
        payload = dict(payload)
        payload["seq"] = seq + 1
        payload["prev"] = prev
        payload["id"] = payload.get("id") or f"{payload['seq']:08d}-{secrets.token_hex(3)}"
        payload["hash"] = row_hash(prev, {k: v for k, v in payload.items() if k != "hash"})
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
        return payload

    def verify(self) -> tuple[bool, str]:
        """Recompute the chain. Returns (ok, message). Any row edited or
        removed after the fact breaks it — that is the point."""
        prev = GENESIS
        for i, row in enumerate(self.rows(), start=1):
            if row.get("seq") != i:
                return False, f"row {i}: seq out of order (got {row.get('seq')})"
            if row.get("prev") != prev:
                return False, f"row {i}: broken link — previous row edited or removed"
            expect = row_hash(prev, {k: v for k, v in row.items() if k != "hash"})
            if row.get("hash") != expect:
                return False, f"row {i}: content edited after writing"
            prev = row["hash"]
        return True, f"chain intact ({len(self.rows())} rows)"


class LedgerError(ValueError):
    """Raised when a write would break a law. Always fail loudly."""
