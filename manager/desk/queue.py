"""The job queue — how the Manager gives orders to the local agents.

SQLite, because it survives a reboot, handles two processes safely, and needs no server.
A "local agent" here is any worker that claims jobs: a dating-cabinet run, an interview
URL sweep, a whisper transcription, a nightly machine check.

The GPU rule is enforced here rather than left to the model's judgement: a job marked
`needs_gpu` will not be handed out until Farid sets the all-clear. That is the difference
between a rule and a hope.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

STATES = ("queued", "claimed", "done", "failed", "blocked")

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    kind        TEXT NOT NULL,
    title       TEXT NOT NULL,
    payload     TEXT NOT NULL DEFAULT '{}',
    state       TEXT NOT NULL DEFAULT 'queued',
    priority    INTEGER NOT NULL DEFAULT 5,
    needs_gpu   INTEGER NOT NULL DEFAULT 0,
    worker      TEXT,
    result      TEXT,
    created     TEXT NOT NULL,
    updated     TEXT NOT NULL,
    run_after   TEXT
);
CREATE INDEX IF NOT EXISTS jobs_state_prio ON jobs(state, priority, id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class JobQueue:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        with closing(self._conn.cursor()) as cur:
            cur.executescript(SCHEMA)

    # ---------- writing ----------

    def add(
        self,
        kind: str,
        title: str,
        payload: dict[str, Any] | None = None,
        *,
        priority: int = 5,
        needs_gpu: bool = False,
        run_after: str | None = None,
    ) -> int:
        now = _now()
        cur = self._conn.execute(
            "INSERT INTO jobs (kind,title,payload,priority,needs_gpu,created,updated,run_after)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (kind, title, json.dumps(payload or {}), priority,
             int(needs_gpu), now, now, run_after),
        )
        return int(cur.lastrowid)

    def claim(self, worker: str, *, gpu_allclear: bool = False) -> dict[str, Any] | None:
        """Hand the highest-priority runnable job to a worker. GPU jobs stay put until
        Farid gives the all-clear — enforced here, not left to the agent's discretion."""
        now = _now()
        gpu_clause = "" if gpu_allclear else " AND needs_gpu = 0"
        row = self._conn.execute(
            "SELECT * FROM jobs WHERE state='queued'"
            f"{gpu_clause}"
            " AND (run_after IS NULL OR run_after <= ?)"
            " ORDER BY priority ASC, id ASC LIMIT 1",
            (now,),
        ).fetchone()
        if row is None:
            return None
        self._conn.execute(
            "UPDATE jobs SET state='claimed', worker=?, updated=? WHERE id=? AND state='queued'",
            (worker, now, row["id"]),
        )
        return self.get(int(row["id"]))

    def finish(self, job_id: int, *, ok: bool, result: str) -> None:
        self._conn.execute(
            "UPDATE jobs SET state=?, result=?, updated=? WHERE id=?",
            ("done" if ok else "failed", result[:4000], _now(), job_id),
        )

    def block(self, job_id: int, reason: str) -> None:
        """Park a job that can't run yet — a missing fact, a pending answer from Farid."""
        self._conn.execute(
            "UPDATE jobs SET state='blocked', result=?, updated=? WHERE id=?",
            (reason[:4000], _now(), job_id),
        )

    # ---------- reading ----------

    def get(self, job_id: int) -> dict[str, Any] | None:
        row = self._conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return _row(row) if row else None

    def list(self, state: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if state:
            rows = self._conn.execute(
                "SELECT * FROM jobs WHERE state=? ORDER BY priority ASC, id ASC LIMIT ?",
                (state, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM jobs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [_row(r) for r in rows]

    def scoreboard(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT state, COUNT(*) AS n FROM jobs GROUP BY state"
        ).fetchall()
        board = {s: 0 for s in STATES}
        board.update({r["state"]: r["n"] for r in rows})
        return board

    def close(self) -> None:
        self._conn.close()


def _row(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["payload"] = json.loads(d["payload"])
    d["needs_gpu"] = bool(d["needs_gpu"])
    return d


def seed_standing_work(q: JobQueue) -> list[int]:
    """The standing daily priorities, expressed as jobs rather than as good intentions."""
    specs: Iterable[tuple[str, str, dict[str, Any], int, bool]] = (
        ("harvest", "Charatan: hunt fresh dating evidence", {"brand": "Charatan"}, 1, False),
        ("harvest", "James Upshall: hunt fresh dating evidence", {"brand": "Upshall"}, 1, False),
        ("harvest", "Interview sweep: pipe-house owners, CEOs, famous makers",
         {"collect": "video_urls", "seed": "Ken Barnes / Pipes Magazine Radio Show"}, 2, False),
        ("machine", "Nightly machine check (read-only)",
         {"checks": ["updates.available", "drivers.problem", "disk.free",
                     "restart.pending", "defender.status"]}, 3, False),
        ("transcribe", "Whisper backlog — waits for GPU all-clear", {"source": "interviews"}, 4, True),
    )
    return [
        q.add(kind, title, payload, priority=prio, needs_gpu=gpu)
        for kind, title, payload, prio, gpu in specs
    ]
