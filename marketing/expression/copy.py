"""Copy generators (P2.6) — Layer 2, EXPRESSION.

Titles and descriptions are FUNCTIONS of the effective genome, computed
late, regenerated whenever generators improve. Never hand-edited: a bad
output means fixing the genome or this generator, then regenerating.

Hard rules enforced here:
  * Tier A claims go through the QA-gate lock (assertable): verified ->
    assert; unverified vision claim -> hedge ("attributed to") in the
    DESCRIPTION only — a marketplace TITLE never carries a hedged brand.
  * Every recorded flaw is disclosed in the description (the honesty
    layer). No flaw suppression path exists.
  * Era claims follow basis: stamping/catalog/hallmark/documentation may
    say "circa"; style says the period loosely; guess says nothing.
  * All output is ASCII-safe (LAW 09).
"""

from __future__ import annotations

import unicodedata

from ..qagate.lock import ClaimMode, assertable

GENERATOR_VERSION = "copy-1.0.0"

_ASCII_MAP = {
    "—": "-", "–": "-", "‘": "'", "’": "'",
    "“": '"', "”": '"', "…": "...", "£": "GBP ",
    "€": "EUR ", "×": "x", "°": " deg",
}

_ASSERTIVE_ERA_BASES = {"stamping", "catalog", "hallmark", "documentation"}


def ascii_safe(text: str) -> str:
    """Transliterate to plain ASCII (LAW 09). Lossy on purpose."""
    for src, dst in _ASCII_MAP.items():
        text = text.replace(src, dst)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def _era_phrase(effective: dict) -> str:
    era = (effective.get("unique_physical") or {}).get("era") or {}
    lo, hi, basis = era.get("min_year"), era.get("max_year"), era.get("basis")
    if not (lo and hi):
        return ""
    if basis in _ASSERTIVE_ERA_BASES:
        mid = (lo + hi) // 2
        return f"circa {(mid // 10) * 10}s" if hi - lo > 4 else f"circa {mid}"
    if basis == "style":
        if hi <= 1945:
            return "pre-war era"
        if hi <= 1975:
            return "mid-century"
        return "late 20th century"
    return ""  # guess -> say nothing


def _condition_phrase(effective: dict) -> str:
    grade = (effective.get("unique_physical") or {}).get("condition_grade")
    return grade.replace("_", " ").title() if grade else ""


def _taxonomy_leaf(effective: dict) -> str:
    taxonomy = effective.get("taxonomy") or ""
    leaf = taxonomy.rsplit("/", 1)[-1] if taxonomy else ""
    return leaf.replace("-", " ").replace("_", " ").title()


def generate_title(effective: dict, max_len: int = 80) -> str:
    """Marketplace-safe title. A hedged brand NEVER appears here —
    hedging is description-only language."""
    parts: list[str] = []

    brand = assertable(effective, "brand")
    if brand.mode is ClaimMode.ASSERT:
        parts.append(str(brand.value))
        model = effective.get("model_line")
        if model:
            parts.append(str(model))
    else:
        origin = effective.get("country_of_origin")
        if origin == "FR":
            parts.append("French")
        elif origin == "GB":
            parts.append("English")
        elif origin == "IT":
            parts.append("Italian")
        elif origin == "DE":
            parts.append("German")

    era = _era_phrase(effective)
    if era:
        parts.append(era)

    leaf = _taxonomy_leaf(effective)
    if leaf:
        parts.append(leaf)

    condition = _condition_phrase(effective)
    suffix = " | Estate" if effective.get("product_type") == "unique_physical" else ""
    title = " ".join(parts) + (f", {condition}" if condition else "") + suffix
    return ascii_safe(title)[:max_len].strip()


def generate_description(effective: dict) -> str:
    """Structured description: hook, facts, honesty layer, provenance,
    measurements, the exact-item promise."""
    unique = effective.get("unique_physical") or {}
    lines: list[str] = []

    hook = effective.get("why_special")
    if hook:
        lines.append(hook.strip().rstrip(".") + ".")
        lines.append("")

    # attribution paragraph — where hedging lives
    brand = assertable(effective, "brand")
    if brand.mode is ClaimMode.ASSERT:
        sentence = f"A {_taxonomy_leaf(effective).lower()} by {brand.value}"
        model = effective.get("model_line")
        if model:
            sentence += f", {model}"
        era = _era_phrase(effective)
        if era:
            sentence += f", {era}"
        lines.append(sentence.strip() + ".")
    elif brand.mode is ClaimMode.HEDGE and brand.candidate:
        lines.append(
            f"Unsigned or not conclusively attributed; characteristics consistent "
            f"with {brand.candidate} (attribution not verified, priced accordingly)."
        )

    stampings = unique.get("stampings_verbatim")
    if stampings:
        lines.append(f'Stamped: "{stampings}".')

    # honesty layer — every flaw, always
    flaws = unique.get("flaws") or []
    restoration = unique.get("restoration") or []
    if flaws:
        readable = ", ".join(f.replace("_", " ") for f in flaws)
        lines.append(f"Condition notes, disclosed in full: {readable}.")
    if restoration:
        readable = ", ".join(r.replace("_", " ") for r in restoration)
        lines.append(f"Workshop care: {readable}.")

    for bullet in effective.get("provenance_context") or []:
        lines.append(f"Provenance: {bullet}.")

    meas = unique.get("measurements") or {}
    dims = []
    if meas.get("length_mm"):
        dims.append(f"length {meas['length_mm']:.0f} mm")
    if meas.get("weight_g"):
        dims.append(f"weight {meas['weight_g']:.0f} g")
    if meas.get("chamber_diameter_mm"):
        dims.append(f"chamber {meas['chamber_diameter_mm']:.0f} mm")
    if dims:
        lines.append("Measurements: " + ", ".join(dims) + ".")

    if effective.get("product_type") == "unique_physical":
        lines.append("")
        lines.append(
            "One-of-a-kind piece - the photographs show the exact item you will receive."
        )

    return ascii_safe("\n".join(lines).strip())
