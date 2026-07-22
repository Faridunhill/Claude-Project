"""Caption + hashtag generator (SOCIAL-ENGINE-001). Expression-layer:
regenerable, versioned via ExpressionStore, ASCII-safe, honest —
the same lock rules as listing copy (a hedged brand is never asserted)."""

from __future__ import annotations

from dataclasses import dataclass

from ..expression.copy import ascii_safe, _era_phrase, _taxonomy_leaf  # shared rules
from ..qagate.lock import ClaimMode, assertable

CAPTION_GENERATOR_VERSION = "caption-1.0.0"

_BASE_TAGS = ["estatepipe", "pipesmoking", "pipecollector", "tobaccopipe", "faridunhill"]

_LEAF_TAGS = {
    "dublin": ["dublinpipe"],
    "billiard": ["billiardpipe"],
    "meerschaum": ["meerschaumpipe"],
    "rhodesian": ["rhodesianpipe"],
}


@dataclass(frozen=True)
class Caption:
    text: str
    hashtags: list[str]
    generator_version: str = CAPTION_GENERATOR_VERSION

    def full(self) -> str:
        return self.text + "\n\n" + " ".join(f"#{t}" for t in self.hashtags)


def generate_caption(effective: dict, kind: str = "new_arrival") -> Caption:
    """kind: new_arrival | sold_archive."""
    brand = assertable(effective, "brand")
    leaf = _taxonomy_leaf(effective)
    era = _era_phrase(effective)

    if brand.mode is ClaimMode.ASSERT:
        subject = f"{brand.value} {effective.get('model_line') or ''}".strip()
    else:
        subject = f"{leaf or 'estate pipe'}"

    hook = effective.get("why_special") or ""
    lines: list[str] = []

    if kind == "sold_archive":
        lines.append(f"From the archive: {subject}{', ' + era if era else ''}.")
        if hook:
            lines.append(hook.rstrip(".") + ".")
        lines.append("Sold - documented forever in the Faridunhill encyclopedia.")
    else:
        lines.append(f"New arrival: {subject}{', ' + era if era else ''}.")
        if hook:
            lines.append(hook.rstrip(".") + ".")
        lines.append("One pipe, one owner - the photographs show the exact piece.")

    tags = list(_BASE_TAGS)
    if brand.mode is ClaimMode.ASSERT:
        tags.append(str(brand.value).lower().replace(" ", ""))
    for token, extra in _LEAF_TAGS.items():
        if token in (leaf or "").lower():
            tags.extend(extra)

    return Caption(text=ascii_safe("\n".join(lines)), hashtags=tags[:12])
