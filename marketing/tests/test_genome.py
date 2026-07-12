"""P2.2 test suite — enforces the ratified rules in code.

Covers: governance rule 2 (every field names its consumer), birth-record
immutability, the corrections ledger + effective view, the quarantine
state machine, validation rules, the connector contract, and the
governance rule 3 smoke test (a listing draft renders from a genome).
"""

import pytest

from marketing.genome import (
    Attribution,
    BirthRecordExists,
    Compliance,
    Correction,
    CorrectionReason,
    Economics,
    EraEstimate,
    GenomeStore,
    IllegalTransition,
    MediaItem,
    ProductGenome,
    UniquePhysicalExtension,
    Visibility,
    completeness_score,
    iter_missing_consumers,
)
from marketing.genome.adapter_itemassets import (
    ItemAssets,
    MediaAsset,
    NotConnected,
    PlaceholderSource,
    StaticSource,
    VisionClaim,
)
from marketing.genome.vocab import (
    AttributionStatus,
    ConditionGrade,
    EraBasis,
    FieldSource,
    FlawCode,
    Material,
    MediaRole,
    ProductType,
)


def make_genome(sku: str = "FH-TP-034") -> ProductGenome:
    return ProductGenome(
        sku=sku,
        product_type=ProductType.UNIQUE_PHYSICAL,
        taxonomy="pipes/estate/dublin",
        brand="Chacom",
        model_line="Gentleman 836",
        country_of_origin="FR",
        media=[
            MediaItem(url="photos/FH-TP-034/01.jpg", role=MediaRole.HERO, seq=0),
            MediaItem(url="photos/FH-TP-034/02.jpg", role=MediaRole.STAMPING, seq=1),
            MediaItem(url="photos/FH-TP-034/03.jpg", role=MediaRole.SCALE, seq=2),
        ],
        economics=Economics(cost_basis=22.0, list_price=99.0, floor_price=55.0),
        provenance_context=["single-owner Bristol estate", "seller insisted original stem"],
        why_special="Unsmoked 1950s French shop stock — the sandblast is factory-fresh",
        unique_physical=UniquePhysicalExtension(
            stampings_verbatim="CHACOM / GENTLEMAN / 836 / FRANCE",
            era=EraEstimate(min_year=1950, max_year=1962, basis=EraBasis.STAMPING),
            materials=[Material.BRIAR, Material.VULCANITE],
            condition_grade=ConditionGrade.VERY_GOOD,
            flaws=[FlawCode.RIM_DARKENING],
            brand_attribution=Attribution(
                candidate="Chacom", status=AttributionStatus.VERIFIED
            ),
        ),
    )


# ---------------------------------------------------------------- governance

def test_every_field_declares_its_consumer():
    """Governance rule 2: a field with no named consumer is forbidden."""
    missing = list(iter_missing_consumers())
    assert missing == [], f"fields without a declared consumer: {missing}"


def test_smoke_listing_draft_renders():
    """Governance rule 3: one listing draft must render from the schema.
    (Minimal renderer — the real expression layer is P2.6; this proves
    the genome is consumable by a generator.)"""
    g = make_genome()
    era = g.unique_physical.era
    era_part = (
        f"circa {era.min_year}" if era.basis != EraBasis.GUESS else "mid-century"
    )
    title = f"{g.brand} {g.model_line} — {era_part} | {g.unique_physical.condition_grade.value.replace('_', ' ').title()} Estate"
    assert "Chacom" in title and "1950" in title
    # Flaw disclosure appears in copy (the honesty layer):
    disclosure = ", ".join(f.value.replace("_", " ") for f in g.unique_physical.flaws)
    assert "rim darkening" in disclosure


# ------------------------------------------------------------- immutability

def test_genome_model_is_frozen():
    g = make_genome()
    with pytest.raises(Exception):
        g.brand = "Dunhill"  # type: ignore[misc]


def test_birth_record_is_insert_only(tmp_path):
    store = GenomeStore(tmp_path / "genome.db")
    store.write_birth(make_genome())
    with pytest.raises(BirthRecordExists):
        store.write_birth(make_genome())  # same SKU — must refuse
    store.close()


# ------------------------------------------------- corrections + effective

