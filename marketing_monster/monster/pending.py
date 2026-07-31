"""PENDING.md — reserved powers without paperwork.

Doc 004 §2.2: the machine drafts every row complete, including its own
recommendation, and holds it pending. Farid answers with a word in chat. The
machine writes the verdict into the ledger. He never types into a file.

This file is generated and overwritten every cycle. Editing it does nothing.
"""
from __future__ import annotations

import pathlib

from .judge import Judge
from .playbook import Playbook
from .report import ledger_health
from .wall import admission_test

HEADER = """# PENDING — {clone}
*Machine-generated {stamp}. Overwritten each cycle; editing this file does nothing.
Answer in chat — the machine writes the rows.*

"""


def render(clone_root: str | pathlib.Path, cookbook_candidates: list[str] | None = None) -> str:
    root = pathlib.Path(clone_root)
    judge, book = Judge(root), Playbook(root)
    from .ledger import now_iso

    out = [HEADER.format(clone=root.name.upper(), stamp=now_iso())]
    n = 0

    for item in judge.open_items():
        n += 1
        out.append(
            f"**{item['decision_id']}**  `{item['needs_farid']}`\n"
            f"> {item['proposal']}\n"
            f"> edge: {item['edge']} · channel: {item['channel_flag']}"
            + (f" · effort: {item['effort_hrs']}h" if item.get("effort_hrs") else "")
            + f"\n> {item['reason']}\n>\n> **→ yes / no**\n"
        )

    for claim in (cookbook_candidates or []):
        n += 1
        a = admission_test(claim)
        marks = " ".join(f"{k}{'ok' if v else 'X'}" for k, v in a["results"].items())
        out.append(
            f"**W-{n:03d}**  `wall`\n"
            f"> A lesson wants to cross into the shared cookbook:\n"
            f"> *\"{claim}\"*\n"
            f"> admission test: {marks} → {'passes' if a['passes'] else 'FAILS'}"
            + (f"\n> flagged: {a['hits']}" if a["hits"] else "")
            + f"\n> machine recommends: {a['recommend']}\n>\n> **→ yes / no**\n"
        )

    due = [x for x in book.lines() if x.status == "CONFIRMED" and x.is_expired()]
    for line in due:
        n += 1
        out.append(
            f"**R-{n:03d}**  `playbook review`\n"
            f"> *\"{line.claim}\"* reaches its review date ({line.review}).\n"
            f"> evidence: n={line.n}, effect={line.effect}\n"
            f"> machine recommends: re-confirm if the Scale still shows it, else drop.\n>\n"
            f"> **→ keep / drop**\n"
        )

    if n == 0:
        out.append("*Nothing needs Farid this cycle.*\n")

    silent = [h["organ"] for h in ledger_health(root) if h["silent"]]
    if silent:
        out.append(f"\n---\n**Not a decision, a warning:** {', '.join(silent)} "
                   "has stopped writing rows.\n")
    return "\n".join(out)


def write(clone_root: str | pathlib.Path, cookbook_candidates: list[str] | None = None):
    root = pathlib.Path(clone_root)
    path = root / "PENDING.md"
    path.write_text(render(root, cookbook_candidates), encoding="utf-8")
    return path
