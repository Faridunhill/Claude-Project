"""THE JUDGE — worth doing? which channels? what price?

Finding M2: a Judge with no written record re-argues dead categories forever
and can never be evaluated. Every proposal produces a row; REJECTs are
permanent memory the Digger must read before proposing again.
"""
from __future__ import annotations

import pathlib

from .ledger import AppendOnlyLog, LedgerError, now_iso

EDGES = {"germany_route", "audience", "expertise", "NONE"}
VERDICTS = {"DO", "DEFER", "REJECT", "PENDING"}
RESERVED = {"floor_price", "spend", "category", "wall", "none"}
CHANNEL_FLAG = {"organic_only", "paid_allowed"}

# Standing fact: all paid channels are closed on the tobacco category —
# permanent and structural, not a preference (v1.0).
CLONE_CHANNEL = {"pipes": "organic_only", "groundtruth": "organic_only",
                 "ashcombe": "paid_allowed"}


class Judge:
    def __init__(self, clone_root: str | pathlib.Path):
        self.root = pathlib.Path(clone_root)
        self.clone = self.root.name
        self.log = AppendOnlyLog(self.root / "judge" / "decisions.jsonl")

    def channel_flag(self) -> str:
        return CLONE_CHANNEL.get(self.clone, "organic_only")

    def rows(self) -> list[dict]:
        return self.log.rows()

    def rejects(self) -> list[dict]:
        return [r for r in self.rows() if r["verdict"] == "REJECT"]

    def open_items(self) -> list[dict]:
        decided = {r["decision_id"] for r in self.rows() if r["verdict"] != "PENDING"}
        return [r for r in self.rows()
                if r["verdict"] == "PENDING" and r["decision_id"] not in decided]

    def decide(self, proposal: str, *, edge: str, verdict: str, reason: str,
               dig_id: str = "", effort_hrs: float | None = None,
               needs_farid: str = "none", review_on: str = "",
               decision_id: str | None = None, resupply: str = "") -> dict:
        if edge not in EDGES:
            raise LedgerError(f"unknown edge {edge!r}; allowed: {sorted(EDGES)}")
        if verdict not in VERDICTS:
            raise LedgerError(f"unknown verdict {verdict!r}")
        if needs_farid not in RESERVED:
            raise LedgerError(f"unknown reserved power {needs_farid!r}")
        if verdict != "PENDING" and not reason.strip():
            raise LedgerError("every decision carries a written reason — that is the record")
        # M2 — permanent reject memory, checked first: a dead category is dead
        # until something changes, whatever the new proposal claims.
        prior = next((r for r in self.rejects()
                      if r["proposal"].strip().lower() == proposal.strip().lower()), None)
        if prior and not resupply.strip():
            raise LedgerError(
                f"this was rejected on {prior['ts'][:10]} — reason: {prior['reason']!r}. "
                "A re-proposal must state what changed (resupply=...)"
            )

        if verdict == "DO" and edge == "NONE":
            raise LedgerError(
                "edge=NONE cannot be a DO without an override reason — the edge filter "
                "exists to stop knife-fights with Amazon (v1.0)"
            )

        return self.log.append({
            "ts": now_iso(), "clone": self.clone,
            "decision_id": decision_id or f"D-{len(self.rows()) + 1:03d}",
            "proposal": proposal, "dig_id": dig_id, "edge": edge,
            "channel_flag": self.channel_flag(), "effort_hrs": effort_hrs,
            "needs_farid": needs_farid, "verdict": verdict, "reason": reason,
            "review_on": review_on, "resupply": resupply,
        })

    def propose(self, proposal: str, *, edge: str, needs_farid: str,
                recommend: str, dig_id: str = "", effort_hrs: float | None = None) -> dict:
        """Queue a reserved-power item for Farid. The row is written complete,
        with the machine's recommendation, and waits for one word."""
        return self.decide(proposal, edge=edge, verdict="PENDING",
                           reason=f"machine recommends: {recommend}",
                           dig_id=dig_id, effort_hrs=effort_hrs, needs_farid=needs_farid)

    def answer(self, decision_id: str, verdict: str, reason: str) -> dict:
        """Farid's word, written into the ledger by the machine."""
        item = next((r for r in self.open_items() if r["decision_id"] == decision_id), None)
        if item is None:
            raise LedgerError(f"no pending item {decision_id!r}")
        return self.decide(item["proposal"], edge=item["edge"], verdict=verdict,
                           reason=reason, dig_id=item["dig_id"],
                           effort_hrs=item["effort_hrs"], needs_farid=item["needs_farid"],
                           decision_id=decision_id, resupply="answered from PENDING")
