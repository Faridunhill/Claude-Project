"""Caption + hashtag generator (SOCIAL-ENGINE-001). Expression-layer:
regenerable, versioned via ExpressionStore, ASCII-safe, honest —
the same lock rules as listing copy (a hedged brand is never asserted)."""

from __future__ import annotations

import re
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


def _hashtag(text: str) -> str:
    """Platform-safe hashtag body: letters and digits only.

    A brand like "Rattray's" must not become "#rattray's" - the
    apostrophe terminates the tag, so the post ships a broken link and
    a stray quote mark.
    """
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _subject_from_catalog_name(name: str, max_len: int = 64) -> str:
    """A human-written listing title, trimmed to caption length.

    Titles are keyword-dense for marketplace search ("... : 161
    Rhodesian, 162 Prince, 163 Billiard with Black Knight Bag"). The
    part before the first colon or dash is the piece's actual name; the
    rest is search tail that reads badly in a social caption.
    """
    head = re.split(r"\s[-|]\s|:", name, maxsplit=1)[0].strip()
    head = head or name.strip()
    if len(head) > max_len:
        head = head[:max_len].rsplit(" ", 1)[0].rstrip(",-")
    return head


def generate_caption(effective: dict, kind: str = "new_arrival") -> Caption:
    """kind: new_arrival | sold_archive."""
    brand = assertable(effective, "brand")
    leaf = _taxonomy_leaf(effective)
    era = _era_phrase(effective)

    # `catalog_name` is the title Farid wrote himself after handling the
    # object, so it is a human claim and may be asserted — the lock
    # exists to stop the machine asserting what IT guessed. The one case
    # it must not override is HEDGE: there the machine holds an
    # unverified vision claim, and the title could smuggle it back in.
    catalog_name = (effective.get("catalog_name") or "").strip()
    if catalog_name and brand.mode is not ClaimMode.HEDGE:
        subject = _subject_from_catalog_name(catalog_name)
    elif brand.mode is ClaimMode.ASSERT:
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
        brand_tag = _hashtag(str(brand.value))
        if brand_tag:
            tags.append(brand_tag)
    for token, extra in _LEAF_TAGS.items():
        if token in (leaf or "").lower():
            tags.extend(extra)

    return Caption(text=ascii_safe("\n".join(lines)), hashtags=tags[:12])
