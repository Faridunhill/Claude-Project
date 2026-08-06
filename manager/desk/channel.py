"""The bridge to the cloud front.

`channel/` in the Claude-Project repo is the only thing the two halves of the empire
share. The Manager reads what Farid dropped in TO_AGENT and writes numbered notes back
to TO_FARID, following the protocol already documented in channel/README.md.

Nothing here pushes to git — writing the file is the Manager's job, deciding to publish
is Farid's.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any


class Channel:
    def __init__(self, channel_dir: Path):
        self.root = channel_dir
        self.to_agent = channel_dir / "TO_AGENT"
        self.to_farid = channel_dir / "TO_FARID"
        self.uploads = channel_dir / "NEW_UPLOADS"

    def available(self) -> bool:
        return self.to_farid.is_dir()

    def inbox(self) -> list[dict[str, Any]]:
        """Everything Farid has left for the Manager, newest first."""
        out: list[dict[str, Any]] = []
        for folder in (self.to_agent, self.uploads):
            if not folder.is_dir():
                continue
            for p in sorted(folder.iterdir()):
                if p.is_dir():
                    out.append({"box": folder.name, "name": p.name, "kind": "folder"})
                    continue
                item: dict[str, Any] = {"box": folder.name, "name": p.name, "kind": "file",
                                        "bytes": p.stat().st_size}
                if p.suffix.lower() in {".md", ".txt"} and p.stat().st_size < 200_000:
                    item["text"] = p.read_text(encoding="utf-8", errors="replace")
                out.append(item)
        return out

    def _next_number(self) -> int:
        highest = 0
        if self.to_farid.is_dir():
            for p in self.to_farid.glob("*.md"):
                m = re.match(r"^(\d{3})_", p.name)
                if m:
                    highest = max(highest, int(m.group(1)))
        return highest + 1

    def write_note(self, title: str, body: str) -> Path:
        """Leave a numbered, dated note for Farid — the protocol from channel/README.md."""
        self.to_farid.mkdir(parents=True, exist_ok=True)
        n = self._next_number()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "note"
        path = self.to_farid / f"{n:03d}_{date.today().isoformat()}_{slug}.md"
        path.write_text(
            f"# {n:03d} — {title}\n\n{body.strip()}\n\n— your agent (Manager, local)\n",
            encoding="utf-8",
        )
        return path
