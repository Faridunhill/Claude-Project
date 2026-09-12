"""Photo vault — matching catalog items to the real photo folders.

THE PROBLEM. The web catalog carries exactly one thumbnail per item, so
every reel is a two-second zoom on a single photograph. Meanwhile the
PC holds the real shoots: 135 photographs for one Rattray's set alone,
32 pipes with folders, thousands more harvested. The agent was reading
the thin catalog while the rich library sat on the same disk.

THE HARD PART. Folder names are not SKUs. `_WRONG_SPLIT_rattrays_mega`
has to be matched to "Rattray's Mary Sandblast Complete Set: 161
Rhodesian, 162 Prince, 163 Billiard" by name alone.

THE METHOD — rarity-weighted token overlap. Shared words are scored by
how rare they are across the catalog, so "rattrays" (one item) counts
for far more than "vintage" (sixty-six). A match is only as good as its
rarest shared word, which is exactly how a human would judge it, and
the evidence is reported so the judgement can be checked.

THE RULE THIS OBEYS. Matching is a guess, and guesses never publish
themselves. `vault-scan` writes `photo_map.proposed.yaml` for a human
to read; the runner reads only `photo_map.yaml`, which a human creates.
Same shape as the QA gate: the machine proposes, a person confirms.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import yaml

PHOTO_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")

#: Words that carry no identifying signal. They appear in scores of
#: titles and in vault folder names used as processing markers.
_STOPWORDS = frozenset("""
a an and the of for with in on at to from by
vintage antique estate rare genuine quality original classic
new old stock nos unused unsmoked mint
pipe pipes smoking tobacco tobacciana
inch inches cm mm oz
wrong split mega done todo tmp temp copy backup final raw edit edited
img image images photo photos pic pics dsc
""".split())

_MIN_TOKEN_LEN = 3


def _stem(word: str) -> str:
    """Fold plurals and possessives onto one form.

    Without this, "Rattray's" in a title tokenises to "rattray" while the
    folder `_WRONG_SPLIT_rattrays_mega` gives "rattrays", and the single
    most obvious match in the whole vault scores zero. Applied to both
    sides, so it only has to be consistent, not linguistically correct.
    """
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def tokenize(text: str, extra_stopwords: frozenset[str] = frozenset()) -> set[str]:
    """Identifying words only: lowercase, split on non-letters, drop
    stopwords, numbers and very short fragments, fold plurals."""
    words = re.split(r"[^a-z0-9]+", text.lower())
    return {
        _stem(w) for w in words
        if len(w) >= _MIN_TOKEN_LEN
        and w not in _STOPWORDS
        and w not in extra_stopwords
        and not w.isdigit()
    }


def natural_key(path: Path):
    """Sort photo_2 before photo_10 — plain string sort does not."""
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", path.name)]


@dataclass(frozen=True)
class VaultFolder:
    path: str
    name: str
    photo_count: int
    tokens: frozenset[str] = field(default_factory=frozenset)

    def photos(self, limit: Optional[int] = None) -> list[str]:
        files = sorted(
            (p for p in Path(self.path).iterdir()
             if p.suffix.lower() in PHOTO_SUFFIXES),
            key=natural_key,
        )
        return [str(p) for p in (files[:limit] if limit else files)]


@dataclass(frozen=True)
class Match:
    sku: str
    name: str
    folder: Optional[VaultFolder]
    score: float
    evidence: tuple[str, ...]          # the shared words that earned it

    @property
    def confident(self) -> bool:
        """Two shared words, or one that is all but unique.

        A single moderately common word is not evidence: "gentleman"
        appears in four titles and would otherwise bind three unrelated
        items to one folder. Corroboration is the same principle the QA
        gate applies to a vision claim.
        """
        if self.folder is None or self.score < CONFIDENT_SCORE:
            return False
        return len(self.evidence) >= 2 or self.score >= NEAR_UNIQUE_SCORE


# Scores are NORMALISED: one word unique to a single title scores 1.0,
# whatever the catalog size. Raw IDF would not do - log(265) clears a
# threshold of 5.0 but log(42) does not, so the same match would be
# confident against 264 items and rejected against 40. Thresholds that
# shift with corpus size are thresholds nobody can reason about.
#
#: Minimum total score before a match is even proposed as confident.
CONFIDENT_SCORE = 0.55
#: A single word carries a match only if it is near-unique: present in
#: one or two titles (>= 0.85). "gentleman", in four of 264, scores
#: 0.75 and is correctly refused on its own.
NEAR_UNIQUE_SCORE = 0.85


def scan_vault(vault_root: str | Path, min_photos: int = 2) -> list[VaultFolder]:
    """Every folder under `vault_root` holding at least `min_photos`.

    Folders with a single photo are skipped: they cannot improve on the
    catalog thumbnail, which is the entire point of looking.
    """
    root = Path(vault_root).expanduser()
    if not root.exists():
        raise FileNotFoundError(f"vault root does not exist: {root}")

    # The vault's own directory names ("photo_vault", "faridunhillpipes")
    # sit in every folder's context and would match any title containing
    # them. Only those two levels: walking the whole absolute path would
    # blacklist words from unrelated parent directories — a vault under
    # a folder named after a brand would make that brand unmatchable.
    root_words = frozenset(
        w for part in (root.name, root.parent.name)
        for w in re.split(r"[^a-z0-9]+", part.lower()) if w
    )

    folders: list[VaultFolder] = []
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        try:
            count = sum(1 for p in path.iterdir()
                        if p.suffix.lower() in PHOTO_SUFFIXES)
        except OSError:
            continue                     # unreadable folder: skip, never abort
        if count >= min_photos:
            # Include parent names: a folder called "mega" under
            # "rattrays" is identified by its parent, not itself.
            context = " ".join(p.name for p in list(path.parents)[:2]) + " " + path.name
            folders.append(VaultFolder(
                path=str(path), name=path.name, photo_count=count,
                tokens=frozenset(tokenize(context, extra_stopwords=root_words)),
            ))
    return folders


def rarity_weights(names: Iterable[str]) -> dict[str, float]:
    """Inverse document frequency over catalog titles.

    A word in one title out of 264 is strong evidence; a word in sixty
    of them is nearly none.
    """
    names = list(names)
    total = max(1, len(names))
    counts: Counter[str] = Counter()
    for name in names:
        counts.update(tokenize(name))
    # Smoothed so weights stay strictly positive: plain log(total/count)
    # is 0 for a word in every title, which collapses the scale on a
    # small corpus. Normalised by the weight of a word unique to one
    # title, so "unique" is always 1.0 regardless of catalog size.
    unit = math.log(total + 1)
    return {
        word: math.log((total + 1) / count) / unit
        for word, count in counts.items()
    }


def match_item(name: str, folders: Iterable[VaultFolder],
               weights: dict[str, float]) -> tuple[Optional[VaultFolder], float, tuple[str, ...]]:
    """Best folder for one title, its score, and the words that earned it."""
    item_tokens = tokenize(name)
    best: Optional[VaultFolder] = None
    best_score = 0.0
    best_shared: tuple[str, ...] = ()

    for folder in folders:
        shared = item_tokens & folder.tokens
        if not shared:
            continue
        # Unknown words (present in the vault but in no title) are
        # maximally rare, so weight them as such rather than zero.
        default = 1.0
        score = sum(weights.get(word, default) for word in shared)
        if score > best_score:
            best, best_score, best_shared = folder, score, tuple(sorted(shared))

    return best, best_score, best_shared


def propose(items, folders: list[VaultFolder]) -> list[Match]:
    """Match every catalog item, best first."""
    weights = rarity_weights(item.name for item in items)
    matches = [
        Match(item.sku, item.name, *match_item(item.name, folders, weights))
        for item in items
    ]
    matches.sort(key=lambda m: m.score, reverse=True)
    return matches


def write_proposal(matches: list[Match], path: str | Path) -> Path:
    """A reviewable file, not a live mapping.

    Confident matches are written as active entries; weaker ones are
    commented out so approving them is a deliberate act of deleting a
    "#", never an oversight.
    """
    path = Path(path)
    lines = [
        "# PROPOSED photo-vault mapping — REVIEW BEFORE USE.",
        "#",
        "# The runner does NOT read this file. Check the entries, then copy",
        "# the ones you agree with into photo_map.yaml.",
        "#",
        "# `matched on` lists the shared words that earned the match. If",
        "# those words do not convince you, the match is wrong.",
        "",
        "photos:",
    ]
    confident = [m for m in matches if m.confident]
    weak = [m for m in matches if m.folder and not m.confident]

    lines.append(f"  # ---- {len(confident)} confident (score >= {CONFIDENT_SCORE}) ----")
    for match in confident:
        lines.append(f"  # {match.name[:70]}")
        lines.append(f"  #   matched on: {', '.join(match.evidence)} "
                     f"(score {match.score:.1f}, {match.folder.photo_count} photos)")
        lines.append(f"  {match.sku}: {match.folder.path!r}")

    lines.append("")
    lines.append(f"  # ---- {len(weak)} weak — delete the '#' only if you agree ----")
    for match in weak:
        lines.append(f"  # {match.name[:70]}")
        lines.append(f"  #   matched on: {', '.join(match.evidence)} "
                     f"(score {match.score:.1f}, {match.folder.photo_count} photos)")
        lines.append(f"  # {match.sku}: {match.folder.path!r}")

    unmatched = [m for m in matches if not m.folder]
    lines += ["", f"# {len(unmatched)} items matched nothing in the vault."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_photo_map(path: str | Path) -> dict[str, str]:
    """The CONFIRMED mapping the runner uses. Absent file = no mapping,
    which is not an error — it means nobody has reviewed one yet."""
    path = Path(path)
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(k): str(v) for k, v in (data.get("photos") or {}).items()}


def photos_for(sku: str, photo_map: dict[str, str], limit: int = 5) -> list[str]:
    """Local photos for a SKU, or [] when it is unmapped or the folder
    has gone. A missing folder is not fatal — the runner falls back to
    the catalog thumbnail."""
    folder = photo_map.get(sku)
    if not folder:
        return []
    path = Path(folder).expanduser()
    if not path.is_dir():
        return []
    files = sorted(
        (p for p in path.iterdir() if p.suffix.lower() in PHOTO_SUFFIXES),
        key=natural_key,
    )
    return [str(p) for p in files[:limit]]
