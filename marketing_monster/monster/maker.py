"""THE MAKER — production, and only what the Judge ordered.

Finding N1: every output is stamped with the playbook version that produced
it. When a lesson is retired, "which of my 400 listings were written under
the bad lesson?" becomes a grep instead of an archaeology project.
"""
from __future__ import annotations

import json
import pathlib

from .ledger import LedgerError, now_iso
from .playbook import Playbook


class Maker:
    def __init__(self, clone_root: str | pathlib.Path):
        self.root = pathlib.Path(clone_root)
        self.out = self.root / "maker" / "out"
        self.out.mkdir(parents=True, exist_ok=True)
        self.playbook = Playbook(self.root)

    def publish(self, asset_id: str, body: str, *, decision_id: str,
                asset_version: str | None = None, kind: str = "listing") -> dict:
        """Refuses to write an unstamped asset (T8), and refuses to write at
        all without the Judge decision that ordered it."""
        if not decision_id.strip():
            raise LedgerError(
                "the Maker only produces what the Judge ordered — supply decision_id "
                "(v1.0: organ 4 takes orders, it does not choose work)"
            )
        asset_version = asset_version or self.playbook.version()
        if not asset_version:
            raise LedgerError("refusing to publish without an asset_version stamp (N1)")

        record = {"asset_id": asset_id, "kind": kind, "decision_id": decision_id,
                  "asset_version": asset_version, "created_at": now_iso(),
                  "lessons_applied": [x.claim for x in self.playbook.for_maker()],
                  "body": body}
        path = self.out / f"{asset_id.replace('/', '__')}.json"
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return record

    def assets(self) -> list[dict]:
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.out.glob("*.json"))]

    def written_under(self, asset_version: str) -> list[str]:
        """The rollback query."""
        return [a["asset_id"] for a in self.assets() if a["asset_version"] == asset_version]
