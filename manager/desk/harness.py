"""The Academy — how the Manager gets better over time without drifting off the laws.

Two layers, deliberately separate:

  laws.md          immutable, hash-locked, Farid-only  (laws.py)
  state/harness.json  refinable, append-logged, agent-writable  (this file)

Every write is evidence-backed and lands in `state/harness_log.jsonl` with a before/after,
so a month of self-improvement can be read as a diff rather than taken on faith. The
law-guard rejects entries that try to reinterpret a protected topic — an agent that
"learns" it may skip approval has learned the one thing it is not allowed to learn.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .laws import PROTECTED_TOPICS

EntryKind = Literal["lesson", "skill", "agent_spec"]
KINDS: tuple[str, ...] = ("lesson", "skill", "agent_spec")

# An entry that both names a protected topic AND uses loosening language is rejected.
# Naming a protected topic alone is fine ("logged the approval token for job 12") —
# it's the combination with permission-weakening verbs that we refuse.
_LOOSENING = re.compile(
    r"\b(skip|bypass|ignore|override|without|no longer|not required|unnecessary|"
    r"exempt|waive|assume|auto[- ]?approve|self[- ]?approve|relax|loosen|"
    r"don'?t need|need not)\b",
    re.IGNORECASE,
)


class LawGuardRejection(ValueError):
    """A proposed harness entry would weaken a law."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def law_guard(text: str) -> None:
    """Reject text that combines a protected topic with permission-weakening language.

    Deliberately blunt and deterministic. A false positive costs one rephrase; a false
    negative costs the property the whole design exists to provide.
    """
    lowered = text.lower()
    hit_topic = next((t for t in PROTECTED_TOPICS if t in lowered), None)
    if hit_topic is None:
        return
    loosening = _LOOSENING.search(text)
    if loosening is None:
        return
    raise LawGuardRejection(
        f"Refused: this entry touches the protected topic {hit_topic!r} with "
        f"loosening language {loosening.group(0)!r}. The laws are not refinable. "
        f"If the law itself is wrong, that is Farid's call — write him a note in "
        f"channel/TO_FARID/ instead."
    )


@dataclass
class Entry:
    id: str
    kind: EntryKind
    title: str
    body: str
    evidence: str
    created: str
    updated: str
    hits: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class Harness:
    path: Path
    log_path: Path
    entries: dict[str, Entry] = field(default_factory=dict)

    # ---------- persistence ----------

    @classmethod
    def load(cls, state_dir: Path) -> "Harness":
        state_dir.mkdir(parents=True, exist_ok=True)
        path = state_dir / "harness.json"
        h = cls(path=path, log_path=state_dir / "harness_log.jsonl")
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            h.entries = {k: Entry(**v) for k, v in raw.get("entries", {}).items()}
        return h

    def save(self) -> None:
        payload = {"entries": {k: v.to_dict() for k, v in self.entries.items()}}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _log(self, action: str, entry_id: str, before: Any, after: Any, evidence: str) -> None:
        record = {
            "at": _now(),
            "action": action,
            "id": entry_id,
            "before": before,
            "after": after,
            "evidence": evidence,
        }
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")

    # ---------- the writable surface ----------

    def write(self, kind: EntryKind, title: str, body: str, evidence: str) -> Entry:
        """Add or update a refinable entry. Every field is law-guarded."""
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {KINDS}, got {kind!r}")
        if not evidence.strip():
            raise ValueError(
                "An entry needs evidence from this session — a tool result, a job "
                "outcome, a file path. Unsourced lessons are how drift starts."
            )
        for chunk in (title, body, evidence):
            law_guard(chunk)

        entry_id = _slug(kind, title)
        before = self.entries[entry_id].to_dict() if entry_id in self.entries else None
        now = _now()
        if before is None:
            entry = Entry(
                id=entry_id, kind=kind, title=title, body=body,
                evidence=evidence, created=now, updated=now,
            )
        else:
            entry = self.entries[entry_id]
            entry.body = body
            entry.evidence = evidence
            entry.updated = now
        self.entries[entry_id] = entry
        self.save()
        self._log("write", entry_id, before, entry.to_dict(), evidence)
        return entry

    def retract(self, entry_id: str, reason: str) -> bool:
        """Delete an entry that turned out to be wrong. Wrong lessons are worse than none."""
        entry = self.entries.pop(entry_id, None)
        if entry is None:
            return False
        self.save()
        self._log("retract", entry_id, entry.to_dict(), None, reason)
        return True

    # ---------- the readable surface ----------

    def recall(self, kind: EntryKind | None = None) -> list[Entry]:
        items = [e for e in self.entries.values() if kind is None or e.kind == kind]
        return sorted(items, key=lambda e: e.updated, reverse=True)

    def system_section(self, limit: int = 40) -> str:
        """The refinable half of the system prompt."""
        items = self.recall()[:limit]
        if not items:
            return (
                "<harness>\nNothing learned yet. Write your first lesson once you have "
                "evidence for it.\n</harness>"
            )
        lines = [
            "<harness>",
            "What you have learned so far. These are yours and revisable; the laws above "
            "are not.",
            "",
        ]
        for e in items:
            lines.append(f"- [{e.kind}] {e.title}: {e.body}  (evidence: {e.evidence})")
        lines.append("</harness>")
        return "\n".join(lines)


def _slug(kind: str, title: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
    return f"{kind}:{base or 'untitled'}"
