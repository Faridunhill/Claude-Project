"""`monster locate` — answer "where does the data live?" in one command.

The cloud side cannot see Farid's PC. Rather than a conversation about paths,
this walks a folder, finds every file that could plausibly be a Well (or a
hub, or a cabinet), and prints a table small enough to paste back.

It reads FILE NAMES, SIZES, and — for delimited text only — the single header
row. It never reads a record, and it writes nothing. Safe to run on anything.
"""
from __future__ import annotations

import csv
import pathlib
from datetime import datetime

DATA_SUFFIXES = {".csv", ".tsv", ".txt", ".json", ".jsonl", ".ndjson",
                 ".xlsx", ".xls", ".xlsm", ".db", ".sqlite", ".sqlite3",
                 ".mdb", ".accdb", ".parquet"}
TEXT_SUFFIXES = {".csv", ".tsv", ".txt"}
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".next", "venv", ".venv",
             "site-packages", "AppData", "Windows", "Program Files",
             "Program Files (x86)", "$RECYCLE.BIN", ".cache"}

# words that suggest this file is what we are looking for
INTEREST = {
    "sold": 6, "order": 5, "transaction": 5, "sale": 5, "ebay": 5,
    "cabinet": 6, "hub": 4, "export": 3, "listing": 4, "inventory": 3,
    "buyer": 3, "customer": 3, "groundtruth": 6, "ground_truth": 6,
    "parcel": 4, "property": 3, "pipe": 3, "catalog": 2, "catalogue": 2,
}


def score(path: pathlib.Path) -> int:
    name = path.name.lower()
    points = sum(w for word, w in INTEREST.items() if word in name)
    points += sum(w for word, w in INTEREST.items() if word in str(path.parent).lower()) // 2
    if path.suffix.lower() in (".csv", ".xlsx", ".jsonl"):
        points += 2
    try:
        size = path.stat().st_size
    except OSError:
        return points
    if size > 5_000_000:
        points += 3
    elif size > 100_000:
        points += 2
    elif size < 200:
        points -= 2
    return points


def header_of(path: pathlib.Path) -> str:
    """First line only, truncated. Never touches record two."""
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return ""
    try:
        with path.open(encoding="utf-8-sig", newline="", errors="replace") as fh:
            row = next(csv.reader(fh), [])
    except (OSError, StopIteration):
        return ""
    joined = ", ".join(c.strip() for c in row[:14] if c.strip())
    return (joined[:150] + "…") if len(joined) > 150 else joined


def human(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


def scan(base: str | pathlib.Path, *, limit: int = 25, max_depth: int = 6) -> list[dict]:
    base = pathlib.Path(base).expanduser()
    found = []
    base_depth = len(base.parts)
    for path in base.rglob("*"):
        try:
            if len(path.parts) - base_depth > max_depth:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if not path.is_file() or path.suffix.lower() not in DATA_SUFFIXES:
                continue
            stat = path.stat()
        except OSError:
            continue
        found.append({
            "path": path, "size": stat.st_size, "score": score(path),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
        })
    found.sort(key=lambda f: (-f["score"], -f["size"]))
    for item in found[:limit]:
        item["header"] = header_of(item["path"])
    return found[:limit]


def render(base: str | pathlib.Path, limit: int = 25) -> str:
    hits = scan(base, limit=limit)
    if not hits:
        return (f"No data-shaped files found under {base}.\n"
                "Try a different folder — Desktop, Documents, or wherever the\n"
                "eBay export and the cabinets were last saved.")
    lines = [f"CANDIDATE DATA FILES under {pathlib.Path(base).expanduser()}",
             "(names, sizes and header rows only — no records were read)", ""]
    for i, h in enumerate(hits, 1):
        lines.append(f"{i:>2}. {h['path']}")
        lines.append(f"    {human(h['size']):>8}  modified {h['modified']}  "
                     f"relevance {h['score']}")
        if h.get("header"):
            lines.append(f"    columns: {h['header']}")
        lines.append("")
    lines.append("Paste this back, or run:  python -m monster inspect pipes \"<path>\"")
    return "\n".join(lines)
