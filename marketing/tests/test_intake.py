"""P2.3 intake pipeline tests.

Each test pins one guarantee from the ratified spec (Build Handoff §BUILD
QUEUE; Round 2 F1/F2). If a guarantee regresses, exactly one test fails.
"""

from __future__ import annotations

import pytest

from marketing.genome.adapter_itemassets import (
    ItemAssets,
    MediaAsset,
    NotConnected,
    PlaceholderSource,
    StaticSource,
    VisionClaim,
)
from marketing.genome.intake import (
    IntakeError,
    IntakeInput,
    build_genome,
    ingest,
)
from marketing.genome.store import BirthRecordExists, GenomeStore
from marketing.genome.vocab import FieldSource, MediaRole, ProductType


def _assets(sku="FH-PIPE-001", **over):
    base = dict(
        sku=sku,
        media=[
            MediaAsset(url="https://cdn/x/hero.jpg", role=MediaRole.HERO, seq=0),
            MediaAsset(url="https://cdn/x/stamp.jpg", role=MediaRole.STAMPING, seq=1),
        ],
        vision_claims=[
            VisionClaim(field_path="brand", value="Peterson", confidence=0.97, model_version="eye-v3"),
            VisionClaim(field_path="country_of_origin", value="IE", confidence=0.88),
            VisionClaim(
                field_path="unique_physical.era",
                value={"min_year": 1950, "max_year": 1970, "basis": "hallmark"},
                confidence=0.72,
            ),
        ],
        stamping_ocr="PETERSON'S / DUBLIN / MADE IN IRELAND / 106",
    )
    base.update(over)
    return ItemAssets(**base)


def _store(tmp_path):
    return GenomeStore(tmp_path / "genome.db")


# -- required-fields / no validation theater --------------------------------

def test_only_sku_and_type_are_required():
    """A bare intake with no assets still produces a valid birth record."""
    genome, result = build_genome(IntakeInput(sku="FH-BARE-1"))
    assert genome.sku == "FH-BARE-1"
    assert genome.product_type is ProductType.UNIQUE_PHYSICAL
    assert result.completeness >= 0.0  # scored, never gated


# -- provenance on every fact -----------------------------------------------

def test_vision_claims_carry_source_and_confidence():
    genome, result = build_genome(IntakeInput(sku="FH-PIPE-001"), assets=_assets())
    prov = genome.field_provenance
    assert prov["brand"].source is FieldSource.VISION
    assert prov["brand"].confidence == 0.97
    assert prov["country_of_origin"].confidence == 0.88
    # low-confidence Tier A fact is recorded faithfully (QA gate will route it)
    assert prov["unique_physical.era"].confidence == 0.72
    assert result.vision_field_count >= 3


def test_human_hook_and_floor_price_are_human_sourced():
    genome, _ = build_genome(
        IntakeInput(
            sku="FH-PIPE-001",
            why_special="Unsmoked 1950s Dublin shop stock — hallmark crisp.",
            economics={"list_price": 149.0, "floor_price": 90.0, "currency": "USD"},
        ),
        assets=_assets(),
    )
    assert genome.why_special.startswith("Unsmoked")
    assert genome.field_provenance["why_special"].source is FieldSource.HUMAN
    # floor_price is the standing wall — always human provenance
    assert genome.field_provenance["economics.floor_price"].source is FieldSource.HUMAN
    assert genome.economics.floor_price == 90.0


# -- precedence: human fact beats a vision claim on the same field ----------

def test_human_fact_overrides_vision_claim():
    genome, _ = build_genome(
        IntakeInput(sku="FH-PIPE-001", human_facts={"brand": "Kapp & Peterson"}),
        assets=_assets(),
    )
    assert genome.brand == "Kapp & Peterson"          # human value, not "Peterson"
    assert genome.field_provenance["brand"].source is FieldSource.HUMAN


# -- the anchor fact + media ------------------------------------------------

def test_stamping_ocr_becomes_the_anchor_fact():
    genome, _ = build_genome(IntakeInput(sku="FH-PIPE-001"), assets=_assets())
    assert genome.unique_physical.stampings_verbatim.startswith("PETERSON")
    assert genome.field_provenance["unique_physical.stampings_verbatim"].source is FieldSource.VISION


def test_media_is_carried_verbatim():
    genome, result = build_genome(IntakeInput(sku="FH-PIPE-001"), assets=_assets())
    assert result.media_count == 2
    assert genome.media[0].role is MediaRole.HERO


# -- unknown paths are reported, never silently dropped ---------------------

def test_unknown_claim_paths_are_reported():
    assets = _assets(vision_claims=[
        VisionClaim(field_path="favourite_colour", value="green", confidence=0.99),
    ])
    _, result = build_genome(IntakeInput(sku="FH-PIPE-001"), assets=assets)
    assert "favourite_colour" in result.unmapped


# -- product-type firewall on the unique_physical extension -----------------

def test_unique_physical_facts_dropped_for_non_unique_type():
    genome, result = build_genome(
        IntakeInput(sku="FH-DIGI-1", product_type=ProductType.DIGITAL),
        assets=_assets(),
    )
    assert genome.unique_physical is None
    assert any("unique_physical" in w for w in result.warnings)


# -- orchestration: fail loud when the Eye is not wired ---------------------

def test_ingest_fails_loud_when_not_connected(tmp_path):
    store = _store(tmp_path)
    with pytest.raises(NotConnected):
        ingest(IntakeInput(sku="FH-PIPE-001"), PlaceholderSource(), store)


def test_ingest_writes_birth_record(tmp_path):
    store = _store(tmp_path)
    source = StaticSource({"FH-PIPE-001": _assets()})
    result = ingest(
        IntakeInput(sku="FH-PIPE-001", why_special="Crisp hallmark."),
        source, store,
    )
    assert result.written is True
    assert store.get_birth("FH-PIPE-001") is not None
    # effective read includes what intake wrote
    eff = store.get_effective("FH-PIPE-001")
    assert eff["brand"] == "Peterson"


def test_ingest_is_insert_only(tmp_path):
    store = _store(tmp_path)
    source = StaticSource({"FH-PIPE-001": _assets()})
    ingest(IntakeInput(sku="FH-PIPE-001"), source, store)
    with pytest.raises(BirthRecordExists):
        ingest(IntakeInput(sku="FH-PIPE-001"), source, store)


def test_ingest_without_assets_lists_from_human_intake(tmp_path):
    store = _store(tmp_path)
    source = StaticSource({})  # SKU genuinely absent (not "not wired")
    result = ingest(
        IntakeInput(sku="FH-ORPHAN-1", why_special="Founder's own bench find."),
        source, store,
    )
    assert result.written is True
    assert result.media_count == 0
    assert any("human intake only" in w for w in result.warnings)
