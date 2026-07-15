"""Batch runner — one command turns a folder of pipes into marketing.

    python -m marketing "C:\\FaridunhillPipes" --out "C:\\FaridunhillPipes\\_marketing" --year 2026

For every `<root>/<pipe>/` folder it: reads the photos + optional notes,
seeds brand/model from the folder name, runs intake → QA gate → listing →
Instagram/TikTok posts → 9:16 reel storyboard, and writes the results
under `--out/<pipe>/`. A top-level INDEX.md lists every pipe, its gate
outcome, and what still needs a human. Nothing is invented — missing facts
are reported as gaps.

Optional per-pipe notes file (`pipe.txt`, `pipe.yaml`, `notes.txt`) —
simple `key: value` lines, all optional:

    brand: Dunhill
    model: Cumberland 41031 Billiard Sandblast
    country: GB
    price: 425
    floor: 360
    currency: USD
    era: 1980-1990 hallmark        # min-max basis; basis decides assert vs hedge
    condition: very_good           # mint/excellent/very_good/good/fair/project
    flaws: rim_darkening, stem_oxidation
    stamping: DUNHILL CUMBERLAND 41031 MADE IN ENGLAND
    why: A Cumberland sandblast with its original sterling band.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from .expression.listing import generate_listing
from .expression.social import generate_reel, generate_social
from .folder_source import FolderItemAssets, parse_folder_name
from .genome.gate import evaluate
from .genome.intake import IntakeInput, ingest
from .genome.schema import ProductGenome
from .genome.store import BirthRecordExists, GenomeStore
from .genome.vocab import ConditionGrade, EraBasis, FlawCode, ProductType

_NOTES_FILES = ("pipe.yaml", "pipe.yml", "pipe.txt", "notes.txt", "notes.md", "info.txt")
_STAMP_FILES = {"stamp.txt", "stamping.txt", "nomenclature.txt", "marks.txt"}

_GRADE_WORDS = {
    "mint": "mint", "excellent": "excellent", "very good": "very_good",
    "good": "good", "fair": "fair", "project": "project",
}
_PRICE_RE = re.compile(r"[$£€]\s?(\d+(?:\.\d{1,2})?)")
_PRICE_KW_RE = re.compile(r"\bprice\b[:\s]*[$£€]?\s?(\d+(?:\.\d{1,2})?)", re.I)


def _find_notes_file(folder: Path) -> Optional[Path]:
    # 1) a conventional name; 2) else a <foldername>.txt; 3) else any .txt
    #    that is not a stamping file.
    for name in _NOTES_FILES:
        f = folder / name
        if f.is_file():
            return f
    named = folder / f"{folder.name}.txt"
    if named.is_file():
        return named
    for f in sorted(folder.glob("*.txt")):
        if f.name.lower() not in _STAMP_FILES:
            return f
    return None


def _read_notes(folder: Path) -> dict[str, str]:
    f = _find_notes_file(folder)
    if f is None:
        return {}
    raw = f.read_text(encoding="utf-8", errors="ignore")
    kv = _parse_kv(raw)
    kv["_raw"] = raw            # keep the whole text for free-form extraction
    return kv


def _extract_price(raw: str) -> Optional[float]:
    m = _PRICE_KW_RE.search(raw) or _PRICE_RE.search(raw)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def _extract_grade(raw: str) -> Optional[str]:
    low = raw.lower()
    found = {v for k, v in _GRADE_WORDS.items() if k in low}
    # only trust an unambiguous single grade (e.g. skip "fair/good")
    return next(iter(found)) if len(found) == 1 else None


def _condition_notes(kv: dict[str, str], raw: str) -> Optional[str]:
    """Prefer an explicit 'condition:' line's text; else the whole note
    (so a human's real description always reaches the listing)."""
    val = kv.get("condition")
    if val and _extract_grade(val) is None and len(val) > 3:
        return val.strip()
    text = raw.strip()
    return text or None


def _parse_kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip().lower()] = val.strip()
    return out


def _era_from_notes(val: str) -> Optional[dict[str, Any]]:
    """'1980-1990 hallmark' -> {min_year, max_year, basis}."""
    parts = val.replace("–", "-").split()
    if not parts:
        return None
    years = parts[0]
    basis = parts[1].lower() if len(parts) > 1 else "style"
    try:
        basis_enum = EraBasis(basis)
    except ValueError:
        basis_enum = EraBasis.STYLE
    if "-" in years:
        lo, _, hi = years.partition("-")
    else:
        lo = hi = years
    try:
        return {"min_year": int(lo), "max_year": int(hi), "basis": basis_enum}
    except ValueError:
        return None


