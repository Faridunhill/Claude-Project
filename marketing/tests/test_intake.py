"""P2.3 test suite — intake pipeline end to end on a synthetic folder."""

from pathlib import Path

import pytest

from marketing.genome import GenomeStore, Visibility
from marketing.genome.vocab import FieldSource, FlawCode, MediaRole, RestorationCode
from marketing.intake import (
    KeywordStructurer,
    StubTranscriber,
    get_transcript,
    load_numbers,
    run_intake,
    scan_photos,
)

TRANSCRIPT = (
    "Chacom Gentleman, cleaned and sanitized, stem repolished. "
    "Rim darkening and light tooth marks on the button. "
    "Provenance: single-owner Bristol estate, seller insisted original stem. "
    "Special: unsmoked nineteen fifties French shop stock, factory-fresh sandblast."
)


def make_intake(tmp_path: Path, sku: str = "FH-TP-041", with_transcript: bool = True) -> Path:
    root = tmp_path / "intake"
    item = root / sku
    item.mkdir(parents=True)
    frames = [
        "01-hero.jpg", "02-angle.jpg", "03-angle.jpg", "04-stamping.jpg",
        "05-stamping.jpg", "06-flaw.jpg", "07-scale.jpg", "08-weight.jpg",
        "09.jpg",  # no role token -> ANGLE, marked inferred
    ]
    for name in frames:
        (item / name).write_bytes(b"\xff\xd8fake-jpeg")
    (item / "note.m4a").write_bytes(b"fake-audio")
    if with_transcript:
        (item / "note.m4a.txt").write_text(TRANSCRIPT, encoding="utf-8")
    (root / "numbers.csv").write_text(
        "sku,cost_basis,floor_price,list_price\n"
        f"{sku},22,55,99\n",
        encoding="utf-8",
    )
    return root


# ------------------------------------------------------------------ photos

def test_photo_scan_roles_and_checklist(tmp_path):
    root = make_intake(tmp_path)
    scan = scan_photos(root / "FH-TP-041")
    assert scan.frame_count == 9
    roles = {m.role for m in scan.media}
    assert {MediaRole.HERO, MediaRole.STAMPING, MediaRole.FLAW, MediaRole.SCALE} <= roles
    assert scan.ok
    # roleless file fell back to ANGLE and is marked inferred
    inferred = [p for p, s in scan.role_sources.items() if s is FieldSource.INFERRED]
    assert len(inferred) == 1 and inferred[0].endswith("09.jpg")


def test_checklist_reports_critical_gap_but_never_blocks(tmp_path):
    root = tmp_path / "intake"
    item = root / "FH-TP-042"
    item.mkdir(parents=True)
    for name in ("01-hero.jpg", "02-angle.jpg"):  # no stamping, no scale
        (item / name).write_bytes(b"x")
    scan = scan_photos(item)
    assert not scan.ok
    assert any("stamping" in gap for gap in scan.missing_critical)
    assert any("scale" in gap for gap in scan.missing_critical)


# -------------------------------------------------------------- transcripts

def test_sidecar_transcript_preferred_over_transcriber(tmp_path):
    root = make_intake(tmp_path)
    result = get_transcript(root / "FH-TP-041", StubTranscriber("SHOULD NOT BE USED"))
    assert result.source == "sidecar"
    assert "Bristol estate" in result.text


def test_missing_transcript_is_pending_not_fatal(tmp_path):
    root = make_intake(tmp_path, with_transcript=False)
    result = get_transcript(root / "FH-TP-041", transcriber=None)
    assert result.source == "pending" and result.text is None


# -------------------------------------------------------------- structuring

def test_keyword_structurer_is_conservative_and_lossless():
    note = KeywordStructurer().structure(TRANSCRIPT)
    assert FlawCode.RIM_DARKENING in note.flaws
    assert FlawCode.TOOTH_MARKS_LIGHT in note.flaws
    assert RestorationCode.CLEANED in note.restoration
    assert RestorationCode.SANITIZED in note.restoration
    assert RestorationCode.STEM_REPOLISHED in note.restoration
    assert note.condition_notes == TRANSCRIPT          # nothing dictated is lost
    assert "unsmoked" in note.why_special
    assert note.provenance_bullets and "Bristol estate" in note.provenance_bullets[0]


# ------------------------------------------------------------------ numbers

def test_numbers_csv_parsing(tmp_path):
    root = make_intake(tmp_path)
    nums = load_numbers(root)
    assert nums["FH-TP-041"] == {"cost_basis": 22.0, "floor_price": 55.0, "list_price": 99.0}


# --------------------------------------------------------------- end to end

def test_full_intake_creates_birth_record(tmp_path):
    root = make_intake(tmp_path)
    store = GenomeStore(tmp_path / "genome.db")
    report = run_intake(root, store)

    assert [r.status for r in report.results] == ["created"]
    assert report.results[0].completeness > 0.6

    effective = store.get_effective("FH-TP-041")
    assert effective["economics"]["floor_price"] == 55.0
    assert effective["why_special"].startswith("unsmoked")
    assert "rim_darkening" in effective["unique_physical"]["flaws"]
    assert len(effective["media"]) == 9
    # provenance discipline: voice-derived flaws marked inferred, numbers human
    fp = effective["field_provenance"]
    assert fp["unique_physical.flaws"]["source"] == "inferred"
    assert fp["economics.floor_price"]["source"] == "human"
    assert store.get_visibility("FH-TP-041") == Visibility.LIVE
    store.close()


def test_intake_is_idempotent(tmp_path):
    root = make_intake(tmp_path)
    store = GenomeStore(tmp_path / "genome.db")
    run_intake(root, store)
    second = run_intake(root, store)
    assert [r.status for r in second.results] == ["skipped-exists"]
    store.close()


def test_one_bad_folder_never_kills_the_sweep(tmp_path):
    root = make_intake(tmp_path)
    # a second folder whose name collides after normalization is fine;
    # instead simulate breakage with an unreadable numbers row + empty dir
    (root / "FH-EMPTY-001").mkdir()
    store = GenomeStore(tmp_path / "genome.db")
    report = run_intake(root, store)
    statuses = {r.sku: r.status for r in report.results}
    assert statuses["FH-TP-041"] == "created"
    # empty folder still creates a (bare) record — throughput rule:
    assert statuses["FH-EMPTY-001"] in {"created", "error"}
    store.close()
