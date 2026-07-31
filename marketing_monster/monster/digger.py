"""THE DIGGER — research, with a permission basis and an expiry date.

Finding M3: public data is scaffolding. Every outside source records how we
were allowed to read it and when the claims drawn from it go stale; own
transactions replace them plank by plank.
"""
from __future__ import annotations

import pathlib
from datetime import date, timedelta

from .ledger import AppendOnlyLog, LedgerError, now_iso

SOURCE_TYPES = {"api", "public_page", "own_transaction", "interview", "purchased"}
PERMISSION = {"official_api", "terms_permit", "purchased", "owned"}
SCAFFOLD_DAYS = 180


class Digger:
    def __init__(self, clone_root: str | pathlib.Path):
        self.root = pathlib.Path(clone_root)
        self.log = AppendOnlyLog(self.root / "digger" / "sources.jsonl")

    def record_source(self, url: str, *, source_type: str, permission_basis: str,
                      claims: list[str] | None = None,
                      expires_on: str | None = None) -> dict:
        if source_type not in SOURCE_TYPES:
            raise LedgerError(f"unknown source_type {source_type!r}")
        if permission_basis not in PERMISSION:
            raise LedgerError(
                f"unknown permission_basis {permission_basis!r} — M3: if we cannot name "
                "how we were allowed to read it, we do not read it"
            )
        own = source_type == "own_transaction"
        return self.log.append({
            "ts": now_iso(), "url": url, "source_type": source_type,
            "permission_basis": permission_basis, "claims_derived": claims or [],
            "expires_on": None if own else (
                expires_on or (date.today() + timedelta(days=SCAFFOLD_DAYS)).isoformat()),
            "replaced_by": None,
        })

    def replace(self, source_id: str, own_evidence_id: str) -> dict:
        """A plank of scaffolding replaced by our own transaction evidence."""
        target = next((r for r in self.log.rows() if r["id"] == source_id), None)
        if target is None:
            raise LedgerError(f"no such source {source_id!r}")
        row = dict(target)
        row.update({"ts": now_iso(), "replaced_by": own_evidence_id, "supersedes": source_id})
        for key in ("id", "seq", "prev", "hash"):
            row.pop(key, None)
        return self.log.append(row)

    def expired(self, today: date | None = None) -> list[dict]:
        today = today or date.today()
        live = {r["url"]: r for r in self.log.rows() if not r.get("replaced_by")}
        return [r for r in live.values()
                if r.get("expires_on") and date.fromisoformat(r["expires_on"]) < today]

    def must_read_rejects(self, judge) -> list[str]:
        """M2: the Digger reads the reject log before proposing anything."""
        return [f"{r['decision_id']}: {r['proposal']} — {r['reason']}" for r in judge.rejects()]