def test_correction_never_mutates_birth(tmp_path):
    store = GenomeStore(tmp_path / "genome.db")
    store.write_birth(make_genome())

    store.record_correction(
        Correction(
            sku="FH-TP-034",
            field_path="brand",
            old_value="Chacom",
            new_value="Chapuis-Comoy",
            reason=CorrectionReason.NEW_DOCUMENTATION,
            note="1955 catalog located; pre-merger stamping",
        )
    )

    birth = store.get_birth("FH-TP-034")
    effective = store.get_effective("FH-TP-034")
    assert birth["brand"] == "Chacom"              # birth untouched
    assert effective["brand"] == "Chapuis-Comoy"   # effective view corrected
    store.close()


def test_corrections_apply_in_timestamp_order(tmp_path):
    store = GenomeStore(tmp_path / "genome.db")
    store.write_birth(make_genome())
    store.record_correction(
        Correction(
            sku="FH-TP-034",
            field_path="unique_physical.condition_grade",
            new_value="good",
            reason=CorrectionReason.DATA_ENTRY_ERROR,
        )
    )
    store.record_correction(
        Correction(
            sku="FH-TP-034",
            field_path="unique_physical.condition_grade",
            new_value="excellent",
            reason=CorrectionReason.EXPERT_REATTRIBUTION,
        )
    )
    effective = store.get_effective("FH-TP-034")
    assert effective["unique_physical"]["condition_grade"] == "excellent"
    store.close()


def test_correction_requires_factual_reason():
    """There is no 'performance' reason category — by design."""
    assert not any("perf" in r.value or "market" in r.value for r in CorrectionReason)


# ------------------------------------------------------ quarantine machine

def test_quarantine_state_machine(tmp_path):
    store = GenomeStore(tmp_path / "genome.db")
    store.write_birth(make_genome())

    assert store.get_visibility("FH-TP-034") == Visibility.LIVE
    store.quarantine("FH-TP-034", "era misattribution detected")
    assert store.get_visibility("FH-TP-034") == Visibility.QUARANTINED
    store.set_visibility("FH-TP-034", Visibility.REPUBLISHING)
    store.set_visibility("FH-TP-034", Visibility.LIVE)
    assert store.get_visibility("FH-TP-034") == Visibility.LIVE

    # Illegal: LIVE -> REPUBLISHING (must quarantine first)
    with pytest.raises(IllegalTransition):
        store.set_visibility("FH-TP-034", Visibility.REPUBLISHING)
    store.close()


# ---------------------------------------------------------------- validation

def test_floor_price_must_not_exceed_list_price():
    with pytest.raises(ValueError):
        Economics(list_price=50.0, floor_price=60.0)


def test_era_range_ordering():
    with pytest.raises(ValueError):
        EraEstimate(min_year=1970, max_year=1950, basis=EraBasis.STAMPING)


def test_provenance_bullets_capped_at_three_and_140_chars():
    with pytest.raises(ValueError):
        ProductGenome(
            sku="X",
            product_type=ProductType.UNIQUE_PHYSICAL,
            provenance_context=["a", "b", "c", "d"],
        )
    with pytest.raises(ValueError):
        ProductGenome(
            sku="X",
            product_type=ProductType.UNIQUE_PHYSICAL,
            provenance_context=["x" * 141],
        )


def test_extension_only_on_unique_physical():
    with pytest.raises(ValueError):
        ProductGenome(
            sku="X",
            product_type=ProductType.DIGITAL,
            unique_physical=UniquePhysicalExtension(),
        )


def test_required_fields_are_minimal():
    """Anti-validation-theater: a bare SKU + type is a valid birth record.
    Completeness is a score, not a gate."""
    g = ProductGenome(sku="FH-MIN-001", product_type=ProductType.UNIQUE_PHYSICAL)
    assert completeness_score(g) == 0.0
    assert completeness_score(make_genome()) > 0.8


# ----------------------------------------------------------------- connector

def test_placeholder_source_fails_loudly():
    with pytest.raises(NotConnected):
        PlaceholderSource().get("FH-TP-034")


def test_static_source_contract():
    src = StaticSource(
        {
            "FH-TP-034": ItemAssets(
                sku="FH-TP-034",
                media=[MediaAsset(url="p/01.jpg", role=MediaRole.STAMPING)],
                vision_claims=[
                    VisionClaim(field_path="brand", value="Chacom", confidence=0.97)
                ],
                stamping_ocr="CHACOM / GENTLEMAN / 836 / FRANCE",
            )
        }
    )
    assets = src.get("FH-TP-034")
    assert assets is not None
    assert assets.vision_claims[0].confidence > 0.9
    assert src.get("UNKNOWN") is None
