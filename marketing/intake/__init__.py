"""Intake pipeline (P2.3) — photos + voice note + two numbers -> birth record."""

from .assemble import IntakeReport, ItemResult, assemble_item, load_numbers, run_intake
from .photos import PhotoScan, scan_photos
from .structure import KeywordStructurer, StructuredNote, TranscriptStructurer
from .transcribe import (
    StubTranscriber,
    Transcriber,
    TranscriptResult,
    WhisperCLITranscriber,
    get_transcript,
)

__all__ = [
    "IntakeReport",
    "ItemResult",
    "KeywordStructurer",
    "PhotoScan",
    "StructuredNote",
    "StubTranscriber",
    "Transcriber",
    "TranscriptResult",
    "TranscriptStructurer",
    "WhisperCLITranscriber",
    "assemble_item",
    "get_transcript",
    "load_numbers",
    "run_intake",
    "scan_photos",
]
