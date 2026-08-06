"""Approval tokens — the only way an ACTION ever runs.

Farid issues a token for one named action. It is single-use and expires. The Manager
cannot mint one: `issue()` is reached from the CLI only, and the agent's tool surface
exposes `consume` indirectly (through machine.run) and nothing else.
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_TTL_MINUTES = 60


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ApprovalBook:
    path: Path
    tokens: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, state_dir: Path) -> "ApprovalBook":
        state_dir.mkdir(parents=True, exist_ok=True)
        path = state_dir / "approvals.json"
        tokens = {}
        if path.exists():
            tokens = json.loads(path.read_text(encoding="utf-8"))
        return cls(path=path, tokens=tokens)

    def save(self) -> None:
        self.path.write_text(json.dumps(self.tokens, indent=2, sort_keys=True), encoding="utf-8")

    def issue(self, action: str, ttl_minutes: int = DEFAULT_TTL_MINUTES) -> str:
        """Farid-only. Mint a single-use token for one action."""
        token = secrets.token_urlsafe(12)
        self.tokens[token] = {
            "action": action,
            "issued": _now().isoformat(timespec="seconds"),
            "expires": (_now() + timedelta(minutes=ttl_minutes)).isoformat(timespec="seconds"),
            "used": False,
        }
        self.save()
        return token

    def consume(self, action: str, token: str | None) -> bool:
        """Spend a token for `action`. False on anything less than a perfect match."""
        if not token:
            return False
        record = self.tokens.get(token)
        if record is None or record["used"] or record["action"] != action:
            return False
        if datetime.fromisoformat(record["expires"]) < _now():
            return False
        record["used"] = True
        record["used_at"] = _now().isoformat(timespec="seconds")
        self.save()
        return True

    def pending(self) -> list[dict[str, Any]]:
        now = _now()
        return [
            {"token": t[:6] + "...", **r}
            for t, r in self.tokens.items()
            if not r["used"] and datetime.fromisoformat(r["expires"]) >= now
        ]
