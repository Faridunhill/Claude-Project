"""Genome schema v1.0 — Marketing DNA birth record (Synthesis §3).

Layer 1 of three. Facts about the object, written at entry, immutable.
Corrections never mutate a birth record — they append to the corrections
ledger (corrections.py) and are merged at read time.

Governance-lite (Synthesis §6), enforced in code and tests:
  1. ADD ONLY, NEVER MUTATE — bump SCHEMA_VERSION when adding fields;
     never rename, delete, or repurpose one.
  2. EVERY FIELD DECLARES ITS CONSUMER — each field carries a
     json_schema_extra={"consumer": ...} naming the machine that reads
     it. `iter_missing_consumers()` is run by the test suite; a field
     without a consumer fails CI.
  3. ONE SMOKE TEST BEFORE ADOPTION — tests/test_genome.py renders a
     listing draft from a genome record on every run.

Required fields are deliberately ≤ 5 (Round 1 Q4: validation theater is
forbidden). Everything else is optional; use `completeness_score()` to
track gaps instead of blocking intake.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .vocab import (
    VOCAB_VERSION,
    AttributionStatus,
    ConditionGrade,
    EraBasis,
    FieldSource,
    FlawCode,
    Material,
    MediaRole,
    ProductType,
    RestorationCode,
)

SCHEMA_VERSION = "1.0.0"


def _c(consumer: str, **kwargs):
    """Field with a declared downstream consumer (governance rule 2)."""
    return Field(json_schema_extra={"consumer": consumer}, **kwargs)


class FieldProvenance(BaseModel):
    """Who asserted a fact, how confidently, and when.

    Consumer: every expression generator — decides assert vs hedge;
    the QA gate — routes low-confidence Tier A fields to review.
    """

    model_config = ConfigDict(frozen=True)

    source: FieldSource = _c("QA gate routing; copy assert-vs-hedge rules")
    confidence: Optional[float] = _c(
        "QA gate confidence rule (Tier A < 0.90 routes to review)",
        default=None,
        ge=0.0,
        le=1.0,
    )
    ts: datetime = _c(
        "audit trail",
        default_factory=lambda: datetime.now(timezone.utc),
    )
    agent: Optional[str] = _c("audit trail — which system wrote this", default=None)


class EraEstimate(BaseModel):
    """Never a point estimate. `basis` decides assert-vs-hedge."""

    model_config = ConfigDict(frozen=True)

    min_year: int = _c("copy 'circa' claims; vintage/antique keyword eligibility", ge=1600, le=2100)
    max_year: int = _c("copy 'circa' claims; price-band selection", ge=1600, le=2100)
    basis: EraBasis = _c("assert-vs-hedge rule in copy generators")

    @model_validator(mode="after")
    def _order(self):
        if self.min_year > self.max_year:
            raise ValueError("era min_year must be <= max_year")
        return self


class Measurements(BaseModel):
    """SI units only. Consumer: marketplace item specifics; size filters;
    shipping-cost automation."""

    model_config = ConfigDict(frozen=True)

    length_mm: Optional[float] = _c("marketplace item specifics; size-filter buyers", default=None, ge=0)
    height_mm: Optional[float] = _c("marketplace item specifics", default=None, ge=0)
    weight_g: Optional[float] = _c("shipping cost automation; item specifics", default=None, ge=0)
    chamber_diameter_mm: Optional[float] = _c("collector item specifics", default=None, ge=0)
    chamber_depth_mm: Optional[float] = _c("collector item specifics", default=None, ge=0)


class MediaItem(BaseModel):
    """A photograph of the physical object. Photos ARE the DNA.
    Generated (synthetic) imagery is NEVER a MediaItem — it lives in the
    expression layer with its own manifest (addendum V2) and is barred
    from listing slots by the placement law."""

    model_config = ConfigDict(frozen=True)

    url: str = _c("channel adapters — listing image slots", min_length=1)
    role: MediaRole = _c("hero selection; flaw pairing; Etsy allowlist; alt-text generation")
    seq: int = _c("image ordering per channel", ge=0, default=0)


class Economics(BaseModel):
    """Marketing without margin awareness is spend, not marketing."""

    model_config = ConfigDict(frozen=True)

    cost_basis: Optional[float] = _c("margin-aware promotion; offer floors", default=None, ge=0)
    list_price: Optional[float] = _c("baseline price on all channels", default=None, ge=0)
    floor_price: Optional[float] = _c(
        "STANDING WALL — repricing/offer automation never crosses this; human-set only",
        default=None,
        ge=0,
    )
    acquired_at: Optional[datetime] = _c("staleness triggers (60/90-day promotion rules)", default=None)
    currency: str = _c("channel adapters; reporting", default="GBP", min_length=3, max_length=3)

    @model_validator(mode="after")
    def _floor_below_list(self):
        if (
            self.floor_price is not None
            and self.list_price is not None
            and self.floor_price > self.list_price
        ):
            raise ValueError("floor_price must be <= list_price")
        return self


class Compliance(BaseModel):
    """Content FACTS only. Per-channel eligibility is DERIVED by the
    rules engine — never stored (Synthesis §3 forbidden list)."""

    model_config = ConfigDict(frozen=True)

    age_restricted: bool = _c("channel-eligibility rules engine", default=True)
    smoking_related: bool = _c(
        "channel-eligibility rules engine; visual-generation negative constraints",
        default=True,
    )
    restricted_materials: list[Material] = _c(
        "CITES / marketplace restriction review before listing",
        default_factory=list,
    )


class Attribution(BaseModel):
    """QA-gate state for a Tier A claim (Synthesis §5). When status is
    not VERIFIED, generators must hedge and the price model treats the
    item as unattributed (no-name floor)."""

    model_config = ConfigDict(frozen=True)

    candidate: str = _c("review screen; hedged copy ('attributed to')", min_length=1)
    status: AttributionStatus = _c("generator lock — assertive claims require VERIFIED")
    basis: FieldSource = _c("QA gate routing", default=FieldSource.VISION)


class UniquePhysicalExtension(BaseModel):
    """Extension for one-of-a-kind physical items (the estate business).
    The forensic core: unique-item businesses live or die here.

    repeatable_physical and digital extensions live in the shared method
    library, NOT in this repository — businesses are firewalled (LAW 06);
    only the method is shared."""

    model_config = ConfigDict(frozen=True)

    stampings_verbatim: Optional[str] = _c(
        "THE ANCHOR FACT — era attribution; authentication copy; collector search terms; "
        "QA-gate corroboration rule (cross-checked against vision claims)",
        default=None,
    )
    era: Optional[EraEstimate] = _c("copy claims; vintage/antique keywords; price band", default=None)
    materials: list[Material] = _c(
        "filters; keywords; compliance restricted-material triggers",
        default_factory=list,
    )
    measurements: Optional[Measurements] = _c("item specifics; shipping", default=None)
    condition_grade: Optional[ConditionGrade] = _c(
        "price model; title modifiers; buyer-expectation copy",
        default=None,
    )
    flaws: list[FlawCode] = _c(
        "honesty layer — auto-disclosed in copy, paired with FLAW photos; returns prevention",
        default_factory=list,
    )
    condition_notes: Optional[str] = _c("copy-generation detail (dictated voice note)", default=None)
    restoration: list[RestorationCode] = _c("copy disclosure; collector trust", default_factory=list)
    brand_attribution: Optional[Attribution] = _c(
        "QA gate hedge-and-list path; generator lock",
        default=None,
    )


class ProductGenome(BaseModel):
    """The birth record. Immutable once written (store.py enforces
    insert-only; corrections go to the ledger).

    Required fields (exactly 3 — validation theater is forbidden):
    sku, product_type, entry via defaults. Everything else optional;
    completeness is a score, not a gate."""

    model_config = ConfigDict(frozen=True)

    sku: str = _c("join key for expression, phenotype, sold-price DB — everything", min_length=1)
    product_type: ProductType = _c("schema routing; channel adapters")
    taxonomy: Optional[str] = _c(
        "channel category mapping; store nav; SEO hubs; COHORT LEARNING KEY",
        default=None,
    )
    brand: Optional[str] = _c(
        "brand hub pages; price benchmarking vs sold DB; cohort key",
        default=None,
    )
    model_line: Optional[str] = _c("collector SEO (shape-number searches); authentication", default=None)
    country_of_origin: Optional[str] = _c(
        "marketplace item specifics; customs; origin keywords",
        default=None,
        min_length=2,
        max_length=2,
    )
    media: list[MediaItem] = _c(
        "listing image slots per channel; flaw pairing; alt-text",
        default_factory=list,
    )
    economics: Economics = _c("pricing, promotion, staleness automation", default_factory=Economics)
    compliance: Compliance = _c("channel-eligibility rules engine", default_factory=Compliance)
    provenance_context: list[str] = _c(
        "story generation from non-regenerable human facts (V1 ruling: voice-captured)",
        default_factory=list,
        max_length=3,
    )
    why_special: Optional[str] = _c(
        "THE per-item hook — seed of every generated narrative (V2 ruling)",
        default=None,
    )
    field_provenance: dict[str, FieldProvenance] = _c(
        "QA gate routing; assert-vs-hedge in every generator",
        default_factory=dict,
    )
    unique_physical: Optional[UniquePhysicalExtension] = _c(
        "forensic core for one-of-a-kind items",
        default=None,
    )
    entry_ts: datetime = _c(
        "audit; freshness",
        default_factory=lambda: datetime.now(timezone.utc),
    )
    schema_version: str = _c("migration control", default=SCHEMA_VERSION)
    vocab_version: str = _c("migration control", default=VOCAB_VERSION)

    @field_validator("provenance_context")
    @classmethod
    def _bullets_short(cls, v: list[str]) -> list[str]:
        for bullet in v:
            if len(bullet) > 140:
                raise ValueError("provenance_context bullets must be <= 140 chars (V1 ruling)")
        return v

    @model_validator(mode="after")
    def _extension_matches_type(self):
        if self.product_type is not ProductType.UNIQUE_PHYSICAL and self.unique_physical is not None:
            raise ValueError("unique_physical extension only valid on unique_physical products")
        return self


# --------------------------------------------------------------------------
# Governance rule 2 enforcement — every field names its consumer.
# --------------------------------------------------------------------------

_ALL_MODELS = (
    FieldProvenance,
    EraEstimate,
    Measurements,
    MediaItem,
    Economics,
    Compliance,
    Attribution,
    UniquePhysicalExtension,
    ProductGenome,
)


def iter_missing_consumers():
    """Yield (model_name, field_name) for every field lacking a declared
    consumer. The test suite asserts this yields nothing."""
    for model in _ALL_MODELS:
        for name, info in model.model_fields.items():
            extra = info.json_schema_extra
            if not (isinstance(extra, dict) and extra.get("consumer")):
                yield (model.__name__, name)


# --------------------------------------------------------------------------
# Completeness score — the anti-validation-theater mechanism.
# --------------------------------------------------------------------------

#: Fields that matter for a sellable unique item, with weights.
_COMPLETENESS_WEIGHTS: dict[str, float] = {
    "media": 3.0,               # photos are the DNA
    "economics.cost_basis": 2.0,
    "economics.floor_price": 2.0,
    "economics.list_price": 1.0,
    "why_special": 2.0,
    "taxonomy": 1.0,
    "brand": 1.0,
    "unique_physical.stampings_verbatim": 2.0,
    "unique_physical.condition_grade": 1.0,
    "unique_physical.era": 1.0,
    "unique_physical.condition_notes": 1.0,
}


def _get_path(genome: ProductGenome, path: str):
    obj = genome
    for part in path.split("."):
        if obj is None:
            return None
        obj = getattr(obj, part, None)
    return obj


def completeness_score(genome: ProductGenome) -> float:
    """0.0–1.0. Reported, never enforced: generators degrade gracefully
    on gaps (era unknown -> copy omits era claims)."""
    total = sum(_COMPLETENESS_WEIGHTS.values())
    earned = 0.0
    for path, weight in _COMPLETENESS_WEIGHTS.items():
        value = _get_path(genome, path)
        if value not in (None, "", [], {}):
            earned += weight
    return round(earned / total, 3)
