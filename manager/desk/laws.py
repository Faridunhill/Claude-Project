"""The immutable core.

`laws.md` is hash-locked. Nothing in the Manager can edit it — the Academy writes to a
separate refinable layer, and this module is what makes that separation real rather than
a promise. If the file changes without a deliberate relock, the Manager refuses to start.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

LAWS_FILE = "laws.md"
LOCK_FILE = "laws.lock"

# Topics in the laws that the refinable layer is never allowed to reinterpret. Used by the
# law-guard in harness.py. Kept here so the guard's vocabulary lives with the laws.
# These are matched as substrings, so they are written as stems on purpose: "approv"
# catches approve / approval / approved / auto-approve, which "approval" alone does not.
PROTECTED_TOPICS = (
    "approv",
    "honesty",
    "pirate",
    "mirror",
    "scan",
    "launch",
    "domain",
    "museum brand list",
    "subscription",
    "law",
    "laws",
    "permission",
    "gate",
)


class LawsTampered(RuntimeError):
    """laws.md changed without a deliberate relock."""


@dataclass(frozen=True)
class Laws:
    text: str
    digest: str

    def system_preamble(self) -> str:
        return (
            "The following laws are immutable. They were authored by Farid and are "
            "hash-locked; you cannot change them and must not act around them.\n\n"
            f"<laws digest=\"{self.digest[:12]}\">\n{self.text}\n</laws>"
        )


def digest_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load(root: Path) -> Laws:
    """Read and verify laws.md. Raises LawsTampered if the lock doesn't match."""
    laws_path = root / LAWS_FILE
    lock_path = root / LOCK_FILE
    text = laws_path.read_text(encoding="utf-8")
    actual = digest_of(text)

    if not lock_path.exists():
        raise LawsTampered(
            f"{LOCK_FILE} is missing. Read {LAWS_FILE}, confirm it says what you want, "
            f"then run: desk laws --relock"
        )

    expected = lock_path.read_text(encoding="utf-8").strip()
    if expected != actual:
        raise LawsTampered(
            f"{LAWS_FILE} does not match {LOCK_FILE}.\n"
            f"  locked: {expected[:16]}...\n"
            f"  actual: {actual[:16]}...\n"
            "Either restore the file from git, or — if you changed it on purpose — "
            "run: desk laws --relock"
        )
    return Laws(text=text, digest=actual)


def relock(root: Path) -> str:
    """Record the current laws.md as the accepted version. Farid runs this, not the agent."""
    text = (root / LAWS_FILE).read_text(encoding="utf-8")
    d = digest_of(text)
    (root / LOCK_FILE).write_text(d + "\n", encoding="utf-8")
    return d
