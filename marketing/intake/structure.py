"""Transcript -> structured genome fields.

Deliberately CONSERVATIVE. This deterministic pass only extracts what it
can match against controlled vocabulary (flaws, restoration) — the full
transcript always lands in condition_notes so nothing dictated is ever
lost. Richer structuring (why_special extraction, provenance bullets)
belongs to the local LLM agents on the PC; they plug in via the same
`TranscriptStructurer` interface and re-run safely because structuring
feeds the BIRTH record only once — later refinements go through the
corrections ledger.

A wrong guess here would be laundered into confident copy downstream,
so: no fuzzy matching, no cleverness. Exact-phrase matching only.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..genome.vocab import FlawCode, RestorationCode


@dataclass(frozen=True)
class StructuredNote:
    condition_notes: str = ""
    flaws: list[FlawCode] = field(default_factory=list)
    restoration: list[RestorationCode] = field(default_factory=list)
    why_special: str = ""                       # only if explicitly marked
    provenance_bullets: list[str] = field(default_factory=list)


class TranscriptStructurer(ABC):
    @abstractmethod
    def structure(self, transcript: str) -> StructuredNote:
        ...


#: Exact phrases (lowercase) -> flaw codes. Extend freely; never fuzzy.
_FLAW_PHRASES: dict[str, FlawCode] = {
    "rim darkening": FlawCode.RIM_DARKENING,
    "darkened rim": FlawCode.RIM_DARKENING,
    "rim char": FlawCode.RIM_CHAR,
    "charred rim": FlawCode.RIM_CHAR,
    "light tooth marks": FlawCode.TOOTH_MARKS_LIGHT,
    "small tooth marks": FlawCode.TOOTH_MARKS_LIGHT,
    "deep tooth marks": FlawCode.TOOTH_MARKS_DEEP,
    "heavy tooth marks": FlawCode.TOOTH_MARKS_DEEP,
    "oxidized stem": FlawCode.STEM_OXIDATION,
    "stem oxidation": FlawCode.STEM_OXIDATION,
    "fills": FlawCode.FILLS,
    "putty fill": FlawCode.FILLS,
    "crack": FlawCode.CRACK,
    "hairline": FlawCode.CRACK,
    "chip": FlawCode.CHIP,
    "scratches": FlawCode.SCRATCHES,
    "scratched": FlawCode.SCRATCHES,
    "dent": FlawCode.DENT,
    "finish wear": FlawCode.FINISH_WEAR,
    "worn finish": FlawCode.FINISH_WEAR,
    "loose stem": FlawCode.LOOSE_STEM_FIT,
    "tight stem": FlawCode.TIGHT_STEM_FIT,
    "replacement stem": FlawCode.REPLACEMENT_STEM,
    "replaced stem": FlawCode.REPLACEMENT_STEM,
    "ghosting": FlawCode.GHOSTING,
    "ghost": FlawCode.GHOSTING,
    "missing": FlawCode.MISSING_PART,
}

_RESTORATION_PHRASES: dict[str, RestorationCode] = {
    "cleaned": RestorationCode.CLEANED,
    "sanitized": RestorationCode.SANITIZED,
    "deep clean": RestorationCode.CLEANED,
    "repolished": RestorationCode.STEM_REPOLISHED,
    "polished the stem": RestorationCode.STEM_REPOLISHED,
    "deoxidized": RestorationCode.STEM_DEOXIDIZED,
    "topped the rim": RestorationCode.RIM_TOPPED,
    "rim topped": RestorationCode.RIM_TOPPED,
    "refinished": RestorationCode.REFINISHED,
    "rewaxed": RestorationCode.REWAXED,
    "new wax": RestorationCode.REWAXED,
    "unrestored": RestorationCode.UNRESTORED,
    "untouched": RestorationCode.UNRESTORED,
}

#: Optional spoken markers. "special: ..." / "story: ..." to end of sentence.
_SPECIAL_RE = re.compile(r"(?:special|the hook)[:\s]+(.+?)(?:\.|$)", re.IGNORECASE)
_PROVENANCE_RE = re.compile(r"(?:provenance|from the estate|estate of)[:\s]*(.+?)(?:\.|$)", re.IGNORECASE)


class KeywordStructurer(TranscriptStructurer):
    def structure(self, transcript: str) -> StructuredNote:
        text = transcript.strip()
        low = text.lower()

        flaws: list[FlawCode] = []
        for phrase, code in _FLAW_PHRASES.items():
            if phrase in low and code not in flaws:
                flaws.append(code)

        restoration: list[RestorationCode] = []
        for phrase, code in _RESTORATION_PHRASES.items():
            if phrase in low and code not in restoration:
                restoration.append(code)

        special = ""
        m = _SPECIAL_RE.search(text)
        if m:
            special = m.group(1).strip()

        bullets: list[str] = []
        pm = _PROVENANCE_RE.search(text)
        if pm:
            bullet = pm.group(1).strip()[:140]
            if bullet:
                bullets.append(bullet)

        return StructuredNote(
            condition_notes=text,
            flaws=flaws,
            restoration=restoration,
            why_special=special,
            provenance_bullets=bullets[:3],
        )
