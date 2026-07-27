"""Publishing tiers, frequency walls, placements log (SOCIAL-ENGINE-001).

Tier 1 — full-auto: business page + IG via official Meta APIs only.
Tier 2 — one-tap packages: personal profile + groups. The machine
PREPARES (video + caption ready on the phone); a HUMAN taps post.
No automation ever touches personal profiles or groups — Meta ToS,
no violations, ever.

Standing walls enforced here (control.yaml, via marketing/policy.py):
  * max_posts_per_group_per_day — the frequency wall, checked in code
  * any Meta account warning -> channel pause + one email, no silent
    retries (the pause flag is persisted; publishing refuses while set)
  * NO PAID PROMOTION (POLICY-META-ADS-001) — Meta prohibits paid ads
    for smoking paraphernalia. `request_boost()` is the single choke
    point and refuses by design. Everything here is organic.

Placements log: every published asset records (channel, url, ts) —
the takedown/remediation index (addendum V2 consumer).
"""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..policy import Walls, load_walls

_SQL = """
CREATE TABLE IF NOT EXISTS placements (
    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku          TEXT NOT NULL,
    asset_path   TEXT NOT NULL,
    channel      TEXT NOT NULL,
    target       TEXT NOT NULL,           -- page|ig|profile|group:<name>
    url          TEXT,
    license_source TEXT,
    ts           TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_place_target ON placements (target, ts);
CREATE TABLE IF NOT EXISTS ready_packages (
    package_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    sku          TEXT NOT NULL,
    target       TEXT NOT NULL,
    video_path   TEXT NOT NULL,
    caption      TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'ready',   -- ready|posted|discarded
    created_ts   TEXT NOT NULL,
    posted_ts    TEXT
);
CREATE TABLE IF NOT EXISTS channel_state (
    channel      TEXT PRIMARY KEY,
    paused       INTEGER NOT NULL DEFAULT 0,
    reason       TEXT,
    updated_ts   TEXT
);
"""


class ChannelPaused(Exception):
    pass


class FrequencyWall(Exception):
    pass


@dataclass(frozen=True)
class PostRequest:
    sku: str
    target: str                # "page" | "ig" | "group:<name>" | "profile"
    video_path: str
    caption: str
    license_source: str = "meta_sound_collection"


class Tier1Publisher(ABC):
    """Official-API publisher (page + IG). Credentials live in env vars
    on the machine that runs it — never in the repo, never shared across
    businesses (firewall)."""

    @abstractmethod
    def post(self, request: PostRequest) -> str:
        """Publish; return the post URL."""


class DryRunPublisher(Tier1Publisher):
    """Default until Meta credentials are configured on the PC. Records
    what WOULD be posted; never touches the network."""

    def __init__(self) -> None:
        self.posted: list[PostRequest] = []

    def post(self, request: PostRequest) -> str:
        self.posted.append(request)
        return f"dryrun://{request.target}/{request.sku}"


