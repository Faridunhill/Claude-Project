"""Catalog adapter tests — the fuel line from content/products to the
generators. The governing rule under test: the adapter never invents a
fact. Absent stays absent; only allowlisted brands are asserted."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from marketing.catalog import (
    build_taxonomy,
    extract_brand,
    extract_era,
    extract_origin,
    extract_shape,
    load_brands,
    load_catalog,
    load_item,
    to_effective,
)
from marketing.genome.vocab import EraBasis, FieldSource, MediaRole

BRANDS_PATH = Path(__file__).resolve().parent.parent / "brands.yaml"
PRODUCTS_DIR = Path(__file__).resolve().parents[2] / "content" / "products"


@pytest.fixture(scope="module")
def brands() -> list[str]:
    return load_brands(BRANDS_PATH)


# ── brand extraction: the honesty boundary ───────────────────────────

def test_allowlisted_brand_is_extracted(brands):
    assert extract_brand("Bari Winking 1999 First Logo Army Mount", brands) == "Bari"


def test_non_brand_words_are_never_extracted(brands):
    """'German' and 'Vintage' lead 100+ titles. Neither is a maker."""
    assert extract_brand("Vintage German Leather Cigar Case with Metal Frame", brands) is None


def test_brand_matches_on_word_boundaries(brands):
    """Substring matching would read 'Bari' out of 'Barista'."""
    assert extract_brand("Barista Coffee Grinder", brands) is None


def test_longest_brand_wins(brands):
    """'CTS Wolfertz' must not degrade to 'CTS'."""
    assert extract_brand("CTS Wolfertz Solingen V-Cut Cigar Cutter", brands) == "CTS Wolfertz"


def test_punctuation_differences_still_match(brands):
    assert extract_brand("French Estate Butz Choquin Jura 1009", brands) == "Butz-Choquin"


# ── era: loose by design ─────────────────────────────────────────────

def test_decade_becomes_a_ten_year_span():
    era = extract_era("Almer Goldplate Chain Pipe Vintage 1980s")
    assert (era["min_year"], era["max_year"]) == (1980, 1989)


def test_explicit_range_is_read():
    era = extract_era("Antique Pipe Tool c. 1900-1930 Stainless Steel")
    assert (era["min_year"], era["max_year"]) == (1900, 1930)


def test_period_words_are_understood():
    assert extract_era("Art Deco Bakelite Guillotine Cutter")["min_year"] == 1920


def test_era_basis_is_always_style():
    """The adapter reads Farid's period wording, not a stamping it
    verified — so copy may say 'mid-century', never 'circa 1955'."""
    for title in ("Vintage 1980s Pipe", "c. 1900-1930 Tool", "Art Deco Cutter"):
        assert extract_era(title)["basis"] == EraBasis.STYLE.value


def test_no_date_means_no_era():
    assert extract_era("German Leather Tobacco Pouch Minimalist") is None


# ── shape / origin / taxonomy ────────────────────────────────────────

def test_shape_prefers_the_most_specific_word():
    assert extract_shape("French Ceramic Mini Churchwarden Straight Billiard") == "churchwarden"


def test_shape_tie_break_is_deterministic():
    """Equal-length matches must always resolve the same way, or the
    same title would land in two different taxonomy nodes on two runs."""
    title = "Smooth Bent Pot Billiard Calabash Estate Pipe"
    assert extract_shape(title) == extract_shape(title) == "billiard"


def test_origin_from_stated_nationality():
    assert extract_origin("French Estate Butz Choquin Jura") == "FR"
    assert extract_origin("Solingen Germany Gold Tone Cutter") == "DE"


def test_taxonomy_does_not_repeat_its_department():
    assert build_taxonomy("meerschaum", "meerschaum") == "meerschaum"
    assert build_taxonomy("estate-pipes", "billiard") == "estate-pipes/billiard"
    assert build_taxonomy("lighters", None) == "lighters"


# ── the effective record ─────────────────────────────────────────────

def test_effective_record_shape(brands):
    effective = to_effective(
        {
            "name": "Bari Winking 1999 Army Mount Straight Billiard",
            "department": "estate-pipes",
            "price": "129.00",
            "sku": "FH-TP-022",
            "images": ["https://cdn.example/a.jpg", "https://cdn.example/b.jpg"],
        },
        brands,
    )
    assert effective["sku"] == "FH-TP-022"
    assert effective["brand"] == "Bari"
    assert effective["list_price"] == 129.00
    assert effective["product_type"] == "unique_physical"
    assert effective["media"][0]["role"] == MediaRole.HERO.value
    assert effective["media"][1]["role"] == MediaRole.ANGLE.value


def test_provenance_is_human_so_copy_may_assert(brands):
    """Titles are hand-written by Farid. That is what unlocks ASSERT."""
    effective = to_effective(
        {"name": "Chacom Gentleman 836", "sku": "X1", "department": "estate-pipes"}, brands
    )
    assert effective["field_provenance"]["brand"]["source"] == FieldSource.HUMAN.value


def test_absent_facts_stay_absent(brands):
    effective = to_effective(
        {"name": "Leather Pouch", "sku": "X2", "department": "leather-bags"}, brands
    )
    assert "brand" not in effective
    assert "country_of_origin" not in effective
    assert "unique_physical" not in effective


def test_bad_price_does_not_crash(brands):
    effective = to_effective({"name": "N", "sku": "X3", "price": "ask"}, brands)
    assert effective["list_price"] is None


def test_item_without_sku_is_rejected(tmp_path, brands):
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump({"name": "No SKU", "department": "lighters"}))
    assert load_item(path, brands) is None


# ── the real catalog ─────────────────────────────────────────────────

@pytest.mark.skipif(not PRODUCTS_DIR.exists(), reason="catalog not present")
def test_real_catalog_loads_and_is_unique_by_sku():
    items = load_catalog(PRODUCTS_DIR, BRANDS_PATH)
    assert len(items) > 200
    skus = [i.sku for i in items]
    assert len(skus) == len(set(skus)), "duplicate SKUs would double-spend daily slots"


@pytest.mark.skipif(not PRODUCTS_DIR.exists(), reason="catalog not present")
def test_every_real_item_generates_a_caption():
    """The whole catalog must survive the generators — one unhandled
    title would break a nightly run."""
    from marketing.social.captions import generate_caption

    for item in load_catalog(PRODUCTS_DIR, BRANDS_PATH):
        caption = generate_caption(item.effective)
        assert caption.text.strip()
        assert caption.hashtags
        assert caption.full().isascii()


@pytest.mark.skipif(not PRODUCTS_DIR.exists(), reason="catalog not present")
def test_no_hashtag_contains_punctuation():
    """#rattray's is a broken tag; #rattrays is not."""
    from marketing.social.captions import generate_caption

    for item in load_catalog(PRODUCTS_DIR, BRANDS_PATH):
        for tag in generate_caption(item.effective).hashtags:
            assert tag.isalnum(), f"{item.sku}: bad hashtag {tag!r}"
