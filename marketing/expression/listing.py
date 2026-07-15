"""Listing copy generator — P2.6 (EXPRESSION layer).

genome (+ QA-gate decision) -> a listing draft: title, description, tags,
ordered images with alt-text, and flaw disclosures. Pure and deterministic
(no I/O), so it is unit-testable and re-runnable; the output is disposable
and regenerated from the genome at will.

Assert-vs-hedge is not a style choice here — it is enforced from the gate:
a Tier A claim is stated as fact only when `decision.assertable_tier_a`
says so. Otherwise the generator hedges ("attributed to") or omits. Copy
never invents an era, a grade, or a maker the record does not carry.

Voice (copy rules): collector-to-collector, plain, no hype adjectives.
Every flaw the record carries is disclosed. `why_special` seeds the lead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..genome.gate import GateDecision, GateOutcome
from ..genome.schema import ProductGenome
from ..genome.vocab import (
    RESTRICTED_MATERIALS,
    ConditionGrade,
    EraBasis,
    FlawCode,
    MediaRole,
    RestorationCode,
)

# --- phrasing tables (narrative text, not machine enums) -------------------

_CONDITION_TITLE: dict[ConditionGrade, str] = {
    ConditionGrade.MINT: "Mint",
    ConditionGrade.EXCELLENT: "Excellent",
    ConditionGrade.VERY_GOOD: "Very Good",
    ConditionGrade.GOOD: "Good",
    ConditionGrade.FAIR: "Fair",
    ConditionGrade.PROJECT: "Restoration Project",
}

_CONDITION_EXPECTATION: dict[ConditionGrade, str] = {
    ConditionGrade.MINT: "Unsmoked, as-new — no wear to report.",
    ConditionGrade.EXCELLENT: "Lightly smoked and expertly cleaned; presents close to new.",
    ConditionGrade.VERY_GOOD: "An honest estate pipe with light, even wear consistent with careful use.",
    ConditionGrade.GOOD: "A sound working pipe showing normal estate wear, detailed below.",
    ConditionGrade.FAIR: "A well-used pipe with visible wear; priced accordingly.",
    ConditionGrade.PROJECT: "Sold as a restoration project — see the condition notes and photos.",
}

_FLAW_PHRASE: dict[FlawCode, str] = {
    FlawCode.RIM_DARKENING: "some darkening to the rim",
    FlawCode.RIM_CHAR: "light charring at the rim",
    FlawCode.TOOTH_MARKS_LIGHT: "light tooth marks on the bit",
    FlawCode.TOOTH_MARKS_DEEP: "deeper tooth marks on the bit",
    FlawCode.STEM_OXIDATION: "some oxidation to the stem",
    FlawCode.FILLS: "factory fills in the briar",
    FlawCode.CRACK: "a crack (detailed in the photos)",
    FlawCode.CHIP: "a small chip (shown in the photos)",
    FlawCode.SCRATCHES: "surface scratches",
    FlawCode.DENT: "a dent to the surface",
    FlawCode.FINISH_WEAR: "wear to the finish",
    FlawCode.LOOSE_STEM_FIT: "a slightly loose stem fit",
    FlawCode.TIGHT_STEM_FIT: "a tight stem fit",
    FlawCode.REPLACEMENT_STEM: "a replacement stem (not original)",
    FlawCode.REPLACEMENT_BAND: "an added band (not original to the pipe)",
    FlawCode.GHOSTING: "a faint ghost of previous tobacco",
    FlawCode.MISSING_PART: "a missing part (detailed below)",
}

_RESTORATION_PHRASE: dict[RestorationCode, str] = {
    RestorationCode.CLEANED: "cleaned",
    RestorationCode.SANITIZED: "sanitized",
    RestorationCode.STEM_REPOLISHED: "stem re-polished",
    RestorationCode.STEM_DEOXIDIZED: "stem de-oxidized",
    RestorationCode.RIM_TOPPED: "rim topped",
    RestorationCode.REFINISHED: "refinished",
    RestorationCode.REWAXED: "re-waxed",
    RestorationCode.STEM_REPLACED: "stem replaced",
    RestorationCode.BAND_REPLACED: "band replaced",
    RestorationCode.UNRESTORED: "left unrestored",
}

_ROLE_ALT: dict[MediaRole, str] = {
    MediaRole.HERO: "main view",
    MediaRole.ANGLE: "additional angle",
    MediaRole.STAMPING: "shank stamping detail",
    MediaRole.FLAW: "condition detail",
    MediaRole.SCALE: "size reference",
    MediaRole.GROUP: "full set",
}

#: photo display order per channel (hero first, disclosures near the end).
_ROLE_ORDER = [MediaRole.HERO, MediaRole.ANGLE, MediaRole.STAMPING,
               MediaRole.SCALE, MediaRole.FLAW, MediaRole.GROUP]

#: per-channel title length ceilings (0 = unlimited).
_TITLE_MAX = {"own_store": 0, "etsy": 140, "ebay": 80}


@dataclass
class ListingDraft:
    sku: str
    channel: str
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    image_order: list[str] = field(default_factory=list)
    alt_texts: dict[str, str] = field(default_factory=dict)
    disclosures: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)      # high-value missing facts
    hedged: list[str] = field(default_factory=list)    # Tier A fields stated as hedges


# --- helpers ---------------------------------------------------------------

def _brand_phrase(genome: ProductGenome, decision: GateDecision) -> tuple[Optional[str], bool]:
    """Return (text, asserted). Asserted brand -> plain name; hedged ->
    'attributed to X'; absent -> (None, False)."""
    if not genome.brand:
        return None, False
    if "brand" in decision.assertable_tier_a:
        return genome.brand, True
    return f"attributed to {genome.brand}", False


def _era_phrase(genome: ProductGenome, decision: GateDecision, reference_year: Optional[int]) -> tuple[Optional[str], list[str]]:
    """Return (era text or None, extra keyword tags). Basis decides assert
    vs hedge (Synthesis §3 era rule)."""
    up = genome.unique_physical
    if up is None or up.era is None:
        return None, []
    era = up.era
    assertable = "unique_physical.era" in decision.assertable_tier_a
    hard_basis = era.basis in (EraBasis.STAMPING, EraBasis.HALLMARK, EraBasis.CATALOG, EraBasis.DOCUMENTATION)

    if assertable and hard_basis:
        text = f"circa {era.min_year}" if era.min_year == era.max_year else f"circa {era.min_year}–{era.max_year}"
    else:
        decade = (era.min_year // 10) * 10
        text = f"{decade}s"  # hedged: decade, no 'circa'

    tags: list[str] = []
    if reference_year is not None and assertable and hard_basis:
        if era.min_year <= reference_year - 100:
            tags.append("antique")          # 100y+ is a legal claim — assert only when hard
        elif era.max_year <= reference_year - 20:
            tags.append("vintage")
    return text, tags


def _disclosures(genome: ProductGenome) -> list[str]:
    up = genome.unique_physical
    if up is None:
        return []
    out = [_FLAW_PHRASE.get(f, f.value.replace("_", " ")) for f in up.flaws]
    return out


def _restoration_note(genome: ProductGenome) -> Optional[str]:
    up = genome.unique_physical
    if up is None or not up.restoration:
        return None
    parts = [_RESTORATION_PHRASE.get(r, r.value.replace("_", " ")) for r in up.restoration]
    return "Work done: " + ", ".join(parts) + "."


def _images(genome: ProductGenome) -> tuple[list[str], dict[str, str]]:
    ordered = sorted(
        genome.media,
        key=lambda m: (_ROLE_ORDER.index(m.role) if m.role in _ROLE_ORDER else 99, m.seq),
    )
    urls = [m.url for m in ordered]
    alts: dict[str, str] = {}
    for m in ordered:
        base = _ROLE_ALT.get(m.role, "photo")
        label = genome.brand or genome.product_type.value
        alts[m.url] = f"{label} — {base}"
    return urls, alts


def _truncate(title: str, limit: int) -> str:
    if not limit or len(title) <= limit:
        return title
    cut = title[:limit].rsplit(" ", 1)[0]
    return cut


# --- the generator ---------------------------------------------------------

def generate_listing(
    genome: ProductGenome,
    decision: GateDecision,
    *,
    channel: str = "own_store",
    reference_year: Optional[int] = None,
) -> ListingDraft:
    up = genome.unique_physical
    brand_text, brand_asserted = _brand_phrase(genome, decision)
    era_text, era_tags = _era_phrase(genome, decision, reference_year)
    disclosures = _disclosures(genome)
    image_order, alt_texts = _images(genome)

    grade = up.condition_grade if up else None

    # -- title -------------------------------------------------------------
    title_bits: list[str] = []
    if brand_asserted and brand_text:
        title_bits.append(brand_text)
    if genome.model_line:
        title_bits.append(genome.model_line)
    if grade is not None and grade not in (ConditionGrade.VERY_GOOD, ConditionGrade.GOOD):
        title_bits.append(_CONDITION_TITLE[grade])
    if not brand_asserted and brand_text:
        # hedged brand never claims the maker in the title
        title_bits.append("Estate Pipe (attributed)")
    else:
        title_bits.append("Estate Pipe")
    title = _truncate(" ".join(b for b in title_bits if b), _TITLE_MAX.get(channel, 0))

    # -- description -------------------------------------------------------
    paras: list[str] = []
    if genome.why_special:
        paras.append(genome.why_special.rstrip("."))
    lead_subject = brand_text if brand_text else "This estate pipe"
    lead = lead_subject[0].upper() + lead_subject[1:]
    if era_text:
        lead += f", {era_text}"
    if genome.country_of_origin:
        lead += f" ({genome.country_of_origin})"
    paras.append(lead + ".")

    if grade is not None:
        paras.append(_CONDITION_EXPECTATION[grade])
    if up and up.condition_notes:
        paras.append(up.condition_notes.rstrip(".") + ".")
    if disclosures:
        paras.append("Honestly noted: " + "; ".join(disclosures) + " — all shown in the photographs.")
    restore = _restoration_note(genome)
    if restore:
        paras.append(restore)
    if up and up.stampings_verbatim:
        paras.append(f"Stamped: {up.stampings_verbatim}.")
    description = "\n\n".join(paras)

    # -- tags --------------------------------------------------------------
    tags: list[str] = ["estate pipe"]
    if brand_asserted and genome.brand:
        tags.append(genome.brand.lower())
    if genome.model_line:
        tags.append(genome.model_line.lower())
    if genome.taxonomy:
        tags.extend(t for t in genome.taxonomy.split("/") if t)
    if up:
        tags.extend(m.value.replace("_", " ") for m in up.materials)
    tags.extend(era_tags)
    # de-dupe, preserve order
    seen: set[str] = set()
    tags = [t for t in tags if not (t in seen or seen.add(t))]

    # -- gaps: high-value facts a good listing wants but this record lacks -
    gaps: list[str] = []
    if not genome.media:
        gaps.append("photos (photos are the DNA — a listing needs them)")
    if grade is None:
        gaps.append("condition grade")
    if up is None or up.era is None:
        gaps.append("era estimate")
    if genome.economics.list_price is None:
        gaps.append("list price")
    if not genome.why_special:
        gaps.append("the why-special hook (one sentence)")

    return ListingDraft(
        sku=genome.sku,
        channel=channel,
        title=title,
        description=description,
        tags=tags,
        image_order=image_order,
        alt_texts=alt_texts,
        disclosures=disclosures,
        gaps=gaps,
        hedged=sorted(decision.hedge_tier_a),
    )
