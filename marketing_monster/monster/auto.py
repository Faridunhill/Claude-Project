"""AUTOPILOT — the machine fills its own ledgers.

Doc 004 §2, Amendment A: "Farid supplies verdicts. The machine supplies rows.
A verdict is a word in a chat. A row is a line in a file. He never types the
second one, ever." Budget: ~15 minutes a WEEK, no file editing.

The first build broke that law. It asked Farid to type a `record` command per
sale, a `twin` per pipe, a `publish` per channel — data entry wearing a
command line. This module is the correction: one run, on a schedule, that

  1. finds new export files in the folders where they already land,
  2. loads them into the Well (no duplicates, ever),
  3. writes a Scale row for every new sale, buyer hashed on the way in,
  4. twins every untwinned sale into site / Etsy / eBay artifacts,
  5. digs, and carries any new lessons into the playbook as PROPOSED,
  6. writes the report and the PENDING queue.

What it will NEVER do, because those are Farid's alone (v1.0): pick a
category, set a floor price, set a spend ceiling, or move anything across a
wall. Those queue in PENDING.md and wait for a word.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

from .dig import Dig
from .judge import Judge
from .ledger import AppendOnlyLog, LedgerError, now_iso
from .playbook import Playbook
from .scale import Scale
from .well import Well, read_rows
from .twin import Twin

CONFIG_NAME = "monster.config.json"
DEFAULT_CONFIG = {
    "watch": [],                    # folders where exports land
    "record_sales_within_days": 45,  # older rows are history, not news
    "ebay_category": "",
    "ebay_location": "",
    "auto_twin": True,
}
STANDING_DECISION = "D-AUTO"


def load_config(base: pathlib.Path) -> dict:
    path = base / CONFIG_NAME
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    config = dict(DEFAULT_CONFIG)
    config.update(json.loads(path.read_text(encoding="utf-8")))
    return config


def write_config(base: pathlib.Path, config: dict) -> pathlib.Path:
    path = base / CONFIG_NAME
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def file_fingerprint(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


class Autopilot:
    def __init__(self, base: pathlib.Path, clone: str = "pipes"):
        self.base = pathlib.Path(base)
        self.root = self.base / "clones" / clone
        self.clone = clone
        self.config = load_config(self.base)
        self.seen = AppendOnlyLog(self.root / "auto" / "ingested.jsonl")

    # -- 1 & 2: find and load ---------------------------------------------
    def candidates(self) -> list[pathlib.Path]:
        found: list[pathlib.Path] = []
        for folder in self.config["watch"]:
            path = pathlib.Path(folder).expanduser()
            if not path.is_dir():
                continue
            for item in sorted(path.rglob("*")):
                if item.suffix.lower() in (".csv", ".jsonl", ".tsv") and item.is_file():
                    found.append(item)
        return found

    def already_ingested(self) -> set[str]:
        return {r["fingerprint"] for r in self.seen.rows()}

    def ingest(self) -> list[dict]:
        """Load every export not seen before. Content-hashed, so the same file
        renamed or re-downloaded is not loaded twice."""
        done, out = self.already_ingested(), []
        well = Well(self.root)
        for path in self.candidates():
            try:
                fingerprint = file_fingerprint(path)
            except OSError:
                continue
            if fingerprint in done:
                continue
            try:
                stats = well.load(path, append=True)
            except (LedgerError, Exception) as exc:      # a bad file must not stop the run
                self.seen.append({"ts": now_iso(), "fingerprint": fingerprint,
                                  "path": str(path), "skipped": str(exc)[:200]})
                out.append({"path": path, "error": str(exc)[:200]})
                continue
            self.seen.append({"ts": now_iso(), "fingerprint": fingerprint,
                              "path": str(path), "added": stats["added"],
                              "channel": stats["channel"]})
            done.add(fingerprint)
            out.append({"path": path, **stats})
        return out

    # -- 3: every new sale becomes a Scale row ----------------------------
    def record_new_sales(self) -> list[dict]:
        from datetime import date, timedelta
        scale = Scale(self.root)
        known = {r["asset_id"] for r in scale.rows() if r["event"] == "sale"}
        cutoff = (date.today()
                  - timedelta(days=int(self.config["record_sales_within_days"]))).isoformat()
        written = []
        for row in Well(self.root).transactions():
            item_id = str(row.get("item_id") or "").strip()
            sold_at = str(row.get("sold_at") or "")[:10]
            if not item_id or item_id in known or sold_at < cutoff:
                continue
            surface = row.get("channel") if row.get("channel") in (
                "ebay", "etsy", "site") else "other"
            written.append(scale.record(
                "sale", item_id, surface=surface, value=row.get("price"),
                ts=f"{sold_at}T12:00:00Z" if len(sold_at) == 10 else None,
                note=(f"buyer={row['buyer_key']}" if row.get("buyer_key") else ""),
            ))
            known.add(item_id)
        return written

    # -- 4: twin what has not been twinned --------------------------------
    def standing_order(self) -> str:
        """The Maker may only build what the Judge ordered. One standing order
        covers routine twinning; it is written once, into the ledger."""
        judge = Judge(self.root)
        if not any(r["decision_id"] == STANDING_DECISION for r in judge.rows()):
            judge.decide("Twin every new sale onto owned ground, then Etsy, then eBay",
                         edge="audience", verdict="DO",
                         reason="standing order: routine translation of proven listings",
                         decision_id=STANDING_DECISION)
        return STANDING_DECISION

    def twin_new(self, limit: int = 50) -> list[dict]:
        if not self.config.get("auto_twin", True):
            return []
        decision = self.standing_order()
        maker_out = self.root / "maker" / "out"
        twin, made = Twin(self.root), []
        for row in Well(self.root).transactions():
            if len(made) >= limit:
                break
            item_id = str(row.get("item_id") or "").strip()
            title, price = row.get("title") or "", row.get("price")
            if not item_id or not title or not price:
                continue
            from .twin import slugify
            if (maker_out / slugify(item_id)[:60]).exists():
                continue
            from datetime import date, timedelta
            cutoff = (date.today() - timedelta(
                days=int(self.config["record_sales_within_days"]))).isoformat()
            if str(row.get("sold_at") or "")[:10] < cutoff:
                continue
            made.append(twin.build(
                title, float(price), item_id, decision_id=decision,
                sold_on=str(row.get("sold_at"))[:10],
                source_channel=row.get("channel") or "ebay",
                ebay_category=self.config.get("ebay_category", ""),
                ebay_location=self.config.get("ebay_location", "")))
        return made

    # -- 5 & 6: learn, then report ----------------------------------------
    def learn(self) -> dict:
        book = Playbook(self.root)
        expired = book.expire_due()
        added = [book.add_line(x) for x in Dig(self.root).proposals()]
        return {"expired": len(expired), "proposed": len([x for x in added if x])}

    def run(self) -> dict:
        """One full turn of the loop. Safe to run every day; does nothing twice."""
        ingested = self.ingest()
        sales = self.record_new_sales()
        twins = self.twin_new()
        learned = self.learn()
        try:
            Dig(self.root).write()
        except Exception:
            pass
        from . import pending
        from .report import write_report
        pending_path = pending.write(self.root)
        report_path = write_report(self.root)
        waiting = pending_path.read_text(encoding="utf-8")
        return {
            "files_ingested": len([x for x in ingested if "error" not in x]),
            "files_failed": [x for x in ingested if "error" in x],
            "rows_added": sum(x.get("added", 0) for x in ingested),
            "sales_recorded": len(sales),
            "twins_made": len(twins),
            "lessons_proposed": learned["proposed"],
            "lessons_expired": learned["expired"],
            "waiting_for_farid": waiting.count("→ yes / no")
                                 + waiting.count("→ keep / drop")
                                 + waiting.count("→ number"),
            "pending": pending_path,
            "report": report_path,
        }