def build_input(folder: Path) -> IntakeInput:
    """Assemble an IntakeInput from a pipe folder (notes override name)."""
    sku = folder.name
    notes = _read_notes(folder)
    brand, model = parse_folder_name(sku)
    brand = notes.get("brand", brand)
    model = notes.get("model", model)

    human_facts: dict[str, Any] = {}
    if brand:
        human_facts["brand"] = brand
    if model:
        human_facts["model_line"] = model
    if notes.get("country"):
        human_facts["country_of_origin"] = notes["country"][:2].upper()
    raw = notes.get("_raw", "")
    # condition grade: a clean 'condition: good' wins; else an unambiguous
    # grade word found anywhere in the note; else left as a gap.
    grade_val = (notes.get("condition") or "").strip().lower()
    grade = None
    try:
        grade = ConditionGrade(grade_val)
    except ValueError:
        picked = _extract_grade(raw)
        if picked:
            grade = ConditionGrade(picked)
    if grade is not None:
        human_facts["unique_physical.condition_grade"] = grade
    # the human's real description always reaches the listing
    cnotes = _condition_notes(notes, raw)
    if cnotes:
        human_facts["unique_physical.condition_notes"] = cnotes
    if notes.get("era"):
        era = _era_from_notes(notes["era"])
        if era:
            human_facts["unique_physical.era"] = era
    if notes.get("flaws"):
        flaws = []
        for token in notes["flaws"].replace(";", ",").split(","):
            token = token.strip().lower()
            try:
                flaws.append(FlawCode(token))
            except ValueError:
                pass
        if flaws:
            human_facts["unique_physical.flaws"] = flaws

    economics: dict[str, Any] = {}
    price = None
    if notes.get("price"):
        try:
            price = float(notes["price"].lstrip("$£€ "))
        except ValueError:
            price = None
    if price is None:
        price = _extract_price(raw)
    if price is not None:
        economics["list_price"] = price
    if notes.get("floor"):
        try:
            economics["floor_price"] = float(notes["floor"].lstrip("$£€"))
        except ValueError:
            pass
    economics["currency"] = notes.get("currency", "USD").upper()[:3]

    return IntakeInput(
        sku=sku,
        product_type=ProductType.UNIQUE_PHYSICAL,
        why_special=notes.get("why") or notes.get("why_special"),
        taxonomy=notes.get("taxonomy"),
        economics=economics or None,
        human_facts=human_facts,
    )


def _load_prices(root: Path) -> list[tuple[str, float]]:
    """Optional `<root>/prices.txt` (or .csv): lines of `substring: price`.
    A folder gets the price of the FIRST substring its name contains — so
    short unique keys ('dunhill', '90s', '246') survive the long, typo-y
    folder names without exact matching."""
    for name in ("prices.txt", "prices.csv"):
        f = root / name
        if not f.is_file():
            continue
        rows: list[tuple[str, float]] = []
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            sep = ":" if ":" in line else ("," if "," in line else None)
            if not sep:
                continue
            key, _, val = line.partition(sep)
            try:
                rows.append((key.strip().lower(), float(val.strip().lstrip("$£€ "))))
            except ValueError:
                continue
        return rows
    return []


def _match_price(folder_name: str, prices: list[tuple[str, float]]) -> Optional[float]:
    low = folder_name.lower()
    for sub, price in prices:
        if sub in low:
            return price
    return None


