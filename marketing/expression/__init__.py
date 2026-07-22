"""Expression layer (P2.6) — generated marketing content; disposable, versioned."""

from .copy import GENERATOR_VERSION, ascii_safe, generate_description, generate_title
from .store import ExpressionRecord, ExpressionStore, inputs_hash

__all__ = [
    "GENERATOR_VERSION",
    "ExpressionRecord",
    "ExpressionStore",
    "ascii_safe",
    "generate_description",
    "generate_title",
    "inputs_hash",
]
