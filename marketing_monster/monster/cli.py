"""monster — the command line. Pure stdlib; runs anywhere Python 3.10+ runs.

    python -m monster init pipes
    python -m monster inspect pipes ~/Downloads/ebay_sold.csv     # reads headers only
    python -m monster load    pipes ~/Downloads/ebay_sold.csv
    python -m monster record  pipes sale listing/dunhill-1961 --value 340
    python -m monster report  pipes
    python -m monster pending pipes
    python -m monster verify  pipes
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from .digger import Digger
from .judge import Judge
from .ledger import LedgerError
from .playbook import Playbook
from .report import weekly_report, write_report
from .scale import Scale
from .wall import Cookbook
from .well import Well, dropped_columns, propose_mapping, read_headers

CLONES = ("pipes", "groundtruth", "ashcombe")
TREE = ("well/raw", "well/derived", "digger/digs", "judge", "playbook",
        "maker/out", "scale/reports")


def root_for(base: pathlib.Path, clone: str) -> pathlib.Path:
    return base / "clones" / clone


def cmd_init(args) -> int:
    base = pathlib.Path(args.base)
    root = root_for(base, args.clone)
    for sub in TREE:
        (root / sub).mkdir(parents=True, exist_ok=True)
    Well(root).salt()
    Playbook(root)
    Cookbook(base / "cookbook")
    (base / ".gitignore").write_text(
        "# the Well is private truth — it never leaves the machine\n"
        "clones/*/well/\nclones/*/scale/events.jsonl\nclones/*/maker/out/\n"
        "clones/*/**/.salt\n", encoding="utf-8")
    print(f"clone ready: {root}")
    print("  one root = one wall. Run this process with THIS root only.")
    return 0


def cmd_inspect(args) -> int:
    """Wave 2's first move — reads headers, writes nothing, touches no data."""
    headers = read_headers(args.csv)
    mapping = propose_mapping(headers)
    print(f"{len(headers)} columns found in {args.csv}\n")
    print("proposed mapping:")
    for field, column in mapping.items():
        print(f"  {field:<14} <- {column or '(not found — supply manually)'}")
    dropped = dropped_columns(headers, mapping)
    print(f"\ndropped on the floor ({len(dropped)}): {', '.join(dropped) or 'none'}")
    print("\nnothing was read or written. Save a mapping.json to override.")
    return 0


def cmd_load(args) -> int:
    root = root_for(pathlib.Path(args.base), args.clone)
    mapping = json.loads(pathlib.Path(args.mapping).read_text()) if args.mapping else None
    stats = Well(root).load(args.csv, mapping, append=args.append,
                            channel=args.channel)
    print(f"loaded {stats['added']} new rows from channel '{stats['channel']}' "
          f"({stats['duplicates_skipped']} duplicates skipped)")
    print(f"Well now holds {stats['transactions']} transactions, "
          f"{stats['buyers']} buyers ({stats['repeat_buyers']} repeat)")
    print(f"dropped columns: {', '.join(stats['dropped_columns']) or 'none'}")
    print("no names, no emails, no addresses were written (M4).")
    return 0


def cmd_record(args) -> int:
    root = root_for(pathlib.Path(args.base), args.clone)
    note = args.note
    if args.buyer:
        # hashed on the way in, never stored raw (M4) — this is what makes
        # "who bought twice" answerable going forward
        note = (note + " " if note else "") + f"buyer={Well(root).buyer_key(args.buyer)}"
    row = Scale(root).record(args.event, args.asset_id, surface=args.surface,
                             value=args.value, attribution=args.attribution or None,
                             reason=args.reason, asset_version=args.asset_version,
                             note=note)
    print(f"{row['id']}  {row['event']}  cohort={row['cohort']}  "
          f"attribution={row['attribution']}"
          + ("  buyer=hashed" if args.buyer else ""))
    return 0


def cmd_report(args) -> int:
    root = root_for(pathlib.Path(args.base), args.clone)
    print(weekly_report(root))
    if args.save:
        print(f"\nsaved: {write_report(root)}")
    return 0


def cmd_pending(args) -> int:
    from . import pending
    root = root_for(pathlib.Path(args.base), args.clone)
    path = pending.write(root)
    print(path.read_text(encoding="utf-8"))
    return 0


def cmd_locate(args) -> int:
    from .locate import render

    def progress(dirs, hits):
        print(f"  ...{dirs:,} folders scanned, {hits} candidates so far",
              end="\r", file=sys.stderr, flush=True)

    body = render(args.path, limit=args.limit, quick=args.quick,
                  progress=None if args.quick else progress)
    print(" " * 60, end="\r", file=sys.stderr)
    print(body)
    return 0


