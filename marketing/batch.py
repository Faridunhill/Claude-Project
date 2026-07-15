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


def _read_notes(folder: Path) -> dict[str, str]:
    for name in _NOTES_FILES:
        f = folder / name
        if f.is_file():
            return _parse_kv(f.read_text(encoding="utf-8", errors="ignore"))
    return {}


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
    if notes.get("condition"):
        try:
            human_facts["unique_physical.condition_grade"] = ConditionGrade(notes["condition"].lower())
        except ValueError:
            pass
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
    if notes.get("price"):
        try:
            economics["list_price"] = float(notes["price"].lstrip("$£€"))
        except ValueError:
            pass
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


def run_batch(root: str | Path, out: str | Path, *, reference_year: Optional[int] = None) -> dict[str, Any]:
    source = FolderItemAssets(root)
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    store = GenomeStore(out_dir / "genome.db")

    index_rows: list[dict[str, Any]] = []
    for folder in source.folders():
        sku = folder.name
        intake = build_input(folder)
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
