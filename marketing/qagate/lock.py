"""THE LOCK (Synthesis §5) — generators cannot make assertive Tier A
claims for unverified vision-sourced facts.

Every copy generator MUST fetch Tier A values through `assertable()`.
Bypassing the review queue therefore produces hedged listings and
visible lost margin — never invisible misattributions. A gate whose
bypass is self-punishing needs no discipline to survive.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from ..genome.vocab import AttributionStatus, FieldSource
from .gate import TIER_A_FIELDS


class ClaimMode(str, Enum):
    ASSERT = "assert"    # "Chacom Gentleman 836"
    HEDGE = "hedge"      # "attributed to Chacom"
    OMIT = "omit"        # say nothing


@dataclass(frozen=True)
class ClaimResult:
    value: Optional[Any]
    mode: ClaimMode
    candidate: Optional[str] = None   # for hedge copy ("attributed to X")


def _get_path(record: dict, path: str):
    node: Any = record
    for part in path.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def assertable(effective: dict, field_path: str) -> ClaimResult:
    """Decide how copy may use a field, from the EFFECTIVE record
    (birth + corrections) and field_provenance.

    Non-Tier-A fields: always assertable if present.
    Tier A fields:
      value present + provenance human, or attribution VERIFIED -> ASSERT
      attribution UNVERIFIED with candidate                     -> HEDGE
      attribution REJECTED or nothing known                     -> OMIT
    """
    value = _get_path(effective, field_path)

    if field_path not in TIER_A_FIELDS:
        if value in (None, "", [], {}):
            return ClaimResult(None, ClaimMode.OMIT)
        return ClaimResult(value, ClaimMode.ASSERT)

    # attribution state written by the review queue
    attribution = (
        _get_path(effective, f"{field_path}.__attribution_status")
        or _get_path(effective, f"attribution.{field_path}")
        or {}
    )
    status = attribution.get("status") if isinstance(attribution, dict) else None

    if value not in (None, "", [], {}):
        provenance = (effective.get("field_provenance") or {}).get(field_path, {})
        source = provenance.get("source")
        if source == FieldSource.HUMAN.value or status == AttributionStatus.VERIFIED.value:
            return ClaimResult(value, ClaimMode.ASSERT)
        # value exists but vision-sourced and not verified -> hedge on it
        return ClaimResult(None, ClaimMode.HEDGE, candidate=str(value))

    if status == AttributionStatus.UNVERIFIED.value:
        return ClaimResult(None, ClaimMode.HEDGE, candidate=attribution.get("candidate"))

    return ClaimResult(None, ClaimMode.OMIT)


def priced_as_unattributed(effective: dict, field_path: str = "brand") -> bool:
    """True when the price model must use the no-name floor for this
    item (hedge-and-list rule): the Tier A field is not assertable."""
    return assertable(effective, field_path).mode is not ClaimMode.ASSERT
