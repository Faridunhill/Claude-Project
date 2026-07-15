"""Corrections ledger + quarantine state machine (Synthesis §1 V4,
Gemini E1 pattern, ratified).

Birth data is immutable, but visibility has a state machine:

    detect -> QUARANTINED (delist everywhere via adapters)
           -> correction appended to ledger (never mutates birth)
           -> effective_data = birth + corrections
           -> expression regenerated
           -> REPUBLISHING -> LIVE

Two hard rules enforced here:
  * A correction NEVER edits the birth record — it is an append-only
    ledger row, merged at read time by `apply_corrections`.
  * Performance-motivated corrections are refused: a correction must
    carry a factual reason category. "It sells better if we call it
    1940s" is fraud, and an automated system would industrialize it.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .vocab import FieldSource


class CorrectionReason(str, Enum):
    """Only factual categories exist. There is deliberately no
    'performance' or 'marketing' reason — that path is fraud."""

    MISREAD_STAMPING = "misread_stamping"
    VISION_ERROR = "vision_error"
    TRANSCRIPTION_ERROR = "transcription_error"
    MEASUREMENT_ERROR = "measurement_error"
    NEW_DOCUMENTATION = "new_documentation"   # e.g. catalog found, hallmark decoded
    EXPERT_REATTRIBUTION = "expert_reattribution"
    DATA_ENTRY_ERROR = "data_entry_error"


class Visibility(str, Enum):
    LIVE = "live"
    QUARANTINED = "quarantined"      # delisted everywhere pending correction
    REPUBLISHING = "republishing"    # corrected, expression regenerating


class Correction(BaseModel):
    """One append-only ledger row. field_path uses dotted genome paths,
    e.g. 'unique_physical.era' or 'brand'."""

    model_config = ConfigDict(frozen=True)

    correction_id: str = Field(default_factory=lambda: f"cor-{uuid.uuid4().hex[:12]}")
    sku: str
    field_path: str
    old_value: Any = None
    new_value: Any = None
    reason: CorrectionReason
    note: Optional[str] = None
    source: FieldSource = FieldSource.HUMAN
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Legal state transitions. Anything not listed raises.
_TRANSITIONS: dict[Visibility, set[Visibility]] = {
    Visibility.LIVE: {Visibility.QUARANTINED},
    Visibility.QUARANTINED: {Visibility.REPUBLISHING},
    Visibility.REPUBLISHING: {Visibility.LIVE, Visibility.QUARANTINED},
}


class IllegalTransition(Exception):
    pass


def transition(current: Visibility, target: Visibility) -> Visibility:
    """Validate a visibility transition; return the new state."""
    if target not in _TRANSITIONS.get(current, set()):
        raise IllegalTransition(f"{current.value} -> {target.value} is not a legal transition")
    return target


def apply_corrections(birth: dict[str, Any], corrections: list[Correction]) -> dict[str, Any]:
    """effective_data = birth + corrections, applied in timestamp order.

    Returns a NEW dict; the birth dict is never modified. Nested paths
    create intermediate dicts as needed (a correction may fill a field
    that was null at birth).
    """
    import copy

    effective = copy.deepcopy(birth)
    for cor in sorted(corrections, key=lambda c: c.ts):
        parts = cor.field_path.split(".")
        node = effective
        for part in parts[:-1]:
            if not isinstance(node.get(part), dict):
                node[part] = {}
            node = node[part]
        node[parts[-1]] = cor.new_value
    return effective