def cmd_dig(args) -> int:
    from .dig import Dig
    root = root_for(pathlib.Path(args.base), args.clone)
    dig = Dig(root)
    if args.propose:
        book = Playbook(root)
        added = [book.add_line(line) for line in dig.proposals()]
        kept = [x for x in added if x]
        print(f"playbook: {len(kept)} new PROPOSED line(s), "
              f"{len(added) - len(kept)} already present")
        for line in kept:
            print(f"  + {line.claim}")
        print("  none is CONFIRMED — each needs a second, non-overlapping cohort.\n")
    if args.save:
        path = dig.write()
        print(dig.report())
        print(f"\nsaved: {path}")
    else:
        print(dig.report())
    return 0


def cmd_decide(args) -> int:
    root = root_for(pathlib.Path(args.base), args.clone)
    row = Judge(root).decide(args.proposal, edge=args.edge, verdict=args.verdict,
                             reason=args.reason, needs_farid=args.needs_farid,
                             resupply=args.resupply)
    print(f"{row['decision_id']}  {row['verdict']}  edge={row['edge']}  "
          f"channel={row['channel_flag']}")
    return 0


def cmd_twin(args) -> int:
    """Twin a proven listing onto owned ground first, borrowed second."""
    from .twin import Twin
    root = root_for(pathlib.Path(args.base), args.clone)
    result = Twin(root).build(args.title, args.price, args.sku,
                              decision_id=args.decision, sold_on=args.sold_on,
                              source_channel=args.source,
                              ebay_category=args.ebay_category,
                              ebay_location=args.ebay_location)
    facts = result["facts"]
    named = ", ".join(f"{k}={v}" for k, v in facts.items() if v)
    print(f"twinned {result['sku'] or '(no sku)'}")
    print(f"  read from the title: {named or 'nothing recognised — check the vocabulary'}")
    print(f"  stamped: {result['asset_version']}  decision: {result['decision_id']}")
    print(f"  lessons applied: {len(result['lessons_applied'])}")
    print(f"  written: {result['out_dir']}")
    for name in result["files"]:
        print(f"    - {name}")
    if result["needs_filling"]:
        print(f"  ebay.csv needs your values: {', '.join(result['needs_filling'])}")
    print("  order: faridunhill first, then Etsy, then the eBay CSV upload.")
    return 0


def cmd_publish(args) -> int:
    """THE MOUTH — owned ground first, borrowed second, and the Scale hears it."""
    root = root_for(pathlib.Path(args.base), args.clone)
    order = ["site", "etsy", "ebay"]
    # Farid's admin holds the listing on faridunhill.com and pushes it to Etsy
    # automatically, so those two are one act, not two. "admin" records both.
    targets = order[:2] if args.where == "admin" else [args.where]
    scale = Scale(root)
    done = {r["surface"] for r in scale.rows()
            if r["event"] == "published" and r["asset_id"] == args.sku}
    if "ebay" in targets and "site" not in done | set(targets):
        print("refused: owned ground first — faridunhill before eBay "
              "(Mouth law, v1.0). Record the admin publish first:\n"
              f"  monster publish {args.clone} {args.sku} --where admin",
              file=sys.stderr)
        return 2
    for where in targets:
        row = scale.record("published", args.sku, surface=where,
                           asset_version=args.asset_version or None,
                           attribution="direct",
                           reason=("faridunhill admin, auto-pushed to Etsy"
                                   if args.where == "admin" else
                                   f"published to {where}"))
        print(f"{row['id']}  published  {args.sku} -> {where}")
    remaining = [x for x in order if x not in done | set(targets)]
    print(f"  still to go: {', '.join(remaining) or 'nothing — live everywhere'}")
    return 0


def cmd_daily(args) -> int:
    """The whole day's routine in one command."""
    from . import pending
    from .dig import Dig
    root = root_for(pathlib.Path(args.base), args.clone)
    book = Playbook(root)

    dropped = book.expire_due()
    if dropped:
        print(f"{len(dropped)} playbook line(s) reached their review date and "
              "stopped being read:")
        for line in dropped:
            print(f"  - {line.claim}")

    if args.propose:
        added = [book.add_line(x) for x in Dig(root).proposals()]
        kept = [x for x in added if x]
        print(f"dig proposed {len(kept)} new lesson(s) "
              f"({len(added) - len(kept)} already known)")

    path = pending.write(root)
    body = path.read_text(encoding="utf-8")
    waiting = body.count("→ yes / no") + body.count("→ keep / drop") + body.count("→ number")
    print(f"\n{'=' * 60}\nWAITING FOR YOU: {waiting} item(s) — {path}\n{'=' * 60}")
    if waiting:
        print(body)
    print(weekly_report(root))
    return 0


