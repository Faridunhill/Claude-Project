"""Marketing DNA — Layer 1 (GENOME).

Immutable birth records + corrections ledger + quarantine state machine.
See marketing/README.md and MARKETING_DNA_SYNTHESIS_v1 §3.
"""

from .schema import (
    SCHEMA_VERSION,
    Attribution,
    Compliance,
    Economics,
    EraEstimate,
    FieldProvenance,
    Measurements,
    MediaItem,
    ProductGenome,
    UniquePhysicalExtension,
    completeness_score,
    iter_missing_consumers,
)
from .corrections import (
    Correction,
    CorrectionReason,
    IllegalTransition,
    Visibility,
    apply_corrections,
    transition,
)
from .store import BirthRecordExists, GenomeStore
from .intake import (
    IntakeError,
    IntakeInput,
    IntakeResult,
    build_genome,
    ingest,
)

__all__ = [
    "SCHEMA_VERSION",
    "Attribution",
    "BirthRecordExists",
    "IntakeError",
    "IntakeInput",
    "IntakeResult",
    "build_genome",
    "ingest",
    "Compliance",
    "Correction",
    "CorrectionReason",
    "Economics",
    "EraEstimate",
    "FieldProvenance",
    "GenomeStore",
    "IllegalTransition",
    "Measurements",
    "MediaItem",
    "ProductGenome",
    "UniquePhysicalExtension",
    "Visibility",
    "apply_corrections",
    "completeness_score",
    "iter_missing_consumers",
    "transition",
]
