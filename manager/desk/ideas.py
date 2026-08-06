"""The idea ledger — brainstorm, and then actually reinforce.

Farid's ask was two things, and the second is the hard one. Generating ideas is cheap;
what usually fails is that a good idea from Tuesday is gone by Friday. So an idea here is
a durable row that accumulates evidence over time:

    raw -> reinforced (evidence arrived) -> adopted (became jobs) | parked (didn't hold up)

An idea can only be reinforced with evidence, and its strength is the count of distinct
reinforcements — not the Manager's enthusiasm for it. That way "reinforce the ideas" means
the ones that survive contact with reality rise, and the rest quietly sink.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

Status = Literal["raw", "reinforced", "adopted", "parked"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Idea:
    id: str
    text: str
    born: str
    status: Status = "raw"
    reinforcements: list[dict[str, str]] = field(default_factory=list)
    note: str = ""

    @property
    def strength(self) -> int:
        return len(self.reinforcements)

    def to_dict(self) -> dict[str, Any]:
        d = self.__dict__.copy()
        d["strength"] = self.strength
        return d


class IdeaLedger:
    def __init__(self, state_dir: Path):
        state_dir.mkdir(parents=True, exist_ok=True)
        self.path = state_dir / "ideas.json"
        self.ideas: dict[str, Idea] = {}
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for k, v in raw.items():
                v.pop("strength", None)
                self.ideas[k] = Idea(**v)

    def save(self) -> None:
        payload = {k: v.to_dict() for k, v in self.ideas.items()}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def propose(self, text: str, note: str = "") -> Idea:
        idea_id = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "idea"
        if idea_id in self.ideas:
            return self.ideas[idea_id]
        idea = Idea(id=idea_id, text=text, born=_now(), note=note)
        self.ideas[idea_id] = idea
        self.save()
        return idea

    def reinforce(self, idea_id: str, evidence: str) -> Idea:
        """Strengthen an idea with a concrete observation. Evidence is mandatory —
        an idea that only gets restated hasn't got stronger, it's just been repeated."""
        idea = self.ideas.get(idea_id)
        if idea is None:
            raise KeyError(f"no idea {idea_id!r}")
        if not evidence.strip():
            raise ValueError("reinforcement needs evidence, not just agreement")
        idea.reinforcements.append({"at": _now(), "evidence": evidence.strip()})
        if idea.status == "raw":
            idea.status = "reinforced"
        self.save()
        return idea

    def set_status(self, idea_id: str, status: Status, note: str = "") -> Idea:
        idea = self.ideas[idea_id]
        idea.status = status
        if note:
            idea.note = note
        self.save()
        return idea

    def ranked(self, limit: int = 20) -> list[Idea]:
        """Strongest first. Parked ideas sink but are never deleted — a parked idea that
        gets new evidence later is exactly the kind of thing sessions forget."""
        live = [i for i in self.ideas.values() if i.status != "parked"]
        parked = [i for i in self.ideas.values() if i.status == "parked"]
        live.sort(key=lambda i: (-i.strength, i.born))
        parked.sort(key=lambda i: (-i.strength, i.born))
        return (live + parked)[:limit]

    def brief(self, limit: int = 12) -> str:
        items = self.ranked(limit)
        if not items:
            return "No ideas on the ledger yet."
        return "\n".join(
            f"- [{i.status} x{i.strength}] {i.text}" + (f" — {i.note}" if i.note else "")
            for i in items
        )