def cmd_auto(args) -> int:
    """One turn of the whole loop, with no typing. This is the daily job."""
    from .auto import Autopilot
    base = pathlib.Path(args.base)
    pilot = Autopilot(base, args.clone)
    if not pilot.config["watch"]:
        print("No watch folders configured yet. Run:\n"
              f"  python -m monster setup {args.clone}", file=sys.stderr)
        return 2
    r = pilot.run()
    print(f"AUTOPILOT — {args.clone} — {len(pilot.config['watch'])} folder(s) watched")
    print(f"  new export files read : {r['files_ingested']}")
    print(f"  new sales into the Well: {r['rows_added']}")
    span = f"  {r['sales_span'][0]} to {r['sales_span'][1]}" if r.get("sales_span") else ""
    print(f"  sales recorded         : {r['sales_recorded']}{span}")
    if r["sales_recorded"] > 100:
        days = int(pilot.config["record_sales_within_days"])
        print(f"  ** {r['sales_recorded']} sales in {days} days is a lot. If that looks "
              "wrong, the dates may have been misread — send me this screen.")
    print(f"  listings written       : {r['twins_made']}")
    print(f"  lessons proposed       : {r['lessons_proposed']}")
    for bad in r["files_failed"]:
        print(f"  ** could not read {bad['path'].name}: {bad['error']}")
    print(f"\n  report : {r['report']}")
    if r["waiting_for_farid"]:
        print(f"\n  ** {r['waiting_for_farid']} question(s) waiting for you: {r['pending']}")
    else:
        print("\n  nothing needs you today.")
    return 0


def cmd_rebuild(args) -> int:
    from .auto import Autopilot
    pilot = Autopilot(pathlib.Path(args.base), args.clone)
    r = pilot.rebuild(args.reason)
    print(f"archived (not deleted): {r['archived_to']}")
    print(f"  moved: {', '.join(r['archived'])}\n")
    print("rebuilt from source files:")
    print(f"  export files read : {r['files_ingested']}")
    print(f"  sales into the Well: {r['rows_added']}")
    span = f"  {r['sales_span'][0]} to {r['sales_span'][1]}" if r.get("sales_span") else ""
    print(f"  sales recorded     : {r['sales_recorded']}{span}")
    for bad in r["files_failed"]:
        print(f"  skipped {pathlib.Path(bad['path']).name}: {bad['error']}")
    print(f"\n  report: {r['report']}")
    return 0


def cmd_setup(args) -> int:
    """Ask once where the exports land, then never ask again."""
    from .auto import DEFAULT_CONFIG, load_config, write_config
    base = pathlib.Path(args.base)
    config = load_config(base)
    if args.watch:
        config["watch"] = sorted(set(config["watch"]) | set(args.watch))
    if args.ebay_category:
        config["ebay_category"] = args.ebay_category
    if args.ebay_location:
        config["ebay_location"] = args.ebay_location
    path = write_config(base, config)
    print(f"saved: {path}")
    for folder in config["watch"]:
        exists = "ok" if pathlib.Path(folder).expanduser().is_dir() else "** NOT FOUND"
        print(f"  watching {folder}  {exists}")
    if not config["watch"]:
        print("  no folders yet — pass --watch \"C:/Users/you/Downloads\"")
    return 0


def cmd_schedule(args) -> int:
    """Write the daily job, and print the one line that registers it."""
    base = pathlib.Path(args.base).resolve()
    home = pathlib.Path(__file__).resolve().parent.parent
    bat = base / "monster_daily.bat"
    bat.write_text(
        "@echo off\r\n"
        f"set \"PYTHONPATH={home}\"\r\n"
        f"cd /d \"{base}\"\r\n"
        f"python -m monster auto {args.clone} >> \"{base}\\autopilot.log\" 2>&1\r\n",
        encoding="utf-8")
    print(f"wrote: {bat}\n")
    print("Paste this ONCE to make it run every day automatically:\n")
    print(f'  schtasks /create /tn "Marketing Monster" /tr "{bat}" '
          f'/sc daily /st {args.at} /f\n')
    print(f"After that it runs by itself at {args.at}. Its output goes to "
          f"{base}\\autopilot.log")
    print("To stop it:  schtasks /delete /tn \"Marketing Monster\" /f")
    return 0


