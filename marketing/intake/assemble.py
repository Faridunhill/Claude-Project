"""Intake assembler — folder + transcript + two numbers -> birth record.

Orchestrates: scan_photos -> get_transcript -> structure -> ProductGenome
-> GenomeStore.write_birth. Idempotent: SKUs that already have a birth
record are skipped (immutability), so the nightly run can sweep the same
intake root forever.

CLI:
    python -m marketing.intake <intake_root> --db marketing/genome.db
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..genome.schema import Economics, FieldProvenance, ProductGenome, UniquePhysicalExtension, completeness_score
from ..genome.store import BirthRecordExists, GenomeStore
from ..genome.vocab import FieldSource, ProductType
from .conventions import NUMBERS_COLUMNS
from .photos import scan_photos
from .structure import KeywordStructurer, TranscriptStructurer
from .transcribe import Transcriber, get_transcript


@dataclass
class ItemResult:
    sku: str
    status: str                      # "created" | "skipped-exists" | "error"
    completeness: float = 0.0
    checklist_report: str = ""
    transcript_source: str = ""
    detail: str = ""


@dataclass
class IntakeReport:
    results: list[ItemResult] = field(default_factory=list)

    def summary(self) -> str:
        created = sum(1 for r in self.results if r.status == "created")
        skipped = sum(1 for r in self.results if r.status == "skipped-exists")
        errors = [r for r in self.results if r.status == "error"]
        pending = sum(1 for r in self.results if r.transcript_source == "pending")
        lines = [
            f"intake: {created} created, {skipped} already existed, "
            f"{len(errors)} errors, {pending} transcripts pending"
        ]
        for r in self.results:
            if r.status == "created":
                lines.append(f"  {r.sku}: completeness {r.completeness:.0%}")
                for cl in r.checklist_report.splitlines():
                    if "gap" in cl:
                        lines.append(f"    {cl}")
        for r in errors:
            lines.append(f"  {r.sku}: ERROR {r.detail}")
        return "\n".join(lines)


def load_numbers(intake_root: Path) -> dict[str, dict[str, float]]:
    """numbers.csv: sku,cost_basis,floor_price[,list_price]."""
    path = intake_root / "numbers.csv"
    out: dict[str, dict[str, float]] = {}
    if not path.exists():
        return out
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            sku = (row.get("sku") or "").strip()
            if not sku:
                continue
            vals: dict[str, float] = {}
            for col in NUMBERS_COLUMNS[1:]:
                raw = (row.get(col) or "").strip()
                if raw:
                    try:
                        vals[col] = float(raw)
                    except ValueError:
                        pass  # bad cell reported via completeness, not a crash
            out[sku] = vals
    return out


def assemble_item(
    item_dir: Path,
    numbers: dict[str, float],
    structurer: TranscriptStructurer,
    transcriber: Optional[Transcriber] = None,
) -> tuple[ProductGenome, str, str]:
    """Build a birth record from one SKU folder. Returns
    (genome, checklist_report, transcript_source)."""
    sku = item_dir.name
    scan = scan_photos(item_dir)
    tr = get_transcript(item_dir, transcriber)

    provenance: dict[str, FieldProvenance] = {
        "media": FieldProvenance(source=FieldSource.HUMAN, agent="intake:photo-checklist"),
    }
    if any(s is FieldSource.INFERRED for s in scan.role_sources.values()):
        provenance["media.roles"] = FieldProvenance(
            source=FieldSource.INFERRED, agent="intake:filename-fallback"
        )

    ext_kwargs: dict = {}
    genome_kwargs: dict = {}
    if tr.text:
        note = structurer.structure(tr.text)
        ext_kwargs = {
            "condition_notes": note.condition_notes,
            "flaws": note.flaws,
            "restoration": note.restoration,
        }
        if note.why_special:
            genome_kwargs["why_special"] = note.why_special
        if note.provenance_bullets:
            genome_kwargs["provenance_context"] = note.provenance_bullets
        provenance["unique_physical.condition_notes"] = FieldProvenance(
            source=FieldSource.HUMAN, agent=f"intake:voice-note({tr.source})"
        )
        if note.flaws:
            provenance["unique_physical.flaws"] = FieldProvenance(
                source=FieldSource.INFERRED, agent="intake:keyword-structurer"
            )

    for money_field in ("cost_basis", "floor_price", "list_price"):
        if money_field in numbers:
            provenance[f"economics.{money_field}"] = FieldProvenance(
                source=FieldSource.HUMAN, agent="intake:numbers.csv"
            )

    genome = ProductGenome(
        sku=sku,
        product_type=ProductType.UNIQUE_PHYSICAL,
        media=scan.media,
        economics=Economics(
            cost_basis=numbers.get("cost_basis"),
            list_price=numbers.get("list_price"),
            floor_price=numbers.get("floor_price"),
        ),
        field_provenance=provenance,
        unique_physical=UniquePhysicalExtension(**ext_kwargs),
        **genome_kwargs,
    )
    return genome, scan.report(), tr.source


def run_intake(
    intake_root: Path,
    store: GenomeStore,
    structurer: Optional[TranscriptStructurer] = None,
    transcriber: Optional[Transcriber] = None,
) -> IntakeReport:
    structurer = structurer or KeywordStructurer()
    numbers_by_sku = load_numbers(intake_root)
    report = IntakeReport()

    for item_dir in sorted(p for p in intake_root.iterdir() if p.is_dir()):
        sku = item_dir.name
        try:
            genome, checklist, tr_source = assemble_item(
                item_dir, numbers_by_sku.get(sku, {}), structurer, transcriber
            )
            store.write_birth(genome)
            report.results.append(
                ItemResult(
                    sku=sku,
                    status="created",
                    completeness=completeness_score(genome),
                    checklist_report=checklist,
                    transcript_source=tr_source,
                )
            )
        except BirthRecordExists:
            report.results.append(ItemResult(sku=sku, status="skipped-exists"))
        except Exception as err:  # one bad folder never kills the sweep
            report.results.append(ItemResult(sku=sku, status="error", detail=str(err)))
    return report


def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="marketing.intake",
        description="Sweep an intake folder into genome birth records.",
    )
    parser.add_argument("intake_root", type=Path)
    parser.add_argument("--db", type=Path, default=Path("marketing/genome.db"))
    args = parser.parse_args(argv)

    store = GenomeStore(args.db)
    try:
        report = run_intake(args.intake_root, store)
    finally:
        store.close()
    print(report.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
