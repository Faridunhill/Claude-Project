"""THE WALL — shared cookbook, separate kitchens.

Finding B3: methods travel, data never does. A lesson may leave a clone only
by passing four written checks, and every crossing is logged. The machine
pre-fills the four results and its recommendation; Farid answers yes or no;
the machine writes the row (doc 004 §2.1).

The dangerous case this exists to stop:
  CROSSES     "photograph the maker's mark at an angle that shows wear"
  DOES NOT    "pre-1970 Dunhills clear at $340+ within nine days"
              — data wearing a method's coat.
"""
from __future__ import annotations

import pathlib
import re

from .ledger import AppendOnlyLog, LedgerError, now_iso

MONEY = re.compile(r"[$€£¥]\s?\d|(?<!\w)\d[\d,.]*\s?(?:usd|eur|gbp|dollars?|euros?)\b", re.I)
FIGURES = re.compile(r"(?<!\w)\d[\d,.]*\s?(?:%|percent|units?|orders?|sales?|items?|days?)\b", re.I)
IDENTIFIER = re.compile(
    r"[\w.+-]+@[\w-]+\.\w+"                       # email
    r"|\bthe (?:buyer|customer|seller|bidder) who\b"  # derivable description
    r"|\b(?:user|account|member)\s*#?\d+\b",
    re.I,
)

TESTS = (
    "1 · no business-specific proper nouns (customers, suppliers, our listings, our brands)",
    "2 · no absolute figures from one business (prices, margins, volumes, counts)",
    "3 · no customer identifier, direct or derivable",
    "4 · it would still be true for a business selling something else",
)


def admission_test(claim: str, proper_nouns: list[str] | None = None) -> dict:
    """Returns the four results plus a recommendation. Checks 1–3 are
    mechanical; check 4 is a judgement the machine can only propose."""
    proper_nouns = proper_nouns or []
    hits = {
        1: [w for w in proper_nouns if re.search(rf"\b{re.escape(w)}\b", claim, re.I)],
        2: [m.group(0) for m in list(MONEY.finditer(claim)) + list(FIGURES.finditer(claim))],
        3: [m.group(0) for m in IDENTIFIER.finditer(claim)],
    }
    results = {n: (not hits[n]) for n in (1, 2, 3)}
    # 4 is inferred from 1–3: a claim naming nothing specific is portable.
    results[4] = all(results.values())
    return {
        "claim": claim,
        "results": results,
        "hits": {n: v for n, v in hits.items() if v},
        "passes": all(results.values()),
        "recommend": "yes" if all(results.values()) else "no",
        "tests": TESTS,
    }


class Cookbook:
    """The only path between clones. Guarded by the admission log."""

    def __init__(self, cookbook_root: str | pathlib.Path):
        self.root = pathlib.Path(cookbook_root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.book = self.root / "COOKBOOK.md"
        self.log = AppendOnlyLog(self.root / "ADMISSION_LOG.jsonl")

    def _claims(self) -> list[str]:
        if not self.book.exists():
            return []
        return [ln.strip("- ").strip() for ln in self.book.read_text(encoding="utf-8").splitlines()
                if ln.startswith("- ")]

    def admit(self, claim: str, *, verdict: str, decided_by: str,
              from_clone: str, proper_nouns: list[str] | None = None) -> dict:
        """verdict is Farid's word. The machine writes the row either way —
        a refusal is as much a record as an admission."""
        assessment = admission_test(claim, proper_nouns)
        if verdict == "yes" and not assessment["passes"]:
            raise LedgerError(
                "cannot admit: the claim fails the admission test "
                f"{assessment['hits']} — it is data wearing a method's coat (B3)"
            )
        row = self.log.append({
            "ts": now_iso(), "claim": claim, "from_clone": from_clone,
            "test_results": {str(k): v for k, v in assessment["results"].items()},
            "machine_recommended": assessment["recommend"],
            "verdict": verdict, "decided_by": decided_by,
        })
        if verdict == "yes":
            existing = self._claims()
            if claim not in existing:
                header = "" if self.book.exists() else (
                    "# COOKBOOK — shared methods only, never data\n\n"
                    "Every line here passed the four-question admission test and is\n"
                    "recorded in ADMISSION_LOG.jsonl. No line may name a business,\n"
                    "a price, a volume, or a customer.\n\n")
                with self.book.open("a", encoding="utf-8") as fh:
                    fh.write(header + f"- {claim}\n")
        return row

    def verify(self) -> tuple[bool, str]:
        """T10 — a cookbook line with no admitted log entry fails the build."""
        ok, msg = self.log.verify()
        if not ok:
            return False, f"admission log: {msg}"
        admitted = {r["claim"] for r in self.log.rows() if r["verdict"] == "yes"}
        for claim in self._claims():
            if claim not in admitted:
                return False, f"cookbook line has no admission-log entry: {claim!r}"
            if not admission_test(claim)["passes"]:
                return False, f"cookbook line no longer passes the test: {claim!r}"
        return True, f"wall intact ({len(self._claims())} shared methods)"
