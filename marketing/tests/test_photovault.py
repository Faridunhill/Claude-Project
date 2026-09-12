"""Photo vault tests.

The vault holds the real shoots (135 photographs for one Rattray's set)
while the catalog carries one thumbnail. Matching folder names to titles
is a guess, so the rules under test are about PRECISION: a wrong match
puts the wrong pipe in a reel, which is worse than no match at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from marketing.photovault import (
    CONFIDENT_SCORE,
    Match,
    load_photo_map,
    natural_key,
    photos_for,
    propose,
    rarity_weights,
    scan_vault,
    tokenize,
    write_proposal,
)


class Item:
    """Minimal stand-in for CatalogItem (propose() needs sku + name)."""

    def __init__(self, sku: str, name: str):
        self.sku, self.name = sku, name


def with_corpus(*items: Item) -> list[Item]:
    """Rarity is measured against the catalog, so a word is only strong
    evidence relative to other titles. Tests that judge confidence need
    a realistic corpus around the item under test, not one title."""
    filler = [
        Item(f"F-{i}", f"Vintage German Leather Tobacco Pouch Variant {i}")
        for i in range(40)
    ]
    return list(items) + filler


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    root = tmp_path / "photo_vault" / "faridunhillpipes"
    for name, count in {
        "_WRONG_SPLIT_rattrays_mega": 135,
        "jurgen_moritz_freehand_323": 12,
        "single_photo_folder": 1,
    }.items():
        folder = root / name
        folder.mkdir(parents=True)
        for i in range(count):
            (folder / f"IMG_{i + 1:03}.jpg").write_bytes(b"\xff\xd8\xff")
    return root


# ── tokenising ───────────────────────────────────────────────────────

def test_possessive_and_plural_fold_together():
    """"Rattray's" in a title and "rattrays" in a folder name must meet.
    Without this the most obvious match in the vault scores zero."""
    assert tokenize("Rattray's Mary") & tokenize("_WRONG_SPLIT_rattrays_mega")


def test_stopwords_carry_no_signal():
    assert tokenize("Vintage Antique Estate Pipe") == set()


def test_processing_markers_are_ignored():
    """WRONG, SPLIT and MEGA are folder bookkeeping, not identity."""
    assert not {"wrong", "split", "mega"} & tokenize("_WRONG_SPLIT_rattrays_mega")


def test_short_fragments_and_numbers_are_dropped():
    tokens = tokenize("S2 161 Ad Astra")
    assert "161" not in tokens and "s2" not in tokens
    assert "astra" in tokens


# ── rarity weighting ─────────────────────────────────────────────────

def test_rare_words_outweigh_common_ones():
    names = ["Rattray Mary"] + [f"German Leather Pouch {i}" for i in range(60)]
    weights = rarity_weights(names)
    assert weights["rattray"] > weights["german"]


# ── matching precision ───────────────────────────────────────────────

def test_the_rattrays_match_is_found(vault):
    items = with_corpus(Item("FH-TP-110", "Rattray's Mary Sandblast Complete Set: 161 Rhodesian"))
    match = propose(items, scan_vault(vault))[0]
    assert match.confident
    assert "rattrays_mega" in match.folder.path
    assert match.folder.photo_count == 135


def test_one_common_word_is_never_confident():
    """"gentleman" appears in four of 264 titles - normalised score 0.75,
    above the base threshold but below near-unique. On its own it would
    otherwise bind three unrelated items to one folder."""
    match = Match("S", "n", folder=object(), score=0.75, evidence=("gentleman",))
    assert match.score > CONFIDENT_SCORE      # clears the base bar
    assert not match.confident                # and is still refused


def test_one_near_unique_word_is_enough():
    """A word unique to one title normalises to exactly 1.0."""
    match = Match("S", "n", folder=object(), score=1.0, evidence=("rattray",))
    assert match.confident


def test_two_words_corroborate():
    """Neither word is near-unique alone; together they are evidence."""
    match = Match("S", "n", folder=object(), score=0.6,
                  evidence=("chacom", "dublin"))
    assert match.confident


def test_confidence_does_not_depend_on_catalog_size():
    """Normalised scoring: the same match must be judged the same way
    against 40 items and against 264. Raw IDF failed this."""
    small = with_corpus(Item("A", "Rattray's Mary Sandblast"))
    large = small + [Item(f"G-{i}", f"Chacom Gentleman {i} Dublin") for i in range(200)]
    assert rarity_weights(n.name for n in small)["rattray"] == pytest.approx(1.0)
    assert rarity_weights(n.name for n in large)["rattray"] == pytest.approx(1.0)


def test_unmatched_item_yields_no_folder(vault):
    items = with_corpus(Item("X", "Zzzz Qqqq Unrelated Object"))
    match = [m for m in propose(items, scan_vault(vault)) if m.sku == "X"][0]
    assert match.folder is None and not match.confident


def test_vault_root_words_are_not_evidence(vault):
    """"photo_vault" and "faridunhillpipes" sit in every folder's path
    and would match any title containing those words."""
    items = with_corpus(Item("X", "Faridunhill Photo Vault Collection"))
    match = [m for m in propose(items, scan_vault(vault)) if m.sku == "X"][0]
    assert not match.confident


def test_single_photo_folders_are_ignored(vault):
    """A one-photo folder cannot improve on the catalog thumbnail."""
    assert all(f.name != "single_photo_folder" for f in scan_vault(vault))


def test_missing_vault_root_is_an_explicit_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        scan_vault(tmp_path / "nope")


# ── the proposal is not a mapping ────────────────────────────────────

def test_weak_matches_are_commented_out(tmp_path, vault):
    items = with_corpus(
        Item("A", "Rattray's Mary Sandblast"),
        # matches the Chacom folder on "gentleman" alone: real overlap,
        # too weak to act on.
        Item("B", "A Gentleman's Travelling Companion"),
    )
    path = write_proposal(propose(items, scan_vault(vault)), tmp_path / "p.yaml")
    body = path.read_text()
    assert "REVIEW BEFORE USE" in body
    for line in body.splitlines():
        if line.strip().startswith("B:"):
            pytest.fail("a weak match must stay commented out")


def test_proposal_records_the_evidence(tmp_path, vault):
    items = with_corpus(Item("A", "Rattray's Mary Sandblast"))
    path = write_proposal(propose(items, scan_vault(vault)), tmp_path / "p.yaml")
    assert "matched on: rattray" in path.read_text()


# ── the confirmed map ────────────────────────────────────────────────

def test_absent_map_is_empty_not_an_error(tmp_path):
    assert load_photo_map(tmp_path / "none.yaml") == {}


def test_confirmed_map_round_trips(tmp_path, vault):
    folder = vault / "_WRONG_SPLIT_rattrays_mega"
    path = tmp_path / "photo_map.yaml"
    path.write_text(f"photos:\n  FH-TP-110: {str(folder)!r}\n")
    assert load_photo_map(path) == {"FH-TP-110": str(folder)}


def test_photos_are_capped_and_naturally_ordered(tmp_path, vault):
    folder = vault / "_WRONG_SPLIT_rattrays_mega"
    photos = photos_for("S", {"S": str(folder)}, limit=5)
    assert len(photos) == 5
    assert Path(photos[0]).name == "IMG_001.jpg"
    assert Path(photos[1]).name == "IMG_002.jpg"      # not IMG_010


def test_natural_key_orders_numerically():
    names = [Path("IMG_10.jpg"), Path("IMG_2.jpg")]
    assert [p.name for p in sorted(names, key=natural_key)] == ["IMG_2.jpg", "IMG_10.jpg"]


def test_vanished_folder_falls_back_silently(tmp_path):
    """A moved folder must not crash the nightly run; the catalog
    thumbnail is still there."""
    assert photos_for("S", {"S": str(tmp_path / "gone")}) == []


def test_unmapped_sku_returns_nothing(vault):
    assert photos_for("UNKNOWN", {"S": str(vault)}) == []
