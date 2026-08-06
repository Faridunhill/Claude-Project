"""The Manager loop.

A manual tool-use loop against the Messages API rather than the SDK's tool runner. Two
reasons, both about this specific job: the runner is beta and this is unattended software
on Farid's own machine, and owning the loop keeps the approval gate in one readable place
where an auditor can see it.

Model policy (see the migration notes for Claude Opus 5):
  * thinking is ON by default — we do not pass a `thinking` field, and `max_tokens` has to
    leave room for it alongside the answer.
  * no temperature / top_p — removed on this model, they return 400.
  * effort is the intelligence/cost dial; `high` for a manager that plans and delegates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import tools
from .approvals import ApprovalBook
from .channel import Channel
from .harness import Harness
from .ideas import IdeaLedger
from .laws import Laws
from .queue import JobQueue

MODEL = "claude-opus-5"
MAX_TOKENS = 16000
EFFORT = "high"
MAX_TURNS = 40


@dataclass
class Context:
    laws: Laws
    harness: Harness
    queue: JobQueue
    ideas: IdeaLedger
    channel: Channel
    approvals: ApprovalBook


def build_system(ctx: Context) -> list[dict[str, Any]]:
    """Immutable laws first, refinable memory second, volatile state last.

    That order is also the caching order: the laws block is byte-stable across every run,
    so it stays cached while the harness and scoreboard churn beneath it.
    """
    return [
        {
            "type": "text",
            "text": ctx.laws.system_preamble(),
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": (
                f"{ctx.harness.system_section()}\n\n"
                f"<ideas>\n{ctx.ideas.brief()}\n</ideas>\n\n"
                f"<queue>\n{ctx.queue.scoreboard()}\n</queue>\n\n"
                "<working_style>\n"
                "You are running as a manager, not a chat assistant. A run ends with work "
                "done: jobs queued or closed, checks read, lessons written, a note left for "
                "Farid. Lead your final message with the scoreboard, then what changed, then "
                "anything you need from him. Do not end a turn on a promise — if your last "
                "paragraph is a plan, do the work now with tool calls instead.\n"
                "</working_style>"
            ),
        },
    ]


def run(client: Any, ctx: Context, instruction: str, *, max_turns: int = MAX_TURNS) -> str:
    """Drive one Manager run to completion. Returns the final assistant text."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": instruction}]
    system = build_system(ctx)
    final_text = ""

    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            tools=tools.SCHEMAS,
            output_config={"effort": EFFORT},
            messages=messages,
        )

        # Claude Opus 5 can decline a request outright; content is empty or partial.
        if response.stop_reason == "refusal":
            detail = getattr(response, "stop_details", None)
            category = getattr(detail, "category", None) if detail else None
            return f"[refused by safety classifiers{f' ({category})' if category else ''}]"

        text_now = "".join(b.text for b in response.content if b.type == "text")
        if text_now:
            final_text = text_now

        if response.stop_reason != "tool_use":
            return final_text

        messages.append({"role": "assistant", "content": response.content})

        # All results for one turn go back in a single user message — splitting them
        # teaches the model to stop making parallel calls.
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            out = tools.dispatch(block.name, dict(block.input), ctx)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": out,
                "is_error": out.startswith(("ERROR", "REFUSED")),
            })
        messages.append({"role": "user", "content": results})

    return final_text + f"\n\n[stopped after {max_turns} turns — run again to continue]"
