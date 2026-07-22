"""Review queue + verdict application (Synthesis §5).

The review screen: stamping macros at zoom, OCR verbatim, the model's
claim with confidence, 2-3 reference exemplars. ONE question, THREE
buttons: Yes / No / Can't tell. ~30 seconds per item.

Verdict application NEVER touches the birth record — attribution state
lands via the corrections ledger:

  YES        -> claim verified: correction sets the field + attribution
                status VERIFIED (assertive copy allowed)
  NO         -> claim rejected: attribution REJECTED, field stays null
  CAN'T TELL -> hedge-and-list: attribution UNVERIFIED, candidate
                recorded, PRICE AT THE NO-NAME FLOOR — unless the
                candidate is worth >= research_queue_min_uplift over the
                floor, in which case the item goes to the research-later
                queue instead of listing.

Underclaiming costs margin; overclaiming costs the business.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from ..genome.corrections import Correction, CorrectionReason
from ..genome.store import GenomeStore
from ..genome.vocab import AttributionStatus, FieldSource, MediaRole
from .gate import GateConfig, GateDecision, Route

_SQL = """
CREATE TABLE IF NOT EXISTS review_queue (
    review_id   TEXT PRIMARY KEY,
    sku         TEXT NOT NULL,
    field_path  TEXT NOT NULL,
    claim_json  TEXT NOT NULL,
    reasons     TEXT NOT NULL,
    kind        TEXT NOT NULL,             -- review | audit
    status      TEXT NOT NULL DEFAULT 'pending',  -- pending | done
    verdict     TEXT,                      -- yes | no | cant_tell
    outcome     TEXT,                      -- verified|rejected|hedged|research_later
    uplift      REAL,                      -- candidate value over no-name floor
    created_ts  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    decided_ts  TEXT
);
CREATE INDEX IF NOT EXISTS idx_review_pending ON review_queue (status, created_ts);
"""


class Verdict(str, Enum):
    YES = "yes"
    NO = "no"
    CANT_TELL = "cant_tell"


@dataclass(frozen=True)
class ReviewScreen:
    """Everything the human sees — one screen, one question."""

    review_id: str
    sku: str
    field_path: str
    claimed_value: object
    confidence: float
    stamping_photos: list[str]
    ocr_verbatim: Optional[str]
    exemplars: list[str]
    question: str


class ReviewQueue:
    def __init__(self, db_path: str | Path, store: GenomeStore, config: GateConfig = GateConfig()):
        self._conn = sqlite3.connect(str(db_path))
        self._conn.executescript(_SQL)
        self._conn.commit()
        self._store = store
        self._config = config

    # -- enqueue -------------------------------------------------------

    def enqueue(self, decision: GateDecision) -> Optional[str]:
        """Queue a REVIEW or AUDIT decision. AUTO_PASS is not queued."""
        if decision.route is Route.AUTO_PASS:
            return None
        review_id = f"rev-{uuid.uuid4().hex[:12]}"
        self._conn.execute(
            "INSERT INTO review_queue (review_id, sku, field_path, claim_json, reasons, kind) "
            "VALUES (?,?,?,?,?,?)",
            (
                review_id,
                decision.sku,
                decision.claim.field_path,
                json.dumps({
                    "value": decision.claim.value,
                    "confidence": decision.claim.confidence,
                    "model_version": decision.claim.model_version,
                }),
                ",".join(r.value for r in decision.reasons),
                decision.route.value,
            ),
        )
        self._conn.commit()
        return review_id

    # -- the screen ----------------------------------------------------

    def build_screen(
        self,
        review_id: str,
        exemplars: Optional[list[str]] = None,
    ) -> ReviewScreen:
        row = self._conn.execute(
            "SELECT sku, field_path, claim_json FROM review_queue WHERE review_id = ?",
            (review_id,),
        ).fetchone()
        if row is None:
            raise KeyError(review_id)
        sku, field_path, claim_json = row
        claim = json.loads(claim_json)

        effective = self._store.get_effective(sku) or {}
        stamping = [
            m["url"] for m in effective.get("media", [])
            if m.get("role") == MediaRole.STAMPING.value
        ]
        ocr = (effective.get("unique_physical") or {}).get("stampings_verbatim")

        return ReviewScreen(
            review_id=review_id,
            sku=sku,
            field_path=field_path,
            claimed_value=claim["value"],
            confidence=claim["confidence"],
            stamping_photos=stamping,
            ocr_verbatim=ocr,
            exemplars=exemplars or [],
            question=f"Is this stamping consistent with {claim['value']}?",
        )

    # -- verdicts ------------------------------------------------------

    def decide(self, review_id: str, verdict: Verdict, uplift: float = 0.0) -> str:
        """Apply a human verdict. Returns the outcome. All genome effects
        go through the corrections ledger — never the birth record."""
        row = self._conn.execute(
            "SELECT sku, field_path, claim_json, status FROM review_queue WHERE review_id = ?",
            (review_id,),
        ).fetchone()
        if row is None:
            raise KeyError(review_id)
        sku, field_path, claim_json, status = row
        if status != "pending":
            raise ValueError(f"{review_id} already decided")
        claim = json.loads(claim_json)

        if verdict is Verdict.YES:
            outcome = "verified"
            self._apply(sku, field_path, claim["value"], AttributionStatus.VERIFIED)
        elif verdict is Verdict.NO:
            outcome = "rejected"
            self._apply(sku, field_path, None, AttributionStatus.REJECTED,
                        candidate=str(claim["value"]))
        else:  # CANT_TELL — hedge-and-list, or research-later above uplift
            if uplift >= self._config.research_queue_min_uplift:
                outcome = "research_later"
            else:
                outcome = "hedged"
            self._apply(sku, field_path, None, AttributionStatus.UNVERIFIED,
                        candidate=str(claim["value"]))

        self._conn.execute(
            "UPDATE review_queue SET status='done', verdict=?, outcome=?, uplift=?, "
            "decided_ts=strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE review_id=?",
            (verdict.value, outcome, uplift, review_id),
        )
        self._conn.commit()
        return outcome

    def _apply(
        self,
        sku: str,
        field_path: str,
        value: object,
        status: AttributionStatus,
        candidate: str = "",
    ) -> None:
        if value is not None:
            self._store.record_correction(Correction(
                sku=sku,
                field_path=field_path,
                new_value=value,
                reason=CorrectionReason.EXPERT_REATTRIBUTION,
                note="QA-gate review verdict: yes",
                source=FieldSource.HUMAN,
            ))
        self._store.record_correction(Correction(
            sku=sku,
            field_path=f"{field_path}.__attribution_status"
            if "." in field_path else f"attribution.{field_path}",
            new_value={"status": status.value, "candidate": candidate or str(value)},
            reason=CorrectionReason.EXPERT_REATTRIBUTION,
            note="QA-gate attribution state",
            source=FieldSource.HUMAN,
        ))

    # -- reporting -----------------------------------------------------

    def pending(self, kind: Optional[str] = None) -> list[str]:
        q = "SELECT review_id FROM review_queue WHERE status='pending'"
        args: tuple = ()
        if kind:
            q += " AND kind=?"
            args = (kind,)
        return [r[0] for r in self._conn.execute(q + " ORDER BY created_ts", args)]

    def hedged_listing_discount(self) -> float:
        """Monthly report line (Code risk #1): the gate's visible cost —
        sum of candidate uplift across hedged items."""
        row = self._conn.execute(
            "SELECT COALESCE(SUM(uplift), 0) FROM review_queue WHERE outcome='hedged'"
        ).fetchone()
        return float(row[0])

    def close(self) -> None:
        self._conn.close()
