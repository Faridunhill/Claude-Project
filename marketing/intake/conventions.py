"""Intake conventions — the contract between the photography table and
the machine (Synthesis §4, the 200-pipe checklist).

Folder layout (one folder per item, named by SKU):

    intake_root/
      numbers.csv               # sku,cost_basis,floor_price[,list_price]
      FH-TP-041/
        01-hero.jpg             # <seq>-<role>.<ext> — role from filename
        02-angle.jpg
        03-stamping.jpg         # macro of every stamping — THE critical frame
        04-flaw.jpg
        05-scale.jpg            # beside ruler / on scale with readout
        note.m4a                # 30-second voice note
        note.m4a.txt            # transcript — written by nightly Whisper on
                                # the PC; if present, audio is never re-sent

Rules embodied here:
  * A skipped photo is unrecoverable after sale; a skipped field is a
    cheap batch job. The checklist REPORTS gaps — it never blocks intake
    (throughput rule: machine defaults, human never blocks).
  * Unknown filename roles fall back to ANGLE and are marked
    source=inferred in field_provenance.
"""

from __future__ import annotations

from ..genome.vocab import MediaRole

#: Accepted photo extensions (lowercase).
PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}

#: Accepted voice-note extensions (lowercase).
AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".ogg", ".aac"}

#: Filename tokens -> media roles.
ROLE_TOKENS: dict[str, MediaRole] = {
    "hero": MediaRole.HERO,
    "angle": MediaRole.ANGLE,
    "stamping": MediaRole.STAMPING,
    "stamp": MediaRole.STAMPING,
    "nomenclature": MediaRole.STAMPING,
    "flaw": MediaRole.FLAW,
    "damage": MediaRole.FLAW,
    "scale": MediaRole.SCALE,
    "ruler": MediaRole.SCALE,
    "weight": MediaRole.SCALE,
    "group": MediaRole.GROUP,
    "lot": MediaRole.GROUP,
}

#: The photo checklist (Synthesis §4). key -> (human label, is_critical).
#: Critical gaps are highlighted first in reports; nothing ever blocks.
CHECKLIST: dict[MediaRole, tuple[str, bool]] = {
    MediaRole.HERO: ("hero shot", True),
    MediaRole.STAMPING: ("stamping macro — unrecoverable after sale", True),
    MediaRole.SCALE: ("scale/ruler frame (weight & size as photos)", True),
    MediaRole.ANGLE: ("additional angles", False),
    MediaRole.FLAW: ("flaw close-ups (only if flaws exist)", False),
}

#: Recommended minimum total frames per item.
MIN_FRAMES = 8

#: numbers.csv column names.
NUMBERS_COLUMNS = ("sku", "cost_basis", "floor_price", "list_price")
