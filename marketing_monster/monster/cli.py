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
from .well import Well, dropped_columns, propose_mapping

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
    import csv
    with open(args.csv, encoding="utf-8-sig", newline="") as fh:
        headers = next(csv.reader(fh))
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
    stats = Well(root).load_csv(args.csv, mapping)
    print(f"loaded {stats['transactions']} transactions, {stats['buyers']} buyers "
          f"({stats['repeat_buyers']} repeat)")
    print(f"dropped columns: {', '.join(stats['dropped_columns']) or 'none'}")
    print("no names, no emails, no addresses were written (M4).")
    return 0


def cmd_record(args) -> int:
    root = root_for(pathlib.Path(args.base), args.clone)
    row = Scale(root).record(args.event, args.asset_id, surface=args.surface,
                             value=args.value, attribution=args.attribution or None,
                             reason=args.reason, asset_version=args.asset_version)
    print(f"{row['id']}  {row['event']}  cohort={row['cohort']}  "
          f"attribution={row['attribution']}")
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
    sp.set_defaults(fn=cmd_load)

    sp = clone_arg(sub.add_parser("record"))
    sp.add_argument("event")
    sp.add_argument("asset_id")
    sp.add_argument("--surface", default="site")
    sp.add_argument("--value", type=float)
    sp.add_argument("--attribution", default="")
    sp.add_argument("--reason", default="")
    sp.add_argument("--asset-version", dest="asset_version")
    sp.set_defaults(fn=cmd_record)

    sp = clone_arg(sub.add_parser("report"))
    sp.add_argument("--save", action="store_true")
    sp.set_defaults(fn=cmd_report)

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
