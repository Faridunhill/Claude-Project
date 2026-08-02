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
                              source_channel=args.source)
    facts = result["facts"]
    named = ", ".join(f"{k}={v}" for k, v in facts.items() if v)
    print(f"twinned {result['sku'] or '(no sku)'}")
    print(f"  read from the title: {named or 'nothing recognised — check the vocabulary'}")
    print(f"  stamped: {result['asset_version']}  decision: {result['decision_id']}")
    print(f"  lessons applied: {len(result['lessons_applied'])}")
    print(f"  written: {result['out_dir']}")
    for name in result["files"]:
        print(f"    - {name}")
    print("  owned ground first: publish site.md before the Etsy copy (Mouth law).")
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
    sp.set_defaults(fn=cmd_twin)

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
