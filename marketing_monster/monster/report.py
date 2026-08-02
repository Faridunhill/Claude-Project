"""The weekly report — and the ledger health block that makes silence visible.

Doc 004 §2.3: an organ that stops writing rows gets flagged in the same breath
as a bad number. A system that reports its own decay cannot lie by omission,
because the omission is the report.

The two numbers this file exists to print, however bad they look:
  · the unattributable share of outcomes (B1)
  · rows written per ledger, and days since the last one (§2.3)
"""
from __future__ import annotations

import pathlib
from datetime import date, datetime, timedelta, timezone

from .ledger import AppendOnlyLog, cohort_of, now_iso
from .playbook import Playbook
from .scale import Scale

SILENT_DAYS = 14  # two cycles

LEDGERS = {
    "events.jsonl": "scale/events.jsonl",
    "decisions.jsonl": "judge/decisions.jsonl",
    "sources.jsonl": "digger/sources.jsonl",
}
ORGAN = {"events.jsonl": "SCALE", "decisions.jsonl": "JUDGE", "sources.jsonl": "DIGGER"}
LABEL = {"sources.jsonl": "digger"}


def _age_days(ts: str) -> float:
    then = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - then).total_seconds() / 86400


def _dig_activity(root: pathlib.Path) -> list[dict]:
    """A written dig is Digger activity. Judging the organ only by
    sources.jsonl — which records OUTSIDE sources — declared it dead while it
    was reading the Well and proposing lessons. A warning that cries wolf
    teaches people to ignore warnings, which is worse than no warning."""
    from datetime import datetime, timezone
    out = []
    for path in (root / "digger" / "digs").glob("*.md"):
        try:
            stamp = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        except OSError:
            continue
        out.append({"ts": stamp.isoformat().replace("+00:00", "Z")})
    return out


def ledger_health(clone_root: str | pathlib.Path) -> list[dict]:
    root = pathlib.Path(clone_root)
    out = []
    for name, rel in LEDGERS.items():
        rows = AppendOnlyLog(root / rel).rows()
        if name == "sources.jsonl":
            rows = sorted(rows + _dig_activity(root), key=lambda r: r["ts"])
        week = sum(1 for r in rows if r.get("ts") and _age_days(r["ts"]) <= 7)
        prev = sum(1 for r in rows if r.get("ts") and 7 < _age_days(r["ts"]) <= 14)
        quiet = _age_days(rows[-1]["ts"]) if rows and rows[-1].get("ts") else None
        # An organ that never ran has not "stopped" — say which it is.
        state = ("not_started" if quiet is None
                 else "silent" if quiet > SILENT_DAYS else "ok")
        out.append({"ledger": name, "organ": ORGAN[name], "this_week": week,
                    "prev_week": prev, "days_quiet": quiet, "state": state,
                    "silent": state != "ok", "total": len(rows)})
    return out


def weekly_report(clone_root: str | pathlib.Path, today: date | None = None) -> str:
    root = pathlib.Path(clone_root)
    today = today or date.today()
    scale, book = Scale(root), Playbook(root)
    health = ledger_health(root)

    week = cohort_of(now_iso())
    lines = [f"LEDGER HEALTH — week {week}"]
    for h in health:
        flag = {"ok": "  ok",
                "not_started": f"  ** {h['organ']} NOT STARTED (no rows yet)",
                "silent": f"  ** {h['organ']} SILENT ({(h['days_quiet'] or 0):.0f}d quiet)",
                }[h["state"]]
        lines.append(f"  {LABEL.get(h['ledger'], h['ledger']):<18}{h['this_week']:>5} rows this week   "
                     f"(prev {h['prev_week']}){flag}")

    pb = book.lines()
    due = [x for x in pb if x.status == "CONFIRMED" and x.is_expired(today)]
    lines.append(
        f"  {'playbook':<18}{sum(1 for x in pb if x.status == 'PROPOSED')} proposed, "
        f"{sum(1 for x in pb if x.status == 'CONFIRMED')} confirmed, "
        f"{len(due)} due for review")

    unattr, total = scale.unattributable_share()
    share = f"{(unattr / total * 100):.0f}%" if total else "n/a"
    lines.append(f"  {'unattributable':<18}{share} of outcomes ({unattr}/{total})")

    # the honest headline: decay outranks performance
    dying = [h["organ"] for h in health if h["silent"]]
    lines += ["", "HEADLINE"]
    if dying:
        verb = "is" if len(dying) == 1 else "are"
        lines.append(f"  ** {' and '.join(dying)} {verb} not writing rows. "
                     "Fix that before reading anything below.")
    else:
        recent = [r for r in scale.rows() if r.get("ts") and _age_days(r["ts"]) <= 7]
        sales = [r for r in recent if r["event"] == "sale"]
        value = sum(r["value"] or 0 for r in sales)
        lines.append(f"  {len(sales)} sales, {value:,.2f} recorded.")
        by_surface: dict[str, list] = {}
        for row in sales:
            by_surface.setdefault(row["surface"], []).append(row["value"] or 0)
        for surface, values in sorted(by_surface.items(), key=lambda kv: -len(kv[1])):
            lines.append(f"    {surface:<8}{len(values):>4} sales  "
                         f"{sum(values):>10,.2f}  avg {sum(values)/len(values):,.0f}")
        if sales:
            lines.append("  Does that match what you actually sold this week? If not, "
                         "the dates in one export are being read wrong — say so.")
        if total and unattr / total > 0.5:
            lines.append(f"  {share} of outcomes have no known cause. That is expected on "
                         "organic-only ground; it is not a measurement.")

    if due:
        lines += ["", "DUE FOR REVIEW (drop to PROPOSED if not re-confirmed)"]
        lines += [f"  - {x.claim}  (review {x.review})" for x in due]

    ok, msg = scale.log.verify()
    lines += ["", f"INTEGRITY  {'ok' if ok else '** BROKEN **'} — {msg}"]
    return "\n".join(lines)


def write_report(clone_root: str | pathlib.Path) -> pathlib.Path:
    root = pathlib.Path(clone_root)
    body = weekly_report(root)
    out = root / "scale" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{cohort_of(now_iso())}.txt"
    path.write_text(body + "\n", encoding="utf-8")
    return path
