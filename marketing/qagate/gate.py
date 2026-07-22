"""QA gate — the four routing rules (Synthesis §5, Code F2, ratified).

Protects the appraiser's name: 95.1% Top-1 at 200 items is ~10 confident
misattributions published everywhere at once unless gated.

Tier A fields (misattribution class): brand, maker, era, restricted
materials. Routing, enforced in code:

  1. CONFIDENCE   — Tier A confidence < threshold        -> REVIEW
  2. CORROBORATION— vision claim inconsistent with OCR   -> REVIEW (always)
  3. PRICE        — list price >= threshold              -> REVIEW (always)
  4. AUDIT        — deterministic ~5% of auto-passes     -> AUDIT queue

Audit sampling is hash-based (sku), not random: reproducible, testable,
and immune to resume/replay double-sampling.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ..genome.adapter_itemassets import VisionClaim

#: Tier A — the misattribution class. Everything else is never gated.
TIER_A_FIELDS = frozenset({
    "brand",
    "maker",
    "unique_physical.era",
    "unique_physical.materials",
})


@dataclass(frozen=True)
class GateConfig:
    """Calibration priors (Synthesis §5). Re-set after the first
    100-item calibration set; the audit queue measures the gate itself."""

    tier_a_confidence_threshold: float = 0.90
    price_review_threshold: float = 150.00
    audit_rate_denominator: int = 20          # 1 in 20 ~= 5%
    research_queue_min_uplift: float = 50.00  # candidate value over no-name floor


class Route(str, Enum):
    AUTO_PASS = "auto_pass"
    REVIEW = "review"
    AUDIT = "audit"


class RouteReason(str, Enum):
    LOW_CONFIDENCE = "low_confidence"
    OCR_MISMATCH = "ocr_mismatch"
    HIGH_PRICE = "high_price"
    AUDIT_SAMPLE = "audit_sample"
    NOT_TIER_A = "not_tier_a"
    PASSED = "passed"


@dataclass(frozen=True)
class GateDecision:
    sku: str
    claim: VisionClaim
    route: Route
    reasons: tuple[RouteReason, ...] = field(default_factory=tuple)


def _corroborated(claim: VisionClaim, stamping_ocr: Optional[str]) -> Optional[bool]:
    """Cross-check the two independent witnesses. Returns None when OCR
    is absent (rule cannot fire), True/False otherwise.

    Conservative token check: for text-valued claims, the claim value's
    first token must appear in the OCR text. Era/material claims are not
    OCR-checkable this way and return None."""
    if not stamping_ocr:
        return None
    value = claim.value
    if not isinstance(value, str) or not value.strip():
        return None
    token = value.strip().split()[0].lower()
    return token in stamping_ocr.lower()


def _audit_sampled(sku: str, denominator: int) -> bool:
    digest = hashlib.sha256(sku.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % denominator == 0


def route_claim(
    sku: str,
    claim: VisionClaim,
    stamping_ocr: Optional[str],
    list_price: Optional[float],
    config: GateConfig = GateConfig(),
) -> GateDecision:
    """Route one vision claim through the four rules."""
    if claim.field_path not in TIER_A_FIELDS:
        return GateDecision(sku, claim, Route.AUTO_PASS, (RouteReason.NOT_TIER_A,))

    reasons: list[RouteReason] = []

    if claim.confidence < config.tier_a_confidence_threshold:
        reasons.append(RouteReason.LOW_CONFIDENCE)

    corroborated = _corroborated(claim, stamping_ocr)
    if corroborated is False:  # OCR present and it disagrees — always review
        reasons.append(RouteReason.OCR_MISMATCH)

    if list_price is not None and list_price >= config.price_review_threshold:
        reasons.append(RouteReason.HIGH_PRICE)

    if reasons:
        return GateDecision(sku, claim, Route.REVIEW, tuple(reasons))

    if _audit_sampled(sku, config.audit_rate_denominator):
        return GateDecision(sku, claim, Route.AUDIT, (RouteReason.AUDIT_SAMPLE,))

    return GateDecision(sku, claim, Route.AUTO_PASS, (RouteReason.PASSED,))


def route_item(
    sku: str,
    claims: list[VisionClaim],
    stamping_ocr: Optional[str],
    list_price: Optional[float],
    config: GateConfig = GateConfig(),
) -> list[GateDecision]:
    return [route_claim(sku, c, stamping_ocr, list_price, config) for c in claims]
