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
from .digger import Digger
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
    "repo": "",                     # the bridge — pulled before every run
    "dossier_folder": "",           # where the cloud drops its research
    "git_pull": True,
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


def parse_dossier_header(path: pathlib.Path) -> dict:
    """Dossiers carry a small machine-readable block the reader never sees:

        <!-- monster
        category: pipe and cigar lighters
        edge: audience
        recommend: DO
        -->
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return {}
    if "<!-- monster" not in text:
        return {}
    block = text.split("<!-- monster", 1)[1].split("-->", 1)[0]
    out = {}
    for line in block.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            out[key.strip().lower()] = value.strip()
    return out


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
                from .well import (looks_like_active_listings,
                                   looks_like_an_upload_file, read_headers)
                headers = read_headers(path)
                if looks_like_an_upload_file(headers):
                    raise LedgerError(
                        "this is an eBay upload file — it creates listings, it does "
                        "not record sales. Nothing to learn from it")
                marker = looks_like_active_listings(headers)
                if marker:
                    raise LedgerError(
                        f"looks like an active-listings report (column {marker!r}) — "
                        "unsold stock is not a sale and will not be loaded as one")
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
        # Days that look like a bulk LISTING upload, not a day of selling.
        # The Well keeps them for inspection; the Scale must not learn from
        # them, because the Scale is what teaches the playbook.
        try:
            quarantined = {s["day"] for s in Dig(self.root).suspicious_days()
                           if s["consecutive"]}
        except Exception:
            quarantined = set()
        known = {r["asset_id"] for r in scale.rows() if r["event"] == "sale"}
        cutoff = (date.today()
                  - timedelta(days=int(self.config["record_sales_within_days"]))).isoformat()
        written = []
        for row in Well(self.root).transactions():
            item_id = str(row.get("item_id") or "").strip()
            sold_at = str(row.get("sold_at") or "")[:10]
            if not item_id or item_id in known:
                continue
            if not sold_at or sold_at < cutoff or sold_at in quarantined:
                continue
            surface = row.get("channel") if row.get("channel") in (
                "ebay", "etsy", "site") else "other"
            from .well import iso_date
            stamped = iso_date(sold_at)
            written.append(scale.record(
                "sale", item_id, surface=surface, value=row.get("price"),
                ts=f"{stamped}T12:00:00Z" if stamped else None,
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
        try:
            quarantined = {s["day"] for s in Dig(self.root).suspicious_days()
                           if s["consecutive"]}
        except Exception:
            quarantined = set()
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
            sold_at = str(row.get("sold_at") or "")[:10]
            if sold_at < cutoff or sold_at in quarantined:
                continue
            made.append(twin.build(
                title, float(price), item_id, decision_id=decision,
                sold_on=str(row.get("sold_at"))[:10],
                source_channel=row.get("channel") or "ebay",
                ebay_category=self.config.get("ebay_category", ""),
                ebay_location=self.config.get("ebay_location", "")))
        return made

    # -- recovery ---------------------------------------------------------
    def rebuild(self, reason: str) -> dict:
        """Start the Well and the Scale again from the source files.

        Nothing is deleted. The ledgers are append-only by law, and a bug in
        the loader does not earn the right to erase history — it earns an
        archive with a written reason, so the bad run stays inspectable.
        """
        import shutil
        if not reason.strip():
            raise LedgerError("a rebuild must state why — it is a correction, "
                              "and corrections carry reasons")
        stamp = now_iso().replace(":", "").replace("-", "")
        archive = self.root / "archive" / stamp
        archive.mkdir(parents=True, exist_ok=True)
        moved = []
        for rel in ("well/derived", "scale/events.jsonl", "auto/ingested.jsonl",
                    "maker/out"):
            source = self.root / rel
            if source.exists():
                target = archive / rel.replace("/", "_")
                shutil.move(str(source), str(target))
                moved.append(rel)
        (archive / "WHY.txt").write_text(
            f"archived {now_iso()}\nreason: {reason}\nmoved: {', '.join(moved)}\n"
            "Nothing here was deleted. This is the state before the rebuild.\n",
            encoding="utf-8")
        (self.root / "well" / "derived").mkdir(parents=True, exist_ok=True)
        result = self.run()
        result["archived_to"] = archive
        result["archived"] = moved
        return result

    # -- 5 & 6: learn, then report ----------------------------------------
    def learn(self) -> dict:
        book = Playbook(self.root)
        expired = book.expire_due()
        added = [book.add_line(x) for x in Dig(self.root).proposals()]
        return {"expired": len(expired), "proposed": len([x for x in added if x])}

    # -- 0: cross the bridge ----------------------------------------------
    def pull(self) -> dict:
        """Bring down whatever the cloud half wrote since yesterday.

        This is the line that makes the two halves one system. Without it a
        human carries files between them, and a system that needs a courier is
        not automatic.
        """
        import subprocess
        repo = self.config.get("repo") or ""
        if not repo or not self.config.get("git_pull", True):
            return {"pulled": False, "why": "no repo configured"}
        path = pathlib.Path(repo).expanduser()
        if not (path / ".git").is_dir():
            return {"pulled": False, "why": f"{path} is not a git checkout"}
        try:
            done = subprocess.run(
                ["git", "-C", str(path), "pull", "--ff-only"],
                capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError) as exc:
            # the network is not a reason to skip the day's work
            return {"pulled": False, "why": str(exc)[:120]}
        message = (done.stdout or done.stderr).strip().splitlines()
        return {"pulled": done.returncode == 0,
                "why": message[-1] if message else "", "repo": str(path)}

    # -- 0b: research the cloud sent down ---------------------------------
    def read_dossiers(self) -> list[dict]:
        """A new dossier queues its own category decision.

        The dossier carries a machine-readable header written by the cloud
        side. Farid still decides — the row lands in PENDING.md as a question,
        because v1.0 reserves category picks for him.
        """
        folder = self.config.get("dossier_folder") or ""
        if not folder:
            return []
        path = pathlib.Path(folder).expanduser()
        if not path.is_dir():
            return []
        digger, judge = Digger(self.root), Judge(self.root)
        done = {r.get("url") for r in digger.log.rows()}
        out = []
        for item in sorted(path.glob("*.md")):
            if str(item) in done:
                continue
            header = parse_dossier_header(item)
            if not header.get("category"):
                continue          # not a dossier, just a note
            try:
                out.append(digger.take_dossier(
                    item, category=header["category"],
                    edge=header.get("edge", "audience"),
                    recommend=header.get("recommend", "DO"), judge=judge))
            except LedgerError:
                continue
        return out

    def run(self) -> dict:
        """One full turn of the loop. Safe to run every day; does nothing twice."""
        pulled = self.pull()
        self.config = load_config(self.base)     # a pull may have changed it
        dossiers = self.read_dossiers()
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
        stamps = sorted(r["ts"][:10] for r in sales if r.get("ts"))
        try:
            spikes = [s for s in Dig(self.root).suspicious_days() if s["consecutive"]]
        except Exception:
            spikes = []
        return {
            "pulled": pulled,
            "dossiers": dossiers,
            "quarantined_days": spikes,
            "sales_span": (stamps[0], stamps[-1]) if stamps else None,
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