class SocialEngine:
    def __init__(
        self,
        db_path: str | Path,
        publisher: Tier1Publisher,
        max_posts_per_group_per_day: Optional[int] = None,
        walls: Optional[Walls] = None,
    ):
        self._conn = sqlite3.connect(str(db_path))
        self._conn.executescript(_SQL)
        self._conn.commit()
        self._publisher = publisher
        self._walls = walls or load_walls()
        # Explicit argument wins; otherwise the wall comes from control.yaml.
        self._group_wall = (
            max_posts_per_group_per_day
            if max_posts_per_group_per_day is not None
            else self._walls.max_posts_per_group_per_day
        )

    # -- walls ---------------------------------------------------------

    def request_boost(self, sku: str, target: str, budget: float) -> None:
        """THE choke point for paid Meta promotion (POLICY-META-ADS-001).

        Every paid path — boosting a post, running an ad set, paying for
        reach — must call this first. While the wall stands it always
        raises `PaidPromotionProhibited`, so a future automation cannot
        spend here by accident: it gets a loud, documented refusal.

        Meta prohibits paid advertising for smoking paraphernalia; a
        boost risks the ad account and the Page. Organic posting via
        `publish_tier1` / `queue_tier2` is the supported route.
        """
        self._walls.assert_meta_paid_promotion_allowed()

    def _check_pause(self, channel: str) -> None:
        row = self._conn.execute(
            "SELECT paused, reason FROM channel_state WHERE channel=?", (channel,)
        ).fetchone()
        if row and row[0]:
            raise ChannelPaused(f"{channel} paused: {row[1]} (needs Farid; no silent retries)")

    def pause_channel(self, channel: str, reason: str) -> dict:
        """Meta warning protocol: pause + ONE email. Returns the email
        payload for the mailer; publishing refuses until Farid unpauses."""
        self._conn.execute(
            "INSERT INTO channel_state (channel, paused, reason, updated_ts) VALUES (?,1,?,?) "
            "ON CONFLICT(channel) DO UPDATE SET paused=1, reason=excluded.reason, "
            "updated_ts=excluded.updated_ts",
            (channel, reason, datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()
        return {
            "to": "farid",
            "subject": f"[FARID OS] {channel} PAUSED",
            "body": f"Channel {channel} paused automatically: {reason}. "
                    "No retries will occur until you unpause.",
        }

    def unpause_channel(self, channel: str) -> None:
        self._conn.execute(
            "UPDATE channel_state SET paused=0, reason=NULL, updated_ts=? WHERE channel=?",
            (datetime.now(timezone.utc).isoformat(), channel),
        )
        self._conn.commit()

    def _check_group_wall(self, target: str, now: datetime) -> None:
        if not target.startswith("group:"):
            return
        day = now.date().isoformat()
        count = self._conn.execute(
            "SELECT COUNT(*) FROM placements WHERE target=? AND substr(ts,1,10)=?",
            (target, day),
        ).fetchone()[0]
        if count >= self._group_wall:
            raise FrequencyWall(
                f"{target} already has {count} post(s) today (wall: {self._group_wall})"
            )

    # -- tier 1: full-auto (page + IG only) -----------------------------

    def publish_tier1(self, request: PostRequest, now: Optional[datetime] = None) -> str:
        if request.target not in ("page", "ig"):
            raise ValueError(
                "Tier 1 automation is page/ig ONLY - profiles and groups are "
                "Tier 2 (human one-tap). This is a ToS wall, not a preference."
            )
        now = now or datetime.now(timezone.utc)
        self._check_pause("meta")
        url = self._publisher.post(request)
        self._log_placement(request, url, now)
        return url

    # -- tier 2: one-tap packages (human posts) --------------------------

    def queue_tier2(self, request: PostRequest, now: Optional[datetime] = None) -> int:
        """Prepare a ready-package for the phone. Machine prepares,
        human posts — the wall is checked at queue time too, so the
        phone never even sees an over-frequency package."""
        now = now or datetime.now(timezone.utc)
        self._check_pause("meta")
        self._check_group_wall(request.target, now)
        cur = self._conn.execute(
            "INSERT INTO ready_packages (sku, target, video_path, caption, created_ts) "
            "VALUES (?,?,?,?,?)",
            (request.sku, request.target, request.video_path, request.caption,
             now.isoformat()),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def mark_posted(self, package_id: int, url: str, now: Optional[datetime] = None) -> None:
        """Called after the human taps post (the phone flow reports back)."""
        now = now or datetime.now(timezone.utc)
        row = self._conn.execute(
            "SELECT sku, target, video_path FROM ready_packages WHERE package_id=? AND status='ready'",
            (package_id,),
        ).fetchone()
        if row is None:
            raise KeyError(package_id)
        sku, target, video_path = row
        self._check_group_wall(target, now)
        self._conn.execute(
            "UPDATE ready_packages SET status='posted', posted_ts=? WHERE package_id=?",
            (now.isoformat(), package_id),
        )
        self._log_placement(
            PostRequest(sku=sku, target=target, video_path=video_path, caption=""),
            url, now,
        )

    def ready_packages(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT package_id, sku, target, video_path, caption FROM ready_packages "
            "WHERE status='ready' ORDER BY created_ts"
        ).fetchall()
        return [
            {"package_id": r[0], "sku": r[1], "target": r[2],
             "video_path": r[3], "caption": r[4]}
            for r in rows
        ]

    # -- placements index ------------------------------------------------

    def _log_placement(self, request: PostRequest, url: str, now: datetime) -> None:
        self._conn.execute(
            "INSERT INTO placements (sku, asset_path, channel, target, url, license_source, ts) "
            "VALUES (?,?,?,?,?,?,?)",
            (request.sku, request.video_path, "meta", request.target, url,
             request.license_source, now.isoformat()),
        )
        self._conn.commit()

    def placements_for(self, sku: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT channel, target, url, license_source, ts FROM placements WHERE sku=? ORDER BY ts",
            (sku,),
        ).fetchall()
        return [
            {"channel": r[0], "target": r[1], "url": r[2],
             "license_source": r[3], "ts": r[4]}
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()
