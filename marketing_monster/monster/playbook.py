"""THE PLAYBOOK — the living half of "frozen brain, living playbook".

Laws enforced here (doc 003 App. B — finding B2, the anti-superstition rules):
  · every line carries n, effect, born, review, src — no exceptions
  · two tiers: STRUCT (high-N proxy metrics) learns fast, OUTCOME (low-N
    revenue) learns slowly
  · nothing reaches CONFIRMED on a single cohort, unless Farid says so and
    the line records that it was his call (src=farid)
  · a line past its review date drops to PROPOSED and stops being read
  · 40 CONFIRMED lines maximum — a cap forces retirement and keeps the file
    short enough that a local model weights every line
"""
from __future__ import annotations

import pathlib
import re
from datetime import date, timedelta

from .ledger import LedgerError

TIERS = {"STRUCT", "OUTCOME"}
STATUSES = {"PROPOSED", "CONFIRMED", "RETIRED"}
CONFIRMED_CAP = 40
REVIEW_DAYS = {"STRUCT": 180, "OUTCOME": 365}

LINE_RE = re.compile(
    r"^\[(?P<tier>\w+)\]\[(?P<status>\w+)\]\s*(?P<claim>.+?)\s*"
    r"::\s*n=(?P<n>[^:]+?)\s*"
    r"::\s*effect=(?P<effect>[^:]+?)\s*"
    r"::\s*born=(?P<born>\d{4}-\d{2}-\d{2})\s*"
    r"::\s*review=(?P<review>\d{4}-\d{2}-\d{2})\s*"
    r"::\s*src=(?P<src>\S+)\s*$"
)

HEADER = """# PLAYBOOK — machine-written, human-deletable

Read before every generation. The Maker reads CONFIRMED only; the Judge may
read PROPOSED. Delete any line at any time — deleting is not maintenance,
it is the safety valve.

"""


class Line:
    __slots__ = ("tier", "status", "claim", "n", "effect", "born", "review", "src", "cohorts")

    def __init__(self, tier, status, claim, n, effect, born, review, src, cohorts=None):
        if tier not in TIERS:
            raise LedgerError(f"unknown tier {tier!r}")
        if status not in STATUSES:
            raise LedgerError(f"unknown status {status!r}")
        for field, val in (("claim", claim), ("n", n), ("effect", effect),
                           ("born", born), ("review", review), ("src", src)):
            if not str(val).strip():
                raise LedgerError(
                    f"playbook line missing {field!r} — B2: a lesson without its "
                    "evidence is a superstition"
                )
        self.tier, self.status, self.claim = tier, status, str(claim).strip()
        self.n, self.effect, self.src = str(n).strip(), str(effect).strip(), str(src).strip()
        self.born, self.review = str(born), str(review)
        self.cohorts = set(cohorts or ())

    def __str__(self) -> str:
        return (f"[{self.tier}][{self.status}] {self.claim} :: n={self.n} :: "
                f"effect={self.effect} :: born={self.born} :: review={self.review} "
                f":: src={self.src}")

    @classmethod
    def parse(cls, text: str) -> "Line":
        m = LINE_RE.match(" ".join(text.split()))
        if not m:
            raise LedgerError(
                "unparseable playbook line — required form:\n"
                "  [STRUCT|OUTCOME][PROPOSED|CONFIRMED|RETIRED] claim :: n=.. :: "
                "effect=.. :: born=YYYY-MM-DD :: review=YYYY-MM-DD :: src=.."
            )
        return cls(**{k: m.group(k) for k in
                      ("tier", "status", "claim", "n", "effect", "born", "review", "src")})

    def is_expired(self, today: date | None = None) -> bool:
        return date.fromisoformat(self.review) < (today or date.today())


class Playbook:
    def __init__(self, clone_root: str | pathlib.Path):
        self.path = pathlib.Path(clone_root) / "playbook" / "PLAYBOOK.md"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def lines(self) -> list[Line]:
        if not self.path.exists():
            return []
        out = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if raw.strip().startswith("["):
                out.append(Line.parse(raw))
        return out

    def _write(self, lines: list[Line]) -> None:
        body = HEADER + "\n".join(str(x) for x in lines) + ("\n" if lines else "")
        self.path.write_text(body, encoding="utf-8")

    def propose(self, tier: str, claim: str, n: str, effect: str, src: str,
                today: date | None = None) -> Line:
        today = today or date.today()
        line = Line(tier, "PROPOSED", claim, n, effect, today.isoformat(),
                    (today + timedelta(days=REVIEW_DAYS[tier])).isoformat(), src)
        self._write(self.lines() + [line])
        return line

    def add_line(self, text: str) -> Line | None:
        """Take a fully-formed line (from a dig) into the playbook as PROPOSED.
        Returns None if the claim is already present — a dig re-run must not
        stack duplicates of the same lesson."""
        line = Line.parse(text)
        line.status = "PROPOSED"
        existing = self.lines()
        if any(x.claim == line.claim for x in existing):
            return None
        self._write(existing + [line])
        return line

    def promote(self, claim: str, cohorts: list[str], *, src: str | None = None,
                today: date | None = None) -> Line:
        """PROPOSED -> CONFIRMED. B2: two non-overlapping cohorts, or Farid's
        explicit override recorded honestly as src=farid."""
        lines = self.lines()
        idx = next((i for i, x in enumerate(lines) if x.claim == claim), None)
        if idx is None:
            raise LedgerError(f"no playbook line matching {claim!r}")
        by_farid = (src or lines[idx].src) == "farid"
        if len(set(cohorts)) < 2 and not by_farid:
            raise LedgerError(
                f"cannot confirm on {len(set(cohorts))} cohort(s) — B2 requires two "
                "non-overlapping cohorts, or Farid's override marked src=farid"
            )
        confirmed = sum(1 for x in lines if x.status == "CONFIRMED")
        if confirmed >= CONFIRMED_CAP:
            raise LedgerError(
                f"playbook is at its cap of {CONFIRMED_CAP} CONFIRMED lines — "
                "retire one before adding another (N2)"
            )
        lines[idx].status = "CONFIRMED"
        if src:
            lines[idx].src = src
        lines[idx].cohorts = set(cohorts)
        self._write(lines)
        return lines[idx]

    def expire_due(self, today: date | None = None) -> list[Line]:
        """A CONFIRMED line past its review date drops back to PROPOSED and is
        no longer read by the Maker. Nobody has to remember to do this."""
        today = today or date.today()
        lines, dropped = self.lines(), []
        for line in lines:
            if line.status == "CONFIRMED" and line.is_expired(today):
                line.status = "PROPOSED"
                dropped.append(line)
        if dropped:
            self._write(lines)
        return dropped

    def for_maker(self, today: date | None = None) -> list[Line]:
        """What the Maker is allowed to read: CONFIRMED and in date."""
        today = today or date.today()
        return [x for x in self.lines()
                if x.status == "CONFIRMED" and not x.is_expired(today)]

    def version(self) -> str:
        """Stamp for Maker output (N1) — the rollback key."""
        import hashlib
        digest = hashlib.sha256(
            "\n".join(str(x) for x in self.for_maker()).encode("utf-8")
        ).hexdigest()[:8]
        return f"pb-{date.today().isoformat()}-{digest}"
