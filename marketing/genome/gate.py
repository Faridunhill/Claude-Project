"""QA gate — P2.4 (Round 2 F2: "gate by consequence × confidence").

The safety layer between a genome birth record and an assertive listing.
Its job is narrow and load-bearing: decide which Tier A claims (the ones
that move price or authenticity) may be ASSERTED, and which must be
routed to a human or HEDGED — so one vision error never ships as fact.

Field tiers by consequence of error (Round 2 F2):
  * Tier A — brand/maker, era, restricted materials. An error here is a
    misattribution: the reputation-killing class.
  * Tier B — shape (model_line), country of origin. Embarrassing, cheap,
    correctable. Tracked, never gated.
  * Tier C — everything else. Never gated.

The four routing rules (all enforced here):
  1. CONFIDENCE — a Tier A vision claim with confidence < 0.90 → review.
  2. CORROBORATION — a Tier A vision claim inconsistent with the verbatim
     stamping OCR → review, regardless of confidence. (Two independent
     extractors; the cheapest catch for confident-but-wrong.)
  3. PRICE — list price ≥ threshold (default £150) → review ALL Tier A
     vision claims regardless of confidence. Buy insurance where the loss
     is.
  4. AUDIT — a random ~5% of otherwise-auto-passing items is also flagged
     for the queue (labeled audit) so the gate's own false-accept rate is
     measurable and the 0.90 prior can be calibrated.

Outcomes:
  * PASS            — every Tier A claim is assertable now.
  * REVIEW          — at least one Tier A claim is routed to a human. The
                      item STILL LISTS; the routed fields HEDGE until a
                      human verifies (hedge-and-list; "Can't tell" lives
                      here). Underclaiming costs margin; overclaiming
                      costs the business.
  * RESEARCH_LATER  — withhold listing: an unverified attribution whose
                      price uplift over the no-name floor ≥ £50, where the
                      expected value of getting it right beats the carrying
                      cost. (Inactive until a pricing uplift is supplied.)

Human-sourced Tier A facts are always assertable — the founder is the
domain expert; a typed fact outranks a model guess and needs no gate.

This module does NOT persist a review queue or verify claims — it decides.
Wiring the decision to a review screen + AttributionStatus writeback is
part of the QA-review UI; the gate gives it everything it needs.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from .schema import ProductGenome
from .vocab import FieldSource, RESTRICTED_MATERIALS

# --- field tiers -----------------------------------------------------------

TIER_A_FIELDS: frozenset[str] = frozenset(
    {"brand", "unique_physical.era", "unique_physical.materials"}
)
TIER_B_FIELDS: frozenset[str] = frozenset({"model_line", "country_of_origin"})

CONFIDENCE_FLOOR = 0.90            # Round 2 F2 rule 1 (a prior, not a truth)
DEFAULT_PRICE_REVIEW_THRESHOLD = 150.0   # rule 3 (currency per control.yaml)
DEFAULT_AUDIT_RATE = 0.05          # rule 4


class GateOutcome(str, Enum):
    PASS = "pass"
    REVIEW = "review"
    RESEARCH_LATER = "research_later"


class RoutingRule(str, Enum):
    CONFIDENCE = "confidence"
    CORROBORATION = "corroboration"
    PRICE = "price"


@dataclass(frozen=True)
class RoutedField:
    """One Tier A field sent to human review, and why."""

    field_path: str
    rule: RoutingRule
    detail: str


@dataclass
class GateDecision:
    sku: str
    outcome: GateOutcome
    routed: list[RoutedField] = field(default_factory=list)
    assertable_tier_a: list[str] = field(default_factory=list)  # may assert now
    hedge_tier_a: list[str] = field(default_factory=list)       # must hedge until verified
    is_audit: bool = False
    reasons: list[str] = field(default_factory=list)

    @property
    def lists(self) -> bool:
        """Does the item go live? Everything lists except RESEARCH_LATER."""
        return self.outcome is not GateOutcome.RESEARCH_LATER


# --- corroboration ---------------------------------------------------------

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN.findall(text.lower()) if len(t) >= 3}


def _brand_corroborated(brand: str, stamping_ocr: Optional[str]) -> Optional[bool]:
    """True/False if we can judge; None if there is no witness to check
    against (no OCR) — absence of a witness is not a contradiction."""
    if not stamping_ocr:
        return None
    brand_tokens = _tokens(brand)
    if not brand_tokens:
        return None
    ocr_tokens = _tokens(stamping_ocr)
    # corroborated if any significant brand token appears in the stamping
    return bool(brand_tokens & ocr_tokens)


# --- audit sampling --------------------------------------------------------

def default_audit_sampler(rate: float = DEFAULT_AUDIT_RATE) -> Callable[[str], bool]:
    """Deterministic ~`rate` sampler keyed on the SKU (reproducible, so a
    given SKU's audit status never flickers between runs). Swap for a
    true RNG sampler in production if desired."""
    bucket = max(1, round(1 / rate))

    def sample(sku: str) -> bool:
        digest = hashlib.sha256(sku.encode()).hexdigest()
        return int(digest, 16) % bucket == 0

    return sample


# --- the gate --------------------------------------------------------------

def evaluate(
    genome: ProductGenome,
    *,
    price_review_threshold: float = DEFAULT_PRICE_REVIEW_THRESHOLD,
    attribution_uplift: Optional[float] = None,
    audit_sampler: Optional[Callable[[str], bool]] = None,
) -> GateDecision:
    """Run the four rules over one genome and return a decision.

    `attribution_uplift` (if known, from the pricing model) is the £ a
    verified attribution would add over the no-name floor; ≥ £50 on an
    unverified vision brand triggers RESEARCH_LATER.
    """
    prov = genome.field_provenance
    stamping = (
        genome.unique_physical.stampings_verbatim
        if genome.unique_physical is not None
        else None
    )
    list_price = genome.economics.list_price
    price_triggered = list_price is not None and list_price >= price_review_threshold

    routed: list[RoutedField] = []
    assertable: list[str] = []
    hedge: list[str] = []
    reasons: list[str] = []

    # Which Tier A fields are actually present on this record?
    present = [f for f in TIER_A_FIELDS if _present(genome, f)]

    for f in present:
        p = prov.get(f)
        source = p.source if p else FieldSource.INFERRED
        conf = p.confidence if p else None

        # Human-asserted facts are authoritative — never gated.
        if source is FieldSource.HUMAN:
            assertable.append(f)
            continue

        field_routes: list[RoutedField] = []

        # Rule 2 — corroboration (brand only has a verbatim witness).
        if f == "brand":
            corro = _brand_corroborated(genome.brand or "", stamping)
            if corro is False:
                field_routes.append(RoutedField(
                    f, RoutingRule.CORROBORATION,
                    f"claimed brand '{genome.brand}' not found in stamping OCR",
                ))

        # Rule 1 — confidence.
        if conf is not None and conf < CONFIDENCE_FLOOR:
            field_routes.append(RoutedField(
                f, RoutingRule.CONFIDENCE, f"confidence {conf:.2f} < {CONFIDENCE_FLOOR}",
            ))

        # Rule 3 — price (routes every Tier A vision claim regardless).
        if price_triggered:
            field_routes.append(RoutedField(
                f, RoutingRule.PRICE,
                f"list price {list_price} ≥ {price_review_threshold} — review all Tier A",
            ))

        if field_routes:
            routed.extend(field_routes)
            hedge.append(f)
        else:
            assertable.append(f)

    # --- resolve the overall outcome -------------------------------------
    if routed:
        outcome = GateOutcome.REVIEW
        rules_hit = sorted({r.rule.value for r in routed})
        reasons.append(f"Tier A fields routed to review ({', '.join(rules_hit)} rule)")

        # RESEARCH_LATER override: a high-value unverified brand attribution.
        brand_routed = any(r.field_path == "brand" for r in routed)
        if (
            brand_routed
            and attribution_uplift is not None
            and attribution_uplift >= 50.0
        ):
            outcome = GateOutcome.RESEARCH_LATER
            reasons.append(
                f"attribution uplift £{attribution_uplift:.0f} ≥ £50 on an unverified "
                "brand — hold for research rather than list at the no-name floor"
            )
    else:
        outcome = GateOutcome.PASS
        reasons.append("all Tier A claims assertable")

    # --- rule 4 — audit (does not change listability, flags the queue) ---
    sampler = audit_sampler or default_audit_sampler()
    is_audit = outcome is GateOutcome.PASS and sampler(genome.sku)
    if is_audit:
        reasons.append("selected for 5% calibration audit")

    return GateDecision(
        sku=genome.sku,
        outcome=outcome,
        routed=routed,
        assertable_tier_a=sorted(assertable),
        hedge_tier_a=sorted(hedge),
        is_audit=is_audit,
        reasons=reasons,
    )


def _present(genome: ProductGenome, path: str) -> bool:
    obj = genome
    for part in path.split("."):
        if obj is None:
            return False
        obj = getattr(obj, part, None)
    return obj not in (None, "", [], {})
