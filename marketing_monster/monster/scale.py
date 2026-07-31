"""THE SCALE — records results, writes back to the Well.

Laws enforced here (doc 003 App. A, doc 004 §6):
  B1 · attribution defaults to `unattributable`; upgrading it requires a reason.
  B1 · every row carries its cohort and the asset_version that produced it.
  --  · rows are never edited; a correction is a new row pointing at the old one.
"""
from __future__ import annotations

import pathlib

from .ledger import AppendOnlyLog, LedgerError, cohort_of, now_iso

SURFACES = {"site", "ebay", "etsy", "instagram", "youtube", "email", "other"}
EVENTS = {
    "impression", "visit", "save", "inquiry", "offer",
    "sale", "expired_unsold", "email_capture",
}
ATTRIBUTION = {"direct", "assumed", "unattributable"}
OUTCOME_EVENTS = {"sale", "expired_unsold", "email_capture"}


class Scale:
    def __init__(self, clone_root: str | pathlib.Path):
        self.root = pathlib.Path(clone_root)
        self.clone = self.root.name
        self.log = AppendOnlyLog(self.root / "scale" / "events.jsonl")

    # -- writing ---------------------------------------------------------
    def record(
        self,
        event: str,
        asset_id: str,
        *,
        surface: str = "site",
        asset_version: str | None = None,
        value: float | None = None,
        currency: str = "USD",
        attribution: str | None = None,
        reason: str = "",
        ts: str | None = None,
        note: str = "",
        corrects: str | None = None,
    ) -> dict:
        if event not in EVENTS:
            raise LedgerError(f"unknown event {event!r}; allowed: {sorted(EVENTS)}")
        if surface not in SURFACES:
            raise LedgerError(f"unknown surface {surface!r}; allowed: {sorted(SURFACES)}")

        # B1 — silence means unattributable. The Scale never guesses a cause.
        attribution = attribution or "unattributable"
        if attribution not in ATTRIBUTION:
            raise LedgerError(f"unknown attribution {attribution!r}")
        if attribution != "unattributable" and not reason.strip():
            raise LedgerError(
                f"attribution={attribution!r} requires a written reason "
                "(B1: an upgrade above 'unattributable' must be justified in the row)"
            )

        ts = ts or now_iso()
        return self.log.append({
            "ts": ts,
            "clone": self.clone,
            "surface": surface,
            "asset_id": asset_id,
            "asset_version": asset_version,
            "event": event,
            "value": value,
            "currency": currency,
            "cohort": cohort_of(ts),
            "attribution": attribution,
            "reason": reason,
            "note": note,
            "corrects": corrects,
        })

    def correct(self, event_id: str, reason: str, **fields) -> dict:
        """The only way to change history: append a row that supersedes another."""
        if not reason.strip():
            raise LedgerError("a correction must carry a reason")
        target = next((r for r in self.log.rows() if r["id"] == event_id), None)
        if target is None:
            raise LedgerError(f"no such event {event_id!r}")
        merged = {k: target[k] for k in
                  ("surface", "asset_id", "asset_version", "event", "value", "currency")}
        merged.update(fields)
        merged.setdefault("attribution", target["attribution"])
        return self.record(reason=reason, corrects=event_id, note="correction", **merged)

    # -- reading ---------------------------------------------------------
    def rows(self) -> list[dict]:
        superseded = {r["corrects"] for r in self.log.rows() if r.get("corrects")}
        return [r for r in self.log.rows() if r["id"] not in superseded]

    def cohorts(self, event: str | None = None) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        for r in self.rows():
            if event and r["event"] != event:
                continue
            out.setdefault(r["cohort"], []).append(r)
        return out

    def unattributable_share(self, rows: list[dict] | None = None) -> tuple[int, int]:
        """(unattributable outcomes, total outcomes) — printed in every report,
        however bad it looks. Organic-only means this number is honestly high."""
        rows = [r for r in (rows if rows is not None else self.rows())
                if r["event"] in OUTCOME_EVENTS]
        return sum(1 for r in rows if r["attribution"] == "unattributable"), len(rows)