def cmd_verify(args) -> int:
    base = pathlib.Path(args.base)
    root = root_for(base, args.clone)
    checks = [("scale", Scale(root).log.verify()),
              ("judge", Judge(root).log.verify()),
              ("digger", Digger(root).log.verify()),
              ("wall", Cookbook(base / "cookbook").verify())]
    bad = 0
    for name, (ok, msg) in checks:
        print(f"  {name:<8}{'ok  ' if ok else 'FAIL'}  {msg}")
        bad += 0 if ok else 1
    return 1 if bad else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="monster", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", default=".", help="marketing root (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def clone_arg(sp):
        sp.add_argument("clone", choices=CLONES)
        return sp

    clone_arg(sub.add_parser("init")).set_defaults(fn=cmd_init)

    sp = clone_arg(sub.add_parser("inspect"))
    sp.add_argument("csv")
    sp.set_defaults(fn=cmd_inspect)

    sp = clone_arg(sub.add_parser("load"))
    sp.add_argument("csv")
    sp.add_argument("--mapping")
    sp.add_argument("--append", action="store_true",
                    help="merge into the existing Well instead of replacing it")
    sp.add_argument("--channel", help="ebay / etsy / site (default: from filename)")
    sp.set_defaults(fn=cmd_load)

    sp = clone_arg(sub.add_parser("record"))
    sp.add_argument("event")
    sp.add_argument("asset_id")
    sp.add_argument("--surface", default="site")
    sp.add_argument("--value", type=float)
    sp.add_argument("--attribution", default="")
    sp.add_argument("--reason", default="")
    sp.add_argument("--asset-version", dest="asset_version")
    sp.add_argument("--buyer", default="", help="username — hashed on the way in, never stored raw")
    sp.add_argument("--note", default="")
    sp.set_defaults(fn=cmd_record)

    sp = clone_arg(sub.add_parser("report"))
    sp.add_argument("--save", action="store_true")
    sp.set_defaults(fn=cmd_report)

    sp = sub.add_parser("locate", help="find candidate data files (reads no records)")
    sp.add_argument("path", nargs="?", default="~")
    sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--quick", action="store_true",
                    help="only Desktop/Documents/Downloads/OneDrive, shallow — seconds")
    sp.set_defaults(fn=cmd_locate)

    sp = clone_arg(sub.add_parser("dig"))
    sp.add_argument("--save", action="store_true")
    sp.add_argument("--propose", action="store_true",
                    help="write the dig's candidate lessons into the playbook as PROPOSED")
    sp.set_defaults(fn=cmd_dig)

    sp = clone_arg(sub.add_parser("decide"))
    sp.add_argument("proposal")
    sp.add_argument("--edge", default="expertise")
    sp.add_argument("--verdict", default="DO")
    sp.add_argument("--reason", required=True)
    sp.add_argument("--needs-farid", dest="needs_farid", default="none")
    sp.add_argument("--resupply", default="")
    sp.set_defaults(fn=cmd_decide)

    sp = clone_arg(sub.add_parser("twin", help="twin a sold listing to owned + borrowed ground"))
    sp.add_argument("title")
    sp.add_argument("price", type=float)
    sp.add_argument("--sku", default="")
    sp.add_argument("--decision", required=True)
    sp.add_argument("--sold-on", dest="sold_on", required=True)
    sp.add_argument("--source", default="ebay")
    sp.add_argument("--ebay-category", dest="ebay_category", default="")
    sp.add_argument("--ebay-location", dest="ebay_location", default="")
    sp.set_defaults(fn=cmd_twin)

    sp = clone_arg(sub.add_parser("publish", help="record that an asset went live"))
    sp.add_argument("sku")
    sp.add_argument("--where", required=True,
                    choices=["admin", "site", "etsy", "ebay"],
                    help="admin = faridunhill + its automatic Etsy push, in one step")
    sp.add_argument("--asset-version", dest="asset_version", default="")
    sp.set_defaults(fn=cmd_publish)

    sp = clone_arg(sub.add_parser("daily", help="the whole day's routine"))
    sp.add_argument("--propose", action="store_true", default=True)
    sp.set_defaults(fn=cmd_daily)

    clone_arg(sub.add_parser("auto", help="one full turn of the loop, no typing")
              ).set_defaults(fn=cmd_auto)

    sp = clone_arg(sub.add_parser("rebuild", help="archive and rebuild from source files"))
    sp.add_argument("--reason", required=True)
    sp.set_defaults(fn=cmd_rebuild)

    sp = clone_arg(sub.add_parser("setup", help="tell it once where exports land"))
    sp.add_argument("--watch", action="append", default=[])
    sp.add_argument("--ebay-category", dest="ebay_category", default="")
    sp.add_argument("--ebay-location", dest="ebay_location", default="")
    sp.set_defaults(fn=cmd_setup)

    sp = clone_arg(sub.add_parser("schedule", help="make it run every day by itself"))
    sp.add_argument("--at", default="08:00")
    sp.set_defaults(fn=cmd_schedule)

    clone_arg(sub.add_parser("pending")).set_defaults(fn=cmd_pending)
    clone_arg(sub.add_parser("verify")).set_defaults(fn=cmd_verify)

    args = p.parse_args(argv)
    try:
        return args.fn(args)
    except LedgerError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
