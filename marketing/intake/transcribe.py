"""Voice-note transcription orchestration.

The actual Whisper run happens on the PC nightly (local model, LAW:
audio never leaves the machine). The contract is file-based and dumb on
purpose: for `note.m4a`, the PC job writes `note.m4a.txt` beside it.

This module:
  * finds the voice note in an item folder,
  * uses an existing sidecar transcript if present (the normal path),
  * otherwise tries a pluggable Transcriber (local whisper CLI if
    installed), and if none is available, reports the audio as PENDING
    — intake still proceeds (throughput rule), the transcript lands on
    the next nightly run.
"""

from __future__ import annotations

import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .conventions import AUDIO_EXTS


@dataclass(frozen=True)
class TranscriptResult:
    text: Optional[str]          # None -> pending
    source: str                  # "sidecar" | "whisper-cli" | "stub" | "pending"
    audio_path: Optional[str] = None


class Transcriber(ABC):
    @abstractmethod
    def transcribe(self, audio: Path) -> Optional[str]:
        """Return transcript text, or None if unable."""


class WhisperCLITranscriber(Transcriber):
    """Uses a locally installed `whisper` CLI if present. Writes the
    sidecar so the work is never repeated."""

    def __init__(self, model: str = "small"):
        self.model = model

    def available(self) -> bool:
        return shutil.which("whisper") is not None

    def transcribe(self, audio: Path) -> Optional[str]:
        if not self.available():
            return None
        try:
            subprocess.run(
                ["whisper", str(audio), "--model", self.model,
                 "--output_format", "txt", "--output_dir", str(audio.parent)],
                check=True, capture_output=True, timeout=600,
            )
        except (subprocess.SubprocessError, OSError):
            return None
        produced = audio.parent / (audio.stem + ".txt")
        return produced.read_text(encoding="utf-8").strip() if produced.exists() else None


class StubTranscriber(Transcriber):
    """For tests and dry runs."""

    def __init__(self, text: str = ""):
        self._text = text

    def transcribe(self, audio: Path) -> Optional[str]:
        return self._text


def find_audio(item_dir: Path) -> Optional[Path]:
    for p in sorted(item_dir.iterdir()):
        if p.is_file() and p.suffix.lower() in AUDIO_EXTS:
            return p
    return None


def get_transcript(item_dir: Path, transcriber: Optional[Transcriber] = None) -> TranscriptResult:
    audio = find_audio(item_dir)
    if audio is None:
        return TranscriptResult(text=None, source="pending", audio_path=None)

    sidecar = audio.parent / (audio.name + ".txt")
    if sidecar.exists():
        return TranscriptResult(
            text=sidecar.read_text(encoding="utf-8").strip(),
            source="sidecar",
            audio_path=str(audio),
        )
    # also accept whisper's default naming: <stem>.txt
    alt = audio.parent / (audio.stem + ".txt")
    if alt.exists():
        return TranscriptResult(
            text=alt.read_text(encoding="utf-8").strip(),
            source="sidecar",
            audio_path=str(audio),
        )

    if transcriber is not None:
        text = transcriber.transcribe(audio)
        if text is not None:
            sidecar.write_text(text, encoding="utf-8")
            kind = "stub" if isinstance(transcriber, StubTranscriber) else "whisper-cli"
            return TranscriptResult(text=text, source=kind, audio_path=str(audio))

    return TranscriptResult(text=None, source="pending", audio_path=str(audio))
