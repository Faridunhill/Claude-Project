"""`desk` — the command line Farid actually types.

    desk check                 read-only sweep of the PC, no model, no network
    desk run "..."             one Manager run against an instruction
    desk brief                 the standing daily run (harvest + machine + report)
    desk queue [--state ...]   look at the job queue
    desk seed                  put the standing daily work on the queue
    desk approve <action>      mint a single-use approval token for one ACTION
    desk laws [--relock]       verify (or re-accept) the immutable laws
    desk review [--limit N]    read what the Manager has taught itself, newest first
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import machine
from .agent import Context, run as run_agent
from .approvals import ApprovalBook
from .channel import Channel
from .harness import Harness
from .ideas import IdeaLedger
from .laws import LawsTampered, load as load_laws, relock
from .queue import JobQueue, seed_standing_work

ROOT = Path(__file__).resolve().parent.parent

DAILY = (
    "Do the standing daily run. In order: read the channel inbox; take the queue "
    "scoreboard; run the read-only machine checks and report anything that needs Farid's "
    "attention; look at what is queued for Charatan, Upshall and the interview harvest and "
    "make sure each has a concrete next step on the queue; reinforce or propose ideas based "
    "on what you actually saw today; write down anything you learned; then leave one note "
    "in the channel that leads with the scoreboard."
)


def load_config(root: Path) -> dict[str, Any]:
    path = root / "config.json"
    if not path.exists():
        path = root / "config.example.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_context(root: Path) -> Context:
    cfg = load_config(root)
    state_dir = root / cfg.get("state_dir", "state")
    return Context(
        laws=load_laws(root),
        harness=Harness.load(state_dir),
        queue=JobQueue(state_dir / "jobs.db"),
        ideas=IdeaLedger(state_dir),
        channel=Channel(Path(cfg["channel_dir"]).expanduser()),
        approvals=ApprovalBook.load(state_dir),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="desk", description="The Encyclopedia Manager.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="Read-only PC sweep. No model, no network.")
    p_run = sub.add_parser("run", help="One Manager run.")
    p_run.add_argument("instruction")
    sub.add_parser("brief", help="The standing daily run.")
    p_q = sub.add_parser("queue", help="Show the job queue.")
    p_q.add_argument("--state")
    sub.add_parser("seed", help="Put the standing daily work on the queue.")
    p_a = sub.add_parser("approve", help="Mint one approval token for one ACTION.")
    p_a.add_argument("action")
    p_a.add_argument("--minutes", type=int, default=60)
    p_l = sub.add_parser("laws", help="Verify the immutable laws.")
    p_l.add_argument("--relock", action="store_true")
    p_r = sub.add_parser("review", help="What the Manager has taught itself.")
    p_r.add_argument("--limit", type=int, default=20)

    args = parser.parse_args(argv)

    if args.cmd == "laws":
        if args.relock:
            print(f"laws.md accepted: {relock(ROOT)}")
            return 0
        try:
            print(f"laws.md verified: {load_laws(ROOT).digest}")
            return 0
        except LawsTampered as exc:
            print(f"LAWS TAMPERED\n{exc}", file=sys.stderr)
            return 2

    if args.cmd == "check":
        # Deliberately model-free: this must work when the API is down or the key is gone.
        for cmd in machine.catalogue():
            if cmd["tier"] != "check":
                continue
            result = machine.run(cmd["name"])
            status = "ok" if result.get("ok") else ("n/a" if result.get("unavailable") else "FAIL")
            print(f"[{status:4}] {cmd['name']:22} {cmd['summary']}")
            if result.get("data") is not None:
                print(json.dumps(result["data"], indent=2, default=str)[:1500])
        return 0

    try:
        ctx = build_context(ROOT)
    except LawsTampered as exc:
        print(f"Refusing to start.\n{exc}", file=sys.stderr)
        return 2

    if args.cmd == "queue":
        for job in ctx.queue.list(args.state):
            gpu = " [gpu]" if job["needs_gpu"] else ""
            print(f"{job['id']:>4} {job['state']:8} p{job['priority']} {job['kind']:11} {job['title']}{gpu}")
        print(f"\n{ctx.queue.scoreboard()}")
        return 0

    if args.cmd == "seed":
        ids = seed_standing_work(ctx.queue)
        print(f"seeded jobs: {ids}")
        return 0

    if args.cmd == "approve":
        if args.action not in machine.REGISTRY:
            print(f"No such command {args.action!r}.", file=sys.stderr)
            return 1
        cmd = machine.REGISTRY[args.action]
        if cmd.tier != "action":
            print(f"{args.action!r} is a read-only check — it needs no approval.")
            return 0
        token = ctx.approvals.issue(args.action, args.minutes)
        print(f"Approved: {cmd.summary}\nToken (single use, {args.minutes} min): {token}")
        return 0

    if args.cmd == "review":
        for entry in ctx.harness.recall()[: args.limit]:
            print(f"[{entry.kind}] {entry.title}\n    {entry.body}\n    evidence: {entry.evidence}\n")
        print(f"Full append-only log: {ctx.harness.log_path}")
        return 0

    # --- the two commands that need the model ---
    try:
        from anthropic import Anthropic
    except ImportError:
        print("pip install anthropic", file=sys.stderr)
        return 1

    client = Anthropic()
    instruction = DAILY if args.cmd == "brief" else args.instruction
    print(run_agent(client, ctx, instruction))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