def run_batch(root: str | Path, out: str | Path, *, reference_year: Optional[int] = None) -> dict[str, Any]:
    source = FolderItemAssets(root)
    prices = _load_prices(Path(root))
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    # The folders are the source of truth for this tool: every run rebuilds
    # from what is on disk NOW. Birth records are insert-only within a run,
    # but a fresh run starts from a clean db so newly added photos/notes are
    # always reflected (a stale record would silently keep old data).
    db_path = out_dir / "genome.db"
    if db_path.exists():
        db_path.unlink()
    store = GenomeStore(db_path)

    index_rows: list[dict[str, Any]] = []
    for folder in source.folders():
        sku = folder.name
        intake = build_input(folder)
        # fill the price from prices.txt if the folder/notes did not carry one
        if not (intake.economics and intake.economics.get("list_price")):
            matched = _match_price(sku, prices)
            if matched is not None:
                econ = dict(intake.economics or {})
                econ["list_price"] = matched
                econ.setdefault("currency", "USD")
                intake.economics = econ
        try:
            result = ingest(intake, source, store)
        except BirthRecordExists:
            # already ingested in a previous run — read it back, regenerate outputs
            result = None
        genome = ProductGenome(**store.get_effective(sku))
        decision = evaluate(genome)  # default ~5% audit sampler for real runs
        listing = generate_listing(genome, decision, reference_year=reference_year)
        ig = generate_social(genome, decision, channel="instagram")
        tt = generate_social(genome, decision, channel="tiktok")
        reel = generate_reel(genome, decision)

        pdir = out_dir / sku
        pdir.mkdir(exist_ok=True)
        (pdir / "listing.md").write_text(_listing_md(listing), encoding="utf-8")
        (pdir / "post-instagram.txt").write_text(_post_txt(ig), encoding="utf-8")
        (pdir / "post-tiktok.txt").write_text(_post_txt(tt), encoding="utf-8")
        (pdir / "reel.json").write_text(json.dumps(_reel_dict(reel), indent=2), encoding="utf-8")

        index_rows.append({
            "sku": sku,
            "title": listing.title,
            "gate": decision.outcome.value,
            "lists": decision.lists,
            "photos": len(genome.media),
            "gaps": listing.gaps,
        })

    (out_dir / "INDEX.md").write_text(_index_md(index_rows), encoding="utf-8")
    (out_dir / "report.json").write_text(json.dumps(index_rows, indent=2), encoding="utf-8")
    return {"count": len(index_rows), "out": str(out_dir), "rows": index_rows}


# --- output formatting -----------------------------------------------------

def _listing_md(l) -> str:
    parts = [f"# {l.title}", "", l.description, "", f"**Tags:** {', '.join(l.tags)}"]
    if l.image_order:
        parts += ["", "**Images (in order):**"] + [f"- {u} — {l.alt_texts.get(u,'')}" for u in l.image_order]
    if l.hedged:
        parts += ["", f"**Hedged (needs your verify):** {', '.join(l.hedged)}"]
    if l.gaps:
        parts += ["", f"**Gaps to fill:** {'; '.join(l.gaps)}"]
    return "\n".join(parts) + "\n"


def _post_txt(p) -> str:
    body = p.caption
    if p.hashtags:
        body += "\n\n" + " ".join("#" + h for h in p.hashtags)
    if p.eligibility_note:
        body += f"\n\n[note: {p.eligibility_note}]"
    if p.gaps:
        body += f"\n[gaps: {'; '.join(p.gaps)}]"
    return body + "\n"


def _reel_dict(r) -> dict[str, Any]:
    return {
        "sku": r.sku, "orientation": r.orientation, "duration_s": r.duration_s,
        "pacing": r.pacing, "notes": r.notes,
        "shots": [asdict(s) for s in r.shots],
    }


def _index_md(rows: list[dict[str, Any]]) -> str:
    lines = ["# Faridunhill — batch marketing output", "",
             f"{len(rows)} pipes processed. Each has: listing.md, post-instagram.txt, "
             "post-tiktok.txt, reel.json.", "",
             "| Pipe | Gate | Lists | Photos | Gaps |", "|---|---|---|---|---|"]
    for r in rows:
        gaps = ", ".join(r["gaps"]) or "—"
        lines.append(f"| {r['sku']} | {r['gate']} | {'yes' if r['lists'] else 'HOLD'} | {r['photos']} | {gaps} |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="marketing", description="Batch-generate marketing from a folder of pipes.")
    ap.add_argument("root", help=r'folder of pipe subfolders, e.g. "C:\FaridunhillPipes"')
    ap.add_argument("--out", default=None, help="output folder (default: <root>/_marketing)")
    ap.add_argument("--year", type=int, default=None, help="reference year for vintage/antique keywords")
    args = ap.parse_args(argv)
    out = args.out or str(Path(args.root) / "_marketing")
    report = run_batch(args.root, out, reference_year=args.year)
    print(f"Processed {report['count']} pipes -> {report['out']}")
    print(f"Open {Path(report['out']) / 'INDEX.md'} for the summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
