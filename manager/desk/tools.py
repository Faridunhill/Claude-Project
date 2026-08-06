"""The Manager's tool surface.

Every tool is narrow on purpose. There is no "run this PowerShell" tool and no "write this
file" tool — the model picks names and passes typed arguments, and this module does the
rest. That is what makes the machine-safety law enforceable rather than aspirational.

Descriptions are prescriptive about *when* to call, not just what the tool does — recent
Opus models reach for tools conservatively, and a trigger condition in the description is
what gets the call rate right.
"""

from __future__ import annotations

import json
from typing import Any

from . import machine
from .harness import LawGuardRejection

SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "machine_catalogue",
        "description": (
            "List every PowerShell command you are allowed to run, with its tier. Call "
            "this first whenever a task involves the PC's health, updates, drivers, disk, "
            "or memory — you cannot run anything that is not on this list, so guessing "
            "wastes a turn."
        ),
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "machine_check",
        "description": (
            "Run one read-only CHECK command and return its output as data. Safe to call "
            "unattended. Call this whenever you need a fact about the machine's current "
            "state — never assume, never report a value you did not read."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Command name from machine_catalogue (tier=check)."}},
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "machine_action",
        "description": (
            "Run a command that CHANGES the machine. Requires an approval token Farid "
            "issued for this exact action with `desk approve <name>`. Call this only when "
            "he has given you a token; without one it fails and that failure is correct. "
            "Never ask the user to paste a token you invented."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Command name from machine_catalogue (tier=action)."},
                "approval_token": {"type": "string", "description": "The token Farid issued for this action."},
            },
            "required": ["name", "approval_token"],
            "additionalProperties": False,
        },
    },
    {
        "name": "queue_scoreboard",
        "description": (
            "Counts of jobs by state. Call this at the start of every run — it is the "
            "scoreboard you lead your report with."
        ),
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "queue_list",
        "description": "List jobs, optionally filtered by state (queued/claimed/done/failed/blocked).",
        "input_schema": {
            "type": "object",
            "properties": {
                "state": {"type": "string", "enum": ["queued", "claimed", "done", "failed", "blocked"]},
                "limit": {"type": "integer"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "queue_add",
        "description": (
            "Give an order to the local agents by putting a job on the queue. Use this "
            "instead of describing work you intend to do later — a job on the queue "
            "survives the end of this session, a sentence in your reply does not. Set "
            "needs_gpu for whisper/transcription work; it will wait for Farid's all-clear."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "description": "e.g. harvest, dating, machine, transcribe, publish"},
                "title": {"type": "string"},
                "payload": {"type": "object", "description": "Anything the worker needs."},
                "priority": {"type": "integer", "description": "1 = highest, 9 = lowest. Default 5."},
                "needs_gpu": {"type": "boolean"},
            },
            "required": ["kind", "title"],
            "additionalProperties": False,
        },
    },
    {
        "name": "queue_finish",
        "description": (
            "Close a job as done or failed, with a result string. Only call this when you "
            "have evidence the work actually happened — a tool result, a file, an output. "
            "Marking a job done that you did not verify is the one failure mode the laws "
            "single out."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "integer"},
                "ok": {"type": "boolean"},
                "result": {"type": "string"},
            },
            "required": ["job_id", "ok", "result"],
            "additionalProperties": False,
        },
    },
    {
        "name": "idea_propose",
        "description": (
            "Put a new idea on the ledger. Use this whenever you think of something worth "
            "keeping — a new angle for the encyclopedia, a workflow fix, a research lead. "
            "Ideas are cheap; losing them between sessions is what costs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}, "note": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    },
    {
        "name": "idea_reinforce",
        "description": (
            "Attach new evidence to an existing idea, raising its strength. Call this when "
            "something you observed this session supports an idea already on the ledger — "
            "that accumulation is how a hunch becomes a plan. Evidence is required; "
            "restating the idea is not reinforcement."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "idea_id": {"type": "string"},
                "evidence": {"type": "string", "description": "What you actually observed, and where."},
            },
            "required": ["idea_id", "evidence"],
            "additionalProperties": False,
        },
    },
    {
        "name": "idea_list",
        "description": "The idea ledger, strongest first. Call this before brainstorming so you build on the ledger instead of repeating it.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "learn",
        "description": (
            "Write an evidence-backed entry to your refinable memory — a lesson, a skill, "
            "or a spec for a local agent. This is how you improve across sessions. Call it "
            "when something worked, something failed, or you found a repeatable procedure. "
            "Entries that try to weaken a law are rejected by the law-guard."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["lesson", "skill", "agent_spec"]},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "evidence": {"type": "string", "description": "What in this session proves it."},
            },
            "required": ["kind", "title", "body", "evidence"],
            "additionalProperties": False,
        },
    },
    {
        "name": "unlearn",
        "description": "Delete a memory entry that turned out to be wrong, with the reason. A wrong lesson is worse than no lesson.",
        "input_schema": {
            "type": "object",
            "properties": {"entry_id": {"type": "string"}, "reason": {"type": "string"}},
            "required": ["entry_id", "reason"],
            "additionalProperties": False,
        },
    },
    {
        "name": "channel_inbox",
        "description": "Read what Farid left in channel/TO_AGENT and NEW_UPLOADS. Call this at the start of any run — he may have answered a question you are blocked on.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "channel_note",
        "description": (
            "Leave a numbered note for Farid in channel/TO_FARID. Use it for anything he "
            "must decide (launches, domain, museum brands, subscriptions), any approval you "
            "need, and your end-of-run report. Lead with the outcome."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"title": {"type": "string"}, "body": {"type": "string", "description": "Markdown."}},
            "required": ["title", "body"],
            "additionalProperties": False,
        },
    },
]


