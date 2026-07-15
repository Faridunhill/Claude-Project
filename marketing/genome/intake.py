"""Intake pipeline — P2.3 (Build Handoff §BUILD QUEUE).

Turns raw entry into a genome BIRTH RECORD. One SKU in, one immutable
record out. This is the only writer of new birth records in normal
operation (store.write_birth is insert-only underneath it).

Two sources feed one record:

  1. Priority 1 — the Eye (via adapter_itemassets.ItemAssetsSource):
       media, vision_claims (with confidence), stamping OCR.
     Marketing reads these as a client; it never rebuilds them.
  2. The human at intake (IntakeInput):
       the `why_special` hook (one sentence, ~15s — the single fact
       machines cannot infer), economics (incl. the human-set
       floor_price standing wall), taxonomy, provenance bullets, and
       any manual facts the founder types.

Governance kept (Synthesis §6; Round 2 F1):
  * NEVER BLOCKS on missing fields — only sku + product_type are
    required; everything else is a completeness SCORE, not a gate
    (validation theater is forbidden).
  * EVERY FACT CARRIES PROVENANCE — source (human/vision) + confidence,
    written to genome.field_provenance so the QA gate (P2.4) can route
    Tier A vision claims < 0.90 to review and every generator can decide
    assert-vs-hedge. One vision error must never propagate as fact.
  * FAILS LOUD, NEVER SILENTLY EMPTY — if the Eye is not wired, the
    source raises NotConnected and intake stops; it does not invent an
    item with no photos.

What intake does NOT do: it does not run the QA gate's routing rules
(confidence / corroboration / price / audit) — that is P2.4. Intake
records the raw provenance the gate consumes and gets out of the way.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .adapter_itemassets import ItemAssets, ItemAssetsSource
from .schema import (
    Economics,
    FieldProvenance,
    MediaItem,
    ProductGenome,
    UniquePhysicalExtension,
    completeness_score,
)
from .store import GenomeStore
from .vocab import FieldSource, ProductType

# --------------------------------------------------------------------------
# Field routing — which genome path each incoming fact lands on.
# Vision claims and manual facts both address fields by these dotted paths
# (the same paths field_provenance is keyed on). Unknown paths are recorded
# in the result's `unmapped` list, never silently dropped.
# --------------------------------------------------------------------------

#: Top-level genome fields intake will populate from a claim/fact.
_TOP_LEVEL_FIELDS = frozenset(
    {"brand", "model_line", "taxonomy", "country_of_origin"}
)

#: unique_physical.* fields (keyed WITHOUT the prefix here).
_UNIQUE_PHYSICAL_FIELDS = frozenset(
    {
        "era",
        "materials",
        "measurements",
        "condition_grade",
        "flaws",
        "condition_notes",
        "restoration",
        "stampings_verbatim",
    }
)

_UP_PREFIX = "unique_physical."


@dataclass
class IntakeInput:
    """The human-supplied half of a birth record.

    Only `sku` and `product_type` are required — mirroring the schema's
    ≤5-required rule. `human_facts` lets the founder type or dictate any
    genome field by its dotted path (e.g. {"brand": "Peterson"}); those
    take precedence over a vision claim on the same field and are marked
    source=human.
    """

    sku: str
    product_type: ProductType = ProductType.UNIQUE_PHYSICAL
    why_special: Optional[str] = None            # THE hook (V2 ruling)
    taxonomy: Optional[str] = None               # cohort-learning key
    provenance_context: list[str] = field(default_factory=list)  # <=3 bullets, <=140 chars
    economics: Optional[dict[str, Any]] = None   # cost_basis/list_price/floor_price/currency/...
    human_facts: dict[str, Any] = field(default_factory=dict)     # dotted path -> value
    agent: str = "intake"                        # audit trail


@dataclass
class IntakeResult:
    """What one intake produced — a report, never a silent success."""

    sku: str
    genome: ProductGenome
    written: bool
    completeness: float
    media_count: int
    vision_field_count: int          # Tier-A/B facts sourced from the Eye
    human_field_count: int           # facts the founder supplied
    unmapped: list[str] = field(default_factory=list)   # claim/fact paths intake did not know
    warnings: list[str] = field(default_factory=list)


class IntakeError(Exception):
    """Raised when intake cannot assemble a valid birth record."""


# --------------------------------------------------------------------------
# Assembly (pure) — build a genome from inputs + assets, no DB, no I/O.
# Fully unit-testable with a StaticSource or hand-built ItemAssets.
# --------------------------------------------------------------------------

def build_genome(
    intake: IntakeInput,
    assets: Optional[ItemAssets] = None,
) -> tuple[ProductGenome, IntakeResult]:
    """Assemble (but do not persist) the birth record.

    Precedence for any single field: human_facts > vision claim. Human
    facts win because the founder is the domain expert and a typed fact
    is authoritative over a model guess.
    """
    top: dict[str, Any] = {"sku": intake.sku, "product_type": intake.product_type}
    up: dict[str, Any] = {}
    provenance: dict[str, FieldProvenance] = {}
    unmapped: list[str] = []
    warnings: list[str] = []
    is_unique = intake.product_type is ProductType.UNIQUE_PHYSICAL

    def place(path: str, value: Any, source: FieldSource, confidence: Optional[float], agent: Optional[str]) -> bool:
        """Route one fact to its bucket + record its provenance. Returns
        True if placed, False if the path is unknown / not applicable."""
        if path in _TOP_LEVEL_FIELDS:
            top[path] = value
        elif path.startswith(_UP_PREFIX) or path in _UNIQUE_PHYSICAL_FIELDS:
            key = path[len(_UP_PREFIX):] if path.startswith(_UP_PREFIX) else path
            if key not in _UNIQUE_PHYSICAL_FIELDS:
                return False
            if not is_unique:
                warnings.append(
                    f"dropped unique_physical fact '{key}' — product_type is "
                    f"{intake.product_type.value}, not unique_physical"
                )
                return False
            up[key] = value
            path = _UP_PREFIX + key  # normalise provenance key
        else:
            return False
        provenance[path] = FieldProvenance(source=source, confidence=confidence, agent=agent)
        return True

    # --- human-supplied direct fields ------------------------------------
    human_field_count = 0
    if intake.why_special:
        top["why_special"] = intake.why_special
        provenance["why_special"] = FieldProvenance(source=FieldSource.HUMAN, agent=intake.agent)
        human_field_count += 1
    if intake.taxonomy:
        top["taxonomy"] = intake.taxonomy
        provenance["taxonomy"] = FieldProvenance(source=FieldSource.HUMAN, agent=intake.agent)
        human_field_count += 1
    if intake.provenance_context:
        top["provenance_context"] = list(intake.provenance_context)
        provenance["provenance_context"] = FieldProvenance(source=FieldSource.HUMAN, agent=intake.agent)
        human_field_count += 1
    if intake.economics:
        top["economics"] = Economics(**intake.economics)
        # floor_price is the human-set STANDING WALL — always human provenance
        if intake.economics.get("floor_price") is not None:
            provenance["economics.floor_price"] = FieldProvenance(
                source=FieldSource.HUMAN, agent=intake.agent
            )

    # --- assets from the Eye (Priority 1) --------------------------------
    media_count = 0
    vision_field_count = 0
    if assets is not None:
        # media: photos ARE the DNA
        media = [MediaItem(url=m.url, role=m.role, seq=m.seq) for m in assets.media]
        if media:
            top["media"] = media
            media_count = len(media)

        # stamping OCR -> the anchor fact + the QA gate's second witness
        if assets.stamping_ocr and is_unique:
            if place("unique_physical.stampings_verbatim", assets.stamping_ocr,
                     FieldSource.VISION, None, "stamping_ocr"):
                vision_field_count += 1

        # vision claims -> Tier A/B fields, each with confidence
        for claim in assets.vision_claims:
            if claim.field_path in intake.human_facts:
                continue  # human fact wins; skip the vision claim for this path
            placed = place(
                claim.field_path, claim.value,
                FieldSource.VISION, claim.confidence, claim.model_version or "eye",
            )
            if placed:
                vision_field_count += 1
            else:
                unmapped.append(claim.field_path)

    # --- manual facts (founder-typed) — highest precedence ---------------
    for path, value in intake.human_facts.items():
        if place(path, value, FieldSource.HUMAN, None, intake.agent):
            human_field_count += 1
        else:
            unmapped.append(path)

    # --- construct the (frozen) record -----------------------------------
    if up:
        top["unique_physical"] = UniquePhysicalExtension(**up)
    top["field_provenance"] = provenance
    # entry_ts / schema_version / vocab_version are left to the schema defaults.

    try:
        genome = ProductGenome(**top)
    except Exception as err:  # pydantic ValidationError et al.
        raise IntakeError(f"intake could not build a valid genome for {intake.sku}: {err}") from err

    result = IntakeResult(
        sku=intake.sku,
        genome=genome,
        written=False,
        completeness=completeness_score(genome),
        media_count=media_count,
        vision_field_count=vision_field_count,
        human_field_count=human_field_count,
        unmapped=unmapped,
        warnings=warnings,
    )
    return genome, result


# --------------------------------------------------------------------------
# Orchestration — pull from the Eye, assemble, persist.
# --------------------------------------------------------------------------

def ingest(
    intake: IntakeInput,
    source: ItemAssetsSource,
    store: GenomeStore,
) -> IntakeResult:
    """Full pipeline for one SKU: fetch assets → build genome → write
    birth record. Raises NotConnected (from the source) if the Eye is not
    wired — intake never fabricates an item with no photos. Raises
    BirthRecordExists (from the store) on a duplicate SKU — birth records
    are insert-only; later changes go to the corrections ledger.
    """
    assets = source.get(intake.sku)  # may raise NotConnected — let it
    if assets is None:
        # Known-absent (StaticSource returns None) is different from
        # not-wired (PlaceholderSource raises). Absent = list from human
        # facts only, still valid, but say so.
        genome, result = build_genome(intake, assets=None)
        result.warnings.append(
            f"no Priority-1 assets found for {intake.sku} — built from human intake only"
        )
    else:
        genome, result = build_genome(intake, assets=assets)

    store.write_birth(genome)  # insert-only; raises BirthRecordExists on dup
    result.written = True
    return result
