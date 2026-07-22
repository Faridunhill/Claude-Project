"""QA gate (P2.4) — consequence-tiered routing, review queue, generator lock."""

from .gate import (
    TIER_A_FIELDS,
    GateConfig,
    GateDecision,
    Route,
    RouteReason,
    route_claim,
    route_item,
)
from .lock import ClaimMode, ClaimResult, assertable, priced_as_unattributed
from .review import ReviewQueue, ReviewScreen, Verdict

__all__ = [
    "TIER_A_FIELDS",
    "ClaimMode",
    "ClaimResult",
    "GateConfig",
    "GateDecision",
    "ReviewQueue",
    "ReviewScreen",
    "Route",
    "RouteReason",
    "Verdict",
    "assertable",
    "priced_as_unattributed",
    "route_claim",
    "route_item",
]