def dispatch(name: str, args: dict[str, Any], ctx: Any) -> str:
    """Execute one tool call. Returns a string for the tool_result block.

    Errors are returned as text rather than raised: the model should see a refusal and
    adapt, not crash the run. `machine_action` without approval lands here as a plain
    'refused' message — which is the system working, not failing.
    """
    try:
        if name == "machine_catalogue":
            return _j(machine.catalogue())

        if name == "machine_check":
            cmd = machine.REGISTRY.get(args["name"])
            if cmd is None:
                return f"No such command {args['name']!r}."
            if cmd.tier != "check":
                return (
                    f"{cmd.name!r} is an ACTION, not a check. Use machine_action, which "
                    "needs an approval token from Farid."
                )
            return _j(machine.run(cmd.name, approvals=ctx.approvals))

        if name == "machine_action":
            try:
                return _j(machine.run(
                    args["name"],
                    approval=args.get("approval_token"),
                    approvals=ctx.approvals,
                ))
            except machine.NotApproved as exc:
                return f"REFUSED: {exc}"

        if name == "queue_scoreboard":
            return _j(ctx.queue.scoreboard())

        if name == "queue_list":
            return _j(ctx.queue.list(args.get("state"), int(args.get("limit", 50))))

        if name == "queue_add":
            job_id = ctx.queue.add(
                args["kind"], args["title"], args.get("payload") or {},
                priority=int(args.get("priority", 5)),
                needs_gpu=bool(args.get("needs_gpu", False)),
            )
            return f"queued job {job_id}: {args['title']}"

        if name == "queue_finish":
            ctx.queue.finish(int(args["job_id"]), ok=bool(args["ok"]), result=args["result"])
            return f"job {args['job_id']} closed as {'done' if args['ok'] else 'failed'}"

        if name == "idea_propose":
            idea = ctx.ideas.propose(args["text"], args.get("note", ""))
            return f"idea {idea.id!r} on the ledger (strength {idea.strength})"

        if name == "idea_reinforce":
            idea = ctx.ideas.reinforce(args["idea_id"], args["evidence"])
            return f"idea {idea.id!r} reinforced — strength now {idea.strength}, status {idea.status}"

        if name == "idea_list":
            return ctx.ideas.brief()

        if name == "learn":
            entry = ctx.harness.write(
                args["kind"], args["title"], args["body"], args["evidence"],
            )
            return f"learned {entry.id!r}"

        if name == "unlearn":
            ok = ctx.harness.retract(args["entry_id"], args["reason"])
            return f"retracted {args['entry_id']!r}" if ok else f"no entry {args['entry_id']!r}"

        if name == "channel_inbox":
            if not ctx.channel.available():
                return "Channel not found on this machine — check the path in config.json."
            return _j(ctx.channel.inbox())

        if name == "channel_note":
            path = ctx.channel.write_note(args["title"], args["body"])
            return f"note written: {path}"

        return f"Unknown tool {name!r}."

    except LawGuardRejection as exc:
        return f"REFUSED BY LAW-GUARD: {exc}"
    except (KeyError, ValueError, TypeError) as exc:
        return f"ERROR in {name}: {exc}"


def _j(obj: Any) -> str:
    return json.dumps(obj, indent=2, default=str)[:20000]
